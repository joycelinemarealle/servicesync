from pydantic import BaseModel, EmailStr
from datetime import datetime


#use pydantic schema describes data in and out API
# which allows to communicate with outside world, each data is validated automatically
#return http error response
#BaseModel gives free validation,
#EmailStr checks is this valid email

#create schema
#CRUD Create, Retried, Updated, Delete
# name must be string,  email EmailStr type, phone string or nothing None makes it optional
#id created in databse not when client send me data

#creating customer
class CustomerCreate(BaseModel):
    name: str
    email : EmailStr
    phone : str | None = None

#read customer back
class CustomerRead(BaseModel):
    id : int
    name: str
    email : EmailStr
    phone: str | None = None

    class Config:
        from_attributes = True

class AppointmentCreate(BaseModel):
    #no id since client only books and db sets id
    customer_id: int
    service_id: int
    start_time: datetime
    #status is confirmed by default so no need to add it

class AppointmentRead(BaseModel):
    id: int
    customer_id: int
    service_id: int
    start_time: datetime
    status: str

    #allow use of object attributes not just dic like  "id: :1 , "name": Jane customer.id, customer.name
    class Config:
        from_attributes = True

class ServiceCreate(BaseModel):
    name: str
    duration_minutes : int

class ServiceRead(BaseModel):
    id: int
    name: str
    duration_minutes : int

    #allow use of object attributes not just dic like  "id: :1 , "name": Jane customer.id, customer.name
    class Config:
        from_attributes = True

