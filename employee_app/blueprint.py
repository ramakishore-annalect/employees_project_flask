import os
from flask import Blueprint, jsonify, request
from employee_app import db
from employee_app.models import Employee
from employee_app.schema import EmployeeSchema
from lib.helper_functions import get_employee_by_id, add_employee, update_employee, delete_employee
from lib.smartsheet_helper import SmartsheetJSONUpdater, SmartsheetEventProcessor

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
    updater = SmartsheetJSONUpdater(
        os.environ.get('API_TOKEN')
    )
    updater.update_from_json(data, "updated_Campaigns", "teams_user")
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
    challenge_value = request.headers.get('Smartsheet-Hook-Challenge')
    if challenge_value:
        response = {
            'smartsheetHookResponse': challenge_value
        }
        print("this is the response from the webhook", response)
        return jsonify(response), 200
    data = request.get_json()
    print("Received data: ", data)
    smartsheet_processor = SmartsheetEventProcessor(os.environ.get('API_TOKEN'), data["scopeObjectId"])
    updated_values = smartsheet_processor.get_updated_values(data["events"])
    print("Updated values:", updated_values)
    
    return 'Webhook received', 200