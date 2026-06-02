from fastapi import HTTPException, status
from surrealdb import AsyncSurreal

from app.core.config import settings
from app.core.database import extract_records
from app.core.security import criar_token, hash_senha, verificar_senha
from app.schemas.auth import (
    CadastroClienteRequest,
    CadastroClienteResponse,
    CadastroLocadoraRequest,
    CadastroResponse,
    LoginRequest,
    LoginResponse,
    StoreOption,
)
from app.schemas.usuario import UsuarioPayload

async def login(payload: LoginRequest, db: AsyncSurreal) -> LoginResponse:
    resultado = await db.query(
        """
        SELECT id, first_name, last_name, email, password_hash, is_admin,
               ->manages.out.id   AS locadora_ids,
               ->manages.role     AS manage_roles,
               ->works_at.out.id   AS filial_ids,
               ->works_at.out.name AS filial_names,
               ->works_at.out.company AS filial_company_ids
        FROM user WHERE email = $email AND active = true LIMIT 1
        """,
        {"email": payload.email},
    )

    if not resultado:
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")

    user = resultado[0]

    if not verificar_senha(payload.senha, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")

    locadora_ids:       list = user.get("locadora_ids")       or []
    manage_roles:       list = user.get("manage_roles")       or []
    filial_ids:         list = user.get("filial_ids")         or []
    filial_names:       list = user.get("filial_names")       or []
    filial_company_ids: list = user.get("filial_company_ids") or []

    nome = f"{user['first_name']} {user['last_name']}"

    # ── usuário gerencia uma empresa (OWNER ou ADMIN) ─────────────────────────
    if locadora_ids:
        locadora_id = str(locadora_ids[0])

        token_payload = UsuarioPayload(
            id=str(user["id"]),
            nome=nome,
            email=user["email"],
            role="locadora",
            locadoraId=locadora_id,
        )

    # ── funcionário de filial (works_at) ──────────────────────────────────────
    elif filial_ids:
        # Múltiplas filiais → pede seleção se nenhuma foi informada
        if len(filial_ids) > 1 and not payload.store_id:
            stores = [
                StoreOption(id=str(fid), name=str(fname))
                for fid, fname in zip(filial_ids, filial_names)
            ]
            return LoginResponse(stores=stores)

        chosen_id = payload.store_id if payload.store_id else str(filial_ids[0])
        # Valida que o store escolhido pertence ao funcionário
        filial_ids_str = [str(f) for f in filial_ids]
        if chosen_id not in filial_ids_str:
            raise HTTPException(status_code=403, detail="Filial não autorizada para este usuário.")

        idx = filial_ids_str.index(chosen_id)
        company_id = str(filial_company_ids[idx]) if idx < len(filial_company_ids) else None

        if not company_id:
            raise HTTPException(status_code=403, detail="Filial sem empresa associada.")

        token_payload = UsuarioPayload(
            id=str(user["id"]),
            nome=nome,
            email=user["email"],
            role="filial",
            locadoraId=company_id,
            matrizId=chosen_id,
            filialIds=[str(f) for f in filial_ids],
            filialNames=[str(n) for n in filial_names],
        )

    else:
        # Sem vínculo empresarial → admin do sistema (is_admin=true) ou cliente final
        role = "admin" if bool(user.get("is_admin", False)) else "customer"
        token_payload = UsuarioPayload(
            id=str(user["id"]),
            nome=nome,
            email=user["email"],
            role=role,
            locadoraId="",
        )

    token = criar_token(token_payload.model_dump(exclude_none=True))
    return LoginResponse(token=token)


async def me(usuario: UsuarioPayload, db: AsyncSurreal) -> UsuarioPayload:
    resultado = await db.query(
        "SELECT id FROM user WHERE email = $email AND active = true LIMIT 1",
        {"email": usuario.email},
    )
    if not resultado:
        raise HTTPException(status_code=401, detail="Usuário não encontrado ou inativo.")
    return usuario


async def cadastrar(payload: CadastroLocadoraRequest, db: AsyncSurreal) -> CadastroResponse:
    cnpj_limpo = ''.join(c for c in payload.cnpj if c.isdigit())

    # ── unicidade de e-mail ───────────────────────────────────────────────────
    resultado_email = await db.query(
        "SELECT id FROM user WHERE email = $email LIMIT 1",
        {"email": payload.email},
    )
    if resultado_email:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado.")

    # ── unicidade de CNPJ ─────────────────────────────────────────────────────
    resultado_cnpj = await db.query(
        "SELECT id FROM company WHERE tax_id = $tax_id LIMIT 1",
        {"tax_id": cnpj_limpo},
    )
    if resultado_cnpj:
        raise HTTPException(status_code=409, detail="CNPJ já cadastrado.")

    # ── cria company ──────────────────────────────────────────────────────────
    partes_nome = payload.nomeResponsavel.strip().split(" ", 1)
    primeiro_nome = partes_nome[0]
    ultimo_nome = partes_nome[1] if len(partes_nome) > 1 else primeiro_nome

    company_result = await db.query(
        """
        CREATE company CONTENT {
            name:    $name,
            tax_id:  $tax_id,
            contact: {
                email: $contact_email,
                phone: $phone
            },
            active: true
        }
        """,
        {
            "name": payload.nomeEmpresa,
            "tax_id": cnpj_limpo,
            "contact_email": payload.email,
            "phone": payload.telefone,
        },
    )

    company = company_result[0] if company_result else None
    if not company:
        raise HTTPException(status_code=500, detail="Erro ao criar a empresa no banco de dados.")

    # ── cria user ─────────────────────────────────────────────────────────────
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
            "first_name": primeiro_nome,
            "last_name": ultimo_nome,
            "email": payload.email,
            "password_hash": hash_senha(payload.senha),
        },
    )

    user = user_result[0] if user_result else None
    if not user:
        raise HTTPException(status_code=500, detail="Erro ao criar o usuário no banco de dados.")

    # ── cria relação manages (OWNER) — passa RecordID diretamente ─────────────
    await db.query(
        "RELATE $user_id->manages->$company_id CONTENT { role: 'OWNER' }",
        {"user_id": user["id"], "company_id": company["id"]},
    )

    return CadastroResponse(locadoraId=str(company["id"]), mensagem="Cadastro realizado com sucesso.")


async def cadastrar_cliente(payload: CadastroClienteRequest, db: AsyncSurreal) -> CadastroClienteResponse:
    resultado_email = await db.query(
        "SELECT id FROM user WHERE email = $email LIMIT 1",
        {"email": payload.email},
    )
    if resultado_email:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado.")

    user_result = await db.query(
        """
        CREATE user CONTENT {
            first_name:    $first_name,
            last_name:     $last_name,
            email:         $email,
            password_hash: $password_hash,
            phone:         $phone,
            active:        true
        }
        """,
        {
            "first_name":    payload.primeiroNome.strip(),
            "last_name":     payload.sobrenome.strip(),
            "email":         payload.email,
            "password_hash": hash_senha(payload.senha),
            "phone":         payload.telefone,
        },
    )

    user = user_result[0] if user_result else None
    if not user:
        raise HTTPException(status_code=500, detail="Erro ao criar o cliente.")

    return CadastroClienteResponse(userId=str(user["id"]), mensagem="Cadastro realizado com sucesso.")


async def trocar_filial(store_id: str, usuario: UsuarioPayload, db: AsyncSurreal) -> LoginResponse:
    result = await db.query(
        """
        SELECT ->works_at.out.id      AS filial_ids,
               ->works_at.out.name    AS filial_names,
               ->works_at.out.company AS filial_company_ids
        FROM type::record($uid) LIMIT 1
        """,
        {'uid': usuario.id},
    )
    records = extract_records(result)
    if not records:
        raise HTTPException(status_code=403, detail='Filial não autorizada.')

    row = records[0]
    filial_ids         = [str(f) for f in (row.get('filial_ids')         or [])]
    filial_names       = [str(n) for n in (row.get('filial_names')       or [])]
    filial_company_ids = row.get('filial_company_ids') or []

    if store_id not in filial_ids:
        raise HTTPException(status_code=403, detail='Filial não autorizada para este usuário.')

    idx = filial_ids.index(store_id)
    company_id = str(filial_company_ids[idx]) if idx < len(filial_company_ids) else None
    if not company_id:
        raise HTTPException(status_code=403, detail='Filial sem empresa associada.')

    token_payload = UsuarioPayload(
        id=usuario.id,
        nome=usuario.nome,
        email=usuario.email,
        role='filial',
        locadoraId=company_id,
        matrizId=store_id,
        filialIds=filial_ids,
        filialNames=filial_names,
    )
    token = criar_token(token_payload.model_dump(exclude_none=True))
    return LoginResponse(token=token)
