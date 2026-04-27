-- ------------------------------
-- LOTE 1: EMPRESAS E USUÁRIOS
-- ------------------------------

-- EMPRESAS
-- Atualizando a 'Localiza' que já tem um INSERT no final do seu schema atual
CREATE company:localiza CONTENT {
    name: 'Localiza Rent a Car S.A.',
    trading_name: 'Localiza',
    tax_id: '16.670.085/0001-55',
    contact: {
        email: 'contato@localiza.com',
        phone: '+55 31 3247-7000'
    },
    website: 'https://www.localiza.com',
    logo_url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Localiza_logo.png/640px-Localiza_logo.png'
};

-- Criando a segunda empresa, Movida
CREATE company:movida CONTENT {
    name: 'Movida Participações S.A.',
    trading_name: 'Movida Rent a Car',
    tax_id: '07.976.147/0001-60',
    contact: {
        email: 'atendimento@movida.com.br',
        phone: '0800 606 8686'
    },
    website: 'https://www.movida.com.br',
    logo_url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Movida_logo.png/640px-Movida_logo.png'
};

-- ------------------------------
-- USUÁRIOS (CLIENTES)
-- ------------------------------
CREATE user:cliente1 CONTENT {
    first_name: 'João',
    last_name: 'Silva',
    email: 'joao.silva@email.com',
    password_hash: 'hash_do_joao_123',
    document_id: '123.456.789-00',
    phone: '+55 11 99999-1111',
    birth_date: d'1985-05-15T00:00:00Z'
};

CREATE user:cliente2 CONTENT {
    first_name: 'Maria',
    last_name: 'Oliveira',
    email: 'maria.oliveira@email.com',
    password_hash: 'hash_da_maria_456',
    document_id: '987.654.321-11',
    phone: '+55 21 98888-2222',
    birth_date: d'1990-10-20T00:00:00Z'
};

-- ------------------------------
-- USUÁRIOS (ADMINS/FUNCIONÁRIOS)
-- ------------------------------
-- Equipe Localiza
CREATE user:admin_localiza CONTENT {
    first_name: 'Roberto',
    last_name: 'Costa',
    email: 'roberto.costa@localiza.com',
    password_hash: 'admin123',
    document_id: '111.222.333-44',
    phone: '+55 31 97777-3333'
};

CREATE user:gerente_sp_localiza CONTENT {
    first_name: 'Ana',
    last_name: 'Santos',
    email: 'ana.santos@localiza.com',
    password_hash: 'gerente123',
    phone: '+55 11 96666-4444'
};

CREATE user:atendente_sp_localiza CONTENT {
    first_name: 'Carlos',
    last_name: 'Pereira',
    email: 'carlos.pereira@localiza.com',
    password_hash: 'atend123',
    phone: '+55 11 95555-5555'
};

-- Equipe Movida
CREATE user:admin_movida CONTENT {
    first_name: 'Fernanda',
    last_name: 'Lima',
    email: 'fernanda.lima@movida.com.br',
    password_hash: 'admin123',
    document_id: '444.555.666-77',
    phone: '+55 11 94444-6666'
};

CREATE user:gerente_rj_movida CONTENT {
    first_name: 'Pedro',
    last_name: 'Alves',
    email: 'pedro.alves@movida.com.br',
    password_hash: 'gerente123',
    phone: '+55 21 93333-7777'
};
