from fastapi import HTTPException
from surrealdb import AsyncSurreal

from app.core.database import extract_records
from app.schemas.tarifa import FeeConditionsRequest, FeeRequest, FeeResponse, FeePricingRequest


def _s(v: object) -> str:
    return str(v) if v is not None else ''


def _fee_row_to_response(row: dict) -> FeeResponse:
    pricing = row.get('pricing', {})
    conds = row.get('conditions', {}) or {}
    return FeeResponse(
        id=_s(row['id']),
        name=row.get('name', ''),
        store=_s(row.get('store', '')),
        store_name=row.get('store_name'),
        store_code=row.get('store_code'),
        active=bool(row.get('active', True)),
        is_tax=bool(row.get('is_tax', False)),
        pricing=FeePricingRequest(
            amount=float(pricing.get('amount', 0)),
            calculation_type=pricing.get('calculation_type', 'FLAT_FEE'),
        ),
        conditions=FeeConditionsRequest(
            applies_after_time=conds.get('applies_after_time'),
            applies_before_time=conds.get('applies_before_time'),
        ),
    )


async def _verificar_loja_empresa(store_id: str, company_id: str, db: AsyncSurreal) -> None:
    check = await db.query(
        "SELECT id FROM type::record($sid) WHERE company = type::record($cid) LIMIT 1",
        {'sid': store_id, 'cid': company_id},
    )
    if not extract_records(check):
        raise HTTPException(status_code=403, detail='Loja não pertence à sua empresa.')


async def listar_fees_empresa(company_id: str, db: AsyncSurreal) -> list[FeeResponse]:
    result = await db.query(
        """
        SELECT *, store.name AS store_name, store.code AS store_code FROM fee
        WHERE store.company = type::record($cid)
        ORDER BY store ASC, name ASC
        """,
        {'cid': company_id},
    )
    rows = extract_records(result)
    return [_fee_row_to_response(r) for r in rows if isinstance(r, dict)]


async def criar_fee(payload: FeeRequest, company_id: str, db: AsyncSurreal) -> FeeResponse:
    await _verificar_loja_empresa(payload.store_id, company_id, db)

    result = await db.query(
        """
        CREATE fee CONTENT {
            store:  type::record($store_id),
            name:   $name,
            active: $active,
            is_tax: $is_tax,
            pricing: {
                amount:           $amount,
                calculation_type: $calc_type
            },
            conditions: {
                applies_after_time:  $after_time,
                applies_before_time: $before_time
            }
        }
        """,
        {
            'store_id': payload.store_id,
            'name': payload.name,
            'active': payload.active,
            'is_tax': payload.is_tax,
            'amount': payload.pricing.amount,
            'calc_type': payload.pricing.calculation_type,
            'after_time': payload.conditions.applies_after_time,
            'before_time': payload.conditions.applies_before_time,
        },
    )
    rows = extract_records(result)
    if not rows:
        raise HTTPException(status_code=500, detail='Erro ao criar taxa.')
    row = rows[0]
    if not isinstance(row, dict):
        result2 = await db.query(
            "SELECT *, store.name AS store_name, store.code AS store_code FROM type::record($id)",
            {'id': str(row)},
        )
        rows2 = extract_records(result2)
        row = rows2[0] if rows2 else {}
    else:
        result2 = await db.query(
            "SELECT *, store.name AS store_name, store.code AS store_code FROM type::record($id)",
            {'id': _s(row['id'])},
        )
        rows2 = extract_records(result2)
        row = rows2[0] if rows2 else row
    return _fee_row_to_response(row)


async def atualizar_fee(fee_id: str, payload: FeeRequest, company_id: str, db: AsyncSurreal) -> FeeResponse:
    check = await db.query(
        "SELECT id FROM type::record($id) WHERE store.company = type::record($cid) LIMIT 1",
        {'id': fee_id, 'cid': company_id},
    )
    if not extract_records(check):
        raise HTTPException(status_code=404, detail='Taxa não encontrada.')

    await db.query(
        """
        UPDATE type::record($id) MERGE {
            name:   $name,
            active: $active,
            is_tax: $is_tax,
            pricing: {
                amount:           $amount,
                calculation_type: $calc_type
            },
            conditions: {
                applies_after_time:  $after_time,
                applies_before_time: $before_time
            }
        }
        """,
        {
            'id': fee_id,
            'name': payload.name,
            'active': payload.active,
            'is_tax': payload.is_tax,
            'amount': payload.pricing.amount,
            'calc_type': payload.pricing.calculation_type,
            'after_time': payload.conditions.applies_after_time,
            'before_time': payload.conditions.applies_before_time,
        },
    )
    result = await db.query(
        "SELECT *, store.name AS store_name, store.code AS store_code FROM type::record($id)",
        {'id': fee_id},
    )
    rows = extract_records(result)
    return _fee_row_to_response(rows[0])


async def desativar_fee(fee_id: str, company_id: str, db: AsyncSurreal) -> None:
    check = await db.query(
        "SELECT id FROM type::record($id) WHERE store.company = type::record($cid) LIMIT 1",
        {'id': fee_id, 'cid': company_id},
    )
    if not extract_records(check):
        raise HTTPException(status_code=404, detail='Taxa não encontrada.')
    await db.query("UPDATE type::record($id) MERGE { active: false }", {'id': fee_id})
