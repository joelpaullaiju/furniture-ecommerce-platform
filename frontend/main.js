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
        
        const nameLower = product.name.toLowerCase().trim();
        let selectedImage = "chair.jpg"; // Default fallback

        // Dynamic image matching based on your local folder files
        if (nameLower.includes("computer") || nameLower.includes("study") || nameLower.includes("desk")) {
            selectedImage = "Computer-table.jpg";
        } else if (nameLower.includes("dining")) {
            selectedImage = "dining-Table.jpg";
        } else if (nameLower.includes("table")) {
            selectedImage = "Computer-table.jpg";
        } else if (nameLower.includes("bed")) {
            selectedImage = "Bed.jpg";
        } else if (nameLower.includes("sofa") || nameLower.includes("couch")) {
            selectedImage = "sofa.jpg";
        } else if (nameLower.includes("chair")) {
            selectedImage = "chair.jpg";
        }

        // Use custom HTTP image URL if specified, otherwise use local file match
        const imageSrc = (product.image_url && product.image_url.startsWith("http")) 
            ? product.image_url 
            : selectedImage;

        card.innerHTML = `
            <div class="relative h-48 bg-gray-100 flex items-center justify-center overflow-hidden">
                <img src="${imageSrc}" alt="${product.name}" class="w-full h-full object-cover" onerror="this.src='chair.jpg'">
                <span class="absolute top-3 right-3 bg-slate-900/80 text-white text-xs font-bold px-2.5 py-1 rounded-full backdrop-blur-sm">
                    ${product.stock} In Stock
                </span>
            </div>
            <div class="p-4">
                <span class="text-xs font-medium text-blue-600 uppercase tracking-wider">${product.functional || product.category || 'Furniture'}</span>
                <h3 class="font-bold text-gray-900 text-lg mt-1">${product.name}</h3>
                <div class="mt-4 flex items-center justify-between">
                    <span class="text-xl font-extrabold text-gray-900">₹ ${product.price}</span>
                    <button onclick="openCheckout('${product.id}', '${product.name}', ${product.price}, ${product.stock})" class="bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-4 py-2 rounded-lg transition shadow-sm">
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
    <div id="checkout-modal" class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center hidden z-50 p-3">
        <div class="bg-white rounded-2xl max-w-sm w-full p-4 shadow-2xl border border-gray-100 flex flex-col max-h-[85vh]">
            <!-- Header -->
            <div class="flex justify-between items-center pb-2 border-b border-gray-100 shrink-0">
                <h3 class="font-bold text-base text-gray-900">Checkout & Payment</h3>
                <button type="button" onclick="closeCheckout()" class="text-gray-400 hover:text-gray-600 text-xl font-bold">&times;</button>
            </div>
            
            <!-- Scrollable Form Body -->
            <form id="checkout-form" onsubmit="handlePurchaseSubmit(event)" class="py-2 overflow-y-auto space-y-2.5 flex-1">
                <div class="bg-gray-50 p-2.5 rounded-lg border border-gray-200">
                    <div class="flex justify-between text-xs"><span class="text-gray-500">Item:</span><span id="modal-item-name" class="font-semibold text-gray-900"></span></div>
                    <div class="flex justify-between text-xs mt-0.5"><span class="text-gray-500">Amount Due:</span><span id="modal-item-price" class="font-bold text-emerald-600"></span></div>
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
                    <label class="block text-[11px] font-semibold text-gray-700 mb-0.5">UPI ID / Mobile Number</label>
                    <input type="text" id="cust-upi" placeholder="username@upi or 10-digit number" class="w-full text-xs p-2 border border-gray-300 rounded-lg">
                </div>

                <!-- Always Visible Action Buttons -->
                <div class="flex gap-2 pt-2 border-t border-gray-100 shrink-0 mt-2">
                    <button type="button" onclick="closeCheckout()" class="w-1/2 py-2 text-xs font-bold text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300">Cancel</button>
                    <button type="submit" id="submit-order-btn" class="w-1/2 py-2 text-xs font-bold text-white bg-emerald-600 rounded-lg hover:bg-emerald-700 shadow">Place Order & Pay</button>
                </div>
            </form>
        </div>
    </div>`;
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function openCheckout(id, name, price, stock) {
    if (stock <= 0) {
        alert("This item is currently out of stock!");
        return;
    }
    currentProduct = { id: id.toString(), name: name, price: parseFloat(price) };
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

    const name = document.getElementById("cust-name").value;
    const paymentMethod = document.querySelector('input[name="payment_method"]:checked')?.value || "GPay";

    const orderPayload = {
        channel: "Web Store",
        customer: name,
        productId: String(currentProduct.id),
        productName: String(currentProduct.name),
        amount: parseFloat(currentProduct.price),
        quantity: 1
    };

    try {
        const response = await fetch(`${API_URL}/api/orders`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(orderPayload)
        });

        if (response.ok) {
            alert(`Order Placed Successfully!\nThank you, ${name}. Payment processed via ${paymentMethod}.`);
            closeCheckout();
            fetchProducts();
        } else {
            const errData = await response.json().catch(() => ({}));
            console.error("FastAPI Error Details:", errData);
            alert(`Checkout failed (${response.status}). Check terminal console.`);
        }
    } catch (err) {
        console.error("Checkout network error:", err);
        alert("Unable to reach backend server.");
    } finally {
        btn.disabled = false;
        btn.textContent = "Place Order & Pay";
    }
}

function connectWebSocket() {
    socket = new WebSocket(WS_URL);
    socket.onmessage = () => fetchProducts();
    socket.onclose = () => setTimeout(connectWebSocket, 3000);
}