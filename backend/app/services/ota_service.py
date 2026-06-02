import uuid

from fastapi import HTTPException
from surrealdb import AsyncSurreal

from app.core.database import extract_records
from app.schemas.ota import OtaKeyListItem, OtaKeyRequest, OtaKeyResponse


def _s(v: object) -> str:
    return str(v) if v is not None else ''


def _row_to_list_item(r: dict) -> OtaKeyListItem:
    company_raw = r.get('company') or {}
    company_id   = _s(company_raw.get('id', '')) if isinstance(company_raw, dict) else _s(company_raw)
    company_name = str(company_raw.get('name', '')) if isinstance(company_raw, dict) else ''
    key_full = str(r.get('key', ''))
    return OtaKeyListItem(
        id=_s(r.get('id')),
        name=str(r.get('name', '')),
        key_preview=key_full[:8] + '…' if len(key_full) >= 8 else key_full,
        company_id=company_id or None,
        company_name=company_name,
        active=bool(r.get('active', True)),
        created_at=_s(r.get('created_at')),
    )


def _row_to_response(r: dict, key_full: str | None = None) -> OtaKeyResponse:
    company_raw = r.get('company') or {}
    company_id   = _s(company_raw.get('id', '')) if isinstance(company_raw, dict) else _s(company_raw)
    company_name = str(company_raw.get('name', '')) if isinstance(company_raw, dict) else ''
    return OtaKeyResponse(
        id=_s(r.get('id')),
        name=str(r.get('name', '')),
        key=key_full or str(r.get('key', '')),
        company_id=company_id or None,
        company_name=company_name,
        active=bool(r.get('active', True)),
        created_at=_s(r.get('created_at')),
    )


async def listar_chaves(db: AsyncSurreal) -> list[OtaKeyListItem]:
    result = await db.query(
        "SELECT *, company FROM ota_key ORDER BY created_at DESC FETCH company"
    )
    rows = extract_records(result)
    return [_row_to_list_item(r) for r in rows if isinstance(r, dict)]


async def criar_chave(payload: OtaKeyRequest, db: AsyncSurreal) -> OtaKeyResponse:
    key = str(uuid.uuid4())
    result = await db.query(
        """
        CREATE ota_key CONTENT {
            name:       $name,
            key:        $key,
            company:    IF $company_id IS NOT NONE THEN type::record($company_id) ELSE NONE END,
            active:     true,
            created_at: time::now()
        }
        """,
        {'name': payload.name, 'key': key, 'company_id': payload.company_id},
    )
    rows = extract_records(result)
    if not rows:
        raise HTTPException(status_code=500, detail='Erro ao criar chave OTA.')
    row = rows[0]
    if not isinstance(row, dict):
        fetch = await db.query("SELECT * FROM type::record($id) FETCH company", {'id': str(row)})
        row = (extract_records(fetch) or [{}])[0]
    else:
        if payload.company_id:
            fetch = await db.query("SELECT * FROM type::record($id) FETCH company", {'id': _s(row.get('id'))})
            row = (extract_records(fetch) or [row])[0]
    return _row_to_response(row, key_full=key)


async def revogar_chave(key_id: str, db: AsyncSurreal) -> None:
    check = await db.query(
        "SELECT id FROM type::record($id) LIMIT 1",
        {'id': key_id},
    )
    if not extract_records(check):
        raise HTTPException(status_code=404, detail='Chave OTA não encontrada.')
    await db.query("UPDATE type::record($id) MERGE { active: false }", {'id': key_id})
