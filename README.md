# 🪑 Smart Furniture Store Management & E-Commerce Platform

An IoT-enabled furniture inventory management and e-commerce platform featuring real-time RFID tracking using an ESP32 edge gateway, a FastAPI backend, SQLite database, WebSocket communication, and interactive customer and admin dashboards.

---

## 📌 System Architecture

The system consists of four main layers:

### 1. Hardware / Edge Layer
- ESP32 Development Board.
- MFRC522 RFID Transceiver (13.56 MHz).
- RFID cards and tags for furniture identification.
- Green and Red LED indicators.
- ESP32 Wi-Fi Access Point.

### 2. Backend Layer
- Python 3 and FastAPI.
- WebSockets for real-time bidirectional communication.
- Automated inventory and order fulfillment logic.
- HTTP communication with the ESP32.

### 3. Database Layer
- SQLite database (furniture.db).
- Product information and inventory records.
- RFID tag UID mappings.
- Customer orders and dispatch status.

### 4. Frontend Layer
- HTML5.
- Tailwind CSS.
- JavaScript.
- Customer Storefront (index.html).
- Admin Control Panel (admin.html).

---

# 📁 Project Structure

text
furniture-ecommerce-platform/
│
├── backend/
│   └── app/
│       └── main.py
│
├── firmware/
│   └── src/
│       └── main.cpp
│
├── index.html
├── admin.html
├── furniture.db
├── README.md
└── LICENSE


Note: This is a simplified overview. Refer to the repository for the complete project structure.

---

# 🚀 Hardware Components & Wiring Diagram

## 1. Required Hardware

| Component | Quantity | Description |
|---|---:|---|
| ESP32 Dev Board | 1 | 30-pin or 38-pin development board |
| MFRC522 RFID Reader | 1 | 13.56 MHz RFID module |
| RFID Tags / Cards | As required | Furniture identification |
| Green LED | 1 | Successful scan indicator |
| Red LED | 1 | Error indicator |
| 220Ω Resistors | 2 | LED current limiting |
| Jumper Wires | As required | Hardware connections |
| Breadboard | 1 | Circuit prototyping |

## 2. RFID Reader Pin Connections

The MFRC522 communicates with the ESP32 using the SPI (Serial Peripheral Interface) protocol.

| MFRC522 Pin | ESP32 GPIO | Description |
|---|---|---|
| SDA (SS) | GPIO 5 | SPI Slave Select |
| SCK | GPIO 18 | SPI Clock |
| MOSI | GPIO 23 | Master Out Slave In |
| MISO | GPIO 19 | Master In Slave Out |
| RST | GPIO 22 | Module Reset |
| GND | GND | Ground |
| 3.3V | 3.3V | Power Supply |

> ⚠️ *Important:* The MFRC522 operates at 3.3V. Never connect its power pin to 5V, as this may damage the module.

## 3. LED Indicator Connections

| LED | ESP32 GPIO | Connection |
|---|---|---|
| Green LED | GPIO 2 | Anode (+) through 220Ω resistor |
| Red LED | GPIO 4 | Anode (+) through 220Ω resistor |

Connect the cathode (-) of both LEDs to GND.

---

# ⚙️ Quick Start Setup Guide

Follow these instructions to install and run the platform on Windows, macOS, or Linux.

## Step 1: Prerequisites

Install the following software:

- Python 3.8 or higher.
- Visual Studio Code or another code editor.
- Google Chrome or another modern web browser.
- Arduino IDE or VS Code with PlatformIO.
- Git (optional).

## Step 2: Clone the Repository

Open Terminal, Command Prompt, or PowerShell.

bash
git clone https://github.com/joelpaullaju/furniture-ecommerce-platform.git


Navigate into the project directory:

bash
cd furniture-ecommerce-platform


Alternatively, download the repository as a ZIP file and extract it.

## Step 3: Install Python Dependencies

Install the required Python packages:

bash
pip install fastapi uvicorn websockets pydantic


## Step 4: Launch the Backend Server

From the root project directory, execute:

bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload


Once the server starts successfully, the FastAPI backend will be available on port 8000.

Keep the terminal running while using the application.

## Step 5: Open the Web Dashboards

Open your browser and visit the following addresses.

*Admin Control Panel:*

type in any browser -
http://localhost:8000/admin.html


*Customer Storefront:*

type in any browser -
http://localhost:8000/index.html


### Accessing the Platform from Other Devices

To access the dashboards from another computer or phone on the same network, replace localhost with the computer's local IP address.

Example:

text
http://192.168.1.100:8000/admin.html
http://192.168.1.100:8000/index.html


Ensure that the firewall allows connections through port 8000.

## Step 6: Upload ESP32 Firmware

1. Connect the ESP32 development board to your computer using a USB cable.
2. Open the firmware project:

   firmware/src/main.cpp

3. Open the project using Arduino IDE or VS Code with PlatformIO.
4. Select the board:

   ESP32 Dev Module

5. Select the appropriate COM port.
6. Compile and upload the firmware.
7. Connect the MFRC522 reader and LED indicators according to the wiring diagram.

### ESP32 Wi-Fi Configuration

The ESP32 is configured with the following Wi-Fi Access Point credentials:

| Setting | Value |
|---|---|
| Wi-Fi SSID | Furniture_Demo_Net |
| Password | password123 |
| ESP32 Access Point IP | 192.168.4.1 |

> *Note:* The FastAPI backend runs on the computer, not on the ESP32. The ESP32 access point address (192.168.4.1) is not the backend server address. Devices accessing the dashboards must be able to reach the computer running FastAPI.

---

# 📖 Comprehensive Demonstration & User Guide

The following steps demonstrate the complete functionality of the platform.

## 1. Adding New Furniture Listings with Multi-Tag RFID Mapping

1. Open the Admin Control Panel:

   http://localhost:8000/admin.html

2. Click the *+ Add New Product* button.
3. Enter the furniture product information:
   - Product Name
   - Price
   - Category
   - Room
   - Material

4. Scan physical RFID tags sequentially using the MFRC522 reader.

### Multi-Tag RFID Mapping

Each RFID tag is associated with the corresponding furniture product.

| Scan | Operation | Product Quantity |
|---|---|---:|
| First Scan | Captures Tag 1 (UID 1) | 1 |
| Second Scan | Adds Tag 2 (UID 2) | 2 |
| Third Scan | Adds Tag 3 (UID 3) | 3 |

5. Click *Save Product*.

The product is stored in the inventory with its associated RFID tag UIDs and updated stock quantity.

## 2. Customer Online Ordering & UPI Payment Demo

1. Open the Customer Storefront:

   http://localhost:8000/index.html

2. Browse the available furniture products.
3. Click *Buy Now* on the desired product.
4. Select a payment option:
   - Google Pay
   - PhonePe
   - Paytm
   - UPI QR Code

5. For the demonstration, enter a test UPI ID (for example, user@upi) where applicable.
6. The UPI QR Code option generates a QR code pre-filled with the item price.
7. Enter the customer's name.
8. Click *Confirm Purchase*.

### Expected Result

- The order is recorded in the backend.
- The Admin Control Panel receives the new order.
- The order appears in the Orders tab.
- The order status is displayed as *Pending Dispatch*.
- WebSocket communication synchronizes updates without requiring a page refresh.

> *Note:* The UPI interface demonstrates the payment flow. Actual payment processing and transaction verification require integration with a payment gateway.

## 3. Automated RFID Warehouse Dispatch & Order Fulfillment

This feature integrates RFID-based inventory management with automated order fulfillment.

### Procedure

1. Open the Admin Control Panel.
2. Navigate to the Orders tab.
3. Identify an order marked *Pending Dispatch*.
4. Locate the RFID tag associated with the ordered furniture product.
5. Scan the RFID tag using the MFRC522 reader.

### Expected System Behaviour

When a mapped RFID tag is scanned, the system performs the following operations:

*1. Stock Deduction*

The corresponding product's inventory quantity decreases by one.

*2. Live Alert Notification*

A notification banner or toast appears on the dashboard indicating that the item has been checked out.

*3. Automated Order Fulfillment*

The oldest eligible Pending Dispatch order is automatically updated to:

Dispatched

*4. Storefront Synchronization*

The customer storefront immediately reflects the updated inventory quantity through real-time WebSocket communication.

This demonstrates how RFID technology can automate warehouse dispatch operations while maintaining synchronized inventory records.

## 4. Manual Order Dispatching

The platform also supports manual dispatch operations through the Admin Control Panel.

### Procedure

1. Navigate to the Admin Control Panel.
2. Open the *Orders* tab.
3. Locate an order marked *Pending Dispatch*.
4. Click the green *Dispatch* button next to the order.

### Expected Result

- The order status changes to *Dispatched*.
- The updated status is reflected on the dashboard.
- Order information is synchronized with the backend.

---

# ✨ Key Project Features

- RFID-based furniture identification and tracking.
- Multi-tag RFID mapping for individual products.
- ESP32-based hardware integration.
- Real-time inventory management.
- FastAPI backend architecture.
- SQLite database for local data storage.
- WebSocket-based real-time communication.
- Interactive customer storefront.
- Administrative inventory management.
- Automated RFID-based warehouse dispatch.
- Manual order fulfillment.
- UPI payment interface demonstration.

---

# 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Hardware | ESP32 Dev Board |
| RFID | MFRC522 (13.56 MHz) |
| Firmware | C++ / Arduino Framework |
| Backend | Python 3, FastAPI |
| Real-Time Communication | WebSockets |
| Database | SQLite |
| Frontend | HTML5, Tailwind CSS, JavaScript |
| Development Tools | VS Code / Arduino IDE |
| Version Control | Git & GitHub |

---

# 🔧 Troubleshooting

| Problem | Suggested Solution |
|---|---|
| ESP32 not detected | Check USB cable, drivers, and COM port. |
| RFID reader not responding | Verify SPI wiring and 3.3V power supply. |
| Backend server not starting | Check Python installation and dependencies. |
| Dashboard not loading | Ensure FastAPI is running on port 8000. |
| RFID tags not detected | Check 13.56 MHz tag compatibility. |
| Real-time updates not working | Verify WebSocket connections and backend status. |
| Cannot access dashboard from phone | Check network connectivity, computer IP, and firewall settings. |

---

# 👨‍💻 Contributors

This project was collaboratively developed by a team of students as an engineering capstone project.

We welcome suggestions, improvements, and contributions.

For bug reports or feature requests, please open an issue in this repository.

---

# 📄 License

This project is licensed under the MIT License.

See the [LICENSE](LICENSE) file for more information.
