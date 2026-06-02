from decimal import Decimal

from fastapi import HTTPException
from surrealdb import AsyncSurreal

from app.core.database import extract_records
from app.schemas.tarifa import (
    RatePlanConditionsRequest,
    RatePlanPriceRequest,
    RatePlanRequest,
    RatePlanResponse,
)


def _s(v: object) -> str:
    return str(v) if v is not None else ''


def _rate_plan_row_to_response(row: dict) -> RatePlanResponse:
    price = row.get('price', {})
    conds = row.get('conditions', {}) or {}
    return RatePlanResponse(
        id=_s(row['id']),
        name=row.get('name', ''),
        active=bool(row.get('active', True)),
        priority=int(row.get('priority', 0)),
        price=RatePlanPriceRequest(
            daily_rate=float(price.get('daily_rate', 0)),
            currency=price.get('currency', 'BRL'),
            mileage_policy=price.get('mileage_policy', 'UNLIMITED'),
            included_km_per_day=int(price.get('included_km_per_day', 0)),
            extra_km_price=float(price.get('extra_km_price', 0)),
        ),
        conditions=RatePlanConditionsRequest(
            categories=[_s(c) for c in (conds.get('categories') or [])],
            stores=[_s(s) for s in (conds.get('stores') or [])],
            min_days=int(conds.get('min_days', 1)),
            max_days=int(conds['max_days']) if conds.get('max_days') is not None else None,
            min_age=int(conds.get('min_age', 18)),
            max_age=int(conds['max_age']) if conds.get('max_age') is not None else None,
            advance_booking_days=int(conds.get('advance_booking_days', 0)),
            allow_one_way=bool(conds.get('allow_one_way', True)),
            valid_from=conds.get('valid_from'),
            valid_to=conds.get('valid_to'),
            promo_code=conds.get('promo_code'),
            allowed_nationalities=list(conds.get('allowed_nationalities') or []),
        ),
        included_protections=[_s(p) for p in (row.get('included_protections') or [])],
        created_at=str(row.get('created_at', '')),
        updated_at=str(row.get('updated_at', '')),
    )


async def listar_rate_plans_empresa(company_id: str, db: AsyncSurreal) -> list[RatePlanResponse]:
    result = await db.query(
        """
        SELECT * FROM rate_plan
        WHERE company = type::record($cid)
        ORDER BY priority DESC, price.daily_rate ASC
        """,
        {'cid': company_id},
    )
    rows = extract_records(result)
    return [_rate_plan_row_to_response(r) for r in rows if isinstance(r, dict)]


async def criar_rate_plan(payload: RatePlanRequest, company_id: str, db: AsyncSurreal) -> RatePlanResponse:
    categories = [f'vehicle_category:{c.split(":")[-1]}' if ':' not in c else c for c in payload.conditions.categories]
    stores = [f'store:{s.split(":")[-1]}' if ':' not in s else s for s in payload.conditions.stores]
    protections = [f'protection:{p.split(":")[-1]}' if ':' not in p else p for p in payload.included_protections]

    result = await db.query(
        """
        CREATE rate_plan CONTENT {
            company:              type::record($cid),
            name:                 $name,
            priority:             $priority,
            active:               $active,
            price: {
                daily_rate:           $daily_rate,
                currency:             $currency,
                mileage_policy:       $mileage_policy,
                included_km_per_day:  $included_km_per_day,
                extra_km_price:       $extra_km_price
            },
            conditions: {
                categories:            array::map($categories, |$c| type::record($c)),
                stores:                array::map($stores,     |$c| type::record($c)),
                min_days:              $min_days,
                max_days:              $max_days,
                min_age:               $min_age,
                max_age:               $max_age,
                advance_booking_days:  $advance_booking_days,
                allow_one_way:         $allow_one_way,
                valid_from:            IF $valid_from IS NOT NONE THEN type::datetime($valid_from) ELSE NONE END,
                valid_to:              IF $valid_to   IS NOT NONE THEN type::datetime($valid_to)   ELSE NONE END,
                promo_code:            $promo_code,
                allowed_nationalities: $allowed_nationalities
            },
            included_protections: array::map($included_protections, |$c| type::record($c))
        }
        """,
        {
            'cid': company_id,
            'name': payload.name,
            'priority': payload.priority,
            'active': payload.active,
            'daily_rate': Decimal(str(payload.price.daily_rate)),
            'currency': payload.price.currency,
            'mileage_policy': payload.price.mileage_policy,
            'included_km_per_day': payload.price.included_km_per_day,
            'extra_km_price': Decimal(str(payload.price.extra_km_price)),
            'categories': categories,
            'stores': stores,
            'min_days': payload.conditions.min_days,
            'max_days': payload.conditions.max_days,
            'min_age': payload.conditions.min_age,
            'max_age': payload.conditions.max_age,
            'advance_booking_days': payload.conditions.advance_booking_days,
            'allow_one_way': payload.conditions.allow_one_way,
            'valid_from': payload.conditions.valid_from.strftime('%Y-%m-%dT%H:%M:%SZ') if payload.conditions.valid_from else None,
            'valid_to': payload.conditions.valid_to.strftime('%Y-%m-%dT%H:%M:%SZ') if payload.conditions.valid_to else None,
            'promo_code': payload.conditions.promo_code,
            'allowed_nationalities': payload.conditions.allowed_nationalities,
            'included_protections': protections,
        },
    )
    if isinstance(result, list) and result and isinstance(result[0], dict):
        status = result[0].get('status')
        if status is not None and status != 'OK':
            surreal_err = result[0].get('result', 'Erro desconhecido no banco de dados.')
            raise HTTPException(status_code=500, detail=str(surreal_err))

    rows = extract_records(result)
    if not rows:
        raise HTTPException(status_code=500, detail='Erro ao criar plano tarifário: resultado vazio.')
    row = rows[0]
    if not isinstance(row, dict):
        result2 = await db.query("SELECT * FROM type::record($id)", {'id': str(row)})
        rows2 = extract_records(result2)
        row = rows2[0] if rows2 else {}
    return _rate_plan_row_to_response(row)


async def atualizar_rate_plan(plan_id: str, payload: RatePlanRequest, company_id: str, db: AsyncSurreal) -> RatePlanResponse:
    check = await db.query(
        "SELECT id FROM type::record($id) WHERE company = type::record($cid) LIMIT 1",
        {'id': plan_id, 'cid': company_id},
    )
    if not extract_records(check):
        raise HTTPException(status_code=404, detail='Plano tarifário não encontrado.')

    categories = [f'vehicle_category:{c.split(":")[-1]}' if ':' not in c else c for c in payload.conditions.categories]
    stores = [f'store:{s.split(":")[-1]}' if ':' not in s else s for s in payload.conditions.stores]
    protections = [f'protection:{p.split(":")[-1]}' if ':' not in p else p for p in payload.included_protections]

    await db.query(
        """
        UPDATE type::record($id) MERGE {
            name:                 $name,
            priority:             $priority,
            active:               $active,
            price: {
                daily_rate:           $daily_rate,
                currency:             $currency,
                mileage_policy:       $mileage_policy,
                included_km_per_day:  $included_km_per_day,
                extra_km_price:       $extra_km_price
            },
            conditions: {
                categories:            array::map($categories, |$c| type::record($c)),
                stores:                array::map($stores,     |$c| type::record($c)),
                min_days:              $min_days,
                max_days:              $max_days,
                min_age:               $min_age,
                max_age:               $max_age,
                advance_booking_days:  $advance_booking_days,
                allow_one_way:         $allow_one_way,
                valid_from:            IF $valid_from IS NOT NONE THEN type::datetime($valid_from) ELSE NONE END,
                valid_to:              IF $valid_to   IS NOT NONE THEN type::datetime($valid_to)   ELSE NONE END,
                promo_code:            $promo_code,
                allowed_nationalities: $allowed_nationalities
            },
            included_protections: array::map($included_protections, |$c| type::record($c))
        }
        """,
        {
            'id': plan_id,
            'name': payload.name,
            'priority': payload.priority,
            'active': payload.active,
            'daily_rate': Decimal(str(payload.price.daily_rate)),
            'currency': payload.price.currency,
            'mileage_policy': payload.price.mileage_policy,
            'included_km_per_day': payload.price.included_km_per_day,
            'extra_km_price': Decimal(str(payload.price.extra_km_price)),
            'categories': categories,
            'stores': stores,
            'min_days': payload.conditions.min_days,
            'max_days': payload.conditions.max_days,
            'min_age': payload.conditions.min_age,
            'max_age': payload.conditions.max_age,
            'advance_booking_days': payload.conditions.advance_booking_days,
            'allow_one_way': payload.conditions.allow_one_way,
            'valid_from': payload.conditions.valid_from.strftime('%Y-%m-%dT%H:%M:%SZ') if payload.conditions.valid_from else None,
            'valid_to': payload.conditions.valid_to.strftime('%Y-%m-%dT%H:%M:%SZ') if payload.conditions.valid_to else None,
            'promo_code': payload.conditions.promo_code,
            'allowed_nationalities': payload.conditions.allowed_nationalities,
            'included_protections': protections,
        },
    )
    result = await db.query("SELECT * FROM type::record($id)", {'id': plan_id})
    rows = extract_records(result)
    return _rate_plan_row_to_response(rows[0])


async def desativar_rate_plan(plan_id: str, company_id: str, db: AsyncSurreal) -> None:
    check = await db.query(
        "SELECT id FROM type::record($id) WHERE company = type::record($cid) LIMIT 1",
        {'id': plan_id, 'cid': company_id},
    )
    if not extract_records(check):
        raise HTTPException(status_code=404, detail='Plano tarifário não encontrado.')
    await db.query("UPDATE type::record($id) MERGE { active: false }", {'id': plan_id})


# ── Funções específicas para filial ───────────────────────────────────────────

async def criar_rate_plan_filial(
    payload: RatePlanRequest,
    company_id: str,
    store_id: str,
    db: AsyncSurreal,
) -> RatePlanResponse:
    # A filial só pode criar planos para a própria loja
    payload.conditions.stores = [store_id]
    return await criar_rate_plan(payload, company_id, db)


async def atualizar_rate_plan_filial(
    plan_id: str,
    payload: RatePlanRequest,
    company_id: str,
    store_id: str,
    db: AsyncSurreal,
) -> RatePlanResponse:
    check = await db.query(
        """
        SELECT id FROM type::record($id)
        WHERE company = type::record($cid)
          AND type::record($sid) INSIDE conditions.stores
        LIMIT 1
        """,
        {'id': plan_id, 'cid': company_id, 'sid': store_id},
    )
    if not extract_records(check):
        raise HTTPException(status_code=404, detail='Plano tarifário não encontrado para esta loja.')

    # Garante que a loja da filial permanece nos stores do plano
    if store_id not in payload.conditions.stores:
        payload.conditions.stores = [store_id]

    return await atualizar_rate_plan(plan_id, payload, company_id, db)


async def desativar_rate_plan_filial(
    plan_id: str,
    company_id: str,
    store_id: str,
    db: AsyncSurreal,
) -> None:
    check = await db.query(
        """
        SELECT id FROM type::record($id)
        WHERE company = type::record($cid)
          AND type::record($sid) INSIDE conditions.stores
        LIMIT 1
        """,
        {'id': plan_id, 'cid': company_id, 'sid': store_id},
    )
    if not extract_records(check):
        raise HTTPException(status_code=404, detail='Plano tarifário não encontrado para esta loja.')
    await db.query("UPDATE type::record($id) MERGE { active: false }", {'id': plan_id})
