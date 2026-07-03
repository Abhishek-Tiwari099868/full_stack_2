from app.models.user import User
from app.extensions import db
from flask_jwt_extended import create_access_token
from datetime import datetime

def handle_google_user(user_info):
    raw_id = user_info.get("sub")
    email = user_info.get("email")

    if raw_id is None or not email:
        raise ValueError("Invalid Google user information: 'sub' and 'email' are required.")

    google_id = str(raw_id)
    name = user_info.get("name") or email.split("@")[0]
    avatar_url = user_info.get("picture")

    # 1. Search by google_id
    user = User.query.filter_by(google_id=google_id).first()

    if not user:
        user = User.query.filter_by(email=email).first()
        if user:
            user.google_id = google_id
            user.provider = "google"
            if avatar_url and not user.avatar_url:
                user.avatar_url = avatar_url
            user.updated_at = datetime.utcnow()
            db.session.commit()
        else:
            user = User(
                name=name,
                email=email,
                google_id=google_id,
                avatar_url=avatar_url,
                provider="google",
                password=None
            )
            db.session.add(user)
            db.session.commit()
    else:
        updated = False
        if avatar_url and user.avatar_url != avatar_url:
            user.avatar_url = avatar_url
            updated = True
        if name and user.name != name:
            user.name = name
            updated = True
        if updated:
            user.updated_at = datetime.utcnow()
            db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    return access_token, user
