from app.database import Base, engine
from app.models import Customer, Appointment, Service  # noqa: F401 — must import so Base "sees" the model

Base.metadata.create_all(bind=engine)
print("Tables created.")