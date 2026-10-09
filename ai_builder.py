import os
import re
import json
import urllib.request
import urllib.error

# 🛡️ THE BULLETPROOF INTERACTIVE ENGINE (MODAL INSPECTION + TOAST + CHECKOUT)
GUARANTEED_CART_ENGINE = """
<!-- ======================================================== -->
<!-- BULLETPROOF DETAIL MODAL, TOAST & WHATSAPP CHECKOUT ENGINE -->
<!-- ======================================================== -->
<style>
    #productModal { display: none !important; position: fixed !important; inset: 0 !important; background: rgba(0, 0, 0, 0.85) !important; backdrop-filter: blur(12px) !important; z-index: 999999 !important; align-items: center !important; justify-content: center !important; padding: 16px !important; box-sizing: border-box !important; }
    #productModal.active { display: flex !important; }
    #cartOverlay { display: none !important; position: fixed !important; inset: 0 !important; background: rgba(0, 0, 0, 0.65) !important; backdrop-filter: blur(4px) !important; z-index: 999998 !important; }
    #cartOverlay.active { display: block !important; }
    #cartDrawer { position: fixed !important; top: 0 !important; right: 0 !important; height: 100% !important; width: 100% !important; max-width: 420px !important; background: #111218 !important; color: #f4f4f5 !important; border-left: 1px solid #27272a !important; box-shadow: -10px 0 30px rgba(0,0,0,0.6) !important; z-index: 999999 !important; transform: translateX(100%) !important; transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important; display: flex !important; flex-direction: column !important; justify-content: space-between !important; padding: 24px !important; box-sizing: border-box !important; }
    #cartDrawer.open { transform: translateX(0%) !important; }
    #cartToast { position: fixed !important; bottom: 24px !important; right: 24px !important; background: #16a34a !important; color: #ffffff !important; padding: 12px 20px !important; border-radius: 9999px !important; font-family: inherit !important; font-size: 13px !important; font-weight: 700 !important; letter-spacing: 0.02em !important; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4) !important; display: flex !important; align-items: center !important; gap: 8px !important; z-index: 9999999 !important; transform: translateY(100px) scale(0.95); opacity: 0; pointer-events: none; transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275), opacity 0.3s ease !important; }
    #cartToast.show { transform: translateY(0) scale(1) !important; opacity: 1 !important; pointer-events: auto; }
</style>
<div id="cartToast">
    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" /></svg>
    <span id="cartToastMsg">Added to bag!</span>
</div>
<script>
    window.KIOSK_PRODUCTS = {
        {% for p in (regular_products or []) + (flash_sales or []) %}
        "{{ p.id }}": {
            "id": {{ p.id }}, "name": {{ p.name|tojson }},
            "price": {{ (p.current_price if p.current_price is defined else (p.original_price if p.original_price is defined else 0)) }},
            "image": {{ (p.image or "")|tojson }}, "description": {{ (p.description or "")|tojson }},
            "attributes": {{ (p.get_attributes() or {})|tojson }}
        },
        {% endfor %}
    };
</script>
<div id="productModal" onclick="if(event.target === this) closeProductModal();">
    <div class="bg-[#14161f] border border-zinc-800 max-w-xl w-full rounded-3xl shadow-2xl relative text-white overflow-hidden flex flex-col md:flex-row max-h-[90vh]">
        <button type="button" onclick="closeProductModal()" class="absolute top-4 right-4 z-10 bg-black/60 hover:bg-black text-zinc-300 hover:text-white rounded-full w-8 h-8 flex items-center justify-center font-bold text-lg cursor-pointer transition">&times;</button>
        <div id="modalImgContainer" class="w-full md:w-1/2 bg-zinc-900 flex items-center justify-center relative min-h-[220px] md:min-h-full overflow-hidden border-b md:border-b-0 md:border-r border-zinc-800">
            <img id="modalProductImg" src="" alt="Product Preview" class="w-full h-full object-cover max-h-[300px] md:max-h-full">
            <div id="modalImgPlaceholder" class="text-zinc-500 font-mono text-xs uppercase text-center p-4" style="display:none;">NO PREVIEW AVAILABLE</div>
        </div>
        <div class="p-6 md:p-8 w-full md:w-1/2 flex flex-col justify-between overflow-y-auto">
            <div>
                <span class="text-[10px] font-mono text-amber-400 uppercase tracking-widest block mb-1">Product Details</span>
                <h3 id="modalProductName" class="font-bold text-xl text-white mb-2 tracking-tight"></h3>
                <p id="modalProductDesc" class="text-xs text-zinc-400 mb-4 leading-relaxed"></p>
                <p id="modalProductPrice" class="font-mono text-2xl font-black text-amber-400 mb-4"></p>
                <div id="modalVariantsContainer" class="space-y-3 mb-6"></div>
            </div>
            <button type="button" onclick="confirmAddToCartFromModal()" class="w-full bg-amber-500 hover:bg-amber-400 text-black font-black py-4 rounded-xl text-xs uppercase tracking-wider transition cursor-pointer shadow-lg shadow-amber-500/20">ADD TO BAG &rarr;</button>
        </div>
    </div>
</div>
<div id="cartOverlay" onclick="toggleCart()"></div>
<aside id="cartDrawer">
    <div>
        <div class="flex justify-between items-center pb-4 border-b border-zinc-800 mb-6">
            <div><h3 class="font-bold text-base uppercase tracking-wider text-white m-0">Your Shopping Bag</h3><span class="text-[10px] text-zinc-400 font-mono">Direct WhatsApp Intake</span></div>
            <button type="button" onclick="toggleCart()" class="text-xs font-mono font-bold text-zinc-400 hover:text-white cursor-pointer">&times; CLOSE</button>
        </div>
        <div id="cartItemsList" class="space-y-3 max-h-[40vh] overflow-y-auto pr-1"></div>
    </div>
    <div class="pt-6 border-t border-zinc-800">
        <div class="flex justify-between items-center mb-6 font-mono"><span class="text-xs uppercase text-zinc-400">Total:</span><span id="cartTotalPrice" class="font-black text-2xl text-amber-400">{{ (store.currency if store and store.currency else '₦') }}0.00</span></div>
        <form id="checkoutForm" onsubmit="handleCheckout(event)" class="space-y-3">
            <input type="text" id="custName" required placeholder="Your Full Name" class="w-full p-3 bg-zinc-900 border border-zinc-800 rounded-xl text-xs text-white outline-none focus:border-amber-500 transition">
            <input type="text" id="custPhone" required placeholder="WhatsApp Number" class="w-full p-3 bg-zinc-900 border border-zinc-800 rounded-xl text-xs text-white outline-none focus:border-amber-500 transition">
            <textarea id="custAddress" required placeholder="Delivery Address" rows="2" class="w-full p-3 bg-zinc-900 border border-zinc-800 rounded-xl text-xs text-white outline-none focus:border-amber-500 transition"></textarea>
            <button type="submit" id="checkoutBtn" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-black py-4 rounded-xl text-xs uppercase tracking-wider transition cursor-pointer shadow-lg">COMPLETE ORDER ON WHATSAPP &rarr;</button>
        </form>
    </div>
</aside>
<script>
    const storeSlug = {{ (store.slug if store else '')|tojson }};
    const storeCurrency = {{ (store.currency if store and store.currency else '₦')|tojson }};
    let cart = []; let currentModalProduct = null; let toastTimeout = null;
    function showCartToast(m){const t=document.getElementById('cartToast'),e=document.getElementById('cartToastMsg');if(!t||!e)return;e.innerText=m||'Added to bag!',t.classList.add('show'),toastTimeout&&clearTimeout(toastTimeout),toastTimeout=setTimeout(()=>{t.classList.remove('show')},2500)}
    function quickAddToCart(i,e){e&&(e.preventDefault(),e.stopPropagation());const p=window.KIOSK_PRODUCTS[i];if(!p)return;const x=cart.find(t=>t.product_id===p.id&&!t.variants);x?x.quantity+=1:cart.push({product_id:p.id,name:p.name,price:p.price,variants:'',quantity:1}),updateCartUI(),showCartToast(`Added ${p.name} to bag!`)}
    function openProductModal(i){const p=window.KIOSK_PRODUCTS[i];if(!p)return;currentModalProduct=p,document.getElementById('modalProductName').innerText=p.name,document.getElementById('modalProductDesc').innerText=p.description||'Premium curated quality.',document.getElementById('modalProductPrice').innerText=`${storeCurrency}${Number(p.price).toLocaleString()}`;const m=document.getElementById('modalProductImg'),h=document.getElementById('modalImgPlaceholder');p.image&&p.image!=='default_product.png'&&p.image!=='None'&&p.image!==''?(m.src=p.image,m.style.display='block',h.style.display='none',m.onerror=function(){this.style.display='none',h.style.display='block'}):(m.style.display='none',h.style.display='block');const c=document.getElementById('modalVariantsContainer');c.innerHTML='';const a=p.attributes||{};for(const[r,o]of Object.entries(a)){if(!Array.isArray(o)||0===o.length)continue;const s=document.createElement('div');s.innerHTML=`<label class='block font-mono text-[10px] uppercase text-amber-400 mb-1 font-bold'>${r}</label><select class='variant-select w-full p-2.5 bg-zinc-900 border border-zinc-800 text-white font-mono text-xs rounded-xl outline-none focus:border-amber-500' data-attr='${r}'>${o.map(t=>`<option value="${t}">${t}</option>`).join('')}</select>`,c.appendChild(s)}document.getElementById('productModal').classList.add('active')}
    function closeProductModal(){document.getElementById('productModal').classList.remove('active'),currentModalProduct=null}
    function confirmAddToCartFromModal(){if(!currentModalProduct)return;const e=[];document.querySelectorAll('.variant-select').forEach(t=>{e.push(`${t.getAttribute('data-attr')}: ${t.value}`)}),cart.push({product_id:currentModalProduct.id,name:currentModalProduct.name,price:currentModalProduct.price,variants:e.join(' | '),quantity:1}),updateCartUI(),showCartToast(`Added ${currentModalProduct.name} to bag!`),closeProductModal()}
    function filterProducts(e){const r=(e||'').toLowerCase().trim();document.querySelectorAll('.product-card, .catalog-item').forEach(e=>{const t=(e.getAttribute('data-name')||e.querySelector('.product-title')?.innerText||e.innerText||'').toLowerCase();e.style.display=t.includes(r)?'':'none'})}
    function filterCatalog(){filterProducts(document.getElementById('catalogSearchInput')?.value)}
    function toggleCart(){document.getElementById('cartDrawer').classList.toggle('open'),document.getElementById('cartOverlay').classList.toggle('active')}
    function updateCartUI(){const e=document.getElementById('cartItemsList'),r=document.getElementById('cartCountBadge'),t=document.getElementById('cartTotalPrice');r&&(r.innerText=cart.reduce((e,r)=>e+r.quantity,0));if(!e)return;e.innerHTML='';let o=0;cart.forEach((r,a)=>{o+=r.price*r.quantity;const s=document.createElement('div');s.className='flex justify-between items-start p-3 bg-zinc-900 border border-zinc-800 rounded-xl text-xs font-mono',s.innerHTML=`<div><strong class="text-white block font-bold">${r.name}</strong>${r.variants?`<span class="text-[10px] text-amber-400 block">${r.variants}</span>`:''}<span class="text-emerald-400 font-bold mt-1 block">${storeCurrency}${Number(r.price).toLocaleString()}</span></div><button type="button" onclick="cart.splice(${a}, 1); updateCartUI();" class="text-rose-400 hover:text-rose-300 font-bold ml-3 text-base cursor-pointer">&times;</button>`,e.appendChild(s)}),t&&(t.innerText=`${storeCurrency}${o.toLocaleString()}`)}
    async function handleCheckout(e){e.preventDefault();if(0===cart.length)return void alert('Your bag is empty.');const r=document.getElementById('checkoutBtn'),t=r.innerText;r.innerText='GENERATING RECEIPT...',r.disabled=!0;const o={customer_name:document.getElementById('custName').value,customer_phone:document.getElementById('custPhone').value,delivery_address:document.getElementById('custAddress').value,cart:cart};try{const e=await fetch(`/${storeSlug}/checkout`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(o)}),a=await e.json();'success'===a.status?(cart=[],updateCartUI(),toggleCart(),window.location.href=a.whatsapp_url):(alert(a.message||'Error creating order.'),r.innerText=t,r.disabled=!1)}catch(e){alert('Connection error.'),r.innerText=t,r.disabled=!1}}
</script>
"""

# ==============================================================================
# 🏛️ THE ELITE MASTER FALLBACK TEMPLATE (Pinterest-Worthy Design)
# Strictly preserves all backend logic while delivering award-winning UI/UX.
# ==============================================================================
MASTER_FALLBACK_TEMPLATE = """<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ store.name }} // Marketplace</title>
    <meta property="og:title" content="{{ store.name }}">
    <meta property="og:description" content="{% if store.show_public_stats %}Over {{ '{:,}'.format(store.views_count) }} visits • Verified Merchant • Shop our official catalog.{% else %}{{ store.bio }}{% endif %}">
    <meta property="og:image" content="{{ url_for('static', filename='uploads/logos/' + store.logo, _external=True) if not store.logo.startswith('http') else store.logo }}">
    <meta property="og:type" content="website">
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    
    <style>
        body { 
            background-color: #09090b; 
            color: #fafafa; 
            font-family: 'Inter', sans-serif; 
            {% if store.background_image %}
            background-image: linear-gradient(to bottom, rgba(9, 9, 11, 0.92), rgba(9, 9, 11, 0.98)), url('{{ store.background_image if store.background_image.startswith("http") else url_for("static", filename="uploads/backgrounds/" + store.background_image) }}');
            background-size: cover; background-attachment: fixed; background-position: center;
            {% endif %} 
        }
        .font-display { font-family: 'Playfair Display', serif; }
        .glass-panel { background: rgba(24, 24, 27, 0.6); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
        .ad-corner-tag { position: absolute; top: 12px; right: 12px; background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(4px); color: #fff; padding: 4px 10px; border-radius: 99px; font-family: 'Inter', sans-serif; font-size: 10px; font-weight: 600; letter-spacing: 0.05em; border: 1px solid rgba(255, 255, 255, 0.1); pointer-events: none; }
        .hide-scrollbar::-webkit-scrollbar { display: none; }
        .hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
    </style>
</head>
<body class="min-h-screen flex flex-col antialiased selection:bg-amber-500/30 selection:text-amber-200">

    <!-- Premium Glass Header -->
    <header class="fixed top-0 left-0 w-full z-40 glass-panel border-b border-white/5 transition-all duration-300">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between gap-4">
            <a href="/{{ store.slug }}" class="flex items-center gap-3 group flex-shrink-0">
                {% if store.logo and store.logo != 'default_logo.png' %}
                    <img src="{{ store.logo if store.logo.startswith('http') else url_for('static', filename='uploads/logos/' + store.logo) }}" class="h-10 w-10 object-contain rounded-full border border-white/10 group-hover:border-amber-500/50 transition-colors duration-300">
                {% else %}
                    <div class="h-10 w-10 rounded-full bg-gradient-to-br from-amber-600 to-amber-800 flex items-center justify-center text-white font-display font-bold text-lg shadow-lg border border-amber-500/20">
                        {{ (store.name[0] if store and store.name else 'M') }}
                    </div>
                {% endif %}
                <div class="hidden sm:block">
                    <h1 class="font-display text-xl font-bold text-white tracking-tight group-hover:text-amber-400 transition-colors">{{ store.name }}</h1>
                    <p class="text-[11px] text-zinc-400 font-medium tracking-wide uppercase">{{ store.bio[:30] }}{% if store.bio|length > 30 %}...{% endif %}</p>
                </div>
            </a>
            
            <button onclick="toggleCart()" class="flex items-center gap-2.5 bg-white text-zinc-950 hover:bg-zinc-200 px-5 py-2.5 rounded-full font-semibold text-sm transition-all duration-300 shadow-lg shadow-white/5 hover:shadow-white/10 hover:-translate-y-0.5">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" /></svg>
                <span>BAG</span>
                <span id="cartCountBadge" class="bg-zinc-950 text-white px-2 py-0.5 rounded-full font-bold text-[0.65rem]">0</span>
            </button>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-16 w-full flex-grow">
        
        <!-- Hero Section -->
        {% if store.is_section_active('hero') and store.hero_image %}
        <div class="mb-16 relative group">
            <div class="absolute inset-0 bg-gradient-to-t from-zinc-950 via-transparent to-transparent z-10 rounded-3xl"></div>
            <img src="{{ store.hero_image if store.hero_image.startswith('http') else url_for('static', filename='uploads/heroes/' + store.hero_image) }}" 
                 alt="Hero Showcase" class="w-full h-64 md:h-96 object-cover rounded-3xl shadow-2xl shadow-black/50 border border-white/5 group-hover:scale-[1.01] transition-transform duration-700 ease-out">
            <div class="absolute bottom-0 left-0 z-20 p-6 md:p-10">
                <h2 class="font-display text-3xl md:text-5xl font-bold text-white mb-2 tracking-tight drop-shadow-lg">{{ store.name }}</h2>
                <p class="text-zinc-300 text-sm md:text-base max-w-lg drop-shadow-md">{{ store.bio }}</p>
            </div>
        </div>
        {% else %}
        <div class="mb-16 text-center py-12">
            <h2 class="font-display text-4xl md:text-6xl font-bold text-white mb-4 tracking-tight">{{ store.name }}</h2>
            <p class="text-zinc-400 text-lg max-w-2xl mx-auto leading-relaxed">{{ store.bio }}</p>
        </div>
        {% endif %}

        <!-- Premium Ad Slot #1 -->
        {% if store.is_section_active('ads') and 1 in ad_slots %}
        <div class="mb-16 relative group">
            <span class="ad-corner-tag">SPONSORED</span>
            <a href="/ad/click/{{ ad_slots[1].id }}" target="_blank" class="block w-full overflow-hidden rounded-2xl border border-white/10 shadow-2xl shadow-black/40">
                <img src="{{ ad_slots[1].banner_image if ad_slots[1].banner_image.startswith('http') else url_for('static', filename='uploads/ads/' + ad_slots[1].banner_image) }}" 
                     alt="Sponsor Ad" class="w-full h-32 md:h-48 object-cover group-hover:scale-[1.02] transition-transform duration-500 ease-out">
            </a>
        </div>
        {% endif %}

        <!-- Flash Sales Section -->
        {% if store.is_section_active('flash_sales') and flash_sales %}
        <section class="mb-20">
            <div class="flex items-center justify-between mb-8">
                <div class="flex items-center gap-3">
                    <div class="relative flex h-3 w-3">
                        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-500 opacity-75"></span>
                        <span class="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
                    </div>
                    <h3 class="font-display text-2xl md:text-3xl font-bold text-white tracking-tight">Flash Deals</h3>
                </div>
                <span class="hidden md:inline-block text-xs font-medium text-zinc-500 uppercase tracking-widest border border-zinc-800 px-3 py-1 rounded-full">Limited Quantity</span>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {% for p in flash_sales %}
                <div class="product-card group bg-zinc-900/50 border border-white/5 rounded-2xl overflow-hidden hover:border-amber-500/30 hover:shadow-2xl hover:shadow-amber-900/10 transition-all duration-300 flex flex-col" data-name="{{ p.name }}">
                    <div onclick="openProductModal({{ p.id }})" class="relative aspect-[4/5] bg-zinc-800 overflow-hidden cursor-pointer">
                        <img src="{{ p.image if p.image.startswith('http') else url_for('static', filename='uploads/products/' + p.image) }}" alt="{{ p.name }}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 ease-out">
                        <div class="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors duration-300 flex items-center justify-center">
                            <span class="opacity-0 group-hover:opacity-100 bg-white/90 backdrop-blur text-zinc-950 text-xs font-bold px-4 py-2 rounded-full transform translate-y-4 group-hover:translate-y-0 transition-all duration-300">Quick View</span>
                        </div>
                    </div>
                    <div class="p-5 flex flex-col flex-grow">
                        <h4 class="font-medium text-base text-white mb-1 line-clamp-1 group-hover:text-amber-400 transition-colors">{{ p.name }}</h4>
                        <p class="text-xs text-zinc-500 mb-4 line-clamp-2 leading-relaxed">{{ p.description }}</p>
                        <div class="mt-auto flex items-end justify-between">
                            <div>
                                <span class="line-through text-zinc-600 text-xs font-medium block">{{ store.currency }}{{ "{:,.2f}".format(p.original_price) }}</span>
                                <span class="font-bold text-xl text-amber-400">{{ store.currency }}{{ "{:,.2f}".format(p.current_price) }}</span>
                            </div>
                            <button type="button" onclick="openProductModal({{ p.id }})" class="bg-white text-zinc-950 hover:bg-amber-400 hover:text-black font-semibold text-xs px-4 py-2.5 rounded-xl transition-all duration-300">SELECT</button>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </section>
        {% endif %}

        <!-- Catalog Header & Search -->
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-10 pb-6 border-b border-white/5">
            <div>
                <h3 class="font-display text-3xl font-bold text-white tracking-tight">Curated Catalog</h3>
                <p class="text-sm text-zinc-500 mt-1">Explore our exclusive collection of premium items.</p>
            </div>
            <div class="relative w-full md:w-80">
                <input type="text" id="catalogSearchInput" onkeyup="filterCatalog()" placeholder="Search products..." 
                       class="w-full pl-10 pr-4 py-3 bg-zinc-900/50 border border-white/10 rounded-xl text-sm text-white placeholder-zinc-500 outline-none focus:border-amber-500/50 focus:ring-1 focus:ring-amber-500/50 transition-all">
                <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
            </div>
        </div>

        <!-- Regular Products Grid -->
        <section class="mb-20">
            <div id="catalogGrid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {% for p in regular_products %}
                <div class="catalog-item product-card group bg-zinc-900/50 border border-white/5 rounded-2xl overflow-hidden hover:border-white/10 hover:shadow-2xl hover:shadow-black/40 transition-all duration-300 flex flex-col" data-name="{{ p.name }}">
                    <div onclick="openProductModal({{ p.id }})" class="relative aspect-[4/5] bg-zinc-800 overflow-hidden cursor-pointer">
                        <img src="{{ p.image if p.image.startswith('http') else url_for('static', filename='uploads/products/' + p.image) }}" alt="{{ p.name }}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 ease-out">
                        <div class="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors duration-300 flex items-center justify-center">
                            <span class="opacity-0 group-hover:opacity-100 bg-white/90 backdrop-blur text-zinc-950 text-xs font-bold px-4 py-2 rounded-full transform translate-y-4 group-hover:translate-y-0 transition-all duration-300">Quick View</span>
                        </div>
                    </div>
                    <div class="p-5 flex flex-col flex-grow">
                        <h4 class="product-title font-medium text-base text-white mb-1 line-clamp-1 group-hover:text-zinc-300 transition-colors">{{ p.name }}</h4>
                        <p class="text-xs text-zinc-500 mb-4 line-clamp-2 leading-relaxed">{{ p.description }}</p>
                        <div class="mt-auto">
                            <div class="mb-4">
                                {% if p.has_discount %}
                                    <span class="line-through text-zinc-600 text-xs font-medium block">{{ store.currency }}{{ "{:,.2f}".format(p.original_price) }}</span>
                                    <span class="font-bold text-lg text-white">{{ store.currency }}{{ "{:,.2f}".format(p.discount_price) }}</span>
                                {% else %}
                                    <span class="font-bold text-lg text-white">{{ store.currency }}{{ "{:,.2f}".format(p.original_price) }}</span>
                                {% endif %}
                                
                                {% if p.is_unlimited_stock %}
                                    <span class="text-[10px] text-emerald-500 font-semibold flex items-center gap-1.5 mt-2">
                                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> In Stock
                                    </span>
                                {% else %}
                                    <span class="text-[10px] text-zinc-500 font-medium flex items-center gap-1.5 mt-2">
                                        <span class="w-1.5 h-1.5 rounded-full bg-zinc-600"></span> {{ p.stock }} units left
                                    </span>
                                {% endif %}
                            </div>

                            {% if p.is_available %}
                                <button type="button" onclick="openProductModal({{ p.id }})" class="w-full bg-zinc-100 hover:bg-white text-zinc-950 font-semibold text-sm py-3 rounded-xl transition-all duration-300 hover:-translate-y-0.5">
                                    View & Order
                                </button>
                            {% else %}
                                <button disabled class="w-full py-3 bg-zinc-800/50 text-zinc-600 font-medium text-sm rounded-xl cursor-not-allowed border border-white/5">
                                    Out of Stock
                                </button>
                            {% endif %}
                        </div>
                    </div>
                </div>
                {% else %}
                <div class="col-span-full py-20 text-center border border-dashed border-white/10 rounded-2xl">
                    <p class="text-zinc-500 font-medium">No regular items available in the catalog right now.</p>
                </div>
                {% endfor %}
            </div>
        </section>

        <!-- Premium Ad Slot #3 -->
        {% if store.is_section_active('ads') and 3 in ad_slots %}
        <div class="mt-10 relative group">
            <span class="ad-corner-tag">SPONSORED</span>
            <a href="/ad/click/{{ ad_slots[3].id }}" target="_blank" class="block w-full overflow-hidden rounded-2xl border border-white/10 shadow-2xl shadow-black/40">
                <img src="{{ ad_slots[3].banner_image if ad_slots[3].banner_image.startswith('http') else url_for('static', filename='uploads/ads/' + ad_slots[3].banner_image) }}" 
                     alt="Sponsor Ad" class="w-full h-32 md:h-48 object-cover group-hover:scale-[1.02] transition-transform duration-500 ease-out">
            </a>
        </div>
        {% endif %}

    </main>

    <footer class="border-t border-white/5 bg-zinc-950 py-12 text-center">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <p class="text-zinc-600 text-sm">Made with <span class="text-amber-500">♥</span> by <a href="/" class="text-zinc-400 hover:text-white font-semibold transition-colors">Marketplace</a> • Powered by Techlite</p>
        </div is the exact backend logic, URL routing, and data structures provided in the baseline.\n\n'
        'STRICT PRESERVATION RULES:\n'
        '1. NEVER alter, remove, or misspell ANY Jinja2 {{ }} or {% %} tags.\n'
        '2. NEVER change the image URL logic: `{{ url if url.startswith(\'http\') else url_for(...) }}`.\n'
        '3. NEVER change the Ad Slot dictionary logic: `{% if 1 in ad_slots %}` and `ad_slots[1].banner_image`.\n'
        '4. NEVER change the product loops or variable names (`regular_products`, `flash_sales`).\n'
        '5. DO NOT output any `<script>` tags. DO NOT output the `<div id="productModal">` or `<aside id="cartDrawer">`. The system injects a bulletproof cart and modal engine automatically.\n'
        '6. Ensure the header has a button with `onclick="toggleCart()"` and `<span id="cartCountBadge">0</span>`.\n'
        '7. Ensure products have `<button onclick="openProductModal({{ p.id }})">`.\n'
        '8. Output ONLY raw HTML. No markdown backticks.\n\n'
        'ELITE DESIGN PRINCIPLES TO APPLY:\n'
        '- Use a sophisticated, premium color palette (e.g., deep zinc/stone backgrounds `bg-zinc-950`, subtle borders `border-white/10`, and elegant accents like `amber-400` or `emerald-500`).\n'
        '- Typography: Pair a clean sans-serif (Inter) for UI with an elegant serif (Playfair Display) for headings. Use `tracking-tight` for large headings.\n'
        '- Cards: Use `aspect-[4/5]` for product images, `rounded-2xl`, subtle background colors (`bg-zinc-900/50`), and smooth hover effects (`hover:-translate-y-1`, `hover:shadow-2xl`, `group-hover:scale-105` for images).\n'
        '- Buttons: Sleek, modern, with smooth transitions (`transition-all duration-300`).\n'
        '- Spacing: Use generous whitespace (`mb-16`, `py-12`, `gap-6`) to let the design breathe and feel expensive.\n'
        '- Glassmorphism: Use `backdrop-blur-xl` and semi-transparent backgrounds for headers or floating elements.\n\n'
        'MASTER BASELINE JINJA2 LOGIC (You MUST use these exact structures for the backend data):\n'
        '---\n'
        '<!-- LOGO -->\n'
        '{% if store.logo and store.logo != \'default_logo.png\' %}\n'
        '    <img src="{{ store.logo if store.logo.startswith(\'http\') else url_for(\'static\', filename=\'uploads/logos/\' + store.logo) }}">\n'
        '{% endif %}\n\n'
        '<!-- AD SLOTS (Dictionary format: 1 in ad_slots, 3 in ad_slots) -->\n'
        '{% if store.is_section_active(\'ads\') and 1 in ad_slots %}\n'
        '    <a href="/ad/click/{{ ad_slots[1].id }}" target="_blank">\n'
        '        <img src="{{ ad_slots[1].banner_image if ad_slots[1].banner_image.startswith(\'http\') else url_for(\'static\', filename=\'uploads/ads/\' + ad_slots[1].banner_image) }}">\n'
        '    </a>\n'
        '{% endif %}\n\n'
        '<!-- HERO SECTION -->\n'
        '{% if store.is_section_active(\'hero\') and store.hero_image %}\n'
        '    <img src="{{ store.hero_image if store.hero_image.startswith(\'http\') else url_for(\'static\', filename=\'uploads/heroes/\' + store.hero_image) }}">\n'
        '{% endif %}\n\n'
        '<!-- FLASH SALES -->\n'
        '{% if store.is_section_active(\'flash_sales\') and flash_sales %}\n'
        '    {% for p in flash_sales %}\n'
        '        <img src="{{ p.image if p.image.startswith(\'http\') else url_for(\'static\', filename=\'uploads/products/\' + p.image) }}">\n'
        '        <h4>{{ p.name }}</h4>\n'
        '        <p>{{ p.description }}</p>\n'
        '        <span>{{ store.currency }}{{ "{:,.2f}".format(p.current_price) }}</span>\n'
        '        <button onclick="openProductModal({{ p.id }})">SELECT & ORDER</button>\n'
        '    {% endfor %}\n'
        '{% endif %}\n\n'
        '<!-- REGULAR PRODUCTS -->\n'
        '{% for p in regular_products %}\n'
        '    <img src="{{ p.image if p.image.startswith(\'http\') else url_for(\'static\', filename=\'uploads/products/\' + p.image) }}">\n'
        '    <h4>{{ p.name }}</h4>\n'
        '    <p>{{ p.description }}</p>\n'
        '    {% if p.has_discount %}\n'
        '        <span>{{ store.currency }}{{ "{:,.2f}".format(p.original_price) }}</span>\n'
        '        <span>{{ store.currency }}{{ "{:,.2f}".format(p.discount_price) }}</span>\n'
        '    {% else %}\n'
        '        <span>{{ store.currency }}{{ "{:,.2f}".format(p.original_price) }}</span>\n'
        '    {% endif %}\n'
        '    <button onclick="openProductModal({{ p.id }})">VIEW & ORDER</button>\n'
        '{% endfor %}\n'
        '---\n\n'
        'TASK: Take the "Design Instructions" and apply beautiful, modern, Pinterest-tier Tailwind CSS classes to the HTML structure. Use the Master Baseline Jinja2 Logic above to populate the data. Remember: DO NOT output the cart/modal HTML or JS. Output ONLY the visual storefront HTML.'
    )

    # 1. Primary: Google Gemini
    gemini_key = (os.environ.get('AI_API_KEY') or '').strip()
    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model_name = os.environ.get('GEMINI_MODEL', 'gemini-2.0-flash')
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(system_instruction)
            raw_text = response.text if response and hasattr(response, 'text') else ""
            raw_html = clean_html_fences(raw_text)
            if raw_html:
                print(f"✨ [AI BUILDER] Bespoke template generated via Primary Gemini ({model_name})!", flush=True)
                return inject_bulletproof_chassis(raw_html, kiosk_name, bio, primary_meta_img)
        except Exception as e:
            print(f"⚠️ [AI BUILDER] Gemini Tier 1 notice: {e}", flush=True)

    # 2. Backup: OpenRouter
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

    # 3. Tier 3: Master Fallback (Guaranteed 100% Fail-Safe & Elite Design)
    print(f"🛡️ [AI BUILDER] Activating Elite Master Marketplace Fallback for '{kiosk_name}'.", flush=True)
    fallback_html = get_curated_fallback_template(kiosk_name, bio, prompt)
    return inject_bulletproof_chassis(fallback_html, kiosk_name, bio, primary_meta_img)
