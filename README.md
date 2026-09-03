# Smart Furniture Store Management & E-Commerce Platform

An edge-to-cloud IoT inventory automation system integrating ESP32 RFID gate nodes, a FastAPI backend, and real-time cloud data synchronization.

## Architecture
- **Edge Layer:** ESP32 + RC522 (13.56 MHz RFID transceiver)
- **Backend:** FastAPI (Python 3.x)
- **Database:** Firebase Realtime Database
- **Storefront & Admin:** Web UI for live stock visibility

## Project Structure
- `firmware/`: Embedded C++ code for the ESP32 reader nodes
- `backend/`: REST API routes, models, and cloud synchronization logic
- `web/`: Admin management dashboard and e-commerce customer portal
- `docs/`: Technical specifications, architecture schematics, and reports
