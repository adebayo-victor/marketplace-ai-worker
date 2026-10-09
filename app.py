import os
import threading
import requests
from flask import Flask, request, jsonify
from ai_builder import generate_kiosk_template

app = Flask(__name__)

def run_ai_task(job):
    kiosk_id = job.get('kiosk_id')
    kiosk_name = job.get('kiosk_name', 'Store')
    callback_url = job.get('callback_url')
    secret = secret = (job.get('secret') or os.environ.get('BUILDER_SECRET_KEY') or '').strip()

    print(f"🚀 [WORKER] Starting AI template generation for #{kiosk_id}: {kiosk_name}")

    try:
        html = generate_kiosk_template(
            kiosk_name=kiosk_name,
            bio=job.get('bio', ''),
            prompt=job.get('prompt', ''),
            logo_url=job.get('logo_url', ''),
            hero_url=job.get('hero_url', ''),
            bg_url=job.get('bg_url', ''),
            currency=job.get('currency', '₦')
        )

        if not html:
            print(f"⚠️ [WORKER] Generation returned empty for #{kiosk_id}.")
            return

        # Deliver generated HTML back to Vercel
        headers = {
            "Authorization": f"Bearer {secret}",
            "Content-Type": "application/json"
        }
        payload = {
            "kiosk_id": kiosk_id,
            "custom_html": html
        }

        print(f"📦 [WORKER] Delivering completed HTML to Vercel: {callback_url}")
        res = requests.post(callback_url, json=payload, headers=headers, timeout=30)
        print(f"✅ [WORKER] Vercel accepted callback. Response status: {res.status_code}")

    except Exception as e:
        print(f"❌ [WORKER] Error during build task: {e}")


@app.route('/health', methods=['GET'])
@app.route('/', methods=['GET'])
def health():
    return jsonify({
        "status": "online",
        "service": "marketplace-ai-worker"
    }), 200


@app.route('/build', methods=['POST'])
def build_endpoint():
    job = request.get_json() or {}

    if not job.get('kiosk_id') or not job.get('callback_url'):
        return jsonify({"status": "error", "message": "Missing kiosk_id or callback_url"}), 400

    # Execute asynchronously in background thread (Render will NOT kill this thread!)
    thread = threading.Thread(target=run_ai_task, args=(job,))
    thread.daemon = False
    thread.start()

    return jsonify({
        "status": "accepted",
        "message": f"Worker processing template for {job.get('kiosk_name')}"
    }), 202


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
