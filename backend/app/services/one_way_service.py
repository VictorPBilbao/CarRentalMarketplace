from decimal import Decimal

from fastapi import HTTPException
from surrealdb import AsyncSurreal

from app.core.database import extract_records
from app.schemas.tarifa import OneWayRequest, OneWayResponse


def _s(v: object) -> str:
    return str(v) if v is not None else ''


async def listar_one_way_filial(store_id: str, db: AsyncSurreal) -> list[OneWayResponse]:
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
        f"""
        RELATE {payload.from_store_id}->allows_return_to->{store_id} CONTENT {{
            active: $active,
            fee: {{
                type:   $fee_type,
                amount: $amount
            }}
        }}
        """,
        {
            'active': payload.active,
            'fee_type': payload.fee_type,
            'amount': Decimal(str(payload.amount)),
        },
    )
    rows = extract_records(result)
    if not rows:
        raise HTTPException(status_code=500, detail='Erro ao criar regra one-way.')

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
