import os
import re
import json
import urllib.request
import urllib.error

# 🛡️ THE BULLETPROOF INTERACTIVE ENGINE (WITH PURE CSS FAILSAFES)
GUARANTEED_CART_ENGINE = """
<!-- ========================================== -->
<!-- BULLETPROOF SHOPPING BAG & CHECKOUT ENGINE -->
<!-- ========================================== -->
<style>
    /* Strict Failsafe CSS: Modal & Drawer can NEVER leak into page layout */
    #productModal {
        display: none !important;
        position: fixed !important;
        inset: 0 !important;
        background: rgba(0, 0, 0, 0.75) !important;
        backdrop-filter: blur(6px) !important;
        z-index: 999999 !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 16px !important;
        box-sizing: border-box !important;
    }
    #productModal.active { display: flex !important; }
    #cartOverlay {
        display: none !important;
        position: fixed !important;
        inset: 0 !important;
        background: rgba(0, 0, 0, 0.6) !important;
        backdrop-filter: blur(4px) !important;
        z-index: 999998 !important;
    }
    #cartOverlay.active { display: block !important; }
    #cartDrawer {
        position: fixed !important;
        top: 0 !important;
        right: 0 !important;
        height: 100% !important;
        width: 100% !important;
        max-width: 420px !important;
        background: #111218 !important;
        color: #f4f4f5 !important;
        border-left: 1px solid #27272a !important;
        box-shadow: -10px 0 30px rgba(0,0,0,0.6) !important;
        z-index: 999999 !important;
        transform: translateX(100%) !important;
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        padding: 24px !important;
        box-sizing: border-box !important;
    }
    #cartDrawer.open { transform: translateX(0%) !important; }
</style>

<script>
    window.KIOSK_PRODUCTS = {
        {% for p in (regular_products or []) + (flash_sales or []) %}
        "{{ p.id }}": {
            "id": {{ p.id }},
            "name": {{ p.name|tojson }},
            "price": {{ (p.current_price if p.current_price is defined else (p.original_price if p.original_price is defined else 0)) }},
            "image": {{ (p.image or "")|tojson }},
            "description": {{ (p.description or "")|tojson }},
            "attributes": {{ (p.get_attributes() or {})|tojson }}
        },
        {% endfor %}
    };
</script>

<!-- Product Specs & Options Modal -->
<div id="productModal">
    <div class="bg-[#14161f] border border-stone-800 p-6 md:p-8 max-w-sm w-full rounded-3xl shadow-2xl relative text-white">
        <button type="button" onclick="closeProductModal()" class="absolute top-4 right-4 text-stone-400 hover:text-white font-bold text-xl cursor-pointer">&times;</button>
        <span class="text-[10px] font-mono text-amber-400 uppercase tracking-widest block mb-1">Select Specifications</span>
        <h3 id="modalProductName" class="font-bold text-lg text-white mb-2 uppercase"></h3>
        <p id="modalProductDesc" class="text-xs text-stone-400 mb-4 leading-relaxed"></p>
        <p id="modalProductPrice" class="font-mono text-2xl font-black text-amber-400 mb-6"></p>
        <div id="modalVariantsContainer" class="space-y-4 mb-6"></div>
        <button type="button" onclick="confirmAddToCart()" 
                class="w-full bg-amber-400 hover:bg-amber-300 text-black font-black py-4 rounded-xl text-xs uppercase tracking-wider transition cursor-pointer shadow-lg">
            ADD TO BAG &rarr;
        </button>
    </div>
</div>

<!-- Slide-Out Shopping Bag Drawer -->
<div id="cartOverlay" onclick="toggleCart()"></div>
<aside id="cartDrawer">
    <div>
        <div class="flex justify-between items-center pb-4 border-b border-stone-800 mb-6">
            <div>
                <h3 class="font-bold text-base uppercase tracking-wider text-white m-0">Your Shopping Bag</h3>
                <span class="text-[10px] text-stone-400 font-mono">Direct WhatsApp Intake</span>
            </div>
            <button type="button" onclick="toggleCart()" class="text-xs font-mono font-bold text-stone-400 hover:text-white cursor-pointer">&times; CLOSE</button>
        </div>
        <div id="cartItemsList" class="space-y-3 max-h-[40vh] overflow-y-auto pr-1"></div>
    </div>
    <div class="pt-6 border-t border-stone-800">
        <div class="flex justify-between items-center mb-6 font-mono">
            <span class="text-xs uppercase text-stone-400">Total:</span>
            <span id="cartTotalPrice" class="font-black text-2xl text-amber-400">{{ (store.currency if store and store.currency else '₦') }}0.00</span>
        </div>
        <form id="checkoutForm" onsubmit="handleCheckout(event)" class="space-y-3">
            <input type="text" id="custName" required placeholder="Your Full Name" 
                   class="w-full p-3 bg-[#181a24] border border-stone-800 rounded-xl text-xs text-white outline-none focus:border-amber-400">
            <input type="text" id="custPhone" required placeholder="WhatsApp Number (e.g. 08012345678)" 
                   class="w-full p-3 bg-[#181a24] border border-stone-800 rounded-xl text-xs text-white outline-none focus:border-amber-400">
            <textarea id="custAddress" required placeholder="Delivery Address / City / Notes" rows="2" 
                      class="w-full p-3 bg-[#181a24] border border-stone-800 rounded-xl text-xs text-white outline-none focus:border-amber-400"></textarea>
            <button type="submit" id="checkoutBtn" 
                    class="w-full bg-[#16a34a] hover:bg-[#15803d] text-white font-black py-4 rounded-xl text-xs uppercase tracking-wider transition cursor-pointer shadow-lg">
                COMPLETE ORDER ON WHATSAPP &rarr;
            </button>
        </form>
    </div>
</aside>

<script>
    const storeSlug = {{ (store.slug if store else '')|tojson }};
    const storeCurrency = {{ (store.currency if store and store.currency else '₦')|tojson }};
    let cart = [];
    let currentModalProduct = null;

    // Guaranteed Live Search
    function filterProducts(query) {
        const q = (query || '').toLowerCase().trim();
        const cards = document.querySelectorAll('.product-card');
        cards.forEach(card => {
            const name = (card.getAttribute('data-name') || card.innerText || '').toLowerCase();
            card.style.display = name.includes(q) ? '' : 'none';
        });
    }

    function toggleCart() {
        const drawer = document.getElementById('cartDrawer');
        const overlay = document.getElementById('cartOverlay');
        if (drawer) drawer.classList.toggle('open');
        if (overlay) overlay.classList.toggle('active');
    }

    function openProductModal(productId) {
        const product = window.KIOSK_PRODUCTS[productId];
        if (!product) return;
        currentModalProduct = product;
        document.getElementById('modalProductName').innerText = product.name;
        document.getElementById('modalProductDesc').innerText = product.description || '';
        document.getElementById('modalProductPrice').innerText = `${storeCurrency}${Number(product.price).toLocaleString()}`;
        const container = document.getElementById('modalVariantsContainer');
        container.innerHTML = '';
        const attrs = product.attributes || {};
        for (const [attr, opts] of Object.entries(attrs)) {
            if (!Array.isArray(opts) || opts.length === 0) continue;
            const group = document.createElement('div');
            group.innerHTML = `
                <label class='block font-mono text-[10px] uppercase text-amber-400 mb-1 font-bold'>${attr}</label>
                <select class='variant-select w-full p-2.5 bg-[#181a24] border border-stone-800 text-white font-mono text-xs rounded-xl outline-none focus:border-amber-400' data-attr='${attr}'>
                    ${opts.map(o => `<option value="${o}">${o}</option>`).join('')}
                </select>
            `;
            container.appendChild(group);
        }
        const modal = document.getElementById('productModal');
        if (modal) modal.classList.add('active');
    }

    function closeProductModal() {
        const modal = document.getElementById('productModal');
        if (modal) modal.classList.remove('active');
        currentModalProduct = null;
    }

    function confirmAddToCart() {
        if (!currentModalProduct) return;
        const selected = [];
        document.querySelectorAll('.variant-select').forEach(s => {
            selected.push(`${s.getAttribute('data-attr')}: ${s.value}`);
        });
        cart.push({
            product_id: currentModalProduct.id,
            name: currentModalProduct.name,
            price: currentModalProduct.price,
            variants: selected.join(' | '),
            quantity: 1
        });
        updateCartUI();
        closeProductModal();
        toggleCart();
    }

    function updateCartUI() {
        const list = document.getElementById('cartItemsList');
        const badge = document.getElementById('cartCountBadge');
        const totalEl = document.getElementById('cartTotalPrice');
        if (badge) badge.innerText = cart.length;
        if (!list) return;
        list.innerHTML = '';
        let total = 0;
        cart.forEach((item, idx) => {
            total += item.price * item.quantity;
            const d = document.createElement('div');
            d.className = 'flex justify-between items-start p-3 bg-[#181a24] border border-stone-800 rounded-xl text-xs font-mono';
            d.innerHTML = `
                <div>
                    <strong class="text-white block font-bold">${item.name}</strong>
                    ${item.variants ? `<span class="text-[10px] text-amber-400 block">${item.variants}</span>` : ''}
                    <span class="text-emerald-400 font-bold mt-1 block">${storeCurrency}${Number(item.price).toLocaleString()}</span>
                </div>
                <button type="button" onclick="cart.splice(${idx}, 1); updateCartUI();" class="text-rose-400 hover:text-rose-300 font-bold ml-3 text-base cursor-pointer">&times;</button>
            `;
            list.appendChild(d);
        });
        if (totalEl) totalEl.innerText = `${storeCurrency}${total.toLocaleString()}`;
    }

    async function handleCheckout(e) {
        e.preventDefault();
        if (cart.length === 0) { alert('Your bag is empty. Please select an item first.'); return; }
        const btn = document.getElementById('checkoutBtn');
        btn.innerText = 'GENERATING WHATSAPP RECEIPT...';
        btn.disabled = true;
        const payload = {
            customer_name: document.getElementById('custName').value,
            customer_phone: document.getElementById('custPhone').value,
            delivery_address: document.getElementById('custAddress').value,
            cart: cart
        };
        try {
            const res = await fetch(`/${storeSlug}/checkout`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (data.status === 'success') {
                cart = [];
                updateCartUI();
                window.location.href = data.whatsapp_url;
            } else {
                alert(data.message || 'Error creating order.');
                btn.innerText = 'COMPLETE ORDER ON WHATSAPP →';
                btn.disabled = false;
            }
        } catch (err) {
            alert('Connection error. Please try again.');
            btn.innerText = 'COMPLETE ORDER ON WHATSAPP →';
            btn.disabled = false;
        }
    }
</script>
"""


# ==============================================================================
# 🎨 3 VERSATILE, CURATED FALLBACK TEMPLATES (NEVER RETURN AN EMPTY PAGE)
# ==============================================================================

FALLBACK_TEMPLATE_LUXURY = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700;900&family=Plus+Jakarta+Sans:wght@400;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #0b0c10; color: #f4f4f5; }
        .font-serif { font-family: 'Playfair Display', serif; }
    </style>
</head>
<body class="min-h-screen flex flex-col justify-between">
    <header class="sticky top-0 z-40 bg-[#111218]/90 backdrop-blur-md border-b border-stone-800 px-6 py-4 flex justify-between items-center">
        <div class="flex items-center space-x-3">
            {% if store and store.logo and store.logo != 'default_logo.png' %}
            <img src="{{ store.logo }}" alt="{{ store.name }}" class="h-10 w-10 object-contain rounded-full border border-amber-400/30">
            {% endif %}
            <span class="text-xl font-bold font-serif uppercase tracking-wider text-white">{{ store.name if store else 'Exclusive Boutique' }}</span>
        </div>
        <div class="flex items-center space-x-4">
            <input type="text" oninput="filterProducts(this.value)" placeholder="Search collection..." class="hidden md:block bg-stone-900 border border-stone-700 text-xs text-white px-4 py-2 rounded-full outline-none focus:border-amber-400 w-52">
            <button onclick="toggleCart()" class="flex items-center space-x-2 bg-stone-900 border border-stone-800 hover:border-amber-400/40 px-4 py-2 rounded-xl transition cursor-pointer">
                <span class="text-xs font-mono font-bold text-amber-400">BAG</span>
                <span id="cartCountBadge" class="bg-amber-400 text-black text-[10px] font-black px-1.5 py-0.5 rounded-full">0</span>
            </button>
        </div>
    </header>

    <section class="relative min-h-[55vh] flex items-center justify-center overflow-hidden bg-black px-4 py-16">
        <div class="relative z-10 max-w-2xl w-full bg-[#111218]/85 backdrop-blur-xl border border-stone-800/80 p-8 md:p-12 rounded-3xl text-center shadow-2xl">
            <span class="inline-block text-[11px] font-mono tracking-widest text-amber-400 uppercase bg-amber-400/10 border border-amber-400/20 px-3.5 py-1 rounded-full mb-4">
                ✨ CURATED SELECTION // BESPOKE
            </span>
            <h1 class="text-4xl md:text-5xl font-black font-serif text-white mb-4 tracking-tight leading-tight">{{ store.name if store else 'Exclusive Boutique' }}</h1>
            <p class="text-stone-300 text-sm md:text-base leading-relaxed mb-8 max-w-lg mx-auto">{{ store.bio if store else 'Experience craftsmanship and curated quality.' }}</p>
            <a href="#products-grid" class="inline-block bg-amber-400 hover:bg-amber-300 text-black font-black text-xs uppercase tracking-widest px-8 py-3.5 rounded-xl transition shadow-lg">EXPLORE CATALOG &darr;</a>
        </div>
    </section>

    <main id="products-grid" class="container mx-auto py-16 px-4 md:px-6 flex-grow">
        <div class="text-center max-w-xl mx-auto mb-10">
            <span class="text-[10px] font-mono tracking-widest text-amber-400 uppercase block mb-1">SIGNATURE ITEMS</span>
            <h2 class="text-3xl font-bold font-serif text-white">Curated Collection</h2>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {% for p in regular_products %}
            <div class="product-card bg-[#14161f] border border-stone-800/90 rounded-2xl p-5 flex flex-col justify-between hover:border-amber-400/40 transition shadow-xl" data-name="{{ p.name }}">
                <div>
                    <div class="w-full h-48 bg-stone-900 rounded-xl overflow-hidden mb-4 relative flex items-center justify-center border border-stone-800">
                        {% if p.image and p.image != 'default_product.png' %}
                        <img src="{{ p.image }}" alt="{{ p.name }}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" class="w-full h-full object-cover">
                        <div style="display:none;" class="text-stone-500 text-xs font-mono uppercase tracking-wider">NO PREVIEW</div>
                        {% else %}
                        <div class="text-stone-500 text-xs font-mono uppercase tracking-wider">NO PREVIEW</div>
                        {% endif %}
                    </div>
                    <h3 class="text-lg font-bold text-white mb-1 uppercase tracking-wide font-serif">{{ p.name }}</h3>
                    <p class="text-xs text-stone-400 mb-4 line-clamp-2 leading-relaxed">{{ p.description or 'Artisanal formulation.' }}</p>
                </div>
                <div class="pt-4 border-t border-stone-800 flex justify-between items-center">
                    <span class="font-mono text-lg font-black text-amber-400">{{ store.currency if store and store.currency else '₦' }}{{ "{:,.0f}".format(p.current_price) }}</span>
                    <button type="button" onclick="openProductModal({{ p.id }})" class="bg-amber-400 hover:bg-amber-300 text-black font-black text-[10px] uppercase tracking-wider py-2.5 px-4 rounded-xl transition cursor-pointer">ORDER NOW</button>
                </div>
            </div>
            {% endfor %}
        </div>
    </main>

    <footer class="border-t border-stone-800/80 py-8 text-center text-xs font-mono text-stone-500">
        &copy; {{ store.name if store else 'Marketplace' }} &bull; Powered by Marketplace
    </footer>
</body>
</html>"""

FALLBACK_TEMPLATE_MINIMAL = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body { font-family: 'Inter', sans-serif; background-color: #090a0f; color: #eceff4; }</style>
</head>
<body class="min-h-screen flex flex-col justify-between">
    <header class="sticky top-0 z-40 bg-[#090a0f]/95 backdrop-blur-md border-b border-stone-800 px-6 py-4 flex justify-between items-center">
        <div class="flex items-center space-x-3">
            {% if store and store.logo and store.logo != 'default_logo.png' %}
            <img src="{{ store.logo }}" alt="{{ store.name }}" class="h-9 w-9 object-contain rounded-md border border-stone-700">
            {% endif %}
            <span class="text-lg font-black uppercase tracking-tight text-white">{{ store.name if store else 'Official Store' }}</span>
        </div>
        <div class="flex items-center space-x-4">
            <input type="text" oninput="filterProducts(this.value)" placeholder="Search products..." class="hidden md:block bg-stone-900 border border-stone-800 text-xs text-white px-4 py-2 rounded-lg outline-none focus:border-stone-600 w-52">
            <button onclick="toggleCart()" class="flex items-center space-x-2 bg-white hover:bg-stone-200 text-black px-4 py-2 rounded-lg transition font-bold text-xs cursor-pointer">
                <span>BAG</span>
                <span id="cartCountBadge" class="bg-black text-white text-[10px] font-black px-1.5 py-0.5 rounded-full">0</span>
            </button>
        </div>
    </header>

    <section class="border-b border-stone-800/80 px-6 py-16 bg-[#0f1118]">
        <div class="container mx-auto max-w-4xl text-left">
            <span class="text-xs font-mono uppercase tracking-widest text-emerald-400 block mb-2">⚡ VERIFIED DIRECT CATALOG</span>
            <h1 class="text-4xl md:text-6xl font-black text-white tracking-tight mb-4 leading-tight">{{ store.name if store else 'Official Store' }}</h1>
            <p class="text-stone-300 text-sm md:text-base max-w-xl leading-relaxed">{{ store.bio if store else 'Welcome to our verified direct marketplace store.' }}</p>
        </div>
    </section>

    <main id="products-grid" class="container mx-auto py-12 px-6 flex-grow">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {% for p in regular_products %}
            <div class="product-card bg-[#11131a] border border-stone-800/80 rounded-xl p-4 flex flex-col justify-between hover:border-stone-600 transition" data-name="{{ p.name }}">
                <div>
                    <div class="w-full h-44 bg-stone-900 rounded-lg overflow-hidden mb-3 relative flex items-center justify-center border border-stone-800">
                        {% if p.image and p.image != 'default_product.png' %}
                        <img src="{{ p.image }}" alt="{{ p.name }}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" class="w-full h-full object-cover">
                        <div style="display:none;" class="text-stone-500 text-xs font-mono uppercase">NO PREVIEW</div>
                        {% else %}
                        <div class="text-stone-500 text-xs font-mono uppercase">NO PREVIEW</div>
                        {% endif %}
                    </div>
                    <h3 class="text-base font-bold text-white mb-1 tracking-tight">{{ p.name }}</h3>
                    <p class="text-xs text-stone-400 mb-3 line-clamp-2">{{ p.description or 'In-stock item.' }}</p>
                </div>
                <div class="pt-3 border-t border-stone-800 flex justify-between items-center">
                    <span class="font-mono text-base font-bold text-white">{{ store.currency if store and store.currency else '₦' }}{{ "{:,.0f}".format(p.current_price) }}</span>
                    <button type="button" onclick="openProductModal({{ p.id }})" class="bg-white hover:bg-stone-200 text-black font-black text-[10px] uppercase tracking-wider py-2 px-3 rounded-lg transition cursor-pointer">ADD TO BAG</button>
                </div>
            </div>
            {% endfor %}
        </div>
    </main>

    <footer class="border-t border-stone-800/80 py-8 text-center text-xs font-mono text-stone-500">
        &copy; {{ store.name if store else 'Storefront' }} &bull; Powered by Marketplace
    </footer>
</body>
</html>"""

FALLBACK_TEMPLATE_URBAN = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;800;900&family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body { font-family: 'Inter', sans-serif; background-color: #121316; color: #f4f4f5; } h1, h2, h3 { font-family: 'Poppins', sans-serif; }</style>
</head>
<body class="min-h-screen flex flex-col justify-between">
    <header class="sticky top-0 z-40 bg-[#121316]/95 backdrop-blur-md border-b border-stone-800 px-6 py-4 flex justify-between items-center">
        <div class="flex items-center space-x-3">
            <span class="text-xl font-black uppercase tracking-wide text-white">{{ store.name if store else 'Urban Hub' }}</span>
        </div>
        <div class="flex items-center space-x-4">
            <input type="text" oninput="filterProducts(this.value)" placeholder="Search the menu..." class="hidden md:block bg-stone-900 border border-stone-800 text-xs text-white px-4 py-2 rounded-full outline-none focus:border-red-500 w-52">
            <button onclick="toggleCart()" class="flex items-center space-x-2 bg-stone-800 border border-stone-700 px-4 py-2 rounded-xl text-white font-bold text-xs cursor-pointer hover:border-red-500">
                <span class="text-red-400">BAG</span>
                <span id="cartCountBadge" class="bg-red-500 text-white text-[10px] font-black px-1.5 py-0.5 rounded-full">0</span>
            </button>
        </div>
    </header>

    <section class="relative min-h-[50vh] flex items-center justify-center overflow-hidden bg-black px-4 py-16">
        <div class="relative z-10 max-w-2xl w-full bg-[#181a24]/90 backdrop-blur-xl border border-stone-800 p-8 md:p-12 rounded-3xl text-center shadow-2xl">
            <span class="inline-block text-[11px] font-mono tracking-widest text-red-400 uppercase bg-red-500/10 border border-red-500/20 px-3.5 py-1 rounded-full mb-4">
                🔥 FRESH FLAME GRILLED // LIVE ORDER
            </span>
            <h1 class="text-4xl md:text-5xl font-black text-white mb-4 tracking-tight leading-tight uppercase">{{ store.name if store else 'Urban Hub' }}</h1>
            <p class="text-stone-300 text-sm md:text-base leading-relaxed mb-8 max-w-lg mx-auto">{{ store.bio if store else 'Crafted fresh daily with authentic flavor.' }}</p>
            <a href="#products-grid" class="inline-block bg-red-500 hover:bg-red-600 text-white font-black text-xs uppercase tracking-widest px-8 py-3.5 rounded-xl transition shadow-lg">EXPLORE MENU &darr;</a>
        </div>
    </section>

    <main id="products-grid" class="container mx-auto py-16 px-4 md:px-6 flex-grow">
        <div class="text-center max-w-xl mx-auto mb-10">
            <h2 class="text-3xl font-black text-white uppercase tracking-tight">Our Specials</h2>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {% for p in regular_products %}
            <div class="product-card bg-[#181a24] border border-stone-800 rounded-2xl p-5 flex flex-col justify-between hover:border-red-500/50 transition shadow-xl" data-name="{{ p.name }}">
                <div>
                    <div class="w-full h-48 bg-stone-900 rounded-xl overflow-hidden mb-4 relative flex items-center justify-center border border-stone-800">
                        {% if p.image and p.image != 'default_product.png' %}
                        <img src="{{ p.image }}" alt="{{ p.name }}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" class="w-full h-full object-cover">
                        <div style="display:none;" class="text-stone-500 text-xs font-mono uppercase tracking-wider">NO PREVIEW</div>
                        {% else %}
                        <div class="text-stone-500 text-xs font-mono uppercase tracking-wider">NO PREVIEW</div>
                        {% endif %}
                    </div>
                    <h3 class="text-lg font-bold text-white mb-1 uppercase tracking-wide">{{ p.name }}</h3>
                    <p class="text-xs text-stone-400 mb-4 line-clamp-2 leading-relaxed">{{ p.description or 'Cooked to order.' }}</p>
                </div>
                <div class="pt-4 border-t border-stone-800 flex justify-between items-center">
                    <span class="font-mono text-lg font-black text-red-400">{{ store.currency if store and store.currency else '₦' }}{{ "{:,.0f}".format(p.current_price) }}</span>
                    <button type="button" onclick="openProductModal({{ p.id }})" class="bg-red-500 hover:bg-red-600 text-white font-black text-[10px] uppercase tracking-wider py-2.5 px-4 rounded-xl transition cursor-pointer">ORDER NOW</button>
                </div>
            </div>
            {% endfor %}
        </div>
    </main>

    <footer class="border-t border-stone-800/80 py-8 text-center text-xs font-mono text-stone-500">
        &copy; {{ store.name if store else 'Urban Hub' }} &bull; Powered by Marketplace
    </footer>
</body>
</html>"""


def get_curated_fallback_template(kiosk_name: str, bio: str, prompt: str) -> str:
    """Selects the best archetype based on prompt/niche keywords, or rotates with a deterministic hash."""
    corpus = f"{kiosk_name} {bio} {prompt}".lower()

    # Niche Keyword Router
    if any(k in corpus for k in ['perfume', 'scent', 'fragrance', 'luxury', 'gold', 'extrait', 'jewelry', 'boutique', 'watch']):
        print(f"🛡️ [FAILSAFE ROUTER] Selected 'Obsidian Luxury' template archetype for '{kiosk_name}'.", flush=True)
        return FALLBACK_TEMPLATE_LUXURY

    if any(k in corpus for k in ['food', 'burger', 'kitchen', 'grill', 'sizzle', 'street', 'dish', 'meal', 'cafe', 'bites', 'snack']):
        print(f"🛡️ [FAILSAFE ROUTER] Selected 'Urban Pulse' template archetype for '{kiosk_name}'.", flush=True)
        return FALLBACK_TEMPLATE_URBAN

    # Deterministic Rotation Fallback
    idx = abs(hash(kiosk_name)) % 3
    fallbacks = [FALLBACK_TEMPLATE_MINIMAL, FALLBACK_TEMPLATE_LUXURY, FALLBACK_TEMPLATE_URBAN]
    print(f"🛡️ [FAILSAFE ROUTER] Selected Archetype #{idx} for '{kiosk_name}'.", flush=True)
    return fallbacks[idx]


# ==============================================================================
# 🛠️ CHASSIS INJECTION & PARSING UTILITIES
# ==============================================================================

def clean_html_fences(raw_text: str) -> str:
    raw_text = re.sub(r'^```html\s*', '', raw_text.strip(), flags=re.IGNORECASE)
    raw_text = re.sub(r'^```\s*', '', raw_text.strip())
    raw_text = re.sub(r'```$', '', raw_text.strip())
    return raw_text.strip()


def inject_bulletproof_chassis(html_content: str, kiosk_name: str = '', bio: str = '', meta_img: str = '') -> str:
    """
    1. Injects clean OpenGraph, Twitter, and SEO tags with correct absolute image priority.
    2. Guarantees Tailwind CSS CDN in <head>.
    3. Strips AI-written duplicate/dummy functions and modals.
    4. Attaches GUARANTEED_CART_ENGINE right before </body>.
    """
    safe_title = kiosk_name.strip() if kiosk_name else "{{ store.name }}"
    safe_desc = bio.strip().replace('"', '&quot;') if bio else "{{ store.bio or 'Explore our catalog on Marketplace' }}"
    safe_img = meta_img.strip() if meta_img else "{{ store.logo or store.hero_image or '' }}"

    meta_tags = (
        '    <meta charset="UTF-8">\n'
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        f'    <title>{safe_title}</title>\n'
        f'    <meta name="description" content="{safe_desc}">\n'
        '    <meta property="og:type" content="website">\n'
        '    <meta property="og:site_name" content="Marketplace">\n'
        f'    <meta property="og:title" content="{safe_title}">\n'
        f'    <meta property="og:description" content="{safe_desc}">\n'
        f'    <meta property="og:image" content="{safe_img}">\n'
        '    <meta name="twitter:card" content="summary_large_image">\n'
        f'    <meta name="twitter:title" content="{safe_title}">\n'
        f'    <meta name="twitter:description" content="{safe_desc}">\n'
        f'    <meta name="twitter:image" content="{safe_img}">'
    )

    # 1. Guarantee Head Meta & Tailwind
    if re.search(r'<head[^>]*>', html_content, re.IGNORECASE):
        html_content = re.sub(r'<title>.*?</title>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        html_content = re.sub(r'<meta\s+property=["\']og:[^>]+>', '', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<meta\s+name=["\']twitter:[^>]+>', '', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<meta\s+name=["\']description["\'][^>]+>', '', html_content, flags=re.IGNORECASE)
        
        injection = f"<head>\n{meta_tags}"
        if 'cdn.tailwindcss.com' not in html_content:
            injection += '\n    <script src="https://cdn.tailwindcss.com"></script>'
        html_content = re.sub(r'<head[^>]*>', injection, html_content, count=1, flags=re.IGNORECASE)

    # 2. Strip broken empty <img> tags
    html_content = re.sub(r'<img[^>]+src=["\']\s*["\'][^>]*>', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<img[^>]+src=["\'](None|null|undefined)["\'][^>]*>', '', html_content, flags=re.IGNORECASE)

    # 3. Strip any broken/duplicate modals the AI attempted to create
    html_content = re.sub(r'<div id="productModal".*?</div>\s*</div>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<aside id="cartDrawer".*?</aside>', '', html_content, flags=re.DOTALL | re.IGNORECASE)

    # 4. Strip dummy duplicate JS definitions that conflict with our engine
    html_content = re.sub(r'function\s+filterProducts\s*\([^)]*\)\s*\{[^}]*\}', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'function\s+toggleCart\s*\([^)]*\)\s*\{[^}]*\}', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'function\s+openProductModal\s*\([^)]*\)\s*\{[^}]*\}', '', html_content, flags=re.DOTALL)

    # 5. Inject guaranteed cart engine
    if re.search(r'</body>', html_content, re.IGNORECASE):
        return re.sub(r'</body>', GUARANTEED_CART_ENGINE + '\n</body>', html_content, count=1, flags=re.IGNORECASE)
    return html_content + '\n' + GUARANTEED_CART_ENGINE


def query_openrouter(prompt_instruction: str, api_key: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": "Bearer " + api_key.strip(),
        "Content-Type": "application/json",
        "HTTP-Referer": "https://marketplace-beryl-delta.vercel.app",
        "X-Title": "Marketplace Kiosk Engine"
    }

    # Reliable OpenRouter model
    model_name = os.environ.get('OPENROUTER_MODEL') or 'meta-llama/llama-3.3-70b-instruct'

    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": prompt_instruction}
        ]
    }

    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=60) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return res_data['choices'][0]['message']['content']
    except Exception as e:
        print(f"OpenRouter Error: {e}", flush=True)
        return None


# ==============================================================================
# 🚀 MASTER GENERATION PIPELINE (PRIMARY GEMINI -> BACKUP OPENROUTER -> 3 ARCHETYPES)
# ==============================================================================

def generate_kiosk_template(kiosk_name: str, bio: str, prompt: str, logo_url: str = '', hero_url: str = '', bg_url: str = '', currency: str = '₦') -> str:
    """
    Tier 1: Google Gemini (Primary Bespoke AI)
    Tier 2: OpenRouter (Backup Bespoke AI)
    Tier 3: Curated Design Archetype (Guaranteed 100% Fail-Safe)
    """
    primary_meta_img = logo_url or hero_url or bg_url or ''

    system_instruction = (
        f'You are an elite creative director designing a bespoke storefront website for "{kiosk_name}".\n'
        'You NEVER build generic, plain, or cookie-cutter templates.\n\n'
        'CLIENT BRIEF & ASSETS:\n'
        f'- Brand Name: "{kiosk_name}"\n'
        f'- Design Instructions: "{prompt}"\n'
        f'- Brand Bio / Slogan: "{bio}"\n'
        f'- Brand Assets: Logo="{logo_url}", Hero="{hero_url}", Background="{bg_url}", Currency="{currency}"\n\n'
        'CRITICAL RULES & DATA SCHEMA:\n'
        '1. IN <head>:\n'
        '   - Include Google Fonts matching the niche and <script src="https://cdn.tailwindcss.com"></script>.\n'
        '2. HERO SECTION:\n'
        '   - Pre-headline pill badge MUST MATCH THE NICHE (e.g. Perfume: "✨ ARTISANAL EXTRAIT // RARE SCENTS", Food: "🔥 FRESH FLAME GRILLED", Tech: "⚡ VERIFIED GEAR").\n'
        '   - High contrast: Wrap hero text in a dark glassmorphic card (e.g. bg-stone-900/85 backdrop-blur-md) so text is ALWAYS easily readable!\n'
        '   - Only render hero <img> if Hero asset is non-empty.\n'
        '3. HEADER & SEARCH:\n'
        '   - Top bar: Brand logo ("' + logo_url + '") and Name, an input calling oninput="filterProducts(this.value)", and a BAG button with onclick="toggleCart()" containing <span id="cartCountBadge">0</span>.\n'
        '4. PRODUCTS LOOP (DATABASE MODEL ALIGNED):\n'
        '   Iterate products using:\n'
        '   {% for p in regular_products %}\n'
        '   <div class="product-card" data-name="{{ p.name }}">\n'
        '       <!-- ISOLATED IMAGE CONTAINER -->\n'
        '       <div class="product-img-box w-full h-48 bg-stone-900 rounded-xl overflow-hidden mb-4 relative flex items-center justify-center border border-stone-800">\n'
        '           {% if p.image and p.image != "default_product.png" %}\n'
        '               <img src="{{ p.image }}" alt="{{ p.name }}" onerror="this.style.display=\'none\'; this.nextElementSibling.style.display=\'flex\';" class="w-full h-full object-cover">\n'
        '               <div style="display:none;" class="text-stone-500 text-xs font-mono uppercase tracking-wider">NO PREVIEW</div>\n'
        '           {% else %}\n'
        '               <div class="text-stone-500 text-xs font-mono uppercase tracking-wider">NO PREVIEW</div>\n'
        '           {% endif %}\n'
        '       </div>\n'
        '       <h3 class="text-lg font-bold text-white mb-1 uppercase tracking-wide">{{ p.name }}</h3>\n'
        '       <p class="text-xs text-stone-300 mb-4 line-clamp-2 leading-relaxed">{{ p.description or "Freshly prepared." }}</p>\n'
        '       <div class="pt-4 border-t border-stone-800 flex justify-between items-center">\n'
        '           <span class="font-mono text-lg font-black text-amber-400">{{ store.currency if store and store.currency else "₦" }}{{ "{:,.0f}".format(p.current_price) }}</span>\n'
        '           <button type="button" onclick="openProductModal({{ p.id }})">ORDER NOW</button>\n'
        '       </div>\n'
        '   </div>\n'
        '   {% endfor %}\n'
        '5. DO NOT write your own checkout drawer or modal scripts. The engine is automatically injected.\n'
        'Output ONLY pure valid HTML. No markdown backticks.'
    )

    # -------------------------------------------------------------
    # 1. Tier 1: Google Gemini (Primary)
    # -------------------------------------------------------------
    gemini_key = (os.environ.get('AI_API_KEY') or '').strip()
    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model_name = os.environ.get('GEMINI_MODEL', 'gemini-2.0-flash')
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(system_instruction)
            
            raw_text = ""
            if response and hasattr(response, 'text'):
                try:
                    raw_text = response.text
                except Exception:
                    pass
            
            raw_html = clean_html_fences(raw_text)
            if raw_html:
                print(f"✨ [AI BUILDER] Bespoke template generated via Primary Gemini ({model_name})!", flush=True)
                return inject_bulletproof_chassis(raw_html, kiosk_name, bio, primary_meta_img)
        except Exception as e:
            print(f"⚠️ [AI BUILDER] Gemini Tier 1 notice: {e}", flush=True)

    # -------------------------------------------------------------
    # 2. Tier 2: OpenRouter (Backup AI)
    # -------------------------------------------------------------
    openrouter_key = (os.environ.get('OPENROUTER_API_KEY') or '').strip()
    if openrouter_key:
        try:
            raw_response = query_openrouter(system_instruction, openrouter_key)
            if raw_response:
                raw_html = clean_html_fences(raw_response)
                if raw_html:
                    print("✨ [AI BUILDER] Bespoke template generated via Backup OpenRouter!", flush=True)
                    return inject_bulletproof_chassis(raw_html, kiosk_name, bio, primary_meta_img)
        except Exception as e:
            print(f"⚠️ [AI BUILDER] OpenRouter Tier 2 notice: {e}", flush=True)

    # -------------------------------------------------------------
    # 3. Tier 3: Curated Design Archetype (Guaranteed 100% Fail-Safe)
    # -------------------------------------------------------------
    print(f"🛡️ [AI BUILDER] Activating Curated Design Archetype fallback for '{kiosk_name}'.", flush=True)
    fallback_html = get_curated_fallback_template(kiosk_name, bio, prompt)
    return inject_bulletproof_chassis(fallback_html, kiosk_name, bio, primary_meta_img)
