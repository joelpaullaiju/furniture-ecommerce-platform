import sqlite3
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Furniture E-Commerce Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "furniture.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            rfid_uid TEXT,
            functional TEXT DEFAULT 'Seating',
            room TEXT DEFAULT 'Living Room',
            material TEXT DEFAULT 'Wooden',
            image_url TEXT DEFAULT 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400'
        )
    """)
    
    # Orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            channel TEXT NOT NULL,
            customer TEXT NOT NULL,
            productId TEXT NOT NULL,
            productName TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT DEFAULT 'Pending Dispatch'
        )
    """)
    
    # Seed default products if database is empty
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO products (name, price, stock, rfid_uid, functional, room, material, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            ("Modern Oak Dining Table", 28500.0, 12, "A38F1209", "Tables", "Dining Room", "Wooden", "https://images.unsplash.com/photo-1530018607912-eff2daa1bac4?w=400"),
            ("Ergonomic Office Chair", 14200.0, 25, "B49G2310", "Seating", "Home Office", "Upholstered", "https://images.unsplash.com/photo-1580481072645-022f9a6d1270?w=400"),
            ("Minimalist Velvet Sofa", 41800.0, 5, "C50H3411", "Seating", "Living Room", "Upholstered", "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400")
        ])
    
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

# Connection Manager for WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

# Track RFID state in memory: { "RFID_UID": "IN" / "OUT" }
rfid_scan_states = {}

# Data Models
class ProductUpdate(BaseModel):
    name: str
    price: float
    stock: int
    rfid_uid: Optional[str] = None

class ProductCreate(BaseModel):
    name: str
    price: float
    stock: int
    rfid_uid: Optional[str] = None
    functional: Optional[str] = "Seating"
    room: Optional[str] = "Living Room"
    material: Optional[str] = "Wooden"
    image_url: Optional[str] = "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400"

class OrderCreate(BaseModel):
    channel: str
    customer: str
    productId: str
    productName: str
    amount: float
    quantity: int = 1

class ScanPayload(BaseModel):
    rfid_uid: str

# Helper Function for Executing Queries
def query_db(query: str, args=(), one=False, commit=False):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, args)
    if commit:
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id
    rv = cursor.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

# --- REST ENDPOINTS ---

@app.get("/api/products")
def get_products():
    rows = query_db("SELECT * FROM products ORDER BY id DESC")
    return [dict(row) for row in rows]

@app.post("/api/products")
async def create_product(payload: ProductCreate):
    rfid = payload.rfid_uid.strip().upper() if payload.rfid_uid else "Unassigned"
    new_id = query_db("""
        INSERT INTO products (name, price, stock, rfid_uid, functional, room, material, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (payload.name, payload.price, payload.stock, rfid, payload.functional, payload.room, payload.material, payload.image_url), commit=True)
    
    await manager.broadcast({"event": "inventory_updated"})
    return {"id": new_id, **payload.dict()}

@app.put("/api/products/{product_id}")
async def update_product(product_id: int, updated: ProductUpdate):
    rfid = updated.rfid_uid.strip().upper() if updated.rfid_uid else "Unassigned"
    query_db("""
        UPDATE products SET name = ?, price = ?, stock = ?, rfid_uid = ? WHERE id = ?
    """, (updated.name, updated.price, updated.stock, rfid, product_id), commit=True)
    
    await manager.broadcast({"event": "inventory_updated"})
    return {"status": "success"}

@app.delete("/api/products/{product_id}")
async def delete_product(product_id: int):
    query_db("DELETE FROM products WHERE id = ?", (product_id,), commit=True)
    await manager.broadcast({"event": "inventory_updated"})
    return {"status": "success"}

@app.get("/api/orders")
def get_orders():
    rows = query_db("SELECT * FROM orders ORDER BY rowid DESC")
    return [dict(row) for row in rows]

@app.post("/api/orders")
async def create_order(payload: OrderCreate):
    # Deduct stock from SQLite
    query_db("UPDATE products SET stock = MAX(0, stock - ?) WHERE id = ?", (payload.quantity, payload.productId), commit=True)

    # Insert order record
    order_count = query_db("SELECT COUNT(*) as count FROM orders", one=True)["count"]
    order_id = f"ORD-{101 + order_count}"
    
    query_db("""
        INSERT INTO orders (id, channel, customer, productId, productName, amount, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (order_id, payload.channel, payload.customer, payload.productId, payload.productName, payload.amount, "Pending Dispatch"), commit=True)

    await manager.broadcast({"event": "order_created"})
    return {"id": order_id, "status": "created"}

# --- ESP32 RFID SCAN ENDPOINT (TOGGLE CHECK-IN / CHECK-OUT) ---
@app.post("/api/scan")
async def handle_rfid_scan(payload: ScanPayload):
    scanned_uid = payload.rfid_uid.strip().upper()
    product = query_db("SELECT * FROM products WHERE UPPER(rfid_uid) = ?", (scanned_uid,), one=True)

    if not product:
        return {"status": "unmatched", "scanned_uid": scanned_uid}

    # Determine action: First scan -> Check-In (+1), Second scan -> Check-Out (-1)
    last_state = rfid_scan_states.get(scanned_uid, "OUT")

    if last_state == "OUT":
        # First scan: Item entering warehouse (Check-In)
        new_stock = product["stock"] + 1
        action = "CHECK_IN"
        status_msg = "Item checked into warehouse"
        rfid_scan_states[scanned_uid] = "IN"
    else:
        # Second scan: Item leaving warehouse (Check-Out)
        new_stock = max(0, product["stock"] - 1)
        action = "CHECK_OUT"
        status_msg = "Item dispatched from warehouse"
        rfid_scan_states[scanned_uid] = "OUT"

    # Update database stock
    query_db("UPDATE products SET stock = ? WHERE id = ?", (new_stock, product["id"]), commit=True)

    # Broadcast update to all connected frontend screens
    await manager.broadcast({
        "event": "live_scan",
        "action": action,
        "scanned_uid": scanned_uid,
        "matched_product": product["name"],
        "new_stock": new_stock,
        "message": status_msg
    })

    return {
        "status": "matched",
        "action": action,
        "scanned_uid": scanned_uid,
        "product_name": product["name"],
        "new_stock": new_stock,
        "message": status_msg
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)