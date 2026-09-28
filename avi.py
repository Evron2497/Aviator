import os
import time
import random
import sqlite3
import hashlib
import secrets
import threading
from datetime import datetime

from flask import (
    Flask,
    request,
    jsonify,
    session,
    redirect,
    render_template_string,
)

# ============================================================
# CONFIGURATION
# ============================================================

DB_NAME = "aviator_live.db"

BETTING_WINDOW = 7.0
MAX_WITHDRAWAL = 250000.0
CRASH_DISPLAY_TIME = 2.5
STARTING_BALANCE = 0.0

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(32))

GAME_LOCK = threading.RLock()


# ============================================================
# DATABASE SETUP
# ============================================================

def get_db():
    conn = sqlite3.connect(DB_NAME, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password, hashed):
    return secrets.compare_digest(hash_password(password), hashed)


def init_db():
    conn = get_db()
    conn.execute("PRAGMA journal_mode=WAL")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone_number TEXT UNIQUE NOT NULL,
            balance REAL DEFAULT 0.0,
            role TEXT DEFAULT 'USER',
            created_at TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS rounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crash_point REAL NOT NULL,
            started_at TEXT NOT NULL,
            ended_at TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS bets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            round_id INTEGER NOT NULL,
            bet_number INTEGER NOT NULL,
            amount REAL NOT NULL,
            auto_cashout REAL,
            cashout_multiplier REAL,
            winnings REAL DEFAULT 0,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    admin = conn.execute("SELECT id FROM users WHERE username = ?", ("admin",)).fetchone()
    if not admin:
        conn.execute("""
            INSERT INTO users (username, password, phone_number, balance, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "admin",
            hash_password("admin123"),
            "254700000000",
            10000.0,
            "ADMIN",
            datetime.now().isoformat()
        ))
    else:
        conn.execute("UPDATE users SET role = 'ADMIN' WHERE username = ?", ("admin",))

    conn.commit()
    conn.close()


# ============================================================
# GAME ENGINE & BOT GENERATOR
# ============================================================

def generate_crash_point():
    value = random.random()
    if value < 0.05:
        return 1.00
    elif value < 0.25:
        return round(random.uniform(1.01, 1.50), 2)
    elif value < 0.65:
        return round(random.uniform(1.51, 3.50), 2)
    elif value < 0.90:
        return round(random.uniform(3.51, 15.00), 2)
    return round(random.uniform(15.01, 150.00), 2)


def calculate_multiplier(elapsed):
    multiplier = 1.0 + (elapsed * 0.22)
    if multiplier > 2.5:
        multiplier += ((elapsed - 6.0) ** 1.25) * 0.05
    return round(max(multiplier, 1.0), 2)


GAME = {
    "round_id": None,
    "crash_point": None,
    "next_crash_point_1": generate_crash_point(),
    "next_crash_point_2": generate_crash_point(),
    "status": "BETTING",
    "betting_start": None,
    "run_start": None,
    "current_multiplier": 1.00,
    "crash_time": None,
    "bot_bets": []
}

FAKE_USERS = [
    "***1", "***2", "***3", "***4", "***5", "***6", "***7", "***8", "***9",
    "alex***", "brian***", "coll***", "david***", "eric***", "frank***", "grace***",
    "harr***", "ian***", "john***", "kevin***", "lucy***", "mike***", "nick***",
    "oliver***", "peter***", "queen***", "ray***", "sam***", "tom***", "victor***",
    "wendy***", "kelv***", "sylv***", "mash***", "kip***", "wanj***", "njeri***",
    "ochi***", "otien***", "maina***", "chep***", "kiprot***", "kibet***", "baras***"
]

def generate_bot_bets():
    bets = []
    count = random.randint(35, 65)
    selected_users = random.sample(FAKE_USERS * 2, count)
    
    for i, user in enumerate(selected_users):
        masked = user[:3] + "***" + str(random.randint(0,9))
        amount = round(random.choice([20, 50, 100, 200, 500, 1000, 2500, 5000, 10000]), 2)
        target_cashout = round(random.uniform(1.10, 6.00), 2) if random.random() > 0.20 else None
        
        bets.append({
            "id": f"bot_{i}",
            "username": masked,
            "amount": amount,
            "auto_cashout": target_cashout,
            "status": "ACTIVE",
            "cashout_multiplier": None,
            "winnings": 0.0
        })
    return bets


def create_round_locked():
    crash_point = GAME["next_crash_point_1"]
    GAME["next_crash_point_1"] = GAME["next_crash_point_2"]
    GAME["next_crash_point_2"] = generate_crash_point()

    now = datetime.now().isoformat()
    conn = get_db()
    cursor = conn.execute("INSERT INTO rounds (crash_point, started_at) VALUES (?, ?)", (crash_point, now))
    round_id = cursor.lastrowid
    conn.commit()
    conn.close()

    GAME["round_id"] = round_id
    GAME["crash_point"] = crash_point
    GAME["status"] = "BETTING"
    GAME["betting_start"] = time.time()
    GAME["run_start"] = None
    GAME["current_multiplier"] = 1.00
    GAME["crash_time"] = None
    GAME["bot_bets"] = generate_bot_bets()


def initialize_game():
    with GAME_LOCK:
        if GAME["round_id"] is None:
            create_round_locked()


def start_running_locked():
    if GAME["status"] != "BETTING":
        return
    GAME["status"] = "RUNNING"
    GAME["run_start"] = time.time()
    GAME["current_multiplier"] = 1.00


def process_auto_cashouts_locked():
    if GAME["status"] != "RUNNING":
        return

    multiplier = GAME["current_multiplier"]
    crash_point = GAME["crash_point"]
    round_id = GAME["round_id"]

    if multiplier >= crash_point:
        return

    for bot in GAME["bot_bets"]:
        if bot["status"] == "ACTIVE" and bot["auto_cashout"] and bot["auto_cashout"] <= multiplier and bot["auto_cashout"] < crash_point:
            bot["status"] = "WON"
            bot["cashout_multiplier"] = bot["auto_cashout"]
            bot["winnings"] = round(bot["amount"] * bot["auto_cashout"], 2)

    for bot in GAME["bot_bets"]:
        if bot["status"] == "ACTIVE" and not bot["auto_cashout"] and multiplier > 1.30:
            if random.random() < 0.05:
                bot["status"] = "WON"
                bot["cashout_multiplier"] = multiplier
                bot["winnings"] = round(bot["amount"] * multiplier, 2)

    conn = get_db()
    bets = conn.execute("""
        SELECT * FROM bets
        WHERE round_id = ? AND status = 'ACTIVE' AND auto_cashout IS NOT NULL
    """, (round_id,)).fetchall()

    for bet in bets:
        target = float(bet["auto_cashout"])
        if target <= multiplier and target < crash_point:
            winnings = round(float(bet["amount"]) * target, 2)
            cursor = conn.execute("""
                UPDATE bets
                SET status = 'WON', cashout_multiplier = ?, winnings = ?
                WHERE id = ? AND status = 'ACTIVE'
            """, (target, winnings, bet["id"]))

            if cursor.rowcount == 1:
                conn.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (winnings, bet["username"]))

    conn.commit()
    conn.close()


def crash_round_locked():
    if GAME["status"] == "CRASHED":
        return

    GAME["status"] = "CRASHED"
    GAME["current_multiplier"] = GAME["crash_point"]
    GAME["crash_time"] = time.time()

    for bot in GAME["bot_bets"]:
        if bot["status"] == "ACTIVE":
            bot["status"] = "LOST"

    conn = get_db()
    conn.execute("UPDATE bets SET status = 'LOST' WHERE round_id = ? AND status = 'ACTIVE'", (GAME["round_id"],))
    conn.execute("UPDATE rounds SET ended_at = ? WHERE id = ?", (datetime.now().isoformat(), GAME["round_id"]))
    conn.commit()
    conn.close()


def tick_game_locked():
    initialize_game()
    now = time.time()

    if GAME["status"] == "BETTING":
        elapsed = now - GAME["betting_start"]
        GAME["current_multiplier"] = 1.50
        if elapsed >= BETTING_WINDOW:
            start_running_locked()

    elif GAME["status"] == "RUNNING":
        elapsed = now - GAME["run_start"]
        multiplier = calculate_multiplier(elapsed)
        GAME["current_multiplier"] = multiplier
        process_auto_cashouts_locked()

        if multiplier >= GAME["crash_point"]:
            crash_round_locked()

    elif GAME["status"] == "CRASHED":
        if GAME["crash_time"] is not None and (now - GAME["crash_time"]) >= CRASH_DISPLAY_TIME:
            create_round_locked()


def game_loop():
    while True:
        try:
            with GAME_LOCK:
                tick_game_locked()
        except Exception as e:
            print("Engine Loop Error:", e)
        time.sleep(0.04)


threading.Thread(target=game_loop, daemon=True).start()
init_db()


# ============================================================
# USER & BET ACTIONS
# ============================================================

def get_user(username):
    conn = get_db()
    row = conn.execute("SELECT username, phone_number, balance, role FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return row


def deduct_balance(username, amount):
    conn = get_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        cursor = conn.execute("UPDATE users SET balance = balance - ? WHERE username = ? AND balance >= ?", (amount, username, amount))
        if cursor.rowcount != 1:
            conn.rollback()
            return False
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()


def place_bet_for_user(username, bet_number, amount, auto_cashout):
    with GAME_LOCK:
        tick_game_locked()
        if bet_number not in [1, 2]:
            return False, "Invalid bet slot."
        if GAME["status"] != "BETTING":
            return False, "Betting closed for this round."

        try:
            amount = float(amount)
        except ValueError:
            return False, "Invalid amount."

        if amount <= 0:
            return False, "Amount must be greater than zero."

        if auto_cashout in (None, "", False):
            auto_cashout = None
        else:
            try:
                auto_cashout = float(auto_cashout)
                if auto_cashout < 1.01:
                    return False, "Auto cashout minimum is 1.01x."
            except ValueError:
                return False, "Invalid auto cashout value."

        conn = get_db()
        try:
            conn.execute("BEGIN IMMEDIATE")
            existing = conn.execute("SELECT id FROM bets WHERE username = ? AND round_id = ? AND bet_number = ?", (username, GAME["round_id"], bet_number)).fetchone()
            if existing:
                conn.rollback()
                return False, f"Bet {bet_number} already placed."

            user = conn.execute("SELECT balance FROM users WHERE username = ?", (username,)).fetchone()
            if not user or float(user["balance"]) < amount:
                conn.rollback()
                return False, "Insufficient balance."

            conn.execute("UPDATE users SET balance = balance - ? WHERE username = ?", (amount, username))
            conn.execute("""
                INSERT INTO bets (username, round_id, bet_number, amount, auto_cashout, winnings, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (username, GAME["round_id"], bet_number, amount, auto_cashout, 0.0, "ACTIVE", datetime.now().isoformat()))
            conn.commit()
            return True, f"Bet {bet_number} placed."
        except Exception:
            conn.rollback()
            return False, "Failed to place bet."
        finally:
            conn.close()


def manual_cashout(username, bet_number):
    with GAME_LOCK:
        tick_game_locked()
        if GAME["status"] != "RUNNING":
            return False, "Flight not running."
        multiplier = GAME["current_multiplier"]
        if multiplier >= GAME["crash_point"]:
            return False, "Round crashed."

        multiplier = round(multiplier, 2)
        conn = get_db()
        try:
            conn.execute("BEGIN IMMEDIATE")
            bet = conn.execute("SELECT * FROM bets WHERE username = ? AND round_id = ? AND bet_number = ? AND status = 'ACTIVE'", (username, GAME["round_id"], bet_number)).fetchone()
            if not bet:
                conn.rollback()
                return False, "No active bet found."

            winnings = round(float(bet["amount"]) * multiplier, 2)
            cursor = conn.execute("UPDATE bets SET status = 'WON', cashout_multiplier = ?, winnings = ? WHERE id = ? AND status = 'ACTIVE'", (multiplier, winnings, bet["id"]))
            if cursor.rowcount != 1:
                conn.rollback()
                return False, "Cashout failed."

            conn.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (winnings, username))
            conn.commit()
            return True, f"Cashed out at {multiplier:.2f}x — KES {winnings:,.2f}"
        except Exception:
            conn.rollback()
            return False, "Cashout error."
        finally:
            conn.close()


# ============================================================
# FLASK ROUTES
# ============================================================

@app.route("/")
def index():
    if "username" not in session:
        return redirect("/login")
    return render_template_string(HTML, username=session["username"])


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and verify_password(password, user["password"]):
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect("/")
        error = "Invalid credentials."

    return render_template_string(LOGIN_HTML, error=error)


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        phone = request.form.get("phone_number", "").strip()

        if not username or not password or not phone:
            error = "All fields are required."
        else:
            conn = get_db()
            try:
                conn.execute("""
                    INSERT INTO users (username, password, phone_number, balance, role, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (username, hash_password(password), phone, STARTING_BALANCE, "USER", datetime.now().isoformat()))
                conn.commit()
                session["username"] = username
                session["role"] = "USER"
                return redirect("/")
            except sqlite3.IntegrityError:
                error = "Username or Phone number already registered."
            finally:
                conn.close()

    return render_template_string(REGISTER_HTML, error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/api/state")
def api_state():
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    with GAME_LOCK:
        tick_game_locked()
        username = session["username"]
        user = get_user(username)
        isAdmin = (user["role"] == "ADMIN")

        conn = get_db()
        history_rows = conn.execute("SELECT crash_point FROM rounds WHERE ended_at IS NOT NULL ORDER BY id DESC LIMIT 20").fetchall()
        history = [float(r["crash_point"]) for r in history_rows][::-1]

        bet_rows = conn.execute("SELECT bet_number, amount, auto_cashout, cashout_multiplier, winnings, status FROM bets WHERE username = ? AND round_id = ?", (username, GAME["round_id"])).fetchall()
        conn.close()

        user_bets = {}
        all_live_bets = []

        for b in GAME["bot_bets"]:
            all_live_bets.append(b)

        for r in bet_rows:
            user_bets[str(r["bet_number"])] = dict(r)
            all_live_bets.append({
                "id": f"real_{r['bet_number']}",
                "username": username,
                "amount": r["amount"],
                "auto_cashout": r["auto_cashout"],
                "status": r["status"],
                "cashout_multiplier": r["cashout_multiplier"],
                "winnings": r["winnings"]
            })

        all_live_bets.sort(key=lambda x: 0 if x["status"] == "ACTIVE" else 1)

        return jsonify({
            "status": GAME["status"],
            "multiplier": GAME["current_multiplier"],
            "crash_point": GAME["crash_point"] if GAME["status"] == "CRASHED" else None,
            "next_crash_point_1": GAME["next_crash_point_1"] if isAdmin else None,
            "next_crash_point_2": GAME["next_crash_point_2"] if isAdmin else None,
            "is_admin": isAdmin,
            "balance": float(user["balance"]),
            "bets": user_bets,
            "live_feed": all_live_bets,
            "history": history,
            "round_id": GAME["round_id"]
        })


@app.route("/api/bet", methods=["POST"])
def api_bet():
    if "username" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    data = request.get_json() or {}
    success, msg = place_bet_for_user(session["username"], int(data.get("bet_number", 1)), data.get("amount", 0), data.get("auto_cashout"))
    return jsonify({"success": success, "message": msg})


@app.route("/api/cashout", methods=["POST"])
def api_cashout():
    if "username" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    data = request.get_json() or {}
    success, msg = manual_cashout(session["username"], int(data.get("bet_number", 1)))
    return jsonify({"success": success, "message": msg})


@app.route("/api/withdraw", methods=["POST"])
def api_withdraw():
    if "username" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    data = request.get_json() or {}
    try:
        amount = float(data.get("amount", 0))
    except ValueError:
        return jsonify({"success": False, "message": "Invalid amount."})
    
    username = session["username"]
    user = get_user(username)
    if user["balance"] < amount:
        return jsonify({"success": False, "message": "Insufficient balance."})
    if deduct_balance(username, amount):
        return jsonify({"success": True, "message": f"Withdrawal of KES {amount:,.2f} initiated for {user['phone_number']}."})
    return jsonify({"success": False, "message": "Withdrawal request failed."})


# ============================================================
# HTML & CLIENT INTERFACE
# ============================================================

LOGIN_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Aviator - Login</title>
<style>
body { margin:0; min-height:100vh; display:flex; justify-content:center; align-items:center; background:#0e1015; font-family:sans-serif; color:#fff; }
.box { width:100%; max-width:360px; padding:30px; border-radius:12px; background:#181c24; border:1px solid #282f3d; }
h2 { text-align:center; color:#28a745; margin-top:0; }
input { width:100%; padding:12px; margin:8px 0 16px; border-radius:6px; border:1px solid #282f3d; background:#0e1015; color:#fff; box-sizing:border-box; }
button { width:100%; padding:12px; border:none; border-radius:6px; background:#28a745; color:#fff; font-weight:bold; cursor:pointer; font-size:16px; }
.error { color:#e53e3e; text-align:center; margin-bottom:12px; font-size:14px; }
a { color:#28a745; text-decoration:none; }
</style>
</head>
<body>
<div class="box">
    <h2>✈️ AVIATOR LOGIN</h2>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST">
        <label>Username</label>
        <input type="text" name="username" required>
        <label>Password</label>
        <input type="password" name="password" required>
        <button type="submit">LOG IN</button>
    </form>
    <p style="text-align:center; font-size:14px; color:#888;">No account? <a href="/register">Register</a></p>
</div>
</body>
</html>
"""

REGISTER_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Aviator - Register</title>
<style>
body { margin:0; min-height:100vh; display:flex; justify-content:center; align-items:center; background:#0e1015; font-family:sans-serif; color:#fff; }
.box { width:100%; max-width:360px; padding:30px; border-radius:12px; background:#181c24; border:1px solid #282f3d; }
h2 { text-align:center; color:#28a745; margin-top:0; }
input { width:100%; padding:12px; margin:8px 0 16px; border-radius:6px; border:1px solid #282f3d; background:#0e1015; color:#fff; box-sizing:border-box; }
button { width:100%; padding:12px; border:none; border-radius:6px; background:#28a745; color:#fff; font-weight:bold; cursor:pointer; font-size:16px; }
.error { color:#e53e3e; text-align:center; margin-bottom:12px; font-size:14px; }
a { color:#28a745; text-decoration:none; }
</style>
</head>
<body>
<div class="box">
    <h2>✈️CREATE ACCOUNT</h2>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST">
        <label>Username</label>
        <input type="text" name="username" required>
        <label>Phone Number (Payouts)</label>
        <input type="text" name="phone_number" placeholder="254712345678" required>
        <label>Password</label>
        <input type="password" name="password" required>
        <button type="submit">SIGN UP</button>
    </form>
    <p style="text-align:center; font-size:14px; color:#888;">Already have an account? <a href="/login">Login</a></p>
</div>
</body>
</html>
"""

HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Aviator Game Interface</title>
<style>
* { box-sizing: border-box; }
body { margin: 0; padding: 0; background-color: #000; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: #fff; user-select: none; }

.header { display: flex; justify-content: space-between; align-items: center; background: #1b1c20; padding: 10px 16px; border-bottom: 1px solid #2a2b30; }
.brand { font-size: 20px; font-weight: 900; color: #28a745; letter-spacing: 1px; }
.wallet { display: flex; align-items: center; gap: 10px; }
.balance { color: #28a745; font-weight: bold; font-size: 16px; }

.deposit-btn { background: #28a745; color: #fff; font-weight: bold; border: none; padding: 8px 16px; border-radius: 20px; cursor: pointer; text-decoration: none; font-size: 13px; }
.withdraw-btn { background: #007bff; color: #fff; font-weight: bold; border: none; padding: 8px 16px; border-radius: 20px; cursor: pointer; font-size: 13px; }

.admin-banner { display: none; background: #d97706; color: #fff; text-align: center; font-weight: bold; padding: 6px; font-size: 14px; border-bottom: 2px solid #b45309; }

.main-layout { max-width: 1200px; margin: 0 auto; padding: 10px; }

/* History Header Line */
.history-line { display: flex; gap: 8px; overflow-x: auto; padding: 6px 0; margin-bottom: 8px; scrollbar-width: none; }
.history-line::-webkit-scrollbar { display: none; }
.hist-item { font-size: 13px; font-weight: 700; padding: 2px 8px; border-radius: 10px; white-space: nowrap; }
.hist-blue { color: #3498db; }
.hist-purple { color: #9b59b6; }
.hist-pink { color: #e91e63; }

/* Display Canvas Stage */
.stage { position: relative; width: 100%; height: 320px; background: radial-gradient(circle at 10% 90%, #20081e 0%, #0d060e 100%); border-radius: 12px 12px 0 0; overflow: hidden; border: 1px solid #2a2c33; }
canvas { width: 100%; height: 100%; display: block; }
.multiplier-overlay { position: absolute; top: 40%; left: 50%; transform: translate(-50%, -50%); font-size: 64px; font-weight: 900; text-align: center; color: #fff; z-index: 10; text-shadow: 0 0 15px rgba(0,0,0,0.8); }
.crashed-text { color: #e53e3e; text-shadow: 0 0 10px rgba(229, 62, 62, 0.6); }

/* Control Panels Grid */
.panels-container { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; background: #141518; padding: 10px; border-radius: 0 0 12px 12px; border: 1px solid #2a2c33; border-top: none; }
.bet-box { background: #1b1c21; border-radius: 10px; padding: 10px; border: 1px solid #25272e; }

.toggle-bar { display: flex; justify-content: center; background: #0e0f12; border-radius: 15px; padding: 2px; margin-bottom: 8px; width: 160px; margin-left: auto; margin-right: auto; }
.toggle-btn { flex: 1; text-align: center; padding: 4px 0; font-size: 12px; border-radius: 13px; cursor: pointer; color: #888; font-weight: bold; }
.toggle-btn.active { background: #252830; color: #fff; }

.auto-options { display: none; margin-bottom: 8px; gap: 8px; align-items: center; justify-content: center; }
.auto-options.show { display: flex; }
.auto-input { width: 80px; background: #0e1013; border: 1px solid #2a2c33; color: #fff; border-radius: 6px; padding: 4px; text-align: center; font-weight: bold; }

.controls-flex { display: flex; gap: 10px; align-items: center; }
.left-inputs { flex: 1; }

.input-stepper { display: flex; align-items: center; background: #0e1013; border-radius: 20px; padding: 2px; border: 1px solid #2a2c33; }
.step-btn { width: 32px; height: 32px; border-radius: 50%; border: none; background: #1b1c21; color: #888; font-size: 18px; cursor: pointer; display: flex; align-items: center; justify-content: center; }
.step-btn:hover { color: #fff; }
.amount-input { flex: 1; background: transparent; border: none; color: #fff; font-size: 16px; font-weight: bold; text-align: center; width: 100%; outline: none; }

.quick-bets { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; margin-top: 6px; }
.q-btn { background: #121316; border: 1px solid #22242b; color: #aaa; border-radius: 10px; padding: 4px; font-size: 11px; cursor: pointer; text-align: center; }
.q-btn:hover { color: #fff; border-color: #444; }

.action-btn { flex: 1.1; height: 82px; border: none; border-radius: 12px; font-weight: 900; cursor: pointer; display: flex; flex-direction: column; justify-content: center; align-items: center; transition: all 0.2s; }
.btn-green { background: #28a745; color: #fff; }
.btn-green:hover { background: #218838; }
.btn-orange { background: #d97706; color: #fff; }
.btn-orange:hover { background: #b45309; }
.btn-blue { background: #007bff; color: #fff; }
.btn-disabled { background: #333 !important; color: #666 !important; cursor: not-allowed; }

.btn-title { font-size: 18px; }
.btn-sub { font-size: 16px; margin-top: 2px; }

/* Feed Section Below */
.feed-section { margin-top: 15px; background: #141518; border-radius: 12px; padding: 12px; border: 1px solid #2a2c33; }
.feed-header { font-size: 12px; color: #888; border-bottom: 1px solid #22242b; padding-bottom: 8px; margin-bottom: 8px; }
.feed-row { display: flex; justify-content: space-between; font-size: 13px; padding: 6px 0; border-bottom: 1px solid #1a1c22; }

@media (max-width: 768px) {
    .panels-container { grid-template-columns: 1fr; }
    .stage { height: 250px; }
}
</style>
</head>
<body>

<div class="admin-banner" id="adminBanner">
    ⚡ ADMIN CONTROLS: NEXT ROUND: <span id="next1">-</span> | ROUND AFTER: <span id="next2">-</span>
</div>

<div class="header">
    <div class="brand">AVIATOR</div>
    <div class="wallet">
        <span class="balance" id="balanceDisplay">0.00 Ksh</span>
        <button class="deposit-btn" onclick="openDepositGateway()">DEPOSIT</button>
        <button class="withdraw-btn" onclick="triggerWithdrawal()">WITHDRAW</button>
        <a href="/logout" style="color:#e53e3e; text-decoration:none; font-size:12px; margin-left:8px;">Logout</a>
    </div>
</div>

<div class="main-layout">
    <!-- History Line -->
    <div class="history-line" id="historyLine"></div>

    <!-- Canvas Animation Stage -->
    <div class="stage">
        <canvas id="flightCanvas"></canvas>
        <div class="multiplier-overlay" id="multiplierDisplay">1.00x</div>
    </div>

    <!-- Controls Area -->
    <div class="panels-container">
        <!-- Panel 1 -->
        <div class="bet-box">
            <div class="toggle-bar">
                <div class="toggle-btn active" id="tabBet1" onclick="switchTab(1, 'bet')">Bet</div>
                <div class="toggle-btn" id="tabAuto1" onclick="switchTab(1, 'auto')">Auto</div>
            </div>
            
            <div class="auto-options" id="autoOpt1">
                <label style="font-size:11px; color:#aaa;">Auto Cashout x</label>
                <input type="number" id="autoCashout1" class="auto-input" value="2.00" step="0.1" min="1.01">
            </div>

            <div class="controls-flex">
                <div class="left-inputs">
                    <div class="input-stepper">
                        <button class="step-btn" onclick="adjustBet(1, -10)">-</button>
                        <input type="number" id="amount1" class="amount-input" value="20.00">
                        <button class="step-btn" onclick="adjustBet(1, 10)">+</button>
                    </div>
                    <div class="quick-bets">
                        <div class="q-btn" onclick="setBet(1, 100)">100</div>
                        <div class="q-btn" onclick="setBet(1, 200)">200</div>
                        <div class="q-btn" onclick="setBet(1, 500)">500</div>
                        <div class="q-btn" onclick="setBet(1, 10000)">10,000</div>
                    </div>
                </div>
                <button class="action-btn btn-green" id="btn1" onclick="handleAction(1)">
                    <span class="btn-title" id="btn1Title">Bet</span>
                    <span class="btn-sub" id="btn1Sub">20.00 KES</span>
                </button>
            </div>
        </div>

        <!-- Panel 2 -->
        <div class="bet-box">
            <div class="toggle-bar">
                <div class="toggle-btn active" id="tabBet2" onclick="switchTab(2, 'bet')">Bet</div>
                <div class="toggle-btn" id="tabAuto2" onclick="switchTab(2, 'auto')">Auto</div>
            </div>

            <div class="auto-options" id="autoOpt2">
                <label style="font-size:11px; color:#aaa;">Auto Cashout x</label>
                <input type="number" id="autoCashout2" class="auto-input" value="2.00" step="0.1" min="1.01">
            </div>

            <div class="controls-flex">
                <div class="left-inputs">
                    <div class="input-stepper">
                        <button class="step-btn" onclick="adjustBet(2, -10)">-</button>
                        <input type="number" id="amount2" class="amount-input" value="20.00">
                        <button class="step-btn" onclick="adjustBet(2, 10)">+</button>
                    </div>
                    <div class="quick-bets">
                        <div class="q-btn" onclick="setBet(2, 100)">100</div>
                        <div class="q-btn" onclick="setBet(2, 200)">200</div>
                        <div class="q-btn" onclick="setBet(2, 500)">500</div>
                        <div class="q-btn" onclick="setBet(2, 10000)">10,000</div>
                    </div>
                </div>
                <button class="action-btn btn-green" id="btn2" onclick="handleAction(2)">
                    <span class="btn-title" id="btn2Title">Bet</span>
                    <span class="btn-sub" id="btn2Sub">20.00 KES</span>
                </button>
            </div>
        </div>
    </div>

    <!-- All Bets Feed -->
    <div class="feed-section">
        <div class="feed-header">ALL BETS (<span id="totalBetsCount">0</span>)</div>
        <div id="liveBetsList"></div>
    </div>
</div>

<script>
let currentStatus = "BETTING";
let currentMult = 1.00;
let userBets = {};
let currentRoundId = null;
let lastAutoPlacedRound = { 1: null, 2: null };

let autoBetEnabled = { 1: false, 2: false };
let activeTab = { 1: 'bet', 2: 'bet' };

const canvas = document.getElementById('flightCanvas');
const ctx = canvas.getContext('2d');

function resizeCanvas() {
    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = canvas.parentElement.clientHeight;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

function drawScene() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    ctx.strokeStyle = "rgba(255, 255, 255, 0.03)";
    ctx.lineWidth = 1;
    for (let x = 0; x < canvas.width; x += 40) {
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
    }
    for (let y = 0; y < canvas.height; y += 40) {
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
    }

    if (currentStatus === 'RUNNING' || currentStatus === 'CRASHED') {
        const progress = Math.min((currentMult - 1) / 5.0, 1.0);
        const startX = 0;
        const startY = canvas.height;
        const endX = canvas.width * 0.75 * Math.min(progress + 0.1, 1.0);
        const endY = canvas.height - (canvas.height * 0.65 * Math.min(progress + 0.1, 1.0));

        ctx.beginPath();
        ctx.moveTo(startX, startY);
        ctx.quadraticCurveTo(endX * 0.5, canvas.height, endX, endY);
        ctx.lineTo(endX, canvas.height);
        ctx.closePath();
        
        const grad = ctx.createLinearGradient(0, 0, 0, canvas.height);
        grad.addColorStop(0, "rgba(229, 62, 62, 0.5)");
        grad.addColorStop(1, "rgba(229, 62, 62, 0.0)");
        ctx.fillStyle = grad;
        ctx.fill();

        ctx.beginPath();
        ctx.moveTo(startX, startY);
        ctx.quadraticCurveTo(endX * 0.5, canvas.height, endX, endY);
        ctx.strokeStyle = "#e53e3e";
        ctx.lineWidth = 4;
        ctx.stroke();

        if (currentStatus === 'RUNNING') {
            ctx.save();
            ctx.translate(endX, endY);
            ctx.fillStyle = "#e53e3e";
            ctx.beginPath();
            ctx.arc(0, 0, 8, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }
    }
    requestAnimationFrame(drawScene);
}
requestAnimationFrame(drawScene);

function switchTab(num, tab) {
    activeTab[num] = tab;
    document.getElementById('tabBet' + num).className = 'toggle-btn' + (tab === 'bet' ? ' active' : '');
    document.getElementById('tabAuto' + num).className = 'toggle-btn' + (tab === 'auto' ? ' active' : '');
    
    const autoOpt = document.getElementById('autoOpt' + num);
    if (tab === 'auto') autoOpt.classList.add('show');
    else autoOpt.classList.remove('show');
    
    updateButtonUI(num);
}

async function syncState() {
    try {
        const res = await fetch('/api/state');
        if (!res.ok) return;
        const data = await res.json();

        document.getElementById('balanceDisplay').innerText = data.balance.toFixed(2) + ' KES';
        currentStatus = data.status;
        currentMult = data.multiplier;
        userBets = data.bets;
        currentRoundId = data.round_id;

        // Admin Telemetry Panel display
        if (data.is_admin) {
            document.getElementById('adminBanner').style.display = 'block';
            document.getElementById('next1').innerText = data.next_crash_point_1 ? data.next_crash_point_1.toFixed(2) + 'x' : '-';
            document.getElementById('next2').innerText = data.next_crash_point_2 ? data.next_crash_point_2.toFixed(2) + 'x' : '-';
        } else {
            document.getElementById('adminBanner').style.display = 'none';
        }

        const multDisplay = document.getElementById('multiplierDisplay');
        if (data.status === 'BETTING') {
            multDisplay.className = 'multiplier-overlay';
            multDisplay.innerText = 'WAITING FOR NEXT ROUND';
            
            // Execute Auto Bets
            checkAndRunAutoBet(1);
            checkAndRunAutoBet(2);

        } else if (data.status === 'RUNNING') {
            multDisplay.className = 'multiplier-overlay';
            multDisplay.innerText = data.multiplier.toFixed(2) + 'x';
        } else if (data.status === 'CRASHED') {
            multDisplay.className = 'multiplier-overlay crashed-text';
            multDisplay.innerText = 'FLEW AWAY!\n' + (data.crash_point ? data.crash_point.toFixed(2) : data.multiplier.toFixed(2)) + 'x';
        }

        // Render History Line
        const histLine = document.getElementById('historyLine');
        histLine.innerHTML = data.history.map(val => {
            let cls = 'hist-blue';
            if (val >= 10.0) cls = 'hist-pink';
            else if (val >= 2.0) cls = 'hist-purple';
            return `<div class="hist-item ${cls}">${val.toFixed(2)}x</div>`;
        }).join('');

        updateButtonUI(1);
        updateButtonUI(2);

        // Render Live Bets
        document.getElementById('totalBetsCount').innerText = data.live_feed.length;
        const feed = document.getElementById('liveBetsList');
        feed.innerHTML = data.live_feed.map(b => {
            let statusText = `<span style="color:#888;">IN PLAY</span>`;
            if (b.status === 'WON') {
                statusText = `<span style="color:#28a745; font-weight:bold;">${b.cashout_multiplier.toFixed(2)}x (+${b.winnings.toFixed(2)})</span>`;
            } else if (b.status === 'LOST') {
                statusText = `<span style="color:#e53e3e;">CRASHED</span>`;
            }
            return `<div class="feed-row">
                <div><b>${b.username}</b></div>
                <div>${b.amount.toFixed(2)} KES</div>
                <div>${statusText}</div>
            </div>`;
        }).join('');

    } catch (e) {
        console.error(e);
    }
}

async function checkAndRunAutoBet(num) {
    if (autoBetEnabled[num] && currentStatus === 'BETTING') {
        if (lastAutoPlacedRound[num] !== currentRoundId) {
            const bet = userBets[num];
            if (!bet || bet.status !== 'ACTIVE') {
                lastAutoPlacedRound[num] = currentRoundId;
                const amount = document.getElementById('amount' + num).value;
                const autoCash = document.getElementById('autoCashout' + num).value;
                await fetch('/api/bet', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ bet_number: num, amount: amount, auto_cashout: autoCash })
                });
            }
        }
    }
}

function updateButtonUI(num) {
    const btn = document.getElementById('btn' + num);
    const title = document.getElementById('btn' + num + 'Title');
    const sub = document.getElementById('btn' + num + 'Sub');
    const inputVal = parseFloat(document.getElementById('amount' + num).value) || 20;
    const bet = userBets[num];

    if (currentStatus === 'RUNNING') {
        if (bet && bet.status === 'ACTIVE') {
            const currentPayout = (bet.amount * currentMult).toFixed(2);
            btn.className = 'action-btn btn-orange';
            title.innerText = 'CASH OUT';
            sub.innerText = currentPayout + ' KES';
            btn.disabled = false;
        } else {
            btn.className = 'action-btn btn-disabled';
            title.innerText = 'Bet';
            sub.innerText = inputVal.toFixed(2) + ' KES';
            btn.disabled = true;
        }
    } else if (currentStatus === 'BETTING') {
        if (activeTab[num] === 'auto') {
            if (autoBetEnabled[num]) {
                btn.className = 'action-btn btn-blue';
                title.innerText = 'AUTO ACTIVE';
                sub.innerText = 'CANCEL';
                btn.disabled = false;
            } else {
                btn.className = 'action-btn btn-green';
                title.innerText = 'AUTO BET';
                sub.innerText = inputVal.toFixed(2) + ' KES';
                btn.disabled = false;
            }
        } else {
            if (bet && bet.status === 'ACTIVE') {
                btn.className = 'action-btn btn-disabled';
                title.innerText = 'WAITING';
                sub.innerText = 'BET PLACED';
                btn.disabled = true;
            } else {
                btn.className = 'action-btn btn-green';
                title.innerText = 'Bet';
                sub.innerText = inputVal.toFixed(2) + ' KES';
                btn.disabled = false;
            }
        }
    } else {
        btn.className = 'action-btn btn-disabled';
        btn.disabled = true;
    }
}

function adjustBet(num, delta) {
    const input = document.getElementById('amount' + num);
    let val = (parseFloat(input.value) || 0) + delta;
    if (val < 10) val = 10;
    input.value = val.toFixed(2);
    updateButtonUI(num);
}

function setBet(num, val) {
    document.getElementById('amount' + num).value = val.toFixed(2);
    updateButtonUI(num);
}

async function handleAction(num) {
    const bet = userBets[num];
    if (currentStatus === 'RUNNING' && bet && bet.status === 'ACTIVE') {
        const res = await fetch('/api/cashout', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ bet_number: num })
        });
        const data = await res.json();
        if (!data.success) alert(data.message);
    } else if (currentStatus === 'BETTING') {
        if (activeTab[num] === 'auto') {
            autoBetEnabled[num] = !autoBetEnabled[num];
            if (autoBetEnabled[num]) {
                checkAndRunAutoBet(num);
            }
        } else {
            const amount = document.getElementById('amount' + num).value;
            const res = await fetch('/api/bet', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ bet_number: num, amount: amount })
            });
            const data = await res.json();
            if (!data.success) alert(data.message);
        }
    }
    syncState();
}

function openDepositGateway() {
    const url = "https://makamescopay.com/pay/86015b66cc589a32";
    const depositWin = window.open(url, "DepositWindow", "width=600,height=700");
    
    const timer = setInterval(() => {
        if (depositWin && depositWin.closed) {
            clearInterval(timer);
            syncState();
        }
    }, 1000);
}

async function triggerWithdrawal() {
    const val = prompt("Enter amount to withdraw (KES):");
    if (!val) return;
    const amount = parseFloat(val);
    if (isNaN(amount) || amount <= 0) {
        alert("Invalid amount.");
        return;
    }
    const res = await fetch('/api/withdraw', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ amount: amount })
    });
    const data = await res.json();
    alert(data.message);
    syncState();
}

setInterval(syncState, 200);
syncState();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)



