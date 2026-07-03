from flask_jwt_extended import create_access_token
from app.models.user import User
from app.extensions import bcrypt


def login_user(email, password):

    # Find user by email
    user = User.query.filter_by(email=email).first()

    # User not found
    if not user:
        return {
            "success": False,
            "message": "Invalid email or password"
        }, 401

    # Check if OAuth-only user
    if user.password is None:
        return {
            "success": False,
            "message": "This account uses Google/GitHub sign-in. Please log in that way."
        }, 401

    # Check password
    if not bcrypt.check_password_hash(user.password, password):
        return {
            "success": False,
            "message": "Invalid email or password"
        }, 401

    # Generate JWT Token
    access_token = create_access_token(identity=str(user.id))

    return {
        "success": True,
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }, 200