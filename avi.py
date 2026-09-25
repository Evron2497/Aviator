# import os
# import time
# import random
# import sqlite3
# import hashlib
# import secrets
# import threading
# from datetime import datetime

# from flask import (
#     Flask,
#     request,
#     jsonify,
#     session,
#     redirect,
#     render_template_string,
# )

# # ============================================================
# # CONFIGURATION
# # ============================================================

# DB_NAME = "aviator_live.db"

# BETTING_WINDOW = 8.0
# MAX_BETS = 2
# MAX_WITHDRAWAL = 250000.0
# CRASH_DISPLAY_TIME = 2.0
# STARTING_BALANCE = 0.0

# app = Flask(__name__)
# app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(32))

# GAME_LOCK = threading.RLock()


# # ============================================================
# # DATABASE SETUP
# # ============================================================

# def get_db():
#     conn = sqlite3.connect(DB_NAME, timeout=10, check_same_thread=False)
#     conn.row_factory = sqlite3.Row
#     return conn


# def hash_password(password):
#     return hashlib.sha256(password.encode("utf-8")).hexdigest()


# def verify_password(password, hashed):
#     return secrets.compare_digest(hash_password(password), hashed)


# def init_db():
#     conn = get_db()
#     conn.execute("PRAGMA journal_mode=WAL")

#     conn.execute("""
#         CREATE TABLE IF NOT EXISTS users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             username TEXT UNIQUE NOT NULL,
#             password TEXT NOT NULL,
#             phone_number TEXT UNIQUE NOT NULL,
#             balance REAL DEFAULT 0.0,
#             role TEXT DEFAULT 'USER',
#             created_at TEXT NOT NULL
#         )
#     """)

#     conn.execute("""
#         CREATE TABLE IF NOT EXISTS rounds (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             crash_point REAL NOT NULL,
#             started_at TEXT NOT NULL,
#             ended_at TEXT
#         )
#     """)

#     conn.execute("""
#         CREATE TABLE IF NOT EXISTS bets (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             username TEXT NOT NULL,
#             round_id INTEGER NOT NULL,
#             bet_number INTEGER NOT NULL,
#             amount REAL NOT NULL,
#             auto_cashout REAL,
#             cashout_multiplier REAL,
#             winnings REAL DEFAULT 0,
#             status TEXT NOT NULL,
#             created_at TEXT NOT NULL
#         )
#     """)

#     # Create default Admin if missing
#     admin = conn.execute("SELECT id FROM users WHERE username = ?", ("admin",)).fetchone()
#     if not admin:
#         conn.execute("""
#             INSERT INTO users (username, password, phone_number, balance, role, created_at)
#             VALUES (?, ?, ?, ?, ?, ?)
#         """, (
#             "admin",
#             hash_password("admin123"),
#             "254700000000",
#             0.0,
#             "ADMIN",
#             datetime.now().isoformat()
#         ))
#     else:
#         conn.execute("UPDATE users SET role = 'ADMIN' WHERE username = ?", ("admin",))

#     conn.commit()
#     conn.close()


# # ============================================================
# # GAME ENGINE & BOT FEED GENERATOR
# # ============================================================

# def generate_crash_point():
#     value = random.random()
#     if value < 0.03:
#         return round(random.uniform(1.00, 1.15), 2)
#     elif value < 0.20:
#         return round(random.uniform(1.16, 2.00), 2)
#     elif value < 0.60:
#         return round(random.uniform(2.01, 5.00), 2)
#     elif value < 0.90:
#         return round(random.uniform(5.01, 20.00), 2)
#     return round(random.uniform(20.00, 100.00), 2)


# def calculate_multiplier(elapsed):
#     multiplier = 1.0 + (elapsed * 0.25)
#     if multiplier > 3:
#         multiplier += (elapsed ** 1.15) * 0.03
#     return round(multiplier, 2)


# GAME = {
#     "round_id": None,
#     "crash_point": None,
#     "next_crash_point": generate_crash_point(),
#     "status": "BETTING",
#     "betting_start": None,
#     "run_start": None,
#     "current_multiplier": 1.00,
#     "crash_time": None,
#     "bot_bets": []
# }

# FAKE_USERS = [
#     "***1", "***2", "***3", "***4", "***5", "***6", "***7", "***8", "***9", "***0",
#     "alex***", "brian***", "coll***", "david***", "eric***", "frank***", "grace***",
#     "harr***", "ian***", "john***", "kevin***", "lucy***", "mike***", "nick***",
#     "oliver***", "peter***", "queen***", "ray***", "sam***", "tom***", "victor***",
#     "wendy***", "xav***", "yves***", "zack***", "kelv***", "sylv***", "mash***",
#     "kip***", "wanj***", "njeri***", "ochi***", "otien***", "maina***", "chep***",
#     "kiprot***", "kibet***", "kipko***", "cherot***", "jelag***", "baras***"
# ]

# def generate_bot_bets():
#     """Generates over 50 realistic random player bets for the new round."""
#     bets = []
#     count = random.randint(55, 75)
#     selected_users = random.sample(FAKE_USERS * 2, count)
    
#     for i, user in enumerate(selected_users):
#         masked = user[:3] + "***" + str(random.randint(0,9))
#         amount = round(random.choice([50, 100, 200, 500, 1000, 2500, 5000, 10000]), 2)
#         target_cashout = round(random.uniform(1.10, 8.50), 2) if random.random() > 0.15 else None
        
#         bets.append({
#             "id": f"bot_{i}",
#             "username": masked,
#             "amount": amount,
#             "auto_cashout": target_cashout,
#             "status": "ACTIVE",
#             "cashout_multiplier": None,
#             "winnings": 0.0
#         })
#     return bets


# def create_round_locked():
#     crash_point = GAME["next_crash_point"]
#     GAME["next_crash_point"] = generate_crash_point()

#     now = datetime.now().isoformat()
#     conn = get_db()
#     cursor = conn.execute("INSERT INTO rounds (crash_point, started_at) VALUES (?, ?)", (crash_point, now))
#     round_id = cursor.lastrowid
#     conn.commit()
#     conn.close()

#     GAME["round_id"] = round_id
#     GAME["crash_point"] = crash_point
#     GAME["status"] = "BETTING"
#     GAME["betting_start"] = time.time()
#     GAME["run_start"] = None
#     GAME["current_multiplier"] = 1.00
#     GAME["crash_time"] = None
#     GAME["bot_bets"] = generate_bot_bets()


# def initialize_game():
#     with GAME_LOCK:
#         if GAME["round_id"] is None:
#             create_round_locked()


# def start_running_locked():
#     if GAME["status"] != "BETTING":
#         return
#     GAME["status"] = "RUNNING"
#     GAME["run_start"] = time.time()
#     GAME["current_multiplier"] = 1.00


# def process_auto_cashouts_locked():
#     if GAME["status"] != "RUNNING":
#         return

#     multiplier = GAME["current_multiplier"]
#     crash_point = GAME["crash_point"]
#     round_id = GAME["round_id"]

#     if multiplier >= crash_point:
#         return

#     for bot in GAME["bot_bets"]:
#         if bot["status"] == "ACTIVE" and bot["auto_cashout"] and bot["auto_cashout"] <= multiplier and bot["auto_cashout"] < crash_point:
#             bot["status"] = "WON"
#             bot["cashout_multiplier"] = bot["auto_cashout"]
#             bot["winnings"] = round(bot["amount"] * bot["auto_cashout"], 2)

#     for bot in GAME["bot_bets"]:
#         if bot["status"] == "ACTIVE" and not bot["auto_cashout"] and multiplier > 1.20:
#             if random.random() < 0.04:
#                 bot["status"] = "WON"
#                 bot["cashout_multiplier"] = multiplier
#                 bot["winnings"] = round(bot["amount"] * multiplier, 2)

#     conn = get_db()
#     bets = conn.execute("""
#         SELECT * FROM bets
#         WHERE round_id = ? AND status = 'ACTIVE' AND auto_cashout IS NOT NULL
#     """, (round_id,)).fetchall()

#     for bet in bets:
#         target = float(bet["auto_cashout"])
#         if target <= multiplier and target < crash_point:
#             winnings = round(float(bet["amount"]) * target, 2)
#             cursor = conn.execute("""
#                 UPDATE bets
#                 SET status = 'WON', cashout_multiplier = ?, winnings = ?
#                 WHERE id = ? AND status = 'ACTIVE'
#             """, (target, winnings, bet["id"]))

#             if cursor.rowcount == 1:
#                 conn.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (winnings, bet["username"]))

#     conn.commit()
#     conn.close()


# def crash_round_locked():
#     if GAME["status"] == "CRASHED":
#         return

#     GAME["status"] = "CRASHED"
#     GAME["current_multiplier"] = GAME["crash_point"]
#     GAME["crash_time"] = time.time()

#     for bot in GAME["bot_bets"]:
#         if bot["status"] == "ACTIVE":
#             bot["status"] = "LOST"

#     conn = get_db()
#     conn.execute("UPDATE bets SET status = 'LOST' WHERE round_id = ? AND status = 'ACTIVE'", (GAME["round_id"],))
#     conn.execute("UPDATE rounds SET ended_at = ? WHERE id = ?", (datetime.now().isoformat(), GAME["round_id"]))
#     conn.commit()
#     conn.close()


# def tick_game_locked():
#     initialize_game()
#     now = time.time()

#     if GAME["status"] == "BETTING":
#         elapsed = now - GAME["betting_start"]
#         GAME["current_multiplier"] = 1.00
#         if elapsed >= BETTING_WINDOW:
#             start_running_locked()

#     elif GAME["status"] == "RUNNING":
#         elapsed = now - GAME["run_start"]
#         multiplier = calculate_multiplier(elapsed)
#         GAME["current_multiplier"] = multiplier
#         process_auto_cashouts_locked()

#         if multiplier >= GAME["crash_point"]:
#             crash_round_locked()

#     elif GAME["status"] == "CRASHED":
#         if GAME["crash_time"] is not None and (now - GAME["crash_time"]) >= CRASH_DISPLAY_TIME:
#             create_round_locked()


# def game_loop():
#     while True:
#         try:
#             with GAME_LOCK:
#                 tick_game_locked()
#         except Exception as e:
#             print("Game engine error:", e)
#         time.sleep(0.05)


# threading.Thread(target=game_loop, daemon=True).start()
# init_db()


# # ============================================================
# # USER & BET ACTIONS
# # ============================================================

# def get_user(username):
#     conn = get_db()
#     row = conn.execute("SELECT username, phone_number, balance, role FROM users WHERE username = ?", (username,)).fetchone()
#     conn.close()
#     return row


# def add_balance(username, amount):
#     conn = get_db()
#     conn.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (amount, username))
#     conn.commit()
#     conn.close()


# def deduct_balance(username, amount):
#     conn = get_db()
#     try:
#         conn.execute("BEGIN IMMEDIATE")
#         cursor = conn.execute("UPDATE users SET balance = balance - ? WHERE username = ? AND balance >= ?", (amount, username, amount))
#         if cursor.rowcount != 1:
#             conn.rollback()
#             return False
#         conn.commit()
#         return True
#     except Exception:
#         conn.rollback()
#         return False
#     finally:
#         conn.close()


# def place_bet_for_user(username, bet_number, amount, auto_cashout):
#     with GAME_LOCK:
#         tick_game_locked()
#         if bet_number not in [1, 2]:
#             return False, "Invalid bet slot."
#         if GAME["status"] != "BETTING":
#             return False, "Betting closed for this round."

#         try:
#             amount = float(amount)
#         except ValueError:
#             return False, "Invalid amount."

#         if amount <= 0:
#             return False, "Amount must be greater than zero."

#         if auto_cashout in (None, "", False):
#             auto_cashout = None
#         else:
#             try:
#                 auto_cashout = float(auto_cashout)
#                 if auto_cashout < 1.01:
#                     return False, "Auto cashout minimum is 1.01x."
#             except ValueError:
#                 return False, "Invalid auto cashout value."

#         conn = get_db()
#         try:
#             conn.execute("BEGIN IMMEDIATE")
#             existing = conn.execute("SELECT id FROM bets WHERE username = ? AND round_id = ? AND bet_number = ?", (username, GAME["round_id"], bet_number)).fetchone()
#             if existing:
#                 conn.rollback()
#                 return False, f"Bet {bet_number} already placed."

#             user = conn.execute("SELECT balance FROM users WHERE username = ?", (username,)).fetchone()
#             if not user or float(user["balance"]) < amount:
#                 conn.rollback()
#                 return False, "Insufficient balance."

#             conn.execute("UPDATE users SET balance = balance - ? WHERE username = ?", (amount, username))
#             conn.execute("""
#                 INSERT INTO bets (username, round_id, bet_number, amount, auto_cashout, winnings, status, created_at)
#                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#             """, (username, GAME["round_id"], bet_number, amount, auto_cashout, 0.0, "ACTIVE", datetime.now().isoformat()))
#             conn.commit()
#             return True, f"Bet {bet_number} placed successfully."
#         except Exception:
#             conn.rollback()
#             return False, "Failed to place bet."
#         finally:
#             conn.close()


# def manual_cashout(username, bet_number):
#     with GAME_LOCK:
#         tick_game_locked()
#         if GAME["status"] != "RUNNING":
#             return False, "Flight not running."
#         multiplier = GAME["current_multiplier"]
#         if multiplier >= GAME["crash_point"]:
#             return False, "Round already crashed."

#         multiplier = round(multiplier, 2)
#         conn = get_db()
#         try:
#             conn.execute("BEGIN IMMEDIATE")
#             bet = conn.execute("SELECT * FROM bets WHERE username = ? AND round_id = ? AND bet_number = ? AND status = 'ACTIVE'", (username, GAME["round_id"], bet_number)).fetchone()
#             if not bet:
#                 conn.rollback()
#                 return False, "No active bet found."

#             winnings = round(float(bet["amount"]) * multiplier, 2)
#             cursor = conn.execute("UPDATE bets SET status = 'WON', cashout_multiplier = ?, winnings = ? WHERE id = ? AND status = 'ACTIVE'", (multiplier, winnings, bet["id"]))
#             if cursor.rowcount != 1:
#                 conn.rollback()
#                 return False, "Cashout failed."

#             conn.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (winnings, username))
#             conn.commit()
#             return True, f"Cashed out at {multiplier:.2f}x — Won KSh {winnings:,.2f}"
#         except Exception:
#             conn.rollback()
#             return False, "Cashout error."
#         finally:
#             conn.close()


# # ============================================================
# # FLASK WEB ROUTES
# # ============================================================

# @app.route("/")
# def index():
#     if "username" not in session:
#         return redirect("/login")
#     return render_template_string(HTML, username=session["username"])


# @app.route("/login", methods=["GET", "POST"])
# def login():
#     error = None
#     if request.method == "POST":
#         username = request.form.get("username", "").strip()
#         password = request.form.get("password", "")

#         conn = get_db()
#         user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
#         conn.close()

#         if user and verify_password(password, user["password"]):
#             session["username"] = user["username"]
#             session["role"] = user["role"]
#             return redirect("/")
#         error = "Invalid credentials."

#     return render_template_string(LOGIN_HTML, error=error)


# @app.route("/register", methods=["GET", "POST"])
# def register():
#     error = None
#     if request.method == "POST":
#         username = request.form.get("username", "").strip()
#         password = request.form.get("password", "")
#         phone = request.form.get("phone_number", "").strip()

#         if not username or not password or not phone:
#             error = "All fields required."
#         else:
#             conn = get_db()
#             try:
#                 conn.execute("""
#                     INSERT INTO users (username, password, phone_number, balance, role, created_at)
#                     VALUES (?, ?, ?, ?, ?, ?)
#                 """, (username, hash_password(password), phone, STARTING_BALANCE, "USER", datetime.now().isoformat()))
#                 conn.commit()
#                 session["username"] = username
#                 session["role"] = "USER"
#                 return redirect("/")
#             except sqlite3.IntegrityError:
#                 error = "Username or phone number already exists."
#             finally:
#                 conn.close()

#     return render_template_string(REGISTER_HTML, error=error)


# @app.route("/logout")
# def logout():
#     session.clear()
#     return redirect("/login")


# @app.route("/api/state")
# def api_state():
#     if "username" not in session:
#         return jsonify({"error": "Unauthorized"}), 401

#     with GAME_LOCK:
#         tick_game_locked()
#         username = session["username"]
#         user = get_user(username)
#         isAdmin = (user["role"] == "ADMIN")

#         conn = get_db()
#         history_rows = conn.execute("SELECT crash_point FROM rounds WHERE ended_at IS NOT NULL ORDER BY id DESC LIMIT 20").fetchall()
#         history = [float(r["crash_point"]) for r in history_rows][::-1]

#         bet_rows = conn.execute("SELECT bet_number, amount, auto_cashout, cashout_multiplier, winnings, status FROM bets WHERE username = ? AND round_id = ?", (username, GAME["round_id"])).fetchall()
#         conn.close()

#         user_bets = {}
#         all_live_bets = []

#         for b in GAME["bot_bets"]:
#             all_live_bets.append(b)

#         for r in bet_rows:
#             user_bets[str(r["bet_number"])] = dict(r)
#             all_live_bets.append({
#                 "id": f"real_{r['bet_number']}",
#                 "username": username + " (You)",
#                 "amount": r["amount"],
#                 "auto_cashout": r["auto_cashout"],
#                 "status": r["status"],
#                 "cashout_multiplier": r["cashout_multiplier"],
#                 "winnings": r["winnings"]
#             })

#         all_live_bets.sort(key=lambda x: 0 if x["status"] == "ACTIVE" else 1)

#         return jsonify({
#             "status": GAME["status"],
#             "multiplier": GAME["current_multiplier"],
#             "crash_point": GAME["crash_point"] if GAME["status"] == "CRASHED" else None,
#             "next_crash_point": GAME["next_crash_point"] if isAdmin else None,
#             "is_admin": isAdmin,
#             "balance": float(user["balance"]),
#             "bets": user_bets,
#             "live_feed": all_live_bets,
#             "history": history,
#             "round_id": GAME["round_id"]
#         })


# @app.route("/api/bet", methods=["POST"])
# def api_bet():
#     if "username" not in session:
#         return jsonify({"success": False, "message": "Unauthorized"}), 401
#     data = request.get_json() or {}
#     success, msg = place_bet_for_user(session["username"], int(data.get("bet_number", 1)), data.get("amount", 0), data.get("auto_cashout"))
#     return jsonify({"success": success, "message": msg})


# @app.route("/api/cashout", methods=["POST"])
# def api_cashout():
#     if "username" not in session:
#         return jsonify({"success": False, "message": "Unauthorized"}), 401
#     data = request.get_json() or {}
#     success, msg = manual_cashout(session["username"], int(data.get("bet_number", 1)))
#     return jsonify({"success": success, "message": msg})


# @app.route("/api/confirm-deposit", methods=["POST"])
# def api_confirm_deposit():
#     if "username" not in session:
#         return jsonify({"success": False, "message": "Unauthorized"}), 401
#     data = request.get_json() or {}
#     try:
#         amount = float(data.get("amount", 0))
#     except ValueError:
#         return jsonify({"success": False, "message": "Invalid amount."})
#     if amount <= 0:
#         return jsonify({"success": False, "message": "Amount must be greater than zero."})
#     add_balance(session["username"], amount)
#     return jsonify({"success": True, "message": f"Successfully credited KSh {amount:,.2f}!"})


# @app.route("/api/withdraw", methods=["POST"])
# def api_withdraw():
#     if "username" not in session:
#         return jsonify({"success": False, "message": "Unauthorized"}), 401
#     data = request.get_json() or {}
#     try:
#         amount = float(data.get("amount", 0))
#     except ValueError:
#         return jsonify({"success": False, "message": "Invalid amount."})
    
#     username = session["username"]
#     user = get_user(username)
#     if user["balance"] < amount:
#         return jsonify({"success": False, "message": "Insufficient balance."})
#     if deduct_balance(username, amount):
#         return jsonify({"success": True, "message": f"Withdrawal of KSh {amount:,.2f} processed to registered number {user['phone_number']}."})
#     return jsonify({"success": False, "message": "Withdrawal failed."})


# # ============================================================
# # TEMPLATES
# # ============================================================

# LOGIN_HTML = r"""
# <!DOCTYPE html>
# <html lang="en">
# <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Aviator - Login</title>
# <style>
# body { margin:0; min-height:100vh; display:flex; justify-content:center; align-items:center; background:#0f141d; font-family:Arial,sans-serif; color:white; }
# .box { width:100%; max-width:380px; padding:30px; border-radius:14px; background:#181f2c; border:1px solid #273142; box-shadow:0 10px 25px rgba(0,0,0,0.5); box-sizing:border-box; margin:15px; }
# h2 { text-align:center; color:#eab308; }
# input { width:100%; padding:12px; font-size:16px; margin-top:8px; margin-bottom:15px; border-radius:8px; border:1px solid #273142; background:#0f141d; color:white; box-sizing:border-box; }
# button { width:100%; padding:12px; font-size:16px; border:none; border-radius:8px; background:#eab308; color:#0f141d; font-weight:bold; cursor:pointer; }
# button:hover { background:#ca8a04; }
# .error { color:#ef4444; text-align:center; margin-bottom:10px; font-size:14px; }
# p { text-align:center; font-size:14px; color:#9ca3af; }
# a { color:#eab308; text-decoration:none; }
# </style>
# </head>
# <body>
# <div class="box">
#     <h2>✈️ AVIATOR LOGIN</h2>
#     {% if error %}<div class="error">{{ error }}</div>{% endif %}
#     <form method="POST">
#         <label>Username</label>
#         <input type="text" name="username" required>
#         <label>Password</label>
#         <input type="password" name="password" required>
#         <button type="submit">LOG IN</button>
#     </form>
#     <p>No account? <a href="/register">Register</a></p>
# </div>
# </body>
# </html>
# """

# REGISTER_HTML = r"""
# <!DOCTYPE html>
# <html lang="en">
# <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Aviator - Register</title>
# <style>
# body { margin:0; min-height:100vh; display:flex; justify-content:center; align-items:center; background:#0f141d; font-family:Arial,sans-serif; color:white; }
# .box { width:100%; max-width:380px; padding:30px; border-radius:14px; background:#181f2c; border:1px solid #273142; box-shadow:0 10px 25px rgba(0,0,0,0.5); box-sizing:border-box; margin:15px; }
# h2 { text-align:center; color:#eab308; }
# input { width:100%; padding:12px; font-size:16px; margin-top:8px; margin-bottom:15px; border-radius:8px; border:1px solid #273142; background:#0f141d; color:white; box-sizing:border-box; }
# button { width:100%; padding:12px; font-size:16px; border:none; border-radius:8px; background:#eab308; color:#0f141d; font-weight:bold; cursor:pointer; }
# .error { color:#ef4444; text-align:center; margin-bottom:10px; font-size:14px; }
# p { text-align:center; font-size:14px; color:#9ca3af; }
# a { color:#eab308; text-decoration:none; }
# </style>
# </head>
# <body>
# <div class="box">
#     <h2>✈️ REGISTER</h2>
#     {% if error %}<div class="error">{{ error }}</div>{% endif %}
#     <form method="POST">
#         <label>Username</label>
#         <input type="text" name="username" required>
#         <label>Phone Number (Withdrawals Payout)</label>
#         <input type="text" name="phone_number" placeholder="254712345678" required>
#         <label>Password</label>
#         <input type="password" name="password" required>
#         <button type="submit">SIGN UP</button>
#     </form>
#     <p>Already registered? <a href="/login">Login</a></p>
# </div>
# </body>
# </html>
# """

# HTML = r"""
# <!DOCTYPE html>
# <html lang="en">
# <head>
# <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
# <title>Aviator Live</title>
# <style>
# * { box-sizing:border-box; }
# body { margin:0; font-family:-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background:#0b0e14; color:#fff; }
# .header { display:flex; justify-content:space-between; align-items:center; background:#121824; padding:12px 15px; border-bottom:1px solid #222b3d; flex-wrap:wrap; gap:10px; }
# .brand { color:#eab308; font-size:18px; font-weight:900; letter-spacing:1px; }
# .wallet-box { display:flex; gap:12px; align-items:center; font-size:13px; flex-wrap:wrap; }
# .balance-val { color:#22c55e; font-weight:bold; font-size:15px; }

# /* Responsive Main Layout Container */
# .main-container { display:flex; max-width:1400px; margin:15px auto; gap:15px; padding:0 10px; }
# .sidebar-bets { width:320px; min-width:280px; background:#121824; border-radius:12px; border:1px solid #222b3d; padding:12px; height:520px; overflow-y:auto; }
# .game-area { flex:1; display:flex; flex-direction:column; gap:15px; min-width:0; }

# /* History Bar with Green & Red styling */
# .history-bar { display:flex; gap:6px; background:#121824; padding:8px 12px; border-radius:8px; border:1px solid #222b3d; overflow-x:auto; }
# .pill-green { padding:4px 10px; border-radius:12px; font-size:12px; font-weight:bold; background:rgba(34,197,94,0.15); color:#22c55e; border:1px solid #22c55e; white-space:nowrap; }
# .pill-red { padding:4px 10px; border-radius:12px; font-size:12px; font-weight:bold; background:rgba(239,68,68,0.15); color:#ef4444; border:1px solid #ef4444; white-space:nowrap; }

# .aviator-screen { position:relative; height:360px; background:radial-gradient(circle at center, #1b0a1a 0%, #0d060f 60%, #070308 100%); border-radius:12px; border:2px solid #222b3d; display:flex; flex-direction:column; justify-content:center; align-items:center; overflow:hidden; }
# .multiplier-display { font-size:60px; font-weight:900; color:#fff; text-shadow:0 0 20px rgba(239,68,68,0.6); z-index:10; text-align:center; padding:0 10px; }
# .status-msg { font-size:16px; color:#eab308; font-weight:bold; margin-top:5px; z-index:10; }

# .admin-banner { background:#7f1d1d; border:1px solid #ef4444; padding:10px 15px; border-radius:8px; display:flex; justify-content:space-between; align-items:center; font-weight:bold; color:#fca5a5; flex-wrap:wrap; gap:5px; }
# .admin-val { color:#fff; font-size:18px; }

# .controls-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
# .bet-panel { background:#121824; border:1px solid #222b3d; border-radius:12px; padding:12px; }
# input { width:100%; padding:10px; font-size:16px; margin:4px 0 10px 0; border-radius:6px; border:1px solid #273142; background:#0b0e14; color:white; }
# button { width:100%; padding:12px; border:none; border-radius:8px; background:#16a34a; color:white; font-weight:900; cursor:pointer; font-size:14px; }
# button.cashout { background:#dc2626; }
# button:disabled { opacity:0.4; cursor:not-allowed; }

# .wallet-panel { background:#121824; border:1px solid #222b3d; border-radius:12px; padding:12px; margin-top:5px; }
# .wallet-row { display:flex; gap:10px; margin-top:8px; flex-wrap:wrap; }
# .wallet-row button { flex:1; min-width:140px; }
# .bet-item { display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #1a2333; font-size:13px; align-items:center; gap:5px; }

# /* Mobile & Android Adaptability */
# @media(max-width: 900px) {
#     .main-container { flex-direction:column-reverse; }
#     .sidebar-bets { width:100%; height:280px; }
#     .controls-grid { grid-template-columns:1fr; }
#     .multiplier-display { font-size:50px; }
#     .aviator-screen { height:280px; }
# }
# </style>
# </head>
# <body>

# <div class="header">
#     <div class="brand">✈️ AVIATOR</div>
#     <div class="wallet-box">
#         <span>Player: <b>{{ username }}</b></span>
#         <span>Balance: <span class="balance-val" id="lblBalance">KSh 0.00</span></span>
#         <a href="/logout" style="color:#ef4444; text-decoration:none; font-weight:bold; margin-left:5px;">Logout</a>
#     </div>
# </div>

# <div class="main-container">
#     <!-- Left Sidebar: Over 50 Live Active Bets Feed -->
#     <div class="sidebar-bets">
#         <h4 style="margin-top:0; color:#9ca3af; border-bottom:1px solid #222b3d; padding-bottom:8px;">ALL BETS (<span id="betCount">0</span>)</h4>
#         <div id="liveBetsFeed"></div>
#     </div>

#     <!-- Main Game Area -->
#     <div class="game-area">
#         <!-- History Bar (Max 20 Rounds: Green if >= 2.00x, Red if < 2.00x) -->
#         <div class="history-bar" id="historyBar"></div>

#         <!-- ADMIN ONLY PANEL -->
#         <div id="adminPanel" class="admin-banner" style="display:none;">
#             <span>👑 ADMIN PANEL: Next Round Preview</span>
#             <span class="admin-val" id="lblNextCrash">--</span>
#         </div>

#         <!-- Aviator Screen -->
#         <div class="aviator-screen">
#             <div class="multiplier-display" id="lblMultiplier">1.00x</div>
#             <div class="status-msg" id="lblStatusMsg">Waiting for next round...</div>
#         </div>

#         <!-- Betting Controls -->
#         <div class="controls-grid">
#             <div class="bet-panel">
#                 <div style="font-weight:bold;">Bet 1</div>
#                 <label>Amount (KSh)</label>
#                 <input type="number" id="betAmount1" value="50" min="1">
#                 <label>Auto Cashout</label>
#                 <input type="number" id="autoCashout1" step="0.1" placeholder="e.g. 2.00">
#                 <button id="btnAction1" onclick="handleBet(1)">PLACE BET</button>
#             </div>
#             <div class="bet-panel">
#                 <div style="font-weight:bold;">Bet 2</div>
#                 <label>Amount (KSh)</label>
#                 <input type="number" id="betAmount2" value="50" min="1">
#                 <label>Auto Cashout</label>
#                 <input type="number" id="autoCashout2" step="0.1" placeholder="e.g. 5.00">
#                 <button id="btnAction2" onclick="handleBet(2)">PLACE BET</button>
#             </div>
#         </div>

#         <!-- Wallet Deposit & Withdrawal -->
#         <div class="wallet-panel">
#             <h4 style="margin-top:0; color:#eab308;">Bank & M-Pesa Wallet</h4>
#             <label>Transaction Amount (KSh)</label>
#             <input type="number" id="walletAmount" placeholder="Enter amount" min="1">
#             <div class="wallet-row">
#                 <button onclick="openDepositLink()" style="background:#2563eb;">Deposit via Prompt Link</button>
#                 <button onclick="withdrawFunds()" style="background:#dc2626;">Withdraw Funds</button>
#             </div>
#         </div>
#     </div>
# </div>

# <script>
# let gameState = "BETTING";
# let userBets = {};

# async function fetchState() {
#     try {
#         let res = await fetch('/api/state');
#         if(res.status === 401) { window.location.href = '/login'; return; }
#         let data = await res.json();
        
#         gameState = data.status;
#         document.getElementById("lblBalance").innerText = "KSh " + data.balance.toLocaleString(undefined, {minimumFractionDigits:2});
        
#         if(data.is_admin) {
#             document.getElementById("adminPanel").style.display = "flex";
#             document.getElementById("lblNextCrash").innerText = data.next_crash_point.toFixed(2) + "x";
#         } else {
#             document.getElementById("adminPanel").style.display = "none";
#         }

#         let histHtml = "";
#         (data.history || []).forEach(val => {
#             let pillClass = val >= 2.0 ? "pill-green" : "pill-red";
#             histHtml += `<div class="${pillClass}">${val.toFixed(2)}x</div>`;
#         });
#         document.getElementById("historyBar").innerHTML = histHtml;

#         let feedHtml = "";
#         let feed = data.live_feed || [];
#         document.getElementById("betCount").innerText = feed.length;
        
#         feed.forEach(bet => {
#             let statusText = "";
#             if(bet.status === "ACTIVE") {
#                 statusText = `<span style="color:#eab308;">Active</span>`;
#             } else if(bet.status === "WON") {
#                 statusText = `<span style="color:#22c55e; font-weight:bold;">${bet.cashout_multiplier.toFixed(2)}x (KSh ${bet.winnings.toLocaleString()})</span>`;
#             } else {
#                 statusText = `<span style="color:#ef4444;">Lost</span>`;
#             }
#             feedHtml += `<div class="bet-item"><span>${bet.username} (KSh ${bet.amount.toLocaleString()})</span>${statusText}</div>`;
#         });
#         document.getElementById("liveBetsFeed").innerHTML = feedHtml;

#         if(gameState === "RUNNING") {
#             document.getElementById("lblMultiplier").innerText = data.multiplier.toFixed(2) + "x";
#             document.getElementById("lblStatusMsg").innerText = "Fly away high!";
#             document.getElementById("lblMultiplier").style.color = "#fff";
#         } else if(gameState === "CRASHED") {
#             document.getElementById("lblMultiplier").innerText = "FLEW AWAY!";
#             document.getElementById("lblStatusMsg").innerText = `Crashed at ${data.crash_point.toFixed(2)}x`;
#             document.getElementById("lblMultiplier").style.color = "#ef4444";
#         } else {
#             document.getElementById("lblMultiplier").innerText = "1.00x";
#             document.getElementById("lblStatusMsg").innerText = "Place your bets!";
#             document.getElementById("lblMultiplier").style.color = "#22c55e";
#         }

#         userBets = data.bets || {};
#         updateButtons();
#     } catch(e) { console.error(e); }
# }

# function updateButtons() {
#     for(let i=1; i<=2; i++) {
#         let btn = document.getElementById("btnAction" + i);
#         let bet = userBets[i];
#         if(bet && bet.status === "ACTIVE") {
#             if(gameState === "RUNNING") {
#                 btn.innerText = "CASHOUT";
#                 btn.className = "cashout";
#                 btn.disabled = false;
#             } else {
#                 btn.innerText = "WAITING FOR ROUND...";
#                 btn.className = "";
#                 btn.disabled = true;
#             }
#         } else {
#             if(gameState === "BETTING") {
#                 btn.innerText = "PLACE BET";
#                 btn.className = "";
#                 btn.disabled = false;
#             } else {
#                 btn.innerText = "BETTING CLOSED";
#                 btn.className = "";
#                 btn.disabled = true;
#             }
#         }
#     }
# }

# async function handleBet(betNum) {
#     let bet = userBets[betNum];
#     if(bet && bet.status === "ACTIVE") {
#         let res = await fetch('/api/cashout', {
#             method: 'POST',
#             headers: {'Content-Type': 'application/json'},
#             body: JSON.stringify({bet_number: betNum})
#         });
#         let d = await res.json();
#         alert(d.message);
#     } else {
#         let amt = document.getElementById("betAmount" + betNum).value;
#         let auto = document.getElementById("autoCashout" + betNum).value;
#         let res = await fetch('/api/bet', {
#             method: 'POST',
#             headers: {'Content-Type': 'application/json'},
#             body: JSON.stringify({bet_number: betNum, amount: amt, auto_cashout: auto})
#         });
#         let d = await res.json();
#         alert(d.message);
#     }
#     fetchState();
# }

# function openDepositLink() {
#     let amt = document.getElementById("walletAmount").value;
#     if(!amt || amt <= 0) { alert("Enter deposit amount first."); return; }

#     // 👉 PASTE YOUR DIRECT PAYMENT PROMPT LINK HERE:
#     let directLink = "https://your-payment-prompt-link.com/pay?amount=" + amt;

#     window.open(directLink, '_blank');
#     if(confirm("Complete the payment prompt on your phone? Click OK once paid to update your balance.")) {
#         fetch('/api/confirm-deposit', {
#             method:'POST',
#             headers:{'Content-Type':'application/json'},
#             body: JSON.stringify({amount: amt})
#         }).then(r => r.json()).then(d => { alert(d.message); fetchState(); });
#     }
# }

# async function withdrawFunds() {
#     let amt = document.getElementById("walletAmount").value;
#     if(!amt || amt <= 0) { alert("Enter withdrawal amount."); return; }
#     let res = await fetch('/api/withdraw', {
#         method:'POST',
#         headers:{'Content-Type':'application/json'},
#         body: JSON.stringify({amount: amt})
#     });
#     let d = await res.json();
#     alert(d.message);
#     fetchState();
# }

# setInterval(fetchState, 300);
# </script>
# </body>
# </html>
# """

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)
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

BETTING_WINDOW = 8.0
MAX_BETS = 2
MAX_WITHDRAWAL = 250000.0
CRASH_DISPLAY_TIME = 2.0
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

    # Create default Admin if missing
    admin = conn.execute("SELECT id FROM users WHERE username = ?", ("admin",)).fetchone()
    if not admin:
        conn.execute("""
            INSERT INTO users (username, password, phone_number, balance, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "admin",
            hash_password("admin123"),
            "254700000000",
            0.0,
            "ADMIN",
            datetime.now().isoformat()
        ))
    else:
        conn.execute("UPDATE users SET role = 'ADMIN' WHERE username = ?", ("admin",))

    conn.commit()
    conn.close()


# ============================================================
# GAME ENGINE & BOT FEED GENERATOR
# ============================================================

def generate_crash_point():
    value = random.random()
    if value < 0.03:
        return round(random.uniform(1.00, 1.15), 2)
    elif value < 0.20:
        return round(random.uniform(1.16, 2.00), 2)
    elif value < 0.60:
        return round(random.uniform(2.01, 5.00), 2)
    elif value < 0.90:
        return round(random.uniform(5.01, 20.00), 2)
    return round(random.uniform(20.00, 100.00), 2)


def calculate_multiplier(elapsed):
    multiplier = 1.0 + (elapsed * 0.25)
    if multiplier > 3:
        multiplier += (elapsed ** 1.15) * 0.03
    return round(multiplier, 2)


GAME = {
    "round_id": None,
    "crash_point": None,
    "next_crash_point": generate_crash_point(),
    "status": "BETTING",
    "betting_start": None,
    "run_start": None,
    "current_multiplier": 1.00,
    "crash_time": None,
    "bot_bets": []
}

FAKE_USERS = [
    "***1", "***2", "***3", "***4", "***5", "***6", "***7", "***8", "***9", "***0",
    "alex***", "brian***", "coll***", "david***", "eric***", "frank***", "grace***",
    "harr***", "ian***", "john***", "kevin***", "lucy***", "mike***", "nick***",
    "oliver***", "peter***", "queen***", "ray***", "sam***", "tom***", "victor***",
    "wendy***", "xav***", "yves***", "zack***", "kelv***", "sylv***", "mash***",
    "kip***", "wanj***", "njeri***", "ochi***", "otien***", "maina***", "chep***",
    "kiprot***", "kibet***", "kipko***", "cherot***", "jelag***", "baras***"
]

def generate_bot_bets():
    """Generates over 50 realistic random player bets for the new round."""
    bets = []
    count = random.randint(55, 75)
    selected_users = random.sample(FAKE_USERS * 2, count)
    
    for i, user in enumerate(selected_users):
        masked = user[:3] + "***" + str(random.randint(0,9))
        amount = round(random.choice([50, 100, 200, 500, 1000, 2500, 5000, 10000]), 2)
        target_cashout = round(random.uniform(1.10, 8.50), 2) if random.random() > 0.15 else None
        
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
    crash_point = GAME["next_crash_point"]
    GAME["next_crash_point"] = generate_crash_point()

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
        if bot["status"] == "ACTIVE" and not bot["auto_cashout"] and multiplier > 1.20:
            if random.random() < 0.04:
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
        GAME["current_multiplier"] = 1.00
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
            print("Game engine error:", e)
        time.sleep(0.05)


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


def add_balance(username, amount):
    conn = get_db()
    conn.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (amount, username))
    conn.commit()
    conn.close()


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
            return True, f"Bet {bet_number} placed successfully."
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
            return False, "Round already crashed."

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
            return True, f"Cashed out at {multiplier:.2f}x — Won KSh {winnings:,.2f}"
        except Exception:
            conn.rollback()
            return False, "Cashout error."
        finally:
            conn.close()


# ============================================================
# FLASK WEB ROUTES
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
            error = "All fields required."
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
                error = "Username or phone number already exists."
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
                "username": username + " (You)",
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
            "next_crash_point": GAME["next_crash_point"] if isAdmin else None,
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


@app.route("/api/confirm-deposit", methods=["POST"])
def api_confirm_deposit():
    if "username" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    data = request.get_json() or {}
    try:
        amount = float(data.get("amount", 0))
    except ValueError:
        return jsonify({"success": False, "message": "Invalid amount."})
    if amount <= 0:
        return jsonify({"success": False, "message": "Amount must be greater than zero."})
    add_balance(session["username"], amount)
    return jsonify({"success": True, "message": f"Successfully credited KSh {amount:,.2f}!"})


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
        return jsonify({"success": True, "message": f"Withdrawal of KSh {amount:,.2f} processed to registered number {user['phone_number']}."})
    return jsonify({"success": False, "message": "Withdrawal failed."})


# ============================================================
# TEMPLATES
# ============================================================

LOGIN_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Aviator - Login</title>
<style>
body { margin:0; min-height:100vh; display:flex; justify-content:center; align-items:center; background:#0f141d; font-family:Arial,sans-serif; color:white; }
.box { width:100%; max-width:380px; padding:30px; border-radius:14px; background:#181f2c; border:1px solid #273142; box-shadow:0 10px 25px rgba(0,0,0,0.5); box-sizing:border-box; margin:15px; }
h2 { text-align:center; color:#eab308; }
input { width:100%; padding:12px; font-size:16px; margin-top:8px; margin-bottom:15px; border-radius:8px; border:1px solid #273142; background:#0f141d; color:white; box-sizing:border-box; }
button { width:100%; padding:12px; font-size:16px; border:none; border-radius:8px; background:#eab308; color:#0f141d; font-weight:bold; cursor:pointer; }
button:hover { background:#ca8a04; }
.error { color:#ef4444; text-align:center; margin-bottom:10px; font-size:14px; }
p { text-align:center; font-size:14px; color:#9ca3af; }
a { color:#eab308; text-decoration:none; }
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
    <p>No account? <a href="/register">Register</a></p>
</div>
</body>
</html>
"""

REGISTER_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Aviator - Register</title>
<style>
body { margin:0; min-height:100vh; display:flex; justify-content:center; align-items:center; background:#0f141d; font-family:Arial,sans-serif; color:white; }
.box { width:100%; max-width:380px; padding:30px; border-radius:14px; background:#181f2c; border:1px solid #273142; box-shadow:0 10px 25px rgba(0,0,0,0.5); box-sizing:border-box; margin:15px; }
h2 { text-align:center; color:#eab308; }
input { width:100%; padding:12px; font-size:16px; margin-top:8px; margin-bottom:15px; border-radius:8px; border:1px solid #273142; background:#0f141d; color:white; box-sizing:border-box; }
button { width:100%; padding:12px; font-size:16px; border:none; border-radius:8px; background:#eab308; color:#0f141d; font-weight:bold; cursor:pointer; }
.error { color:#ef4444; text-align:center; margin-bottom:10px; font-size:14px; }
p { text-align:center; font-size:14px; color:#9ca3af; }
a { color:#eab308; text-decoration:none; }
</style>
</head>
<body>
<div class="box">
    <h2>✈️ REGISTER</h2>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST">
        <label>Username</label>
        <input type="text" name="username" required>
        <label>Phone Number (Withdrawals Payout)</label>
        <input type="text" name="phone_number" placeholder="254712345678" required>
        <label>Password</label>
        <input type="password" name="password" required>
        <button type="submit">SIGN UP</button>
    </form>
    <p>Already registered? <a href="/login">Login</a></p>
</div>
</body>
</html>
"""

HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Aviator Live</title>
<style>
* { box-sizing:border-box; }
body { margin:0; font-family:-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background:#0b0e14; color:#fff; }
.header { display:flex; justify-content:space-between; align-items:center; background:#121824; padding:12px 15px; border-bottom:1px solid #222b3d; flex-wrap:wrap; gap:10px; }
.brand { color:#eab308; font-size:18px; font-weight:900; letter-spacing:1px; }
.wallet-box { display:flex; gap:12px; align-items:center; font-size:13px; flex-wrap:wrap; }
.balance-val { color:#22c55e; font-weight:bold; font-size:15px; }

/* Responsive Main Layout Container */
.main-container { display:flex; max-width:1400px; margin:15px auto; gap:15px; padding:0 10px; }
.sidebar-bets { width:320px; min-width:280px; background:#121824; border-radius:12px; border:1px solid #222b3d; padding:12px; height:520px; overflow-y:auto; }
.game-area { flex:1; display:flex; flex-direction:column; gap:15px; min-width:0; }

/* History Bar with Green & Red styling */
.history-bar { display:flex; gap:6px; background:#121824; padding:8px 12px; border-radius:8px; border:1px solid #222b3d; overflow-x:auto; }
.pill-green { padding:4px 10px; border-radius:12px; font-size:12px; font-weight:bold; background:rgba(34,197,94,0.15); color:#22c55e; border:1px solid #22c55e; white-space:nowrap; }
.pill-red { padding:4px 10px; border-radius:12px; font-size:12px; font-weight:bold; background:rgba(239,68,68,0.15); color:#ef4444; border:1px solid #ef4444; white-space:nowrap; }

/* Aviator Game Canvas & Animation Area */
.aviator-screen { position:relative; height:360px; background:radial-gradient(circle at center, #1b0a1a 0%, #0d060f 60%, #070308 100%); border-radius:12px; border:2px solid #222b3d; display:flex; flex-direction:column; justify-content:center; align-items:center; overflow:hidden; }
.multiplier-display { font-size:60px; font-weight:900; color:#fff; text-shadow:0 0 20px rgba(239,68,68,0.6); z-index:10; text-align:center; padding:0 10px; }
.status-msg { font-size:16px; color:#eab308; font-weight:bold; margin-top:5px; z-index:10; }

/* Flying Airplane Aviator Animation */
.plane-container { position: absolute; bottom: 30px; left: 30px; font-size: 45px; transition: transform 0.1s linear; z-index: 5; pointer-events: none; filter: drop-shadow(0 0 10px rgba(234,179,8,0.7)); display: none; }
.plane-trail { position: absolute; bottom: 0; left: 0; height: 3px; background: linear-gradient(90deg, transparent, #ef4444, #eab308); z-index: 4; display: none; transition: width 0.1s linear; }

.admin-banner { background:#7f1d1d; border:1px solid #ef4444; padding:10px 15px; border-radius:8px; display:flex; justify-content:space-between; align-items:center; font-weight:bold; color:#fca5a5; flex-wrap:wrap; gap:5px; }
.admin-val { color:#fff; font-size:18px; }

.controls-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
.bet-panel { background:#121824; border:1px solid #222b3d; border-radius:12px; padding:12px; }
input { width:100%; padding:10px; font-size:16px; margin:4px 0 10px 0; border-radius:6px; border:1px solid #273142; background:#0b0e14; color:white; }
button { width:100%; padding:12px; border:none; border-radius:8px; background:#16a34a; color:white; font-weight:900; cursor:pointer; font-size:14px; }
button.cashout { background:#dc2626; }
button:disabled { opacity:0.4; cursor:not-allowed; }

.wallet-panel { background:#121824; border:1px solid #222b3d; border-radius:12px; padding:12px; margin-top:5px; }
.wallet-row { display:flex; gap:10px; margin-top:8px; flex-wrap:wrap; }
.wallet-row button { flex:1; min-width:140px; }
.bet-item { display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #1a2333; font-size:13px; align-items:center; gap:5px; }

/* Mobile & Android Adaptability */
@media(max-width: 900px) {
    .main-container { flex-direction:column-reverse; }
    .sidebar-bets { width:100%; height:280px; }
    .controls-grid { grid-template-columns:1fr; }
    .multiplier-display { font-size:50px; }
    .aviator-screen { height:280px; }
}
</style>
</head>
<body>

<div class="header">
    <div class="brand">✈️ AVIATOR</div>
    <div class="wallet-box">
        <span>Player: <b>{{ username }}</b></span>
        <span>Balance: <span class="balance-val" id="lblBalance">KSh 0.00</span></span>
        <a href="/logout" style="color:#ef4444; text-decoration:none; font-weight:bold; margin-left:5px;">Logout</a>
    </div>
</div>

<div class="main-container">
    <!-- Left Sidebar: Over 50 Live Active Bets Feed -->
    <div class="sidebar-bets">
        <h4 style="margin-top:0; color:#9ca3af; border-bottom:1px solid #222b3d; padding-bottom:8px;">ALL BETS (<span id="betCount">0</span>)</h4>
        <div id="liveBetsFeed"></div>
    </div>

    <!-- Main Game Area -->
    <div class="game-area">
        <!-- History Bar (Max 20 Rounds: Green if >= 2.00x, Red if < 2.00x) -->
        <div class="history-bar" id="historyBar"></div>

        <!-- ADMIN ONLY PANEL -->
        <div id="adminPanel" class="admin-banner" style="display:none;">
            <span>ADMIN PANEL: Next Round Preview</span>
            <span class="admin-val" id="lblNextCrash">--</span>
        </div>

        <!-- Aviator Screen with Airplane Animation -->
        <div class="aviator-screen" id="aviatorScreen">
            <div class="plane-trail" id="planeTrail"></div>
            <div class="plane-container" id="planeContainer">✈️</div>
            <div class="multiplier-display" id="lblMultiplier">1.00x</div>
            <div class="status-msg" id="lblStatusMsg">Waiting for next round...</div>
        </div>

        <!-- Betting Controls -->
        <div class="controls-grid">
            <div class="bet-panel">
                <div style="font-weight:bold;">Bet 1</div>
                <label>Amount (KSh)</label>
                <input type="number" id="betAmount1" value="50" min="1">
                <label>Auto Cashout</label>
                <input type="number" id="autoCashout1" step="0.1" placeholder="e.g. 2.00">
                <button id="btnAction1" onclick="handleBet(1)">PLACE BET</button>
            </div>
            <div class="bet-panel">
                <div style="font-weight:bold;">Bet 2</div>
                <label>Amount (KSh)</label>
                <input type="number" id="betAmount2" value="50" min="1">
                <label>Auto Cashout</label>
                <input type="number" id="autoCashout2" step="0.1" placeholder="e.g. 5.00">
                <button id="btnAction2" onclick="handleBet(2)">PLACE BET</button>
            </div>
        </div>

        <!-- Wallet Deposit & Withdrawal -->
        <div class="wallet-panel">
            <h4 style="margin-top:0; color:#eab308;">M-Pesa Wallet</h4>
            <label>Transaction Amount (KSh)</label>
            <input type="number" id="walletAmount" placeholder="Enter amount" min="1">
            <div class="wallet-row">
                <button onclick="openDepositLink()" style="background:#2563eb;">Deposit</button>
                <button onclick="withdrawFunds()" style="background:#dc2626;">Withdraw Funds</button>
            </div>
        </div>
    </div>
</div>

<script>
let gameState = "BETTING";
let userBets = {};

async function fetchState() {
    try {
        let res = await fetch('/api/state');
        if(res.status === 401) { window.location.href = '/login'; return; }
        let data = await res.json();
        
        gameState = data.status;
        document.getElementById("lblBalance").innerText = "KSh " + data.balance.toLocaleString(undefined, {minimumFractionDigits:2});
        
        if(data.is_admin) {
            document.getElementById("adminPanel").style.display = "flex";
            document.getElementById("lblNextCrash").innerText = data.next_crash_point.toFixed(2) + "x";
        } else {
            document.getElementById("adminPanel").style.display = "none";
        }

        let histHtml = "";
        (data.history || []).forEach(val => {
            let pillClass = val >= 2.0 ? "pill-green" : "pill-red";
            histHtml += `<div class="${pillClass}">${val.toFixed(2)}x</div>`;
        });
        document.getElementById("historyBar").innerHTML = histHtml;

        let feedHtml = "";
        let feed = data.live_feed || [];
        document.getElementById("betCount").innerText = feed.length;
        
        feed.forEach(bet => {
            let statusText = "";
            if(bet.status === "ACTIVE") {
                statusText = `<span style="color:#eab308;">Active</span>`;
            } else if(bet.status === "WON") {
                statusText = `<span style="color:#22c55e; font-weight:bold;">${bet.cashout_multiplier.toFixed(2)}x (KSh ${bet.winnings.toLocaleString()})</span>`;
            } else {
                statusText = `<span style="color:#ef4444;">Lost</span>`;
            }
            feedHtml += `<div class="bet-item"><span>${bet.username} (KSh ${bet.amount.toLocaleString()})</span>${statusText}</div>`;
        });
        document.getElementById("liveBetsFeed").innerHTML = feedHtml;

        let planeEl = document.getElementById("planeContainer");
        let trailEl = document.getElementById("planeTrail");

        if(gameState === "RUNNING") {
            document.getElementById("lblMultiplier").innerText = data.multiplier.toFixed(2) + "x";
            document.getElementById("lblStatusMsg").innerText = "Fly away high!";
            document.getElementById("lblMultiplier").style.color = "#fff";
            
            // Show and animate airplane climb path
            planeEl.style.display = "block";
            trailEl.style.display = "block";
            
            let progress = Math.min((data.multiplier - 1.0) / 4.0, 1.0); // scales position with multiplier
            let posX = 30 + (progress * 220);
            let posY = 30 + (progress * 140);
            planeEl.style.transform = `translate(${posX}px, -${posY}px) rotate(-15deg)`;
            trailEl.style.width = (posX + 10) + "px";

        } else if(gameState === "CRASHED") {
            document.getElementById("lblMultiplier").innerText = "FLEW AWAY!";
            document.getElementById("lblStatusMsg").innerText = `Crashed at ${data.crash_point.toFixed(2)}x`;
            document.getElementById("lblMultiplier").style.color = "#ef4444";
            
            // Crash animation effect
            planeEl.style.transform = `translate(260px, -180px) rotate(75deg) scale(0.8)`;
            setTimeout(() => { planeEl.style.display = "none"; trailEl.style.display = "none"; }, 1500);

        } else {
            document.getElementById("lblMultiplier").innerText = "1.00x";
            document.getElementById("lblStatusMsg").innerText = "Place your bets!";
            document.getElementById("lblMultiplier").style.color = "#22c55e";
            planeEl.style.display = "none";
            planeEl.style.transform = "translate(0px, 0px) rotate(0deg)";
            trailEl.style.width = "0px";
            trailEl.style.display = "none";
        }

        userBets = data.bets || {};
        updateButtons();
    } catch(e) { console.error(e); }
}

function updateButtons() {
    for(let i=1; i<=2; i++) {
        let btn = document.getElementById("btnAction" + i);
        let bet = userBets[i];
        if(bet && bet.status === "ACTIVE") {
            if(gameState === "RUNNING") {
                btn.innerText = "CASHOUT";
                btn.className = "cashout";
                btn.disabled = false;
            } else {
                btn.innerText = "WAITING FOR ROUND...";
                btn.className = "";
                btn.disabled = true;
            }
        } else {
            if(gameState === "BETTING") {
                btn.innerText = "PLACE BET";
                btn.className = "";
                btn.disabled = false;
            } else {
                btn.innerText = "BETTING CLOSED";
                btn.className = "";
                btn.disabled = true;
            }
        }
    }
}

async function handleBet(betNum) {
    let bet = userBets[betNum];
    if(bet && bet.status === "ACTIVE") {
        let res = await fetch('/api/cashout', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({bet_number: betNum})
        });
        let d = await res.json();
        alert(d.message);
    } else {
        let amt = document.getElementById("betAmount" + betNum).value;
        let auto = document.getElementById("autoCashout" + betNum).value;
        let res = await fetch('/api/bet', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({bet_number: betNum, amount: amt, auto_cashout: auto})
        });
        let d = await res.json();
        alert(d.message);
    }
    fetchState();
}

function openDepositLink() {
    let amt = document.getElementById("walletAmount").value;
    if(!amt || amt <= 0) { alert("Enter deposit amount first."); return; }

    // 👉 PASTE YOUR DIRECT PAYMENT PROMPT LINK HERE:
    let directLink = "https://your-payment-prompt-link.com/pay?amount=" + amt;

    window.open(directLink, '_blank');
    if(confirm("Complete the payment prompt on your phone? Click OK once paid to update your balance.")) {
        fetch('/api/confirm-deposit', {
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body: JSON.stringify({amount: amt})
        }).then(r => r.json()).then(d => { alert(d.message); fetchState(); });
    }
}

async function withdrawFunds() {
    let amt = document.getElementById("walletAmount").value;
    if(!amt || amt <= 0) { alert("Enter withdrawal amount."); return; }
    let res = await fetch('/api/withdraw', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({amount: amt})
    });
    let d = await res.json();
    alert(d.message);
    fetchState();
}

setInterval(fetchState, 300);
</script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
