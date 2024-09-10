from flask import Blueprint, jsonify, request
from employee_app import db
from employee_app.models import Employee
from employee_app.schema import EmployeeSchema
from lib.helper_functions import get_employee_by_id, add_employee, update_employee, delete_employee

employee_bp = Blueprint('employee', __name__)
employee_schema = EmployeeSchema() 
employees_schema = EmployeeSchema(many=True)

@employee_bp.route('/', methods=['GET'])
def get_all_employees():
    all_employees = Employee.query.all()
    result = employees_schema.dump(all_employees)
    return jsonify(result)

@employee_bp.route('/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    employee = get_employee_by_id(employee_id)
    if not employee:
        return jsonify({'message': 'Employee not found'}), 404
    return employee_schema.jsonify(employee)

@employee_bp.route('/', methods=['POST'])
def create_employee():
    data = request.get_json()
    new_employee = add_employee(data)
    return employee_schema.jsonify(new_employee), 201

@employee_bp.route('/<int:employee_id>', methods=['PUT'])
def update_employee_details(employee_id):
    employee = get_employee_by_id(employee_id)
    if not employee:
        return jsonify({'message': 'Employee not found'}), 404

    data = request.get_json()
    updated_employee = update_employee(employee_id, data)
    return employee_schema.jsonify(updated_employee)

@employee_bp.route('/<int:employee_id>', methods=['DELETE'])
def delete_employee_details(employee_id):
    employee = get_employee_by_id(employee_id)
    if not employee:
        return jsonify({'message': 'Employee not found'}), 404

    delete_employee(employee_id)
    return jsonify({'message': 'Employee deleted successfully'}), 200

@employee_bp.route('/webhook', methods=['POST'])
def webhook():
    if 'smartsheetHookChallenge' in request.headers:
        # Respond to the verification request
        challenge = request.headers['smartsheetHookChallenge']
        print("----->>>>", challenge)
        return jsonify({'smartsheetHookResponse': challenge}), 200
    data = request.json
    print(data)
    return jsonify({'status': 'success'}), 200