from app.database import Base, engine
from app.models import Customer #noqa: F401 - must import so  Base "sees" the model

Base.metadata.create_all(bind=engine) #looks at every model inherited from base
print("Tables created.")