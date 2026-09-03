from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Smart Furniture Inventory System API",
    description="Edge-to-cloud ingestion engine for RFID gates and storefront sync",
    version="1.0.0",
)

# Enable CORS for local web dashboards
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "online", "system": "Smart Furniture Ingestion Engine"}

@app.post("/api/v1/scan", tags=["Edge Ingestion"])
def process_rfid_scan(payload: dict):
    return {
        "status": "received",
        "data": payload
    }
