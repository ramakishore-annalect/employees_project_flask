from employee_app import db
#from sqlalchemy.ext.declarative import declarative_base

#Base = declarative_base()

class Employee(db.Model):
    __tablename__ = 'employee'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    department = db.Column(db.String(50))
    
    def __repr__(self):
        return f'<Employee {self.name}>'