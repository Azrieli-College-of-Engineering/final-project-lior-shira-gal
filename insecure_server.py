from flask import Flask, request, make_response, redirect, url_for
import pickle
import base64

app = Flask(__name__)

# =========================
# Insecure session cookie
# =========================
# השרת ישמור "סשן" כ-cookie שהלקוח מחזיק.
# ה-cookie מכיל base64 של pickle.dumps(dict).
# הבעיה: הלקוח יכול לשנות את התוכן, והשרת עדיין יעשה loads.

COOKIE_NAME = "session"


def encode_session(session_dict: dict) -> str:
    raw = pickle.dumps(session_dict, protocol=pickle.HIGHEST_PROTOCOL)
    return base64.urlsafe_b64encode(raw).decode("utf-8")


def decode_session(cookie_value: str) -> dict | None:
    try:
        raw = base64.urlsafe_b64decode(cookie_value.encode("utf-8"))
        # ⚠️ נקודת התורפה: deserialization על נתון שמגיע מהלקוח
        return pickle.loads(raw)
    except Exception:
        return None


def get_session() -> dict:
    cookie_value = request.cookies.get(COOKIE_NAME)
    if not cookie_value:
        return {"logged_in": False, "user": None, "is_admin": False}
    session = decode_session(cookie_value)
    if not isinstance(session, dict):
        return {"logged_in": False, "user": None, "is_admin": False}
    # ברירת מחדל אם חסרים שדות
    session.setdefault("logged_in", False)
    session.setdefault("user", None)
    session.setdefault("is_admin", False)
    return session


def set_session(resp, session_dict: dict):
    resp.set_cookie(
        COOKIE_NAME,
        encode_session(session_dict),
        httponly=False,   # בכוונה לא "הכי בטוח" כדי שיהיה קל להדגים שינוי לקוח
        samesite="Lax"
    )
    return resp

# =========================
# Routes
# =========================


@app.get("/")
def home():
    s = get_session()
    return f"""
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>Insecure Deserialization Demo</title>
      <style>
        :root {{
          --bg: #0b1220;
          --card: #121a2b;
          --muted: #9fb0d0;
          --text: #e9eefc;
          --accent: #5EC0BC;
          --danger: #ff5d5d;
          --warning: #ffcc66;
          --border: rgba(255,255,255,.08);
          --shadow: 0 18px 50px rgba(0,0,0,.45);
          --radius: 16px;
          --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
          --sans: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
        }}
        * {{ box-sizing: border-box; }}
        body {{
          margin: 0;
          font-family: var(--sans);
          background: radial-gradient(1000px 700px at 15% 10%, rgba(94,192,188,.20), transparent 60%),
                      radial-gradient(900px 600px at 80% 20%, rgba(255,204,102,.14), transparent 60%),
                      var(--bg);
          color: var(--text);
          min-height: 100vh;
          display: grid;
          place-items: center;
          padding: 32px 16px;
        }}
        .wrap {{
          width: min(980px, 100%);
          display: grid;
          gap: 16px;
        }}
        .header {{
          display: flex;
          justify-content: space-between;
          align-items: flex-end;
          gap: 12px;
        }}
        .title {{
          margin: 0;
          font-size: 28px;
          letter-spacing: .2px;
        }}
        .subtitle {{
          margin: 6px 0 0 0;
          color: var(--muted);
          font-size: 14px;
        }}
        .pill {{
          font-family: var(--mono);
          font-size: 12px;
          color: rgba(233,238,252,.9);
          border: 1px solid var(--border);
          background: rgba(18,26,43,.7);
          padding: 8px 10px;
          border-radius: 999px;
          backdrop-filter: blur(8px);
        }}
        .grid {{
          display: grid;
          grid-template-columns: 1.2fr .8fr;
          gap: 16px;
        }}
        @media (max-width: 860px) {{
          .grid {{ grid-template-columns: 1fr; }}
        }}
        .card {{
          background: linear-gradient(180deg, rgba(18,26,43,.92), rgba(18,26,43,.75));
          border: 1px solid var(--border);
          border-radius: var(--radius);
          box-shadow: var(--shadow);
          padding: 18px;
        }}
        .section-title {{
          margin: 0 0 12px 0;
          font-size: 16px;
          color: rgba(233,238,252,.95);
          letter-spacing: .2px;
        }}
        .stats {{
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 12px;
          margin-top: 6px;
        }}
        @media (max-width: 520px) {{
          .stats {{ grid-template-columns: 1fr; }}
        }}
        .stat {{
          border: 1px solid var(--border);
          border-radius: 14px;
          padding: 12px;
          background: rgba(255,255,255,.03);
        }}
        .label {{
          color: var(--muted);
          font-size: 12px;
          margin-bottom: 6px;
        }}
        .value {{
          font-size: 18px;
          font-weight: 700;
        }}
        .value.mono {{
          font-family: var(--mono);
          font-weight: 600;
          font-size: 15px;
        }}
        .badge {{
          display: inline-flex;
          align-items: center;
          gap: 8px;
          border-radius: 999px;
          padding: 6px 10px;
          font-size: 12px;
          border: 1px solid var(--border);
          background: rgba(255,255,255,.03);
        }}
        .dot {{
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: var(--muted);
        }}
        .dot.ok {{ background: var(--accent); }}
        .dot.no {{ background: var(--danger); }}
        .actions {{
          display: grid;
          gap: 10px;
          margin-top: 10px;
        }}
        .btn {{
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 12px;
          padding: 12px 14px;
          border-radius: 14px;
          border: 1px solid var(--border);
          background: rgba(255,255,255,.03);
          color: var(--text);
          text-decoration: none;
          transition: transform .08s ease, border-color .2s ease, background .2s ease;
        }}
        .btn:hover {{
          transform: translateY(-1px);
          border-color: rgba(94,192,188,.55);
          background: rgba(94,192,188,.08);
        }}
        .btn .hint {{
          color: var(--muted);
          font-size: 12px;
          font-family: var(--mono);
        }}
        .btn.danger:hover {{
          border-color: rgba(255,93,93,.65);
          background: rgba(255,93,93,.08);
        }}
        .note {{
          margin-top: 14px;
          padding: 12px 14px;
          border-radius: 14px;
          border: 1px dashed rgba(255,255,255,.18);
          background: rgba(255,255,255,.02);
          color: rgba(233,238,252,.9);
          font-size: 13px;
          line-height: 1.45;
        }}
        code {{
          font-family: var(--mono);
          font-size: 12px;
          background: rgba(255,255,255,.06);
          padding: 2px 6px;
          border-radius: 8px;
          border: 1px solid rgba(255,255,255,.08);
        }}
      </style>
    </head>

    <body>
      <div class="wrap">
        <div class="header">
          <div>
            <h1 class="title">Insecure Deserialization Demo</h1>
            <p class="subtitle">Localhost • Cookie session stored using <code>pickle</code> (unsafe)</p>
          </div>
          <div class="pill">http://127.0.0.1:5000</div>
        </div>

        <div class="grid">
          <div class="card">
            <h2 class="section-title">Session status</h2>

            <div style="display:flex; gap:10px; flex-wrap:wrap;">
              <span class="badge">
                <span class="dot {'ok' if s['logged_in'] else 'no'}"></span>
                Logged in: <b>{s['logged_in']}</b>
              </span>
              <span class="badge">
                <span class="dot {'ok' if s['is_admin'] else 'no'}"></span>
                Admin: <b>{s['is_admin']}</b>
              </span>
            </div>

            <div class="stats">
              <div class="stat">
                <div class="label">User</div>
                <div class="value mono">{s['user']}</div>
              </div>
              <div class="stat">
                <div class="label">Cookie name</div>
                <div class="value mono">{COOKIE_NAME}</div>
              </div>
              <div class="stat">
                <div class="label">Vulnerability</div>
                <div class="value">Pickle loads</div>
              </div>
            </div>

            <div class="note">
              <b>Why is this vulnerable?</b><br/>
              The session lives in a client-controlled cookie. The server blindly performs
              <code>pickle.loads</code> on cookie data → session tampering / privilege escalation is possible.
            </div>
          </div>

          <div class="card">
            <h2 class="section-title">Actions</h2>
            <div class="actions">
              <a class="btn" href="/login?user=alice">
                <span>Login as alice</span>
                <span class="hint">/login?user=alice</span>
              </a>
              <a class="btn" href="/login?user=bob">
                <span>Login as bob</span>
                <span class="hint">/login?user=bob</span>
              </a>
              <a class="btn" href="/admin">
                <span>Admin page</span>
                <span class="hint">/admin</span>
              </a>
              <a class="btn danger" href="/logout">
                <span>Logout</span>
                <span class="hint">/logout</span>
              </a>
            </div>

            <div class="note">
              <b>Tip for the demo:</b><br/>
              Open DevTools → Application → Cookies → <code>{COOKIE_NAME}</code><br/>
              Observe how the session is stored client-side.
            </div>
          </div>
        </div>
      </div>
    </body>
    </html>
    """

    s = get_session()
    return f"""
    <h2>Insecure Deserialization Demo (localhost)</h2>
    <p>Logged in: <b>{s['logged_in']}</b></p>
    <p>User: <b>{s['user']}</b></p>
    <p>Admin: <b>{s['is_admin']}</b></p>

    <ul>
      <li><a href="/login?user=alice">Login as alice</a></li>
      <li><a href="/login?user=bob">Login as bob</a></li>
      <li><a href="/admin">Admin page</a></li>
      <li><a href="/logout">Logout</a></li>
    </ul>

    <p><b>Note:</b> The session is stored in a client cookie using Pickle (unsafe).</p>
    """


@app.get("/login")
def login():
    user = request.args.get("user", "guest")
    # "לוגין" פיקטיבי: כל אחד יכול להתחבר, אדמין תמיד False
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
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>Admin Panel</title>
      <style>
        body {{
          margin: 0;
          font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
          background: #0b1220;
          color: #e9eefc;
          display: grid;
          place-items: center;
          min-height: 100vh;
          padding: 24px;
        }}
        .card {{
          width: min(720px, 100%);
          background: rgba(18,26,43,.9);
          border: 1px solid rgba(255,255,255,.10);
          border-radius: 16px;
          padding: 22px;
          box-shadow: 0 18px 50px rgba(0,0,0,.45);
        }}
        h2 {{ margin: 0 0 8px 0; }}
        p {{ margin: 8px 0; color: rgba(233,238,252,.9); line-height: 1.5; }}
        .mono {{
          font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
          background: rgba(255,255,255,.06);
          border: 1px solid rgba(255,255,255,.08);
          padding: 2px 6px;
          border-radius: 8px;
          font-size: 12px;
        }}
        a {{
          display: inline-block;
          margin-top: 14px;
          text-decoration: none;
          color: #0b1220;
          background: #5EC0BC;
          padding: 10px 14px;
          border-radius: 12px;
          font-weight: 700;
        }}
      </style>
    </head>
    <body>
      <div class="card">
        <h2>Admin Panel</h2>
        <p>Welcome, <b>{s.get('user')}</b>!</p>
        <p class="mono">If you reached here by changing the cookie, that's the vulnerability.</p>
        <a href="/">Back to Home</a>
      </div>
    </body>
    </html>
    """

    s = get_session()
    if not s.get("logged_in"):
        return "Not logged in", 401
    if not s.get("is_admin"):
        return "Forbidden (not admin)", 403
    return f"""
    <h2>Admin Panel</h2>
    <p>Welcome, {s.get('user')}!</p>
    <p>⚠️ If you reached here by changing the cookie, that's the vulnerability.</p>
    """


@app.get("/logout")
def logout():
    resp = make_response(redirect(url_for("home")))
    resp.delete_cookie(COOKIE_NAME)
    return resp


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
