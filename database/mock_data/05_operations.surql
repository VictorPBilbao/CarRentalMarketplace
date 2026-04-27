-- ------------------------------
-- LOTE 5: OPERACIONAL (RESERVAS, CONTRATOS E DISPONIBILIDADE)
-- ------------------------------

-- ------------------------------
-- RESERVAS (RESERVATIONS)
-- Nota: O schema exige que pickup_time > time::now(), então as reservas apontam para o futuro.
-- ------------------------------

-- Reserva 1: Cliente da Localiza, pegando em Congonhas e devolvendo em Guarulhos (One-Way)
CREATE reservation:res_loc_1 CONTENT {
    customer: user:cliente1,
    category: vehicle_category:loc_eco,
    pickup_store: store:cgh_localiza,
    dropoff_store: store:gru_localiza,
    pickup_time: time::now() + 1d,
    dropoff_time: time::now() + 4d,
    flight_number: 'LA3344',
    notes: 'Cliente solicitou cadeirinha de bebê e lavagem antecipada.',
    status: 'ACTIVE',
    pricing: {
        total_days: 3,
        daily_rate: 90.00,
        fees: 80.00, -- 80 da taxa de devolução
        total_amount: 350.00,
        breakdown: [
            { type: 'BASE_RATE', amount: 270.00, description: '3 diárias x R$ 90 (Tarifa Flexível)' },
            { type: 'LOGISTICS_FEE', amount: 80.00, description: 'Taxa de Retorno (Drop-off GRU)' }
        ]
    }
};

-- Reserva 2: Cliente da Movida, final de semana
CREATE reservation:res_mov_1 CONTENT {
    customer: user:cliente2,
    category: vehicle_category:mov_eco,
    pickup_store: store:sdumont_movida,
    dropoff_store: store:sdumont_movida,
    pickup_time: time::now() + 2d,
    dropoff_time: time::now() + 4d,
    flight_number: NONE,
    notes: 'Reserva Promocional de Fim de Semana',
    status: 'CONFIRMED',
    pricing: {
        total_days: 2,
        daily_rate: 75.00,
        fees: 0.00,
        total_amount: 150.00,
        breakdown: [
            { type: 'BASE_RATE', amount: 150.00, description: '2 diárias Promoção Fim de Semana' }
        ]
    }
};

-- ------------------------------
-- CONTRATOS DE ALUGUEL (RENTAL AGREEMENTS)
-- ------------------------------

-- O cliente 1 já retirou o veículo da Localiza (Status OPEN_
CREATE rental_agreement:ra_loc_1 CONTENT {
    reservation: reservation:res_loc_1,
    customer: user:cliente1,
    vehicle: vehicle:loc_kwid_1,
    contract_number: 'LOC-2026-001',
    status: 'OPEN',
    signed_contract_url: 'https://exemplo.localiza.com/contracts/LOC-2026-001.pdf',
    extra_charges: 0.00,
    checkout: {
        employee: user:atendente_sp_localiza,
        store: store:cgh_localiza,
        time: time::now(),
        mileage: 15400,
        fuel_level: 100, -- Tanque cheio
        notes: 'Veículo em perfeitas condições. Cadeira de bebê instalada no banco traseiro.',
        photo_urls: [
            'https://storage.exemplo.com/photos/kwid_frente.jpg',
            'https://storage.exemplo.com/photos/kwid_painel.jpg'
        ]
    },
    checkin: NONE
};

-- ------------------------------
-- LIVRO DE DISPONIBILIDADE (AVAILABILITY LEDGER)
-- (Opcional, mas ótimo para dashboards)
-- ------------------------------

CREATE availability_ledger CONTENT {
    store: store:cgh_localiza,
    category: vehicle_category:loc_eco,
    block_date: time::now() + 1d,
    total_fleet: 10,
    total_booked: 1,
    total_maintenance: 1
};

CREATE availability_ledger CONTENT {
    store: store:sdumont_movida,
    category: vehicle_category:mov_eco,
    block_date: time::now() + 2d,
    total_fleet: 5,
    total_booked: 1,
    total_maintenance: 0
};
