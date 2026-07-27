from apiflask import APIFlask, abort
from app.database import db_manager
from app.jwt_loader import init_jwt_loaders
import os
import flask_jwt_extended
import datetime
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import request, current_app, jsonify
from flask_cors import CORS
import hmac

jwt = flask_jwt_extended.JWTManager()


def create_app():
    app = APIFlask(__name__)
    # Define allowed origins dynamically based on environment
    ALLOWED_ORIGINS = [
        "https://localhost:4200",  # Angular local dev server
        os.getenv(
            "FRONTEND_URL", "https://your-angular-app.onrender.com"
        ),  # Production Render URL
    ]
    # Configure CORS globally for all routes under /api/
    CORS(
        app,
        resources={r"/api/*": {"origins": ALLOWED_ORIGINS}},
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        supports_credentials=True,
    )
    app.secret_key = os.environ.get("APPLICATION_ENCRYPTION_KEY")
    if not app.secret_key:
        # Crash the application immediately at startup if the key is missing
        exit(
            "CRITICAL ERROR: Application encryption key is not set in the environment."
        )

    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_ENCRYPTION_KEY")
    if not app.config["JWT_SECRET_KEY"]:
        # Crash the application immediately at startup if the key is missing
        exit(
            "CRITICAL ERROR: Application encryption key is not set in the environment."
        )
    app.config["JWT_COOKIE_SECURE"] = True  # Requires HTTPS
    app.config["JWT_COOKIE_SAMESITE"] = "None"  # Allows cross-site/cross-origin cookies
    app.config["JWT_COOKIE_CSRF_PROTECT"] = True  # Enable CSRF protection (recommended)
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(hours=1)
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False
    app.config["OPENAPI_SERVERS"] = [
        {"url": "https://localhost:2540", "description": "API Gateway Server"}
    ]

    app.config["DATABASE_URI"] = os.environ.get(
        "DATABASE_URI", "https://localhost:2540"
    )
    app.config["SPEC_PROCESSOR_PASS_OBJECT"] = True
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,  # <-- CRITICAL FOR HTTPS Fix
        x_host=1,
        x_port=1,
    )
    app.config["WEBHOOK_SECRET"] = os.environ.get(
        "GOOGLE_FORMS_WEBHOOK_SECRET", "your-secure-secret"
    )

    @app.before_request
    def enforce_default_security():
        # Ignore static files, schema JSONs, or Swagger docs
        print(request.endpoint, flush=True)
        if (
            request.endpoint == "webhooks_bp.google_forms_webhook"
            or request.endpoint == "webhooks_bp.google_forms_webhook_batch"
        ):
            client_secret = request.headers.get("X-Webhook-Secret")
            # Validate the secret using constant-time string comparison (prevents timing attacks)
            if not client_secret or not hmac.compare_digest(
                client_secret, app.config.get("WEBHOOK_SECRET", "")
            ):
                return abort(
                    401, message="Unauthorized: Invalid or missing webhook secret"
                )

            # Bypass JWT check for this route
            return
        if request.endpoint in [
            "specs",
            "swagger_ui",
            "redoc",
            "static",
            "openapi.spec",
        ]:
            return
        if request.method == "OPTIONS":
            return None  # Let Flask-CORS handle the response

        # Find the Python function handling the current request
        view_func = (
            current_app.view_functions.get(request.endpoint)
            if request.endpoint
            else None
        )
        if not view_func:
            return

        # 1. Check if the endpoint is explicitly marked as @public
        if getattr(view_func, "_is_public", False):
            return  # Allow access immediately

        # 2. Force JWT verification for everything else
        try:
            flask_jwt_extended.verify_jwt_in_request()
        except Exception as e:
            abort(401, message="Authentication token missing or invalid.")
        claims = flask_jwt_extended.get_jwt()
        perm = claims.get("mangement_privilege", False)
        twofactor = claims.get("is_2fa_verified", False)

        # 3. Determine required role: Check for custom tag, otherwise DEFAULT TO ADMIN
        required_role = getattr(
            view_func, "_required_role", "MANAGEMENT"
        )  # 🟢 Default is 'admin'!

        # 4. Enforce the privilege level
        # (Assuming your hierarchy is: admin > operator)
        if required_role == "MANAGEMENT" and not perm:
            abort(403, message="Access Denied. Administrator privileges required.")

    jwt.init_app(app)
    init_jwt_loaders(jwt)
    db_manager.init_app(app)

    from app.routes.auth import auth_bp

    app.register_blueprint(auth_bp, url_prefix="/api/v3/auth")

    from app.routes.handover import handover_bp

    app.register_blueprint(handover_bp, url_prefix="/api/v3/handover")

    from app.routes.operations import operations_bp

    app.register_blueprint(operations_bp, url_prefix="/api/v3/operations")

    from app.routes.personnel import personnel_bp

    app.register_blueprint(personnel_bp, url_prefix="/api/v3/personnel")

    from app.routes.service_user import service_user_bp

    app.register_blueprint(service_user_bp, url_prefix="/api/v3/serviceuser")

    from app.routes.webhooks import webhooks_bp

    app.register_blueprint(webhooks_bp, url_prefix="/webhooks")

    return app
