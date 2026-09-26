from sqlalchemy.exc import IntegrityError
from app.database import SessionLocal
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import app
from app.models import Customer, Service, Appointment
from app.schemas import(
    CustomerCreate, CustomerRead,
    ServiceCreate, ServiceRead,
    AppointmentCreate, AppointmentRead
)

#when send POST request to this ULR run create_appointment function
#POST sending you data to creat something, the return filter through model
#payload(dummy variable is data client sending me, comes back in schema form set
#FastApi does automatic validation take json request check follow schema of create and return as payload validate by A..Read
#Session every request is a session
#get_db FastAPI dependency injection before running function call get_db(), what produced put in db

#1)open door with , 2) client input validation, 3)validate the references 4) create appointment 5) save to db add,commit,references 6) return appointment
app = FastAPI(title="ServiceSync")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/appointments", response_model=AppointmentRead)
def create_appointment(payload:AppointmentCreate, db: Session = Depends(get_db)):
    # validate references first, for clean error messages. see if customer and service exist in database
    if db.query(Customer).filter(Customer.id == payload.customer_id).first() is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    if db.query(Service).filter(Service.id == payload.service_id).first() is None:
        raise HTTPException(status_code=404, detail="Service not found")

   #create appointment
    appointment = Appointment(
        customer_id=payload.customer_id,
        service_id=payload.service_id,
        start_time=payload.start_time,
    )
#409 error request invalid more specific than 500 which something went wrong with server
    db.add(appointment)
    try:
        db.commit() #try to save
    except IntegrityError: #database rejected (duplicate start_time
        db.rollback()   #undo failed transaction
        raise HTTPException(
            status_code=409,
            detail="That time slot is already booked."
        )
    db.refresh(appointment)
    return appointment


@app.get("/appointments/{appointment_id}", response_model=AppointmentRead)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appoiontmnet not found")
    return appointment

@app.post("/customers", response_model=CustomerRead)
def create_customer(payload:CustomerCreate, db: Session = Depends(get_db)):
    #Create customer
    customer = Customer(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

@app.get("/customers/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id:int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@app.post("/services", response_model=ServiceRead)
def create_service(payload:ServiceCreate, db: Session = Depends(get_db)):

    service = Service(
        name=payload.name,
        price=payload.price,
        duration_minutes=payload.duration_minutes,
    )

    db.add(service)
    db.commit()
    db.refresh(service)
    return service

@app.get("/services/{service_id}", response_model=ServiceRead)
def get_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return service
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
