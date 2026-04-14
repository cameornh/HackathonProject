from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db
from services import DashboardService, CustomerService, StaffService, TaskService, OrderService
from sqlalchemy import text
import os

app = Flask(__name__)
CORS(app)

# Database Configuration
# Using the credentials from application-prod.properties
DB_USER = "postgres.dyzicukfjhfjvsiggucf"
DB_PASS = "Prlax08310805"
DB_HOST = "aws-0-us-west-2.pooler.supabase.com"
DB_PORT = "5432" # Direct connection port
DB_NAME = "postgres"

# For Supabase pooling, sometimes the username needs to be part of the database name or handled specifically.
# Let's try the direct connection first.
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/api/dashboard/pricing-suggestions', methods=['GET'])
def get_pricing_suggestions():
    location_id = request.args.get('locationId', default=1, type=int)
    suggestions = DashboardService.get_menu_pricing_suggestions(location_id)
    return jsonify(suggestions)

@app.route('/api/dashboard/stock-alerts', methods=['GET'])
def get_stock_alerts():
    location_id = request.args.get('locationId', default=1, type=int)
    alerts = DashboardService.get_manager_dashboard(location_id)
    return jsonify(alerts)

# Customer Routes
@app.route('/api/customers', methods=['GET'])
def get_customers():
    customers = CustomerService.get_all_customers()
    return jsonify(customers)

@app.route('/api/customers', methods=['POST'])
def create_customer():
    data = request.json
    customer_id = CustomerService.create_customer(data)
    return jsonify({"customer_id": customer_id}), 201

@app.route('/api/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = CustomerService.get_customer_by_id(customer_id)
    if customer:
        return jsonify(customer)
    return jsonify({"error": "Customer not found"}), 404

# Staff Routes
@app.route('/api/staff', methods=['GET'])
def get_staff():
    staff = StaffService.get_all_staff()
    return jsonify(staff)

@app.route('/api/staff', methods=['POST'])
def create_staff():
    data = request.json
    staff_id = StaffService.create_staff(data)
    return jsonify({"staff_id": staff_id}), 201

# Task Routes
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = TaskService.get_all_tasks()
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.json
    task_id = TaskService.create_task(data)
    return jsonify({"task_id": task_id}), 201

@app.route('/api/tasks/<int:task_id>', methods=['PATCH'])
def update_task_status(task_id):
    data = request.json
    status = data.get('status')
    if TaskService.update_task_status(task_id, status):
        return jsonify({"message": "Task status updated"})
    return jsonify({"error": "Task not found"}), 404

# Order Routes
@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.json
    order_id = OrderService.create_order(data)
    return jsonify({"order_id": order_id}), 201

if __name__ == '__main__':
    app.run(debug=True, port=8080) # Running on 8080 to match frontend's expected port
