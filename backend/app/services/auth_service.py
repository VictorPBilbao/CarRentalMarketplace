from fastapi import HTTPException, status
from surrealdb import AsyncSurreal

from app.core.config import settings
from app.core.security import criar_token, hash_senha, verificar_senha
from app.schemas.auth import CadastroLocadoraRequest, CadastroResponse, LoginRequest, LoginResponse
from app.schemas.usuario import UsuarioPayload

async def login(payload: LoginRequest, db: AsyncSurreal) -> LoginResponse:
    resultado = await db.query(
        """
        SELECT id, first_name, last_name, email, password_hash,
               ->manages.out.id AS locadora_ids,
               ->manages.role   AS manage_roles
        FROM user WHERE email = $email LIMIT 1
        """,
        {"email": payload.email},
    )

    registros = resultado[0].get("result", [])
    if not registros:
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")

    user = registros[0]

    if not verificar_senha(payload.senha, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")

    locadora_ids: list = user.get("locadora_ids") or []
    manage_roles: list = user.get("manage_roles") or []

    if not locadora_ids:
        raise HTTPException(status_code=403, detail="Usuário sem locadora associada.")

    locadora_id = str(locadora_ids[0])
    manage_role = (manage_roles[0] if manage_roles else "ADMIN").upper()

    role: str = "locadora" if manage_role in ("OWNER", "ADMIN") else "filial"

    token_payload = UsuarioPayload(
        id=str(user["id"]),
        nome=f"{user['first_name']} {user['last_name']}",
        email=user["email"],
        role=role,
        locadoraId=locadora_id,
    )

    token = criar_token(token_payload.model_dump(exclude_none=True))
    return LoginResponse(token=token)


async def cadastrar(payload: CadastroLocadoraRequest, db: AsyncSurreal) -> CadastroResponse:
    cnpj_limpo = ''.join(c for c in payload.cnpj if c.isdigit())

    # ── unicidade de e-mail ───────────────────────────────────────────────────
    resultado_email = await db.query(
        "SELECT id FROM user WHERE email = $email LIMIT 1",
        {"email": payload.email},
    )
    if resultado_email and resultado_email[0].get("result"):
        raise HTTPException(status_code=409, detail="E-mail já cadastrado.")

    # ── unicidade de CNPJ ─────────────────────────────────────────────────────
    resultado_cnpj = await db.query(
        "SELECT id FROM company WHERE tax_id = $tax_id LIMIT 1",
        {"tax_id": cnpj_limpo},
    )
    if resultado_cnpj and resultado_cnpj[0].get("result"):
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

    company = company_result[0]["result"][0]
    company_id: str = str(company["id"])

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

    user = user_result[0]["result"][0]
    user_id: str = str(user["id"])

    # ── cria relação manages (OWNER) ──────────────────────────────────────────
    await db.query(
        """
        RELATE $user_id->manages->$company_id CONTENT { role: 'OWNER' }
        """,
        {"user_id": user_id, "company_id": company_id},
    )

    return CadastroResponse(locadoraId=company_id, mensagem="Cadastro realizado com sucesso.")
