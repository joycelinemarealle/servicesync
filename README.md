
# ServiceSync

A backend booking system for a hair business — customers can register, browse services, and book appointments with the stylist. Built as a learning project to go deep on backend engineering, databases, and (later) distributed systems.

Originally prototyped as a Java/Spring/Angular app; this version is a ground-up rebuild in Python to focus on backend fundamentals done well.

## What it does

- Register and look up customers
- List the services on offer (e.g. braiding, blowout) with price and duration
- Book an appointment linking a customer to a service at a specific time
- (In progress) Prevent double-booking the same time slot

## Tech stack

- **FastAPI** — web framework for the REST API
- **PostgreSQL** — database, run in Docker
- **SQLAlchemy** — talks to the database using Python objects instead of raw SQL
- **Pydantic** — validates data coming in and going out of the API
- **Docker** — runs Postgres in an isolated container
- **Alembic** — database migrations (planned)

### Planned additions

- **React** — a frontend so customers can register and book from a browser, calling this API
- **Docker Compose** — run the app and database together with one command
- **Kubernetes** — container orchestration, to explore running the system as scalable, self-healing services once it's split into multiple pieces

### Planned AI layer

An LLM used as an untrusted input parser at the edge — it turns messy human text into structured, validated data, then normal deterministic code does the actual database work.

- **Natural-language service search** — e.g. "box braids under $100 this weekend" parsed into a structured query (service type + price + date)
- **Smart scheduling suggestions** — when a slot is taken, suggest the best alternative times based on service duration and existing bookings
- **Booking assistant chatbot** — a conversational way to book, where the model calls the booking logic via tool calling and handles multi-turn state

## How it's structured

```
servicesync/
  app/
    __init__.py
    database.py     # database connection + session setup
    models.py       # database tables (Customer, Service, Appointment)
    schemas.py      # data shapes for API requests/responses
    main.py         # the API endpoints
  create_tables.py  # one-off script to create the tables
```

### The data model

Three tables, with Appointment linking the other two:

- **Customer** — id, name, email, phone
- **Service** — id, name, price, duration
- **Appointment** — id, customer_id (→ Customer), service_id (→ Service), start_time, status

An appointment belongs to one customer and one service; a customer or service can have many appointments.

## Running it locally

**Prerequisites:** Python 3.11+, Docker Desktop.

1. **Start the database** (runs Postgres in Docker, exposed on port 5433):
   ```
   docker run --name servicesync-db \
     -e POSTGRES_PASSWORD=devpass \
     -e POSTGRES_DB=servicesync \
     -p 5433:5432 -d postgres:16
   ```
   > Note: mapped to **5433** (not the default 5432) to avoid a conflict with a native Postgres already running on this machine.

2. **Set up the Python environment:**
   ```
   python -m venv venv
   source venv/bin/activate
   pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv alembic "pydantic[email]"
   ```

3. **Create the tables:**
   ```
   python create_tables.py
   ```

4. **Run the API:**
   ```
   uvicorn app.main:app --reload
   ```

5. **Open the interactive docs** at http://localhost:8000/docs to try the endpoints.

## API endpoints

| Method | Path | What it does |
|--------|------|--------------|
| POST | `/customers` | Register a new customer |
| GET | `/customers/{id}` | Get a customer by id |
| POST | `/services` | Add a service |
| GET | `/services` | List all services |
| POST | `/appointments` | Book an appointment |
| GET | `/appointments/{id}` | Get an appointment by id |

## Roadmap

- [ ] Prevent double-booking (transactions + locking)
- [ ] Authentication (password hashing + JWT login)
- [ ] Automated tests (pytest)
- [ ] Database migrations with Alembic
- [ ] React frontend
- [ ] Containerize the app with Docker Compose
- [ ] Explore deployment / orchestration
- [ ] AI: natural-language service search
- [ ] AI: smart scheduling suggestions
- [ ] AI: booking assistant chatbot

## Notes

This is a learning project, built step by step to understand *why* each piece works, not just to make it run.

# servicesync
app uses 5433 port