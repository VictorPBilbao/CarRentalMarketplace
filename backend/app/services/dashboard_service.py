from datetime import datetime, timezone

from fastapi import HTTPException, status
from surrealdb import AsyncSurreal

from app.schemas.dashboard import (
    ContratosStats,
    DashboardResponse,
    FiliaisStats,
    FrotaStats,
    ReservaRecente,
    ReservasStats,
)
from app.core.database import extract_records
from app.schemas.usuario import UsuarioPayload


def _fmt_dt(value: object) -> str:
    """Converte datetime (objeto ou string ISO) para 'DD/MM HH:MM'."""
    try:
        if isinstance(value, datetime):
            return value.strftime("%d/%m %H:%M")
        if isinstance(value, str):
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return dt.strftime("%d/%m %H:%M")
    except Exception:
        pass
    return str(value)


async def get_dashboard(usuario: UsuarioPayload, db: AsyncSurreal) -> DashboardResponse:
    company_id = usuario.locadoraId

    # ── 1. Frota ──────────────────────────────────────────────────────────────
    frota_rows = await db.query(
        """
        SELECT status, count() AS total
        FROM vehicle
        WHERE company = type::record($company_id)
        GROUP BY status
        """,
        {"company_id": company_id},
    )

    frota_records = extract_records(frota_rows)
    frota_map: dict[str, int] = {r.get("status"): r.get("total") for r in frota_records if isinstance(r, dict)}
    frota = FrotaStats(
        total=sum(frota_map.values()),
        disponivel=frota_map.get("AVAILABLE", 0),
        alugado=frota_map.get("RENTED", 0),
        manutencao=frota_map.get("MAINTENANCE", 0),
        em_transito=frota_map.get("IN_TRANSIT", 0),
    )

    # ── 2. Reservas por status ────────────────────────────────────────────────
    reserva_rows = await db.query(
        """
        SELECT status, count() AS total
        FROM reservation
        WHERE pickup_store.company = type::record($company_id)
        GROUP BY status
        """,
        {"company_id": company_id},
    )

    res_records = extract_records(reserva_rows)
    res_map: dict[str, int] = {r.get("status"): r.get("total") for r in res_records if isinstance(r, dict)}

    # ── 3. Retiradas e devoluções de hoje ─────────────────────────────────────
    hoje_retirada_rows = await db.query(
        """
        SELECT count() AS total
        FROM reservation
        WHERE pickup_store.company = type::record($company_id)
          AND time::floor(pickup_time, 1d) = time::floor(time::now(), 1d)
          AND status INSIDE ['CONFIRMED', 'ACTIVE']
        GROUP ALL
        """,
        {"company_id": company_id},
    )

    hoje_devolucao_rows = await db.query(
        """
        SELECT count() AS total
        FROM reservation
        WHERE pickup_store.company = type::record($company_id)
          AND time::floor(dropoff_time, 1d) = time::floor(time::now(), 1d)
          AND status = 'ACTIVE'
        GROUP ALL
        """,
        {"company_id": company_id},
    )

    hoje_r_records = extract_records(hoje_retirada_rows)
    hoje_retirada = (hoje_r_records[0].get("total", 0) if hoje_r_records and isinstance(hoje_r_records[0], dict) else 0)
    
    hoje_d_records = extract_records(hoje_devolucao_rows)
    hoje_devolucao = (hoje_d_records[0].get("total", 0) if hoje_d_records and isinstance(hoje_d_records[0], dict) else 0)

    reservas = ReservasStats(
        pendente=res_map.get("PENDING", 0),
        confirmada=res_map.get("CONFIRMED", 0),
        ativa=res_map.get("ACTIVE", 0),
        hoje_retirada=hoje_retirada,
        hoje_devolucao=hoje_devolucao,
    )

    # ── 4. Contratos em aberto ────────────────────────────────────────────────
    contratos_rows = await db.query(
        """
        SELECT count() AS total
        FROM rental_agreement
        WHERE vehicle.company = type::record($company_id)
          AND status = 'OPEN'
        GROUP ALL
        """,
        {"company_id": company_id},
    )

    cont_records = extract_records(contratos_rows)
    contratos = ContratosStats(
        aberto=(cont_records[0].get("total", 0) if cont_records and isinstance(cont_records[0], dict) else 0),
    )

    # ── 5. Filiais ────────────────────────────────────────────────────────────
    filiais_rows = await db.query(
        """
        SELECT count() AS total, count(active = true) AS ativas
        FROM store
        WHERE company = type::record($company_id)
        GROUP ALL
        """,
        {"company_id": company_id},
    )

    fil_records = extract_records(filiais_rows)
    filiais_data = fil_records[0] if fil_records and isinstance(fil_records[0], dict) else {}
    
    filiais = FiliaisStats(
        total=filiais_data.get("total", 0),
        ativas=filiais_data.get("ativas", 0),
    )

    # ── 6. Reservas recentes ──────────────────────────────────────────────────
    recentes_rows = await db.query(
        """
        SELECT
            id,
            created_at,
            customer.first_name AS primeiro_nome,
            customer.last_name  AS ultimo_nome,
            category.group_name AS categoria,
            pickup_store.name   AS filial,
            pickup_time,
            dropoff_time,
            status,
            pricing.total_amount AS valor
        FROM reservation
        WHERE pickup_store.company = type::record($company_id)
        ORDER BY created_at DESC
        LIMIT 10
        FETCH customer, category, pickup_store
        """,
        {"company_id": company_id},
    )

    rec_records = extract_records(recentes_rows)
    reservas_recentes: list[ReservaRecente] = []
    
    for row in rec_records:
        if not isinstance(row, dict):
            continue
        reservas_recentes.append(
            ReservaRecente(
                id=str(row.get("id", "")).split(":")[-1],
                cliente=f"{row.get('primeiro_nome', '')} {row.get('ultimo_nome', '')}".strip(),
                categoria=row.get("categoria") or "—",
                filial=row.get("filial") or "—",
                retirada=_fmt_dt(row.get("pickup_time")),
                devolucao=_fmt_dt(row.get("dropoff_time")),
                status=row.get("status", ""),
                valor=float(row.get("valor") or 0),
            )
        )

    return DashboardResponse(
        frota=frota,
        reservas=reservas,
        contratos=contratos,
        filiais=filiais,
        reservas_recentes=reservas_recentes,
    )
