from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime

db = SQLAlchemy()

class Ingredient(db.Model):
    __tablename__ = 'ingredients'
    ing_id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String)
    unit_cost = db.Column(db.Float)
    lead_time_days = db.Column(db.Integer)
    shelf_life_days = db.Column(db.Integer)

class Event(db.Model):
    __tablename__ = 'events'
    event_date = db.Column(db.Date, primary_key=True)
    event_name = db.Column(db.String)
    impact_multiplier = db.Column(db.Float)

class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    menu_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    base_price = db.Column(db.Float)

class Recipe(db.Model):
    __tablename__ = 'recipes'
    menu_id = db.Column(db.Integer, db.ForeignKey('menu_items.menu_id'), primary_key=True)
    ing_id = db.Column(db.BigInteger, db.ForeignKey('ingredients.ing_id'), primary_key=True)
    qty_needed = db.Column(db.Integer)

class Order(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    order_date = db.Column(db.DateTime)
    location_id = db.Column(db.Integer)
    customer_id = db.Column(db.Integer)
    menu_id = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    total_price = db.Column(db.Float)
    status = db.Column(db.String)
    is_surge_pricing = db.Column(db.Boolean)

class InventoryLog(db.Model):
    __tablename__ = 'inventory_logs'
    log_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    log_date = db.Column(db.Date)
    location_id = db.Column(db.Integer)
    ing_id = db.Column(db.BigInteger)
    stock_level = db.Column(db.Integer)
    reorder_suggested = db.Column(db.Boolean)

class Customer(db.Model):
    __tablename__ = 'customers'
    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True)
    phone = db.Column(db.String)
    loyalty_points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Staff(db.Model):
    __tablename__ = 'staff'
    staff_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    role = db.Column(db.String)
    email = db.Column(db.String, unique=True)

class Task(db.Model):
    __tablename__ = 'tasks'
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String, nullable=False)
    due_date = db.Column(db.DateTime)
    status = db.Column(db.String, default='Pending')
    assigned_to = db.Column(db.Integer, db.ForeignKey('staff.staff_id'))
