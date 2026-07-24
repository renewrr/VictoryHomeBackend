from flask import request, jsonify
from apiflask import APIBlueprint

webhooks_bp = APIBlueprint("service_user_bp", __name__, tag="Service User System")


@webhooks_bp.route("/google-forms", methods=["POST"])
def google_forms_webhook():
    data = request.get_json()

    # Process the form response (e.g., parse payload, write to SQLAlchemy)
    response_id = data.get("responseId")
    answers = data.get("answers", {})

    # Example SQLAlchemy record creation
    # submission = FormSubmission(form_response_id=response_id, payload=answers)
    # db.session.add(submission)
    # db.session.commit()

    return jsonify({"status": "success", "received_id": response_id}), 200
