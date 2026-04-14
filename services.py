from models import db, Ingredient, Event, MenuItem, Recipe, Order, InventoryLog, Customer, Staff, Task
from sqlalchemy import text
from datetime import date, timedelta, datetime
import math

class DashboardService:
    @staticmethod
    def get_menu_pricing_suggestions(location_id):
        suggestions = []
        
        # Get events in next 48 hours
        today = date.today()
        tomorrow = today + timedelta(days=1)
        events = Event.query.filter(Event.event_date.between(today, tomorrow)).all()
        
        # Iterate through menu items
        menu_items = MenuItem.query.all()
        
        for item in menu_items:
            markup = 0.0
            reason = "Standard Demand"
            
            # Check all ingredients for menu item
            recipes = Recipe.query.filter_by(menu_id=item.menu_id).all()
            for r in recipes:
                stock = DashboardService.get_current_stock(location_id, r.ing_id)
                # If stock critically low apply scarcity markup
                if stock < 15:
                    markup = max(markup, 0.15)
                    reason = "Inventory Scarcity (Ingredients low)"
            
            # Check for demand surge
            for e in events:
                if e.impact_multiplier > 1.3:
                    markup = max(markup, 0.20)
                    reason = f"High Demand Event: {e.event_name}"
            
            suggested_price = item.base_price * (1 + markup)
            
            suggestions.append({
                "menuItemName": item.name,
                "currentPrice": item.base_price,
                "suggestedPrice": round(suggested_price, 2),
                "surgeReason": reason,
                "stockStatus": "Surge Pricing Active" if markup > 0 else "Stable"
            })
            
        return suggestions

    @staticmethod
    def get_manager_dashboard(location_id):
        alerts = []
        ingredients = Ingredient.query.all()
        
        # Get upcoming events for next 7 days
        today = date.today()
        next_week = today + timedelta(days=7)
        upcoming_events = Event.query.filter(Event.event_date.between(today, next_week)).all()
        
        for ing in ingredients:
            current_stock = DashboardService.get_current_stock(location_id, ing.ing_id)
            base_burn_rate = DashboardService.get_actual_daily_burn_rate(location_id, ing.ing_id)
            
            total_projected_usage_next_7_days = 0
            max_multiplier_found = 1.0
            highest_impact_event_name = ""
            
            for day in range(7):
                future_date = today + timedelta(days=day)
                daily_multiplier = 1.0
                
                for e in upcoming_events:
                    if e.event_date == future_date:
                        daily_multiplier = e.impact_multiplier
                        if daily_multiplier > max_multiplier_found:
                            max_multiplier_found = daily_multiplier
                            highest_impact_event_name = e.event_name
                
                total_projected_usage_next_7_days += (base_burn_rate * daily_multiplier)
            
            avg_event_adjusted_burn_rate = total_projected_usage_next_7_days / 7.0
            days_until_stockout = 999
            if avg_event_adjusted_burn_rate > 0:
                days_until_stockout = int(current_stock / avg_event_adjusted_burn_rate)
            
            suggested_markup = 0.0
            pricing_rationale = "Standard Pricing"
            
            if max_multiplier_found > 1.2:
                if days_until_stockout <= ing.lead_time_days:
                    suggested_markup = 0.20
                    pricing_rationale = f"Critical Stockout Risk + {highest_impact_event_name}"
                else:
                    suggested_markup = 0.10
                    pricing_rationale = f"Increased Demand: {highest_impact_event_name}"
            elif days_until_stockout <= 1:
                suggested_markup = 0.05
                pricing_rationale = "Inventory Scarcity"
            
            lead_time = ing.lead_time_days
            status = "OK"
            event_note = f" [Impact: {highest_impact_event_name}]" if highest_impact_event_name else ""
            recommendation = f"Healthy Stock{event_note}"
            
            if days_until_stockout <= lead_time:
                status = "CRITICAL"
                recommendation = f"ORDER IMMEDIATELY: Stockout in {days_until_stockout} days.{event_note}"
            elif days_until_stockout <= lead_time + 2:
                status = "WARNING"
                recommendation = f"Low stock. Reorder within 48 hours.{event_note}"
            
            alerts.append({
                "ingredientName": ing.name,
                "currentStock": current_stock,
                "dailyBurnRate": round(avg_event_adjusted_burn_rate, 1),
                "daysUntilStockout": days_until_stockout,
                "status": status,
                "suggestedPriceMarkup": suggested_markup,
                "pricingRationale": pricing_rationale,
                "recommendation": "ORDER IMMEDIATELY" if status == "CRITICAL" else "Monitor Stock",
                "dataSource": "aws-0-us-west-2.pooler.supabase.com"
            })
            
        return alerts

    @staticmethod
    def get_current_stock(location_id, ing_id):
        log = InventoryLog.query.filter_by(location_id=location_id, ing_id=ing_id).order_by(InventoryLog.log_id.desc()).first()
        return log.stock_level if log else 0

    @staticmethod
    def get_actual_daily_burn_rate(location_id, ing_id):
        # Using raw SQL for the join and aggregation as in the original Java code
        sql = text("""
            SELECT COALESCE(SUM(o.quantity * r.qty_needed), 0) / 7.0
            FROM orders o
            JOIN recipes r ON o.menu_id = r.menu_id
            WHERE o.location_id = :locId
            AND r.ing_id = :ingId
            AND o.order_date >= NOW() - INTERVAL '7 days'
        """)
        
        result = db.session.execute(sql, {"locId": location_id, "ing_id": ing_id}).scalar()
        actual_rate = float(result) if result is not None else 0.0
        return max(actual_rate, 10.0)

class CustomerService:
    @staticmethod
    def get_all_customers():
        customers = Customer.query.all()
        return [{
            "customer_id": c.customer_id,
            "name": c.name,
            "email": c.email,
            "phone": c.phone,
            "loyalty_points": c.loyalty_points,
            "created_at": c.created_at.isoformat()
        } for c in customers]

    @staticmethod
    def create_customer(data):
        customer = Customer(
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            loyalty_points=data.get('loyalty_points', 0)
        )
        db.session.add(customer)
        db.session.commit()
        return customer.customer_id

    @staticmethod
    def get_customer_by_id(customer_id):
        c = Customer.query.get(customer_id)
        if not c:
            return None
        return {
            "customer_id": c.customer_id,
            "name": c.name,
            "email": c.email,
            "phone": c.phone,
            "loyalty_points": c.loyalty_points,
            "created_at": c.created_at.isoformat()
        }

class StaffService:
    @staticmethod
    def get_all_staff():
        staff = Staff.query.all()
        return [{
            "staff_id": s.staff_id,
            "name": s.name,
            "role": s.role,
            "email": s.email
        } for s in staff]

    @staticmethod
    def create_staff(data):
        staff = Staff(
            name=data.get('name'),
            role=data.get('role'),
            email=data.get('email')
        )
        db.session.add(staff)
        db.session.commit()
        return staff.staff_id

class TaskService:
    @staticmethod
    def get_all_tasks():
        tasks = Task.query.all()
        return [{
            "task_id": t.task_id,
            "description": t.description,
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "status": t.status,
            "assigned_to": t.assigned_to
        } for t in tasks]

    @staticmethod
    def create_task(data):
        task = Task(
            description=data.get('description'),
            due_date=datetime.fromisoformat(data.get('due_date')) if data.get('due_date') else None,
            status=data.get('status', 'Pending'),
            assigned_to=data.get('assigned_to')
        )
        db.session.add(task)
        db.session.commit()
        return task.task_id

    @staticmethod
    def update_task_status(task_id, status):
        task = Task.query.get(task_id)
        if task:
            task.status = status
            db.session.commit()
            return True
        return False

class OrderService:
    @staticmethod
    def create_order(data):
        order = Order(
            order_date=datetime.now(),
            location_id=data.get('location_id'),
            customer_id=data.get('customer_id'),
            menu_id=data.get('menu_id'),
            quantity=data.get('quantity'),
            total_price=data.get('total_price'),
            status=data.get('status', 'Completed'),
            is_surge_pricing=data.get('is_surge_pricing', False)
        )
        db.session.add(order)
        
        # Update loyalty points if customer exists
        if order.customer_id:
            customer = Customer.query.get(order.customer_id)
            if customer:
                customer.loyalty_points += int(order.total_price)
        
        db.session.commit()
        return order.order_id
