# ServiceSync

A backend booking system for a hair business — customers can register, browse services, and book appointments with the stylist. Built as a learning project to go deep on backend engineering, databases, and later distributed systems.

Originally prototyped as a Java/Spring/Angular app; this version is a ground-up rebuild in Python to focus on backend fundamentals done well.

## What it does

- Register customers with securely hashed passwords
- Look up customers
- List the services on offer (e.g. braiding, blowout) with price and duration
- Book an appointment linking a customer to a service at a specific time
- Prevent double-booking the same time slot (returns a clean `409 Conflict`)

## Tech stack

- **FastAPI** — web framework for the REST API
- **PostgreSQL** — database, run in Docker
- **SQLAlchemy** — talks to the database using Python objects instead of raw SQL
- **Pydantic** — validates data coming in and going out of the API
- **Argon2 / pwdlib** — hashes and verifies customer passwords
- **Docker** — runs Postgres in an isolated container
- **Alembic** — manages database schema migrations

### Planned additions

- **JWT authentication** — customer login and protected endpoints
- **React** — a frontend so customers can register and book from a browser, calling this API
- **Docker Compose** — run the app and database together with one command
- **Kubernetes** — container orchestration, to explore running the system as scalable, self-healing services once it is split into multiple pieces

### Planned AI layer

An LLM used as an untrusted input parser at the edge — it turns messy human text into structured, validated data, then normal deterministic code does the actual database work.

- **Natural-language service search** — e.g. "box braids under $100 this weekend" parsed into a structured query (service type + price + date)
- **Smart scheduling suggestions** — interpret customer preferences and suggest valid alternatives based on deterministic availability checks
- **Booking assistant chatbot** — a conversational way to book, where the model calls the booking logic through tool calling and handles multi-turn state

## How it is structured

```text
servicesync/
  app/
    __init__.py
    database.py     # database connection + session setup
    models.py       # database tables (Customer, Service, Appointment)
    schemas.py      # data shapes for API requests/responses
    security.py     # password hashing and verification
    main.py         # API endpoints

  alembic/
    versions/       # database migration history
    env.py          # connects Alembic to the app's database/models

  alembic.ini       # Alembic configuration
  create_tables.py  # original script used to create the tables
```

## The data model

Three tables, with `Appointment` linking the other two:

- **Customer** — id, name, email, phone, hashed_password
- **Service** — id, name, price, duration
- **Appointment** — id, customer_id (→ Customer), service_id (→ Service), start_time, status, created_at

An appointment belongs to one customer and one service; a customer or service can have many appointments.

## Running it locally

**Prerequisites:** Python 3.11+, Docker Desktop.

### 1. Start the database

Postgres runs in Docker and is exposed on port `5433`:

```bash
docker run --name servicesync-db \
  -e POSTGRES_PASSWORD=devpass \
  -e POSTGRES_DB=servicesync \
  -p 5433:5432 -d postgres:16
```

> Port `5433` is used instead of the default `5432` to avoid a conflict with a native Postgres already running on the machine.

### 2. Set up the Python environment

```bash
python -m venv venv
source venv/bin/activate
python -m pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv alembic "pydantic[email]" "pwdlib[argon2]"
```

### 3. Create the tables

```bash
python create_tables.py
```

### 4. Run the API

```bash
uvicorn app.main:app --reload
```

### 5. Open the API docs

Open `http://localhost:8000/docs` to test the endpoints through FastAPI's interactive Swagger UI.

## API endpoints

| Method | Path | What it does |
|--------|------|--------------|
| POST | `/customers` | Register a new customer with a hashed password |
| GET | `/customers/{id}` | Get a customer by id |
| POST | `/services` | Add a service |
| GET | `/services` | List all services |
| GET | `/services/{id}` | Get a service by id |
| POST | `/appointments` | Book an appointment; rejects a taken slot with 409 |
| GET | `/appointments/{id}` | Get an appointment by id |

## Preventing double-booking

`start_time` has a **unique constraint** at the database level, so two appointments cannot share the exact same slot.

A naive "check if free, then book" approach has a race condition: two requests arriving at the same time could both see the slot as available before either one saves.

The unique constraint closes that gap. PostgreSQL atomically rejects the second insert. The API catches the resulting `IntegrityError`, rolls back the failed transaction, and returns a `409 Conflict` ("That time slot is already booked.") instead of an unhandled 500 error.

**Current limit:** this prevents exact-time collisions, not duration overlaps. For example, a two-hour appointment starting at 2:00 PM does not yet prevent another appointment from starting at 3:00 PM. Duration-aware overlap detection is a planned follow-up.

## Database migrations with Alembic

Alembic manages changes to the database schema without having to drop and recreate tables.

SQLAlchemy models describe what the schema **should** look like, while PostgreSQL contains the actual existing tables. Alembic tracks schema changes as migrations so the database can be updated while keeping existing data.

Alembic is connected to:

- `DATABASE_URL` — tells Alembic which PostgreSQL database to update
- `Base.metadata` — tells Alembic what tables and columns are defined by the SQLAlchemy models

The database is now tracked by Alembic. Migrations have been used to add `created_at` to appointments and `hashed_password` to customers.

The `hashed_password` column was first added as nullable so existing customer records could be handled safely. After the old development data was removed, a second migration changed the column to `NOT NULL`.

### Migration workflow

After changing a SQLAlchemy model:

```bash
# 1. Generate a migration
python -m alembic revision --autogenerate -m "describe the change"

# 2. Apply the migration
python -m alembic upgrade head

# 3. Verify the models and database are in sync
python -m alembic check
```

Generated migrations are reviewed before applying them to the database.

## Password authentication

Customer passwords are never stored in plaintext. When a customer registers, the password is validated through the Pydantic request schema, hashed with **Argon2**, and only the resulting hash is stored in PostgreSQL.

The `security.py` module contains separate functions for hashing and verifying passwords:

```text
Registration:
password → hash_password() → Argon2 hash → PostgreSQL

Login:
password + stored hash → verify_password() → True / False
```

The raw password and `hashed_password` are not included in the customer response schema, so they are never returned by the API.

Password verification is implemented and tested. JWT login is the next authentication step.

## Roadmap

- [x] Prevent double-booking (unique constraint + 409 Conflict)
- [x] Database migrations with Alembic
- [x] Password hashing with Argon2
- [x] Password verification
- [ ] JWT login
- [ ] Protected authenticated endpoints
- [ ] Duration-aware overlap detection (row locking or exclusion constraint)
- [ ] Automated tests (pytest)
- [ ] AI: natural-language service search
- [ ] AI: smart scheduling suggestions (builds on overlap detection)
- [ ] AI: booking assistant chatbot (needs auth)
- [ ] React frontend
- [ ] Containerize the app with Docker Compose
- [ ] Explore deployment / orchestration

## Notes

This is a learning project, built step by step to understand *why* each piece works, not just to make it run.