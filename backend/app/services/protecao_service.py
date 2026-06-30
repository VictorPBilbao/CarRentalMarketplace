from decimal import Decimal

from fastapi import HTTPException
from surrealdb import AsyncSurreal

from app.core.database import extract_records
from app.schemas.tarifa import PricingMatrixItem, ProtecaoRequest, ProtecaoResponse


def _s(v: object) -> str:
    return str(v) if v is not None else ''


def _protecao_row_to_response(row: dict) -> ProtecaoResponse:
    matrix_raw = row.get('pricing_matrix') or []
    matrix = [
        PricingMatrixItem(
            category=_s(item.get('category', '')),
            daily_rate=float(item.get('daily_rate', 0)),
            deductible_amount=float(item.get('deductible_amount', 0)),
        )
        for item in matrix_raw
        if isinstance(item, dict)
    ]
    return ProtecaoResponse(
        id=_s(row['id']),
        name=row.get('name', ''),
        code=row.get('code', ''),
        pricing_matrix=matrix,
    )


async def listar_protecoes_empresa(company_id: str, db: AsyncSurreal) -> list[ProtecaoResponse]:
    result = await db.query(
        "SELECT * FROM protection WHERE company = type::record($cid) ORDER BY name ASC",
        {'cid': company_id},
    )
    rows = extract_records(result)
    return [_protecao_row_to_response(r) for r in rows if isinstance(r, dict)]


async def criar_protecao(payload: ProtecaoRequest, company_id: str, db: AsyncSurreal) -> ProtecaoResponse:
    matrix = [
        {
            'category': f'vehicle_category:{item.category.split(":")[-1]}' if ':' not in item.category else item.category,
            'daily_rate': Decimal(str(item.daily_rate)),
            'deductible_amount': Decimal(str(item.deductible_amount)),
        }
        for item in payload.pricing_matrix
    ]
    result = await db.query(
        """
        CREATE protection CONTENT {
            company:        type::record($cid),
            name:           $name,
            code:           $code,
            pricing_matrix: array::map($matrix, |$item| {
                category:          type::record($item.category),
                daily_rate:        $item.daily_rate,
                deductible_amount: $item.deductible_amount
            })
        }
        """,
        {'cid': company_id, 'name': payload.name, 'code': payload.code, 'matrix': matrix},
    )
    rows = extract_records(result)
    if not rows:
        raise HTTPException(status_code=500, detail='Erro ao criar proteção.')
    row = rows[0]
    if not isinstance(row, dict):
        result2 = await db.query("SELECT * FROM type::record($id)", {'id': str(row)})
        rows2 = extract_records(result2)
        row = rows2[0] if rows2 else {}
    return _protecao_row_to_response(row)


async def atualizar_protecao(prot_id: str, payload: ProtecaoRequest, company_id: str, db: AsyncSurreal) -> ProtecaoResponse:
    check = await db.query(
        "SELECT id FROM type::record($id) WHERE company = type::record($cid) LIMIT 1",
        {'id': prot_id, 'cid': company_id},
    )
    if not extract_records(check):
        raise HTTPException(status_code=404, detail='Proteção não encontrada.')

    matrix = [
        {
            'category': f'vehicle_category:{item.category.split(":")[-1]}' if ':' not in item.category else item.category,
            'daily_rate': Decimal(str(item.daily_rate)),
            'deductible_amount': Decimal(str(item.deductible_amount)),
        }
        for item in payload.pricing_matrix
    ]
    await db.query(
        """
        UPDATE type::record($id) MERGE {
            name:           $name,
            code:           $code,
            pricing_matrix: array::map($matrix, |$item| {
                category:          type::record($item.category),
                daily_rate:        $item.daily_rate,
                deductible_amount: $item.deductible_amount
            })
        }
        """,
        {'id': prot_id, 'name': payload.name, 'code': payload.code, 'matrix': matrix},
    )
    result = await db.query("SELECT * FROM type::record($id)", {'id': prot_id})
    rows = extract_records(result)
    return _protecao_row_to_response(rows[0])


async def excluir_protecao(prot_id: str, company_id: str, db: AsyncSurreal) -> None:
    check = await db.query(
        "SELECT id FROM type::record($id) WHERE company = type::record($cid) LIMIT 1",
        {'id': prot_id, 'cid': company_id},
    )
    if not extract_records(check):
        raise HTTPException(status_code=404, detail='Proteção não encontrada.')
    await db.query("DELETE type::record($id)", {'id': prot_id})
