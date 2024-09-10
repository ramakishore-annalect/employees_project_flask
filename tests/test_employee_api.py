import sys
import pytest
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

sys.path.append("/Users/ramakishorenooji/code/employees_project_flask")  

from employee_app import create_app, db  
from employee_app.models import Base, Employee
from employee_app.config import TestingConfig

new_mock_db_uri = "postgresql://ramakishorenooji:@localhost/mock_db"

@pytest.fixture(scope="session")
def app():
    """Create a Flask app with the testing configuration."""
    app = create_app(TestingConfig)
    yield app

@pytest.fixture(scope="session")
def test_engine(app):
    """Get the database engine from the app."""
    with app.app_context(): 
        engine = db.engine  # Use db.engine directly
        yield engine

@pytest.fixture(scope="function")
def db_session(test_engine, app):
    Session = scoped_session(sessionmaker(bind=test_engine, autocommit=False)) 
    Base.query = Session.query_property()
    Base.metadata.bind = test_engine

    with app.app_context():
        Base.metadata.create_all(test_engine)
        yield Session
        Session.rollback()
        Base.metadata.drop_all(test_engine)
        Session.remove()

def set_isolation_level(session, isolation_level="READ COMMITTED"):
    """Sets the transaction isolation level for the given session."""
    session.connection().execute(f"SET TRANSACTION ISOLATION LEVEL {isolation_level}")

@pytest.fixture
def client(db_session, app):  # Inject the mock db_session into the client fixture
    app.config["TESTING"] = True
    app.extensions["sqlalchemy"].db = db_session 

    with app.test_client() as client:
        yield client

def test_get_all_employees_empty(client):
    response = client.get('/employees/')
    assert response.status_code == 200
    assert json.loads(response.data) == []

def test_create_employee(client):
    data = {'name': 'John Doe', 'email': 'john.doe@example.com', 'department': 'Engineering'}
    response = client.post('/employees/', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 201
    assert 'id' in json.loads(response.data)

# def test_create_employee_duplicate_email(client):
#     # Create an employee first to simulate a duplicate email scenario
#     existing_employee = Employee(name='Existing Employee', email='existing.email@example.com')
#     db.session.add(existing_employee)
#     db.session.commit()

#     data = {'name': 'John Doe', 'email': 'existing.email@example.com', 'department': 'Engineering'} 

#     with pytest.raises(ValueError) as exc_info:
#         client.post('/employees/', data=json.dumps(data), content_type='application/json')

#     assert str(exc_info.value) == "Employee with this email already exists"

# def test_get_employee(client):
#     employee = Employee(name='Jane Smith', email='jane.smith@example.com')
#     db.session.add(employee)
#     db.session.commit()

#     response = client.get(f'/employees/{employee.id}/')  
#     assert response.status_code == 200
#     assert json.loads(response.data)['name'] == 'Jane Smith'

# def test_update_employee(client):
#     employee = Employee(name='Alice Johnson', email='alice.johnson@example.com')
#     db.session.add(employee)
#     db.session.commit()

#     updated_data = {'name': 'Alice Brown', 'email': 'alice.brown@example.com'}
#     response = client.put(f'/employees/{employee.id}/', data=json.dumps(updated_data), content_type='application/json')
#     assert response.status_code == 200

#     updated_employee = json.loads(response.data)
#     assert updated_employee['name'] == 'Alice Brown'
#     assert updated_employee['email'] == 'alice.brown@example.com'

# def test_delete_employee(client):
#     employee = Employee(name='Bob Wilson', email='bob.wilson@example.com')
#     db.session.add(employee)
#     db.session.commit()

#     response = client.delete(f'/employees/{employee.id}/')
#     assert response.status_code == 200

#     deleted_employee = Employee.query.get(employee.id)
#     assert deleted_employee is None 

# Add more test cases here to cover other scenarios and edge cases
