
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Annotated

from database import Base, engine, get_db
import models

# Create MySQL tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Employee Management System API")

# Database session dependency
DBSession = Annotated[Session, Depends(get_db)]


# Request data validation
class EmployeeCreate(BaseModel):
    name: str
    age: int
    email: EmailStr
    salary: float
    department: str


class EmployeeUpdate(BaseModel):
    name: str
    age: int
    email: EmailStr
    salary: float
    department: str


class EmployeeResponse(EmployeeCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


# HOME
@app.get("/")
def home():
    return {"message": "Employee Management API is running!"}


# CREATE: Add employee
@app.post("/employees", response_model=EmployeeResponse, status_code=201)
def create_employee(data: EmployeeCreate, db: DBSession):
    existing = db.query(models.Employee).filter(
        models.Employee.email == str(data.email)
    ).first()

    if existing:
        raise HTTPException(status_code=409, detail="Email already exists")

    employee = models.Employee(**data.model_dump())
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


# READ: Get all employees
@app.get("/employees", response_model=list[EmployeeResponse])
def get_employees(db: DBSession):
    return db.query(models.Employee).all()


# READ: Get one employee by ID
@app.get("/employees/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: int, db: DBSession):
    employee = db.query(models.Employee).filter(
        models.Employee.id == employee_id
    ).first()

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    return employee


# UPDATE: Update employee by ID
@app.put("/employees/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int, data: EmployeeUpdate, db: DBSession
):
    employee = db.query(models.Employee).filter(
        models.Employee.id == employee_id
    ).first()

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    duplicate = db.query(models.Employee).filter(
        models.Employee.email == str(data.email),
        models.Employee.id != employee_id
    ).first()

    if duplicate:
        raise HTTPException(status_code=409, detail="Email already exists")

    for key, value in data.model_dump().items():
        setattr(employee, key, value)

    db.commit()
    db.refresh(employee)
    return employee


# DELETE: Delete employee by ID
@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int, db: DBSession):
    employee = db.query(models.Employee).filter(
        models.Employee.id == employee_id
    ).first()

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    db.delete(employee)
    db.commit()

    return {"message": "Employee deleted successfully"}


if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
