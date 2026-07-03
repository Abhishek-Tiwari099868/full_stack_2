from app.models.user import User
from app.extensions import db, bcrypt


def register_user(name, email, password):

    # Check if email already exists
    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return {
            "success": False,
            "message": "Email already exists."
        }

    # Hash password
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    # Create user
    new_user = User(
        name=name,
        email=email,
        password=hashed_password
    )

    # Save to database
    db.session.add(new_user)
    db.session.commit()

    return {
        "success": True,
        "message": "User registered successfully."
    }