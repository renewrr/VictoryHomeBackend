from flask import request, jsonify
from apiflask import APIBlueprint
from app.decorators import public
from app.repositories.webhooks_repo import WebhookRepository
import time

webhooks_bp = APIBlueprint("webhooks_bp", __name__, tag="Webhooks System")


@webhooks_bp.route("/google-forms", methods=["POST"])
@public
def google_forms_webhook():
    payload = request.get_json() or {}
    response_id = payload.get("responseId")
    timestamp = payload.get("timestamp", "")
    answers = payload.get("answers", {})

    if not response_id:
        return jsonify({"error": "Missing responseId"}), 400
    WebhookRepository.post_webhook_message(response_id, timestamp, answers)

    return jsonify({"status": "success", "received_id": response_id}), 200


@webhooks_bp.route("/google-forms-batch", methods=["POST"])
@public
def google_forms_webhook_batch():
    payload = request.get_json() or []
    t0 = time.perf_counter()
    WebhookRepository.batch_post_webhook_message(payload)
    t1 = time.perf_counter()

    return (
        jsonify(
            {"status": "success", "received_rows": len(payload), "used_time": t1 - t0}
        ),
        200,
    )
