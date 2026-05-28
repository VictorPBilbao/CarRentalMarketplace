from fastapi import HTTPException
from surrealdb import AsyncSurreal

from app.core.database import extract_records
from app.schemas.tarifa import AddonPricingRequest, AddonRequest, AddonResponse


def _s(v: object) -> str:
    return str(v) if v is not None else ''


def _addon_row_to_response(row: dict) -> AddonResponse:
    pricing = row.get('pricing', {})
    return AddonResponse(
        id=_s(row['id']),
        name=row.get('name', ''),
        description=row.get('description', ''),
        type=row.get('type', ''),
        active=bool(row.get('active', True)),
        stores=[_s(s) for s in (row.get('stores') or [])],
        pricing=AddonPricingRequest(
            amount=float(pricing.get('amount', 0)),
            calculation_type=pricing.get('calculation_type', 'PER_TRIP'),
            max_amount_per_trip=float(pricing['max_amount_per_trip']) if pricing.get('max_amount_per_trip') is not None else None,
        ),
        created_at=str(row.get('created_at', '')),
        updated_at=str(row.get('updated_at', '')),
    )


async def listar_addons_empresa(company_id: str, db: AsyncSurreal) -> list[AddonResponse]:
    result = await db.query(
        "SELECT * FROM addon WHERE company = type::record($cid) ORDER BY name ASC",
        {'cid': company_id},
    )
    rows = extract_records(result)
    return [_addon_row_to_response(r) for r in rows if isinstance(r, dict)]


async def criar_addon(payload: AddonRequest, company_id: str, db: AsyncSurreal) -> AddonResponse:
    result = await db.query(
        """
        CREATE addon CONTENT {
            company:     type::record($cid),
            name:        $name,
            description: $description,
            type:        $type,
            active:      $active,
            stores:      $stores,
            pricing: {
                amount:              $amount,
                calculation_type:    $calc_type,
                max_amount_per_trip: $max_per_trip
            }
        }
        """,
        {
            'cid': company_id,
            'name': payload.name,
            'description': payload.description,
            'type': payload.type,
            'active': payload.active,
            'stores': [f'store:{s.split(":")[-1]}' if ':' not in s else s for s in payload.stores],
            'amount': payload.pricing.amount,
            'calc_type': payload.pricing.calculation_type,
            'max_per_trip': payload.pricing.max_amount_per_trip,
        },
    )
    rows = extract_records(result)
    if not rows:
        raise HTTPException(status_code=500, detail='Erro ao criar addon.')
    row = rows[0]
    if not isinstance(row, dict):
        result2 = await db.query("SELECT * FROM type::record($id)", {'id': str(row)})
        rows2 = extract_records(result2)
        row = rows2[0] if rows2 else {}
    return _addon_row_to_response(row)


async def atualizar_addon(addon_id: str, payload: AddonRequest, company_id: str, db: AsyncSurreal) -> AddonResponse:
    check = await db.query(
        "SELECT id FROM type::record($id) WHERE company = type::record($cid) LIMIT 1",
        {'id': addon_id, 'cid': company_id},
    )
    if not extract_records(check):
        raise HTTPException(status_code=404, detail='Addon não encontrado.')

    await db.query(
        """
        UPDATE type::record($id) MERGE {
            name:        $name,
            description: $description,
            type:        $type,
            active:      $active,
            stores:      $stores,
            pricing: {
                amount:              $amount,
                calculation_type:    $calc_type,
                max_amount_per_trip: $max_per_trip
            }
        }
        """,
        {
            'id': addon_id,
            'name': payload.name,
            'description': payload.description,
            'type': payload.type,
            'active': payload.active,
            'stores': payload.stores,
            'amount': payload.pricing.amount,
            'calc_type': payload.pricing.calculation_type,
            'max_per_trip': payload.pricing.max_amount_per_trip,
        },
    )
    result = await db.query("SELECT * FROM type::record($id)", {'id': addon_id})
    rows = extract_records(result)
    return _addon_row_to_response(rows[0])


async def desativar_addon(addon_id: str, company_id: str, db: AsyncSurreal) -> None:
    check = await db.query(
        "SELECT id FROM type::record($id) WHERE company = type::record($cid) LIMIT 1",
        {'id': addon_id, 'cid': company_id},
    )
    if not extract_records(check):
        raise HTTPException(status_code=404, detail='Addon não encontrado.')
    await db.query("UPDATE type::record($id) MERGE { active: false }", {'id': addon_id})
