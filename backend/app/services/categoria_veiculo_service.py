from datetime import datetime

from fastapi import HTTPException
from surrealdb import AsyncSurreal

from app.core.database import extract_records
from app.schemas.categoria_veiculo import CategoriaVeiculoRequest, CategoriaVeiculoResponse
from app.schemas.usuario import UsuarioPayload


def _dt(v: object) -> str:
    if isinstance(v, datetime):
        return v.isoformat()
    return str(v) if v else ''


def _row_to_response(row: dict) -> CategoriaVeiculoResponse:
    features_raw = row.get('features') or {}
    capacity_raw = features_raw.get('capacity') or {}

    return CategoriaVeiculoResponse(
        id=str(row['id']),
        code=row['code'],
        group_name=row['group_name'],
        acriss_code=row.get('acriss_code'),
        description=row.get('description'),
        features={
            'air_conditioning': bool(features_raw.get('air_conditioning', True)),
            'capacity': {
                'passengers':      int(capacity_raw.get('passengers', 1)),
                'small_suitcases': int(capacity_raw.get('small_suitcases', 0)),
                'large_suitcases': int(capacity_raw.get('large_suitcases', 0)),
            },
            'doors':        int(features_raw.get('doors', 4)),
            'fuel_type':    features_raw.get('fuel_type', 'FLEX'),
            'transmission': features_raw.get('transmission', 'MANUAL'),
        },
        representative_models=row.get('representative_models') or [],
        image_url=row.get('image_url'),
        active=bool(row.get('active', True)),
        created_at=_dt(row.get('created_at')),
        updated_at=_dt(row.get('updated_at')),
    )


async def listar(usuario: UsuarioPayload, db: AsyncSurreal) -> list[CategoriaVeiculoResponse]:
    result = await db.query(
        """
        SELECT * FROM vehicle_category
        WHERE company = type::record($company_id) AND active = true
        ORDER BY group_name ASC
        """,
        {'company_id': usuario.locadoraId},
    )
    records = extract_records(result)
    return [_row_to_response(r) for r in records if isinstance(r, dict)]


async def buscar_por_id(
    categoria_id: str,
    usuario: UsuarioPayload,
    db: AsyncSurreal,
) -> CategoriaVeiculoResponse:
    result = await db.query(
        """
        SELECT * FROM type::record($id)
        WHERE company = type::record($company_id)
        LIMIT 1
        """,
        {'id': categoria_id, 'company_id': usuario.locadoraId},
    )
    records = extract_records(result)
    if not records:
        raise HTTPException(status_code=404, detail='Categoria não encontrada.')
    return _row_to_response(records[0])


async def criar(
    payload: CategoriaVeiculoRequest,
    usuario: UsuarioPayload,
    db: AsyncSurreal,
) -> CategoriaVeiculoResponse:
    dup = await db.query(
        "SELECT id FROM vehicle_category WHERE company = type::record($cid) AND code = $code LIMIT 1",
        {'cid': usuario.locadoraId, 'code': payload.code.upper()},
    )
    if extract_records(dup):
        raise HTTPException(status_code=409, detail='Já existe uma categoria com este código.')

    result = await db.query(
        """
        CREATE vehicle_category CONTENT {
            code:                  $code,
            group_name:            $group_name,
            acriss_code:           $acriss_code,
            description:           $description,
            company:               type::record($company_id),
            features:              $features,
            representative_models: $representative_models,
            image_url:             $image_url,
            active:                true
        }
        """,
        {
            'code':                  payload.code.upper(),
            'group_name':            payload.group_name,
            'acriss_code':           payload.acriss_code.upper() if payload.acriss_code else None,
            'description':           payload.description,
            'company_id':            usuario.locadoraId,
            'features':              payload.features.model_dump(),
            'representative_models': payload.representative_models,
            'image_url':             payload.image_url,
        },
    )

    records = extract_records(result)
    if not records:
        raise HTTPException(status_code=500, detail='Erro ao criar categoria.')

    row = records[0]
    if isinstance(row, dict):
        return _row_to_response(row)
    return await buscar_por_id(str(row), usuario, db)


async def atualizar(
    categoria_id: str,
    payload: CategoriaVeiculoRequest,
    usuario: UsuarioPayload,
    db: AsyncSurreal,
) -> CategoriaVeiculoResponse:
    exists = await db.query(
        "SELECT id FROM type::record($id) WHERE company = type::record($cid) LIMIT 1",
        {'id': categoria_id, 'cid': usuario.locadoraId},
    )
    if not extract_records(exists):
        raise HTTPException(status_code=404, detail='Categoria não encontrada.')

    # Verifica duplicidade de código apenas se mudou
    dup = await db.query(
        """
        SELECT id FROM vehicle_category
        WHERE company = type::record($cid) AND code = $code AND id != type::record($id)
        LIMIT 1
        """,
        {'cid': usuario.locadoraId, 'code': payload.code.upper(), 'id': categoria_id},
    )
    if extract_records(dup):
        raise HTTPException(status_code=409, detail='Já existe outra categoria com este código.')

    result = await db.query(
        """
        UPDATE type::record($id) MERGE {
            code:                  $code,
            group_name:            $group_name,
            acriss_code:           $acriss_code,
            description:           $description,
            features:              $features,
            representative_models: $representative_models,
            image_url:             $image_url
        }
        """,
        {
            'id':                    categoria_id,
            'code':                  payload.code.upper(),
            'group_name':            payload.group_name,
            'acriss_code':           payload.acriss_code.upper() if payload.acriss_code else None,
            'description':           payload.description,
            'features':              payload.features.model_dump(),
            'representative_models': payload.representative_models,
            'image_url':             payload.image_url,
        },
    )

    records = extract_records(result)
    if not records:
        raise HTTPException(status_code=500, detail='Erro ao atualizar categoria.')

    row = records[0]
    if isinstance(row, dict):
        return _row_to_response(row)
    return await buscar_por_id(categoria_id, usuario, db)
