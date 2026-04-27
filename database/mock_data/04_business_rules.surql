-- ------------------------------
-- LOTE 4: REGRAS DE NEGÓCIO, LOGÍSTICA E PLANOS TARIFÁRIOS
-- ------------------------------

-- ------------------------------
-- CRIAR FILIAL EXTRA PARA LOGÍSTICA INTRA-COMPANY
-- Vamos criar a filial Guarulhos para podermos ver as transferências e devoluções.
-- ------------------------------
CREATE store:gru_localiza CONTENT {
    company: company:localiza,
    code: 'GRU',
    name: 'Localiza Aeroporto Guarulhos',
    location_type: 'AIRPORT',
    pickup_method: 'SHUTTLE',
    location: (-46.4730, -23.4355),
    address: {
        country: 'Brasil',
        state: 'SP',
        city: 'Guarulhos',
        neighborhood: 'Cumbica',
        street: 'Rodovia Hélio Smidt',
        number: 's/n',
        postal_code: '07190-100',
        complement: 'Terminal 2 Desembarque Oitão'
    },
    contact: {
        email: 'agencia.gru@localiza.com',
        phone: '+55 11 2445-0000',
        manager_name: 'Marcos Silva'
    },
    amenities: ['Wi-Fi', 'Van/Shuttle Gratuito', 'Café'],
    operating_hours: [
        { day_of_week: 'MONDAY', open: '00:00', close: '23:59', is_closed: false },
        { day_of_week: 'TUESDAY', open: '00:00', close: '23:59', is_closed: false },
        { day_of_week: 'WEDNESDAY', open: '00:00', close: '23:59', is_closed: false },
        { day_of_week: 'THURSDAY', open: '00:00', close: '23:59', is_closed: false },
        { day_of_week: 'FRIDAY', open: '00:00', close: '23:59', is_closed: false },
        { day_of_week: 'SATURDAY', open: '00:00', close: '23:59', is_closed: false },
        { day_of_week: 'SUNDAY', open: '00:00', close: '23:59', is_closed: false }
    ],
    instructions: {
        pickup: 'Pegue a van Localiza na calçada fora do desembarque do T2 ou T3.',
        dropoff: 'Siga as placas "Pátio Locadoras" na entrada do aeroporto.',
        extra: 'Funcionamento 24h.'
    }
};

-- ------------------------------
-- LOGÍSTICA ENTRE LOJAS (ALLOWS_RETURN_TO / CAN_SUPPLY_TO)
-- ------------------------------

-- Permitir devolução de um carro retirado em Congonhas (CGH) lá em Guarulhos (GRU)
RELATE store:cgh_localiza->allows_return_to->store:gru_localiza CONTENT {
    fee: { 
        amount: 80.00, 
        type: 'FIXED' 
    }
};

-- Permitir que Guarulhos (GRU) forneça carros de emergência para Congonhas (CGH)
RELATE store:gru_localiza->can_supply_to->store:cgh_localiza CONTENT {
    transfer_fee: 150.00,
    transit_time_hours: 2,
    allowed_categories: [vehicle_category:loc_eco, vehicle_category:loc_suv]
};


-- ------------------------------
-- PLANOS TARIFÁRIOS (RATE PLANS)
-- ------------------------------

-- Localiza: Tarifa Flexível (Km Livre, qualquer categoria, disponível em SP)
CREATE rate_plan:loc_flex CONTENT {
    company: company:localiza,
    name: 'Tarifa Flexível SP',
    priority: 10,
    conditions: {
        advance_booking_days: 0,
        allow_one_way: true,
        allowed_nationalities: [], -- Sem restrição
        categories: [vehicle_category:loc_eco, vehicle_category:loc_suv],
        max_age: NONE,
        max_days: NONE,
        min_age: 21,
        min_days: 1,
        promo_code: NONE,
        stores: [store:cgh_localiza, store:gru_localiza],
        valid_from: NONE,
        valid_to: NONE
    },
    included_protections: [],
    price: {
        currency: 'BRL',
        daily_rate: 90.00,
        extra_km_price: 0.00,
        included_km_per_day: 0,
        mileage_policy: 'UNLIMITED'
    }
};

-- Movida: Tarifa Promocional Fim de Semana (Km Controlada, Seguro Incluso, Apenas SDU)
CREATE rate_plan:mov_weekend CONTENT {
    company: company:movida,
    name: 'Promoção Fim de Semana Carioca',
    priority: 50, -- Maior prioridade sobrescreve tarifas base
    conditions: {
        advance_booking_days: 2, -- Tem que reservar com 2 dias de antecedência
        allow_one_way: false,    -- Devolver na mesma loja
        allowed_nationalities: [],
        categories: [vehicle_category:mov_eco],
        max_age: NONE,
        max_days: 4,             -- Máximo de 4 dias para configurar "fim de semana"
        min_age: 18,
        min_days: 2,
        promo_code: 'VERAO2024',
        stores: [store:sdumont_movida],
        valid_from: NONE,
        valid_to: NONE
    },
    included_protections: [protection:mov_completa],
    price: {
        currency: 'BRL',
        daily_rate: 75.00, 
        extra_km_price: 1.25, -- Cobrado por km excedente
        included_km_per_day: 150,
        mileage_policy: 'LIMITED'
    }
};
