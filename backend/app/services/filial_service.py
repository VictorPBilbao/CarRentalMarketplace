from datetime import datetime

from fastapi import HTTPException
from surrealdb import AsyncSurreal

from app.core.database import extract_records
from app.schemas.filial import FilialRequest, FilialResponse
from app.schemas.usuario import UsuarioPayload


def _dt(v: object) -> str:
    if isinstance(v, datetime):
        return v.isoformat()
    return str(v) if v else ''


def _parse_location(v: object) -> dict:
    """Converte o campo geometry<point> do SurrealDB → {latitude, longitude}."""
    if v is None:
        return {'latitude': 0.0, 'longitude': 0.0}
    # surrealdb SDK ≥1.x pode retornar objeto com atributos
    if hasattr(v, 'longitude') and hasattr(v, 'latitude'):
        return {'latitude': float(v.latitude), 'longitude': float(v.longitude)}
    if hasattr(v, 'coordinates'):
        c = v.coordinates
        return {'longitude': float(c[0]), 'latitude': float(c[1])}
    # GeoJSON dict padrão
    if isinstance(v, dict):
        if v.get('type') == 'Point':
            c = v.get('coordinates', [0.0, 0.0])
            return {'longitude': float(c[0]), 'latitude': float(c[1])}
        if 'latitude' in v:
            return {'latitude': float(v['latitude']), 'longitude': float(v['longitude'])}
    return {'latitude': 0.0, 'longitude': 0.0}


def _row_to_response(row: dict) -> FilialResponse:
    return FilialResponse(
        id=str(row['id']),
        name=row['name'],
        code=row['code'],
        location_type=row['location_type'],
        pickup_method=row['pickup_method'],
        address=row['address'],
        contact=row['contact'],
        location=_parse_location(row.get('location')),
        instructions=row.get('instructions') or {},
        operating_hours=row.get('operating_hours') or [],
        amenities=row.get('amenities') or [],
        active=bool(row.get('active', True)),
        created_at=_dt(row.get('created_at')),
        updated_at=_dt(row.get('updated_at')),
    )


async def listar(usuario: UsuarioPayload, db: AsyncSurreal) -> list[FilialResponse]:
    result = await db.query(
        """
        SELECT * FROM store
        WHERE company = type::record($company_id)
        ORDER BY name ASC
        """,
        {'company_id': usuario.locadoraId},
    )
    records = extract_records(result)
    return [_row_to_response(r) for r in records if isinstance(r, dict)]


async def buscar_por_id(filial_id: str, usuario: UsuarioPayload, db: AsyncSurreal) -> FilialResponse:
    result = await db.query(
        """
        SELECT * FROM type::record($id)
        WHERE company = type::record($company_id)
        LIMIT 1
        """,
        {'id': filial_id, 'company_id': usuario.locadoraId},
    )
    records = extract_records(result)
    if not records:
        raise HTTPException(status_code=404, detail='Filial não encontrada.')
    return _row_to_response(records[0])


async def criar(payload: FilialRequest, usuario: UsuarioPayload, db: AsyncSurreal) -> FilialResponse:
    dup_result = await db.query(
        "SELECT id FROM store WHERE company = type::record($cid) AND code = $code LIMIT 1",
        {'cid': usuario.locadoraId, 'code': payload.code.upper()},
    )
    if extract_records(dup_result):
        raise HTTPException(status_code=409, detail='Já existe uma filial com este código.')

    result = await db.query(
        f"""
        CREATE store SET
            name            = $name,
            code            = $code,
            location_type   = $location_type,
            pickup_method   = $pickup_method,
            company         = type::record($company_id),
            address         = $address,
            contact         = $contact,
            location        = type::point([{payload.location.longitude}, {payload.location.latitude}]),
            instructions    = $instructions,
            operating_hours = $operating_hours,
            amenities       = $amenities,
            active          = true
        """,
        {
            'name':            payload.name,
            'code':            payload.code.upper(),
            'location_type':   payload.location_type,
            'pickup_method':   payload.pickup_method,
            'company_id':      usuario.locadoraId,
            'address':         payload.address.model_dump(),
            'contact':         payload.contact.model_dump(),
            'instructions':    payload.instructions.model_dump(),
            'operating_hours': [h.model_dump() for h in payload.operating_hours],
            'amenities':       payload.amenities,
        },
    )

    records = extract_records(result)
    print(f"DEBUG RESULT: {result}", flush=True)
    if not records:
        # Debugging temporário: levantar erro com o conteúdo real do result
        raise HTTPException(status_code=500, detail=f'Erro ao criar filial. Result: {result}')

    row = records[0]
    if isinstance(row, str) and "Parse error" in row:
        raise HTTPException(status_code=500, detail=f'Erro no parse: {row}')
    if isinstance(row, str) and "error" in row.lower():
        raise HTTPException(status_code=500, detail=f'Erro BD: {row}')

    if isinstance(row, dict):
        return _row_to_response(row)
    # SDK returned record ID string instead of full record; re-fetch
    return await buscar_por_id(str(row), usuario, db)


async def atualizar(filial_id: str, payload: FilialRequest, usuario: UsuarioPayload, db: AsyncSurreal) -> FilialResponse:
    exists = await db.query(
        "SELECT id FROM type::record($id) WHERE company = type::record($cid) LIMIT 1",
        {'id': filial_id, 'cid': usuario.locadoraId},
    )
    if not extract_records(exists):
        raise HTTPException(status_code=404, detail='Filial não encontrada.')

    result = await db.query(
        """
        UPDATE type::record($id) MERGE {
            name:            $name,
            code:            $code,
            location_type:   $location_type,
            pickup_method:   $pickup_method,
            address:         $address,
            contact:         $contact,
            location:        $location,
            instructions:    $instructions,
            operating_hours: $operating_hours,
            amenities:       $amenities
        }
        """,
        {
            'id':             filial_id,
            'name':           payload.name,
            'code':           payload.code.upper(),
            'location_type':  payload.location_type,
            'pickup_method':  payload.pickup_method,
            'address':        payload.address.model_dump(),
            'contact':        payload.contact.model_dump(),
            'location':       {'type': 'Point', 'coordinates': [payload.location.longitude, payload.location.latitude]},
            'instructions':   payload.instructions.model_dump(),
            'operating_hours': [h.model_dump() for h in payload.operating_hours],
            'amenities':      payload.amenities,
        },
    )

    records = extract_records(result)
    if not records:
        raise HTTPException(status_code=500, detail='Erro ao atualizar filial.')

    row = records[0]
    if isinstance(row, dict):
        return _row_to_response(row)
    # SDK returned record ID string instead of full record; re-fetch
    return await buscar_por_id(filial_id, usuario, db)
