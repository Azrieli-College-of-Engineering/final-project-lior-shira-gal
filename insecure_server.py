import pickle
import base64
import sys
from datetime import datetime, timedelta
from flask import Flask, request, make_response, redirect, url_for

sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)

COOKIE_NAME = "booking_session"

FLIGHTS = {
    "TLV-NYC": {"price": 1200, "destination": "New York", "origin": "Tel Aviv"},
    "TLV-LON": {"price": 450, "destination": "London", "origin": "Tel Aviv"},
    "TLV-PAR": {"price": 380, "destination": "Paris", "origin": "Tel Aviv"},
    "TLV-BKK": {"price": 850, "destination": "Bangkok", "origin": "Tel Aviv"},
}


def encode_session(session_dict: dict) -> str:
    raw = pickle.dumps(session_dict, protocol=pickle.HIGHEST_PROTOCOL)
    return base64.urlsafe_b64encode(raw).decode("utf-8")


def decode_session(cookie_value: str) -> dict | None:
    try:
        raw = base64.urlsafe_b64decode(cookie_value.encode("utf-8"))
        return pickle.loads(raw)
    except Exception:
        return None


def get_session() -> dict:
    cookie_value = request.cookies.get(COOKIE_NAME)
    if not cookie_value:
        return {
            "logged_in": False,
            "user": None,
            "is_vip": False,
            "bookings": [],
            "loyalty_points": 0
        }
    session = decode_session(cookie_value)
    if not isinstance(session, dict):
        return {
            "logged_in": False,
            "user": None,
            "is_vip": False,
            "bookings": [],
            "loyalty_points": 0
        }
    session.setdefault("logged_in", False)
    session.setdefault("user", None)
    session.setdefault("is_vip", False)
    session.setdefault("bookings", [])
    session.setdefault("loyalty_points", 0)
    return session


def set_session(resp, session_dict: dict):
    resp.set_cookie(
        COOKIE_NAME,
        encode_session(session_dict),
        httponly=False,
        samesite="Lax"
    )
    return resp


@app.get("/")
def home():
    s = get_session()
    next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

    return f"""
    <!doctype html>
    <html lang="en" dir="ltr">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>SkyFly ✈️ - Flight Booking</title>
      <style>
        * {{
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }}
        
        @keyframes gradient {{
          0% {{ background-position: 0% 50%; }}
          50% {{ background-position: 100% 50%; }}
          100% {{ background-position: 0% 50%; }}
        }}
        
        @keyframes float {{
          0%, 100% {{ transform: translateY(0px); }}
          50% {{ transform: translateY(-15px); }}
        }}
        
        @keyframes slideIn {{
          from {{ opacity: 0; transform: translateY(30px); }}
          to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        @keyframes pulse {{
          0%, 100% {{ opacity: 1; transform: scale(1); }}
          50% {{ opacity: 0.9; transform: scale(1.05); }}
        }}
        
        body {{
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
          background: linear-gradient(-45deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #00d4ff 75%, #0095ff 100%);
          background-size: 400% 400%;
          animation: gradient 20s ease infinite;
          color: #333;
          line-height: 1.6;
          padding: 2rem 1rem;
          min-height: 100vh;
        }}
        
        .container {{
          max-width: 1400px;
          margin: 0 auto;
          animation: slideIn 0.6s ease-out;
        }}
        
        .header {{
          text-align: center;
          margin-bottom: 3rem;
          color: white;
        }}
        
        .logo {{
          font-size: 3.5rem;
          margin-bottom: 0.5rem;
          animation: float 4s ease-in-out infinite;
          filter: drop-shadow(0 10px 25px rgba(0,0,0,0.3));
        }}
        
        .header h1 {{
          font-size: 2.8rem;
          font-weight: 800;
          background: linear-gradient(135deg, #fff 0%, #e0e0e0 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          margin-bottom: 0.5rem;
          text-shadow: 0 4px 20px rgba(0,0,0,0.2);
        }}
        
        .header p {{
          color: rgba(255,255,255,0.95);
          font-size: 1.2rem;
        }}
        
        .user-bar {{
          display: flex;
          justify-content: space-between;
          align-items: center;
          background: rgba(255,255,255,0.95);
          padding: 1.25rem 2rem;
          border-radius: 1.5rem;
          margin-bottom: 2rem;
          box-shadow: 0 15px 50px rgba(0,0,0,0.15);
          flex-wrap: wrap;
          gap: 1rem;
        }}
        
        .user-info {{
          display: flex;
          align-items: center;
          gap: 1rem;
        }}
        
        .user-badge {{
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.75rem 1.5rem;
          border-radius: 9999px;
          font-weight: 600;
          border: 2px solid;
        }}
        
        .user-badge.logged-in {{
          background: linear-gradient(135deg, rgba(34,197,94,0.2), rgba(34,197,94,0.1));
          border-color: #22c55e;
          color: #15803d;
        }}
        
        .user-badge.logged-out {{
          background: linear-gradient(135deg, rgba(239,68,68,0.2), rgba(239,68,68,0.1));
          border-color: #ef4444;
          color: #991b1b;
        }}
        
        .vip-badge {{
          background: linear-gradient(135deg, #fbbf24, #f59e0b);
          color: white;
          padding: 0.5rem 1.25rem;
          border-radius: 9999px;
          font-weight: 700;
          font-size: 0.9rem;
          box-shadow: 0 5px 15px rgba(251,191,36,0.4);
          animation: pulse 3s ease-in-out infinite;
        }}
        
        .points {{
          background: linear-gradient(135deg, #667eea, #764ba2);
          color: white;
          padding: 0.5rem 1.25rem;
          border-radius: 9999px;
          font-weight: 600;
          font-size: 0.9rem;
        }}
        
        .user-actions {{
          display: flex;
          gap: 1rem;
          flex-wrap: wrap;
        }}
        
        .btn {{
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem 1.5rem;
          border-radius: 0.75rem;
          text-decoration: none;
          font-weight: 600;
          transition: all 0.3s ease;
          border: 2px solid;
          font-size: 0.95rem;
        }}
        
        .btn:hover {{
          transform: translateY(-2px);
          box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }}
        
        .btn-primary {{
          background: linear-gradient(135deg, #667eea, #764ba2);
          border-color: #667eea;
          color: white;
        }}
        
        .btn-secondary {{
          background: white;
          border-color: #d1d5db;
          color: #374151;
        }}
        
        .btn-danger {{
          background: linear-gradient(135deg, #f093fb, #f5576c);
          border-color: #f5576c;
          color: white;
        }}
        
        .grid {{
          display: grid;
          grid-template-columns: 2fr 1fr;
          gap: 2rem;
          margin-top: 2rem;
        }}
        
        @media (max-width: 1024px) {{
          .grid {{
            grid-template-columns: 1fr;
          }}
        }}
        
        .card {{
          background: white;
          border-radius: 1.5rem;
          padding: 2rem;
          box-shadow: 0 20px 60px rgba(0,0,0,0.1);
          animation: slideIn 0.8s ease-out;
        }}
        
        .card-title {{
          font-size: 1.75rem;
          font-weight: 700;
          color: #1f2937;
          margin-bottom: 1.5rem;
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }}
        
        .flight-list {{
          display: grid;
          gap: 1.25rem;
        }}
        
        .flight-card {{
          background: linear-gradient(135deg, rgba(102,126,234,0.05), rgba(118,75,162,0.05));
          border: 2px solid #e5e7eb;
          border-radius: 1.25rem;
          padding: 1.75rem;
          transition: all 0.3s ease;
          cursor: pointer;
        }}
        
        .flight-card:hover {{
          border-color: #667eea;
          box-shadow: 0 10px 30px rgba(102,126,234,0.2);
          transform: translateY(-3px);
        }}
        
        .flight-route {{
          display: flex;
          align-items: center;
          gap: 1rem;
          margin-bottom: 1rem;
        }}
        
        .flight-city {{
          font-size: 1.5rem;
          font-weight: 700;
          color: #1f2937;
        }}
        
        .flight-arrow {{
          font-size: 1.5rem;
          color: #667eea;
        }}
        
        .flight-details {{
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 1rem;
          margin-top: 1rem;
        }}
        
        .flight-detail {{
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }}
        
        .detail-label {{
          font-size: 0.75rem;
          color: #6b7280;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }}
        
        .detail-value {{
          font-size: 1rem;
          font-weight: 600;
          color: #1f2937;
        }}
        
        .price {{
          font-size: 1.75rem;
          font-weight: 800;
          background: linear-gradient(135deg, #667eea, #764ba2);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }}
        
        .sidebar {{
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }}
        
        .info-box {{
          background: linear-gradient(135deg, rgba(251,191,36,0.15), rgba(251,191,36,0.05));
          border: 2px solid rgba(251,191,36,0.5);
          border-radius: 1.25rem;
          padding: 1.5rem;
        }}
        
        .info-title {{
          font-weight: 700;
          color: #92400e;
          margin-bottom: 0.75rem;
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 1.1rem;
        }}
        
        .info-content {{
          color: #78350f;
          line-height: 1.7;
          font-size: 0.95rem;
        }}
        
        code {{
          font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
          background: rgba(0,0,0,0.1);
          padding: 0.2rem 0.5rem;
          border-radius: 0.375rem;
          font-size: 0.85em;
          color: #92400e;
          font-weight: 600;
        }}
        
        .stats {{
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1rem;
        }}
        
        .stat {{
          background: white;
          border: 2px solid #e5e7eb;
          border-radius: 1rem;
          padding: 1.25rem;
          text-align: center;
        }}
        
        .stat-value {{
          font-size: 1.75rem;
          font-weight: 800;
          color: #667eea;
          margin-bottom: 0.25rem;
        }}
        
        .stat-label {{
          font-size: 0.8rem;
          color: #6b7280;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }}
        
        .bookings-section {{
          margin-top: 1.5rem;
        }}
        
        .booking-item {{
          background: linear-gradient(135deg, rgba(34,197,94,0.1), rgba(34,197,94,0.05));
          border: 2px solid rgba(34,197,94,0.3);
          border-radius: 1rem;
          padding: 1rem;
          margin-bottom: 0.75rem;
        }}
        
        .booking-route {{
          font-weight: 600;
          color: #15803d;
          margin-bottom: 0.25rem;
        }}
        
        .booking-date {{
          font-size: 0.85rem;
          color: #166534;
        }}
        
        .empty-state {{
          text-align: center;
          padding: 2rem;
          color: #9ca3af;
        }}
        
        .empty-icon {{
          font-size: 3rem;
          margin-bottom: 1rem;
          opacity: 0.5;
        }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <div class="logo">✈️</div>
          <h1>SkyFly</h1>
          <p>Innovative and Secure Flight Booking Experience</p>
        </div>
        
        <div class="user-bar">
          <div class="user-info">
            <div class="user-badge {'logged-in' if s['logged_in'] else 'logged-out'}">
              <span>{'🟢' if s['logged_in'] else '🔴'}</span>
              <span>{'Logged in: ' + s['user'] if s['logged_in'] else 'Not logged in'}</span>
            </div>
            {f'<div class="vip-badge">⭐ VIP Member</div>' if s.get('is_vip') else ''}
            {f'<div class="points">💎 {s.get("loyalty_points", 0)} Points</div>' if s['logged_in'] else ''}
          </div>
          
          <div class="user-actions">
            {'''
            <a class="btn btn-primary" href="/login?user=alice">👤 Login as Alice</a>
            <a class="btn btn-primary" href="/login?user=bob">👤 Login as Bob</a>
            ''' if not s['logged_in'] else f'''
            <a class="btn btn-secondary" href="/vip-lounge">🌟 VIP Lounge</a>
            <a class="btn btn-danger" href="/logout">🚪 Logout</a>
            '''}
          </div>
        </div>
        
        <div class="grid">
          <div>
            <div class="card">
              <h2 class="card-title">
                <span>🌍</span>
                <span>Popular Flights</span>
              </h2>
              
              <div class="flight-list">
                <div class="flight-card" onclick="window.location.href='/book?flight=TLV-NYC'">
                  <div class="flight-route">
                    <span class="flight-city">TLV</span>
                    <span class="flight-arrow">✈️</span>
                    <span class="flight-city">NYC</span>
                  </div>
                  <div class="flight-details">
                    <div class="flight-detail">
                      <span class="detail-label">Date</span>
                      <span class="detail-value">{next_week}</span>
                    </div>
                    <div class="flight-detail">
                      <span class="detail-label">Duration</span>
                      <span class="detail-value">12 hours</span>
                    </div>
                    <div class="flight-detail">
                      <span class="detail-label">Price</span>
                      <span class="price">$1,200</span>
                    </div>
                  </div>
                </div>
                
                <div class="flight-card" onclick="window.location.href='/book?flight=TLV-LON'">
                  <div class="flight-route">
                    <span class="flight-city">TLV</span>
                    <span class="flight-arrow">✈️</span>
                    <span class="flight-city">LDN</span>
                  </div>
                  <div class="flight-details">
                    <div class="flight-detail">
                      <span class="detail-label">Date</span>
                      <span class="detail-value">{next_week}</span>
                    </div>
                    <div class="flight-detail">
                      <span class="detail-label">Duration</span>
                      <span class="detail-value">5 hours</span>
                    </div>
                    <div class="flight-detail">
                      <span class="detail-label">Price</span>
                      <span class="price">$450</span>
                    </div>
                  </div>
                </div>
                
                <div class="flight-card" onclick="window.location.href='/book?flight=TLV-PAR'">
                  <div class="flight-route">
                    <span class="flight-city">TLV</span>
                    <span class="flight-arrow">✈️</span>
                    <span class="flight-city">CDG</span>
                  </div>
                  <div class="flight-details">
                    <div class="flight-detail">
                      <span class="detail-label">Date</span>
                      <span class="detail-value">{next_week}</span>
                    </div>
                    <div class="flight-detail">
                      <span class="detail-label">Duration</span>
                      <span class="detail-value">4.5 hours</span>
                    </div>
                    <div class="flight-detail">
                      <span class="detail-label">Price</span>
                      <span class="price">$380</span>
                    </div>
                  </div>
                </div>
                
                <div class="flight-card" onclick="window.location.href='/book?flight=TLV-BKK'">
                  <div class="flight-route">
                    <span class="flight-city">TLV</span>
                    <span class="flight-arrow">✈️</span>
                    <span class="flight-city">BKK</span>
                  </div>
                  <div class="flight-details">
                    <div class="flight-detail">
                      <span class="detail-label">Date</span>
                      <span class="detail-value">{next_week}</span>
                    </div>
                    <div class="flight-detail">
                      <span class="detail-label">Duration</span>
                      <span class="detail-value">10 hours</span>
                    </div>
                    <div class="flight-detail">
                      <span class="detail-label">Price</span>
                      <span class="price">$850</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            {f'''
            <div class="card bookings-section">
              <h2 class="card-title">
                <span>📋</span>
                <span>My Bookings</span>
              </h2>
              {('<div class="empty-state"><div class="empty-icon">✈️</div><p>No active bookings</p></div>') if not s.get('bookings') else ''.join([f'<div class="booking-item"><div class="booking-route">{b}</div><div class="booking-date">{next_week}</div></div>' for b in s.get('bookings', [])])}
            </div>
            ''' if s['logged_in'] else ''}
          </div>

          <div class="sidebar">
            <div class="card">
              <h2 class="card-title">
                <span>📊</span>
                <span>Statistics</span>
              </h2>
              
              <div class="stats">
                <div class="stat">
                  <div class="stat-value">{len(s.get('bookings', []))}</div>
                  <div class="stat-label">Bookings</div>
                </div>
                <div class="stat">
                  <div class="stat-value">{s.get('loyalty_points', 0)}</div>
                  <div class="stat-label">Points</div>
                </div>
                <div class="stat">
                  <div class="stat-value">{'Yes' if s.get('is_vip') else 'No'}</div>
                  <div class="stat-label">VIP</div>
                </div>
                <div class="stat">
                  <div class="stat-value">{COOKIE_NAME}</div>
                  <div class="stat-label">Cookie</div>
                </div>
              </div>
            </div>

            <div class="info-box">
              <div class="info-title">
                <span>⚠️</span>
                <span>Security Vulnerability - Demo</span>
              </div>
              <div class="info-content">
                This site uses <code>pickle.loads()</code> on session data coming from the client.
                This allows the client to modify VIP status, loyalty points, and even execute Remote Code Execution.
                <br><br>
                Open DevTools → Application → Cookies → <code>{COOKIE_NAME}</code> to see the cookie.
              </div>
            </div>
          </div>
        </div>
      </div>
    </body>
    </html>
    """


@app.get("/login")
def login():
    user = request.args.get("user", "guest")
    session = {
        "logged_in": True,
        "user": user,
        "is_vip": False, 
        "bookings": [],
        "loyalty_points": 100
    }
    resp = make_response(redirect(url_for("home")))
    return set_session(resp, session)


@app.get("/book")
def book():
    s = get_session()
    if not s.get("logged_in"):
        return redirect(url_for("home"))
    
    flight_code = request.args.get("flight", "")
    if flight_code not in FLIGHTS:
        return redirect(url_for("home"))
    
    flight = FLIGHTS[flight_code]
    
    bookings = s.get("bookings", [])
    booking_text = f"{flight['origin']} → {flight['destination']}"
    if booking_text not in bookings:
        bookings.append(booking_text)

    s["loyalty_points"] = s.get("loyalty_points", 0) + 50
    s["bookings"] = bookings

    resp = make_response(redirect(url_for("home")))
    return set_session(resp, s)


@app.get("/vip-lounge")
def vip_lounge():
    s = get_session()

    if not s.get("logged_in"):
        return f"""
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <title>Login Required - SkyFly</title>
          <style>
            * {{
              margin: 0;
              padding: 0;
              box-sizing: border-box;
            }}

            @keyframes gradient {{
              0% {{ background-position: 0% 50%; }}
              50% {{ background-position: 100% 50%; }}
              100% {{ background-position: 0% 50%; }}
            }}

            body {{
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
              background: linear-gradient(-45deg, #f093fb 0%, #f5576c 25%, #ff6b6b 100%);
              background-size: 400% 400%;
              animation: gradient 15s ease infinite;
              display: flex;
              align-items: center;
              justify-content: center;
              min-height: 100vh;
              padding: 1rem;
            }}

            .card {{
              max-width: 500px;
              background: white;
              border-radius: 2rem;
              padding: 3rem 2rem;
              box-shadow: 0 30px 80px rgba(0,0,0,0.3);
              text-align: center;
            }}

            .icon {{
              font-size: 5rem;
              margin-bottom: 1.5rem;
            }}

            h1 {{
              font-size: 1.75rem;
              color: #1f2937;
              margin-bottom: 1rem;
            }}

            p {{
              color: #6b7280;
              margin-bottom: 2rem;
              font-size: 1.05rem;
            }}

            .btn {{
              display: inline-flex;
              align-items: center;
              gap: 0.75rem;
              padding: 1rem 2rem;
              background: linear-gradient(135deg, #667eea, #764ba2);
              color: white;
              text-decoration: none;
              border-radius: 1rem;
              font-weight: 600;
              transition: all 0.3s ease;
            }}

            .btn:hover {{
              transform: translateY(-2px);
              box-shadow: 0 10px 30px rgba(102,126,234,0.4);
            }}
          </style>
        </head>
        <body>
          <div class="card">
            <div class="icon">🔒</div>
            <h1>Login Required</h1>
            <p>You must be logged in to access the VIP lounge</p>
            <a href="/" class="btn">
              <span>🏠</span>
              <span>Go to Home</span>
            </a>
          </div>
        </body>
        </html>
        """, 401

    if not s.get("is_vip"):
        return f"""
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <title>Access Denied - SkyFly</title>
          <style>
            * {{
              margin: 0;
              padding: 0;
              box-sizing: border-box;
            }}

            @keyframes gradient {{
              0% {{ background-position: 0% 50%; }}
              50% {{ background-position: 100% 50%; }}
              100% {{ background-position: 0% 50%; }}
            }}

            @keyframes shake {{
              0%, 100% {{ transform: translateX(0); }}
              25% {{ transform: translateX(-5px); }}
              75% {{ transform: translateX(5px); }}
            }}

            body {{
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
              background: linear-gradient(-45deg, #ff6b6b 0%, #ee5a6f 25%, #f093fb 100%);
              background-size: 400% 400%;
              animation: gradient 15s ease infinite;
              display: flex;
              align-items: center;
              justify-content: center;
              min-height: 100vh;
              padding: 1rem;
            }}

            .card {{
              max-width: 550px;
              background: white;
              border-radius: 2rem;
              padding: 3rem 2rem;
              box-shadow: 0 30px 80px rgba(0,0,0,0.3);
              text-align: center;
            }}

            .icon {{
              font-size: 5rem;
              margin-bottom: 1.5rem;
              animation: shake 1s ease-in-out;
            }}

            h1 {{
              font-size: 1.75rem;
              color: #1f2937;
              margin-bottom: 1rem;
            }}

            p {{
              color: #6b7280;
              margin-bottom: 2rem;
              font-size: 1.05rem;
              line-height: 1.6;
            }}

            .info-box {{
              background: linear-gradient(135deg, rgba(251,191,36,0.15), rgba(251,191,36,0.05));
              border: 2px solid rgba(251,191,36,0.5);
              border-radius: 1rem;
              padding: 1.25rem;
              margin-bottom: 2rem;
              text-align: right;
            }}

            .info-title {{
              font-weight: 700;
              color: #92400e;
              margin-bottom: 0.5rem;
            }}

            .info-content {{
              color: #78350f;
              font-size: 0.95rem;
              line-height: 1.6;
            }}

            code {{
              font-family: 'SF Mono', Monaco, monospace;
              background: rgba(0,0,0,0.1);
              padding: 0.2rem 0.5rem;
              border-radius: 0.375rem;
              font-size: 0.85em;
              color: #92400e;
              font-weight: 600;
            }}

            .btn {{
              display: inline-flex;
              align-items: center;
              gap: 0.75rem;
              padding: 1rem 2rem;
              background: linear-gradient(135deg, #667eea, #764ba2);
              color: white;
              text-decoration: none;
              border-radius: 1rem;
              font-weight: 600;
              transition: all 0.3s ease;
            }}

            .btn:hover {{
              transform: translateY(-2px);
              box-shadow: 0 10px 30px rgba(102,126,234,0.4);
            }}
          </style>
        </head>
        <body>
          <div class="card">
            <div class="icon">⛔</div>
            <h1>Access Limited to VIP Members</h1>
            <p>Only VIP members can access the special lounge</p>

            <a href="/" class="btn">
              <span>Return</span>
            </a>
          </div>
        </body>
        </html>
        """, 403

    return f"""
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>VIP Lounge - SkyFly</title>
      <style>
        * {{
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }}

        @keyframes gradient {{
          0% {{ background-position: 0% 50%; }}
          50% {{ background-position: 100% 50%; }}
          100% {{ background-position: 0% 50%; }}
        }}

        @keyframes sparkle {{
          0%, 100% {{ opacity: 1; transform: scale(1); }}
          50% {{ opacity: 0.7; transform: scale(1.2); }}
        }}

        @keyframes float {{
          0%, 100% {{ transform: translateY(0); }}
          50% {{ transform: translateY(-20px); }}
        }}

        body {{
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          background: linear-gradient(-45deg, #fbbf24 0%, #f59e0b 25%, #d97706 50%, #b45309 100%);
          background-size: 400% 400%;
          animation: gradient 20s ease infinite;
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 100vh;
          padding: 2rem 1rem;
        }}

        .container {{
          max-width: 900px;
          width: 100%;
        }}
        
        .vip-icon {{
          font-size: 6rem;
          text-align: center;
          margin-bottom: 1rem;
          animation: float 4s ease-in-out infinite;
          filter: drop-shadow(0 15px 40px rgba(0,0,0,0.4));
        }}
        
        .card {{
          background: rgba(255,255,255,0.95);
          border-radius: 2rem;
          padding: 3rem 2.5rem;
          box-shadow: 0 30px 90px rgba(0,0,0,0.4);
          border: 3px solid rgba(251,191,36,0.5);
        }}
        
        h1 {{
          font-size: 2.5rem;
          font-weight: 800;
          text-align: center;
          background: linear-gradient(135deg, #fbbf24, #d97706);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          margin-bottom: 0.5rem;
        }}
        
        .subtitle {{
          text-align: center;
          color: #92400e;
          font-size: 1.1rem;
          margin-bottom: 2rem;
        }}
        
        .welcome-badge {{
          text-align: center;
          margin-bottom: 2rem;
        }}
        
        .badge {{
          display: inline-flex;
          align-items: center;
          gap: 0.75rem;
          padding: 1rem 2rem;
          background: linear-gradient(135deg, #fbbf24, #f59e0b);
          color: white;
          border-radius: 9999px;
          font-weight: 700;
          font-size: 1.15rem;
          box-shadow: 0 10px 30px rgba(251,191,36,0.5);
          animation: sparkle 3s ease-in-out infinite;
        }}
        
        .perks {{
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1.5rem;
          margin: 2rem 0;
        }}
        
        .perk {{
          background: linear-gradient(135deg, rgba(251,191,36,0.15), rgba(251,191,36,0.05));
          border: 2px solid rgba(251,191,36,0.3);
          border-radius: 1.25rem;
          padding: 1.75rem;
          text-align: center;
          transition: all 0.3s ease;
        }}
        
        .perk:hover {{
          transform: translateY(-5px);
          box-shadow: 0 15px 40px rgba(251,191,36,0.3);
          border-color: rgba(251,191,36,0.6);
        }}
        
        .perk-icon {{
          font-size: 2.5rem;
          margin-bottom: 0.75rem;
        }}
        
        .perk-title {{
          font-weight: 700;
          color: #92400e;
          margin-bottom: 0.5rem;
        }}
        
        .perk-desc {{
          color: #78350f;
          font-size: 0.95rem;
        }}
        
        .info-box {{
          background: linear-gradient(135deg, rgba(34,197,94,0.15), rgba(34,197,94,0.05));
          border: 2px solid rgba(34,197,94,0.5);
          border-radius: 1.25rem;
          padding: 1.5rem;
          margin: 2rem 0;
        }}
        
        .info-title {{
          font-weight: 700;
          color: #15803d;
          margin-bottom: 0.75rem;
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 1.1rem;
        }}
        
        .info-content {{
          color: #166534;
          line-height: 1.7;
        }}
        
        code {{
          font-family: 'SF Mono', Monaco, monospace;
          background: rgba(0,0,0,0.1);
          padding: 0.2rem 0.5rem;
          border-radius: 0.375rem;
          font-size: 0.85em;
          color: #15803d;
          font-weight: 600;
        }}
        
        .actions {{
          display: flex;
          gap: 1rem;
          justify-content: center;
          flex-wrap: wrap;
          margin-top: 2rem;
        }}
        
        .btn {{
          display: inline-flex;
          align-items: center;
          gap: 0.75rem;
          padding: 1rem 2rem;
          border-radius: 1rem;
          text-decoration: none;
          font-weight: 600;
          transition: all 0.3s ease;
          border: 2px solid;
        }}
        
        .btn:hover {{
          transform: translateY(-2px);
          box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        .btn-primary {{
          background: linear-gradient(135deg, #667eea, #764ba2);
          border-color: #667eea;
          color: white;
        }}
        
        .btn-secondary {{
          background: white;
          border-color: #d1d5db;
          color: #374151;
        }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="vip-icon">👑</div>

        <div class="card">
          <h1>Welcome to VIP Lounge</h1>
          <p class="subtitle">Exclusive Experience for Valued Customers</p>
          <div class="info-box">
              <div class="info-content">
              We reached this point by modifying the session cookie.  
              This demonstrates a successful exploitation of the vulnerability caused by using  
              <code>pickle.loads()</code> on data received from the client, and highlights an insecure serialization vulnerability.
          </div>
          </div>
          <div class="welcome-badge">
            <span class="badge">
              <span>⭐</span>
              <span>Hello {s.get('user')} - VIP Member</span>
            </span>
          </div>
          
          <div class="perks">
            <div class="perk">
              <div class="perk-icon">🎁</div>
              <div class="perk-title">Exclusive Discounts</div>
              <div class="perk-desc">Up to 40% off all flights</div>
            </div>
            
            <div class="perk">
              <div class="perk-icon">🚀</div>
              <div class="perk-title">Priority Booking</div>
              <div class="perk-desc">Priority in queue and seat selection</div>
            </div>
            
            <div class="perk">
              <div class="perk-icon">💎</div>
              <div class="perk-title">Triple Points</div>
              <div class="perk-desc">3X points accumulation</div>
            </div>
            
            <div class="perk">
              <div class="perk-icon">🏨</div>
              <div class="perk-title">Free Upgrades</div>
              <div class="perk-desc">Automatic upgrade to business class</div>
            </div>
            
            <div class="perk">
              <div class="perk-icon">🍾</div>
              <div class="perk-title">Luxury Lounge</div>
              <div class="perk-desc">Free access to all lounges</div>
            </div>
            
            <div class="perk">
              <div class="perk-icon">📞</div>
              <div class="perk-title">24/7 Support</div>
              <div class="perk-desc">Dedicated customer service</div>
            </div>
          </div>
          
          
          
          <div class="actions">
            <a href="/" class="btn btn-primary">
              <span>🏠</span>
              <span>Back to Home</span>
            </a>
            <a href="/logout" class="btn btn-secondary">
              <span>🚪</span>
              <span>Logout</span>
            </a>
          </div>
        </div>
      </div>
    </body>
    </html>
    """


@app.get("/logout")
def logout():
    resp = make_response(redirect(url_for("home")))
    resp.delete_cookie(COOKIE_NAME)
    return resp


if __name__ == "__main__":
    print("a demonstration of insecure deserialization. Running on: http://127.0.0.1:5000")
    print("the vulnerability is: pickle.loads() on client data")
    print("=" * 50)
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=True)
