from app.models.user import User
from app.extensions import db
from flask_jwt_extended import create_access_token
from datetime import datetime

def handle_github_user(user_info):
    raw_id = user_info.get("id")
    email = user_info.get("email")

    if raw_id is None or not email:
        raise ValueError("Invalid GitHub user information: 'id' and 'email' are required.")

    github_id = str(raw_id)
    name = user_info.get("name") or user_info.get("login") or email.split("@")[0]
    avatar_url = user_info.get("avatar_url")

    # 1. Search by github_id
    user = User.query.filter_by(github_id=github_id).first()

    if not user:
        # 2. Search by email for account linking
        user = User.query.filter_by(email=email).first()
        if user:
            user.github_id = github_id
            user.provider = "github"
            if avatar_url and not user.avatar_url:
                user.avatar_url = avatar_url
            user.updated_at = datetime.utcnow()
            db.session.commit()
        else:
            user = User(
                name=name,
                email=email,
                github_id=github_id,
                avatar_url=avatar_url,
                provider="github",
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
