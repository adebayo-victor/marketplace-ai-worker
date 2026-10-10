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
    <div class="bg-[#14161f] border border-stone-800 max-w-xl w-full rounded-3xl shadow-2xl relative text-white overflow-hidden flex flex-col md:flex-row max-h-[90vh]">
        <button type="button" onclick="closeProductModal()" class="absolute top-4 right-4 z-10 bg-black/60 hover:bg-black text-stone-300 hover:text-white rounded-full w-8 h-8 flex items-center justify-center font-bold text-lg cursor-pointer transition">&times;</button>
        <div id="modalImgContainer" class="w-full md:w-1/2 bg-stone-900 flex items-center justify-center relative min-h-[220px] md:min-h-full overflow-hidden border-b md:border-b-0 md:border-r border-stone-800">
            <img id="modalProductImg" src="" alt="Product Preview" class="w-full h-full object-cover max-h-[300px] md:max-h-full">
            <div id="modalImgPlaceholder" class="text-stone-500 font-mono text-xs uppercase text-center p-4" style="display:none;">NO PREVIEW AVAILABLE</div>
        </div>
        <div class="p-6 md:p-8 w-full md:w-1/2 flex flex-col justify-between overflow-y-auto">
            <div>
                <span class="text-[10px] font-mono text-amber-400 uppercase tracking-widest block mb-1">Product Details</span>
                <h3 id="modalProductName" class="font-bold text-xl text-white mb-2 tracking-tight"></h3>
                <p id="modalProductDesc" class="text-xs text-stone-400 mb-4 leading-relaxed"></p>
                <p id="modalProductPrice" class="font-mono text-2xl font-black text-amber-400 mb-4"></p>
                <div id="modalVariantsContainer" class="space-y-3 mb-6"></div>
            </div>
            <button type="button" onclick="confirmAddToCartFromModal()" class="w-full bg-amber-400 hover:bg-amber-300 text-black font-black py-4 rounded-xl text-xs uppercase tracking-wider transition cursor-pointer shadow-lg">ADD TO BAG &rarr;</button>
        </div>
    </div>
</div>
<div id="cartOverlay" onclick="toggleCart()"></div>
<aside id="cartDrawer">
    <div>
        <div class="flex justify-between items-center pb-4 border-b border-stone-800 mb-6">
            <div><h3 class="font-bold text-base uppercase tracking-wider text-white m-0">Your Shopping Bag</h3><span class="text-[10px] text-stone-400 font-mono">Direct WhatsApp Intake</span></div>
            <button type="button" onclick="toggleCart()" class="text-xs font-mono font-bold text-stone-400 hover:text-white cursor-pointer">&times; CLOSE</button>
        </div>
        <div id="cartItemsList" class="space-y-3 max-h-[40vh] overflow-y-auto pr-1"></div>
    </div>
    <div class="pt-6 border-t border-stone-800">
        <div class="flex justify-between items-center mb-6 font-mono"><span class="text-xs uppercase text-stone-400">Total:</span><span id="cartTotalPrice" class="font-black text-2xl text-amber-400">{{ (store.currency if store and store.currency else '₦') }}0.00</span></div>
        <form id="checkoutForm" onsubmit="handleCheckout(event)" class="space-y-3">
            <input type="text" id="custName" required placeholder="Your Full Name" class="w-full p-3 bg-[#181a24] border border-stone-800 rounded-xl text-xs text-white outline-none focus:border-amber-400">
            <input type="text" id="custPhone" required placeholder="WhatsApp Number" class="w-full p-3 bg-[#181a24] border border-stone-800 rounded-xl text-xs text-white outline-none focus:border-amber-400">
            <textarea id="custAddress" required placeholder="Delivery Address" rows="2" class="w-full p-3 bg-[#181a24] border border-stone-800 rounded-xl text-xs text-white outline-none focus:border-amber-400"></textarea>
            <button type="submit" id="checkoutBtn" class="w-full bg-[#16a34a] hover:bg-[#15803d] text-white font-black py-4 rounded-xl text-xs uppercase tracking-wider transition cursor-pointer shadow-lg">COMPLETE ORDER ON WHATSAPP &rarr;</button>
        </form>
    </div>
</aside>
<script>
    const storeSlug = {{ (store.slug if store else '')|tojson }};
    const storeCurrency = {{ (store.currency if store and store.currency else '₦')|tojson }};
    let cart = []; let currentModalProduct = null; let toastTimeout = null;
    function showCartToast(m){const t=document.getElementById('cartToast'),e=document.getElementById('cartToastMsg');if(!t||!e)return;e.innerText=m||'Added to bag!',t.classList.add('show'),toastTimeout&&clearTimeout(toastTimeout),toastTimeout=setTimeout(()=>{t.classList.remove('show')},2500)}
    function quickAddToCart(i,e){e&&(e.preventDefault(),e.stopPropagation());const p=window.KIOSK_PRODUCTS[i];if(!p)return;const x=cart.find(t=>t.product_id===p.id&&!t.variants);x?x.quantity+=1:cart.push({product_id:p.id,name:p.name,price:p.price,variants:'',quantity:1}),updateCartUI(),showCartToast(`Added ${p.name} to bag!`)}
    function openProductModal(i){const p=window.KIOSK_PRODUCTS[i];if(!p)return;currentModalProduct=p,document.getElementById('modalProductName').innerText=p.name,document.getElementById('modalProductDesc').innerText=p.description||'Premium curated quality.',document.getElementById('modalProductPrice').innerText=`${storeCurrency}${Number(p.price).toLocaleString()}`;const m=document.getElementById('modalProductImg'),h=document.getElementById('modalImgPlaceholder');p.image&&p.image!=='default_product.png'&&p.image!=='None'&&p.image!==''?(m.src=p.image,m.style.display='block',h.style.display='none',m.onerror=function(){this.style.display='none',h.style.display='block'}):(m.style.display='none',h.style.display='block');const c=document.getElementById('modalVariantsContainer');c.innerHTML='';const a=p.attributes||{};for(const[r,o]of Object.entries(a)){if(!Array.isArray(o)||0===o.length)continue;const s=document.createElement('div');s.innerHTML=`<label class='block font-mono text-[10px] uppercase text-amber-400 mb-1 font-bold'>${r}</label><select class='variant-select w-full p-2.5 bg-[#181a24] border border-stone-800 text-white font-mono text-xs rounded-xl outline-none focus:border-amber-400' data-attr='${r}'>${o.map(t=>`<option value="${t}">${t}</option>`).join('')}</select>`,c.appendChild(s)}document.getElementById('productModal').classList.add('active')}
    function closeProductModal(){document.getElementById('productModal').classList.remove('active'),currentModalProduct=null}
    function confirmAddToCartFromModal(){if(!currentModalProduct)return;const e=[];document.querySelectorAll('.variant-select').forEach(t=>{e.push(`${t.getAttribute('data-attr')}: ${t.value}`)}),cart.push({product_id:currentModalProduct.id,name:currentModalProduct.name,price:currentModalProduct.price,variants:e.join(' | '),quantity:1}),updateCartUI(),showCartToast(`Added ${currentModalProduct.name} to bag!`),closeProductModal()}
    function filterProducts(e){const r=(e||'').toLowerCase().trim();document.querySelectorAll('.product-card, .catalog-item').forEach(e=>{const t=(e.getAttribute('data-name')||e.querySelector('.product-title')?.innerText||e.innerText||'').toLowerCase();e.style.display=t.includes(r)?'':'none'})}
    function filterCatalog(){filterProducts(document.getElementById('catalogSearchInput')?.value)}
    function toggleCart(){document.getElementById('cartDrawer').classList.toggle('open'),document.getElementById('cartOverlay').classList.toggle('active')}
    function updateCartUI(){const e=document.getElementById('cartItemsList'),r=document.getElementById('cartCountBadge'),t=document.getElementById('cartTotalPrice');r&&(r.innerText=cart.reduce((e,r)=>e+r.quantity,0));if(!e)return;e.innerHTML='';let o=0;cart.forEach((r,a)=>{o+=r.price*r.quantity;const s=document.createElement('div');s.className='flex justify-between items-start p-3 bg-[#181a24] border border-stone-800 rounded-xl text-xs font-mono',s.innerHTML=`<div><strong class="text-white block font-bold">${r.name}</strong>${r.variants?`<span class="text-[10px] text-amber-400 block">${r.variants}</span>`:''}<span class="text-emerald-400 font-bold mt-1 block">${storeCurrency}${Number(r.price).toLocaleString()}</span></div><button type="button" onclick="cart.splice(${a}, 1); updateCartUI();" class="text-rose-400 hover:text-rose-300 font-bold ml-3 text-base cursor-pointer">&times;</button>`,e.appendChild(s)}),t&&(t.innerText=`${storeCurrency}${o.toLocaleString()}`)}
    async function handleCheckout(e){e.preventDefault();if(0===cart.length)return void alert('Your bag is empty.');const r=document.getElementById('checkoutBtn'),t=r.innerText;r.innerText='GENERATING RECEIPT...',r.disabled=!0;const o={customer_name:document.getElementById('custName').value,customer_phone:document.getElementById('custPhone').value,delivery_address:document.getElementById('custAddress').value,cart:cart};try{const e=await fetch(`/${storeSlug}/checkout`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(o)}),a=await e.json();'success'===a.status?(cart=[],updateCartUI(),toggleCart(),window.location.href=a.whatsapp_url):(alert(a.message||'Error creating order.'),r.innerText=t,r.disabled=!1)}catch(e){alert('Connection error.'),r.innerText=t,r.disabled=!1}}
</script>
"""

# ==============================================================================
# 🏛️ THE ELITE MASTER FALLBACK TEMPLATE (Pinterest/Awwwards Level)
# Preserves 100% of your backend logic, but with stunning, modern design.
# ==============================================================================
MASTER_FALLBACK_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
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
        body { background-color: #fafafa; color: #18181b; font-family: 'Inter', sans-serif; margin: 0;
            {% if store.background_image %}
            background-image: linear-gradient(rgba(250, 250, 250, 0.92), rgba(250, 250, 250, 0.92)), url('{{ store.background_image if store.background_image.startswith("http") else url_for("static", filename="uploads/backgrounds/" + store.background_image) }}');
            background-size: cover; background-attachment: fixed; background-position: center;
            {% endif %} }
        .font-serif { font-family: 'Playfair Display', serif; }
        .ad-corner-tag { position: absolute; top: 12px; right: 12px; background: rgba(0, 0, 0, 0.7); color: #fff; padding: 4px 10px; border-radius: 6px; font-family: 'Inter', sans-serif; font-size: 10px; font-weight: 700; letter-spacing: 1px; backdrop-filter: blur(4px); border: 1px solid rgba(255, 255, 255, 0.15); pointer-events: none; }
    </style>
</head>
<body class="min-h-screen flex flex-col justify-between antialiased">
    <header class="bg-white/80 backdrop-blur-md border-b border-stone-100 py-5 px-6 sticky top-0 z-40 transition-all duration-300">
        <div class="max-w-7xl mx-auto flex items-center justify-between">
            <div class="flex items-center gap-4">
                {% if store.logo and store.logo != 'default_logo.png' %}
                    <img src="{{ store.logo if store.logo.startswith('http') else url_for('static', filename='uploads/logos/' + store.logo) }}" class="h-11 w-11 object-contain rounded-full border border-stone-100 shadow-sm">
                {% else %}
                    <div class="h-11 w-11 rounded-full bg-stone-900 flex items-center justify-center text-white font-serif font-bold text-lg shadow-md">{{ (store.name[0] if store and store.name else 'M') }}</div>
                {% endif %}
                <div>
                    <a href="/{{ store.slug }}" class="font-serif font-bold text-xl text-stone-900 tracking-tight">{{ store.name }}</a>
                    <p class="text-stone-500 text-xs font-medium m-0">{{ store.bio }}</p>
                </div>
            </div>
            <button onclick="toggleCart()" class="flex items-center gap-2 bg-stone-900 hover:bg-stone-800 text-white px-5 py-2.5 rounded-xl font-semibold text-sm transition-all duration-300 shadow-lg hover:shadow-xl cursor-pointer">
                <span>BAG</span>
                <span id="cartCountBadge" class="bg-white text-stone-900 px-2 py-0.5 rounded-full font-bold text-[0.65rem]">0</span>
            </button>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-6 py-12 w-full flex-grow">
        {% if store.is_section_active('ads') and 1 in ad_slots %}
        <div class="mb-12 relative group">
            <span class="ad-corner-tag">AD</span>
            <a href="/ad/click/{{ ad_slots[1].id }}" target="_blank" class="block w-full overflow-hidden rounded-2xl border border-stone-200 shadow-sm">
                <img src="{{ ad_slots[1].banner_image if ad_slots[1].banner_image.startswith('http') else url_for('static', filename='uploads/ads/' + ad_slots[1].banner_image) }}" alt="Sponsor Ad" class="w-full h-32 md:h-40 object-cover group-hover:scale-[1.02] transition-transform duration-500">
            </a>
        </div>
        {% endif %}

        {% if store.is_section_active('hero') and store.hero_image %}
        <div class="mb-16">
            <img src="{{ store.hero_image if store.hero_image.startswith('http') else url_for('static', filename='uploads/heroes/' + store.hero_image) }}" alt="Hero Showcase" class="w-full h-64 md:h-96 object-cover rounded-3xl shadow-xl border border-stone-100">
        </div>
        {% endif %}

        {% if store.is_section_active('flash_sales') and flash_sales %}
        <section class="mb-20">
            <div class="flex items-center gap-3 mb-8">
                <span class="bg-red-50 text-red-600 px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider border border-red-100">🔥 Flash Deals</span>
                <span class="text-stone-500 text-sm font-medium">Limited quantity promotions</span>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
                {% for p in flash_sales %}
                <div class="product-card bg-white rounded-2xl border border-stone-100 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300 overflow-hidden group flex flex-col" data-name="{{ p.name }}">
                    <div class="aspect-[4/5] bg-stone-100 overflow-hidden relative cursor-pointer" onclick="openProductModal({{ p.id }})">
                        <img src="{{ p.image if p.image.startswith('http') else url_for('static', filename='uploads/products/' + p.image) }}" alt="{{ p.name }}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500">
                    </div>
                    <div class="p-6 flex flex-col flex-grow">
                        <h4 class="font-serif font-bold text-lg text-stone-900 mb-1 tracking-tight cursor-pointer hover:text-stone-600 transition" onclick="openProductModal({{ p.id }})">{{ p.name }}</h4>
                        <p class="text-stone-500 text-sm mb-5 line-clamp-2 leading-relaxed">{{ p.description }}</p>
                        <div class="mt-auto flex items-center justify-between pt-4 border-t border-stone-100">
                            <div>
                                <span class="line-through text-stone-400 text-xs font-medium block">{{ store.currency }}{{ "{:,.2f}".format(p.original_price) }}</span>
                                <span class="font-bold text-xl text-red-600">{{ store.currency }}{{ "{:,.2f}".format(p.current_price) }}</span>
                            </div>
                            <button type="button" onclick="openProductModal({{ p.id }})" class="bg-stone-900 text-white px-5 py-2.5 rounded-xl text-sm font-semibold hover:bg-stone-800 transition-all duration-300 shadow-md cursor-pointer">Select</button>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </section>
        {% endif %}

        <div class="flex flex-wrap items-center justify-between gap-4 mb-10 pb-6 border-b border-stone-200">
            <div>
                <h3 class="font-serif text-2xl font-bold text-stone-900 tracking-tight m-0">Catalog</h3>
                <p class="text-stone-500 text-sm m-0">Freshly prepared & available items</p>
            </div>
            <input type="text" id="catalogSearchInput" onkeyup="filterCatalog()" placeholder="Search products..." class="px-4 py-3 border border-stone-200 text-sm rounded-xl bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-stone-900/10 focus:border-stone-900 transition-all w-64">
        </div>

        <section class="mb-20">
            <div id="catalogGrid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
                {% for p in regular_products %}
                <div class="catalog-item product-card bg-white rounded-2xl border border-stone-100 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300 overflow-hidden group flex flex-col" data-name="{{ p.name }}">
                    <div class="aspect-[4/5] bg-stone-100 overflow-hidden relative cursor-pointer" onclick="openProductModal({{ p.id }})">
                        <img src="{{ p.image if p.image.startswith('http') else url_for('static', filename='uploads/products/' + p.image) }}" alt="{{ p.name }}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500">
                    </div>
                    <div class="p-6 flex flex-col flex-grow">
                        <h4 class="product-title font-serif font-bold text-lg text-stone-900 mb-1 tracking-tight cursor-pointer hover:text-stone-600 transition" onclick="openProductModal({{ p.id }})">{{ p.name }}</h4>
                        <p class="text-stone-500 text-sm mb-5 line-clamp-2 leading-relaxed">{{ p.description }}</p>
                        <div class="mt-auto pt-4 border-t border-stone-100">
                            <div class="flex items-baseline gap-2 mb-4">
                                {% if p.has_discount %}
                                    <span class="line-through text-stone-400 text-xs font-medium">{{ store.currency }}{{ "{:,.2f}".format(p.original_price) }}</span>
                                    <span class="font-bold text-xl text-stone-900">{{ store.currency }}{{ "{:,.2f}".format(p.discount_price) }}</span>
                                {% else %}
                                    <span class="font-bold text-xl text-stone-900">{{ store.currency }}{{ "{:,.2f}".format(p.original_price) }}</span>
                                {% endif %}
                            </div>
                            {% if p.is_unlimited_stock %}
                                <span class="text-[0.65rem] text-emerald-600 font-bold block mb-4">● Freshly Made / In Stock</span>
                            {% else %}
                                <span class="text-[0.65rem] text-stone-400 block mb-4">{{ p.stock }} units left</span>
                            {% endif %}
                            
                            {% if p.is_available %}
                                <button type="button" onclick="openProductModal({{ p.id }})" class="w-full bg-stone-900 text-white py-3 rounded-xl text-sm font-semibold hover:bg-stone-800 transition-all duration-300 shadow-md cursor-pointer">VIEW & ORDER</button>
                            {% else %}
                                <button disabled class="w-full py-3 bg-stone-100 text-stone-400 text-sm font-semibold rounded-xl cursor-not-allowed">OUT OF STOCK</button>
                            {% endif %}
                        </div>
                    </div>
                </div>
                {% else %}
                <div class="col-span-full text-center py-20">
                    <p class="text-stone-400 text-lg font-serif italic">No regular items available in catalog right now.</p>
                </div>
                {% endfor %}
            </div>
        </section>

        {% if store.is_section_active('ads') and 3 in ad_slots %}
        <div class="mt-10 relative group">
            <span class="ad-corner-tag">AD</span>
            <a href="/ad/click/{{ ad_slots[3].id }}" target="_blank" class="block w-full overflow-hidden rounded-2xl border border-stone-200 shadow-sm">
                <img src="{{ ad_slots[3].banner_image if ad_slots[3].banner_image.startswith('http') else url_for('static', filename='uploads/ads/' + ad_slots[3].banner_image) }}" alt="Sponsor Ad" class="w-full h-32 md:h-40 object-cover group-hover:scale-[1.02] transition-transform duration-500">
            </a>
        </div>
        {% endif %}
    </main>

    <footer class="bg-white border-t border-stone-100 py-10 text-center text-sm text-stone-500">
        Made with <a href="/" class="text-stone-900 font-bold hover:underline">Marketplace</a> • Powered by Techlite
    </footer>
</body>
</html>"""


def get_curated_fallback_template(kiosk_name: str, bio: str, prompt: str) -> str:
    return MASTER_FALLBACK_TEMPLATE


def clean_html_fences(raw_text: str) -> str:
    raw_text = re.sub(r'^```html\s*', '', raw_text.strip(), flags=re.IGNORECASE)
    raw_text = re.sub(r'^```\s*', '', raw_text.strip())
    raw_text = re.sub(r'```$', '', raw_text.strip())
    return raw_text.strip()


def inject_bulletproof_chassis(html_content: str, kiosk_name: str = '', bio: str = '', meta_img: str = '') -> str:
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

    if re.search(r'<head[^>]*>', html_content, re.IGNORECASE):
        html_content = re.sub(r'<title>.*?</title>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        html_content = re.sub(r'<meta\s+property=["\']og:[^>]+>', '', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<meta\s+name=["\']twitter:[^>]+>', '', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<meta\s+name=["\']description["\'][^>]+>', '', html_content, flags=re.IGNORECASE)
        
        injection = f"<head>\n{meta_tags}"
        if 'cdn.tailwindcss.com' not in html_content:
            injection += '\n    <script src="https://cdn.tailwindcss.com"></script>'
        html_content = re.sub(r'<head[^>]*>', injection, html_content, count=1, flags=re.IGNORECASE)

    # 🧹 AGGRESSIVE CLEANUP: Strip any AI hallucinated modals, drawers, or scripts 
    html_content = re.sub(r'<div[^>]*id=["\']productModal["\'][^>]*>.*?</div>\s*</div>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<aside[^>]*id=["\']cartDrawer["\'][^>]*>.*?</aside>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<div[^>]*id=["\']cartOverlay["\'][^>]*>.*?</div>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<script[^>]*>.*?window\.KIOSK_PRODUCTS.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<img[^>]+src=["\']\s*["\'][^>]*>', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<img[^>]+src=["\'](None|null|undefined)["\'][^>]*>', '', html_content, flags=re.IGNORECASE)

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
    
    # 🚀 UPDATED: Using the top-tier FREE NVIDIA Nemotron 3 Ultra model.
    # It has 550B parameters, making it smart enough to follow strict Jinja2 rules 
    # without hallucinating. If you set an env var, it will use that instead.
    model_name = os.environ.get('OPENROUTER_MODEL') or 'nvidia/nemotron-3-ultra:free'

    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt_instruction}]
    }
    
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=60) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return res_data['choices'][0]['message']['content']
    except Exception as e:
        print(f"OpenRouter Error: {e}", flush=True)
        return None

def generate_kiosk_template(kiosk_name: str, bio: str, prompt: str, logo_url: str = '', hero_url: str = '', bg_url: str = '', currency: str = '₦') -> str:
    primary_meta_img = logo_url or hero_url or bg_url or ''

    # 🚨 THE "JINJA DNA" PROMPT: Forces true creativity while strictly preserving backend logic
    system_instruction = (
        f'You are an Awwwards-winning UI/UX Designer. Your task is to generate a visually stunning, unique, "Pinterest-level" elite storefront using Tailwind CSS.\n\n'
        'CRITICAL: You are NOT given a template to copy. You are given a set of STRICT JINJA2 RULES and VARIABLES. You must build a completely original HTML structure around these rules. Do not replicate the structure, classes, or layout of any example you have seen.\n\n'
        
        '🚨 STRICT JINJA2 RULES (You MUST use these exact snippets where applicable):\n'
        '1. COPYRIGHT: ALWAYS use `{{ store.created_at.year if store and store.created_at else \'2026\' }}`. NEVER use `{{ now }}` or any undefined variables.\n'
        '2. LOGO: `{% if store.logo and store.logo != \'default_logo.png\' %}<img src="{{ store.logo if store.logo.startswith(\'http\') else url_for(\'static\', filename=\'uploads/logos/\' + store.logo) }}" class="...">{% endif %}`\n'
        '3. AD SLOTS (Dictionary): `{% if store.is_section_active(\'ads\') and 1 in ad_slots %}` ... Image: `{{ ad_slots[1].banner_image if ad_slots[1].banner_image.startswith(\'http\') else url_for(\'static\', filename=\'uploads/ads/\' + ad_slots[1].banner_image) }}` ... Link: `/ad/click/{{ ad_slots[1].id }}` ... `{% endif %}` (Apply same logic for slot 3).\n'
        '4. HERO: `{% if store.is_section_active(\'hero\') and store.hero_image %}` ... Image: `{{ store.hero_image if store.hero_image.startswith(\'http\') else url_for(\'static\', filename=\'uploads/heroes/\' + store.hero_image) }}` ... `{% endif %}`\n'
        '5. FLASH SALES LOOP: `{% for p in flash_sales %}` ... Image: `{{ p.image if p.image.startswith(\'http\') else url_for(\'static\', filename=\'uploads/products/\' + p.image) }}` ... Name: `{{ p.name }}` ... Price: `{{ store.currency }}{{ "{:,.2f}".format(p.current_price) }}` ... Button MUST have `onclick="openProductModal({{ p.id }})"`.\n'
        '6. REGULAR PRODUCTS LOOP: `{% for p in regular_products %}` ... Image: `{{ p.image if p.image.startswith(\'http\') else url_for(\'static\', filename=\'uploads/products/\' + p.image) }}` ... Name: `{{ p.name }}` ... Price: `{% if p.has_discount %}{{ store.currency }}{{ "{:,.2f}".format(p.original_price) }}{{ store.currency }}{{ "{:,.2f}".format(p.discount_price) }}{% else %}{{ store.currency }}{{ "{:,.2f}".format(p.original_price) }}{% endif %}` ... Stock: `{% if p.is_unlimited_stock %}In Stock{% else %}{{ p.stock }} units left{% endif %}` ... Button MUST have `onclick="openProductModal({{ p.id }})"`.\n'
        '7. EMPTY STATE: `{% else %}<p>No items available.</p>{% endfor %}`\n'
        '8. CART TRIGGER: Header MUST contain a button with `onclick="toggleCart()"` and `<span id="cartCountBadge">0</span>`.\n\n'

        '🚨 STRICT PROHIBITIONS:\n'
        '1. DO NOT output ANY `<script>` tags. DO NOT output `<div id="productModal">` or `<aside id="cartDrawer">`. The system injects a bulletproof cart and modal engine automatically.\n'
        '2. DO NOT copy generic HTML structures. Be completely original and creative with the layout, spacing, and Tailwind classes.\n'
        '3. Output ONLY raw HTML. No markdown backticks.\n\n'

        '🎨 ELITE DESIGN MANDATES:\n'
        '1. Typography: Use `tracking-tight` for headings. Mix elegant fonts (e.g., Playfair Display for headings, Inter for body).\n'
        '2. Spacing: Be generous. Use `gap-6` or `gap-8` for grids. Use `py-16` or `py-20` for section padding.\n'
        '3. Product Cards: `bg-white`, `rounded-2xl`, `border border-stone-100`, `shadow-sm`. Add `hover:shadow-xl hover:-translate-y-1 transition-all duration-300`.\n'
        '4. Images: Use `aspect-square` or `aspect-[4/5]`, `overflow-hidden`, `bg-stone-100`. Add `group-hover:scale-105 transition-transform duration-500`.\n'
        '5. Buttons: Use sophisticated palettes. Use `rounded-xl` or `rounded-full`, `font-semibold`, and smooth hover transitions.\n\n'

        'TASK: Build a completely new, stunning, elite HTML storefront using ONLY the Jinja2 rules above. Be wildly creative with the layout, but strictly obedient to the variables.'
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

    # 2. Backup: OpenRouter (Using the new FREE Nemotron 3 Ultra)
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
