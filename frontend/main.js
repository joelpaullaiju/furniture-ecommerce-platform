// Automatically detect the server IP (handles 192.168.4.4, 192.168.4.2, or localhost)
const HOST = window.location.host; 
const API_URL = `${window.location.protocol}//${HOST}`;
const WS_URL = `ws://${HOST}/ws`;

let socket = null;

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
    fetchProducts();
    connectWebSocket();
});

// Fetch all available products from FastAPI backend
async function fetchProducts() {
    try {
        const response = await fetch(`${API_URL}/api/products`);
        if (!response.ok) throw new Error("Failed to fetch products");
        const products = await response.json();
        renderProducts(products);
    } catch (error) {
        console.error("Error fetching products:", error);
    }
}

// Render product cards in the DOM
function renderProducts(products) {
    const grid = document.getElementById("product-grid");
    const countBadge = document.getElementById("product-count");
    
    if (!grid) return;
    grid.innerHTML = "";

    if (countBadge) {
        countBadge.textContent = `${products.length} Items`;
    }

    if (products.length === 0) {
        grid.innerHTML = `<p class="col-span-full text-center text-gray-500 py-8">No products available in catalog.</p>`;
        return;
    }

    products.forEach(product => {
        const card = document.createElement("div");
        card.className = "bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition";
        
        // Use local image path or fallback placeholder
        const imageSrc = product.image_url ? product.image_url : "chair.jpg";

        card.innerHTML = `
            <div class="relative h-48 bg-gray-100 flex items-center justify-center overflow-hidden">
                <img src="${imageSrc}" alt="${product.name}" class="w-full h-full object-cover" onerror="this.src='https://via.placeholder.com/300x200?text=No+Image'">
                <span class="absolute top-3 right-3 bg-slate-900/80 text-white text-xs font-bold px-2.5 py-1 rounded-full backdrop-blur-sm">
                    ${product.stock} In Stock
                </span>
            </div>
            <div class="p-4">
                <span class="text-xs font-medium text-blue-600 uppercase tracking-wider">${product.category || 'Furniture'}</span>
                <h3 class="font-bold text-gray-900 text-lg mt-1">${product.name}</h3>
                <div class="mt-4 flex items-center justify-between">
                    <span class="text-xl font-extrabold text-gray-900">₹ ${product.price}</span>
                    <button onclick="buyProduct(${product.id})" class="bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-4 py-2 rounded-lg transition shadow-sm">
                        Buy Now
                    </button>
                </div>
            </div>
        `;
        grid.appendChild(card);
    });
}

// Connect to ESP32 / FastAPI WebSocket for live RFID inventory sync
function connectWebSocket() {
    socket = new WebSocket(WS_URL);

    socket.onopen = () => {
        console.log("Connected to Live Inventory WebSocket Sync");
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("WebSocket event received:", data);
        // Refresh products list on stock/RFID update
        fetchProducts();
    };

    socket.onclose = () => {
        console.log("WebSocket connection closed. Reconnecting in 3s...");
        setTimeout(connectWebSocket, 3000);
    };

    socket.onerror = (err) => {
        console.error("WebSocket error:", err);
    };
}

function buyProduct(productId) {
    alert(`Order placed for Product ID: ${productId}`);
}