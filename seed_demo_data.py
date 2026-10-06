"""
Seed sample categories, suppliers, products, and inventory stock
so the frontend displays rich real data immediately.
"""
import sys
import os
import importlib.util

ROOT = os.path.abspath(os.path.dirname(__file__))

def load_module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

db_path = os.path.join(ROOT, "inventory.db")
db_url = f"sqlite:///{db_path}"
engine = create_engine(db_url, connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)
session = Session()

# Load product models
sys.path.insert(0, os.path.join(ROOT, "backend", "services", "product-service"))
from app.infrastructure.database.models import CategoryModel, SupplierModel, ProductModel
from app.infrastructure.database.database import Base as ProductBase
ProductBase.metadata.create_all(engine)

print("Seeding categories & suppliers...")
cat_electronics = CategoryModel(name="Electronics & Hardware", description="Laptops, monitors, peripherals, and server parts")
cat_office = CategoryModel(name="Office & Ergonomics", description="Standing desks, chairs, monitor arms, and desk accessories")
cat_networking = CategoryModel(name="Networking & Cables", description="Routers, switches, Cat6 cables, and fiber patch cords")

for cat in [cat_electronics, cat_office, cat_networking]:
    if not session.query(CategoryModel).filter_by(name=cat.name).first():
        session.add(cat)
session.commit()

sup_nexus = SupplierModel(name="Nexus Global Supplies", email="contact@nexusglobal.com", phone="+1-555-0199", address="100 Tech Blvd, San Jose, CA")
sup_ergo = SupplierModel(name="ErgoDirect International", email="orders@ergodirect.com", phone="+1-555-0142", address="45 Comfort Way, Austin, TX")
sup_cyber = SupplierModel(name="CyberLink Hardware Co.", email="sales@cyberlink.net", phone="+1-555-0188", address="880 Matrix Ave, Seattle, WA")

for sup in [sup_nexus, sup_ergo, sup_cyber]:
    if not session.query(SupplierModel).filter_by(name=sup.name).first():
        session.add(sup)
session.commit()

cats = {c.name: c.id for c in session.query(CategoryModel).all()}
sups = {s.name: s.id for s in session.query(SupplierModel).all()}

products_data = [
    {
        "name": "Ultra-Wide 34\" IPS Curved Monitor",
        "sku": "MON-UW34-01",
        "description": "3440x1440 WQHD 144Hz curved HDR display with USB-C 90W PD",
        "price": 549.99,
        "cat": cats["Electronics & Hardware"],
        "sup": sups["Nexus Global Supplies"],
        "stock": 18,
        "reorder": 5
    },
    {
        "name": "Custom Wireless Mechanical Keyboard (RGB)",
        "sku": "KBD-MECH-W01",
        "description": "Hot-swappable mechanical switches, triple-mode Bluetooth/2.4G/Wired, aluminum frame",
        "price": 129.50,
        "cat": cats["Electronics & Hardware"],
        "sup": sups["Nexus Global Supplies"],
        "stock": 42,
        "reorder": 10
    },
    {
        "name": "Ergonomic Mesh High-Back Executive Chair",
        "sku": "CHR-ERGO-02",
        "description": "Adaptive lumbar support, 4D armrests, breathable Korean mesh, synchronous tilt mechanism",
        "price": 389.00,
        "cat": cats["Office & Ergonomics"],
        "sup": sups["ErgoDirect International"],
        "stock": 6,
        "reorder": 10
    },
    {
        "name": "Dual Motor Electric Standing Desk (60x30)",
        "sku": "DSK-STND-60",
        "description": "Heavy-duty steel dual motor frame with memory keypad and solid bamboo tabletop",
        "price": 499.00,
        "cat": cats["Office & Ergonomics"],
        "sup": sups["ErgoDirect International"],
        "stock": 15,
        "reorder": 5
    },
    {
        "name": "Cat6A Shielded Ethernet Cable 50ft (10Gbps)",
        "sku": "CBL-CAT6A-50",
        "description": "Pure bare copper conductors, 550MHz 10GBASE-T, snagless gold-plated RJ45 connectors",
        "price": 24.99,
        "cat": cats["Networking & Cables"],
        "sup": sups["CyberLink Hardware Co."],
        "stock": 4,
        "reorder": 15
    }
]

created_prods = []
for p in products_data:
    existing = session.query(ProductModel).filter_by(sku=p["sku"]).first()
    if not existing:
        prod = ProductModel(
            name=p["name"],
            sku=p["sku"],
            description=p["description"],
            price=p["price"],
            category_id=p["cat"],
            supplier_id=p["sup"],
            is_active=True
        )
        session.add(prod)
        session.commit()
        session.refresh(prod)
        created_prods.append((prod.id, p["stock"], p["reorder"]))
    else:
        created_prods.append((existing.id, p["stock"], p["reorder"]))

# Seed inventory via raw SQL to avoid model collision
for pid, stock, reorder in created_prods:
    existing_inv = session.execute(
        text("SELECT id FROM inventory WHERE product_id = :pid"), {"pid": pid}
    ).fetchone()
    if not existing_inv:
        session.execute(
            text("INSERT INTO inventory (product_id, quantity, reorder_level, created_at, updated_at) VALUES (:pid, :qty, :reorder, datetime('now'), datetime('now'))"),
            {"pid": pid, "qty": stock, "reorder": reorder}
        )
        session.execute(
            text("INSERT INTO stock_transactions (product_id, transaction_type, quantity, reference, notes, created_by, created_at) VALUES (:pid, 'STOCK_IN', :qty, 'SEED', 'Initial seed stock', 'system', datetime('now'))"),
            {"pid": pid, "qty": stock}
        )
session.commit()

# Seed order
order_count = session.execute(text("SELECT count(*) FROM orders")).scalar()
if order_count == 0 and created_prods:
    pid = created_prods[0][0]
    session.execute(
        text("INSERT INTO orders (user_id, status, notes, total_amount, created_at, updated_at) VALUES ('1', 'CONFIRMED', 'Demo Enterprise Order', 1099.98, datetime('now'), datetime('now'))")
    )
    session.commit()
    order_id = session.execute(text("SELECT last_insert_rowid()")).scalar()
    session.execute(
        text("INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (:oid, :pid, 2, 549.99, 1099.98)"),
        {"oid": order_id, "pid": pid}
    )
    session.commit()

print("All sample data seeded successfully!")
session.close()
