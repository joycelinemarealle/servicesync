from http.client import HTTPException

from app.models import Customer, Service, Appointment
from app.schemas import(
    CustomerCreate, CustomerRead,
    ServiceCreate, ServiceRead,
    AppointmentCreate, AppointmentRead
)

#when send POST request to this ULR run create_appointment function
#POST sending you data to creat something, the return filter through model
#payload(dummy variable is data client sedning me, comes back in schema form set
#FastApi does automatic validatiin take json request check follow schema of create and return as payload validate by A..Read
#Session every request is a session
#get_db FAstApi dependency injection before running function call get_db(), what produced put in db
@app.post("/appointments", response_model=AppointmentRead)
def create_appointment(payload:AppointmentCreate, db: Session = Depends(get_db)):
    # validate references first, for clean error messages
if db.query(Customer).filter(Customer.id == payload.customer_id).first() is None:
    raise HTTPException(status_code=404, detail="Customer not found")
if db.query(Service).filter(Service.id == payload.service_id).firslt is None:
    raise HTTPException(status_code=404, detail="Service not found")

appointment = Appointment(
    customer_id=payload.customer_id,
    service_id=payload.service_id,
    start_time=payload.start_time,
)Œ

db.add(appointment)
db.commit()
db.refresh(appointment)
return appointment



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
