from flask import Blueprint, request, jsonify
from app.services.auth.register_service import register_user
from marshmallow import ValidationError
from app.services.auth.login_service import login_user
from app.schemas.auth_schemas import RegisterSchema
from app.schemas.login_schemas import LoginSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User

auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)

register_schema = RegisterSchema()
login_schemas = LoginSchema()


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    try:
        validated_data = register_schema.load(data)
    except ValidationError as err:
        return jsonify({
            "success": False,
            "errors": err.messages
        }), 400

    response = register_user(
        validated_data["name"],
        validated_data["email"],
        validated_data["password"]
    )
    return jsonify(response)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    try:
        validated_data = login_schemas.load(data)
    except ValidationError as err:
        return jsonify({
            "success": False,
            "errors": err.messages
        }), 400

    response, status_code = login_user(
        validated_data["email"],
        validated_data["password"]
    )

    return jsonify(response), status_code


@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    return jsonify({
        "success": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }), 200