from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException
from loguru import logger
from surrealdb import AsyncSurreal

from app.core.database import extract_records
from app.services import disponibilidade_service
from app.schemas.reserva import (
    AtualizarStatusRequest,
    CriarReservaClienteRequest,
    CriarReservaRequest,
    ItemPricingResponse,
    PricingResponse,
    ReservaResponse,
)

TRANSICOES_VALIDAS: dict[str, list[str]] = {
    'PENDING':   ['CONFIRMED', 'CANCELLED'],
    'CONFIRMED': ['ACTIVE', 'CANCELLED', 'NO_SHOW'],
    'ACTIVE':    ['COMPLETED', 'CANCELLED'],
    'COMPLETED': [],
    'CANCELLED': [],
    'NO_SHOW':   [],
}


def _dt(v: object) -> str:
    if isinstance(v, datetime):
        return v.isoformat()
    return str(v) if v else ''


def _pricing_to_response(p: dict) -> PricingResponse:
    breakdown = [
        ItemPricingResponse(
            type=item.get('type', ''),
            description=item.get('description', ''),
            amount=float(item.get('amount', 0)),
        )
        for item in (p.get('breakdown') or [])
    ]
    return PricingResponse(
        daily_rate=float(p.get('daily_rate', 0)),
        total_days=int(p.get('total_days', 0)),
        fees=float(p.get('fees', 0)),
        total_amount=float(p.get('total_amount', 0)),
        breakdown=breakdown,
    )


def _row_to_response(row: dict) -> ReservaResponse:
    first = str(row.get('_cust_fn') or '')
    last  = str(row.get('_cust_ln') or '')
    customer_name = f"{first} {last}".strip() or str(row['customer'])

    return ReservaResponse(
        id=str(row['id']),
        customer=str(row['customer']),
        customer_name=customer_name,
        category=str(row['category']),
        category_name=str(row.get('_cat_name') or ''),
        category_code=str(row.get('_cat_code') or ''),
        pickup_store=str(row['pickup_store']),
        pickup_store_name=str(row.get('_pickup_name') or ''),
        dropoff_store=str(row['dropoff_store']),
        dropoff_store_name=str(row.get('_dropoff_name') or ''),
        pickup_time=_dt(row.get('pickup_time')),
        dropoff_time=_dt(row.get('dropoff_time')),
        flight_number=row.get('flight_number'),
        notes=row.get('notes'),
        pricing=_pricing_to_response(row.get('pricing', {})),
        status=row.get('status', 'PENDING'),
        created_at=_dt(row.get('created_at')),
        updated_at=_dt(row.get('updated_at')),
    )


async def _check_loja(store_id: str, company_id: str, db: AsyncSurreal) -> None:
    result = await db.query(
        "SELECT id FROM store WHERE id = type::record($id) AND company = type::record($cid) LIMIT 1",
        {'id': store_id, 'cid': company_id},
    )
    if not extract_records(result):
        raise HTTPException(status_code=403, detail='Loja não pertence à sua empresa.')


async def _check_categoria(categoria_id: str, company_id: str, db: AsyncSurreal) -> None:
    result = await db.query(
        "SELECT id FROM vehicle_category WHERE id = type::record($id) AND company = type::record($cid) AND active = true LIMIT 1",
        {'id': categoria_id, 'cid': company_id},
    )
    if not extract_records(result):
        raise HTTPException(status_code=403, detail='Categoria não pertence à sua empresa ou está inativa.')


async def _get_company_from_store(store_id: str, db: AsyncSurreal) -> str:
    result = await db.query(
        "SELECT company FROM store WHERE id = type::record($id) LIMIT 1",
        {'id': store_id},
    )
    records = extract_records(result)
    if not records or not records[0].get('company'):
        raise HTTPException(status_code=404, detail='Loja não encontrada.')
    return str(records[0]['company'])


async def _check_customer(customer_id: str, db: AsyncSurreal) -> None:
    result = await db.query(
        "SELECT id FROM user WHERE id = type::record($id) AND active = true LIMIT 1",
        {'id': customer_id},
    )
    if not extract_records(result):
        raise HTTPException(status_code=404, detail='Cliente não encontrado ou inativo.')


async def listar(
    company_id: str,
    db: AsyncSurreal,
    store_id: str | None = None,
    status: str | None = None,
) -> list[ReservaResponse]:
    params: dict = {'cid': company_id}
    store_clause = ''
    status_clause = ''

    if store_id:
        store_clause = ' AND pickup_store = type::record($sid)'
        params['sid'] = store_id

    if status:
        status_clause = ' AND status = $status'
        params['status'] = status

    result = await db.query(
        f"""
        SELECT *,
            customer.first_name AS _cust_fn,
            customer.last_name  AS _cust_ln,
            category.group_name AS _cat_name,
            category.code       AS _cat_code,
            pickup_store.name   AS _pickup_name,
            dropoff_store.name  AS _dropoff_name
        FROM reservation
        WHERE pickup_store.company = type::record($cid){store_clause}{status_clause}
        ORDER BY created_at DESC
        """,
        params,
    )
    records = extract_records(result)
    return [_row_to_response(r) for r in records if isinstance(r, dict)]


async def buscar_por_id(
    reserva_id: str,
    company_id: str,
    db: AsyncSurreal,
    store_id: str | None = None,
) -> ReservaResponse:
    params: dict = {'id': reserva_id, 'cid': company_id}
    store_clause = ''

    if store_id:
        store_clause = ' AND pickup_store = type::record($sid)'
        params['sid'] = store_id

    result = await db.query(
        f"""
        SELECT *,
            customer.first_name AS _cust_fn,
            customer.last_name  AS _cust_ln,
            category.group_name AS _cat_name,
            category.code       AS _cat_code,
            pickup_store.name   AS _pickup_name,
            dropoff_store.name  AS _dropoff_name
        FROM reservation
        WHERE id = type::record($id)
          AND pickup_store.company = type::record($cid){store_clause}
        LIMIT 1
        """,
        params,
    )
    records = extract_records(result)
    if not records:
        raise HTTPException(status_code=404, detail='Reserva não encontrada.')
    return _row_to_response(records[0])


async def criar(
    payload: CriarReservaRequest,
    company_id: str,
    db: AsyncSurreal,
) -> ReservaResponse:
    await _check_loja(payload.pickup_store_id, company_id, db)
    await _check_loja(payload.dropoff_store_id, company_id, db)
    await _check_categoria(payload.category_id, company_id, db)
    await _check_customer(payload.customer_id, db)

    disponivel = await disponibilidade_service.verificar_disponibilidade(
        payload.pickup_store_id, payload.category_id,
        payload.pickup_time, payload.dropoff_time, db,
    )
    if disponivel <= 0:
        raise HTTPException(
            status_code=409,
            detail='Sem disponibilidade para a categoria solicitada nas datas informadas.',
        )

    base = payload.pricing.daily_rate * payload.pricing.total_days

    # Garante que existe pelo menos o item BASE_RATE no breakdown
    breakdown = [item.model_dump() for item in payload.pricing.breakdown]
    if not any(item['type'] == 'BASE_RATE' for item in breakdown):
        breakdown.insert(0, {
            'type': 'BASE_RATE',
            'description': f'{payload.pricing.total_days} dia(s) × R$ {payload.pricing.daily_rate:.2f}',
            'amount': base,
        })

    # Processar adicionais selecionados
    for sel in (payload.selected_addons or []):
        addon_rows = extract_records(await db.query(
            "SELECT name, pricing FROM addon WHERE id = type::record($id) AND active = true LIMIT 1",
            {'id': sel.addon_id},
        ))
        if not addon_rows:
            continue
        addon = addon_rows[0]
        pricing_cfg = addon.get('pricing', {})
        amount_cfg  = float(pricing_cfg.get('amount', 0))
        calc_type   = pricing_cfg.get('calculation_type', 'PER_TRIP')
        max_amt     = pricing_cfg.get('max_amount_per_trip')

        qty = max(sel.quantity, 1)
        if calc_type == 'PER_DAY':
            raw = amount_cfg * payload.pricing.total_days * qty
            if max_amt is not None:
                raw = min(raw, float(max_amt) * qty)
        elif calc_type == 'PERCENTAGE':
            raw = base * amount_cfg / 100 * qty
            if max_amt is not None:
                raw = min(raw, float(max_amt) * qty)
        else:  # PER_TRIP
            raw = amount_cfg * qty

        breakdown.append({
            'type': 'ADDON',
            'description': f'{addon.get("name", sel.addon_id)} × {qty}',
            'amount': round(raw, 2),
        })

    # total_amount = fees + itens não-taxa do breakdown (FEE/TAX já estão em pricing.fees)
    total_amount = payload.pricing.fees + sum(
        item['amount'] for item in breakdown if item['type'] not in ('FEE', 'TAX')
    )

    # Converte para Decimal — campos decimal no SurrealDB rejeitam float CBOR
    breakdown_db = [
        {**item, 'amount': Decimal(str(item['amount']))}
        for item in breakdown
    ]

    try:
        result = await db.query(
            """
            CREATE reservation CONTENT {
                customer:      type::record($customer_id),
                category:      type::record($category_id),
                pickup_store:  type::record($pickup_store_id),
                dropoff_store: type::record($dropoff_store_id),
                pickup_time:   type::datetime($pickup_time),
                dropoff_time:  type::datetime($dropoff_time),
                flight_number: $flight_number,
                notes:         $notes,
                status:        'PENDING',
                pricing: {
                    daily_rate:   $daily_rate,
                    total_days:   $total_days,
                    fees:         $fees,
                    total_amount: $total_amount,
                    breakdown:    $breakdown
                }
            }
            """,
            {
                'customer_id':      payload.customer_id,
                'category_id':      payload.category_id,
                'pickup_store_id':  payload.pickup_store_id,
                'dropoff_store_id': payload.dropoff_store_id,
                'pickup_time':      payload.pickup_time.isoformat(),
                'dropoff_time':     payload.dropoff_time.isoformat(),
                'flight_number':    payload.flight_number,
                'notes':            payload.notes,
                'daily_rate':       Decimal(str(payload.pricing.daily_rate)),
                'total_days':       payload.pricing.total_days,
                'fees':             Decimal(str(payload.pricing.fees)),
                'total_amount':     Decimal(str(total_amount)),
                'breakdown':        breakdown_db,
            },
        )
    except Exception as exc:
        msg = str(exc)
        if isinstance(exc, dict):
            msg = exc.get('message', msg)
        raise HTTPException(status_code=422, detail=f'Erro ao criar reserva: {msg}')

    records = extract_records(result)
    if not records:
        raise HTTPException(status_code=500, detail='Erro ao criar reserva.')

    await disponibilidade_service.ocupar_disponibilidade(
        payload.pickup_store_id, payload.category_id,
        payload.pickup_time, payload.dropoff_time, db,
    )

    row = records[0]
    if isinstance(row, dict):
        return _row_to_response(row)
    return await buscar_por_id(str(row), company_id, db)


async def listar_cliente(
    user_id: str,
    db: AsyncSurreal,
    status: str | None = None,
) -> list[ReservaResponse]:
    params: dict = {'uid': user_id}
    status_clause = ''
    if status:
        status_clause = ' AND status = $status'
        params['status'] = status

    result = await db.query(
        f"""
        SELECT *,
            category.group_name AS _cat_name,
            category.code       AS _cat_code,
            pickup_store.name   AS _pickup_name,
            dropoff_store.name  AS _dropoff_name
        FROM reservation
        WHERE customer = type::record($uid){status_clause}
        ORDER BY pickup_time ASC
        """,
        params,
    )
    records = extract_records(result)
    return [_row_to_response(r) for r in records if isinstance(r, dict)]


async def buscar_por_id_cliente(
    reserva_id: str,
    user_id: str,
    db: AsyncSurreal,
) -> ReservaResponse:
    result = await db.query(
        """
        SELECT *,
            category.group_name AS _cat_name,
            category.code       AS _cat_code,
            pickup_store.name   AS _pickup_name,
            dropoff_store.name  AS _dropoff_name
        FROM reservation
        WHERE id = type::record($id)
          AND customer = type::record($uid)
        LIMIT 1
        """,
        {'id': reserva_id, 'uid': user_id},
    )
    records = extract_records(result)
    if not records:
        raise HTTPException(status_code=404, detail='Reserva não encontrada.')
    return _row_to_response(records[0])


async def atualizar_status(
    reserva_id: str,
    payload: AtualizarStatusRequest,
    company_id: str,
    db: AsyncSurreal,
    store_id: str | None = None,
) -> ReservaResponse:
    reserva = await buscar_por_id(reserva_id, company_id, db, store_id)

    permitidos = TRANSICOES_VALIDAS.get(reserva.status, [])
    if payload.status not in permitidos:
        raise HTTPException(
            status_code=422,
            detail=f"Transição '{reserva.status}' → '{payload.status}' não é permitida.",
        )

    result = await db.query(
        "UPDATE type::record($id) MERGE { status: $status }",
        {'id': reserva_id, 'status': payload.status},
    )

    if payload.status in ('CANCELLED', 'NO_SHOW', 'COMPLETED'):
        try:
            pickup = datetime.fromisoformat(reserva.pickup_time)
            dropoff = datetime.fromisoformat(reserva.dropoff_time)
            await disponibilidade_service.liberar_disponibilidade(
                reserva.pickup_store, reserva.category,
                pickup, dropoff, db,
            )
        except Exception as exc:
            logger.warning(f"Falha ao liberar disponibilidade na reserva {reserva_id}: {exc}")

    records = extract_records(result)
    if not records:
        raise HTTPException(status_code=500, detail='Erro ao atualizar status da reserva.')

    row = records[0]
    if isinstance(row, dict):
        return _row_to_response(row)
    return await buscar_por_id(reserva_id, company_id, db)


async def criar_cliente(
    payload: CriarReservaClienteRequest,
    user_id: str,
    db: AsyncSurreal,
) -> ReservaResponse:
    company_id = await _get_company_from_store(payload.pickup_store_id, db)
    full = CriarReservaRequest(
        customer_id=user_id,
        category_id=payload.category_id,
        pickup_store_id=payload.pickup_store_id,
        dropoff_store_id=payload.dropoff_store_id,
        pickup_time=payload.pickup_time,
        dropoff_time=payload.dropoff_time,
        flight_number=payload.flight_number,
        notes=payload.notes,
        pricing=payload.pricing,
        selected_addons=payload.selected_addons,
    )
    return await criar(full, company_id, db)
