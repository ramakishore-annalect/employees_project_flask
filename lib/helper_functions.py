from employee_app import db
from employee_app.models import Employee
from sqlalchemy.exc import IntegrityError


def get_employee_by_id(employee_id):
    employee = Employee.query.get(employee_id)
    if not employee:
        raise ValueError("Employee not found")
    return employee


def add_employee(employee_data):
    # Basic validation - you can add more checks as needed
    if not all(key in employee_data for key in ("name", "email")):
        raise ValueError("Missing required fields: name, email")

    new_employee = Employee(**employee_data)
    try:
        db.session.add(new_employee)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError("Employee with this email already exists")
    return new_employee


def update_employee(employee_id, employee_data):
    employee = get_employee_by_id(employee_id)

    for key, value in employee_data.items():
        setattr(employee, key, value)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError("Update failed, possibly due to duplicate email")

    return employee


def delete_employee(employee_id):
    employee = get_employee_by_id(employee_id)
    db.session.delete(employee)
    db.session.commit()
