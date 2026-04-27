-- ------------------------------
-- LOTE 3: VEÍCULOS, ADICIONAIS, PROTEÇÕES E TAXAS
-- ------------------------------

-- ------------------------------
-- VEÍCULOS (FROTA)
-- ------------------------------
-- Veículos Localiza (CGH)
CREATE vehicle:loc_kwid_1 CONTENT {
    company: company:localiza,
    category: vehicle_category:loc_eco,
    current_store: store:cgh_localiza,
    plate: 'ABC1D23',
    chassis_number: '9BR1234567890ABCD',
    make: 'Renault',
    model: 'Kwid Zen 1.0',
    year: 2023,
    color: 'Branco',
    mileage_km: 15400,
    status: 'AVAILABLE'
};

CREATE vehicle:loc_renegade_1 CONTENT {
    company: company:localiza,
    category: vehicle_category:loc_suv,
    current_store: store:cgh_localiza,
    plate: 'XYZ9W87',
    chassis_number: '9BR9876543210WXYZ',
    make: 'Jeep',
    model: 'Renegade Sport 1.3 Turbo',
    year: 2024,
    color: 'Prata',
    mileage_km: 5200,
    status: 'AVAILABLE'
};

-- Veículos Movida (SDU)
CREATE vehicle:mov_polo_1 CONTENT {
    company: company:movida,
    category: vehicle_category:mov_eco,
    current_store: store:sdumont_movida,
    plate: 'RIO2A22',
    chassis_number: '9BW1112223334ABCD',
    make: 'Volkswagen',
    model: 'Polo Track 1.0 TSI',
    year: 2024,
    color: 'Preto',
    mileage_km: 8100,
    status: 'AVAILABLE'
};

-- ------------------------------
-- ADICIONAIS (ADDONS)
-- ------------------------------

-- Localiza Addons
CREATE addon:loc_cadeira_bebe CONTENT {
    company: company:localiza,
    name: 'Cadeira de Bebê',
    description: 'Assento de segurança obrigatório para crianças de 1 a 4 anos.',
    type: 'EQUIPMENT',
    pricing: {
        amount: 35.00,
        calculation_type: 'PER_DAY',
        max_amount_per_trip: 200.00
    }
};

CREATE addon:loc_lavagem CONTENT {
    company: company:localiza,
    name: 'Lavagem Garantida',
    description: 'Devolva o carro sujo sem se preocupar com taxas extras de limpeza simples.',
    type: 'SERVICE',
    pricing: {
        amount: 45.00,
        calculation_type: 'PER_TRIP'
    }
};

-- Movida Addons
CREATE addon:mov_gps CONTENT {
    company: company:movida,
    name: 'GPS Integrado',
    description: 'Sistema de navegação para facilitar sua viagem.',
    type: 'EQUIPMENT',
    pricing: {
        amount: 25.00,
        calculation_type: 'PER_DAY',
        max_amount_per_trip: 150.00
    }
};

-- ------------------------------
-- PROTEÇÕES (SEGUROS)
-- ------------------------------
CREATE protection:loc_basica CONTENT {
    company: company:localiza,
    code: 'PROT_BASICA',
    name: 'Proteção Básica do Veículo (LDW)',
    pricing_matrix: [
        {
            category: vehicle_category:loc_eco,
            daily_rate: 38.00,
            deductible_amount: 3000.00
        },
        {
            category: vehicle_category:loc_suv,
            daily_rate: 55.00,
            deductible_amount: 5000.00
        }
    ]
};

CREATE protection:mov_completa CONTENT {
    company: company:movida,
    code: 'PROT_COMPLETA',
    name: 'Proteção Completa (Casco + Terceiros)',
    pricing_matrix: [
        {
            category: vehicle_category:mov_eco,
            daily_rate: 65.00,
            deductible_amount: 1000.00
        }
    ]
};

-- ------------------------------
-- TAXAS LOCAIS (FEES)
-- ------------------------------
CREATE fee:loc_taxa_aeroporto_cgh CONTENT {
    name: 'Taxa Aeroportuária - Congonhas',
    store: store:cgh_localiza,
    pricing: {
        amount: 12.00,
        calculation_type: 'PERCENTAGE'
    },
    conditions: {
        applies_after_time: NONE,
        applies_before_time: NONE
    }
};

CREATE fee:mov_taxa_limpeza_pesada CONTENT {
    name: 'Taxa de Limpeza Pesada ou Estofado',
    store: store:sdumont_movida,
    pricing: {
        amount: 250.00,
        calculation_type: 'FLAT_FEE'
    },
    conditions: {
        applies_after_time: NONE,
        applies_before_time: NONE
    }
};
