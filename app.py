import os
import sys
import time
import queue
import threading
import requests
from flask import Flask, request, jsonify
from ai_builder import generate_kiosk_template

app = Flask(__name__)

# ⚙️ Configuration for N or T Activation
# N = Number of items in buffer before activating immediately
# T = Max seconds to wait before activating whatever is in the buffer
BATCH_N = int(os.environ.get('QUEUE_BATCH_N', 2))
TIMEOUT_T = int(os.environ.get('QUEUE_TIMEOUT_T', 20))

# Thread-safe intake queue
task_queue = queue.Queue()


def process_single_job(job):
    """Executes AI generation and delivers callback to Vercel."""
    kiosk_id = job.get('kiosk_id')
    kiosk_name = job.get('kiosk_name', 'Store')
    callback_url = job.get('callback_url')
    secret = job.get('secret')

    print(f"🚀 [WORKER] Generating template for #{kiosk_id}: {kiosk_name}", flush=True)

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
            print(f"⚠️ [WORKER] Generation returned empty for #{kiosk_id}.", flush=True)
            return

        headers = {
            "Authorization": f"Bearer {secret}",
            "Content-Type": "application/json"
        }
        payload = {
            "kiosk_id": kiosk_id,
            "custom_html": html
        }

        print(f"📦 [WORKER] Delivering completed HTML to Vercel: {callback_url}", flush=True)
        res = requests.post(callback_url, json=payload, headers=headers, timeout=30)
        print(f"✅ [WORKER] Vercel accepted callback for #{kiosk_id}. Status: {res.status_code}", flush=True)

    except Exception as e:
        print(f"❌ [WORKER] Error processing #{kiosk_id}: {e}", flush=True)


def n_or_t_consumer_loop():
    """
    Dedicated worker loop:
    Buffers incoming jobs until either:
      1. N jobs are collected, OR
      2. T seconds have passed since the first job arrived.
    """
    print(f"👷 [QUEUE ENGINE] Started with requirements: N={BATCH_N} jobs OR T={TIMEOUT_T}s window.", flush=True)

    while True:
        # Step 1: Wait for the first job to arrive (blocking)
        first_job = task_queue.get()
        if first_job is None:
            break

        buffer = [first_job]
        first_arrival_time = time.time()
        print(f"📥 [BUFFER] First job #{first_job.get('kiosk_id')} arrived. Window started (Waiting for N={BATCH_N} or T={TIMEOUT_T}s)...", flush=True)

        # Step 2: Accumulate jobs until N items reached OR T seconds expire
        while len(buffer) < BATCH_N:
            time_elapsed = time.time() - first_arrival_time
            remaining_time = TIMEOUT_T - time_elapsed

            if remaining_time <= 0:
                print(f"⏰ [ACTIVATION: T EXPIRED] {TIMEOUT_T}s limit reached. Triggering activation with {len(buffer)} job(s) in buffer.", flush=True)
                break

            try:
                # Wait for next item up to the remaining time of T
                next_job = task_queue.get(timeout=remaining_time)
                buffer.append(next_job)
                print(f"📥 [BUFFER] Added job #{next_job.get('kiosk_id')}. Buffer status: {len(buffer)}/{BATCH_N}", flush=True)

                if len(buffer) >= BATCH_N:
                    print(f"⚡ [ACTIVATION: N REACHED] Target threshold N={BATCH_N} reached! Triggering immediate activation.", flush=True)
                    break

            except queue.Empty:
                print(f"⏰ [ACTIVATION: T EXPIRED] {TIMEOUT_T}s window elapsed with no new jobs. Activating buffer.", flush=True)
                break

        # Step 3: Process the activated batch one-by-one to preserve 512MB RAM limit
        print(f"🔥 [EXECUTION] Activating batch of {len(buffer)} job(s)...", flush=True)
        for job in buffer:
            try:
                process_single_job(job)
            finally:
                task_queue.task_done()

        print("🏁 [EXECUTION] Batch completed. Worker is idle and waiting for next window...", flush=True)


# Launch the N-or-T consumer daemon
consumer_thread = threading.Thread(target=n_or_t_consumer_loop, daemon=True)
consumer_thread.start()


# =============================================================
# 🟢 UPTIMEROBOT & HEALTHCHECK ENDPOINT
# =============================================================
@app.route('/', methods=['GET', 'HEAD'])
@app.route('/health', methods=['GET', 'HEAD'])
def health():
    """Returns in < 1ms to keep UptimeRobot happy without interfering with the buffer."""
    return jsonify({
        "status": "online",
        "service": "marketplace-ai-worker",
        "queue_depth": task_queue.qsize(),
        "n_requirement": BATCH_N,
        "t_requirement_seconds": TIMEOUT_T
    }), 200


# =============================================================
# 📥 JOB INTAKE ENDPOINT
# =============================================================
@app.route('/build', methods=['POST'])
def build_endpoint():
    job = request.get_json() or {}

    if not job.get('kiosk_id') or not job.get('callback_url'):
        return jsonify({"status": "error", "message": "Missing kiosk_id or callback_url"}), 400

    task_queue.put(job)
    current_depth = task_queue.qsize()
    print(f"📥 [INTAKE] Enqueued #{job.get('kiosk_id')}: {job.get('kiosk_name')} (Queue depth: {current_depth})", flush=True)

    return jsonify({
        "status": "queued",
        "message": f"Job for {job.get('kiosk_name')} buffered.",
        "queue_depth": current_depth,
        "n_requirement": BATCH_N,
        "t_requirement_seconds": TIMEOUT_T
    }), 202


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
