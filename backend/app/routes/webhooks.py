from flask import request, jsonify
from apiflask import APIBlueprint
from app.decorators import public
from app.repositories.webhooks_repo import WebhookRepository

webhooks_bp = APIBlueprint("webhooks_bp", __name__, tag="Webhooks System")


@webhooks_bp.route("/google-forms", methods=["POST"])
@public
def google_forms_webhook():
    payload = request.get_json() or {}
    response_id = payload.get("responseId")
    timestamp = payload.get("timestamp")
    answers = payload.get("answers", {})

    if not response_id:
        return jsonify({"error": "Missing responseId"}), 400
    WebhookRepository.post_webhook_message(response_id, timestamp, answers)

    return jsonify({"status": "success", "received_id": response_id}), 200
