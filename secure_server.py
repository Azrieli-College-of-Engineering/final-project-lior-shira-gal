from flask import Flask, request, make_response, redirect, url_for
import pickle
import base64
import os
import hmac
import hashlib

app = Flask(__name__)

COOKIE_NAME = "session"

# מפתח סודי לחתימה (בפרודקשן חייב להיות ב-ENV ולא בקוד)
SECRET_KEY = os.environ.get("SESSION_HMAC_KEY", "dev-only-change-me").encode("utf-8")


def _hmac_sha256(data: str) -> str:
    """Return hex digest of HMAC-SHA256 over data (string)."""
    return hmac.new(SECRET_KEY, data.encode("utf-8"), hashlib.sha256).hexdigest()


def sign_payload(payload_b64: str) -> str:
    """Create signed cookie value: payload.signature"""
    signature = _hmac_sha256(payload_b64)
    return f"{payload_b64}.{signature}"


def verify_and_extract(cookie_value: str) -> str | None:
    """Verify signature; if valid return payload_b64 else None."""
    try:
        payload_b64, sig = cookie_value.rsplit(".", 1)
    except ValueError:
        return None

    expected = _hmac_sha256(payload_b64)

    # השוואה בטוחה נגד timing attacks
    if not hmac.compare_digest(expected, sig):
        return None

    return payload_b64


def encode_session(session_dict: dict) -> str:
    raw = pickle.dumps(session_dict, protocol=pickle.HIGHEST_PROTOCOL)
    payload_b64 = base64.urlsafe_b64encode(raw).decode("utf-8")
    return sign_payload(payload_b64)


def decode_session(cookie_value: str) -> dict | None:
    payload_b64 = verify_and_extract(cookie_value)
    if payload_b64 is None:
        return None

    try:
        raw = base64.urlsafe_b64decode(payload_b64.encode("utf-8"))
        # ✅ deserialization רק אחרי אימות HMAC
        obj = pickle.loads(raw)
        return obj
    except Exception:
        return None


def get_session() -> dict:
    cookie_value = request.cookies.get(COOKIE_NAME)
    if not cookie_value:
        return {"logged_in": False, "user": None, "is_admin": False}

    session = decode_session(cookie_value)
    if not isinstance(session, dict):
        # אם משהו לא תקין (שינוי, שגיאה, לא dict) → נזרוק לסשן ברירת מחדל
        return {"logged_in": False, "user": None, "is_admin": False}

    session.setdefault("logged_in", False)
    session.setdefault("user", None)
    session.setdefault("is_admin", False)
    return session


def set_session(resp, session_dict: dict):
    resp.set_cookie(
        COOKIE_NAME,
        encode_session(session_dict),
        httponly=True,   # מומלץ: JS לא יוכל לקרוא את ה-cookie
        samesite="Lax"
    )
    return resp


@app.get("/")
def home():
    s = get_session()
    return f"""
    <h2>Secure Deserialization Demo (HMAC protected)</h2>

    <p>Logged in: <b>{s['logged_in']}</b></p>
    <p>User: <b>{s['user']}</b></p>
    <p>Admin: <b>{s['is_admin']}</b></p>

    <ul>
      <li><a href="/login?user=alice">Login as alice</a></li>
      <li><a href="/login?user=bob">Login as bob</a></li>
      <li><a href="/admin">Admin page</a></li>
      <li><a href="/logout">Logout</a></li>
    </ul>

    <p><b>Note:</b> The session cookie is Pickle + Base64, but protected with HMAC (integrity).</p>
    """


@app.get("/login")
def login():
    user = request.args.get("user", "guest")
    session = {"logged_in": True, "user": user, "is_admin": False}
    resp = make_response(redirect(url_for("home")))
    return set_session(resp, session)


@app.get("/admin")
def admin():
    s = get_session()
    if not s.get("logged_in"):
        return "Not logged in", 401
    if not s.get("is_admin"):
        return "Forbidden (not admin)", 403

    return f"""
    <h2>Admin Panel</h2>
    <p>Welcome, {s.get('user')}!</p>
    <p>If you tried to tamper with the cookie, HMAC should block it.</p>
    """


@app.get("/logout")
def logout():
    resp = make_response(redirect(url_for("home")))
    resp.delete_cookie(COOKIE_NAME)
    return resp


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
