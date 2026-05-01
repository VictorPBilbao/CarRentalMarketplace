from datetime import date, datetime, timedelta

from surrealdb import AsyncSurreal

from app.core.database import extract_records


def _datas_no_periodo(pickup: datetime, dropoff: datetime) -> list[date]:
    start = pickup.date()
    end = dropoff.date()
    days: list[date] = []
    current = start
    while current < end:
        days.append(current)
        current += timedelta(days=1)
    return days or [start]


async def _total_frota(store_id: str, category_id: str, db: AsyncSurreal) -> int:
    result = await db.query(
        """
        SELECT count() AS total FROM vehicle
        WHERE current_store = type::record($store)
          AND category = type::record($category)
          AND status != 'DECOMMISSIONED'
        GROUP ALL
        """,
        {'store': store_id, 'category': category_id},
    )
    rows = extract_records(result)
    return int(rows[0].get('total', 0)) if rows else 0


async def verificar_disponibilidade(
    store_id: str,
    category_id: str,
    pickup_time: datetime,
    dropoff_time: datetime,
    db: AsyncSurreal,
) -> int:
    """Retorna o mínimo de unidades disponíveis no período. 0 = sem disponibilidade."""
    total_fleet = await _total_frota(store_id, category_id, db)
    if total_fleet == 0:
        return 0

    datas = _datas_no_periodo(pickup_time, dropoff_time)
    min_disponivel = total_fleet

    for d in datas:
        result = await db.query(
            """
            SELECT total_booked, total_maintenance FROM availability_ledger
            WHERE store = type::record($store)
              AND category = type::record($category)
              AND time::floor(block_date, 1d) = time::floor(type::datetime($date_iso), 1d)
            LIMIT 1
            """,
            {'store': store_id, 'category': category_id, 'date_iso': d.isoformat() + 'T00:00:00Z'},
        )
        rows = extract_records(result)
        if rows and isinstance(rows[0], dict):
            booked = int(rows[0].get('total_booked', 0))
            manut = int(rows[0].get('total_maintenance', 0))
            disponivel = total_fleet - booked - manut
        else:
            disponivel = total_fleet
        min_disponivel = min(min_disponivel, disponivel)

    return max(min_disponivel, 0)


async def ocupar_disponibilidade(
    store_id: str,
    category_id: str,
    pickup_time: datetime,
    dropoff_time: datetime,
    db: AsyncSurreal,
) -> None:
    """Incrementa total_booked para cada dia do período."""
    total_fleet = await _total_frota(store_id, category_id, db)
    datas = _datas_no_periodo(pickup_time, dropoff_time)

    for d in datas:
        date_iso = d.isoformat() + 'T00:00:00Z'
        existing = await db.query(
            """
            SELECT id, total_booked FROM availability_ledger
            WHERE store = type::record($store)
              AND category = type::record($category)
              AND time::floor(block_date, 1d) = time::floor(type::datetime($date_iso), 1d)
            LIMIT 1
            """,
            {'store': store_id, 'category': category_id, 'date_iso': date_iso},
        )
        rows = extract_records(existing)
        if rows and isinstance(rows[0], dict):
            row_id = str(rows[0]['id'])
            booked = int(rows[0].get('total_booked', 0))
            await db.query(
                "UPDATE type::record($id) MERGE { total_booked: $booked }",
                {'id': row_id, 'booked': booked + 1},
            )
        else:
            await db.query(
                """
                CREATE availability_ledger CONTENT {
                    store:             type::record($store),
                    category:          type::record($category),
                    block_date:        type::datetime($date_iso),
                    total_fleet:       $fleet,
                    total_booked:      1,
                    total_maintenance: 0
                }
                """,
                {'store': store_id, 'category': category_id, 'date_iso': date_iso, 'fleet': total_fleet},
            )


async def liberar_disponibilidade(
    store_id: str,
    category_id: str,
    pickup_time: datetime,
    dropoff_time: datetime,
    db: AsyncSurreal,
) -> None:
    """Decrementa total_booked para cada dia do período (ao cancelar reserva)."""
    datas = _datas_no_periodo(pickup_time, dropoff_time)

    for d in datas:
        date_iso = d.isoformat() + 'T00:00:00Z'
        existing = await db.query(
            """
            SELECT id, total_booked FROM availability_ledger
            WHERE store = type::record($store)
              AND category = type::record($category)
              AND time::floor(block_date, 1d) = time::floor(type::datetime($date_iso), 1d)
            LIMIT 1
            """,
            {'store': store_id, 'category': category_id, 'date_iso': date_iso},
        )
        rows = extract_records(existing)
        if rows and isinstance(rows[0], dict):
            row_id = str(rows[0]['id'])
            booked = max(int(rows[0].get('total_booked', 0)) - 1, 0)
            await db.query(
                "UPDATE type::record($id) MERGE { total_booked: $booked }",
                {'id': row_id, 'booked': booked},
            )
