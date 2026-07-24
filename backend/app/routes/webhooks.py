from flask import request, jsonify
from apiflask import APIBlueprint
from app.decorators import public

webhooks_bp = APIBlueprint("webhooks_bp", __name__, tag="Webhooks System")


@webhooks_bp.route("/google-forms", methods=["POST"])
@public
def google_forms_webhook():
    data = request.get_json()

    # Process the form response (e.g., parse payload, write to SQLAlchemy)
    response_id = data.get("responseId")
    answers = data.get("answers", {})
    print(response_id, answers, flush=True)

    # Example SQLAlchemy record creation
    # submission = FormSubmission(form_response_id=response_id, payload=answers)
    # db.session.add(submission)
    # db.session.commit()

    return jsonify({"status": "success", "received_id": response_id}), 200
