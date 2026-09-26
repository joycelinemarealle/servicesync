from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

#for database
from app.database import Base
class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False) #hold value from customers table + cant be empty
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    start_time = Column(DateTime, nullable=False, unique=True)
    status = Column(String, nullable=False, default="confirmed")
    created_at = Column(DateTime, nullable=False, server_default=func.now())     # allows appointment.service.namepyth

    # allows appointment.service.namepyth
    customer = relationship("Customer")
    service = relationship("Service")


class Service(Base):
    __tablename__ =  "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    price = Column(Integer, nullable=True)
    duration_minutes = Column(Integer, nullable=True)

