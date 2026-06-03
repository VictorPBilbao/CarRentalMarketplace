from surrealdb import AsyncSurreal

from app.core.database import extract_records
from app.schemas.admin_dashboard import (
    AdminDashboardResponse,
    EmpresasStats,
    LojasStats,
    OtaKeyEmpresa,
    OtaKeysStats,
    ReservasAdminStats,
    StatusCount,
    VeiculosStats,
)


async def get_admin_dashboard(db: AsyncSurreal) -> AdminDashboardResponse:
    # ── 1. Empresas ───────────────────────────────────────────────────────────
    empresas_rows = await db.query("SELECT count() AS total FROM company GROUP ALL")
    empresas_records = extract_records(empresas_rows)
    empresas_total = (
        empresas_records[0].get("total", 0)
        if empresas_records and isinstance(empresas_records[0], dict)
        else 0
    )

    # ── 2. Lojas ──────────────────────────────────────────────────────────────
    lojas_rows = await db.query(
        "SELECT count() AS total, count(active = true) AS ativas FROM store GROUP ALL"
    )
    lojas_records = extract_records(lojas_rows)
    lojas_data = lojas_records[0] if lojas_records and isinstance(lojas_records[0], dict) else {}

    # ── 3. Veículos por status ────────────────────────────────────────────────
    veiculos_rows = await db.query(
        "SELECT status, count() AS qty FROM vehicle GROUP BY status"
    )
    veiculos_records = extract_records(veiculos_rows)
    veiculos_por_status = [
        StatusCount(status=r.get("status", ""), qty=r.get("qty", 0))
        for r in veiculos_records
        if isinstance(r, dict) and r.get("status")
    ]
    veiculos_total = sum(s.qty for s in veiculos_por_status)

    # ── 4. Reservas por status ────────────────────────────────────────────────
    reservas_rows = await db.query(
        "SELECT status, count() AS qty FROM reservation GROUP BY status"
    )
    reservas_records = extract_records(reservas_rows)
    reservas_por_status = [
        StatusCount(status=r.get("status", ""), qty=r.get("qty", 0))
        for r in reservas_records
        if isinstance(r, dict) and r.get("status")
    ]
    reservas_total = sum(s.qty for s in reservas_por_status)

    # ── 5. OTA keys ───────────────────────────────────────────────────────────
    ota_total_rows = await db.query("SELECT count() AS total FROM ota_key GROUP ALL")
    ota_total_records = extract_records(ota_total_rows)
    ota_total = (
        ota_total_records[0].get("total", 0)
        if ota_total_records and isinstance(ota_total_records[0], dict)
        else 0
    )

    ota_ativas_rows = await db.query(
        "SELECT count() AS total FROM ota_key WHERE active = true GROUP ALL"
    )
    ota_ativas_records = extract_records(ota_ativas_rows)
    ota_ativas = (
        ota_ativas_records[0].get("total", 0)
        if ota_ativas_records and isinstance(ota_ativas_records[0], dict)
        else 0
    )

    ota_empresa_rows = await db.query(
        """
        SELECT company.name AS empresa, count() AS total
        FROM ota_key
        WHERE active = true
        GROUP BY company
        """
    )
    ota_empresa_records = extract_records(ota_empresa_rows)
    ota_por_empresa = []
    for r in ota_empresa_records:
        if not isinstance(r, dict):
            continue
        empresa_val = r.get("empresa")
        if isinstance(empresa_val, list):
            empresa_val = empresa_val[0] if empresa_val else None
        ota_por_empresa.append(
            OtaKeyEmpresa(empresa=str(empresa_val) if empresa_val else "Sem empresa", total=r.get("total", 0))
        )

    return AdminDashboardResponse(
        empresas=EmpresasStats(total=empresas_total),
        lojas=LojasStats(
            total=lojas_data.get("total", 0),
            ativas=lojas_data.get("ativas", 0),
        ),
        veiculos=VeiculosStats(total=veiculos_total, por_status=veiculos_por_status),
        reservas=ReservasAdminStats(total=reservas_total, por_status=reservas_por_status),
        ota_keys=OtaKeysStats(
            total=ota_total,
            ativas=ota_ativas,
            por_empresa=ota_por_empresa,
        ),
    )
