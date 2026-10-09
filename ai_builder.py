import os
import re
import json
import urllib.request
import urllib.error

# 🛡️ THE BULLETPROOF INTERACTIVE ENGINE (MODAL INSPECTION + TOAST + CHECKOUT)
# (Assuming your GUARANTEED_CART_ENGINE string is defined here exactly as before)
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
# 🏛️ THE MASTER FALLBACK TEMPLATE (Your exact Marketplace logic)
# Stripped of JS/Modals so the Bulletproof Engine can handle them safely.
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
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        :root { --clay: #8d5b3e; --cream: #f9f5f0; --dark-oak: #2d1e14; }
        body { background-color: var(--cream); color: var(--dark-oak); font-family: 'Georgia', serif; margin: 0;
            {% if store.background_image %}
            background-image: linear-gradient(rgba(249, 245, 240, 0.88), rgba(249, 245, 240, 0.88)), url('{{ store.background_image if store.background_image.startswith("http") else url_for("static", filename="uploads/backgrounds/" + store.background_image) }}');
            background-size: cover; background-attachment: fixed; background-position: center;
            {% endif %} }
        .font-ui { font-family: 'Montserrat', sans-serif; }
        .btn-oak { background: var(--dark-oak); color: white; padding: 12px 20px; font-family: 'Montserrat', sans-serif; font-size: 0.7rem; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; text-decoration: none; border: none; cursor: pointer; transition: 0.3s; }
        .btn-clay { background: var(--clay); color: white; padding: 12px 20px; font-family: 'Montserrat', sans-serif; font-size: 0.7rem; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; text-decoration: none; border: none; cursor: pointer; transition: 0.3s; }
        .ad-corner-tag { position: absolute; top: 10px; right: 10px; background: rgba(0, 0, 0, 0.65); color: #fff; padding: 2px 8px; border-radius: 4px; font-family: monospace; font-size: 9px; font-weight: bold; letter-spacing: 1px; backdrop-filter: blur(4px); border: 1px solid rgba(255, 255, 255, 0.2); pointer-events: none; }
    </style>
</head>
<body class="min-h-screen flex flex-col justify-between">
    <header class="bg-white/95 backdrop-blur border-b border-[#eee] py-5 px-6 sticky top-0 z-40">
        <div class="max-w-6xl mx-auto flex items-center justify-between">
            <div class="flex items-center gap-3">
                {% if store.logo and store.logo != 'default_logo.png' %}
                    <img src="{{ store.logo if store.logo.startswith('http') else url_for('static', filename='uploads/logos/' + store.logo) }}" class="h-10 w-10 object-contain rounded-full">
                {% endif %}
                <div>
                    <a href="/{{ store.slug }}" class="font-ui font-semibold text-lg text-dark-oak tracking-wider">{{ store.name }}</a>
                    <p class="font-serif italic text-xs text-stone-500 m-0">{{ store.bio }}</p>
                </div>
            </div>
            <button onclick="toggleCart()" class="btn-clay flex items-center gap-2 cursor-pointer">
                <span>BAG</span>
                <span id="cartCountBadge" class="bg-white text-clay px-2 py-0.5 rounded-full font-bold text-[0.65rem]">0</span>
            </button>
        </div>
    </header>

    <main class="max-w-6xl mx-auto px-6 py-10 w-full flex-grow">
        {% if store.is_section_active('ads') and 1 in ad_slots %}
        <div class="mb-10 relative">
            <span class="ad-corner-tag">AD</span>
            <a href="/ad/click/{{ ad_slots[1].id }}" target="_blank">
                <img src="{{ ad_slots[1].banner_image if ad_slots[1].banner_image.startswith('http') else url_for('static', filename='uploads/ads/' + ad_slots[1].banner_image) }}" alt="Sponsor Ad" class="w-full h-28 md:h-36 object-cover border border-[#eee] shadow-sm rounded-xl">
            </a>
        </div>
        {% endif %}

        {% if store.is_section_active('hero') and store.hero_image %}
        <div class="mb-12">
            <img src="{{ store.hero_image if store.hero_image.startswith('http') else url_for('static', filename='uploads/heroes/' + store.hero_image) }}" alt="Hero Showcase" class="w-full h-48 md:h-64 object-cover rounded-2xl shadow-sm border border-[#eee]">
        </div>
        {% endif %}

        {% if store.is_section_active('flash_sales') and flash_sales %}
        <section class="mb-14">
            <div class="flex items-center gap-3 mb-6">
                <span class="font-ui text-xs font-bold uppercase tracking-wider bg-[#ffebeb] text-[#b33a3a] px-3 py-1 border border-[#b33a3a]/20">🔥 Flash Deals</span>
                <span class="font-serif italic text-sm text-stone-500">Limited quantity promotions</span>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                {% for p in flash_sales %}
                <div class="product-card bg-white p-6 border-t-[4px] border-[#b33a3a] shadow-sm flex flex-col justify-between" data-name="{{ p.name }}">
                    <div>
                        <div class="h-44 bg-stone-50 mb-4 overflow-hidden flex items-center justify-center">
                            <img src="{{ p.image if p.image.startswith('http') else url_for('static', filename='uploads/products/' + p.image) }}" alt="{{ p.name }}" class="object-cover h-full w-full">
                        </div>
                        <h4 class="font-ui font-semibold text-base mb-1">{{ p.name }}</h4>
                        <p class="font-serif text-xs text-stone-500 mb-4">{{ p.description }}</p>
                    </div>
                    <div>
                        <div class="mb-4">
                            <span class="line-through text-stone-400 font-ui text-xs">{{ store.currency }}{{ "{:,.2f}".format(p.original_price) }}</span>
                            <span class="font-ui font-bold text-lg text-[#b33a3a] ml-2">{{ store.currency }}{{ "{:,.2f}".format(p.current_price) }}</span>
                        </div>
                        <button type="button" onclick="openProductModal({{ p.id }})" class="btn-clay w-full text-center cursor-pointer">SELECT & ORDER</button>
                    </div>
                </div>
                {% endfor %}
            </div>
        </section>
        {% endif %}

        <div class="flex flex-wrap items-center justify-between gap-4 mb-8 pb-4 border-b border-[#eee]">
            <div>
                <h3 class="font-ui text-xl font-normal lowercase tracking-tight m-0">kiosk catalog</h3>
                <p class="font-serif italic text-xs text-stone-400 m-0">Freshly prepared & available items</p>
            </div>
            <input type="text" id="catalogSearchInput" onkeyup="filterCatalog()" placeholder="Search menu or products..." class="p-2.5 border border-stone-200 text-xs font-ui outline-none w-64 rounded-xl bg-white shadow-sm focus:border-clay">
        </div>

        <section class="mb-14">
            <div id="catalogGrid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
                {% for p in regular_products %}
                <div class="catalog-item product-card bg-white p-6 border-t-[4px] border-clay shadow-sm flex flex-col justify-between" data-name="{{ p.name }}">
                    <div>
                        <div class="h-48 bg-stone-50 mb-4 overflow-hidden flex items-center justify-center">
                            <img src="{{ p.image if p.image.startswith('http') else url_for('static', filename='uploads/products/' + p.image) }}" alt="{{ p.name }}" class="object-cover h-full w-full">
                        </div>
                        <h4 class="product-title font-ui font-semibold text-base text-dark-oak mb-1">{{ p.name }}</h4>
                        <p class="font-serif text-xs text-stone-500 mb-4">{{ p.description }}</p>
                    </div>
                    <div>
                        <div class="mb-4 font-ui">
                            {% if p.has_discount %}
                                <span class="line-through text-stone-400 text-xs">{{ store.currency }}{{ "{:,.2f}".format(p.original_price) }}</span>
                                <span class="font-bold text-base text-clay ml-1">{{ store.currency }}{{ "{:,.2f}".format(p.discount_price) }}</span>
                            {% else %}
                                <span class="font-bold text-base text-dark-oak">{{ store.currency }}{{ "{:,.2f}".format(p.original_price) }}</span>
                            {% endif %}
                            {% if p.is_unlimited_stock %}
                                <span class="text-[0.65rem] text-emerald-600 font-bold block mt-0.5">● Freshly Made / In Stock</span>
                            {% else %}
                                <span class="text-[0.65rem] text-stone-400 block mt-0.5">{{ p.stock }} units left</span>
                            {% endif %}
                        </div>
                        {% if p.is_available %}
                            <button type="button" onclick="openProductModal({{ p.id }})" class="btn-oak w-full text-center cursor-pointer">VIEW & ORDER</button>
                        {% else %}
                            <button disabled class="w-full py-3 bg-stone-100 text-stone-400 font-ui text-xs font-semibold uppercase tracking-wider cursor-not-allowed">OUT OF STOCK</button>
                        {% endif %}
                    </div>
                </div>
                {% else %}
                <p class="font-serif italic text-stone-400 col-span-3">No regular items available in catalog right now.</p>
                {% endfor %}
            </div>
        </section>

        {% if store.is_section_active('ads') and 3 in ad_slots %}
        <div class="mt-10 relative">
            <span class="ad-corner-tag">AD</span>
            <a href="/ad/click/{{ ad_slots[3].id }}" target="_blank">
                <img src="{{ ad_slots[3].banner_image if ad_slots[3].banner_image.startswith('http') else url_for('static', filename='uploads/ads/' + ad_slots[3].banner_image) }}" alt="Sponsor Ad" class="w-full h-28 md:h-36 object-cover border border-[#eee] shadow-sm rounded-xl">
            </a>
        </div>
        {% endif %}
    </main>

    <footer class="bg-white border-t border-[#eee] py-8 text-center text-xs font-ui text-stone-400">
        Made with <a href="/" class="text-clay font-bold">Marketplace</a> • Powered by Techlite
    </footer>
</body>
</html>"""


def get_curated_fallback_template(kiosk_name: str, bio: str, prompt: str) -> str:
    # We now exclusively use your Master Marketplace Template as the ultimate fail-safe
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
    # to ensure the GUARANTEED_CART_ENGINE is the ONLY source of truth for functionality.
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
    model_name = os.environ.get('OPENROUTER_MODEL') or 'meta-llama/llama-3.3-70b-instruct'
    payload = {"model": model_name, "messages": [{"role": "user", "content": prompt_instruction}]}
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

    # 🚨 THE "HOLY GRAIL" PROMPT: Forces the AI to use your exact backend logic
    system_instruction = (
        f'You are an Elite UI/UX Designer. Your task is to restyle a "Master Baseline Template" to match a specific design prompt using Tailwind CSS.\n'
        'CRITICAL: You MUST preserve the EXACT Jinja2 backend logic, URL routing, and data structures provided in the baseline.\n\n'
        'STRICT PRESERVATION RULES:\n'
        '1. NEVER alter, remove, or misspell ANY Jinja2 {{ }} or {% %} tags.\n'
        '2. NEVER change the image URL logic: `{{ url if url.startswith(\'http\') else url_for(...) }}`.\n'
        '3. NEVER change the Ad Slot dictionary logic: `{% if 1 in ad_slots %}` and `ad_slots[1].banner_image`.\n'
        '4. NEVER change the product loops or variable names (`regular_products`, `flash_sales`).\n'
        '5. DO NOT output any `<script>` tags. DO NOT output the `<div id="productModal">` or `<aside id="cartDrawer">`. The system injects a bulletproof cart and modal engine automatically.\n'
        '6. Ensure the header has a button with `onclick="toggleCart()"` and `<span id="cartCountBadge">0</span>`.\n'
        '7. Ensure products have `<button onclick="openProductModal({{ p.id }})">`.\n'
        '8. Output ONLY raw HTML. No markdown backticks.\n\n'
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
        'TASK: Take the "Design Instructions" and apply beautiful, modern Tailwind CSS classes to the HTML structure. Use the Master Baseline Jinja2 Logic above to populate the data. Remember: DO NOT output the cart/modal HTML or JS. Output ONLY the visual storefront HTML.'
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

    # 3. Tier 3: Master Fallback (Guaranteed 100% Fail-Safe & Functional)
    print(f"🛡️ [AI BUILDER] Activating Master Marketplace Fallback for '{kiosk_name}'.", flush=True)
    fallback_html = get_curated_fallback_template(kiosk_name, bio, prompt)
    return inject_bulletproof_chassis(fallback_html, kiosk_name, bio, primary_meta_img)
