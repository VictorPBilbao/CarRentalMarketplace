-- ------------------------------
-- OPTION
-- ------------------------------

OPTION IMPORT;

-- ------------------------------
-- TABLE: addon
-- ------------------------------

DEFINE TABLE addon TYPE NORMAL SCHEMAFULL PERMISSIONS NONE;

DEFINE FIELD active ON addon TYPE bool DEFAULT true PERMISSIONS FULL;
DEFINE FIELD company ON addon TYPE record<company> PERMISSIONS FULL;
DEFINE FIELD created_at ON addon TYPE datetime DEFAULT time::now() READONLY PERMISSIONS FULL;
DEFINE FIELD description ON addon TYPE string PERMISSIONS FULL;
DEFINE FIELD name ON addon TYPE string ASSERT string::len($value) > 2 PERMISSIONS FULL;
DEFINE FIELD pricing ON addon TYPE object PERMISSIONS FULL;
DEFINE FIELD pricing.amount ON addon TYPE decimal ASSERT $value >= 0f PERMISSIONS FULL;
DEFINE FIELD pricing.calculation_type ON addon TYPE string ASSERT $value INSIDE ['PER_DAY', 'PER_TRIP', 'PERCENTAGE'] PERMISSIONS FULL;
DEFINE FIELD pricing.max_amount_per_trip ON addon TYPE none | decimal PERMISSIONS FULL;
DEFINE FIELD stores ON addon TYPE array<record<store>> DEFAULT [] PERMISSIONS FULL;
DEFINE FIELD stores.* ON addon TYPE record<store> PERMISSIONS FULL;
DEFINE FIELD type ON addon TYPE string ASSERT $value INSIDE ['INSURANCE', 'EQUIPMENT', 'SERVICE', 'FEE'] PERMISSIONS FULL;
DEFINE FIELD updated_at ON addon TYPE datetime VALUE time::now() PERMISSIONS FULL;



-- ------------------------------
-- TABLE DATA: addon
-- ------------------------------

INSERT [ { active: true, company: company:localiza, created_at: d'2026-04-27T22:31:53.040150444Z', description: 'Assento de segurança obrigatório para crianças de 1 a 4 anos.', id: addon:loc_cadeira_bebe, name: 'Cadeira de Bebê', pricing: { amount: 35dec, calculation_type: 'PER_DAY', max_amount_per_trip: 200dec }, stores: [], type: 'EQUIPMENT', updated_at: d'2026-04-27T22:31:53.045733565Z' }, { active: true, company: company:localiza, created_at: d'2026-04-27T22:31:53.045961527Z', description: 'Devolva o carro sujo sem se preocupar com taxas extras de limpeza simples.', id: addon:loc_lavagem, name: 'Lavagem Garantida', pricing: { amount: 45dec, calculation_type: 'PER_TRIP' }, stores: [], type: 'SERVICE', updated_at: d'2026-04-27T22:31:53.046002615Z' }, { active: true, company: company:movida, created_at: d'2026-04-27T22:31:53.046148481Z', description: 'Sistema de navegação para facilitar sua viagem.', id: addon:mov_gps, name: 'GPS Integrado', pricing: { amount: 25dec, calculation_type: 'PER_DAY', max_amount_per_trip: 150dec }, stores: [], type: 'EQUIPMENT', updated_at: d'2026-04-27T22:31:53.046169220Z' } ];

-- ------------------------------
-- TABLE: allows_return_to
-- ------------------------------

DEFINE TABLE allows_return_to TYPE RELATION IN store OUT store SCHEMAFULL PERMISSIONS NONE;

DEFINE FIELD active ON allows_return_to TYPE bool DEFAULT true PERMISSIONS FULL;
DEFINE FIELD created_at ON allows_return_to TYPE datetime DEFAULT time::now() READONLY PERMISSIONS FULL;
DEFINE FIELD fee ON allows_return_to TYPE object PERMISSIONS FULL;
DEFINE FIELD fee.amount ON allows_return_to TYPE decimal DEFAULT 0f PERMISSIONS FULL;
DEFINE FIELD fee.type ON allows_return_to TYPE string ASSERT $value INSIDE ['FREE', 'FIXED', 'PER_KM'] PERMISSIONS FULL;
DEFINE FIELD in ON allows_return_to TYPE record<store> PERMISSIONS FULL;
DEFINE FIELD out ON allows_return_to TYPE record<store> PERMISSIONS FULL;



-- ------------------------------
-- TABLE DATA: allows_return_to
-- ------------------------------

INSERT RELATION [ { active: true, created_at: d'2026-04-27T22:34:01.064443069Z', fee: { amount: 80dec, type: 'FIXED' }, id: allows_return_to:vw5sb7sa8r9nfjtby3it, in: store:cgh_localiza, out: store:gru_localiza } ];

-- ------------------------------
-- TABLE: availability_ledger
-- ------------------------------

DEFINE TABLE availability_ledger TYPE NORMAL SCHEMAFULL PERMISSIONS NONE;

DEFINE FIELD block_date ON availability_ledger TYPE datetime PERMISSIONS FULL;
DEFINE FIELD category ON availability_ledger TYPE record<vehicle_category> PERMISSIONS FULL;
DEFINE FIELD created_at ON availability_ledger TYPE datetime DEFAULT time::now() READONLY PERMISSIONS FULL;
DEFINE FIELD store ON availability_ledger TYPE record<store> PERMISSIONS FULL;
DEFINE FIELD total_booked ON availability_ledger TYPE int DEFAULT 0 ASSERT $value >= 0 PERMISSIONS FULL;
DEFINE FIELD total_fleet ON availability_ledger TYPE int DEFAULT 0 ASSERT $value >= 0 PERMISSIONS FULL;
DEFINE FIELD total_maintenance ON availability_ledger TYPE int DEFAULT 0 ASSERT $value >= 0 PERMISSIONS FULL;
DEFINE FIELD updated_at ON availability_ledger TYPE datetime VALUE time::now() PERMISSIONS FULL;

DEFINE INDEX store_category_date ON availability_ledger FIELDS store, category, block_date UNIQUE;


-- ------------------------------
-- TABLE DATA: availability_ledger
-- ------------------------------

INSERT [ { block_date: d'2026-04-29T22:35:07.474071560Z', category: vehicle_category:mov_eco, created_at: d'2026-04-27T22:35:07.474082752Z', id: availability_ledger:efc9tgmpo1xx5mocu1ng, store: store:sdumont_movida, total_booked: 1, total_fleet: 5, total_maintenance: 0, updated_at: d'2026-04-27T22:35:07.474094024Z' }, { block_date: d'2026-04-28T22:35:07.472974537Z', category: vehicle_category:loc_eco, created_at: d'2026-04-27T22:35:07.472992532Z', id: availability_ledger:rvxhlnnqyyt5338cuu20, store: store:cgh_localiza, total_booked: 1, total_fleet: 10, total_maintenance: 1, updated_at: d'2026-04-27T22:35:07.473002552Z' } ];

-- ------------------------------
-- TABLE: can_supply_to
-- ------------------------------

DEFINE TABLE can_supply_to TYPE RELATION IN store OUT store SCHEMAFULL PERMISSIONS NONE;

DEFINE FIELD active ON can_supply_to TYPE bool DEFAULT true PERMISSIONS FULL;
DEFINE FIELD allowed_categories ON can_supply_to TYPE array<record<vehicle_category>> DEFAULT [] PERMISSIONS FULL;
DEFINE FIELD allowed_categories.* ON can_supply_to TYPE record<vehicle_category> PERMISSIONS FULL;
DEFINE FIELD created_at ON can_supply_to TYPE datetime DEFAULT time::now() READONLY PERMISSIONS FULL;
DEFINE FIELD in ON can_supply_to TYPE record<store> PERMISSIONS FULL;
DEFINE FIELD out ON can_supply_to TYPE record<store> PERMISSIONS FULL;
DEFINE FIELD transfer_fee ON can_supply_to TYPE decimal ASSERT $value >= 0f PERMISSIONS FULL;
DEFINE FIELD transit_time_hours ON can_supply_to TYPE int ASSERT $value >= 1 PERMISSIONS FULL;



-- ------------------------------
-- TABLE DATA: can_supply_to
-- ------------------------------

INSERT RELATION [ { active: true, allowed_categories: [vehicle_category:loc_eco, vehicle_category:loc_suv], created_at: d'2026-04-27T22:34:01.064601829Z', id: can_supply_to:02qvtwln89494tv0wqwi, in: store:gru_localiza, out: store:cgh_localiza, transfer_fee: 150dec, transit_time_hours: 2 } ];

-- ------------------------------
-- TABLE: company
-- ------------------------------

DEFINE TABLE company TYPE NORMAL SCHEMAFULL PERMISSIONS NONE;

DEFINE FIELD active ON company TYPE bool DEFAULT true PERMISSIONS FULL;
DEFINE FIELD contact ON company TYPE object PERMISSIONS FULL;
DEFINE FIELD contact.email ON company TYPE string ASSERT string::is_email($value) PERMISSIONS FULL;
DEFINE FIELD contact.phone ON company TYPE string PERMISSIONS FULL;
DEFINE FIELD created_at ON company TYPE datetime DEFAULT time::now() READONLY PERMISSIONS FULL;
DEFINE FIELD logo_url ON company TYPE none | string ASSERT $value = NONE OR string::is_url($value) PERMISSIONS FULL;
DEFINE FIELD name ON company TYPE string PERMISSIONS FULL;
DEFINE FIELD tax_id ON company TYPE string ASSERT string::len($value) > 5 PERMISSIONS FULL;
DEFINE FIELD trading_name ON company TYPE none | string PERMISSIONS FULL;
DEFINE FIELD updated_at ON company TYPE datetime VALUE time::now() PERMISSIONS FULL;
DEFINE FIELD website ON company TYPE none | string ASSERT $value = NONE OR string::is_url($value) PERMISSIONS FULL;



-- ------------------------------
-- TABLE DATA: company
-- ------------------------------

INSERT [ { active: true, contact: { email: 'contato@localiza.com', phone: '+55 31 3247-7000' }, created_at: d'2026-04-27T22:29:24.793679257Z', id: company:localiza, logo_url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Localiza_logo.png/640px-Localiza_logo.png', name: 'Localiza Rent a Car S.A.', tax_id: '16.670.085/0001-55', trading_name: 'Localiza', updated_at: d'2026-04-27T22:29:24.793776187Z', website: 'https://www.localiza.com' }, { active: true, contact: { email: 'atendimento@movida.com.br', phone: '0800 606 8686' }, created_at: d'2026-04-27T22:29:24.793994215Z', id: company:movida, logo_url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Movida_logo.png/640px-Movida_logo.png', name: 'Movida Participações S.A.', tax_id: '07.976.147/0001-60', trading_name: 'Movida Rent a Car', updated_at: d'2026-04-27T22:29:24.794024475Z', website: 'https://www.movida.com.br' } ];

-- ------------------------------
-- TABLE: fee
-- ------------------------------

DEFINE TABLE fee TYPE NORMAL SCHEMAFULL PERMISSIONS NONE;

DEFINE FIELD active ON fee TYPE bool DEFAULT true PERMISSIONS FULL;
DEFINE FIELD conditions ON fee TYPE object PERMISSIONS FULL;
DEFINE FIELD conditions.applies_after_time ON fee TYPE none | string PERMISSIONS FULL;
DEFINE FIELD conditions.applies_before_time ON fee TYPE none | string PERMISSIONS FULL;
DEFINE FIELD name ON fee TYPE string PERMISSIONS FULL;
DEFINE FIELD pricing ON fee TYPE object PERMISSIONS FULL;
DEFINE FIELD pricing.amount ON fee TYPE decimal PERMISSIONS FULL;
DEFINE FIELD pricing.calculation_type ON fee TYPE string ASSERT $value INSIDE ['PERCENTAGE', 'FLAT_FEE'] PERMISSIONS FULL;
DEFINE FIELD store ON fee TYPE record<store> PERMISSIONS FULL;



-- ------------------------------
-- TABLE DATA: fee
-- ------------------------------

INSERT [ { active: true, conditions: {  }, id: fee:loc_taxa_aeroporto_cgh, name: 'Taxa Aeroportuária - Congonhas', pricing: { amount: 12dec, calculation_type: 'PERCENTAGE' }, store: store:cgh_localiza }, { active: true, conditions: {  }, id: fee:mov_taxa_limpeza_pesada, name: 'Taxa de Limpeza Pesada ou Estofado', pricing: { amount: 250dec, calculation_type: 'FLAT_FEE' }, store: store:sdumont_movida } ];

-- ------------------------------
-- TABLE: manages
-- ------------------------------

DEFINE TABLE manages TYPE RELATION IN user OUT company SCHEMAFULL PERMISSIONS NONE;

DEFINE FIELD created_at ON manages TYPE datetime DEFAULT time::now() READONLY PERMISSIONS FULL;
DEFINE FIELD in ON manages TYPE record<user> PERMISSIONS FULL;
DEFINE FIELD out ON manages TYPE record<company> PERMISSIONS FULL;
DEFINE FIELD role ON manages TYPE string DEFAULT 'ADMIN' ASSERT $value INSIDE ['OWNER', 'ADMIN'] PERMISSIONS FULL;



-- ------------------------------
-- TABLE DATA: manages
-- ------------------------------

INSERT RELATION [ { created_at: d'2026-04-27T22:30:47.324584627Z', id: manages:6kgg4i31r4n1sxm1k79q, in: user:admin_movida, out: company:movida, role: 'ADMIN' }, { created_at: d'2026-04-27T22:30:47.324466327Z', id: manages:nz85sfd5nyq5y8lrngdj, in: user:admin_localiza, out: company:localiza, role: 'ADMIN' } ];

-- ------------------------------
-- TABLE: protection
-- ------------------------------

DEFINE TABLE protection TYPE NORMAL SCHEMAFULL PERMISSIONS NONE;

DEFINE FIELD code ON protection TYPE string PERMISSIONS FULL;
DEFINE FIELD company ON protection TYPE record<company> PERMISSIONS FULL;
DEFINE FIELD name ON protection TYPE string PERMISSIONS FULL;
DEFINE FIELD pricing_matrix ON protection TYPE array<object> PERMISSIONS FULL;
DEFINE FIELD pricing_matrix.* ON protection TYPE object PERMISSIONS FULL;
DEFINE FIELD pricing_matrix.*.category ON protection TYPE record<vehicle_category> PERMISSIONS FULL;
DEFINE FIELD pricing_matrix.*.daily_rate ON protection TYPE decimal PERMISSIONS FULL;
DEFINE FIELD pricing_matrix.*.deductible_amount ON protection TYPE decimal PERMISSIONS FULL;



-- ------------------------------
-- TABLE DATA: protection
-- ------------------------------

INSERT [ { code: 'PROT_BASICA', company: company:localiza, id: protection:loc_basica, name: 'Proteção Básica do Veículo (LDW)', pricing_matrix: [{ category: vehicle_category:loc_eco, daily_rate: 38dec, deductible_amount: 3000dec }, { category: vehicle_category:loc_suv, daily_rate: 55dec, deductible_amount: 5000dec }] }, { code: 'PROT_COMPLETA', company: company:movida, id: protection:mov_completa, name: 'Proteção Completa (Casco + Terceiros)', pricing_matrix: [{ category: vehicle_category:mov_eco, daily_rate: 65dec, deductible_amount: 1000dec }] } ];

-- ------------------------------
-- TABLE: quote
-- ------------------------------

DEFINE TABLE quote TYPE NORMAL SCHEMAFULL PERMISSIONS NONE;

DEFINE FIELD applied_rate_plan ON quote TYPE record<rate_plan> PERMISSIONS FULL;
DEFINE FIELD category ON quote TYPE record<vehicle_category> PERMISSIONS FULL;
DEFINE FIELD created_at ON quote TYPE datetime DEFAULT time::now() READONLY PERMISSIONS FULL;
DEFINE FIELD dropoff_store ON quote TYPE record<store> PERMISSIONS FULL;
DEFINE FIELD dropoff_time ON quote TYPE datetime PERMISSIONS FULL;
DEFINE FIELD expires_at ON quote TYPE datetime DEFAULT time::now() + 15m READONLY PERMISSIONS FULL;
DEFINE FIELD pickup_store ON quote TYPE record<store> PERMISSIONS FULL;
DEFINE FIELD pickup_time ON quote TYPE datetime PERMISSIONS FULL;
DEFINE FIELD pricing ON quote TYPE object PERMISSIONS FULL;
DEFINE FIELD pricing.addons_total ON quote TYPE decimal DEFAULT 0f PERMISSIONS FULL;
DEFINE FIELD pricing.breakdown ON quote TYPE array<object> DEFAULT [] PERMISSIONS FULL;
DEFINE FIELD pricing.breakdown.* ON quote TYPE object PERMISSIONS FULL;
DEFINE FIELD pricing.breakdown.*.amount ON quote TYPE decimal PERMISSIONS FULL;
DEFINE FIELD pricing.breakdown.*.description ON quote TYPE string PERMISSIONS FULL;
DEFINE FIELD pricing.breakdown.*.type ON quote TYPE string ASSERT $value INSIDE ['BASE_RATE', 'ADDON', 'INSURANCE', 'LOGISTICS_FEE', 'DRIVER_FEE', 'TAX', 'DISCOUNT', 'FEE'] PERMISSIONS FULL;
DEFINE FIELD pricing.currency ON quote TYPE string DEFAULT 'BRL' PERMISSIONS FULL;
DEFINE FIELD pricing.daily_rate ON quote TYPE decimal PERMISSIONS FULL;
DEFINE FIELD pricing.fees_total ON quote TYPE decimal DEFAULT 0f PERMISSIONS FULL;
DEFINE FIELD pricing.final_total ON quote TYPE decimal PERMISSIONS FULL;
DEFINE FIELD pricing.total_days ON quote TYPE int PERMISSIONS FULL;
DEFINE FIELD selected_addons ON quote TYPE array<object> DEFAULT [] PERMISSIONS FULL;
DEFINE FIELD selected_addons.* ON quote TYPE object PERMISSIONS FULL;
DEFINE FIELD selected_addons.*.addon ON quote TYPE record<addon> PERMISSIONS FULL;
DEFINE FIELD selected_addons.*.quantity ON quote TYPE int ASSERT $value >= 1 PERMISSIONS FULL;
DEFINE FIELD selected_addons.*.total_price ON quote TYPE decimal PERMISSIONS FULL;



-- ------------------------------
-- TABLE DATA: quote
-- ------------------------------


-- ------------------------------
-- TABLE: rate_plan
-- ------------------------------

DEFINE TABLE rate_plan TYPE NORMAL SCHEMAFULL PERMISSIONS NONE;

DEFINE FIELD active ON rate_plan TYPE bool DEFAULT true PERMISSIONS FULL;
DEFINE FIELD company ON rate_plan TYPE record<company> PERMISSIONS FULL;
DEFINE FIELD conditions ON rate_plan TYPE object PERMISSIONS FULL;
DEFINE FIELD conditions.advance_booking_days ON rate_plan TYPE int DEFAULT 0 PERMISSIONS FULL;
DEFINE FIELD conditions.allow_one_way ON rate_plan TYPE bool DEFAULT true PERMISSIONS FULL;
DEFINE FIELD conditions.allowed_nationalities ON rate_plan TYPE array<string> DEFAULT [] PERMISSIONS FULL;
DEFINE FIELD conditions.allowed_nationalities.* ON rate_plan TYPE string PERMISSIONS FULL;
DEFINE FIELD conditions.categories ON rate_plan TYPE array<record<vehicle_category>> ASSERT array::len($value) > 0 PERMISSIONS FULL;
DEFINE FIELD conditions.categories.* ON rate_plan TYPE record<vehicle_category> PERMISSIONS FULL;
DEFINE FIELD conditions.max_age ON rate_plan TYPE none | int PERMISSIONS FULL;
DEFINE FIELD conditions.max_days ON rate_plan TYPE none | int PERMISSIONS FULL;
DEFINE FIELD conditions.min_age ON rate_plan TYPE int DEFAULT 18 ASSERT $value >= 18 PERMISSIONS FULL;
DEFINE FIELD conditions.min_days ON rate_plan TYPE int DEFAULT 1 ASSERT $value >= 1 PERMISSIONS FULL;
DEFINE FIELD conditions.promo_code ON rate_plan TYPE none | string PERMISSIONS FULL;
DEFINE FIELD conditions.stores ON rate_plan TYPE array<record<store>> DEFAULT [] PERMISSIONS FULL;
DEFINE FIELD conditions.stores.* ON rate_plan TYPE record<store> PERMISSIONS FULL;
DEFINE FIELD conditions.valid_from ON rate_plan TYPE none | datetime PERMISSIONS FULL;
DEFINE FIELD conditions.valid_to ON rate_plan TYPE none | datetime PERMISSIONS FULL;
DEFINE FIELD created_at ON rate_plan TYPE datetime DEFAULT time::now() READONLY PERMISSIONS FULL;
DEFINE FIELD included_protections ON rate_plan TYPE array<record<protection>> DEFAULT [] PERMISSIONS FULL;
DEFINE FIELD included_protections.* ON rate_plan TYPE record<protection> PERMISSIONS FULL;
DEFINE FIELD name ON rate_plan TYPE string ASSERT string::len($value) > 2 PERMISSIONS FULL;
DEFINE FIELD price ON rate_plan TYPE object PERMISSIONS FULL;
DEFINE FIELD price.currency ON rate_plan TYPE string DEFAULT 'BRL' ASSERT $value INSIDE ['BRL', 'USD', 'EUR'] PERMISSIONS FULL;
DEFINE FIELD price.daily_rate ON rate_plan TYPE decimal ASSERT $value >= 0f PERMISSIONS FULL;
DEFINE FIELD price.extra_km_price ON rate_plan TYPE decimal DEFAULT 0f PERMISSIONS FULL;
DEFINE FIELD price.included_km_per_day ON rate_plan TYPE int DEFAULT 0 PERMISSIONS FULL;
DEFINE FIELD price.mileage_policy ON rate_plan TYPE string DEFAULT 'UNLIMITED' ASSERT $value INSIDE ['UNLIMITED', 'LIMITED'] PERMISSIONS FULL;
DEFINE FIELD priority ON rate_plan TYPE int DEFAULT 0 PERMISSIONS FULL;
DEFINE FIELD updated_at ON rate_plan TYPE datetime VALUE time::now() PERMISSIONS FULL;



-- ------------------------------
-- TABLE DATA: rate_plan
-- ------------------------------

INSERT [ { active: true, company: company:localiza, conditions: { advance_booking_days: 0, allow_one_way: true, allowed_nationalities: [], categories: [vehicle_category:loc_eco, vehicle_category:loc_suv], min_age: 21, min_days: 1, stores: [store:cgh_localiza, store:gru_localiza] }, created_at: d'2026-04-27T22:34:01.070567142Z', id: rate_plan:loc_flex, included_protections: [], name: 'Tarifa Flexível SP', price: { currency: 'BRL', daily_rate: 90dec, extra_km_price: 0dec, included_km_per_day: 0, mileage_policy: 'UNLIMITED' }, priority: 10, updated_at: d'2026-04-27T22:34:01.070616799Z' }, { active: true, company: company:movida, conditions: { advance_booking_days: 2, allow_one_way: false, allowed_nationalities: [], categories: [vehicle_category:mov_eco], max_days: 4, min_age: 18, min_days: 2, promo_code: 'VERAO2024', stores: [store:sdumont_movida] }, created_at: d'2026-04-27T22:34:01.071164571Z', id: rate_plan:mov_weekend, included_protections: [protection:mov_completa], name: 'Promoção Fim de Semana Carioca', price: { currency: 'BRL', daily_rate: 75dec, extra_km_price: 1.25dec, included_km_per_day: 150, mileage_policy: 'LIMITED' }, priority: 50, updated_at: d'2026-04-27T22:34:01.071183969Z' } ];

-- ------------------------------
-- TABLE: rental_agreement
-- ------------------------------

DEFINE TABLE rental_agreement TYPE NORMAL SCHEMAFULL PERMISSIONS NONE;

DEFINE FIELD checkin ON rental_agreement TYPE none | object PERMISSIONS FULL;
DEFINE FIELD checkin.employee ON rental_agreement TYPE record<user> PERMISSIONS FULL;
DEFINE FIELD checkin.fuel_level ON rental_agreement TYPE int ASSERT $value >= 0 AND $value <= 100 PERMISSIONS FULL;
DEFINE FIELD checkin.mileage ON rental_agreement TYPE int ASSERT $value >= $this.checkout.mileage PERMISSIONS FULL;
DEFINE FIELD checkin.notes ON rental_agreement TYPE none | string PERMISSIONS FULL;
DEFINE FIELD checkin.photo_urls ON rental_agreement TYPE array<string> DEFAULT [] PERMISSIONS FULL;
DEFINE FIELD checkin.photo_urls.* ON rental_agreement TYPE string PERMISSIONS FULL;
DEFINE FIELD checkin.store ON rental_agreement TYPE record<store> PERMISSIONS FULL;
DEFINE FIELD checkin.time ON rental_agreement TYPE datetime PERMISSIONS FULL;
DEFINE FIELD checkout ON rental_agreement TYPE object PERMISSIONS FULL;
DEFINE FIELD checkout.employee ON rental_agreement TYPE record<user> PERMISSIONS FULL;
DEFINE FIELD checkout.fuel_level ON rental_agreement TYPE int ASSERT $value >= 0 AND $value <= 100 PERMISSIONS FULL;
DEFINE FIELD checkout.mileage ON rental_agreement TYPE int ASSERT $value >= 0 PERMISSIONS FULL;
DEFINE FIELD checkout.notes ON rental_agreement TYPE none | string PERMISSIONS FULL;
DEFINE FIELD checkout.photo_urls ON rental_agreement TYPE array<string> DEFAULT [] PERMISSIONS FULL;
DEFINE FIELD checkout.photo_urls.* ON rental_agreement TYPE string PERMISSIONS FULL;
DEFINE FIELD checkout.store ON rental_agreement TYPE record<store> PERMISSIONS FULL;
DEFINE FIELD checkout.time ON rental_agreement TYPE datetime DEFAULT time::now() PERMISSIONS FULL;
DEFINE FIELD contract_number ON rental_agreement TYPE string ASSERT string::len($value) > 5 PERMISSIONS FULL;
DEFINE FIELD created_at ON rental_agreement TYPE datetime DEFAULT time::now() READONLY PERMISSIONS FULL;
DEFINE FIELD customer ON rental_agreement TYPE record<user> PERMISSIONS FULL;
DEFINE FIELD extra_charges ON rental_agreement TYPE decimal DEFAULT 0f PERMISSIONS FULL;
DEFINE FIELD reservation ON rental_agreement TYPE record<reservation> PERMISSIONS FULL;
DEFINE FIELD signed_contract_url ON rental_agreement TYPE none | string ASSERT $value = NONE OR string::is_url($value) PERMISSIONS FULL;
DEFINE FIELD status ON rental_agreement TYPE string DEFAULT 'DRAFT' ASSERT $value INSIDE ['DRAFT', 'OPEN', 'CLOSED', 'VOIDED'] PERMISSIONS FULL;
DEFINE FIELD updated_at ON rental_agreement TYPE datetime VALUE time::now() PERMISSIONS FULL;
DEFINE FIELD vehicle ON rental_agreement TYPE record<vehicle> PERMISSIONS FULL;



-- ------------------------------
-- TABLE DATA: rental_agreement
-- ------------------------------

INSERT [ { checkout: { employee: user:atendente_sp_localiza, fuel_level: 100, mileage: 15400, notes: 'Veículo em perfeitas condições. Cadeira de bebê instalada no banco traseiro.', photo_urls: ['https://storage.exemplo.com/photos/kwid_frente.jpg', 'https://storage.exemplo.com/photos/kwid_painel.jpg'], store: store:cgh_localiza, time: d'2026-04-27T22:35:07.472741241Z' }, contract_number: 'LOC-2026-001', created_at: d'2026-04-27T22:35:07.472791970Z', customer: user:cliente1, extra_charges: 0dec, id: rental_agreement:ra_loc_1, reservation: reservation:res_loc_1, signed_contract_url: 'https://exemplo.localiza.com/contracts/LOC-2026-001.pdf', status: 'OPEN', updated_at: d'2026-04-27T22:35:07.472811859Z', vehicle: vehicle:loc_kwid_1 } ];

-- ------------------------------
-- TABLE: reservation
-- ------------------------------

DEFINE TABLE reservation TYPE NORMAL SCHEMAFULL PERMISSIONS NONE;

DEFINE FIELD category ON reservation TYPE record<vehicle_category> PERMISSIONS FULL;
DEFINE FIELD created_at ON reservation TYPE datetime DEFAULT time::now() READONLY PERMISSIONS FULL;
DEFINE FIELD customer ON reservation TYPE record<user> PERMISSIONS FULL;
DEFINE FIELD dropoff_store ON reservation TYPE record<store> PERMISSIONS FULL;
DEFINE FIELD dropoff_time ON reservation TYPE datetime ASSERT $value > $this.pickup_time PERMISSIONS FULL;
DEFINE FIELD flight_number ON reservation TYPE none | string PERMISSIONS FULL;
DEFINE FIELD notes ON reservation TYPE none | string PERMISSIONS FULL;
DEFINE FIELD pickup_store ON reservation TYPE record<store> PERMISSIONS FULL;
DEFINE FIELD pickup_time ON reservation TYPE datetime ASSERT $value > time::now() PERMISSIONS FULL;
DEFINE FIELD pricing ON reservation TYPE object PERMISSIONS FULL;
DEFINE FIELD pricing.breakdown ON reservation TYPE array<object> DEFAULT [] PERMISSIONS FULL;
DEFINE FIELD pricing.breakdown.* ON reservation TYPE object PERMISSIONS FULL;
DEFINE FIELD pricing.breakdown.*.amount ON reservation TYPE decimal PERMISSIONS FULL;
DEFINE FIELD pricing.breakdown.*.description ON reservation TYPE string PERMISSIONS FULL;
DEFINE FIELD pricing.breakdown.*.type ON reservation TYPE string ASSERT $value INSIDE ['BASE_RATE', 'ADDON', 'INSURANCE', 'LOGISTICS_FEE', 'DRIVER_FEE', 'TAX', 'DISCOUNT', 'FEE'] PERMISSIONS FULL;
DEFINE FIELD pricing.daily_rate ON reservation TYPE decimal PERMISSIONS FULL;
DEFINE FIELD pricing.fees ON reservation TYPE decimal DEFAULT 0f PERMISSIONS FULL;
DEFINE FIELD pricing.total_amount ON reservation TYPE decimal PERMISSIONS FULL;
DEFINE FIELD pricing.total_days ON reservation TYPE int ASSERT $value >= 1 PERMISSIONS FULL;
DEFINE FIELD status ON reservation TYPE string DEFAULT 'PENDING' ASSERT $value INSIDE ['PENDING', 'CONFIRMED', 'ACTIVE', 'COMPLETED', 'CANCELLED', 'NO_SHOW'] PERMISSIONS FULL;
DEFINE FIELD updated_at ON reservation TYPE datetime VALUE time::now() PERMISSIONS FULL;



-- ------------------------------
-- TABLE DATA: reservation
-- ------------------------------

INSERT [ { category: vehicle_category:loc_eco, created_at: d'2026-04-27T22:35:07.471932361Z', customer: user:cliente1, dropoff_store: store:gru_localiza, dropoff_time: d'2026-05-01T22:35:07.471874798Z', flight_number: 'LA3344', id: reservation:res_loc_1, notes: 'Cliente solicitou cadeirinha de bebê e lavagem antecipada.', pickup_store: store:cgh_localiza, pickup_time: d'2026-04-28T22:35:07.471856954Z', pricing: { breakdown: [{ amount: 270dec, description: '3 diárias x R$ 90 (Tarifa Flexível)', type: 'BASE_RATE' }, { amount: 80dec, description: 'Taxa de Retorno (Drop-off GRU)', type: 'LOGISTICS_FEE' }], daily_rate: 90dec, fees: 80dec, total_amount: 350dec, total_days: 3 }, status: 'ACTIVE', updated_at: d'2026-04-27T22:35:07.471993921Z' }, { category: vehicle_category:mov_eco, created_at: d'2026-04-27T22:35:07.472448980Z', customer: user:cliente2, dropoff_store: store:sdumont_movida, dropoff_time: d'2026-05-01T22:35:07.472407429Z', id: reservation:res_mov_1, notes: 'Reserva Promocional de Fim de Semana', pickup_store: store:sdumont_movida, pickup_time: d'2026-04-29T22:35:07.472405095Z', pricing: { breakdown: [{ amount: 150dec, description: '2 diárias Promoção Fim de Semana', type: 'BASE_RATE' }], daily_rate: 75dec, fees: 0dec, total_amount: 150dec, total_days: 2 }, status: 'CONFIRMED', updated_at: d'2026-04-27T22:35:07.472512074Z' } ];

-- ------------------------------
-- TABLE: store
-- ------------------------------

DEFINE TABLE store TYPE NORMAL SCHEMAFULL PERMISSIONS NONE;

DEFINE FIELD active ON store TYPE bool DEFAULT true PERMISSIONS FULL;
DEFINE FIELD address ON store TYPE object PERMISSIONS FULL;
DEFINE FIELD address.city ON store TYPE string PERMISSIONS FULL;
DEFINE FIELD address.complement ON store TYPE none | string PERMISSIONS FULL;
DEFINE FIELD address.country ON store TYPE string PERMISSIONS FULL;
DEFINE FIELD address.neighborhood ON store TYPE string PERMISSIONS FULL;
DEFINE FIELD address.number ON store TYPE string PERMISSIONS FULL;
DEFINE FIELD address.postal_code ON store TYPE string PERMISSIONS FULL;
DEFINE FIELD address.state ON store TYPE string PERMISSIONS FULL;
DEFINE FIELD address.street ON store TYPE string PERMISSIONS FULL;
DEFINE FIELD amenities ON store TYPE array<string> PERMISSIONS FULL;
DEFINE FIELD amenities.* ON store TYPE string PERMISSIONS FULL;
DEFINE FIELD code ON store TYPE string ASSERT string::len($value) >= 3 PERMISSIONS FULL;
DEFINE FIELD company ON store TYPE record<company> PERMISSIONS FULL;
DEFINE FIELD contact ON store TYPE object PERMISSIONS FULL;
DEFINE FIELD contact.email ON store TYPE string ASSERT string::is_email($value) PERMISSIONS FULL;
DEFINE FIELD contact.manager_name ON store TYPE none | string PERMISSIONS FULL;
DEFINE FIELD contact.phone ON store TYPE string PERMISSIONS FULL;
DEFINE FIELD created_at ON store TYPE datetime DEFAULT time::now() READONLY PERMISSIONS FULL;
DEFINE FIELD instructions ON store TYPE object PERMISSIONS FULL;
DEFINE FIELD instructions.dropoff ON store TYPE none | string PERMISSIONS FULL;
DEFINE FIELD instructions.extra ON store TYPE none | string PERMISSIONS FULL;
DEFINE FIELD instructions.pickup ON store TYPE none | string PERMISSIONS FULL;
DEFINE FIELD location ON store TYPE geometry<point> PERMISSIONS FULL;
DEFINE FIELD location_type ON store TYPE string ASSERT $value INSIDE ['AIRPORT', 'TRAIN_STATION', 'CITY_CENTER', 'HOTEL', 'PORT', 'MALL', 'OTHER'] PERMISSIONS FULL;
DEFINE FIELD name ON store TYPE string ASSERT string::len($value) >= 3 PERMISSIONS FULL;
DEFINE FIELD operating_hours ON store TYPE array<object> DEFAULT [] PERMISSIONS FULL;
DEFINE FIELD operating_hours.* ON store TYPE object PERMISSIONS FULL;
DEFINE FIELD operating_hours.*.close ON store TYPE none | string ASSERT $value = NONE OR $value = /^[0-2][0-9]:[0-5][0-9]$/ PERMISSIONS FULL;
DEFINE FIELD operating_hours.*.day_of_week ON store TYPE string ASSERT $value INSIDE ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY', 'HOLIDAY'] PERMISSIONS FULL;
DEFINE FIELD operating_hours.*.is_closed ON store TYPE bool DEFAULT false PERMISSIONS FULL;
DEFINE FIELD operating_hours.*.open ON store TYPE none | string ASSERT $value = NONE OR $value = /^[0-2][0-9]:[0-5][0-9]$/ PERMISSIONS FULL;
DEFINE FIELD pickup_method ON store TYPE string ASSERT $value INSIDE ['IN_TERMINAL', 'SHUTTLE', 'MEET_AND_GREET', 'WALK', 'DELIVERY'] PERMISSIONS FULL;
DEFINE FIELD special_hours ON store TYPE array DEFAULT [] PERMISSIONS FULL;
DEFINE FIELD special_hours.* ON store TYPE object PERMISSIONS FULL;
DEFINE FIELD special_hours.*.close ON store TYPE none | string ASSERT $value = NONE OR $value = /^[0-2][0-9]:[0-5][0-9]$/ PERMISSIONS FULL;
DEFINE FIELD special_hours.*.date ON store TYPE datetime PERMISSIONS FULL;
DEFINE FIELD special_hours.*.is_closed ON store TYPE bool DEFAULT false PERMISSIONS FULL;
DEFINE FIELD special_hours.*.open ON store TYPE none | string ASSERT $value = NONE OR $value = /^[0-2][0-9]:[0-5][0-9]$/ PERMISSIONS FULL;
DEFINE FIELD updated_at ON store TYPE datetime VALUE time::now() PERMISSIONS FULL;



-- ------------------------------
-- TABLE DATA: store
-- ------------------------------

INSERT [ { active: true, address: { city: 'São Paulo', complement: 'Desembarque', country: 'Brasil', neighborhood: 'Vila Congonhas', number: 's/n', postal_code: '04626-911', state: 'SP', street: 'Av. Washington Luís' }, amenities: ['Wi-Fi', 'Café', 'Sala VIP', 'Banheiros'], code: 'CGH', company: company:localiza, contact: { email: 'agencia.cgh@localiza.com', manager_name: 'Ana Santos', phone: '+55 11 5090-0000' }, created_at: d'2026-04-27T22:30:47.322181437Z', id: store:cgh_localiza, instructions: { dropoff: 'Devolução no estacionamento G2, setor de Locadoras.', extra: 'Tolerância de 1h em caso de atrasos de voo informados previamente.', pickup: 'Siga para o balcão no saguão de desembarque principal.' }, location: (-46.6622, -23.6273), location_type: 'AIRPORT', name: 'Localiza Aeroporto Congonhas', operating_hours: [{ close: '23:59', day_of_week: 'MONDAY', is_closed: false, open: '05:00' }, { close: '23:59', day_of_week: 'TUESDAY', is_closed: false, open: '05:00' }, { close: '23:59', day_of_week: 'WEDNESDAY', is_closed: false, open: '05:00' }, { close: '23:59', day_of_week: 'THURSDAY', is_closed: false, open: '05:00' }, { close: '23:59', day_of_week: 'FRIDAY', is_closed: false, open: '05:00' }, { close: '22:00', day_of_week: 'SATURDAY', is_closed: false, open: '05:00' }, { close: '23:59', day_of_week: 'SUNDAY', is_closed: false, open: '06:00' }], pickup_method: 'IN_TERMINAL', special_hours: [], updated_at: d'2026-04-27T22:30:47.322381376Z' }, { active: true, address: { city: 'Guarulhos', complement: 'Terminal 2 Desembarque Oitão', country: 'Brasil', neighborhood: 'Cumbica', number: 's/n', postal_code: '07190-100', state: 'SP', street: 'Rodovia Hélio Smidt' }, amenities: ['Wi-Fi', 'Van/Shuttle Gratuito', 'Café'], code: 'GRU', company: company:localiza, contact: { email: 'agencia.gru@localiza.com', manager_name: 'Marcos Silva', phone: '+55 11 2445-0000' }, created_at: d'2026-04-27T22:34:01.064020963Z', id: store:gru_localiza, instructions: { dropoff: 'Siga as placas "Pátio Locadoras" na entrada do aeroporto.', extra: 'Funcionamento 24h.', pickup: 'Pegue a van Localiza na calçada fora do desembarque do T2 ou T3.' }, location: (-46.473, -23.4355), location_type: 'AIRPORT', name: 'Localiza Aeroporto Guarulhos', operating_hours: [{ close: '23:59', day_of_week: 'MONDAY', is_closed: false, open: '00:00' }, { close: '23:59', day_of_week: 'TUESDAY', is_closed: false, open: '00:00' }, { close: '23:59', day_of_week: 'WEDNESDAY', is_closed: false, open: '00:00' }, { close: '23:59', day_of_week: 'THURSDAY', is_closed: false, open: '00:00' }, { close: '23:59', day_of_week: 'FRIDAY', is_closed: false, open: '00:00' }, { close: '23:59', day_of_week: 'SATURDAY', is_closed: false, open: '00:00' }, { close: '23:59', day_of_week: 'SUNDAY', is_closed: false, open: '00:00' }], pickup_method: 'SHUTTLE', special_hours: [], updated_at: d'2026-04-27T22:34:01.064135046Z' }, { active: true, address: { city: 'Rio de Janeiro', complement: 'Saguão de Desembarque', country: 'Brasil', neighborhood: 'Centro', number: 's/n', postal_code: '20021-340', state: 'RJ', street: 'Praça Sen. Salgado Filho' }, amenities: ['Wi-Fi', 'Água', 'Atendimento Rápido'], code: 'SDU', company: company:movida, contact: { email: 'agencia.sdu@movida.com.br', manager_name: 'Pedro Alves', phone: '+55 21 3333-0000' }, created_at: d'2026-04-27T22:30:47.324101728Z', id: store:sdumont_movida, instructions: { dropoff: 'Acesso pela pista lateral antes do embarque.', extra: 'Recomendamos antecedência de 2 horas para a devolução.', pickup: 'Desça a escada rolante até o desembarque, nosso balcão estará à esquerda.' }, location: (-43.1631, -22.9105), location_type: 'AIRPORT', name: 'Movida Aeroporto Santos Dumont', operating_hours: [{ close: '23:00', day_of_week: 'MONDAY', is_closed: false, open: '06:00' }, { close: '23:00', day_of_week: 'TUESDAY', is_closed: false, open: '06:00' }, { close: '23:00', day_of_week: 'WEDNESDAY', is_closed: false, open: '06:00' }, { close: '23:00', day_of_week: 'THURSDAY', is_closed: false, open: '06:00' }, { close: '23:00', day_of_week: 'FRIDAY', is_closed: false, open: '06:00' }, { close: '22:00', day_of_week: 'SATURDAY', is_closed: false, open: '06:00' }, { close: '23:00', day_of_week: 'SUNDAY', is_closed: false, open: '06:00' }], pickup_method: 'IN_TERMINAL', special_hours: [], updated_at: d'2026-04-27T22:30:47.324211321Z' } ];

-- ------------------------------
-- TABLE: user
-- ------------------------------

DEFINE TABLE user TYPE NORMAL SCHEMAFULL PERMISSIONS NONE;

DEFINE FIELD active ON user TYPE bool DEFAULT true PERMISSIONS FULL;
DEFINE FIELD birth_date ON user TYPE none | datetime PERMISSIONS FULL;
DEFINE FIELD created_at ON user TYPE datetime DEFAULT time::now() READONLY PERMISSIONS FULL;
DEFINE FIELD document_id ON user TYPE none | string PERMISSIONS FULL;
DEFINE FIELD email ON user TYPE string ASSERT string::is_email($value) PERMISSIONS FULL;
DEFINE FIELD first_name ON user TYPE string ASSERT string::len($value) > 1 PERMISSIONS FULL;
DEFINE FIELD last_name ON user TYPE string ASSERT string::len($value) > 1 PERMISSIONS FULL;
DEFINE FIELD password_hash ON user TYPE string PERMISSIONS FULL;
DEFINE FIELD phone ON user TYPE none | string PERMISSIONS FULL;
DEFINE FIELD updated_at ON user TYPE datetime VALUE time::now() PERMISSIONS FULL;



-- ------------------------------
-- TABLE DATA: user
-- ------------------------------

INSERT [ { active: true, created_at: d'2026-04-27T22:29:24.794477063Z', document_id: '111.222.333-44', email: 'roberto.costa@localiza.com', first_name: 'Roberto', id: user:admin_localiza, last_name: 'Costa', password_hash: '$argon2id$v=19$m=16,t=2,p=1$dXl1d3dQd1ZQS2RFU1c5dw$JVT+I0bJypeMwLRBkp+Gag', phone: '+55 31 97777-3333', updated_at: d'2026-04-27T23:49:01.948272607Z' }, { active: true, created_at: d'2026-04-27T22:29:24.794942716Z', document_id: '444.555.666-77', email: 'fernanda.lima@movida.com.br', first_name: 'Fernanda', id: user:admin_movida, last_name: 'Lima', password_hash: '$argon2id$v=19$m=16,t=2,p=1$dXl1d3dQd1ZQS2RFU1c5dw$JVT+I0bJypeMwLRBkp+Gag', phone: '+55 11 94444-6666', updated_at: d'2026-04-27T23:49:01.949165641Z' }, { active: true, created_at: d'2026-04-27T22:29:24.794792993Z', email: 'carlos.pereira@localiza.com', first_name: 'Carlos', id: user:atendente_sp_localiza, last_name: 'Pereira', password_hash: '$argon2id$v=19$m=16,t=2,p=1$dXl1d3dQd1ZQS2RFU1c5dw$JVT+I0bJypeMwLRBkp+Gag', phone: '+55 11 95555-5555', updated_at: d'2026-04-27T23:49:01.949251364Z' }, { active: true, birth_date: d'1985-05-15T00:00:00Z', created_at: d'2026-04-27T22:29:24.794170812Z', document_id: '123.456.789-00', email: 'joao.silva@email.com', first_name: 'João', id: user:cliente1, last_name: 'Silva', password_hash: '$argon2id$v=19$m=16,t=2,p=1$dXl1d3dQd1ZQS2RFU1c5dw$JVT+I0bJypeMwLRBkp+Gag', phone: '+55 11 99999-1111', updated_at: d'2026-04-27T23:49:01.949355493Z' }, { active: true, birth_date: d'1990-10-20T00:00:00Z', created_at: d'2026-04-27T22:29:24.794339042Z', document_id: '987.654.321-11', email: 'maria.oliveira@email.com', first_name: 'Maria', id: user:cliente2, last_name: 'Oliveira', password_hash: '$argon2id$v=19$m=16,t=2,p=1$dXl1d3dQd1ZQS2RFU1c5dw$JVT+I0bJypeMwLRBkp+Gag', phone: '+55 21 98888-2222', updated_at: d'2026-04-27T23:49:01.949426167Z' }, { active: true, created_at: d'2026-04-27T22:29:24.795076900Z', email: 'pedro.alves@movida.com.br', first_name: 'Pedro', id: user:gerente_rj_movida, last_name: 'Alves', password_hash: '$argon2id$v=19$m=16,t=2,p=1$dXl1d3dQd1ZQS2RFU1c5dw$JVT+I0bJypeMwLRBkp+Gag', phone: '+55 21 93333-7777', updated_at: d'2026-04-27T23:49:01.949488275Z' }, { active: true, created_at: d'2026-04-27T22:29:24.794616566Z', email: 'ana.santos@localiza.com', first_name: 'Ana', id: user:gerente_sp_localiza, last_name: 'Santos', password_hash: '$argon2id$v=19$m=16,t=2,p=1$dXl1d3dQd1ZQS2RFU1c5dw$JVT+I0bJypeMwLRBkp+Gag', phone: '+55 11 96666-4444', updated_at: d'2026-04-27T23:49:01.949546566Z' } ];

-- ------------------------------
-- TABLE: vehicle
-- ------------------------------

DEFINE TABLE vehicle TYPE NORMAL SCHEMAFULL PERMISSIONS NONE;

DEFINE FIELD category ON vehicle TYPE record<vehicle_category> PERMISSIONS FULL;
DEFINE FIELD chassis_number ON vehicle TYPE string ASSERT string::len($value) = 17 PERMISSIONS FULL;
DEFINE FIELD color ON vehicle TYPE string PERMISSIONS FULL;
DEFINE FIELD company ON vehicle TYPE record<company> PERMISSIONS FULL;
DEFINE FIELD created_at ON vehicle TYPE datetime DEFAULT time::now() READONLY PERMISSIONS FULL;
DEFINE FIELD current_store ON vehicle TYPE record<store> PERMISSIONS FULL;
DEFINE FIELD make ON vehicle TYPE string PERMISSIONS FULL;
DEFINE FIELD mileage_km ON vehicle TYPE int DEFAULT 0 ASSERT $value >= 0 PERMISSIONS FULL;
DEFINE FIELD model ON vehicle TYPE string PERMISSIONS FULL;
DEFINE FIELD plate ON vehicle TYPE string ASSERT string::len($value) >= 6 PERMISSIONS FULL;
DEFINE FIELD status ON vehicle TYPE string DEFAULT 'AVAILABLE' ASSERT $value INSIDE ['AVAILABLE', 'RENTED', 'MAINTENANCE', 'IN_TRANSIT', 'DECOMMISSIONED'] PERMISSIONS FULL;
DEFINE FIELD updated_at ON vehicle TYPE datetime VALUE time::now() PERMISSIONS FULL;
DEFINE FIELD year ON vehicle TYPE int ASSERT $value >= 2000 PERMISSIONS FULL;



-- ------------------------------
-- TABLE DATA: vehicle
-- ------------------------------

INSERT [ { category: vehicle_category:loc_eco, chassis_number: '9BR1234567890ABCD', color: 'Branco', company: company:localiza, created_at: d'2026-04-27T22:31:53.039531982Z', current_store: store:cgh_localiza, id: vehicle:loc_kwid_1, make: 'Renault', mileage_km: 15400, model: 'Kwid Zen 1.0', plate: 'ABC1D23', status: 'AVAILABLE', updated_at: d'2026-04-27T22:31:53.039577158Z', year: 2023 }, { category: vehicle_category:loc_suv, chassis_number: '9BR9876543210WXYZ', color: 'Prata', company: company:localiza, created_at: d'2026-04-27T22:31:53.039800631Z', current_store: store:cgh_localiza, id: vehicle:loc_renegade_1, make: 'Jeep', mileage_km: 5200, model: 'Renegade Sport 1.3 Turbo', plate: 'XYZ9W87', status: 'AVAILABLE', updated_at: d'2026-04-27T22:31:53.039855696Z', year: 2024 }, { category: vehicle_category:mov_eco, chassis_number: '9BW1112223334ABCD', color: 'Preto', company: company:movida, created_at: d'2026-04-27T22:31:53.040007273Z', current_store: store:sdumont_movida, id: vehicle:mov_polo_1, make: 'Volkswagen', mileage_km: 8100, model: 'Polo Track 1.0 TSI', plate: 'RIO2A22', status: 'AVAILABLE', updated_at: d'2026-04-27T22:31:53.040022151Z', year: 2024 } ];

-- ------------------------------
-- TABLE: vehicle_category
-- ------------------------------

DEFINE TABLE vehicle_category TYPE NORMAL SCHEMAFULL PERMISSIONS NONE;

DEFINE FIELD acriss_code ON vehicle_category TYPE none | string ASSERT $value = NONE OR string::len($value) = 4 PERMISSIONS FULL;
DEFINE FIELD active ON vehicle_category TYPE bool DEFAULT true PERMISSIONS FULL;
DEFINE FIELD code ON vehicle_category TYPE string ASSERT string::len($value) > 1 PERMISSIONS FULL;
DEFINE FIELD company ON vehicle_category TYPE record<company> PERMISSIONS FULL;
DEFINE FIELD created_at ON vehicle_category TYPE datetime DEFAULT time::now() READONLY PERMISSIONS FULL;
DEFINE FIELD description ON vehicle_category TYPE none | string PERMISSIONS FULL;
DEFINE FIELD features ON vehicle_category TYPE object PERMISSIONS FULL;
DEFINE FIELD features.air_conditioning ON vehicle_category TYPE bool DEFAULT true PERMISSIONS FULL;
DEFINE FIELD features.capacity ON vehicle_category TYPE object PERMISSIONS FULL;
DEFINE FIELD features.capacity.large_suitcases ON vehicle_category TYPE int DEFAULT 0 PERMISSIONS FULL;
DEFINE FIELD features.capacity.passengers ON vehicle_category TYPE int ASSERT $value >= 1 PERMISSIONS FULL;
DEFINE FIELD features.capacity.small_suitcases ON vehicle_category TYPE int DEFAULT 0 PERMISSIONS FULL;
DEFINE FIELD features.doors ON vehicle_category TYPE int ASSERT $value >= 2 PERMISSIONS FULL;
DEFINE FIELD features.fuel_type ON vehicle_category TYPE string ASSERT $value INSIDE ['GASOLINE', 'DIESEL', 'ELECTRIC', 'HYBRID', 'FLEX'] PERMISSIONS FULL;
DEFINE FIELD features.transmission ON vehicle_category TYPE string ASSERT $value INSIDE ['MANUAL', 'AUTOMATIC'] PERMISSIONS FULL;
DEFINE FIELD group_name ON vehicle_category TYPE string PERMISSIONS FULL;
DEFINE FIELD image_url ON vehicle_category TYPE none | string ASSERT $value = NONE OR string::is_url($value) PERMISSIONS FULL;
DEFINE FIELD representative_models ON vehicle_category TYPE array<string> PERMISSIONS FULL;
DEFINE FIELD representative_models.* ON vehicle_category TYPE string PERMISSIONS FULL;
DEFINE FIELD updated_at ON vehicle_category TYPE datetime VALUE time::now() PERMISSIONS FULL;



-- ------------------------------
-- TABLE DATA: vehicle_category
-- ------------------------------

INSERT [ { acriss_code: 'CFAR', active: true, code: 'GX', company: company:localiza, created_at: d'2026-04-27T22:30:47.325241964Z', description: 'Veículos mais altos e confortáveis, ideais para famílias.', features: { air_conditioning: true, capacity: { large_suitcases: 2, passengers: 5, small_suitcases: 2 }, doors: 4, fuel_type: 'FLEX', transmission: 'AUTOMATIC' }, group_name: 'SUV Compacto', id: vehicle_category:loc_suv, image_url: 'https://example.com/images/loc_suv.png', representative_models: ['Jeep Renegade', 'VW Kicks', 'Hyundai T-Cross'], updated_at: d'2026-04-27T22:30:47.325272593Z' }, { acriss_code: 'ECAR', active: true, code: 'AX', company: company:movida, created_at: d'2026-04-27T22:30:47.325541876Z', description: 'Econômico, prático com o conforto do câmbio automático.', features: { air_conditioning: true, capacity: { large_suitcases: 1, passengers: 5, small_suitcases: 2 }, doors: 4, fuel_type: 'FLEX', transmission: 'AUTOMATIC' }, group_name: 'Econômico com Ar', id: vehicle_category:mov_eco, image_url: 'https://example.com/images/mov_eco.png', representative_models: ['VW Polo', 'Chevrolet Onix', 'Hyundai HB20'], updated_at: d'2026-04-27T22:30:47.325568178Z' } ];

-- ------------------------------
-- TABLE: works_at
-- ------------------------------

DEFINE TABLE works_at TYPE RELATION IN user OUT store SCHEMAFULL PERMISSIONS NONE;

DEFINE FIELD created_at ON works_at TYPE datetime DEFAULT time::now() READONLY PERMISSIONS FULL;
DEFINE FIELD in ON works_at TYPE record<user> PERMISSIONS FULL;
DEFINE FIELD out ON works_at TYPE record<store> PERMISSIONS FULL;
DEFINE FIELD role ON works_at TYPE string DEFAULT 'CLERK' ASSERT $value INSIDE ['MANAGER', 'CLERK', 'MECHANIC'] PERMISSIONS FULL;



-- ------------------------------
-- TABLE DATA: works_at
-- ------------------------------

INSERT RELATION [ { created_at: d'2026-04-27T22:30:47.324686755Z', id: works_at:7uhk6m9zkrtgipwwb27b, in: user:gerente_sp_localiza, out: store:cgh_localiza, role: 'MANAGER' }, { created_at: d'2026-04-27T22:30:47.324912193Z', id: works_at:ichgcu8su4fktghzltge, in: user:gerente_rj_movida, out: store:sdumont_movida, role: 'MANAGER' }, { created_at: d'2026-04-27T22:30:47.324796348Z', id: works_at:n6x1ohk5f5z0vfks60ca, in: user:atendente_sp_localiza, out: store:cgh_localiza, role: 'CLERK' } ];

