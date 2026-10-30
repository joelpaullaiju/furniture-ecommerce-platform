import os
import sqlite3
from typing import List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

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
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sku TEXT,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            rfid_uid TEXT,
            functional TEXT DEFAULT 'Seating',
            room TEXT DEFAULT 'Living Room',
            material TEXT DEFAULT 'Wooden',
            image_url TEXT DEFAULT 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400'
        )
    """)
    
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
    
    conn.commit()
    conn.close()

init_db()

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
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()
rfid_scan_states = {}

class ProductUpdate(BaseModel):
    name: str
    sku: Optional[str] = None
    price: float
    stock: int
    rfid_uid: Optional[str] = None
    functional: Optional[str] = None
    room: Optional[str] = None
    material: Optional[str] = None

class ProductCreate(BaseModel):
    name: str
    sku: Optional[str] = None
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

class UnbindPayload(BaseModel):
    product_id: str
    rfid_uid: str

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

@app.get("/api/products")
def get_products():
    rows = query_db("SELECT * FROM products ORDER BY id DESC")
    return [dict(row) for row in rows]

@app.post("/api/products")
async def create_product(payload: ProductCreate):
    rfid_input = payload.rfid_uid.strip().upper() if payload.rfid_uid else "Unassigned"
    sku_val = payload.sku.strip() if payload.sku else f"FURN-{payload.name[:3].upper()}-001"
    
    tag_list = [t.strip() for t in rfid_input.split(",") if t.strip() and t.strip() != "UNASSIGNED"]
    clean_rfid_str = ", ".join(tag_list) if tag_list else "Unassigned"

    new_id = query_db("""
        INSERT INTO products (name, sku, price, stock, rfid_uid, functional, room, material, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (payload.name, sku_val, payload.price, payload.stock, clean_rfid_str, payload.functional, payload.room, payload.material, payload.image_url), commit=True)
    
    for tag in tag_list:
        rfid_scan_states[tag] = "IN"

    await manager.broadcast({"event": "inventory_updated"})
    return {"id": new_id, **payload.dict()}

@app.put("/api/products/{product_id}")
async def update_product(product_id: int, updated: ProductUpdate):
    existing = query_db("SELECT * FROM products WHERE id = ?", (product_id,), one=True)
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")

    existing_tags = [t.strip().upper() for t in existing["rfid_uid"].split(",") if t.strip() and t.strip().upper() != "UNASSIGNED"]
    new_tags_input = [t.strip().upper() for t in (updated.rfid_uid or "").split(",") if t.strip() and t.strip().upper() != "UNASSIGNED"]

    for tag in new_tags_input:
        if tag not in existing_tags:
            existing_tags.append(tag)
            rfid_scan_states[tag] = "IN"

    combined_rfid = ", ".join(existing_tags) if existing_tags else "Unassigned"
    sku_val = updated.sku.strip() if updated.sku else existing["sku"]
    func_val = updated.functional if updated.functional else existing["functional"]
    room_val = updated.room if updated.room else existing["room"]
    mat_val = updated.material if updated.material else existing["material"]

    query_db("""
        UPDATE products 
        SET name = ?, sku = ?, price = ?, stock = ?, rfid_uid = ?, functional = ?, room = ?, material = ? 
        WHERE id = ?
    """, (updated.name, sku_val, updated.price, updated.stock, combined_rfid, func_val, room_val, mat_val, product_id), commit=True)
    
    await manager.broadcast({"event": "inventory_updated"})
    return {"status": "success"}

@app.delete("/api/products/{product_id}")
async def delete_product(product_id: int):
    query_db("DELETE FROM products WHERE id = ?", (product_id,), commit=True)
    await manager.broadcast({"event": "inventory_updated"})
    return {"status": "success"}

@app.post("/api/unbind-tag")
async def unbind_tag(payload: UnbindPayload):
    product = query_db("SELECT * FROM products WHERE id = ?", (payload.product_id,), one=True)
    if product and product["rfid_uid"]:
        target_tag = payload.rfid_uid.strip().upper()
        tags = [t.strip().upper() for t in product["rfid_uid"].split(",") if t.strip()]
        tags = [t for t in tags if t != target_tag]
        
        new_rfid_str = ", ".join(tags) if tags else "Unassigned"
        query_db("UPDATE products SET rfid_uid = ? WHERE id = ?", (new_rfid_str, payload.product_id), commit=True)
        
        if target_tag in rfid_scan_states:
            del rfid_scan_states[target_tag]

    await manager.broadcast({"event": "inventory_updated"})
    return {"status": "success"}

@app.get("/api/orders")
def get_orders():
    rows = query_db("SELECT * FROM orders ORDER BY rowid DESC")
    return [dict(row) for row in rows]

@app.post("/api/orders")
async def create_order(payload: OrderCreate):
    query_db("UPDATE products SET stock = MAX(0, stock - ?) WHERE id = ?", (payload.quantity, payload.productId), commit=True)

    order_count = query_db("SELECT COUNT(*) as count FROM orders", one=True)["count"]
    order_id = f"ORD-{101 + order_count}"
    
    query_db("""
        INSERT INTO orders (id, channel, customer, productId, productName, amount, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (order_id, payload.channel, payload.customer, payload.productId, payload.productName, payload.amount, "Pending Dispatch"), commit=True)

    await manager.broadcast({"event": "order_created"})
    return {"id": order_id, "status": "created"}

# Manual Order Dispatch Endpoint
@app.put("/api/orders/{order_id}/dispatch")
async def manual_dispatch_order(order_id: str):
    query_db("UPDATE orders SET status = 'Dispatched' WHERE id = ?", (order_id,), commit=True)
    await manager.broadcast({"event": "order_created"})
    return {"status": "success"}

@app.post("/api/scan")
async def handle_rfid_scan(payload: ScanPayload):
    scanned_uid = payload.rfid_uid.strip().upper()
    product = query_db("SELECT * FROM products WHERE UPPER(rfid_uid) LIKE ?", (f"%{scanned_uid}%",), one=True)

    if not product:
        await manager.broadcast({
            "event": "unassigned_scan",
            "rfid_uid": scanned_uid
        })
        return {"status": "unmatched", "scanned_uid": scanned_uid}

    last_state = rfid_scan_states.get(scanned_uid, "IN")

    if last_state == "IN":
        new_stock = max(0, product["stock"] - 1)
        action = "CHECK_OUT"
        status_msg = "Item dispatched from warehouse"
        rfid_scan_states[scanned_uid] = "OUT"

        pending_order = query_db(
            "SELECT * FROM orders WHERE productId = ? AND status = 'Pending Dispatch' ORDER BY rowid ASC", 
            (str(product["id"]),), 
            one=True
        )
        if pending_order:
            query_db("UPDATE orders SET status = 'Dispatched' WHERE id = ?", (pending_order["id"],), commit=True)
            status_msg = f"Item dispatched & Order {pending_order['id']} marked as Dispatched!"

    else:
        new_stock = product["stock"] + 1
        action = "CHECK_IN"
        status_msg = "Item checked into warehouse"
        rfid_scan_states[scanned_uid] = "IN"

    query_db("UPDATE products SET stock = ? WHERE id = ?", (new_stock, product["id"]), commit=True)

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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "frontend"))

if not os.path.exists(frontend_dir):
    frontend_dir = BASE_DIR

app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")