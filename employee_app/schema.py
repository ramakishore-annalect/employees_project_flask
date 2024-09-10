from employee_app import  ma
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from employee_app.models import Employee

class EmployeeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Employee
        load_instance = True