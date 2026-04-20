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

INSERT [ { id: company:localiza, name: 'Localiza Rent a Car' } ];

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


