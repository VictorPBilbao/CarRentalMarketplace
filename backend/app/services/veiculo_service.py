from datetime import datetime

from fastapi import HTTPException
from surrealdb import AsyncSurreal

from app.core.database import extract_records
from app.schemas.veiculo import VeiculoRequest, VeiculoResponse


def _dt(v: object) -> str:
    if isinstance(v, datetime):
        return v.isoformat()
    return str(v) if v else ''


def _row_to_response(row: dict) -> VeiculoResponse:
    return VeiculoResponse(
        id=str(row['id']),
        make=row['make'],
        model=row['model'],
        year=int(row['year']),
        color=row['color'],
        plate=row['plate'],
        chassis_number=row['chassis_number'],
        mileage_km=int(row.get('mileage_km', 0)),
        status=row.get('status', 'AVAILABLE'),
        category=str(row['category']),
        current_store=str(row['current_store']),
        company=str(row['company']),
        created_at=_dt(row.get('created_at')),
        updated_at=_dt(row.get('updated_at')),
    )


async def _check_loja(store_id: str, company_id: str, db: AsyncSurreal) -> None:
    """Garante que a loja pertence à empresa."""
    result = await db.query(
        "SELECT id FROM type::record($id) WHERE company = type::record($cid) LIMIT 1",
        {'id': store_id, 'cid': company_id},
    )
    if not extract_records(result):
        raise HTTPException(status_code=403, detail='Loja não pertence à sua empresa.')


async def _check_categoria(categoria_id: str, company_id: str, db: AsyncSurreal) -> None:
    """Garante que a categoria pertence à empresa e está ativa."""
    result = await db.query(
        "SELECT id FROM type::record($id) WHERE company = type::record($cid) AND active = true LIMIT 1",
        {'id': categoria_id, 'cid': company_id},
    )
    if not extract_records(result):
        raise HTTPException(status_code=403, detail='Categoria não pertence à sua empresa ou está inativa.')


async def listar(
    company_id: str,
    db: AsyncSurreal,
    store_id: str | None = None,
) -> list[VeiculoResponse]:
    if store_id:
        result = await db.query(
            """
            SELECT * FROM vehicle
            WHERE company = type::record($cid) AND current_store = type::record($sid)
            ORDER BY make ASC, model ASC
            """,
            {'cid': company_id, 'sid': store_id},
        )
    else:
        result = await db.query(
            """
            SELECT * FROM vehicle
            WHERE company = type::record($cid)
            ORDER BY make ASC, model ASC
            """,
            {'cid': company_id},
        )
    records = extract_records(result)
    return [_row_to_response(r) for r in records if isinstance(r, dict)]


async def buscar_por_id(
    veiculo_id: str,
    company_id: str,
    db: AsyncSurreal,
    store_id: str | None = None,
) -> VeiculoResponse:
    params: dict = {'id': veiculo_id, 'cid': company_id}
    store_clause = ''
    if store_id:
        store_clause = ' AND current_store = type::record($sid)'
        params['sid'] = store_id

    result = await db.query(
        f"SELECT * FROM type::record($id) WHERE company = type::record($cid){store_clause} LIMIT 1",
        params,
    )
    records = extract_records(result)
    if not records:
        raise HTTPException(status_code=404, detail='Veículo não encontrado.')
    return _row_to_response(records[0])


async def criar(
    payload: VeiculoRequest,
    company_id: str,
    store_id: str,
    db: AsyncSurreal,
) -> VeiculoResponse:
    await _check_loja(store_id, company_id, db)
    await _check_categoria(payload.category, company_id, db)

    dup_plate = await db.query(
        "SELECT id FROM vehicle WHERE company = type::record($cid) AND plate = $plate LIMIT 1",
        {'cid': company_id, 'plate': payload.plate.upper()},
    )
    if extract_records(dup_plate):
        raise HTTPException(status_code=409, detail='Já existe um veículo com esta placa.')

    dup_chassis = await db.query(
        "SELECT id FROM vehicle WHERE company = type::record($cid) AND chassis_number = $chassis LIMIT 1",
        {'cid': company_id, 'chassis': payload.chassis_number.upper()},
    )
    if extract_records(dup_chassis):
        raise HTTPException(status_code=409, detail='Já existe um veículo com este número de chassi.')

    result = await db.query(
        """
        CREATE vehicle CONTENT {
            make:           $make,
            model:          $model,
            year:           $year,
            color:          $color,
            plate:          $plate,
            chassis_number: $chassis_number,
            mileage_km:     $mileage_km,
            status:         $status,
            category:       type::record($category_id),
            current_store:  type::record($store_id),
            company:        type::record($company_id)
        }
        """,
        {
            'make':           payload.make,
            'model':          payload.model,
            'year':           payload.year,
            'color':          payload.color,
            'plate':          payload.plate.upper(),
            'chassis_number': payload.chassis_number.upper(),
            'mileage_km':     payload.mileage_km,
            'status':         payload.status,
            'category_id':    payload.category,
            'store_id':       store_id,
            'company_id':     company_id,
        },
    )

    records = extract_records(result)
    if not records:
        raise HTTPException(status_code=500, detail='Erro ao criar veículo.')

    row = records[0]
    if isinstance(row, dict):
        return _row_to_response(row)
    return await buscar_por_id(str(row), company_id, db)


async def atualizar(
    veiculo_id: str,
    payload: VeiculoRequest,
    company_id: str,
    store_id: str,
    db: AsyncSurreal,
    store_restrito: str | None = None,
) -> VeiculoResponse:
    """
    store_restrito: quando não None, exige que o veículo esteja nessa loja
    antes de permitir a edição (usado pelo contexto de filial).
    """
    params: dict = {'id': veiculo_id, 'cid': company_id}
    store_clause = ''
    if store_restrito:
        store_clause = ' AND current_store = type::record($sid)'
        params['sid'] = store_restrito

    exists = await db.query(
        f"SELECT id FROM type::record($id) WHERE company = type::record($cid){store_clause} LIMIT 1",
        params,
    )
    if not extract_records(exists):
        raise HTTPException(status_code=404, detail='Veículo não encontrado.')

    await _check_loja(store_id, company_id, db)
    await _check_categoria(payload.category, company_id, db)

    dup_plate = await db.query(
        """
        SELECT id FROM vehicle
        WHERE company = type::record($cid) AND plate = $plate AND id != type::record($id)
        LIMIT 1
        """,
        {'cid': company_id, 'plate': payload.plate.upper(), 'id': veiculo_id},
    )
    if extract_records(dup_plate):
        raise HTTPException(status_code=409, detail='Já existe outro veículo com esta placa.')

    dup_chassis = await db.query(
        """
        SELECT id FROM vehicle
        WHERE company = type::record($cid) AND chassis_number = $chassis AND id != type::record($id)
        LIMIT 1
        """,
        {'cid': company_id, 'chassis': payload.chassis_number.upper(), 'id': veiculo_id},
    )
    if extract_records(dup_chassis):
        raise HTTPException(status_code=409, detail='Já existe outro veículo com este número de chassi.')

    result = await db.query(
        """
        UPDATE type::record($id) MERGE {
            make:           $make,
            model:          $model,
            year:           $year,
            color:          $color,
            plate:          $plate,
            chassis_number: $chassis_number,
            mileage_km:     $mileage_km,
            status:         $status,
            category:       type::record($category_id),
            current_store:  type::record($store_id)
        }
        """,
        {
            'id':             veiculo_id,
            'make':           payload.make,
            'model':          payload.model,
            'year':           payload.year,
            'color':          payload.color,
            'plate':          payload.plate.upper(),
            'chassis_number': payload.chassis_number.upper(),
            'mileage_km':     payload.mileage_km,
            'status':         payload.status,
            'category_id':    payload.category,
            'store_id':       store_id,
        },
    )

    records = extract_records(result)
    if not records:
        raise HTTPException(status_code=500, detail='Erro ao atualizar veículo.')

    row = records[0]
    if isinstance(row, dict):
        return _row_to_response(row)
    return await buscar_por_id(veiculo_id, company_id, db)
