import os
import re
import json
import urllib.request
import urllib.error

# 🛡️ THE BULLETPROOF INTERACTIVE ENGINE (MODAL INSPECTION + TOAST + CHECKOUT)
# (Keep your existing GUARANTEED_CART_ENGINE exactly as it was. It is perfect.)
# For brevity, assuming GUARANTEED_CART_ENGINE is defined above this line as in your previous code.

# ==============================================================================
# 🎨 3 PREMIUM, "ZERO-ASSET PROOF" FALLBACK TEMPLATES
# These templates look 10/10 even if NO images (logo, hero, products) are uploaded.
# ==============================================================================

FALLBACK_TEMPLATE_MINIMAL = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;800&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body { font-family: 'Inter', sans-serif; background-color: #FAFAFA; color: #18181B; }</style>
</head>
<body class="min-h-screen flex flex-col">
    <header class="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-zinc-200 px-4 md:px-8 py-4 flex justify-between items-center">
        <div class="flex items-center gap-3">
            {% if store and store.logo and store.logo not in ['default_logo.png', '', 'None', 'null'] %}
            <img src="{{ store.logo }}" alt="{{ store.name }}" class="h-11 w-11 object-contain rounded-full border border-zinc-100 shadow-sm">
            {% else %}
            <div class="h-11 w-11 rounded-full bg-gradient-to-br from-zinc-900 to-zinc-700 flex items-center justify-center text-white font-black text-lg shadow-md">{{ (store.name[0] if store and store.name else 'S') }}</div>
            {% endif %}
            <span class="text-lg font-bold tracking-tight text-zinc-900">{{ store.name if store else 'Store' }}</span>
        </div>
        <div class="flex items-center gap-3">
            <input type="text" oninput="filterProducts(this.value)" placeholder="Search..." class="hidden md:block bg-zinc-100 border border-zinc-200 text-sm px-4 py-2 rounded-full outline-none focus:ring-2 focus:ring-zinc-900 w-48 transition">
            <button onclick="toggleCart()" class="flex items-center gap-2 bg-zinc-900 hover:bg-zinc-800 text-white px-5 py-2.5 rounded-full transition font-semibold text-sm shadow-md">
                <span>Bag</span>
                <span id="cartCountBadge" class="bg-white text-zinc-900 text-[10px] font-black px-1.5 py-0.5 rounded-full">0</span>
            </button>
        </div>
    </header>

    {% if not store or store.is_section_active('hero') %}
    <section class="relative px-4 md:px-8 py-20 md:py-28 bg-gradient-to-br from-zinc-50 via-white to-zinc-100 border-b border-zinc-200 overflow-hidden">
        <div class="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSA2MCAwIEwgMCAwIDAgNjAiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI2U0ZTRlNyIgc3Ryb2tlLXdpZHRoPSIxIi8+PC9wYXR0ZXJuPjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI2dyaWQpIi8+PC9zdmc+')] opacity-60"></div>
        <div class="relative z-10 max-w-4xl mx-auto text-center">
            <h1 class="text-4xl md:text-6xl font-extrabold text-zinc-900 tracking-tight mb-4 leading-tight">{{ store.name if store else 'Welcome' }}</h1>
            <p class="text-zinc-500 text-base md:text-lg max-w-xl mx-auto leading-relaxed mb-8">{{ store.bio if store else 'Discover our curated collection of premium products.' }}</p>
            <a href="#products-grid" class="inline-flex items-center gap-2 bg-zinc-900 hover:bg-zinc-800 text-white px-8 py-3.5 rounded-full font-semibold text-sm transition shadow-lg hover:shadow-xl hover:-translate-y-0.5">
                Explore Collection <span>&darr;</span>
            </a>
        </div>
    </section>
    {% endif %}

    {% if ad_slots and (not store or store.is_section_active('ads')) %}
        {% for ad in ad_slots %}
            {% if ad.is_active and ad.banner_image and ad.banner_image not in ['', 'None', 'null'] %}
            <div class="my-8 px-4 md:px-8 max-w-6xl mx-auto w-full">
                <a href="{{ ad.target_link or '#' }}" {% if ad.target_link %}target="_blank"{% endif %} class="relative block w-full overflow-hidden rounded-2xl border border-zinc-200 shadow-sm group">
                    <img src="{{ ad.banner_image }}" alt="Promotion" class="w-full h-40 sm:h-56 md:h-64 object-cover group-hover:scale-[1.02] transition-transform duration-500">
                    <span class="absolute top-4 right-4 bg-white/90 backdrop-blur text-zinc-900 text-[10px] font-bold tracking-wider px-3 py-1 rounded-full shadow-sm">SPONSORED</span>
                </a>
            </div>
            {% endif %}
        {% endfor %}
    {% endif %}

    {% if flash_sales and (not store or store.is_section_active('flash_sales')) %}
    <section class="py-12 px-4 md:px-8 bg-zinc-50 border-y border-zinc-200">
        <div class="max-w-7xl mx-auto">
            <div class="flex items-center gap-2 mb-8">
                <span class="flex h-3 w-3 relative"><span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span><span class="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span></span>
                <h2 class="text-xl font-bold text-zinc-900 uppercase tracking-wide">Flash Deals</h2>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                {% for p in flash_sales %}
                <div class="product-card bg-white border border-zinc-200 rounded-2xl p-4 flex flex-col shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all duration-300" data-name="{{ p.name }}">
                    <div onclick="openProductModal({{ p.id }})" class="relative aspect-square bg-zinc-100 rounded-xl overflow-hidden mb-4 group cursor-pointer">
                        {% if p.image and p.image not in ['default_product.png', '', 'None', 'null'] %}
                        <img src="{{ p.image }}" alt="{{ p.name }}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500">
                        <div style="display:none;" class="absolute inset-0 flex-col items-center justify-center bg-gradient-to-br from-zinc-100 to-zinc-200 text-zinc-400">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 mb-2 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                            <span class="text-[10px] font-bold uppercase tracking-widest">Preview Unavailable</span>
                        </div>
                        {% else %}
                        <div class="absolute inset-0 flex flex-col items-center justify-center bg-gradient-to-br from-zinc-100 to-zinc-200 text-zinc-400">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 mb-2 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                            <span class="text-[10px] font-bold uppercase tracking-widest">Preview Unavailable</span>
                        </div>
                        {% endif %}
                    </div>
                    <h3 onclick="openProductModal({{ p.id }})" class="font-semibold text-zinc-900 mb-1 cursor-pointer hover:text-zinc-600 transition line-clamp-1">{{ p.name }}</h3>
                    <p class="text-xs text-zinc-500 mb-4 line-clamp-2 leading-relaxed">{{ p.description or 'Premium quality item.' }}</p>
                    <div class="mt-auto flex justify-between items-center pt-4 border-t border-zinc-100">
                        <div>
                            {% if p.has_discount %}
                            <span class="line-through text-zinc-400 text-xs font-medium block">{{ store.currency if store else '₦' }}{{ "{:,.0f}".format(p.original_price) }}</span>
                            {% endif %}
                            <span class="font-bold text-red-600 text-lg">{{ store.currency if store else '₦' }}{{ "{:,.0f}".format(p.current_price) }}</span>
                        </div>
                        <button type="button" onclick="quickAddToCart({{ p.id }}, event)" class="bg-zinc-900 hover:bg-zinc-800 text-white text-[10px] font-bold uppercase tracking-wider py-2.5 px-4 rounded-xl transition shadow-md">Add</button>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </section>
    {% endif %}

    <main id="products-grid" class="py-16 px-4 md:px-8 max-w-7xl mx-auto flex-grow">
        <h2 class="text-2xl font-bold text-zinc-900 mb-8">All Products</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {% for p in regular_products %}
            <div class="product-card bg-white border border-zinc-200 rounded-2xl p-4 flex flex-col shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all duration-300" data-name="{{ p.name }}">
                <div onclick="openProductModal({{ p.id }})" class="relative aspect-square bg-zinc-100 rounded-xl overflow-hidden mb-4 group cursor-pointer">
                    {% if p.image and p.image not in ['default_product.png', '', 'None', 'null'] %}
                    <img src="{{ p.image }}" alt="{{ p.name }}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500">
                    <div style="display:none;" class="absolute inset-0 flex-col items-center justify-center bg-gradient-to-br from-zinc-100 to-zinc-200 text-zinc-400">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 mb-2 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                        <span class="text-[10px] font-bold uppercase tracking-widest">Preview Unavailable</span>
                    </div>
                    {% else %}
                    <div class="absolute inset-0 flex flex-col items-center justify-center bg-gradient-to-br from-zinc-100 to-zinc-200 text-zinc-400">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 mb-2 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                        <span class="text-[10px] font-bold uppercase tracking-widest">Preview Unavailable</span>
                    </div>
                    {% endif %}
                </div>
                <h3 onclick="openProductModal({{ p.id }})" class="font-semibold text-zinc-900 mb-1 cursor-pointer hover:text-zinc-600 transition line-clamp-1">{{ p.name }}</h3>
                <p class="text-xs text-zinc-500 mb-4 line-clamp-2 leading-relaxed">{{ p.description or 'Premium quality item.' }}</p>
                <div class="mt-auto flex justify-between items-center pt-4 border-t border-zinc-100">
                    <div>
                        {% if p.has_discount %}
                        <span class="line-through text-zinc-400 text-xs font-medium block">{{ store.currency if store else '₦' }}{{ "{:,.0f}".format(p.original_price) }}</span>
                        {% endif %}
                        <span class="font-bold text-zinc-900 text-lg">{{ store.currency if store else '₦' }}{{ "{:,.0f}".format(p.current_price) }}</span>
                    </div>
                    <button type="button" onclick="quickAddToCart({{ p.id }}, event)" class="bg-zinc-900 hover:bg-zinc-800 text-white text-[10px] font-bold uppercase tracking-wider py-2.5 px-4 rounded-xl transition shadow-md">Add</button>
                </div>
            </div>
            {% endfor %}
        </div>
    </main>

    <footer class="border-t border-zinc-200 py-10 text-center text-sm text-zinc-500 bg-white">
        &copy; {{ store.name if store else 'Store' }} &bull; Powered by Marketplace
    </footer>
</body>
</html>"""

# (Note: For brevity, I am providing the fully upgraded MINIMAL template above. 
# The LUXURY and URBAN templates follow the EXACT SAME logic for logos, heroes, and image fallbacks.
# You should replace your existing FALLBACK_TEMPLATE_LUXURY and FALLBACK_TEMPLATE_URBAN 
# with the same robust {% if store.logo not in [...] %} and {% if p.image not in [...] %} checks.)

def get_curated_fallback_template(kiosk_name: str, bio: str, prompt: str) -> str:
    corpus = f"{kiosk_name} {bio} {prompt}".lower()
    if any(k in corpus for k in ['perfume', 'scent', 'fragrance', 'luxury', 'gold', 'extrait', 'jewelry', 'boutique', 'watch', 'premium']):
        return FALLBACK_TEMPLATE_LUXURY # Ensure this has the zero-asset fallbacks too
    if any(k in corpus for k in ['food', 'burger', 'kitchen', 'grill', 'sizzle', 'street', 'dish', 'meal', 'cafe', 'bites', 'snack', 'urban']):
        return FALLBACK_TEMPLATE_URBAN # Ensure this has the zero-asset fallbacks too
    
    return FALLBACK_TEMPLATE_MINIMAL


def clean_html_fences(raw_text: str) -> str:
    raw_text = re.sub(r'^```html\s*', '', raw_text.strip(), flags=re.IGNORECASE)
    raw_text = re.sub(r'^```\s*', '', raw_text.strip())
    raw_text = re.sub(r'```$', '', raw_text.strip())
    return raw_text.strip()


def inject_bulletproof_chassis(html_content: str, kiosk_name: str = '', bio: str = '', meta_img: str = '') -> str:
    # (Keep your existing inject_bulletproof_chassis logic here)
    # It perfectly handles meta tags and appends the GUARANTEED_CART_ENGINE.
    
    if re.search(r'</body>', html_content, re.IGNORECASE):
        return re.sub(r'</body>', GUARANTEED_CART_ENGINE + '\n</body>', html_content, count=1, flags=re.IGNORECASE)
    return html_content + '\n' + GUARANTEED_CART_ENGINE


def generate_kiosk_template(kiosk_name: str, bio: str, prompt: str, logo_url: str = '', hero_url: str = '', bg_url: str = '', currency: str = '₦') -> str:
    primary_meta_img = logo_url or hero_url or bg_url or ''

    # 🚨 ZERO-ASSET PROOF AI PROMPT
    system_instruction = (
        f'You are a Strict Tailwind CSS Theme Injector. Your ONLY job is to modify the CSS classes of a provided, perfectly working HTML skeleton to match a design prompt.\n'
        'DO NOT invent, hallucinate, or hardcode ANY products, prices, images, or names. ALL content comes from backend Jinja2 variables.\n\n'
        '🚨 CRITICAL "ZERO-ASSET" HANDLING RULES:\n'
        '1. LOGO: If no logo URL is provided, DO NOT use an `<img>` tag. Use the provided Jinja fallback to generate a beautiful gradient avatar with the first letter of the store name.\n'
        '2. HERO/BACKGROUND: If no hero/background image is provided, DO NOT leave it blank. Use stunning CSS gradients, mesh backgrounds, or subtle SVG patterns (like the grid pattern in the skeleton) to create a premium visual backdrop.\n'
        '3. PRODUCT IMAGES: ALWAYS use the exact `onerror` fallback provided in the skeleton. If an image fails to load, it must show the beautiful "Preview Unavailable" gradient placeholder.\n\n'
        'STRICT RULES:\n'
        '1. NEVER alter, remove, or misspell ANY Jinja2 {{{{ }}}} tags or {{% %}} blocks.\n'
        '2. You may ONLY change Tailwind CSS classes (colors, fonts, spacing, borders, shadows) to match the design prompt.\n'
        '3. DO NOT generate any <script> tags for cart, modals, or toasts. They are auto-injected.\n'
        '4. DO NOT output markdown backticks (```). Output ONLY raw HTML.\n\n'
        'BASE SKELETON TO STYLE (Apply your Tailwind classes to this structure):\n'
        '<!DOCTYPE html>\n'
        '<html lang="en">\n'
        '<head>\n'
        '    <meta charset="UTF-8">\n'
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '    <title>{{{{ store.name }}}}</title>\n'
        '    <script src="https://cdn.tailwindcss.com"></script>\n'
        '    <!-- Add 1-2 Google Fonts based on design prompt here -->\n'
        '</head>\n'
        '<body class="bg-gray-50 text-gray-900">\n'
        '    <header class="sticky top-0 z-40 bg-white/80 backdrop-blur border-b p-4 flex justify-between items-center">\n'
        '        <div class="flex items-center gap-3">\n'
        '            {{% if store.logo and store.logo not in ["default_logo.png", "", "None", "null"] %}}\n'
        '            <img src="{{{{ store.logo }}}}" class="h-11 w-11 object-contain rounded-full border border-gray-200 shadow-sm">\n'
        '            {{% else %}}\n'
        '            <div class="h-11 w-11 rounded-full bg-gradient-to-br from-gray-900 to-gray-700 flex items-center justify-center text-white font-black text-lg shadow-md">{{{{ (store.name[0] if store and store.name else \'S\') }}}}</div>\n'
        '            {{% endif %}}\n'
        '            <h1 class="text-lg font-bold">{{{{ store.name }}}}</h1>\n'
        '        </div>\n'
        '        <div class="flex items-center gap-3">\n'
        '            <input type="text" oninput="filterProducts(this.value)" placeholder="Search..." class="hidden md:block bg-gray-100 border border-gray-200 text-sm px-4 py-2 rounded-full outline-none">\n'
        '            <button onclick="toggleCart()" class="px-5 py-2.5 bg-gray-900 text-white rounded-full font-semibold text-sm flex items-center gap-2 shadow-md">\n'
        '                Bag <span id="cartCountBadge" class="bg-white text-gray-900 text-[10px] font-black px-1.5 py-0.5 rounded-full">0</span>\n'
        '            </button>\n'
        '        </div>\n'
        '    </header>\n'
        '    {{% if not store or store.is_section_active("hero") %}}\n'
        '    <section class="relative p-8 md:p-16 text-center bg-gradient-to-br from-gray-50 via-white to-gray-100 overflow-hidden">\n'
        '        <div class="absolute inset-0 bg-[url(\'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSA2MCAwIEwgMCAwIDAgNjAiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI2U1ZTdlYiIgc3Ryb2tlLXdpZHRoPSIxIi8+PC9wYXR0ZXJuPjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI2dyaWQpIi8+PC9zdmc+')] opacity-40"></div>\n'
        '        <div class="relative z-10">\n'
        '            <h2 class="text-4xl md:text-6xl font-black mb-4 tracking-tight">{{{{ store.name }}}}</h2>\n'
        '            <p class="text-gray-600 mb-8 max-w-xl mx-auto text-lg leading-relaxed">{{{{ store.bio }}}}</p>\n'
        '            <a href="#products-grid" class="inline-block px-8 py-4 bg-gray-900 text-white rounded-full font-bold text-sm uppercase tracking-wider shadow-xl hover:-translate-y-0.5 transition-all duration-300">Shop Collection</a>\n'
        '        </div>\n'
        '    </section>\n'
        '    {{% endif %}}\n'
        '    {{% if ad_slots and (not store or store.is_section_active("ads")) %}}\n'
        '        {{% for ad in ad_slots %}}\n'
        '            {{% if ad.is_active and ad.banner_image and ad.banner_image not in ["", "None", "null"] %}}\n'
        '            <div class="my-8 px-4 max-w-6xl mx-auto">\n'
        '                <a href="{{{{ ad.target_link or \'#\' }}}}" target="_blank" class="relative block w-full overflow-hidden rounded-2xl border shadow-xl group">\n'
        '                    <img src="{{{{ ad.banner_image }}}}" class="w-full h-40 sm:h-56 md:h-64 object-cover group-hover:scale-[1.02] transition duration-500">\n'
        '                    <span class="absolute top-4 right-4 bg-white/90 backdrop-blur text-gray-900 text-[10px] font-bold px-3 py-1 rounded-full shadow-sm">SPONSORED</span>\n'
        '                </a>\n'
        '            </div>\n'
        '            {{% endif %}}\n'
        '        {{% endfor %}}\n'
        '    {{% endif %}}\n'
        '    {{% if flash_sales and (not store or store.is_section_active("flash_sales")) %}}\n'
        '    <section class="py-12 px-4 bg-gray-50 border-y border-gray-200">\n'
        '        <div class="max-w-7xl mx-auto">\n'
        '            <h2 class="text-2xl font-black mb-8 text-red-600 flex items-center gap-2">⚡ FLASH SALES</h2>\n'
        '            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">\n'
        '                {{% for p in flash_sales %}}\n'
        '                <div class="product-card bg-white border border-gray-200 rounded-2xl p-4 flex flex-col shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all duration-300" data-name="{{{{ p.name }}}}">\n'
        '                    <div onclick="openProductModal({{{{ p.id }}}})" class="relative aspect-square bg-gray-100 rounded-xl overflow-hidden mb-4 group cursor-pointer">\n'
        '                        {{% if p.image and p.image not in ["default_product.png", "", "None", "null"] %}}\n'
        '                        <img src="{{{{ p.image }}}}" alt="{{{{ p.name }}}}" onerror="this.style.display=\'none\'; this.nextElementSibling.style.display=\'flex\';" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500">\n'
        '                        <div style="display:none;" class="absolute inset-0 flex-col items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200 text-gray-400">\n'
        '                            <svg class="h-10 w-10 mb-2 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>\n'
        '                            <span class="text-[10px] font-bold uppercase tracking-widest">Preview Unavailable</span>\n'
        '                        </div>\n'
        '                        {{% else %}}\n'
        '                        <div class="absolute inset-0 flex flex-col items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200 text-gray-400">\n'
        '                            <svg class="h-10 w-10 mb-2 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>\n'
        '                            <span class="text-[10px] font-bold uppercase tracking-widest">Preview Unavailable</span>\n'
        '                        </div>\n'
        '                        {{% endif %}}\n'
        '                    </div>\n'
        '                    <h3 onclick="openProductModal({{{{ p.id }}}})" class="font-semibold text-gray-900 mb-1 cursor-pointer hover:text-gray-600 transition line-clamp-1">{{{{ p.name }}}}</h3>\n'
        '                    <p class="text-xs text-gray-500 mb-4 line-clamp-2 leading-relaxed">{{{{ p.description }}}}</p>\n'
        '                    <div class="mt-auto flex justify-between items-center pt-4 border-t border-gray-100">\n'
        '                        <div>\n'
        '                            {{% if p.has_discount %}}\n'
        '                            <span class="line-through text-gray-400 text-xs font-medium block">{{{{ store.currency }}}}{{{{ "{:,.0f}".format(p.original_price) }}}}</span>\n'
        '                            {{% endif %}}\n'
        '                            <span class="font-bold text-red-600 text-lg">{{{{ store.currency }}}}{{{{ "{:,.0f}".format(p.current_price) }}}}</span>\n'
        '                        </div>\n'
        '                        <button type="button" onclick="quickAddToCart({{{{ p.id }}}}, event)" class="bg-gray-900 hover:bg-gray-800 text-white text-[10px] font-bold uppercase tracking-wider py-2.5 px-4 rounded-xl transition shadow-md">Add</button>\n'
        '                    </div>\n'
        '                </div>\n'
        '                {{% endfor %}}\n'
        '            </div>\n'
        '        </div>\n'
        '    </section>\n'
        '    {{% endif %}}\n'
        '    <main id="products-grid" class="py-16 px-4 max-w-7xl mx-auto flex-grow">\n'
        '        <h2 class="text-2xl font-black text-gray-900 mb-8">All Products</h2>\n'
        '        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">\n'
        '            {{% for p in regular_products %}}\n'
        '            <div class="product-card bg-white border border-gray-200 rounded-2xl p-4 flex flex-col shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all duration-300" data-name="{{{{ p.name }}}}">\n'
        '                <div onclick="openProductModal({{{{ p.id }}}})" class="relative aspect-square bg-gray-100 rounded-xl overflow-hidden mb-4 group cursor-pointer">\n'
        '                    {{% if p.image and p.image not in ["default_product.png", "", "None", "null"] %}}\n'
        '                    <img src="{{{{ p.image }}}}" alt="{{{{ p.name }}}}" onerror="this.style.display=\'none\'; this.nextElementSibling.style.display=\'flex\';" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500">\n'
        '                    <div style="display:none;" class="absolute inset-0 flex-col items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200 text-gray-400">\n'
        '                        <svg class="h-10 w-10 mb-2 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>\n'
        '                        <span class="text-[10px] font-bold uppercase tracking-widest">Preview Unavailable</span>\n'
        '                    </div>\n'
        '                    {{% else %}}\n'
        '                    <div class="absolute inset-0 flex flex-col items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200 text-gray-400">\n'
        '                        <svg class="h-10 w-10 mb-2 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>\n'
        '                        <span class="text-[10px] font-bold uppercase tracking-widest">Preview Unavailable</span>\n'
        '                    </div>\n'
        '                    {{% endif %}}\n'
        '                </div>\n'
        '                <h3 onclick="openProductModal({{{{ p.id }}}})" class="font-semibold text-gray-900 mb-1 cursor-pointer hover:text-gray-600 transition line-clamp-1">{{{{ p.name }}}}</h3>\n'
        '                <p class="text-xs text-gray-500 mb-4 line-clamp-2 leading-relaxed">{{{{ p.description }}}}</p>\n'
        '                <div class="mt-auto flex justify-between items-center pt-4 border-t border-gray-100">\n'
        '                    <div>\n'
        '                        {{% if p.has_discount %}}\n'
        '                        <span class="line-through text-gray-400 text-xs font-medium block">{{{{ store.currency }}}}{{{{ "{:,.0f}".format(p.original_price) }}}}</span>\n'
        '                        {{% endif %}}\n'
        '                        <span class="font-bold text-gray-900 text-lg">{{{{ store.currency }}}}{{{{ "{:,.0f}".format(p.current_price) }}}}</span>\n'
        '                    </div>\n'
        '                    <button type="button" onclick="quickAddToCart({{{{ p.id }}}}, event)" class="bg-gray-900 hover:bg-gray-800 text-white text-[10px] font-bold uppercase tracking-wider py-2.5 px-4 rounded-xl transition shadow-md">Add</button>\n'
        '                </div>\n'
        '            </div>\n'
        '            {{% endfor %}}\n'
        '        </div>\n'
        '    </main>\n'
        '    <footer class="border-t border-gray-200 py-10 text-center text-sm text-gray-500 bg-white">\n'
        '        &copy; {{{{ store.name }}}} &bull; Powered by Marketplace\n'
        '    </footer>\n'
        '</body>\n'
        '</html>\n\n'
        'TASK: Take the "Design Instructions" prompt and ONLY modify the Tailwind CSS classes (colors, fonts, spacing, borders, shadows, background colors) in the skeleton above to match the requested vibe. DO NOT remove or alter any Jinja2 {{{{ }}}} tags, {{% %}} blocks, or onclick handlers.'
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

    # 3. Tier 3: Curated Design Archetype (Guaranteed 100% Fail-Safe & Beautiful)
    print(f"🛡️ [AI BUILDER] Activating Premium Curated Design Archetype fallback for '{kiosk_name}'.", flush=True)
    fallback_html = get_curated_fallback_template(kiosk_name, bio, prompt)
    return inject_bulletproof_chassis(fallback_html, kiosk_name, bio, primary_meta_img)
