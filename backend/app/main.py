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

# In-Memory Inventory Database
inventory_db = [
    {
        "id": 1,
        "name": "Modern Oak Dining Table",
        "price": 28500.0,
        "stock": 12,
        "rfid_uid": "A38F1209",
        "functional": "Tables",
        "room": "Dining Room",
        "material": "Wooden",
        "image_url": "https://images.unsplash.com/photo-1530018607912-eff2daa1bac4?w=400"
    },
    {
        "id": 2,
        "name": "Ergonomic Office Chair",
        "price": 14200.0,
        "stock": 25,
        "rfid_uid": "B49G2310",
        "functional": "Seating",
        "room": "Home Office",
        "material": "Upholstered",
        "image_url": "https://images.unsplash.com/photo-1580481072645-022f9a6d1270?w=400"
    },
    {
        "id": 3,
        "name": "Minimalist Velvet Sofa",
        "price": 41800.0,
        "stock": 5,
        "rfid_uid": "C50H3411",
        "functional": "Seating",
        "room": "Living Room",
        "material": "Upholstered",
        "image_url": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400"
    }
]

# In-Memory Orders Database
orders_db = [
    {
        "id": "ORD-104",
        "channel": "Online Store",
        "customer": "Rahul Sharma",
        "productId": "2",
        "productName": "Ergonomic Office Chair",
        "amount": 14200.0,
        "status": "Pending Dispatch"
    },
    {
        "id": "ORD-103",
        "channel": "In-Store (Offline)",
        "customer": "Walk-in Customer",
        "productId": "1",
        "productName": "Modern Oak Dining Table",
        "amount": 28500.0,
        "status": "Dispatched"
    }
]

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

# --- REST ENDPOINTS ---

@app.get("/api/products")
def get_products():
    return inventory_db

@app.post("/api/products")
async def create_product(payload: ProductCreate):
    new_id = len(inventory_db) + 1
    new_item = {
        "id": new_id,
        "name": payload.name,
        "price": payload.price,
        "stock": payload.stock,
        "rfid_uid": payload.rfid_uid.strip().upper() if payload.rfid_uid else "Unassigned",
        "functional": payload.functional or "Seating",
        "room": payload.room or "Living Room",
        "material": payload.material or "Wooden",
        "image_url": payload.image_url or "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400"
    }
    inventory_db.insert(0, new_item)
    await manager.broadcast({"event": "inventory_updated", "data": inventory_db})
    return new_item

@app.put("/api/products/{product_id}")
async def update_product(product_id: int, updated: ProductUpdate):
    for item in inventory_db:
        if item["id"] == product_id:
            item["name"] = updated.name
            item["price"] = updated.price
            item["stock"] = updated.stock
            if updated.rfid_uid:
                item["rfid_uid"] = updated.rfid_uid.strip().upper()
            await manager.broadcast({"event": "inventory_updated", "data": inventory_db})
            return item
    raise HTTPException(status_code=404, detail="Product not found")

@app.delete("/api/products/{product_id}")
async def delete_product(product_id: int):
    global inventory_db
    inventory_db = [item for item in inventory_db if str(item["id"]) != str(product_id)]
    await manager.broadcast({"event": "inventory_updated", "data": inventory_db})
    return {"status": "success"}

@app.get("/api/orders")
def get_orders():
    return orders_db

@app.post("/api/orders")
async def create_order(payload: OrderCreate):
    # 1. Reduce stock for the purchased product
    for item in inventory_db:
        if str(item["id"]) == str(payload.productId):
            item["stock"] = max(0, item["stock"] - payload.quantity)
            break

    # 2. Store Order
    new_order = {
        "id": f"ORD-{100 + len(orders_db) + 1}",
        "channel": payload.channel,
        "customer": payload.customer,
        "productId": payload.productId,
        "productName": payload.productName,
        "amount": payload.amount,
        "status": "Pending Dispatch"
    }
    orders_db.insert(0, new_order)
    
    # 3. Broadcast real-time WebSocket update for inventory and orders
    await manager.broadcast({"event": "order_created", "orders": orders_db, "data": inventory_db})
    return new_order

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)