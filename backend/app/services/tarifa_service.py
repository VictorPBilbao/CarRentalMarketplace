import asyncio
from datetime import date, datetime
from decimal import Decimal

from fastapi import HTTPException
from surrealdb import AsyncSurreal

from app.core.database import extract_records
from app.schemas.tarifa import (
    AddonDisponivel,
    AddonRequest,
    AddonResponse,
    AddonSelecionado,
    BuscarTarifasResponse,
    CotacaoRequest,
    CotacaoResponse,
    FeeCalculado,
    FeeRequest,
    FeeResponse,
    ItemCotacao,
    LojaAlternativa,
    OneWayRequest,
    OneWayResponse,
    ProtecaoIncluida,
    RatePlanDisponivel,
    TaxaOneWay,
)
from app.services import disponibilidade_service


def _total_days(pickup: datetime, dropoff: datetime) -> int:
    d = (dropoff.date() - pickup.date()).days
    return max(d, 1)


def _s(v: object) -> str:
    return str(v) if v is not None else ''


# ── Queries ao banco ──────────────────────────────────────────────────────────

async def _buscar_rate_plans(
    company_id: str,
    pickup_store_id: str,
    dropoff_store_id: str,
    category_id: str,
    pickup_time: datetime,
    dropoff_time: datetime,
    customer_age: int,
    promo_code: str | None,
    db: AsyncSurreal,
) -> list[dict]:
    total_days = _total_days(pickup_time, dropoff_time)
    is_one_way = pickup_store_id != dropoff_store_id
    advance_days = max((pickup_time.date() - date.today()).days, 0)

    result = await db.query(
        """
        SELECT * FROM rate_plan
        WHERE company = type::record($cid)
          AND active = true
          AND type::record($category) INSIDE conditions.categories
          AND (array::len(conditions.stores) = 0 OR type::record($pickup_store) INSIDE conditions.stores)
          AND $total_days >= conditions.min_days
          AND (conditions.max_days IS NONE OR $total_days <= conditions.max_days)
          AND $customer_age >= conditions.min_age
          AND (conditions.max_age IS NONE OR $customer_age <= conditions.max_age)
          AND (conditions.valid_from IS NONE OR conditions.valid_from <= type::datetime($pickup_time))
          AND (conditions.valid_to IS NONE OR conditions.valid_to >= type::datetime($dropoff_time))
          AND $advance_days >= conditions.advance_booking_days
          AND ($is_one_way = false OR conditions.allow_one_way = true)
          AND (conditions.promo_code IS NONE OR ($promo_code IS NOT NONE AND conditions.promo_code = $promo_code))
        ORDER BY price.daily_rate ASC
        """,
        {
            'cid': company_id,
            'category': category_id,
            'pickup_store': pickup_store_id,
            'total_days': total_days,
            'customer_age': customer_age,
            'pickup_time': pickup_time.isoformat(),
            'dropoff_time': dropoff_time.isoformat(),
            'advance_days': advance_days,
            'is_one_way': is_one_way,
            'promo_code': promo_code,
        },
    )
    return extract_records(result)


async def _buscar_fees(store_id: str, db: AsyncSurreal) -> list[dict]:
    result = await db.query(
        "SELECT * FROM fee WHERE store = type::record($sid) AND active = true",
        {'sid': store_id},
    )
    return extract_records(result)


async def _buscar_addons(company_id: str, pickup_store_id: str, db: AsyncSurreal) -> list[dict]:
    result = await db.query(
        """
        SELECT * FROM addon
        WHERE company = type::record($cid)
          AND active = true
          AND (array::len(stores) = 0 OR type::record($sid) INSIDE stores)
        ORDER BY name ASC
        """,
        {'cid': company_id, 'sid': pickup_store_id},
    )
    return extract_records(result)


async def _buscar_taxa_one_way(
    pickup_store_id: str,
    dropoff_store_id: str,
    db: AsyncSurreal,
) -> dict | None:
    if pickup_store_id == dropoff_store_id:
        return None
    result = await db.query(
        """
        SELECT fee, in, out FROM allows_return_to
        WHERE in = type::record($pickup) AND out = type::record($dropoff) AND active = true
        LIMIT 1
        """,
        {'pickup': pickup_store_id, 'dropoff': dropoff_store_id},
    )
    records = extract_records(result)
    return records[0] if records else None


async def _buscar_protecoes(
    company_id: str,
    protection_ids: list[str],
    category_id: str,
    db: AsyncSurreal,
) -> list[ProtecaoIncluida]:
    if not protection_ids:
        return []
    result = await db.query(
        "SELECT id, name, code, pricing_matrix FROM protection WHERE company = type::record($cid)",
        {'cid': company_id},
    )
    rows = extract_records(result)

    found: list[ProtecaoIncluida] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        prot_id = _s(row.get('id'))
        if prot_id not in protection_ids:
            continue
        for entry in (row.get('pricing_matrix') or []):
            if _s(entry.get('category')) == category_id:
                found.append(ProtecaoIncluida(
                    id=prot_id,
                    name=row.get('name', ''),
                    code=row.get('code', ''),
                    daily_rate=float(entry.get('daily_rate', 0)),
                    deductible_amount=float(entry.get('deductible_amount', 0)),
                ))
                break
    return found


# ── Conversores ───────────────────────────────────────────────────────────────

def _plan_to_response(plan: dict, total_days: int) -> RatePlanDisponivel:
    price = plan.get('price', {})
    conds = plan.get('conditions', {})
    daily_rate = float(price.get('daily_rate', 0))
    return RatePlanDisponivel(
        id=_s(plan['id']),
        name=plan.get('name', ''),
        daily_rate=daily_rate,
        total_days=total_days,
        subtotal=round(daily_rate * total_days, 2),
        mileage_policy=price.get('mileage_policy', 'UNLIMITED'),
        included_km_per_day=int(price.get('included_km_per_day', 0)),
        extra_km_price=float(price.get('extra_km_price', 0)),
        currency=price.get('currency', 'BRL'),
        included_protections=[_s(p) for p in (plan.get('included_protections') or [])],
        allow_one_way=bool(conds.get('allow_one_way', True)),
    )


def _addon_to_response(addon: dict) -> AddonDisponivel:
    pricing = addon.get('pricing', {})
    max_amt = pricing.get('max_amount_per_trip')
    return AddonDisponivel(
        id=_s(addon['id']),
        name=addon.get('name', ''),
        description=addon.get('description', ''),
        type=addon.get('type', ''),
        pricing_amount=float(pricing.get('amount', 0)),
        pricing_type=pricing.get('calculation_type', 'PER_TRIP'),
        max_amount_per_trip=float(max_amt) if max_amt is not None else None,
    )


def _fee_to_response(fee: dict) -> FeeCalculado:
    pricing = fee.get('pricing', {})
    conds = fee.get('conditions', {}) or {}
    return FeeCalculado(
        id=_s(fee['id']),
        name=fee.get('name', ''),
        amount=float(pricing.get('amount', 0)),
        calculation_type=pricing.get('calculation_type', 'FLAT_FEE'),
        applies_after_time=conds.get('applies_after_time'),
        applies_before_time=conds.get('applies_before_time'),
    )


def _addon_row_to_response(row: dict) -> AddonResponse:
    from app.schemas.tarifa import AddonPricingRequest
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


def _fee_row_to_response(row: dict) -> FeeResponse:
    from app.schemas.tarifa import FeeConditionsRequest, FeePricingRequest
    pricing = row.get('pricing', {})
    conds = row.get('conditions', {}) or {}
    return FeeResponse(
        id=_s(row['id']),
        name=row.get('name', ''),
        store=_s(row.get('store', '')),
        store_name=row.get('store_name'),
        store_code=row.get('store_code'),
        active=bool(row.get('active', True)),
        pricing=FeePricingRequest(
            amount=float(pricing.get('amount', 0)),
            calculation_type=pricing.get('calculation_type', 'FLAT_FEE'),
        ),
        conditions=FeeConditionsRequest(
            applies_after_time=conds.get('applies_after_time'),
            applies_before_time=conds.get('applies_before_time'),
        ),
    )


# ── Cálculos de valor ─────────────────────────────────────────────────────────

def _fee_applies(fee: FeeCalculado, pickup_time: datetime) -> bool:
    hm = pickup_time.strftime('%H:%M')
    if fee.applies_after_time and hm < fee.applies_after_time:
        return False
    if fee.applies_before_time and hm > fee.applies_before_time:
        return False
    return True


def _calc_fee_amount(fee: FeeCalculado, base_subtotal: float) -> float:
    if fee.calculation_type == 'PERCENTAGE':
        return round(base_subtotal * fee.amount / 100, 2)
    return round(fee.amount, 2)


def _calc_addon_amount(addon: AddonDisponivel, daily_rate: float, total_days: int, qty: int) -> float:
    if addon.pricing_type == 'PER_DAY':
        raw = addon.pricing_amount * total_days * qty
        if addon.max_amount_per_trip is not None:
            raw = min(raw, addon.max_amount_per_trip * qty)
    elif addon.pricing_type == 'PER_TRIP':
        raw = addon.pricing_amount * qty
    else:  # PERCENTAGE
        raw = daily_rate * total_days * addon.pricing_amount / 100 * qty
        if addon.max_amount_per_trip is not None:
            raw = min(raw, addon.max_amount_per_trip * qty)
    return round(raw, 2)


# ── Casos de uso públicos: busca/cotação ──────────────────────────────────────

async def buscar_tarifas(
    company_id: str,
    pickup_store_id: str,
    dropoff_store_id: str,
    category_id: str,
    pickup_time: datetime,
    dropoff_time: datetime,
    customer_age: int,
    promo_code: str | None,
    db: AsyncSurreal,
) -> BuscarTarifasResponse:
    total_days = _total_days(pickup_time, dropoff_time)
    is_one_way = pickup_store_id != dropoff_store_id

    plans_raw, fees_raw, addons_raw, one_way_raw, disponibilidade = await asyncio.gather(
        _buscar_rate_plans(
            company_id, pickup_store_id, dropoff_store_id, category_id,
            pickup_time, dropoff_time, customer_age, promo_code, db,
        ),
        _buscar_fees(pickup_store_id, db),
        _buscar_addons(company_id, pickup_store_id, db),
        _buscar_taxa_one_way(pickup_store_id, dropoff_store_id, db),
        disponibilidade_service.verificar_disponibilidade(
            pickup_store_id, category_id, pickup_time, dropoff_time, db,
        ),
    )

    one_way: TaxaOneWay | None = None
    if one_way_raw and isinstance(one_way_raw, dict):
        fee_data = one_way_raw.get('fee', {}) or {}
        one_way = TaxaOneWay(
            pickup_store=pickup_store_id,
            dropoff_store=dropoff_store_id,
            fee_type=fee_data.get('type', 'FREE'),
            amount=float(fee_data.get('amount', 0)),
        )

    # Estoque compartilhado: busca lojas vizinhas se sem disponibilidade
    lojas_alternativas: list[LojaAlternativa] = []
    if disponibilidade == 0:
        supply_result = await db.query(
            """
            SELECT out.id AS store_id, out.name AS store_name,
                   transit_time_hours, transfer_fee
            FROM can_supply_to
            WHERE in = type::record($store)
              AND active = true
              AND (array::len(allowed_categories) = 0 OR type::record($category) INSIDE allowed_categories)
            """,
            {'store': pickup_store_id, 'category': category_id},
        )
        supply_rows = extract_records(supply_result)
        for row in (supply_rows or []):
            if not isinstance(row, dict):
                continue
            alt_id = _s(row.get('store_id', ''))
            if not alt_id:
                continue
            alt_disp = await disponibilidade_service.verificar_disponibilidade(
                alt_id, category_id, pickup_time, dropoff_time, db,
            )
            if alt_disp > 0:
                lojas_alternativas.append(LojaAlternativa(
                    store_id=alt_id,
                    store_name=str(row.get('store_name', '')),
                    transit_time_hours=int(row.get('transit_time_hours', 0)),
                    transfer_fee=float(row.get('transfer_fee', 0)),
                    available_units=alt_disp,
                ))

    return BuscarTarifasResponse(
        total_days=total_days,
        is_one_way=is_one_way,
        rate_plans=[_plan_to_response(p, total_days) for p in plans_raw if isinstance(p, dict)],
        available_addons=[_addon_to_response(a) for a in addons_raw if isinstance(a, dict)],
        store_fees=[_fee_to_response(f) for f in fees_raw if isinstance(f, dict)],
        one_way_fee=one_way,
        disponibilidade=disponibilidade,
        lojas_alternativas=lojas_alternativas,
    )


# ── Listagem gerencial ────────────────────────────────────────────────────────

async def listar_rate_plans_empresa(company_id: str, db: AsyncSurreal) -> list[dict]:
    result = await db.query(
        """
        SELECT * FROM rate_plan
        WHERE company = type::record($cid)
        ORDER BY price.daily_rate ASC, priority DESC
        """,
        {'cid': company_id},
    )
    return extract_records(result)


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


async def listar_addons_empresa(company_id: str, db: AsyncSurreal) -> list[AddonResponse]:
    result = await db.query(
        """
        SELECT * FROM addon
        WHERE company = type::record($cid)
        ORDER BY name ASC
        """,
        {'cid': company_id},
    )
    rows = extract_records(result)
    return [_addon_row_to_response(r) for r in rows if isinstance(r, dict)]


# ── CRUD: Addon ───────────────────────────────────────────────────────────────

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
                amount:             $amount,
                calculation_type:   $calc_type,
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


# ── CRUD: Fee ─────────────────────────────────────────────────────────────────

async def _verificar_loja_empresa(store_id: str, company_id: str, db: AsyncSurreal) -> None:
    check = await db.query(
        "SELECT id FROM type::record($sid) WHERE company = type::record($cid) LIMIT 1",
        {'sid': store_id, 'cid': company_id},
    )
    if not extract_records(check):
        raise HTTPException(status_code=403, detail='Loja não pertence à sua empresa.')


async def criar_fee(payload: FeeRequest, company_id: str, db: AsyncSurreal) -> FeeResponse:
    await _verificar_loja_empresa(payload.store_id, company_id, db)

    result = await db.query(
        """
        CREATE fee CONTENT {
            store:  type::record($store_id),
            name:   $name,
            active: $active,
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


# ── CRUD: One-Way (allows_return_to) ─────────────────────────────────────────

async def listar_one_way_filial(store_id: str, db: AsyncSurreal) -> list[OneWayResponse]:
    """Lista regras one-way onde a loja atual é o destino (out)."""
    result = await db.query(
        """
        SELECT id, in, out, fee, active,
               in.name AS from_store_name
        FROM allows_return_to
        WHERE out = type::record($store)
        ORDER BY in ASC
        """,
        {'store': store_id},
    )
    rows = extract_records(result)
    out: list[OneWayResponse] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        fee_data = row.get('fee', {}) or {}
        out.append(OneWayResponse(
            id=_s(row['id']),
            from_store_id=_s(row.get('in', '')),
            from_store_name=str(row.get('from_store_name', '')),
            to_store_id=_s(row.get('out', '')),
            fee_type=fee_data.get('type', 'FREE'),
            amount=float(fee_data.get('amount', 0)),
            active=bool(row.get('active', True)),
        ))
    return out


async def criar_one_way(payload: OneWayRequest, store_id: str, db: AsyncSurreal) -> OneWayResponse:
    # Verifica se já existe
    existing = await db.query(
        """
        SELECT id FROM allows_return_to
        WHERE in = type::record($from) AND out = type::record($to)
        LIMIT 1
        """,
        {'from': payload.from_store_id, 'to': store_id},
    )
    if extract_records(existing):
        raise HTTPException(status_code=409, detail='Regra one-way já existe para este par de lojas.')

    result = await db.query(
        """
        RELATE type::record($from)->allows_return_to->type::record($to) CONTENT {
            active: $active,
            fee: {
                type:   $fee_type,
                amount: $amount
            }
        }
        """,
        {
            'from': payload.from_store_id,
            'to': store_id,
            'active': payload.active,
            'fee_type': payload.fee_type,
            'amount': Decimal(str(payload.amount)),
        },
    )
    rows = extract_records(result)
    if not rows:
        raise HTTPException(status_code=500, detail='Erro ao criar regra one-way.')

    # Fetch with store name
    rules = await listar_one_way_filial(store_id, db)
    row_id = _s(rows[0]['id']) if isinstance(rows[0], dict) else str(rows[0])
    found = next((r for r in rules if r.id == row_id), None)
    if found:
        return found
    raise HTTPException(status_code=500, detail='Erro ao recuperar regra one-way criada.')


async def atualizar_one_way(rule_id: str, payload: OneWayRequest, store_id: str, db: AsyncSurreal) -> OneWayResponse:
    check = await db.query(
        "SELECT id FROM type::record($id) WHERE out = type::record($store) LIMIT 1",
        {'id': rule_id, 'store': store_id},
    )
    if not extract_records(check):
        raise HTTPException(status_code=404, detail='Regra one-way não encontrada.')

    await db.query(
        """
        UPDATE type::record($id) MERGE {
            active: $active,
            fee: { type: $fee_type, amount: $amount }
        }
        """,
        {'id': rule_id, 'active': payload.active, 'fee_type': payload.fee_type, 'amount': Decimal(str(payload.amount))},
    )
    rules = await listar_one_way_filial(store_id, db)
    found = next((r for r in rules if r.id == rule_id), None)
    if not found:
        raise HTTPException(status_code=404, detail='Regra one-way não encontrada após atualização.')
    return found


async def excluir_one_way(rule_id: str, store_id: str, db: AsyncSurreal) -> None:
    check = await db.query(
        "SELECT id FROM type::record($id) WHERE out = type::record($store) LIMIT 1",
        {'id': rule_id, 'store': store_id},
    )
    if not extract_records(check):
        raise HTTPException(status_code=404, detail='Regra one-way não encontrada.')
    await db.query("DELETE type::record($id)", {'id': rule_id})


# ── Cotação completa ──────────────────────────────────────────────────────────

async def calcular_cotacao(
    payload: CotacaoRequest,
    company_id: str,
    db: AsyncSurreal,
) -> CotacaoResponse:
    total_days = _total_days(payload.pickup_time, payload.dropoff_time)
    is_one_way = payload.pickup_store_id != payload.dropoff_store_id

    plans_raw, fees_raw, addons_raw, one_way_raw = await asyncio.gather(
        _buscar_rate_plans(
            company_id, payload.pickup_store_id, payload.dropoff_store_id,
            payload.category_id, payload.pickup_time, payload.dropoff_time,
            payload.customer_age, payload.promo_code, db,
        ),
        _buscar_fees(payload.pickup_store_id, db),
        _buscar_addons(company_id, payload.pickup_store_id, db),
        _buscar_taxa_one_way(payload.pickup_store_id, payload.dropoff_store_id, db),
    )

    if not plans_raw:
        raise HTTPException(
            status_code=404,
            detail='Nenhum plano tarifário aplicável para os parâmetros informados.',
        )

    plans_response = [_plan_to_response(p, total_days) for p in plans_raw if isinstance(p, dict)]
    if payload.rate_plan_id:
        plan = next((p for p in plans_response if p.id == payload.rate_plan_id), None)
        if not plan:
            raise HTTPException(status_code=422, detail='O plano tarifário informado não é aplicável para estes parâmetros.')
    else:
        plan = plans_response[0]

    daily_rate = plan.daily_rate
    subtotal_base = round(daily_rate * total_days, 2)

    breakdown: list[ItemCotacao] = [
        ItemCotacao(
            type='BASE_RATE',
            description=f'{total_days} dia(s) × R$ {daily_rate:.2f} ({plan.name})',
            amount=subtotal_base,
        )
    ]

    fees_response = [_fee_to_response(f) for f in fees_raw if isinstance(f, dict)]
    fees_total = 0.0
    for fee in fees_response:
        if not _fee_applies(fee, payload.pickup_time):
            continue
        calculated = _calc_fee_amount(fee, subtotal_base)
        fees_total += calculated
        breakdown.append(ItemCotacao(type='FEE', description=fee.name, amount=calculated))

    addons_map = {_s(a['id']): a for a in addons_raw if isinstance(a, dict)}
    addons_total = 0.0
    for sel in payload.selected_addons:
        raw = addons_map.get(sel.addon_id)
        if not raw:
            raise HTTPException(status_code=422, detail=f'Adicional {sel.addon_id!r} não disponível para esta loja.')
        addon_resp = _addon_to_response(raw)
        calculated = _calc_addon_amount(addon_resp, daily_rate, total_days, sel.quantity)
        addons_total += calculated
        breakdown.append(ItemCotacao(type='ADDON', description=f'{addon_resp.name} × {sel.quantity}', amount=calculated))

    one_way_fee_amount = 0.0
    if is_one_way and one_way_raw and isinstance(one_way_raw, dict):
        fee_data = one_way_raw.get('fee', {}) or {}
        fee_type = fee_data.get('type', 'FREE')
        if fee_type == 'FIXED':
            one_way_fee_amount = float(fee_data.get('amount', 0))
        if one_way_fee_amount > 0:
            breakdown.append(ItemCotacao(
                type='LOGISTICS_FEE',
                description='Taxa de retorno (devolução em outra loja)',
                amount=one_way_fee_amount,
            ))

    final_total = round(subtotal_base + fees_total + addons_total + one_way_fee_amount, 2)
    protecoes = await _buscar_protecoes(company_id, plan.included_protections, payload.category_id, db)
    addons_response = [_addon_to_response(a) for a in addons_raw if isinstance(a, dict)]

    return CotacaoResponse(
        rate_plan_id=plan.id,
        rate_plan_name=plan.name,
        daily_rate=daily_rate,
        total_days=total_days,
        subtotal_base=subtotal_base,
        addons_total=round(addons_total, 2),
        fees_total=round(fees_total, 2),
        one_way_fee=round(one_way_fee_amount, 2),
        final_total=final_total,
        breakdown=breakdown,
        included_protections=protecoes,
        available_addons=addons_response,
    )
