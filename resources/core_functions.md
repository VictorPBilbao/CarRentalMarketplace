# Core Functions: Car Rental Marketplace

This document outlines the primary domains, CRUD operations, and specific business logic required for the API and Database schema.

## 1. Store / Location Management (Admin/Manager)

Manages the physical locations where vehicles are picked up and returned.

- **Create/Update Store:** Define location, operating hours, timezone, contact info and other relevant details.
- **Read Stores:** List all stores, or search by geographic coordinates/city.
- **Archive Store:** Soft delete a location (cannot be deleted if active bookings exist).

## 2. Categories (Admin/Manager)

Defines the types of vehicles available (e.g., Economy, SUV, Luxury).

- **Create/Update Category:** Set name, description
- **Read Categories:** List available categories.
- **Archive Category:** Soft delete.

## 3. Groups (Admin/Manager)

A group can be part of a category and can be used to further segment vehicles (e.g., SUV category might have groups like Compact SUV, Full-size SUV), each one with its own pricing and inventory and code. The client will select the group, not the category, but the category is used for filtering and reporting. Inside the group, the client can get any vehicle that belongs to it, so the group is the one that defines the inventory and pricing, not the category.

- **Create/Update Group:** Set name, description, standard passenger capacity, luggage capacity, and transmission type. Creates a SIPP code for standardization.
- **Read Groups:** List available groups.
- **Archive Group:** Soft delete.

## 3. Vehicles / Fleet (Admin/Manager)

Manages the actual physical cars assigned to categories and stores.

- **Create/Update Vehicle:** Register license plate, VIN, make, model, year, category ID, and current store ID.
- **Read Vehicles:** Filter by store, category, or status.
- **Update Status:** Mark a vehicle as `Active`, `In Maintenance`, or `Retired`.

## 4. Optionals / Add-ons (Admin/Manager)

Extras that customers can add to their rental (e.g., Child Seat, GPS).

- **Create/Update Optional:** Define name, description, daily rate OR flat rate, and max quantity per rental.
- **Read Optionals:** List available add-ons.
- **Archive Optional:** Soft delete.

## 5. Protections / Insurance (Admin/Manager)

Coverage plans offered to the customer (e.g., Basic, Premium, Full Coverage).

- **Create/Update Protection:** Set name, description, coverage limits, deductible amount, and daily cost.
- **Read Protections:** List available insurance packages.

## 6. Fees & Surcharges (Admin/Manager)

Conditional charges applied to the rental.

- **Create/Update Fee:** Define fee type (e.g., Young Driver, Cleaning, Airport Tax), application logic (percentage vs. flat), and conditions.
- **Read Fees:** List active fee rules.

## 7. One-Way Drop-off (Admin/Manager)

Rules and pricing for returning a vehicle to a different store than the pickup location.

- **Create/Update Route Fee:** Define a specific fee for `Origin Store A` -> `Destination Store B`. Flat fee or by distance.
- **Read Route Fees:** Get the matrix of relocation costs.

## 8. Pricing Engine (Admin/System)

Manages the dynamic and seasonal pricing of categories.

- **Create/Update Base Price:** Set default daily rate per category/store.
- **Create/Update Seasonal Multiplier:** Set price adjustments for specific date ranges (e.g., Holidays = 1.5x base rate).
- **Calculate Rate (Internal):** Function to calculate the exact daily rate for a specific date range.

## 9. Availability (System/Internal)

Tracks inventory to prevent double-booking. This is read-heavy and requires strict overlap validation.

- **Check Availability:** For a given `Store`, `Date Range`, and `Category`, calculate if `Total Vehicles - Overlapping Bookings > 0`.
- **Block Dates:** Manually block out vehicle availability for maintenance.

## 10. Booking / Checkout (Outsider Client)

The customer-facing transaction flow.

- **Search Availability:** Input: Pickup Store, Drop-off Store, Dates. Output: Available Categories with base prices.
- **Generate Quote:** Input: Category, Dates, selected Optionals, selected Protection, customer age (for fees). Output: Detailed itemized price breakdown (Base + Optionals + Protections + Fees + Taxes).
- **Create Reservation (Checkout):** Lock the vehicle inventory, save customer details, and generate a pending booking.
- **Process Payment:** Confirm transaction and transition booking status from `Pending` to `Confirmed`.
- **Read/Manage Booking:** Customer can view their itinerary.
- **Modify Booking:** Change dates or add-ons (triggers a re-quote and availability check).
- **Cancel Booking:** Release inventory and apply cancellation fee logic.
