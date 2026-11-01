const HOST = window.location.host; 
const API_URL = `${window.location.protocol}//${HOST}`;
const WS_URL = `ws://${HOST}/ws`;

let socket = null;
let currentProduct = null;

document.addEventListener("DOMContentLoaded", () => {
    fetchProducts();
    connectWebSocket();
    injectCheckoutModal();
});

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

function renderProducts(products) {
    const grid = document.getElementById("product-grid");
    const countBadge = document.getElementById("product-count");
    
    if (!grid) return;
    grid.innerHTML = "";

    if (countBadge) countBadge.textContent = `${products.length} Items`;

    if (products.length === 0) {
        grid.innerHTML = `<p class="col-span-full text-center text-gray-500 py-8">No products available in catalog.</p>`;
        return;
    }

    products.forEach(product => {
        const card = document.createElement("div");
        card.className = "bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition";
        
        const imageSrc = product.image_url ? product.image_url : "chair.jpg";

        card.innerHTML = `
            <div class="relative h-48 bg-gray-100 flex items-center justify-center overflow-hidden">
                <img src="${imageSrc}" alt="${product.name}" class="w-full h-full object-cover" onerror="this.src='chair.jpg'">
                <span class="absolute top-3 right-3 bg-slate-900/80 text-white text-xs font-bold px-2.5 py-1 rounded-full backdrop-blur-sm">
                    ${product.stock} In Stock
                </span>
            </div>
            <div class="p-4">
                <span class="text-xs font-medium text-blue-600 uppercase tracking-wider">${product.category || 'Furniture'}</span>
                <h3 class="font-bold text-gray-900 text-lg mt-1">${product.name}</h3>
                <div class="mt-4 flex items-center justify-between">
                    <span class="text-xl font-extrabold text-gray-900">₹ ${product.price}</span>
                    <button onclick="openCheckout(${product.id}, '${product.name}', ${product.price}, ${product.stock})" class="bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-4 py-2 rounded-lg transition shadow-sm">
                        Buy Now
                    </button>
                </div>
            </div>
        `;
        grid.appendChild(card);
    });
}

function injectCheckoutModal() {
    if (document.getElementById("checkout-modal")) return;

    const modalHTML = `
    <div id="checkout-modal" class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center hidden z-50 p-4">
        <div class="bg-white rounded-2xl max-w-sm w-full p-5 shadow-2xl border border-gray-100 max-h-[85vh] flex flex-col">
            <!-- Header -->
            <div class="flex justify-between items-center pb-3 border-b border-gray-100">
                <h3 class="font-bold text-base text-gray-900">Checkout & Payment</h3>
                <button type="button" onclick="closeCheckout()" class="text-gray-400 hover:text-gray-600 text-xl font-bold">&times;</button>
            </div>
            
            <!-- Scrollable Body so buttons are ALWAYS visible -->
            <form id="checkout-form" onsubmit="handlePurchaseSubmit(event)" class="py-3 flex-grow overflow-y-auto space-y-3">
                <div class="bg-gray-50 p-2.5 rounded-lg border border-gray-200">
                    <div class="flex justify-between text-xs"><span class="text-gray-500">Item:</span><span id="modal-item-name" class="font-semibold text-gray-900"></span></div>
                    <div class="flex justify-between text-xs mt-1"><span class="text-gray-500">Amount Due:</span><span id="modal-item-price" class="font-bold text-emerald-600"></span></div>
                </div>

                <div>
                    <label class="block text-[11px] font-semibold text-gray-700 mb-0.5">Full Name</label>
                    <input type="text" id="cust-name" required placeholder="Enter full name" class="w-full text-xs p-2 border border-gray-300 rounded-lg">
                </div>
                <div>
                    <label class="block text-[11px] font-semibold text-gray-700 mb-0.5">Mobile Number</label>
                    <input type="tel" id="cust-phone" required placeholder="10-digit mobile number" class="w-full text-xs p-2 border border-gray-300 rounded-lg">
                </div>

                <div>
                    <label class="block text-[11px] font-semibold text-gray-700 mb-1">Select Payment Method</label>
                    <div class="grid grid-cols-2 gap-1.5 text-xs">
                        <label class="flex items-center gap-1.5 border border-gray-200 p-1.5 rounded-lg cursor-pointer hover:bg-gray-50">
                            <input type="radio" name="payment_method" value="GPay" checked>
                            <span class="text-xs">Google Pay</span>
                        </label>
                        <label class="flex items-center gap-1.5 border border-gray-200 p-1.5 rounded-lg cursor-pointer hover:bg-gray-50">
                            <input type="radio" name="payment_method" value="PhonePe">
                            <span class="text-xs">PhonePe</span>
                        </label>
                        <label class="flex items-center gap-1.5 border border-gray-200 p-1.5 rounded-lg cursor-pointer hover:bg-gray-50">
                            <input type="radio" name="payment_method" value="Paytm">
                            <span class="text-xs">Paytm</span>
                        </label>
                        <label class="flex items-center gap-1.5 border border-gray-200 p-1.5 rounded-lg cursor-pointer hover:bg-gray-50">
                            <input type="radio" name="payment_method" value="UPI ID">
                            <span class="text-xs">UPI ID</span>
                        </label>
                    </div>
                </div>

                <div>
                    <label class="block text-[11px] font-semibold text-gray-700 mb-0.5">UPI ID / Phone Number</label>
                    <input type="text" id="cust-upi" placeholder="username@upi or mobile number" class="w-full text-xs p-2 border border-gray-300 rounded-lg">
                </div>
            </form>

            <!-- Fixed Footer with Guaranteed Submit & Cancel Buttons -->
            <div class="flex gap-2 pt-3 border-t border-gray-100 mt-auto">
                <button type="button" onclick="closeCheckout()" class="w-1/2 py-2 text-xs font-bold text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300">Cancel</button>
                <button type="submit" form="checkout-form" id="submit-order-btn" class="w-1/2 py-2 text-xs font-bold text-white bg-emerald-600 rounded-lg hover:bg-emerald-700 shadow">Place Order & Pay</button>
            </div>
        </div>
    </div>`;
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function openCheckout(id, name, price, stock) {
    if (stock <= 0) {
        alert("This item is currently out of stock!");
        return;
    }
    currentProduct = { id, name, price };
    document.getElementById("modal-item-name").textContent = name;
    document.getElementById("modal-item-price").textContent = `₹ ${price}`;
    document.getElementById("checkout-modal").classList.remove("hidden");
}

function closeCheckout() {
    document.getElementById("checkout-modal").classList.add("hidden");
    const form = document.getElementById("checkout-form");
    if (form) form.reset();
    currentProduct = null;
}

async function handlePurchaseSubmit(event) {
    event.preventDefault();
    if (!currentProduct) return;

    const btn = document.getElementById("submit-order-btn");
    btn.disabled = true;
    btn.textContent = "Processing...";

    // Strategy: Try endpoints in order until one returns 200 OK
    const endpoints = [
        { url: `${API_URL}/api/products/${currentProduct.id}/buy`, method: "POST", body: { quantity: 1 } },
        { url: `${API_URL}/api/products/${currentProduct.id}/purchase`, method: "POST", body: { quantity: 1 } },
        { url: `${API_URL}/api/orders`, method: "POST", body: { product_id: currentProduct.id, quantity: 1 } },
        { url: `${API_URL}/api/purchase`, method: "POST", body: { product_id: currentProduct.id, quantity: 1 } }
    ];

    let success = false;

    for (const ep of endpoints) {
        try {
            const res = await fetch(ep.url, {
                method: ep.method,
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(ep.body)
            });
            if (res.ok) {
                success = true;
                break;
            }
        } catch (err) {
            console.warn(`Failed calling ${ep.url}:`, err);
        }
    }

    if (success) {
        alert("Order Placed Successfully!");
        closeCheckout();
        fetchProducts();
    } else {
        alert("Checkout failed. Check server terminal for FastAPI routes.");
    }

    btn.disabled = false;
    btn.textContent = "Place Order & Pay";
}

function connectWebSocket() {
    socket = new WebSocket(WS_URL);
    socket.onmessage = () => fetchProducts();
    socket.onclose = () => setTimeout(connectWebSocket, 3000);
}