import requests
import time
import subprocess
import sys
import json

def test_api():
    print("Starting Flask server...")
    # Start Flask server in the background
    process = subprocess.Popen([sys.executable, "app.py"], cwd="/Users/cameronhalaby/Desktop/hackathon/flask_backend")
    time.sleep(5) # Wait for server to start
    
    try:
        # 1. Test Customers
        print("\n--- Testing Customers ---")
        customer_data = {"name": "Test User", "email": f"test_{int(time.time())}@example.com", "phone": "1234567890"}
        res = requests.post("http://localhost:8080/api/customers", json=customer_data)
        print(f"Create Customer Status: {res.status_code}")
        customer_id = res.json().get("customer_id")
        print(f"Customer ID: {customer_id}")

        res = requests.get("http://localhost:8080/api/customers")
        print(f"List Customers Status: {res.status_code}")
        print(f"Customers Count: {len(res.json())}")

        res = requests.get(f"http://localhost:8080/api/customers/{customer_id}")
        print(f"Get Customer Status: {res.status_code}")
        print(f"Customer Name: {res.json().get('name')}")

        # 2. Test Staff
        print("\n--- Testing Staff ---")
        staff_data = {"name": "Staff Member", "role": "Manager", "email": f"staff_{int(time.time())}@example.com"}
        res = requests.post("http://localhost:8080/api/staff", json=staff_data)
        print(f"Create Staff Status: {res.status_code}")
        staff_id = res.json().get("staff_id")
        print(f"Staff ID: {staff_id}")

        res = requests.get("http://localhost:8080/api/staff")
        print(f"List Staff Status: {res.status_code}")
        print(f"Staff Count: {len(res.json())}")

        # 3. Test Tasks
        print("\n--- Testing Tasks ---")
        task_data = {"description": "Reorder buns", "assigned_to": staff_id}
        res = requests.post("http://localhost:8080/api/tasks", json=task_data)
        print(f"Create Task Status: {res.status_code}")
        task_id = res.json().get("task_id")
        print(f"Task ID: {task_id}")

        res = requests.patch(f"http://localhost:8080/api/tasks/{task_id}", json={"status": "In Progress"})
        print(f"Update Task Status: {res.status_code}")

        res = requests.get("http://localhost:8080/api/tasks")
        print(f"List Tasks Status: {res.status_code}")
        print(f"Tasks Count: {len(res.json())}")

        # 4. Test Orders
        print("\n--- Testing Orders ---")
        order_data = {
            "location_id": 1,
            "customer_id": customer_id,
            "menu_id": 1,
            "quantity": 2,
            "total_price": 24.0,
            "status": "Completed"
        }
        res = requests.post("http://localhost:8080/api/orders", json=order_data)
        print(f"Create Order Status: {res.status_code}")
        order_id = res.json().get("order_id")
        print(f"Order ID: {order_id}")

        # Verify loyalty points update
        res = requests.get(f"http://localhost:8080/api/customers/{customer_id}")
        print(f"Customer Loyalty Points: {res.json().get('loyalty_points')}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("\nStopping Flask server...")
        process.terminate()

if __name__ == "__main__":
    test_api()
