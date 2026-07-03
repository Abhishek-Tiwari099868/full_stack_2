from flask import Blueprint, request, redirect, url_for, current_app
from app.utils.oauth import oauth
from app.services.oauth.google_service import handle_google_user
from app.services.oauth.github_service import handle_github_user
import urllib.parse

oauth_bp = Blueprint("oauth", __name__, url_prefix="/api/oauth")


def _default_frontend_url():
    return current_app.config.get("FRONTEND_URL", "http://127.0.0.1:5500")


@oauth_bp.route("/google/login")
def google_login():
    frontend_url = request.args.get("frontend_url") or request.referrer or _default_frontend_url()
    redirect_uri = url_for("oauth.google_callback", _external=True)
    return oauth.google.authorize_redirect(
        redirect_uri,
        state=frontend_url,
        prompt="select_account"
    )


@oauth_bp.route("/google/callback")
def google_callback():
    frontend_url = request.args.get("state") or _default_frontend_url()

    error = request.args.get("error")
    if error:
        error_desc = request.args.get("error_description") or error
        return redirect(f"{frontend_url}?error={urllib.parse.quote(error_desc)}")

    try:
        token = oauth.google.authorize_access_token()
        user_info = token.get("userinfo")
        if not user_info:
            user_info = oauth.google.parse_id_token(token)

        jwt_token, user = handle_google_user(user_info)
        return redirect(f"{frontend_url}?token={jwt_token}")
    except Exception as e:
        current_app.logger.error(f"Google OAuth failed: {e}")
        return redirect(f"{frontend_url}?error=oauth_failed")


@oauth_bp.route("/github/login")
def github_login():
    frontend_url = request.args.get("frontend_url") or request.referrer or _default_frontend_url()
    redirect_uri = url_for("oauth.github_callback", _external=True)
    return oauth.github.authorize_redirect(redirect_uri, state=frontend_url)


@oauth_bp.route("/github/callback")
def github_callback():
    frontend_url = request.args.get("state") or _default_frontend_url()

    error = request.args.get("error")
    if error:
        error_desc = request.args.get("error_description") or error
        return redirect(f"{frontend_url}?error={urllib.parse.quote(error_desc)}")

    try:
        token = oauth.github.authorize_access_token()
        profile_resp = oauth.github.get("user")
        profile = profile_resp.json()

        email = profile.get("email")
        if not email:
            emails_resp = oauth.github.get("user/emails")
            emails = emails_resp.json()
            if isinstance(emails, list):
                for email_obj in emails:
                    if email_obj.get("primary") and email_obj.get("verified"):
                        email = email_obj.get("email")
                        break
                if not email and len(emails) > 0:
                    email = emails[0].get("email")

        if not email:
            email = f"{profile.get('login')}@users.noreply.github.com"

        user_info = {
            "id": profile.get("id"),
            "name": profile.get("name") or profile.get("login"),
            "login": profile.get("login"),
            "email": email,
            "avatar_url": profile.get("avatar_url")
        }

        jwt_token, user = handle_github_user(user_info)
        return redirect(f"{frontend_url}?token={jwt_token}")
    except Exception as e:
        current_app.logger.error(f"GitHub OAuth failed: {e}")
        return redirect(f"{frontend_url}?error=oauth_failed")
