# Smart Furniture Store Management & E-Commerce Platform

An IoT-enabled inventory automation system featuring real-time RFID tracking using an ESP32 edge gateway, a FastAPI backend, dynamic SQLite database, WebSockets live synchronization, and interactive customer & admin web dashboards.

---

## 🏗️ System Architecture

* **Hardware / Edge Layer**: ESP32 Dev Module + MFRC522 RFID Transceiver (13.56 MHz). Operates as a Wi-Fi Access Point (`Furniture_Demo_Net`) and dispatches card UID HTTP requests.
* **Backend Layer**: FastAPI (Python 3.x) with WebSockets for real-time bidirectional communication and automated order fulfillment logic.
* **Database Layer**: SQLite (`furniture.db`) for lightweight local data storage (products, stock levels, order logs).
* **Frontend Layer**: Responsive HTML5 + Tailwind CSS web interfaces for both the Public Storefront (`index.html`) and the Admin Control Panel (`admin.html`).

---

## 📁 Project Structure

```text
furniture-ecommerce-platform/
├── backend/
│   └── app/
│       └── main.py              # FastAPI server, WebSockets & REST API routes
├── frontend/
│   ├── index.html               # Customer store with UPI/QR payment options
│   └── admin.html               # Admin dashboard (Listings, Orders, Multi-Tag RFID)
├── firmware/
│   └── src/
│       └── main.cpp             # ESP32 C++ firmware for MFRC522 RFID reader
├── furniture.db                 # Auto-generated SQLite database
└── README.md                    # Project documentation
