from fastapi import HTTPException, status
from surrealdb import AsyncSurreal

from app.core.config import settings
from app.core.security import criar_token, hash_senha, verificar_senha
from app.schemas.auth import (
    CadastroClienteRequest,
    CadastroClienteResponse,
    CadastroLocadoraRequest,
    CadastroResponse,
    LoginRequest,
    LoginResponse,
)
from app.schemas.usuario import UsuarioPayload

async def login(payload: LoginRequest, db: AsyncSurreal) -> LoginResponse:
    resultado = await db.query(
        """
        SELECT id, first_name, last_name, email, password_hash,
               ->manages.out.id  AS locadora_ids,
               ->manages.role    AS manage_roles,
               ->works_at.out.id AS filial_ids,
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

    locadora_ids:      list = user.get("locadora_ids")      or []
    manage_roles:      list = user.get("manage_roles")      or []
    filial_ids:        list = user.get("filial_ids")        or []
    filial_company_ids: list = user.get("filial_company_ids") or []

    nome = f"{user['first_name']} {user['last_name']}"

    # ── usuário gerencia uma empresa (OWNER ou ADMIN) ─────────────────────────
    if locadora_ids:
        locadora_id = str(locadora_ids[0])
        manage_role = (manage_roles[0] if manage_roles else "ADMIN").upper()
        role = "locadora" if manage_role == "OWNER" else "admin"

        token_payload = UsuarioPayload(
            id=str(user["id"]),
            nome=nome,
            email=user["email"],
            role=role,
            locadoraId=locadora_id,
        )

    # ── funcionário de filial (works_at) ──────────────────────────────────────
    elif filial_ids:
        filial_id  = str(filial_ids[0])
        company_id = str(filial_company_ids[0]) if filial_company_ids else None

        if not company_id:
            raise HTTPException(status_code=403, detail="Filial sem empresa associada.")

        token_payload = UsuarioPayload(
            id=str(user["id"]),
            nome=nome,
            email=user["email"],
            role="filial",
            locadoraId=company_id,
            matrizId=filial_id,
        )

    else:
        # Sem vínculo empresarial → cliente final
        token_payload = UsuarioPayload(
            id=str(user["id"]),
            nome=nome,
            email=user["email"],
            role="customer",
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
