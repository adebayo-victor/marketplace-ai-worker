import os
import threading
import requests
from flask import Flask, request, jsonify
from ai_builder import generate_kiosk_template, generate_universal_template # <-- Added universal import

app = Flask(__name__)

# ==============================================================================
# EXISTING KIOSK BUILDER (Preserved 100% Intact)
# ==============================================================================
def run_ai_task(job):
    kiosk_id = job.get('kiosk_id')
    kiosk_name = job.get('kiosk_name', 'Store')
    callback_url = job.get('callback_url')
    secret = (job.get('secret') or os.environ.get('BUILDER_SECRET_KEY') or '').strip()

    print(f"🚀 [WORKER] Starting AI template generation for Kiosk #{kiosk_id}: {kiosk_name}")

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
            print(f"⚠️ [WORKER] Generation returned empty for Kiosk #{kiosk_id}.")
            return

        headers = {
            "Authorization": f"Bearer {secret}",
            "Content-Type": "application/json"
        }
        payload = {
            "kiosk_id": kiosk_id,
            "custom_html": html
        }

        print(f"📦 [WORKER] Delivering completed Kiosk HTML to Vercel: {callback_url}")
        res = requests.post(callback_url, json=payload, headers=headers, timeout=30)
        print(f"✅ [WORKER] Vercel accepted callback. Response status: {res.status_code}")

    except Exception as e:
        print(f"❌ [WORKER] Error during Kiosk build task: {e}")


@app.route('/build', methods=['POST'])
def build_endpoint():
    job = request.get_json() or {}

    if not job.get('kiosk_id') or not job.get('callback_url'):
        return jsonify({"status": "error", "message": "Missing kiosk_id or callback_url"}), 400

    thread = threading.Thread(target=run_ai_task, args=(job,))
    thread.daemon = True
    thread.start()

    return jsonify({
        "status": "accepted",
        "message": f"Worker processing template for {job.get('kiosk_name')}"
    }), 202


# ==============================================================================
# NEW: UNIVERSAL AI EXECUTOR (For Flyers, and eventually everything else)
# ==============================================================================
def run_universal_task(job):
    task_id = job.get('task_id')
    callback_url = job.get('callback_url')
    system_prompt = job.get('system_prompt', '')
    user_prompt = job.get('user_prompt', '')
    secret = (job.get('secret') or os.environ.get('BUILDER_SECRET_KEY') or '').strip()

    print(f"🚀 [WORKER] Starting Universal AI Task #{task_id}")

    try:
        # Call the new universal generator in ai_builder.py
        html = generate_universal_template(system_prompt, user_prompt)

        if not html:
            print(f"⚠️ [WORKER] Universal generation returned empty for #{task_id}.")
            return

        headers = {
            "Authorization": f"Bearer {secret}",
            "Content-Type": "application/json"
        }
        payload = {
            "task_id": task_id,
            "status": "success",
            "html": html
        }

        print(f"📦 [WORKER] Delivering Universal result to: {callback_url}")
        res = requests.post(callback_url, json=payload, headers=headers, timeout=30)
        print(f"✅ [WORKER] Main app accepted callback. Status: {res.status_code}")

    except Exception as e:
        print(f"❌ [WORKER] Error during Universal task #{task_id}: {e}")
        # Send error back to main app so it doesn't hang forever
        requests.post(callback_url, json={
            "task_id": task_id, 
            "status": "error", 
            "message": str(e)
        }, headers={"Authorization": f"Bearer {secret}", "Content-Type": "application/json"})


@app.route('/execute', methods=['POST'])
def execute_endpoint():
    job = request.get_json() or {}

    if not job.get('task_id') or not job.get('callback_url') or not job.get('system_prompt'):
        return jsonify({"status": "error", "message": "Missing task_id, callback_url, or system_prompt"}), 400

    thread = threading.Thread(target=run_universal_task, args=(job,))
    thread.daemon = True
    thread.start()

    return jsonify({
        "status": "accepted",
        "message": "Universal task queued for processing",
        "task_id": job.get('task_id')
    }), 202


# ==============================================================================
# HEALTH CHECKS
# ==============================================================================
@app.route('/health', methods=['GET'])
@app.route('/', methods=['GET'])
def health():
    return jsonify({
        "status": "online",
        "service": "marketplace-ai-worker",
        "endpoints": ["/build (kiosk)", "/execute (universal)"]
    }), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
