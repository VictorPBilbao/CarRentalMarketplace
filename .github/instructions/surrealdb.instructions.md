---
description: "Use when designing, writing, or refactoring SurrealDB database schemas, queries, or scripts. Enforces SurrealDB 3.0 best practices and strict definitions."
applyTo: "**/*.surql"
---

# SurrealDB 3.0 Design & Schema Standards

- **Target SurrealDB 3.0 features and syntax** for all new database files and queries.
- **Strict Definitions:** Always use explicit `DEFINE` statements.
    - Tables should explicitly define their schema strictness (`SCHEMAFULL` is preferred for structured data).
    - Explicitly define `PERMISSIONS` for tables and fields (e.g., `PERMISSIONS NONE` for backend-only access, or specific `WHERE` clauses for row-level security).
- **Strong Typing & Validation:**
    - Define all fields with explicit types using `DEFINE FIELD` (e.g., `TYPE string`, `TYPE record<other_table>`, `TYPE datetime`).
    - Use `ASSERT` clauses on fields for strict data validation at the database level.
- **Relationships over JOINs:**
    - Leverage SurrealDB's graph database capabilities.
    - Use record links (`record<table_name>`) for one-to-many relationships.
    - Use graph edges (`RELATE`) for many-to-many or complex relationships with properties.
- **Record IDs:**
    - Utilize SurrealDB's native record IDs (`table:id`).
    - Prefer auto-generated IDs or deterministic IDs over custom string manipulation, unless required by domain logic.
- **Events & Indexes:**
    - Define indexes (`DEFINE INDEX`) for querying performance on frequently searched fields.
    - Use `DEFINE EVENT` for reactive database logic (e.g., automatically updating timestamps or auditing).
- **Adhere to the Official Docs:** Always refer to and prefer the patterns shown in the official [SurrealDB Documentation](https://surrealdb.com/docs/surrealdb).

## Example

```surql
-- Users Table
DEFINE TABLE user TYPE NORMAL SCHEMAFULL PERMISSIONS NONE;
DEFINE FIELD email ON user TYPE string ASSERT $value != NONE AND string::is::email($value) PERMISSIONS FULL;
DEFINE FIELD created_at ON user TYPE datetime DEFAULT time::now() PERMISSIONS FULL;

-- Vehicles Table
DEFINE TABLE vehicle TYPE NORMAL SCHEMAFULL PERMISSIONS NONE;
DEFINE FIELD plate ON vehicle TYPE string ASSERT string::len($value) > 5 PERMISSIONS FULL;
DEFINE FIELD active ON vehicle TYPE bool DEFAULT true PERMISSIONS FULL;

-- Rental Edge (Graph Relation)
DEFINE TABLE rented TYPE RELATION IN user OUT vehicle SCHEMAFULL PERMISSIONS NONE;
DEFINE FIELD start_date ON rented TYPE datetime DEFAULT time::now() PERMISSIONS FULL;
DEFINE FIELD end_date ON rented TYPE option<datetime> PERMISSIONS FULL;
```
