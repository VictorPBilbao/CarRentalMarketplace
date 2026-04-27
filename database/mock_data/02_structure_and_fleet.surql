-- ------------------------------
-- LOTE 2: ESTRUTURA (FILIAIS), RELAÇÕES TRABALHISTAS E CATEGORIAS DE VEÍCULOS
-- ------------------------------

-- ------------------------------
-- FILIAIS (STORES)
-- ------------------------------

-- Filiais Localiza (SP)
CREATE store:cgh_localiza CONTENT {
    company: company:localiza,
    code: 'CGH',
    name: 'Localiza Aeroporto Congonhas',
    location_type: 'AIRPORT',
    pickup_method: 'IN_TERMINAL',
    location: (-46.6622, -23.6273), -- Longitude, Latitude
    address: {
        country: 'Brasil',
        state: 'SP',
        city: 'São Paulo',
        neighborhood: 'Vila Congonhas',
        street: 'Av. Washington Luís',
        number: 's/n',
        postal_code: '04626-911',
        complement: 'Desembarque'
    },
    contact: {
        email: 'agencia.cgh@localiza.com',
        phone: '+55 11 5090-0000',
        manager_name: 'Ana Santos'
    },
    amenities: ['Wi-Fi', 'Café', 'Sala VIP', 'Banheiros'],
    operating_hours: [
        { day_of_week: 'MONDAY', open: '05:00', close: '23:59', is_closed: false },
        { day_of_week: 'TUESDAY', open: '05:00', close: '23:59', is_closed: false },
        { day_of_week: 'WEDNESDAY', open: '05:00', close: '23:59', is_closed: false },
        { day_of_week: 'THURSDAY', open: '05:00', close: '23:59', is_closed: false },
        { day_of_week: 'FRIDAY', open: '05:00', close: '23:59', is_closed: false },
        { day_of_week: 'SATURDAY', open: '05:00', close: '22:00', is_closed: false },
        { day_of_week: 'SUNDAY', open: '06:00', close: '23:59', is_closed: false }
    ],
    instructions: {
        pickup: 'Siga para o balcão no saguão de desembarque principal.',
        dropoff: 'Devolução no estacionamento G2, setor de Locadoras.',
        extra: 'Tolerância de 1h em caso de atrasos de voo informados previamente.'
    }
};

-- Filiais Movida (RJ e SP)
CREATE store:sdumont_movida CONTENT {
    company: company:movida,
    code: 'SDU',
    name: 'Movida Aeroporto Santos Dumont',
    location_type: 'AIRPORT',
    pickup_method: 'IN_TERMINAL',
    location: (-43.1631, -22.9105),
    address: {
        country: 'Brasil',
        state: 'RJ',
        city: 'Rio de Janeiro',
        neighborhood: 'Centro',
        street: 'Praça Sen. Salgado Filho',
        number: 's/n',
        postal_code: '20021-340',
        complement: 'Saguão de Desembarque'
    },
    contact: {
        email: 'agencia.sdu@movida.com.br',
        phone: '+55 21 3333-0000',
        manager_name: 'Pedro Alves'
    },
    amenities: ['Wi-Fi', 'Água', 'Atendimento Rápido'],
    operating_hours: [
        { day_of_week: 'MONDAY', open: '06:00', close: '23:00', is_closed: false },
        { day_of_week: 'TUESDAY', open: '06:00', close: '23:00', is_closed: false },
        { day_of_week: 'WEDNESDAY', open: '06:00', close: '23:00', is_closed: false },
        { day_of_week: 'THURSDAY', open: '06:00', close: '23:00', is_closed: false },
        { day_of_week: 'FRIDAY', open: '06:00', close: '23:00', is_closed: false },
        { day_of_week: 'SATURDAY', open: '06:00', close: '22:00', is_closed: false },
        { day_of_week: 'SUNDAY', open: '06:00', close: '23:00', is_closed: false }
    ],
    instructions: {
        pickup: 'Desça a escada rolante até o desembarque, nosso balcão estará à esquerda.',
        dropoff: 'Acesso pela pista lateral antes do embarque.',
        extra: 'Recomendamos antecedência de 2 horas para a devolução.'
    }
};

-- ------------------------------
-- RELAÇÕES EMPRESARIAIS (MANAGES)
-- ------------------------------
RELATE user:admin_localiza->manages->company:localiza CONTENT { role: 'ADMIN' };
RELATE user:admin_movida->manages->company:movida CONTENT { role: 'ADMIN' };

-- ------------------------------
-- RELAÇÕES TRABALHISTAS (WORKS_AT)
-- ------------------------------
RELATE user:gerente_sp_localiza->works_at->store:cgh_localiza CONTENT { role: 'MANAGER' };
RELATE user:atendente_sp_localiza->works_at->store:cgh_localiza CONTENT { role: 'CLERK' };

RELATE user:gerente_rj_movida->works_at->store:sdumont_movida CONTENT { role: 'MANAGER' };

-- ------------------------------
-- CATEGORIAS DE VEÍCULOS (VEHICLE CATEGORIES)
-- ------------------------------

-- Localiza - Categorias
CREATE vehicle_category:loc_eco CONTENT {
    company: company:localiza,
    code: 'B',
    group_name: 'Econômico',
    acriss_code: 'ECMR',
    description: 'Veículos econômicos e compactos. Ideal para o dia a dia na cidade.',
    features: {
        air_conditioning: true,
        doors: 4,
        transmission: 'MANUAL',
        fuel_type: 'FLEX',
        capacity: {
            passengers: 5,
            large_suitcases: 1,
            small_suitcases: 1
        }
    },
    representative_models: ['Fiat Mobi', 'Renault Kwid', 'Chevrolet Mobi'],
    image_url: 'https://example.com/images/loc_eco.png'
};

CREATE vehicle_category:loc_suv CONTENT {
    company: company:localiza,
    code: 'GX',
    group_name: 'SUV Compacto',
    acriss_code: 'CFAR',
    description: 'Veículos mais altos e confortáveis, ideais para famílias.',
    features: {
        air_conditioning: true,
        doors: 4,
        transmission: 'AUTOMATIC',
        fuel_type: 'FLEX',
        capacity: {
            passengers: 5,
            large_suitcases: 2,
            small_suitcases: 2
        }
    },
    representative_models: ['Jeep Renegade', 'VW Kicks', 'Hyundai T-Cross'],
    image_url: 'https://example.com/images/loc_suv.png'
};

-- Movida - Categorias
CREATE vehicle_category:mov_eco CONTENT {
    company: company:movida,
    code: 'AX',
    group_name: 'Econômico com Ar',
    acriss_code: 'ECAR',
    description: 'Econômico, prático com o conforto do câmbio automático.',
    features: {
        air_conditioning: true,
        doors: 4,
        transmission: 'AUTOMATIC',
        fuel_type: 'FLEX',
        capacity: {
            passengers: 5,
            large_suitcases: 1,
            small_suitcases: 2
        }
    },
    representative_models: ['VW Polo', 'Chevrolet Onix', 'Hyundai HB20'],
    image_url: 'https://example.com/images/mov_eco.png'
};
