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


Hardware Components & Wiring Diagram

1. Required Hardware

Component| Quantity| Description
ESP32 Dev Board| 1| 30-pin or 38-pin development board
MFRC522 RFID Reader| 1| 13.56 MHz RFID reader module
RFID Tags / Cards| As required| For identifying individual furniture items
Green LED| 1| Successful scan indicator
Red LED| 1| Error or unsuccessful scan indicator
220Ω Resistors| 2| LED current limiting
Jumper Wires| As required| Hardware connections
Breadboard| 1| Circuit prototyping

2. RFID Reader Pin Connections

The MFRC522 communicates with the ESP32 using the SPI (Serial Peripheral Interface) protocol.

MFRC522 Pin| ESP32 GPIO| Description
SDA (SS)| GPIO 5| SPI Slave Select
SCK| GPIO 18| SPI Clock
MOSI| GPIO 23| Master Out Slave In
MISO| GPIO 19| Master In Slave Out
RST| GPIO 22| Module Reset
GND| GND| Ground
3.3V| 3.3V| Power Supply

Important: The MFRC522 operates at 3.3V. Do NOT connect its power pin to 5V, as this may damage the module.

LED Indicator Connections

LED| ESP32 GPIO| Connection
Green LED| GPIO 2| Anode (+) through 220Ω resistor
Red LED| GPIO 4| Anode (+) through 220Ω resistor

Connect the cathode (-) of both LEDs to GND.

---

⚙️ Quick Start Setup Guide

Follow these instructions to install and run the Smart Furniture Store Management & E-Commerce Platform on a Windows, macOS, or Linux computer.

Step 1: Prerequisites

Make sure the following software is installed:

- Python 3.8 or higher
- Visual Studio Code or any code editor
- Google Chrome or another modern web browser
- Arduino IDE or VS Code with PlatformIO
- Git (optional, for cloning the repository)

Step 2: Clone the Repository

Open Terminal, Command Prompt, or PowerShell and execute:

git clone https://github.com/YOUR_USERNAME/furniture-ecommerce-platform.git

Navigate into the project directory:

cd furniture-ecommerce-platform

Alternatively, download the repository as a ZIP file and extract it.

Step 3: Install Python Dependencies

Install the required Python packages:

pip install fastapi uvicorn websockets pydantic

Step 4: Launch the Backend Server

From the root project directory, execute:

python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

Once the server starts successfully, the FastAPI backend will be available on port "8000".

Keep this terminal window running while using the application.

Step 5: Open the Web Dashboards

Open Google Chrome or any modern web browser.

Admin Control Panel:

http://localhost:8000/admin.html

Customer Storefront:

http://localhost:8000/index.html

To access the dashboards from another device on the same network, replace "localhost" with the computer's local IP address.

For example:

http://192.168.1.100:8000/admin.html
http://192.168.1.100:8000/index.html

Make sure the computer's firewall allows connections to port "8000".

Step 6: Flash the ESP32 Firmware

1. Connect the ESP32 development board to your computer using a USB cable.

2. Open the following firmware file:
   
   "firmware/src/main.cpp"

3. Open the project using Arduino IDE or VS Code with PlatformIO.

4. Select the board:
   
   "ESP32 Dev Module"

5. Select the appropriate COM port.

6. Compile and upload the firmware.

7. Connect the MFRC522 RFID reader and LED indicators according to the wiring diagram above.

ESP32 Wi-Fi Configuration

The ESP32 is configured with the following Wi-Fi access point credentials:

Setting| Value
Wi-Fi SSID| "Furniture_Demo_Net"
Password| "password123"
Default ESP32 Access Point IP| "192.168.4.1"

Note: The FastAPI backend runs on your computer, not on the ESP32. To access the web dashboards from a phone, connect the phone to a network that can reach the computer and use the computer's IP address with port "8000". The ESP32 access point IP is not the FastAPI server address.

---

📖 Comprehensive Demonstration & User Guide

Follow these steps to demonstrate the complete functionality of the platform.

1. Adding New Furniture Listings with Multi-Tag RFID Mapping

1. Open the Admin Control Panel:
   
   "http://localhost:8000/admin.html"

2. Click the + Add New Product button.

3. Enter the furniture product information:
   
   - Product Name
   - Price
   - Category
   - Room
   - Material

4. Scan physical RFID tags sequentially using the MFRC522 reader.

Multi-Tag RFID Mapping

Each scanned RFID tag is associated with the furniture product.

Scan| Operation| Product Quantity
First Scan| Captures RFID Tag 1 (UID 1)| 1
Second Scan| Adds RFID Tag 2 (UID 2)| 2
Third Scan| Adds RFID Tag 3 (UID 3)| 3

5. Click Save Product.

The product is now stored in the inventory with its associated RFID tag UIDs and automatically updated stock quantity.

2. Customer Online Ordering & UPI Payment Demo

1. Open the Customer Storefront:
   
   "http://localhost:8000/index.html"

2. Browse the available furniture products.

3. Click Buy Now on the desired product.

4. Select a payment option:
   
   - Google Pay
   - PhonePe
   - Paytm
   - UPI QR Code

5. For the demonstration, enter a test UPI ID (for example, "user@upi") where applicable.

6. The UPI QR code option generates a QR code pre-filled with the item price.

7. Enter the customer's name.

8. Click Confirm Purchase.

Expected Result

- The order is recorded in the backend.
- The Admin Control Panel receives the new order.
- The order appears in the Orders tab.
- The order status is displayed as Pending Dispatch.
- Updates are synchronized through WebSockets without requiring a page refresh.

Note: The UPI interface demonstrates the payment flow. Actual payment processing and verification require a payment gateway integration.

3. Automated RFID Warehouse Dispatch & Order Fulfillment

This feature demonstrates the integration of RFID-based inventory management with automated order fulfillment.

Procedure

1. Open the Admin Control Panel.
2. Navigate to the Orders tab.
3. Identify an order with the status Pending Dispatch.
4. Locate the physical RFID tag associated with the ordered furniture product.
5. Scan the RFID tag using the MFRC522 reader.

Expected System Behaviour

When a mapped RFID tag is scanned, the system performs the following operations:

1. Stock Deduction

The corresponding product's inventory quantity decreases by one.

2. Live Alert Notification

A notification banner or toast appears on the dashboard indicating that the item has been checked out.

3. Automated Order Fulfillment

The oldest eligible Pending Dispatch order is automatically updated to:

"Dispatched"

4. Storefront Synchronization

The customer storefront immediately reflects the updated inventory quantity through real-time WebSocket communication.

This demonstrates how RFID technology can automate warehouse dispatch operations while maintaining synchronized inventory records.

4. Manual Order Dispatching

The platform also supports manual dispatch operations through the Admin Control Panel.

Procedure

1. Navigate to the Admin Control Panel.
2. Open the Orders tab.
3. Locate an order with the status Pending Dispatch.
4. Click the green Dispatch button next to the order.

Expected Result

- The order status changes to Dispatched.
- The update is reflected immediately on the dashboard.
- The order information is synchronized with the backend.

---

🎯 Project Features

- RFID-based furniture identification and tracking.
- Multi-tag RFID mapping for individual products.
- ESP32-based hardware integration.
- Real-time inventory management.
- FastAPI backend architecture.
- SQLite database for local data storage.
- WebSocket-based real-time communication.
- Interactive customer storefront.
- Administrative inventory and order management.
- Automated RFID-based warehouse dispatch.
- Manual order fulfillment.
- UPI payment interface demonstration.

🛠️ Technology Stack

Layer| Technology
Hardware| ESP32 Dev Board
RFID| MFRC522 (13.56 MHz)
Firmware| C++ / Arduino Framework
Backend| Python 3, FastAPI
Real-Time Communication| WebSockets
Database| SQLite
Frontend| HTML5, Tailwind CSS, JavaScript
Development Tools| VS Code / Arduino IDE
Version Control| Git & GitHub

---

📌 Troubleshooting

Problem| Suggested Solution
ESP32 not detected| Check USB cable, drivers, and COM port
RFID reader not responding| Verify SPI wiring and 3.3V power supply
Backend server not starting| Verify Python installation and dependencies
Dashboard not loading| Ensure the FastAPI server is running on port 8000
RFID tags not detected| Check tag compatibility (13.56 MHz)
Real-time updates not working| Verify WebSocket connections and backend status
Cannot access dashboard from phone| Check network connectivity, computer IP, and firewall settings

---

👨‍💻 Contributors

This project was developed collaboratively by a team of students as an engineering capstone project.

For contributions, bug reports, or suggestions, feel free to open an issue or submit a pull request.

📄 License

This project is licensed under the MIT License. See the "LICENSE" file for more information.├── furniture.db                 # Auto-generated SQLite database
└── README.md                    # Project documentation
