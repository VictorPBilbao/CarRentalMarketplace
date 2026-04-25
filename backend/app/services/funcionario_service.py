from datetime import datetime

from fastapi import HTTPException
from surrealdb import AsyncSurreal

from app.core.database import extract_records
from app.core.security import hash_senha
from app.schemas.funcionario import FuncionarioRequest, FuncionarioResponse
from app.schemas.usuario import UsuarioPayload


def _dt(v: object) -> str:
    if isinstance(v, datetime):
        return v.isoformat()
    return str(v) if v else ''


def _row_to_response(row: dict) -> FuncionarioResponse:
    user = row.get('in') or {}
    if not isinstance(user, dict):
        user = {}
    return FuncionarioResponse(
        id=str(user.get('id', '')),
        first_name=str(user.get('first_name', '')),
        last_name=str(user.get('last_name', '')),
        email=str(user.get('email', '')),
        role=str(row.get('role', 'CLERK')),
        active=bool(user.get('active', True)),
        created_at=_dt(row.get('created_at')),
    )


async def _verificar_filial(filial_id: str, usuario: UsuarioPayload, db: AsyncSurreal):
    rows = await db.query(
        "SELECT id FROM type::record($id) WHERE company = type::record($company_id) LIMIT 1",
        {'id': filial_id, 'company_id': usuario.locadoraId},
    )
    if not extract_records(rows):
        raise HTTPException(status_code=404, detail='Filial não encontrada.')


async def listar(filial_id: str, usuario: UsuarioPayload, db: AsyncSurreal) -> list[FuncionarioResponse]:
    await _verificar_filial(filial_id, usuario, db)

    rows = await db.query(
        """
        SELECT * FROM works_at
        WHERE out = type::record($filial_id)
        FETCH in
        """,
        {'filial_id': filial_id},
    )
    records = extract_records(rows)
    return [_row_to_response(r) for r in records if isinstance(r, dict)]


async def criar(
    filial_id: str,
    payload: FuncionarioRequest,
    usuario: UsuarioPayload,
    db: AsyncSurreal,
) -> FuncionarioResponse:
    await _verificar_filial(filial_id, usuario, db)

    existe = await db.query(
        "SELECT id FROM user WHERE email = $email LIMIT 1",
        {'email': payload.email},
    )
    if extract_records(existe):
        raise HTTPException(status_code=409, detail='E-mail já cadastrado.')

    user_result = await db.query(
        """
        CREATE user CONTENT {
            first_name:    $first_name,
            last_name:     $last_name,
            email:         $email,
            password_hash: $password_hash,
            active:        true
        }
        """,
        {
            'first_name':    payload.first_name,
            'last_name':     payload.last_name,
            'email':         payload.email,
            'password_hash': hash_senha(payload.senha),
        },
    )
    user_records = extract_records(user_result)

    if not user_records:
        raise HTTPException(status_code=500, detail='Erro ao criar usuário.')

    user = user_records[0]

    # Some SDK versions return the record ID string instead of a full dict
    if not isinstance(user, dict):
        fetched = await db.query(
            "SELECT * FROM user WHERE email = $email LIMIT 1",
            {'email': payload.email},
        )
        f_records = extract_records(fetched)
        if not f_records:
            raise HTTPException(status_code=500, detail='Erro ao criar usuário.')
        user = f_records[0]

    await db.query(
        """
        LET $u = type::record($user_id);
        LET $f = type::record($filial_id);
        RELATE $u->works_at->$f CONTENT { role: $role };
        """,
        {'user_id': user.get('id'), 'filial_id': filial_id, 'role': payload.role},
    )

    return FuncionarioResponse(
        id=str(user.get('id')),
        first_name=user.get('first_name'),
        last_name=user.get('last_name'),
        email=user.get('email'),
        role=payload.role,
        active=True,
        created_at='',
    )


async def remover(filial_id: str, user_id: str, usuario: UsuarioPayload, db: AsyncSurreal):
    await _verificar_filial(filial_id, usuario, db)

    await db.query(
        "DELETE works_at WHERE in = type::record($user_id) AND out = type::record($filial_id)",
        {'user_id': user_id, 'filial_id': filial_id},
    )
