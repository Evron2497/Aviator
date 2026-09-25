# # import os
# # import time
# # import random
# # import sqlite3
# # import hashlib
# # import secrets
# # import threading
# # from datetime import datetime

# # from flask import (
# #     Flask,
# #     request,
# #     jsonify,
# #     session,
# #     redirect,
# #     render_template_string,
# # )

# # # ============================================================
# # # CONFIGURATION
# # # ============================================================

# # DB_NAME = "aviator_live.db"

# # BETTING_WINDOW = 8.0
# # MAX_BETS = 2
# # MAX_WITHDRAWAL = 250000.0
# # CRASH_DISPLAY_TIME = 0.5
# # STARTING_BALANCE = 0.0

# # app = Flask(__name__)
# # app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(32))

# # GAME_LOCK = threading.RLock()


# # # ============================================================
# # # DATABASE SETUP
# # # ============================================================

# # def get_db():
# #     conn = sqlite3.connect(DB_NAME, timeout=10, check_same_thread=False)
# #     conn.row_factory = sqlite3.Row
# #     return conn


# # def hash_password(password):
# #     return hashlib.sha256(password.encode("utf-8")).hexdigest()


# # def verify_password(password, hashed):
# #     return secrets.compare_digest(hash_password(password), hashed)


# # def init_db():
# #     conn = get_db()
# #     conn.execute("PRAGMA journal_mode=WAL")

# #     conn.execute("""
# #         CREATE TABLE IF NOT EXISTS users (
# #             id INTEGER PRIMARY KEY AUTOINCREMENT,
# #             username TEXT UNIQUE NOT NULL,
# #             password TEXT NOT NULL,
# #             phone_number TEXT UNIQUE NOT NULL,
# #             balance REAL DEFAULT 0.0,
# #             role TEXT DEFAULT 'USER',
# #             created_at TEXT NOT NULL
# #         )
# #     """)

# #     conn.execute("""
# #         CREATE TABLE IF NOT EXISTS rounds (
# #             id INTEGER PRIMARY KEY AUTOINCREMENT,
# #             crash_point REAL NOT NULL,
# #             started_at TEXT NOT NULL,
# #             ended_at TEXT
# #         )
# #     """)

# #     conn.execute("""
# #         CREATE TABLE IF NOT EXISTS bets (
# #             id INTEGER PRIMARY KEY AUTOINCREMENT,
# #             username TEXT NOT NULL,
# #             round_id INTEGER NOT NULL,
# #             bet_number INTEGER NOT NULL,
# #             amount REAL NOT NULL,
# #             auto_cashout REAL,
# #             cashout_multiplier REAL,
# #             winnings REAL DEFAULT 0,
# #             status TEXT NOT NULL,
# #             created_at TEXT NOT NULL
# #         )
# #     """)

# #     # Create default Admin if missing
# #     admin = conn.execute("SELECT id FROM users WHERE username = ?", ("admin",)).fetchone()
# #     if not admin:
# #         conn.execute("""
# #             INSERT INTO users (username, password, phone_number, balance, role, created_at)
# #             VALUES (?, ?, ?, ?, ?, ?)
# #         """, (
# #             "admin",
# #             hash_password("admin123"),
# #             "254700000000",
# #             0.0,
# #             "ADMIN",
# #             datetime.now().isoformat()
# #         ))
# #     else:
# #         conn.execute("UPDATE users SET role = 'ADMIN' WHERE username = ?", ("admin",))

# #     conn.commit()
# #     conn.close()


# # # ============================================================
# # # GAME ENGINE & BOT FEED GENERATOR
# # # ============================================================

# # def generate_crash_point():
# #     value = random.random()
# #     if value < 0.03:
# #         return round(random.uniform(1.00, 1.15), 2)
# #     elif value < 0.20:
# #         return round(random.uniform(1.16, 2.00), 2)
# #     elif value < 0.60:
# #         return round(random.uniform(2.01, 5.00), 2)
# #     elif value < 0.90:
# #         return round(random.uniform(5.01, 20.00), 2)
# #     return round(random.uniform(20.00, 100.00), 2)


# # def calculate_multiplier(elapsed):
# #     multiplier = 1.0 + (elapsed * 0.25)
# #     if multiplier > 3:
# #         multiplier += (elapsed ** 1.15) * 0.03
# #     return round(multiplier, 2)


# # GAME = {
# #     "round_id": None,
# #     "crash_point": None,
# #     "next_crash_point": generate_crash_point(),
# #     "status": "BETTING",
# #     "betting_start": None,
# #     "run_start": None,
# #     "current_multiplier": 1.00,
# #     "crash_time": None,
# #     "bot_bets": []
# # }

# # FAKE_USERS = [
# #     "***1", "***2", "***3", "***4", "***5", "***6", "***7", "***8", "***9", "***0",
# #     "alex***", "brian***", "coll***", "david***", "eric***", "frank***", "grace***",
# #     "harr***", "ian***", "john***", "kevin***", "lucy***", "mike***", "nick***",
# #     "oliver***", "peter***", "queen***", "ray***", "sam***", "tom***", "victor***",
# #     "wendy***", "xav***", "yves***", "zack***", "kelv***", "sylv***", "mash***",
# #     "kip***", "wanj***", "njeri***", "ochi***", "otien***", "maina***", "chep***",
# #     "kiprot***", "kibet***", "kipko***", "cherot***", "jelag***", "baras***"
# # ]

# # def generate_bot_bets():
# #     """Generates over 50 realistic random player bets for the new round."""
# #     bets = []
# #     count = random.randint(55, 75)
# #     selected_users = random.sample(FAKE_USERS * 2, count)
    
# #     for i, user in enumerate(selected_users):
# #         masked = user[:3] + "***" + str(random.randint(0,9))
# #         amount = round(random.choice([50, 100, 200, 500, 1000, 2500, 5000, 10000]), 2)
# #         target_cashout = round(random.uniform(1.10, 8.50), 2) if random.random() > 0.15 else None
        
# #         bets.append({
# #             "id": f"bot_{i}",
# #             "username": masked,
# #             "amount": amount,
# #             "auto_cashout": target_cashout,
# #             "status": "ACTIVE",
# #             "cashout_multiplier": None,
# #             "winnings": 0.0
# #         })
# #     return bets


# # def create_round_locked():
# #     crash_point = GAME["next_crash_point"]
# #     GAME["next_crash_point"] = generate_crash_point()

# #     now = datetime.now().isoformat()
# #     conn = get_db()
# #     cursor = conn.execute("INSERT INTO rounds (crash_point, started_at) VALUES (?, ?)", (crash_point, now))
# #     round_id = cursor.lastrowid
# #     conn.commit()
# #     conn.close()

# #     GAME["round_id"] = round_id
# #     GAME["crash_point"] = crash_point
# #     GAME["status"] = "BETTING"
# #     GAME["betting_start"] = time.time()
# #     GAME["run_start"] = None
# #     GAME["current_multiplier"] = 1.00
# #     GAME["crash_time"] = None
# #     GAME["bot_bets"] = generate_bot_bets()


# # def initialize_game():
# #     with GAME_LOCK:
# #         if GAME["round_id"] is None:
# #             create_round_locked()


# # def start_running_locked():
# #     if GAME["status"] != "BETTING":
# #         return
# #     GAME["status"] = "RUNNING"
# #     GAME["run_start"] = time.time()
# #     GAME["current_multiplier"] = 1.00


# # def process_auto_cashouts_locked():
# #     if GAME["status"] != "RUNNING":
# #         return

# #     multiplier = GAME["current_multiplier"]
# #     crash_point = GAME["crash_point"]
# #     round_id = GAME["round_id"]

# #     if multiplier >= crash_point:
# #         return

# #     for bot in GAME["bot_bets"]:
# #         if bot["status"] == "ACTIVE" and bot["auto_cashout"] and bot["auto_cashout"] <= multiplier and bot["auto_cashout"] < crash_point:
# #             bot["status"] = "WON"
# #             bot["cashout_multiplier"] = bot["auto_cashout"]
# #             bot["winnings"] = round(bot["amount"] * bot["auto_cashout"], 2)

# #     for bot in GAME["bot_bets"]:
# #         if bot["status"] == "ACTIVE" and not bot["auto_cashout"] and multiplier > 1.20:
# #             if random.random() < 0.04:
# #                 bot["status"] = "WON"
# #                 bot["cashout_multiplier"] = multiplier
# #                 bot["winnings"] = round(bot["amount"] * multiplier, 2)

# #     conn = get_db()
# #     bets = conn.execute("""
# #         SELECT * FROM bets
# #         WHERE round_id = ? AND status = 'ACTIVE' AND auto_cashout IS NOT NULL
# #     """, (round_id,)).fetchall()

# #     for bet in bets:
# #         target = float(bet["auto_cashout"])
# #         if target <= multiplier and target < crash_point:
# #             winnings = round(float(bet["amount"]) * target, 2)
# #             cursor = conn.execute("""
# #                 UPDATE bets
# #                 SET status = 'WON', cashout_multiplier = ?, winnings = ?
# #                 WHERE id = ? AND status = 'ACTIVE'
# #             """, (target, winnings, bet["id"]))

# #             if cursor.rowcount == 1:
# #                 conn.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (winnings, bet["username"]))

# #     conn.commit()
# #     conn.close()


# # def crash_round_locked():
# #     if GAME["status"] == "CRASHED":
# #         return

# #     GAME["status"] = "CRASHED"
# #     GAME["current_multiplier"] = GAME["crash_point"]
# #     GAME["crash_time"] = time.time()

# #     for bot in GAME["bot_bets"]:
# #         if bot["status"] == "ACTIVE":
# #             bot["status"] = "LOST"

# #     conn = get_db()
# #     conn.execute("UPDATE bets SET status = 'LOST' WHERE round_id = ? AND status = 'ACTIVE'", (GAME["round_id"],))
# #     conn.execute("UPDATE rounds SET ended_at = ? WHERE id = ?", (datetime.now().isoformat(), GAME["round_id"]))
# #     conn.commit()
# #     conn.close()


# # def tick_game_locked():
# #     initialize_game()
# #     now = time.time()

# #     if GAME["status"] == "BETTING":
# #         elapsed = now - GAME["betting_start"]
# #         GAME["current_multiplier"] = 1.00
# #         if elapsed >= BETTING_WINDOW:
# #             start_running_locked()

# #     elif GAME["status"] == "RUNNING":
# #         elapsed = now - GAME["run_start"]
# #         multiplier = calculate_multiplier(elapsed)
# #         GAME["current_multiplier"] = multiplier
# #         process_auto_cashouts_locked()

# #         if multiplier >= GAME["crash_point"]:
# #             crash_round_locked()

# #     elif GAME["status"] == "CRASHED":
# #         if GAME["crash_time"] is not None and (now - GAME["crash_time"]) >= CRASH_DISPLAY_TIME:
# #             create_round_locked()


# # def game_loop():
# #     while True:
# #         try:
# #             with GAME_LOCK:
# #                 tick_game_locked()
# #         except Exception as e:
# #             print("Game engine error:", e)
# #         time.sleep(0.05)


# # threading.Thread(target=game_loop, daemon=True).start()
# # init_db()


# # # ============================================================
# # # USER & BET ACTIONS
# # # ============================================================

# # def get_user(username):
# #     conn = get_db()
# #     row = conn.execute("SELECT username, phone_number, balance, role FROM users WHERE username = ?", (username,)).fetchone()
# #     conn.close()
# #     return row


# # def add_balance(username, amount):
# #     conn = get_db()
# #     conn.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (amount, username))
# #     conn.commit()
# #     conn.close()


# # def deduct_balance(username, amount):
# #     conn = get_db()
# #     try:
# #         conn.execute("BEGIN IMMEDIATE")
# #         cursor = conn.execute("UPDATE users SET balance = balance - ? WHERE username = ? AND balance >= ?", (amount, username, amount))
# #         if cursor.rowcount != 1:
# #             conn.rollback()
# #             return False
# #         conn.commit()
# #         return True
# #     except Exception:
# #         conn.rollback()
# #         return False
# #     finally:
# #         conn.close()


# # def place_bet_for_user(username, bet_number, amount, auto_cashout):
# #     with GAME_LOCK:
# #         tick_game_locked()
# #         if bet_number not in [1, 2]:
# #             return False, "Invalid bet slot."
# #         if GAME["status"] != "BETTING":
# #             return False, "Betting closed for this round."

# #         try:
# #             amount = float(amount)
# #         except ValueError:
# #             return False, "Invalid amount."

# #         if amount <= 0:
# #             return False, "Amount must be greater than zero."

# #         if auto_cashout in (None, "", False):
# #             auto_cashout = None
# #         else:
# #             try:
# #                 auto_cashout = float(auto_cashout)
# #                 if auto_cashout < 1.01:
# #                     return False, "Auto cashout minimum is 1.01x."
# #             except ValueError:
# #                 return False, "Invalid auto cashout value."

# #         conn = get_db()
# #         try:
# #             conn.execute("BEGIN IMMEDIATE")
# #             existing = conn.execute("SELECT id FROM bets WHERE username = ? AND round_id = ? AND bet_number = ?", (username, GAME["round_id"], bet_number)).fetchone()
# #             if existing:
# #                 conn.rollback()
# #                 return False, f"Bet {bet_number} already placed."

# #             user = conn.execute("SELECT balance FROM users WHERE username = ?", (username,)).fetchone()
# #             if not user or float(user["balance"]) < amount:
# #                 conn.rollback()
# #                 return False, "Insufficient balance."

# #             conn.execute("UPDATE users SET balance = balance - ? WHERE username = ?", (amount, username))
# #             conn.execute("""
# #                 INSERT INTO bets (username, round_id, bet_number, amount, auto_cashout, winnings, status, created_at)
# #                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)
# #             """, (username, GAME["round_id"], bet_number, amount, auto_cashout, 0.0, "ACTIVE", datetime.now().isoformat()))
# #             conn.commit()
# #             return True, f"Bet {bet_number} placed successfully."
# #         except Exception:
# #             conn.rollback()
# #             return False, "Failed to place bet."
# #         finally:
# #             conn.close()


# # def manual_cashout(username, bet_number):
# #     with GAME_LOCK:
# #         tick_game_locked()
# #         if GAME["status"] != "RUNNING":
# #             return False, "Flight not running."
# #         multiplier = GAME["current_multiplier"]
# #         if multiplier >= GAME["crash_point"]:
# #             return False, "Round already crashed."

# #         multiplier = round(multiplier, 2)
# #         conn = get_db()
# #         try:
# #             conn.execute("BEGIN IMMEDIATE")
# #             bet = conn.execute("SELECT * FROM bets WHERE username = ? AND round_id = ? AND bet_number = ? AND status = 'ACTIVE'", (username, GAME["round_id"], bet_number)).fetchone()
# #             if not bet:
# #                 conn.rollback()
# #                 return False, "No active bet found."

# #             winnings = round(float(bet["amount"]) * multiplier, 2)
# #             cursor = conn.execute("UPDATE bets SET status = 'WON', cashout_multiplier = ?, winnings = ? WHERE id = ? AND status = 'ACTIVE'", (multiplier, winnings, bet["id"]))
# #             if cursor.rowcount != 1:
# #                 conn.rollback()
# #                 return False, "Cashout failed."

# #             conn.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (winnings, username))
# #             conn.commit()
# #             return True, f"Cashed out at {multiplier:.2f}x — Won KSh {winnings:,.2f}"
# #         except Exception:
# #             conn.rollback()
# #             return False, "Cashout error."
# #         finally:
# #             conn.close()


# # # ============================================================
# # # FLASK WEB ROUTES
# # # ============================================================

# # @app.route("/")
# # def index():
# #     if "username" not in session:
# #         return redirect("/login")
# #     return render_template_string(HTML, username=session["username"])


# # @app.route("/login", methods=["GET", "POST"])
# # def login():
# #     error = None
# #     if request.method == "POST":
# #         username = request.form.get("username", "").strip()
# #         password = request.form.get("password", "")

# #         conn = get_db()
# #         user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
# #         conn.close()

# #         if user and verify_password(password, user["password"]):
# #             session["username"] = user["username"]
# #             session["role"] = user["role"]
# #             return redirect("/")
# #         error = "Invalid credentials."

# #     return render_template_string(LOGIN_HTML, error=error)


# # @app.route("/register", methods=["GET", "POST"])
# # def register():
# #     error = None
# #     if request.method == "POST":
# #         username = request.form.get("username", "").strip()
# #         password = request.form.get("password", "")
# #         phone = request.form.get("phone_number", "").strip()

# #         if not username or not password or not phone:
# #             error = "All fields required."
# #         else:
# #             conn = get_db()
# #             try:
# #                 conn.execute("""
# #                     INSERT INTO users (username, password, phone_number, balance, role, created_at)
# #                     VALUES (?, ?, ?, ?, ?, ?)
# #                 """, (username, hash_password(password), phone, STARTING_BALANCE, "USER", datetime.now().isoformat()))
# #                 conn.commit()
# #                 session["username"] = username
# #                 session["role"] = "USER"
# #                 return redirect("/")
# #             except sqlite3.IntegrityError:
# #                 error = "Username or phone number already exists."
# #             finally:
# #                 conn.close()

# #     return render_template_string(REGISTER_HTML, error=error)


# # @app.route("/logout")
# # def logout():
# #     session.clear()
# #     return redirect("/login")


# # @app.route("/api/state")
# # def api_state():
# #     if "username" not in session:
# #         return jsonify({"error": "Unauthorized"}), 401

# #     with GAME_LOCK:
# #         tick_game_locked()
# #         username = session["username"]
# #         user = get_user(username)
# #         isAdmin = (user["role"] == "ADMIN")

# #         conn = get_db()
# #         history_rows = conn.execute("SELECT crash_point FROM rounds WHERE ended_at IS NOT NULL ORDER BY id DESC LIMIT 20").fetchall()
# #         history = [float(r["crash_point"]) for r in history_rows][::-1]

# #         bet_rows = conn.execute("SELECT bet_number, amount, auto_cashout, cashout_multiplier, winnings, status FROM bets WHERE username = ? AND round_id = ?", (username, GAME["round_id"])).fetchall()
# #         conn.close()

# #         user_bets = {}
# #         all_live_bets = []

# #         for b in GAME["bot_bets"]:
# #             all_live_bets.append(b)

# #         for r in bet_rows:
# #             user_bets[str(r["bet_number"])] = dict(r)
# #             all_live_bets.append({
# #                 "id": f"real_{r['bet_number']}",
# #                 "username": username + " (You)",
# #                 "amount": r["amount"],
# #                 "auto_cashout": r["auto_cashout"],
# #                 "status": r["status"],
# #                 "cashout_multiplier": r["cashout_multiplier"],
# #                 "winnings": r["winnings"]
# #             })

# #         all_live_bets.sort(key=lambda x: 0 if x["status"] == "ACTIVE" else 1)

# #         return jsonify({
# #             "status": GAME["status"],
# #             "multiplier": GAME["current_multiplier"],
# #             "crash_point": GAME["crash_point"] if GAME["status"] == "CRASHED" else None,
# #             "next_crash_point": GAME["next_crash_point"] if isAdmin else None,
# #             "is_admin": isAdmin,
# #             "balance": float(user["balance"]),
# #             "bets": user_bets,
# #             "live_feed": all_live_bets,
# #             "history": history,
# #             "round_id": GAME["round_id"]
# #         })


# # @app.route("/api/bet", methods=["POST"])
# # def api_bet():
# #     if "username" not in session:
# #         return jsonify({"success": False, "message": "Unauthorized"}), 401
# #     data = request.get_json() or {}
# #     success, msg = place_bet_for_user(session["username"], int(data.get("bet_number", 1)), data.get("amount", 0), data.get("auto_cashout"))
# #     return jsonify({"success": success, "message": msg})


# # @app.route("/api/cashout", methods=["POST"])
# # def api_cashout():
# #     if "username" not in session:
# #         return jsonify({"success": False, "message": "Unauthorized"}), 401
# #     data = request.get_json() or {}
# #     success, msg = manual_cashout(session["username"], int(data.get("bet_number", 1)))
# #     return jsonify({"success": success, "message": msg})


# # @app.route("/api/confirm-deposit", methods=["POST"])
# # def api_confirm_deposit():
# #     if "username" not in session:
# #         return jsonify({"success": False, "message": "Unauthorized"}), 401
# #     data = request.get_json() or {}
# #     try:
# #         amount = float(data.get("amount", 0))
# #     except ValueError:
# #         return jsonify({"success": False, "message": "Invalid amount."})
# #     if amount <= 0:
# #         return jsonify({"success": False, "message": "Amount must be greater than zero."})
# #     add_balance(session["username"], amount)
# #     return jsonify({"success": True, "message": f"Successfully credited KSh {amount:,.2f}!"})


# # @app.route("/api/withdraw", methods=["POST"])
# # def api_withdraw():
# #     if "username" not in session:
# #         return jsonify({"success": False, "message": "Unauthorized"}), 401
# #     data = request.get_json() or {}
# #     try:
# #         amount = float(data.get("amount", 0))
# #     except ValueError:
# #         return jsonify({"success": False, "message": "Invalid amount."})
    
# #     username = session["username"]
# #     user = get_user(username)
# #     if user["balance"] < amount:
# #         return jsonify({"success": False, "message": "Insufficient balance."})
# #     if deduct_balance(username, amount):
# #         return jsonify({"success": True, "message": f"Withdrawal of KSh {amount:,.2f} processed to registered number {user['phone_number']}."})
# #     return jsonify({"success": False, "message": "Withdrawal failed."})


# # # ============================================================
# # # TEMPLATES
# # # ============================================================

# # LOGIN_HTML = r"""
# # <!DOCTYPE html>
# # <html lang="en">
# # <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Aviator - Login</title>
# # <style>
# # body { margin:0; min-height:100vh; display:flex; justify-content:center; align-items:center; background:#0f141d; font-family:Arial,sans-serif; color:white; }
# # .box { width:100%; max-width:380px; padding:30px; border-radius:14px; background:#181f2c; border:1px solid #273142; box-shadow:0 10px 25px rgba(0,0,0,0.5); box-sizing:border-box; margin:15px; }
# # h2 { text-align:center; color:#eab308; }
# # input { width:100%; padding:12px; font-size:16px; margin-top:8px; margin-bottom:15px; border-radius:8px; border:1px solid #273142; background:#0f141d; color:white; box-sizing:border-box; }
# # button { width:100%; padding:12px; font-size:16px; border:none; border-radius:8px; background:#eab308; color:#0f141d; font-weight:bold; cursor:pointer; }
# # button:hover { background:#ca8a04; }
# # .error { color:#ef4444; text-align:center; margin-bottom:10px; font-size:14px; }
# # p { text-align:center; font-size:14px; color:#9ca3af; }
# # a { color:#eab308; text-decoration:none; }
# # </style>
# # </head>
# # <body>
# # <div class="box">
# #     <h2>✈️ AVIATOR LOGIN</h2>
# #     {% if error %}<div class="error">{{ error }}</div>{% endif %}
# #     <form method="POST">
# #         <label>Username</label>
# #         <input type="text" name="username" required>
# #         <label>Password</label>
# #         <input type="password" name="password" required>
# #         <button type="submit">LOG IN</button>
# #     </form>
# #     <p>No account? <a href="/register">Register</a></p>
# # </div>
# # </body>
# # </html>
# # """

# # REGISTER_HTML = r"""
# # <!DOCTYPE html>
# # <html lang="en">
# # <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Aviator - Register</title>
# # <style>
# # body { margin:0; min-height:100vh; display:flex; justify-content:center; align-items:center; background:#0f141d; font-family:Arial,sans-serif; color:white; }
# # .box { width:100%; max-width:380px; padding:30px; border-radius:14px; background:#181f2c; border:1px solid #273142; box-shadow:0 10px 25px rgba(0,0,0,0.5); box-sizing:border-box; margin:15px; }
# # h2 { text-align:center; color:#eab308; }
# # input { width:100%; padding:12px; font-size:16px; margin-top:8px; margin-bottom:15px; border-radius:8px; border:1px solid #273142; background:#0f141d; color:white; box-sizing:border-box; }
# # button { width:100%; padding:12px; font-size:16px; border:none; border-radius:8px; background:#eab308; color:#0f141d; font-weight:bold; cursor:pointer; }
# # .error { color:#ef4444; text-align:center; margin-bottom:10px; font-size:14px; }
# # p { text-align:center; font-size:14px; color:#9ca3af; }
# # a { color:#eab308; text-decoration:none; }
# # </style>
# # </head>
# # <body>
# # <div class="box">
# #     <h2>✈️ REGISTER</h2>
# #     {% if error %}<div class="error">{{ error }}</div>{% endif %}
# #     <form method="POST">
# #         <label>Username</label>
# #         <input type="text" name="username" required>
# #         <label>Phone Number (Withdrawals Payout)</label>
# #         <input type="text" name="phone_number" placeholder="254712345678" required>
# #         <label>Password</label>
# #         <input type="password" name="password" required>
# #         <button type="submit">SIGN UP</button>
# #     </form>
# #     <p>Already registered? <a href="/login">Login</a></p>
# # </div>
# # </body>
# # </html>
# # """

# # HTML = r"""
# # <!DOCTYPE html>
# # <html lang="en">
# # <head>
# # <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
# # <title>Aviator Live</title>
# # <style>
# # * { box-sizing:border-box; }
# # body { margin:0; font-family:-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background:#0b0e14; color:#fff; }
# # .header { display:flex; justify-content:space-between; align-items:center; background:#121824; padding:12px 15px; border-bottom:1px solid #222b3d; flex-wrap:wrap; gap:10px; }
# # .brand { color:#eab308; font-size:18px; font-weight:900; letter-spacing:1px; }
# # .wallet-box { display:flex; gap:12px; align-items:center; font-size:13px; flex-wrap:wrap; }
# # .balance-val { color:#22c55e; font-weight:bold; font-size:15px; }

# # /* Responsive Main Layout Container */
# # .main-container { display:flex; max-width:1400px; margin:15px auto; gap:15px; padding:0 10px; }
# # .sidebar-bets { width:320px; min-width:280px; background:#121824; border-radius:12px; border:1px solid #222b3d; padding:12px; height:520px; overflow-y:auto; }
# # .game-area { flex:1; display:flex; flex-direction:column; gap:15px; min-width:0; }

# # /* History Bar with Green & Red styling */
# # .history-bar { display:flex; gap:6px; background:#121824; padding:8px 12px; border-radius:8px; border:1px solid #222b3d; overflow-x:auto; }
# # .pill-green { padding:4px 10px; border-radius:12px; font-size:12px; font-weight:bold; background:rgba(34,197,94,0.15); color:#22c55e; border:1px solid #22c55e; white-space:nowrap; }
# # .pill-red { padding:4px 10px; border-radius:12px; font-size:12px; font-weight:bold; background:rgba(239,68,68,0.15); color:#ef4444; border:1px solid #ef4444; white-space:nowrap; }

# # /* Aviator Game Canvas & Animation Area */
# # .aviator-screen { position:relative; height:360px; background:radial-gradient(circle at center, #1b0a1a 0%, #0d060f 60%, #070308 100%); border-radius:12px; border:2px solid #222b3d; display:flex; flex-direction:column; justify-content:center; align-items:center; overflow:hidden; }
# # .multiplier-display { font-size:60px; font-weight:900; color:#fff; text-shadow:0 0 20px rgba(239,68,68,0.6); z-index:10; text-align:center; padding:0 10px; }
# # .status-msg { font-size:16px; color:#eab308; font-weight:bold; margin-top:5px; z-index:10; }

# # /* Flying Airplane Aviator Animation */
# # .plane-container { position: absolute; bottom: 30px; left: 30px; font-size: 45px; transition: transform 0.1s linear; z-index: 5; pointer-events: none; filter: drop-shadow(0 0 10px rgba(234,179,8,0.7)); display: none; }
# # .plane-trail { position: absolute; bottom: 0; left: 0; height: 3px; background: linear-gradient(90deg, transparent, #ef4444, #eab308); z-index: 4; display: none; transition: width 0.1s linear; }

# # .admin-banner { background:#7f1d1d; border:1px solid #ef4444; padding:10px 15px; border-radius:8px; display:flex; justify-content:space-between; align-items:center; font-weight:bold; color:#fca5a5; flex-wrap:wrap; gap:5px; }
# # .admin-val { color:#fff; font-size:18px; }

# # .controls-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
# # .bet-panel { background:#121824; border:1px solid #222b3d; border-radius:12px; padding:12px; }
# # input { width:100%; padding:10px; font-size:16px; margin:4px 0 10px 0; border-radius:6px; border:1px solid #273142; background:#0b0e14; color:white; }
# # button { width:100%; padding:12px; border:none; border-radius:8px; background:#16a34a; color:white; font-weight:900; cursor:pointer; font-size:14px; }
# # button.cashout { background:#dc2626; }
# # button:disabled { opacity:0.4; cursor:not-allowed; }

# # .wallet-panel { background:#121824; border:1px solid #222b3d; border-radius:12px; padding:12px; margin-top:5px; }
# # .wallet-row { display:flex; gap:10px; margin-top:8px; flex-wrap:wrap; }
# # .wallet-row button { flex:1; min-width:140px; }
# # .bet-item { display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #1a2333; font-size:13px; align-items:center; gap:5px; }

# # /* Mobile & Android Adaptability */
# # @media(max-width: 900px) {
# #     .main-container { flex-direction:column-reverse; }
# #     .sidebar-bets { width:100%; height:280px; }
# #     .controls-grid { grid-template-columns:1fr; }
# #     .multiplier-display { font-size:50px; }
# #     .aviator-screen { height:280px; }
# # }
# # </style>
# # </head>
# # <body>

# # <div class="header">
# #     <div class="brand">✈️ AVIATOR</div>
# #     <div class="wallet-box">
# #         <span>Player: <b>{{ username }}</b></span>
# #         <span>Balance: <span class="balance-val" id="lblBalance">KSh 0.00</span></span>
# #         <a href="/logout" style="color:#ef4444; text-decoration:none; font-weight:bold; margin-left:5px;">Logout</a>
# #     </div>
# # </div>

# # <div class="main-container">
# #     <!-- Left Sidebar: Over 50 Live Active Bets Feed -->
# #     <div class="sidebar-bets">
# #         <h4 style="margin-top:0; color:#9ca3af; border-bottom:1px solid #222b3d; padding-bottom:8px;">ALL BETS (<span id="betCount">0</span>)</h4>
# #         <div id="liveBetsFeed"></div>
# #     </div>

# #     <!-- Main Game Area -->
# #     <div class="game-area">
# #         <!-- History Bar (Max 20 Rounds: Green if >= 2.00x, Red if < 2.00x) -->
# #         <div class="history-bar" id="historyBar"></div>

# #         <!-- ADMIN ONLY PANEL -->
# #         <div id="adminPanel" class="admin-banner" style="display:none;">
# #             <span>ADMIN PANEL: Next Round Preview</span>
# #             <span class="admin-val" id="lblNextCrash">--</span>
# #         </div>

# #         <!-- Aviator Screen with Airplane Animation -->
# #         <div class="aviator-screen" id="aviatorScreen">
# #             <div class="plane-trail" id="planeTrail"></div>
# #             <div class="plane-container" id="planeContainer">✈️</div>
# #             <div class="multiplier-display" id="lblMultiplier">1.00x</div>
# #             <div class="status-msg" id="lblStatusMsg">Waiting for next round...</div>
# #         </div>

# #         <!-- Betting Controls -->
# #         <div class="controls-grid">
# #             <div class="bet-panel">
# #                 <div style="font-weight:bold;">Bet 1</div>
# #                 <label>Amount (KSh)</label>
# #                 <input type="number" id="betAmount1" value="50" min="1">
# #                 <label>Auto Cashout</label>
# #                 <input type="number" id="autoCashout1" step="0.1" placeholder="e.g. 2.00">
# #                 <button id="btnAction1" onclick="handleBet(1)">PLACE BET</button>
# #             </div>
# #             <div class="bet-panel">
# #                 <div style="font-weight:bold;">Bet 2</div>
# #                 <label>Amount (KSh)</label>
# #                 <input type="number" id="betAmount2" value="50" min="1">
# #                 <label>Auto Cashout</label>
# #                 <input type="number" id="autoCashout2" step="0.1" placeholder="e.g. 5.00">
# #                 <button id="btnAction2" onclick="handleBet(2)">PLACE BET</button>
# #             </div>
# #         </div>

# #         <!-- Wallet Deposit & Withdrawal -->
# #         <div class="wallet-panel">
# #             <h4 style="margin-top:0; color:#eab308;">M-Pesa Wallet</h4>
# #             <label>Transaction Amount (KSh)</label>
# #             <input type="number" id="walletAmount" placeholder="Enter amount" min="1">
# #             <div class="wallet-row">
# #                 <button onclick="openDepositLink()" style="background:#2563eb;">Deposit</button>
# #                 <button onclick="withdrawFunds()" style="background:#dc2626;">Withdraw Funds</button>
# #             </div>
# #         </div>
# #     </div>
# # </div>

# # <script>
# # let gameState = "BETTING";
# # let userBets = {};

# # async function fetchState() {
# #     try {
# #         let res = await fetch('/api/state');
# #         if(res.status === 401) { window.location.href = '/login'; return; }
# #         let data = await res.json();
        
# #         gameState = data.status;
# #         document.getElementById("lblBalance").innerText = "KSh " + data.balance.toLocaleString(undefined, {minimumFractionDigits:2});
        
# #         if(data.is_admin) {
# #             document.getElementById("adminPanel").style.display = "flex";
# #             document.getElementById("lblNextCrash").innerText = data.next_crash_point.toFixed(2) + "x";
# #         } else {
# #             document.getElementById("adminPanel").style.display = "none";
# #         }

# #         let histHtml = "";
# #         (data.history || []).forEach(val => {
# #             let pillClass = val >= 2.0 ? "pill-green" : "pill-red";
# #             histHtml += `<div class="${pillClass}">${val.toFixed(2)}x</div>`;
# #         });
# #         document.getElementById("historyBar").innerHTML = histHtml;

# #         let feedHtml = "";
# #         let feed = data.live_feed || [];
# #         document.getElementById("betCount").innerText = feed.length;
        
# #         feed.forEach(bet => {
# #             let statusText = "";
# #             if(bet.status === "ACTIVE") {
# #                 statusText = `<span style="color:#eab308;">Active</span>`;
# #             } else if(bet.status === "WON") {
# #                 statusText = `<span style="color:#22c55e; font-weight:bold;">${bet.cashout_multiplier.toFixed(2)}x (KSh ${bet.winnings.toLocaleString()})</span>`;
# #             } else {
# #                 statusText = `<span style="color:#ef4444;">Lost</span>`;
# #             }
# #             feedHtml += `<div class="bet-item"><span>${bet.username} (KSh ${bet.amount.toLocaleString()})</span>${statusText}</div>`;
# #         });
# #         document.getElementById("liveBetsFeed").innerHTML = feedHtml;

# #         let planeEl = document.getElementById("planeContainer");
# #         let trailEl = document.getElementById("planeTrail");

# #         if(gameState === "RUNNING") {
# #             document.getElementById("lblMultiplier").innerText = data.multiplier.toFixed(2) + "x";
# #             document.getElementById("lblStatusMsg").innerText = "Fly away high!";
# #             document.getElementById("lblMultiplier").style.color = "#fff";
            
# #             // Show and animate airplane climb path
# #             planeEl.style.display = "block";
# #             trailEl.style.display = "block";
            
# #             let progress = Math.min((data.multiplier - 1.0) / 4.0, 1.0); // scales position with multiplier
# #             let posX = 30 + (progress * 220);
# #             let posY = 30 + (progress * 140);
# #             planeEl.style.transform = `translate(${posX}px, -${posY}px) rotate(-15deg)`;
# #             trailEl.style.width = (posX + 10) + "px";

# #         } else if(gameState === "CRASHED") {
# #             document.getElementById("lblMultiplier").innerText = "FLEW AWAY!";
# #             document.getElementById("lblStatusMsg").innerText = `Crashed at ${data.crash_point.toFixed(2)}x`;
# #             document.getElementById("lblMultiplier").style.color = "#ef4444";
            
# #             // Crash animation effect
# #             planeEl.style.transform = `translate(260px, -180px) rotate(75deg) scale(0.8)`;
# #             setTimeout(() => { planeEl.style.display = "none"; trailEl.style.display = "none"; }, 1500);

# #         } else {
# #             document.getElementById("lblMultiplier").innerText = "1.00x";
# #             document.getElementById("lblStatusMsg").innerText = "Place your bets!";
# #             document.getElementById("lblMultiplier").style.color = "#22c55e";
# #             planeEl.style.display = "none";
# #             planeEl.style.transform = "translate(0px, 0px) rotate(0deg)";
# #             trailEl.style.width = "0px";
# #             trailEl.style.display = "none";
# #         }

# #         userBets = data.bets || {};
# #         updateButtons();
# #     } catch(e) { console.error(e); }
# # }

# # function updateButtons() {
# #     for(let i=1; i<=2; i++) {
# #         let btn = document.getElementById("btnAction" + i);
# #         let bet = userBets[i];
# #         if(bet && bet.status === "ACTIVE") {
# #             if(gameState === "RUNNING") {
# #                 btn.innerText = "CASHOUT";
# #                 btn.className = "cashout";
# #                 btn.disabled = false;
# #             } else {
# #                 btn.innerText = "WAITING FOR ROUND...";
# #                 btn.className = "";
# #                 btn.disabled = true;
# #             }
# #         } else {
# #             if(gameState === "BETTING") {
# #                 btn.innerText = "PLACE BET";
# #                 btn.className = "";
# #                 btn.disabled = false;
# #             } else {
# #                 btn.innerText = "BETTING CLOSED";
# #                 btn.className = "";
# #                 btn.disabled = true;
# #             }
# #         }
# #     }
# # }

# # async function handleBet(betNum) {
# #     let bet = userBets[betNum];
# #     if(bet && bet.status === "ACTIVE") {
# #         let res = await fetch('/api/cashout', {
# #             method: 'POST',
# #             headers: {'Content-Type': 'application/json'},
# #             body: JSON.stringify({bet_number: betNum})
# #         });
# #         let d = await res.json();
# #         alert(d.message);
# #     } else {
# #         let amt = document.getElementById("betAmount" + betNum).value;
# #         let auto = document.getElementById("autoCashout" + betNum).value;
# #         let res = await fetch('/api/bet', {
# #             method: 'POST',
# #             headers: {'Content-Type': 'application/json'},
# #             body: JSON.stringify({bet_number: betNum, amount: amt, auto_cashout: auto})
# #         });
# #         let d = await res.json();
# #         alert(d.message);
# #     }
# #     fetchState();
# # }

# # function openDepositLink() {
# #     let amt = document.getElementById("walletAmount").value;
# #     if(!amt || amt <= 0) { alert("Enter deposit amount first."); return; }

# #     // 👉 PASTE YOUR DIRECT PAYMENT PROMPT LINK HERE:
# #     let directLink = "https://your-payment-prompt-link.com/pay?amount=" + amt;

# #     window.open(directLink, '_blank');
# #     if(confirm("Complete the payment prompt on your phone? Click OK once paid to update your balance.")) {
# #         fetch('/api/confirm-deposit', {
# #             method:'POST',
# #             headers:{'Content-Type':'application/json'},
# #             body: JSON.stringify({amount: amt})
# #         }).then(r => r.json()).then(d => { alert(d.message); fetchState(); });
# #     }
# # }

# # async function withdrawFunds() {
# #     let amt = document.getElementById("walletAmount").value;
# #     if(!amt || amt <= 0) { alert("Enter withdrawal amount."); return; }
# #     let res = await fetch('/api/withdraw', {
# #         method:'POST',
# #         headers:{'Content-Type':'application/json'},
# #         body: JSON.stringify({amount: amt})
# #     });
# #     let d = await res.json();
# #     alert(d.message);
# #     fetchState();
# # }

# # setInterval(fetchState, 300);
# # </script>
# # </body>
# # </html>
# # """

# # if __name__ == "__main__":
# #     app.run(host="0.0.0.0", port=5000, debug=True)
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

# BETTING_WINDOW = 5.0
# MAX_BETS = 2
# MAX_WITHDRAWAL = 250000.0
# CRASH_DISPLAY_TIME = 0.5
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

#     conn.execute("""
#         CREATE TABLE IF NOT EXISTS password_resets (
#             phone_number TEXT PRIMARY KEY,
#             code TEXT NOT NULL,
#             expires_at REAL NOT NULL
#         )
#     """)

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
# # GAME ENGINE & HIGH SPEED ACCELERATION
# # ============================================================

# def generate_crash_point():
#     value = random.random()
#     if value < 0.03:
#         return round(random.uniform(1.00, 1.10), 2)
#     elif value < 0.20:
#         return round(random.uniform(1.11, 2.05), 2)
#     elif value < 0.60:
#         return round(random.uniform(2.06, 5.00), 2)
#     elif value < 0.88:
#         return round(random.uniform(5.01, 20.00), 2)
#     return round(random.uniform(20.00, 200.00), 2)


# def calculate_multiplier(elapsed):
#     multiplier = 1.0 + (elapsed * 0.65) + ((elapsed ** 1.42) * 0.15)
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
#     bets = []
#     count = random.randint(55, 75)
#     selected_users = random.sample(FAKE_USERS * 2, count)
    
#     for i, user in enumerate(selected_users):
#         masked = user[:3] + "***" + str(random.randint(0,9))
#         amount = round(random.choice([50, 100, 200, 500, 1000, 2500, 5000, 10000]), 2)
#         target_cashout = round(random.uniform(1.10, 10.00), 2) if random.random() > 0.15 else None
        
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
#         time.sleep(0.025)


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


# @app.route("/forgot-password", methods=["GET", "POST"])
# def forgot_password():
#     step = request.form.get("step", "request")
#     error = None
#     success = None
#     phone = request.form.get("phone_number", "").strip()

#     if request.method == "POST":
#         conn = get_db()
#         if step == "request":
#             user = conn.execute("SELECT * FROM users WHERE phone_number = ?", (phone,)).fetchone()
#             if user:
#                 code = f"{random.randint(1000, 9999)}"
#                 expires = time.time() + 300
#                 conn.execute("INSERT OR REPLACE INTO password_resets (phone_number, code, expires_at) VALUES (?, ?, ?)", (phone, code, expires))
#                 conn.commit()
#                 success = f"Verification code sent to {phone}. (Simulation Code: {code})"
#                 step = "verify"
#             else:
#                 error = "Phone number not found in our records."
#             conn.close()

#         elif step == "verify":
#             code = request.form.get("code", "").strip()
#             new_pass = request.form.get("new_password", "").strip()
#             record = conn.execute("SELECT * FROM password_resets WHERE phone_number = ?", (phone,)).fetchone()

#             if record and record["code"] == code and time.time() < record["expires_at"]:
#                 if new_pass:
#                     hashed = hash_password(new_pass)
#                     conn.execute("UPDATE users SET password = ? WHERE phone_number = ?", (hashed, phone))
#                     conn.execute("DELETE FROM password_resets WHERE phone_number = ?", (phone,))
#                     conn.commit()
#                     conn.close()
#                     return redirect("/login?reset=success")
#                 else:
#                     error = "Enter a new password."
#                     step = "verify"
#             else:
#                 error = "Invalid or expired verification code."
#                 step = "verify"
#             conn.close()

#     return render_template_string(FORGOT_HTML, step=step, error=error, success=success, phone=phone)


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
# # TEMPLATES (ODIBET AVIATOR THEME + ACCURATE AUDIO & ANIMATION)
# # ============================================================

# LOGIN_HTML = r"""
# <!DOCTYPE html>
# <html lang="en">
# <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Aviator - Login</title>
# <style>
# body { margin:0; min-height:100vh; display:flex; justify-content:center; align-items:center; background:#1b0606; font-family:Arial,sans-serif; color:white; }
# .box { width:100%; max-width:380px; padding:30px; border-radius:14px; background:#2c0c0c; border:1px solid #5a1515; box-shadow:0 10px 25px rgba(0,0,0,0.7); box-sizing:border-box; margin:15px; }
# h2 { text-align:center; color:#eab308; }
# input { width:100%; padding:12px; font-size:16px; margin-top:8px; margin-bottom:15px; border-radius:8px; border:1px solid #5a1515; background:#1b0606; color:white; box-sizing:border-box; }
# button { width:100%; padding:12px; font-size:16px; border:none; border-radius:8px; background:#eab308; color:#1b0606; font-weight:bold; cursor:pointer; }
# button:hover { background:#ca8a04; }
# .error { color:#ef4444; text-align:center; margin-bottom:10px; font-size:14px; }
# .success { color:#22c55e; text-align:center; margin-bottom:10px; font-size:14px; }
# p { text-align:center; font-size:14px; color:#9ca3af; }
# a { color:#eab308; text-decoration:none; }
# </style>
# </head>
# <body>
# <div class="box">
#     <h2>✈️ AVIATOR LOGIN</h2>
#     {% if request.args.get('reset') == 'success' %}
#     <div class="success">Password reset successful! Please log in.</div>
#     {% endif %}
#     {% if error %}<div class="error">{{ error }}</div>{% endif %}
#     <form method="POST">
#         <label>Username</label>
#         <input type="text" name="username" required>
#         <label>Password</label>
#         <input type="password" name="password" required>
#         <button type="submit">LOG IN</button>
#     </form>
#     <p><a href="/forgot-password">Forgot Password?</a></p>
#     <p>No account? <a href="/register">Register</a></p>
# </div>
# </body>
# </html>
# """

# FORGOT_HTML = r"""
# <!DOCTYPE html>
# <html lang="en">
# <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Aviator - Reset Password</title>
# <style>
# body { margin:0; min-height:100vh; display:flex; justify-content:center; align-items:center; background:#1b0606; font-family:Arial,sans-serif; color:white; }
# .box { width:100%; max-width:380px; padding:30px; border-radius:14px; background:#2c0c0c; border:1px solid #5a1515; box-shadow:0 10px 25px rgba(0,0,0,0.7); box-sizing:border-box; margin:15px; }
# h2 { text-align:center; color:#eab308; }
# input { width:100%; padding:12px; font-size:16px; margin-top:8px; margin-bottom:15px; border-radius:8px; border:1px solid #5a1515; background:#1b0606; color:white; box-sizing:border-box; }
# button { width:100%; padding:12px; font-size:16px; border:none; border-radius:8px; background:#eab308; color:#1b0606; font-weight:bold; cursor:pointer; }
# .error { color:#ef4444; text-align:center; margin-bottom:10px; font-size:14px; }
# .success { color:#22c55e; text-align:center; margin-bottom:10px; font-size:14px; }
# p { text-align:center; font-size:14px; color:#9ca3af; }
# a { color:#eab308; text-decoration:none; }
# </style>
# </head>
# <body>
# <div class="box">
#     <h2>🔒 RESET PASSWORD</h2>
#     {% if error %}<div class="error">{{ error }}</div>{% endif %}
#     {% if success %}<div class="success">{{ success }}</div>{% endif %}
    
#     <form method="POST">
#         {% if step == 'request' %}
#         <input type="hidden" name="step" value="request">
#         <label>Registered Phone Number</label>
#         <input type="text" name="phone_number" placeholder="254712345678" required>
#         <button type="submit">SEND VERIFICATION CODE</button>
#         {% elif step == 'verify' %}
#         <input type="hidden" name="step" value="verify">
#         <input type="hidden" name="phone_number" value="{{ phone }}">
#         <label>Enter 4-Digit Code Sent to SMS</label>
#         <input type="text" name="code" placeholder="1234" required>
#         <label>New Password</label>
#         <input type="password" name="new_password" required>
#         <button type="submit">UPDATE PASSWORD</button>
#         {% endif %}
#     </form>
#     <p><a href="/login">Back to Login</a></p>
# </div>
# </body>
# </html>
# """

# REGISTER_HTML = r"""
# <!DOCTYPE html>
# <html lang="en">
# <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Aviator - Register</title>
# <style>
# body { margin:0; min-height:100vh; display:flex; justify-content:center; align-items:center; background:#1b0606; font-family:Arial,sans-serif; color:white; }
# .box { width:100%; max-width:380px; padding:30px; border-radius:14px; background:#2c0c0c; border:1px solid #5a1515; box-shadow:0 10px 25px rgba(0,0,0,0.7); box-sizing:border-box; margin:15px; }
# h2 { text-align:center; color:#eab308; }
# input { width:100%; padding:12px; font-size:16px; margin-top:8px; margin-bottom:15px; border-radius:8px; border:1px solid #5a1515; background:#1b0606; color:white; box-sizing:border-box; }
# button { width:100%; padding:12px; font-size:16px; border:none; border-radius:8px; background:#eab308; color:#1b0606; font-weight:bold; cursor:pointer; }
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
#         <label>Phone Number (Withdrawals & Recovery)</label>
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
# <title>Odibet Aviator Live</title>
# <style>
# * { box-sizing:border-box; }
# body { margin:0; font-family:-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background:#160404; color:#fff; }
# .header { display:flex; justify-content:space-between; align-items:center; background:#240808; padding:12px 15px; border-bottom:2px solid #5a1515; flex-wrap:wrap; gap:10px; }
# .brand { color:#eab308; font-size:18px; font-weight:900; letter-spacing:1px; }
# .wallet-box { display:flex; gap:12px; align-items:center; font-size:13px; flex-wrap:wrap; }
# .balance-val { color:#22c55e; font-weight:bold; font-size:15px; }

# .sound-btn { background:#3a1010; border:1px solid #7a1c1c; color:#cbd5e1; padding:6px 10px; border-radius:6px; cursor:pointer; font-size:12px; font-weight:bold; }
# .sound-btn.active { background:#eab308; color:#1b0606; border-color:#eab308; }

# .main-container { display:flex; max-width:1400px; margin:15px auto; gap:15px; padding:0 10px; }
# .sidebar-bets { width:320px; min-width:280px; background:#240808; border-radius:12px; border:1px solid #5a1515; padding:12px; height:520px; overflow-y:auto; }
# .game-area { flex:1; display:flex; flex-direction:column; gap:15px; min-width:0; }

# .history-bar { display:flex; gap:6px; background:#240808; padding:8px 12px; border-radius:8px; border:1px solid #5a1515; overflow-x:auto; direction:ltr; justify-content:flex-start; align-items:center; }
# .pill-green { padding:4px 10px; border-radius:12px; font-size:12px; font-weight:bold; background:rgba(34,197,94,0.2); color:#22c55e; border:1px solid #22c55e; white-space:nowrap; }
# .pill-red { padding:4px 10px; border-radius:12px; font-size:12px; font-weight:bold; background:rgba(239,68,68,0.2); color:#ef4444; border:1px solid #ef4444; white-space:nowrap; }

# .aviator-screen { position:relative; height:360px; background:radial-gradient(circle at center, #591212 0%, #2b0606 60%, #160202 100%); border-radius:12px; border:2px solid #7a1c1c; display:flex; flex-direction:column; justify-content:center; align-items:center; overflow:hidden; }
# .multiplier-display { font-size:65px; font-weight:900; color:#fff; text-shadow:0 0 25px rgba(239,68,68,0.8); z-index:10; text-align:center; padding:0 10px; }
# .status-msg { font-size:16px; color:#eab308; font-weight:bold; margin-top:5px; z-index:10; }

# svg.flight-path { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 2; pointer-events: none; }
# .plane-icon { position: absolute; font-size: 42px; z-index: 5; pointer-events: none; transform: translate(-50%, 50%) rotate(-10deg); filter: drop-shadow(0 0 14px rgba(239,68,68,0.9)); display: none; transition: transform 0.1s linear; }

# .admin-banner { background:#7f1d1d; border:1px solid #ef4444; padding:10px 15px; border-radius:8px; display:flex; justify-content:space-between; align-items:center; font-weight:bold; color:#fca5a5; flex-wrap:wrap; gap:5px; }
# .admin-val { color:#fff; font-size:18px; }

# .controls-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
# .bet-panel { background:#240808; border:1px solid #5a1515; border-radius:12px; padding:12px; }
# input { width:100%; padding:10px; font-size:16px; margin:4px 0 10px 0; border-radius:6px; border:1px solid #5a1515; background:#160404; color:white; }
# button { width:100%; padding:12px; border:none; border-radius:8px; background:#16a34a; color:white; font-weight:900; cursor:pointer; font-size:14px; }
# button.cashout { background:#dc2626; }
# button:disabled { opacity:0.4; cursor:not-allowed; }

# .wallet-panel { background:#240808; border:1px solid #5a1515; border-radius:12px; padding:12px; margin-top:5px; }
# .wallet-row { display:flex; gap:10px; margin-top:8px; flex-wrap:wrap; }
# .wallet-row button { flex:1; min-width:140px; }
# .bet-item { display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #3a1010; font-size:13px; align-items:center; gap:5px; }

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
#     <div class="brand">✈️ ODIBET AVIATOR</div>
#     <div class="wallet-box">
#         <button id="soundToggle" class="sound-btn active" onclick="toggleSound()">🔊 Sound: ON</button>
#         <span>Player: <b>{{ username }}</b></span>
#         <span>Balance: <span class="balance-val" id="lblBalance">KSh 0.00</span></span>
#         <a href="/logout" style="color:#ef4444; text-decoration:none; font-weight:bold; margin-left:5px;">Logout</a>
#     </div>
# </div>

# <div class="main-container">
#     <div class="sidebar-bets">
#         <h4 style="margin-top:0; color:#eab308; border-bottom:1px solid #5a1515; padding-bottom:8px;">ALL BETS (<span id="betCount">0</span>)</h4>
#         <div id="liveBetsFeed"></div>
#     </div>

#     <div class="game-area">
#         <div class="history-bar" id="historyBar"></div>

#         <div id="adminPanel" class="admin-banner" style="display:none;">
#             <span>ADMIN PANEL: Next Round Preview</span>
#             <span class="admin-val" id="lblNextCrash">--</span>
#         </div>

#         <div class="aviator-screen" id="aviatorScreen">
#             <svg class="flight-path" id="flightSvg" viewBox="0 0 400 300" preserveAspectRatio="none">
#                 <path id="curvePath" d="M 0 300 Q 200 300 400 300" fill="none" stroke="#ef4444" stroke-width="4" />
#             </svg>
#             <div class="plane-icon" id="planeIcon">✈️</div>
            
#             <div class="multiplier-display" id="lblMultiplier">1.00x</div>
#             <div class="status-msg" id="lblStatusMsg">Waiting for next round...</div>
#         </div>

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

#         <div class="wallet-panel">
#             <h4 style="margin-top:0; color:#eab308;">M-Pesa Wallet</h4>
#             <label>Transaction Amount (KSh)</label>
#             <input type="number" id="walletAmount" placeholder="Enter amount" min="1">
#             <div class="wallet-row">
#                 <button onclick="openDepositLink()" style="background:#2563eb;">Deposit</button>
#                 <button onclick="withdrawFunds()" style="background:#dc2626;">Withdraw Funds</button>
#             </div>
#         </div>
#     </div>
# </div>

# <script>
# let gameState = "BETTING";
# let userBets = {};
# let soundEnabled = true;
# let audioCtx = null;

# function initAudio() {
#     if(!audioCtx) {
#         audioCtx = new (window.AudioContext || window.webkitAudioContext)();
#     }
# }

# // Spribe & Odibet Authentic Audio Synthesis Engine
# function playOdibetTakeoffSound() {
#     if(!soundEnabled) return;
#     try {
#         initAudio();
#         let now = audioCtx.currentTime;
#         let osc = audioCtx.createOscillator();
#         let gain = audioCtx.createGain();
#         osc.type = "sawtooth";
#         osc.frequency.setValueAtTime(90, now);
#         osc.frequency.exponentialRampToValueAtTime(700, now + 1.2);
        
#         gain.gain.setValueAtTime(0.12, now);
#         gain.gain.linearRampToValueAtTime(0.001, now + 1.2);
        
#         osc.connect(gain);
#         gain.connect(audioCtx.destination);
#         osc.start(now);
#         osc.stop(now + 1.2);
#     } catch(e) {}
# }

# function playOdibetCashoutSound() {
#     if(!soundEnabled) return;
#     try {
#         initAudio();
#         let now = audioCtx.currentTime;
#         let osc = audioCtx.createOscillator();
#         let gain = audioCtx.createGain();
#         osc.type = "sine";
#         osc.frequency.setValueAtTime(523.25, now);
#         osc.frequency.setValueAtTime(783.99, now + 0.1);
#         osc.frequency.setValueAtTime(1046.50, now + 0.2);
        
#         gain.gain.setValueAtTime(0.2, now);
#         gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.35);
        
#         osc.connect(gain);
#         gain.connect(audioCtx.destination);
#         osc.start(now);
#         osc.stop(now + 0.35);
#     } catch(e) {}
# }

# function playOdibetCrashSound() {
#     if(!soundEnabled) return;
#     try {
#         initAudio();
#         let now = audioCtx.currentTime;
#         let osc = audioCtx.createOscillator();
#         let gain = audioCtx.createGain();
#         osc.type = "sawtooth";
#         osc.frequency.setValueAtTime(220, now);
#         osc.frequency.linearRampToValueAtTime(40, now + 0.55);
        
#         gain.gain.setValueAtTime(0.3, now);
#         gain.gain.linearRampToValueAtTime(0.0001, now + 0.55);
        
#         osc.connect(gain);
#         gain.connect(audioCtx.destination);
#         osc.start(now);
#         osc.stop(now + 0.55);
#     } catch(e) {}
# }

# function toggleSound() {
#     soundEnabled = !soundEnabled;
#     let btn = document.getElementById("soundToggle");
#     if(soundEnabled) {
#         btn.innerText = "🔊 Sound: ON";
#         btn.classList.add("active");
#     } else {
#         btn.innerText = "🔇 Sound: OFF";
#         btn.classList.remove("active");
#     }
# }

# async function fetchState() {
#     try {
#         let res = await fetch('/api/state');
#         if(res.status === 401) { window.location.href = '/login'; return; }
#         let data = await res.json();
        
#         let oldState = gameState;
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

#         let planeEl = document.getElementById("planeIcon");
#         let curvePath = document.getElementById("curvePath");

#         if(gameState === "RUNNING") {
#             if(oldState !== "RUNNING") {
#                 playOdibetTakeoffSound();
#             }

#             document.getElementById("lblMultiplier").innerText = data.multiplier.toFixed(2) + "x";
#             document.getElementById("lblStatusMsg").innerText = "Fly away high!";
#             document.getElementById("lblMultiplier").style.color = "#fff";
            
#             planeEl.style.display = "block";
            
#             let progress = Math.min((data.multiplier - 1.0) / 4.0, 1.0);
#             let svgW = 400, svgH = 300;
#             let targetX = 40 + (progress * 310);
#             let targetY = 270 - (progress * 210);
#             let controlX = targetX * 0.55;
#             let controlY = 280;
            
#             curvePath.setAttribute("d", `M 0 300 Q ${controlX} ${controlY} ${targetX} ${targetY}`);
            
#             let screenBox = document.getElementById("aviatorScreen").getBoundingClientRect();
#             let planeLeft = (targetX / svgW) * screenBox.width;
#             let planeTop = (targetY / svgH) * screenBox.height;
            
#             planeEl.style.left = planeLeft + "px";
#             planeEl.style.top = planeTop + "px";
#             planeEl.style.transform = `translate(-50%, 50%) rotate(${-15 - (progress * 25)}deg)`;

#         } else if(gameState === "CRASHED") {
#             if(oldState === "RUNNING") {
#                 playOdibetCrashSound();
#             }
#             document.getElementById("lblMultiplier").innerText = "FLEW AWAY!";
#             document.getElementById("lblStatusMsg").innerText = `Crashed at ${data.crash_point.toFixed(2)}x`;
#             document.getElementById("lblMultiplier").style.color = "#ef4444";
            
#             setTimeout(() => { planeEl.style.display = "none"; }, 1200);

#         } else {
#             document.getElementById("lblMultiplier").innerText = "1.00x";
#             document.getElementById("lblStatusMsg").innerText = "Place your bets!";
#             document.getElementById("lblMultiplier").style.color = "#22c55e";
#             curvePath.setAttribute("d", "M 0 300 Q 200 300 400 300");
#             planeEl.style.display = "none";
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
#         if(d.success) playOdibetCashoutSound();
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
#         if(d.success) playOdibetTakeoffSound();
#         alert(d.message);
#     }
#     fetchState();
# }

# function openDepositLink() {
#     let amt = document.getElementById("walletAmount").value;
#     if(!amt || amt <= 0) { alert("Enter deposit amount first."); return; }

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

# setInterval(fetchState, 75);
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
# CONFIGURATION & RULES
# ============================================================

DB_NAME = "aviator_live.db"

BETTING_WINDOW = 5.0
MAX_BETS = 2
MIN_DEPOSIT = 200.0
MIN_WITHDRAWAL = 1000.0
CRASH_DISPLAY_TIME = 0.5
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

    conn.execute("""
        CREATE TABLE IF NOT EXISTS password_resets (
            phone_number TEXT PRIMARY KEY,
            code TEXT NOT NULL,
            expires_at REAL NOT NULL
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
            0.0,
            "ADMIN",
            datetime.now().isoformat()
        ))
    else:
        conn.execute("UPDATE users SET role = 'ADMIN' WHERE username = ?", ("admin",))

    conn.commit()
    conn.close()


# ============================================================
# GAME ENGINE & ODIBET ACCELERATION CURVE
# ============================================================

def generate_crash_point():
    value = random.random()
    if value < 0.03:
        return round(random.uniform(1.00, 1.10), 2)
    elif value < 0.20:
        return round(random.uniform(1.11, 2.05), 2)
    elif value < 0.60:
        return round(random.uniform(2.06, 5.00), 2)
    elif value < 0.88:
        return round(random.uniform(5.01, 20.00), 2)
    return round(random.uniform(20.00, 200.00), 2)


def calculate_multiplier(elapsed):
    multiplier = 1.0 + (elapsed * 0.45) + ((elapsed ** 1.65) * 0.12)
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

FIRST_NAMES = [
    "alex", "brian", "coll", "david", "eric", "frank", "grace", "harr", "ian", "john",
    "kevin", "lucy", "mike", "nick", "oliver", "peter", "queen", "ray", "sam", "tom",
    "victor", "wendy", "xav", "yves", "zack", "kelv", "sylv", "mash", "kip", "wanj",
    "njeri", "ochi", "otien", "maina", "chep", "kiprot", "kibet", "kipko", "cherot",
    "jelag", "baras", "mutiso", "odhi", "korir", "kipng", "chepk", "kipke", "kipch"
]

def generate_bot_bets():
    bets = []
    count = random.randint(780, 840)
    for i in range(count):
        prefix = random.choice(FIRST_NAMES)
        masked = prefix[:3] + "***" + str(random.randint(0, 9))
        amount = round(random.choice([50, 100, 200, 500, 1000, 2500, 5000, 10000]), 2)
        target_cashout = round(random.uniform(1.10, 15.00), 2) if random.random() > 0.12 else None
        
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


def process_auto_cashouts_and_bets_locked():
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
        GAME["current_multiplier"] = 1.00
        if elapsed >= BETTING_WINDOW:
            start_running_locked()

    elif GAME["status"] == "RUNNING":
        elapsed = now - GAME["run_start"]
        multiplier = calculate_multiplier(elapsed)
        GAME["current_multiplier"] = multiplier
        process_auto_cashouts_and_bets_locked()

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
        time.sleep(0.025)


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


def mask_username(username):
    if len(username) <= 3:
        return username + "***"
    return username[:3] + "***" + str(len(username))


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
            return False, "Betting closed for this round. Wait for next round."

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
                return False, f"Bet {bet_number} already placed for this round."

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
            return True, f"Bet {bet_number} placed successfully!"
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


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    step = request.form.get("step", "request")
    error = None
    success = None
    phone = request.form.get("phone_number", "").strip()

    if request.method == "POST":
        conn = get_db()
        if step == "request":
            user = conn.execute("SELECT * FROM users WHERE phone_number = ?", (phone,)).fetchone()
            if user:
                code = f"{random.randint(1000, 9999)}"
                expires = time.time() + 300
                conn.execute("INSERT OR REPLACE INTO password_resets (phone_number, code, expires_at) VALUES (?, ?, ?)", (phone, code, expires))
                conn.commit()
                success = f"Verification code sent to {phone}. (Simulation Code: {code})"
                step = "verify"
            else:
                error = "Phone number not found in records."
            conn.close()

        elif step == "verify":
            code = request.form.get("code", "").strip()
            new_pass = request.form.get("new_password", "").strip()
            record = conn.execute("SELECT * FROM password_resets WHERE phone_number = ?", (phone,)).fetchone()

            if record and record["code"] == code and time.time() < record["expires_at"]:
                if new_pass:
                    hashed = hash_password(new_pass)
                    conn.execute("UPDATE users SET password = ? WHERE phone_number = ?", (hashed, phone))
                    conn.execute("DELETE FROM password_resets WHERE phone_number = ?", (phone,))
                    conn.commit()
                    conn.close()
                    return redirect("/login?reset=success")
                else:
                    error = "Enter a new password."
                    step = "verify"
            else:
                error = "Invalid or expired verification code."
                step = "verify"
            conn.close()

    return render_template_string(FORGOT_HTML, step=step, error=error, success=success, phone=phone)


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
        masked_self = mask_username(username)

        conn = get_db()
        history_rows = conn.execute("SELECT crash_point FROM rounds WHERE ended_at IS NOT NULL ORDER BY id DESC LIMIT 25").fetchall()
        history = [float(r["crash_point"]) for r in history_rows][::-1]

        bet_rows = conn.execute("SELECT bet_number, amount, auto_cashout, cashout_multiplier, winnings, status FROM bets WHERE username = ? AND round_id = ?", (username, GAME["round_id"])).fetchall()
        conn.close()

        user_bets = {}
        all_live_bets = []

        for r in bet_rows:
            user_bets[str(r["bet_number"])] = dict(r)
            all_live_bets.append({
                "id": f"real_{r['bet_number']}",
                "username": masked_self + " (You)",
                "amount": r["amount"],
                "auto_cashout": r["auto_cashout"],
                "status": r["status"],
                "cashout_multiplier": r["cashout_multiplier"],
                "winnings": r["winnings"],
                "is_self": True
            })

        for b in GAME["bot_bets"]:
            all_live_bets.append(b)

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
    success, msg = place_bet_for_user(
        session["username"],
        int(data.get("bet_number", 1)),
        data.get("amount", 0),
        data.get("auto_cashout")
    )
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
    
    if amount < MIN_DEPOSIT:
        return jsonify({"success": False, "message": f"Minimum deposit amount is KSh {MIN_DEPOSIT:,.2f}."})
    
    add_balance(session["username"], amount)
    return jsonify({"success": True, "message": f"Successfully deposited KSh {amount:,.2f} via M-Pesa prompt link!"})


@app.route("/api/withdraw", methods=["POST"])
def api_withdraw():
    if "username" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    data = request.get_json() or {}
    try:
        amount = float(data.get("amount", 0))
    except ValueError:
        return jsonify({"success": False, "message": "Invalid amount."})
    
    if amount < MIN_WITHDRAWAL:
        return jsonify({"success": False, "message": f"Minimum withdrawal amount is KSh {MIN_WITHDRAWAL:,.2f}."})
    
    username = session["username"]
    user = get_user(username)
    if user["balance"] < amount:
        return jsonify({"success": False, "message": "Insufficient balance for this withdrawal."})
    
    if deduct_balance(username, amount):
        return jsonify({"success": True, "message": f"Withdrawal request of KSh {amount:,.2f} sent to {user['phone_number']}. Processing via M-Pesa..."})
    return jsonify({"success": False, "message": "Withdrawal failed."})


# ============================================================
# TEMPLATES (LIVE CASH-OUT WINNINGS PREVIEW ON BUTTON)
# ============================================================

LOGIN_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Aviator - Login</title>
<style>
body { margin:0; min-height:100vh; display:flex; justify-content:center; align-items:center; background:#1b0606; font-family:Arial,sans-serif; color:white; }
.box { width:100%; max-width:380px; padding:30px; border-radius:14px; background:#2c0c0c; border:1px solid #5a1515; box-shadow:0 10px 25px rgba(0,0,0,0.7); box-sizing:border-box; margin:15px; }
h2 { text-align:center; color:#eab308; }
input { width:100%; padding:12px; font-size:16px; margin-top:8px; margin-bottom:15px; border-radius:8px; border:1px solid #5a1515; background:#1b0606; color:white; box-sizing:border-box; }
button { width:100%; padding:12px; font-size:16px; border:none; border-radius:8px; background:#eab308; color:#1b0606; font-weight:bold; cursor:pointer; }
button:hover { background:#ca8a04; }
.error { color:#ef4444; text-align:center; margin-bottom:10px; font-size:14px; }
.success { color:#22c55e; text-align:center; margin-bottom:10px; font-size:14px; }
p { text-align:center; font-size:14px; color:#9ca3af; }
a { color:#eab308; text-decoration:none; }
</style>
</head>
<body>
<div class="box">
    <h2>✈️ AVIATOR LOGIN</h2>
    {% if request.args.get('reset') == 'success' %}
    <div class="success">Password reset successful! Please log in.</div>
    {% endif %}
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST">
        <label>Username</label>
        <input type="text" name="username" required>
        <label>Password</label>
        <input type="password" name="password" required>
        <button type="submit">LOG IN</button>
    </form>
    <p><a href="/forgot-password">Forgot Password?</a></p>
    <p>No account? <a href="/register">Register</a></p>
</div>
</body>
</html>
"""

FORGOT_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Aviator - Reset Password</title>
<style>
body { margin:0; min-height:100vh; display:flex; justify-content:center; align-items:center; background:#1b0606; font-family:Arial,sans-serif; color:white; }
.box { width:100%; max-width:380px; padding:30px; border-radius:14px; background:#2c0c0c; border:1px solid #5a1515; box-shadow:0 10px 25px rgba(0,0,0,0.7); box-sizing:border-box; margin:15px; }
h2 { text-align:center; color:#eab308; }
input { width:100%; padding:12px; font-size:16px; margin-top:8px; margin-bottom:15px; border-radius:8px; border:1px solid #5a1515; background:#1b0606; color:white; box-sizing:border-box; }
button { width:100%; padding:12px; font-size:16px; border:none; border-radius:8px; background:#eab308; color:#1b0606; font-weight:bold; cursor:pointer; }
.error { color:#ef4444; text-align:center; margin-bottom:10px; font-size:14px; }
.success { color:#22c55e; text-align:center; margin-bottom:10px; font-size:14px; }
p { text-align:center; font-size:14px; color:#9ca3af; }
a { color:#eab308; text-decoration:none; }
</style>
</head>
<body>
<div class="box">
    <h2>🔒 RESET PASSWORD</h2>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    {% if success %}<div class="success">{{ success }}</div>{% endif %}
    
    <form method="POST">
        {% if step == 'request' %}
        <input type="hidden" name="step" value="request">
        <label>Registered Phone Number</label>
        <input type="text" name="phone_number" placeholder="254712345678" required>
        <button type="submit">SEND VERIFICATION CODE</button>
        {% elif step == 'verify' %}
        <input type="hidden" name="step" value="verify">
        <input type="hidden" name="phone_number" value="{{ phone }}">
        <label>Enter 4-Digit Code Sent to SMS</label>
        <input type="text" name="code" placeholder="1234" required>
        <label>New Password</label>
        <input type="password" name="new_password" required>
        <button type="submit">UPDATE PASSWORD</button>
        {% endif %}
    </form>
    <p><a href="/login">Back to Login</a></p>
</div>
</body>
</html>
"""

REGISTER_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Aviator - Register</title>
<style>
body { margin:0; min-height:100vh; display:flex; justify-content:center; align-items:center; background:#1b0606; font-family:Arial,sans-serif; color:white; }
.box { width:100%; max-width:380px; padding:30px; border-radius:14px; background:#2c0c0c; border:1px solid #5a1515; box-shadow:0 10px 25px rgba(0,0,0,0.7); box-sizing:border-box; margin:15px; }
h2 { text-align:center; color:#eab308; }
input { width:100%; padding:12px; font-size:16px; margin-top:8px; margin-bottom:15px; border-radius:8px; border:1px solid #5a1515; background:#1b0606; color:white; box-sizing:border-box; }
button { width:100%; padding:12px; font-size:16px; border:none; border-radius:8px; background:#eab308; color:#1b0606; font-weight:bold; cursor:pointer; }
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
        <label>Phone Number (Withdrawals & Recovery)</label>
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
<title>Odi Casino Aviator</title>
<style>
* { box-sizing:border-box; }
body { margin:0; font-family:-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background:#0f0f0f; color:#fff; display:flex; justify-content:center; }

.app-wrapper { 
    width:100%; 
    max-width:480px; 
    background:#160404; 
    min-height:100vh; 
    display:flex; 
    flex-direction:column; 
    border-left:1px solid #331010; 
    border-right:1px solid #331010; 
    position:relative; 
    transition: all 0.3s ease;
}

/* Desktop Responsive Layout */
@media (min-width: 900px) {
    body { background: #080202; align-items: center; padding: 20px 0; }
    .app-wrapper { max-width: 1150px; border: 1px solid #4a1515; border-radius: 16px; overflow: hidden; box-shadow: 0 15px 40px rgba(0,0,0,0.9); min-height: 850px; display: grid; grid-template-columns: 280px 1fr 340px; grid-template-rows: auto auto 1fr; }
    
    .top-header { grid-column: 1 / -1; }
    .aviator-subbar { grid-column: 1 / -1; }
    .history-bar { grid-column: 1 / -1; }
    
    .menu-drawer { position: relative !important; left: 0 !important; width: 100% !important; height: 100% !important; box-shadow: none !important; border-right: 1px solid #3a1010 !important; grid-row: 4 / 6; display: flex !important; }
    .menu-header button { display: none !important; }
    
    .center-stage { grid-column: 2; grid-row: 4; display: flex; flex-direction: column; }
    .aviator-screen { height: 360px !important; }
    .betting-container { flex-direction: row !important; gap: 12px; }
    .bet-card { flex: 1; }

    .live-feed-section { grid-column: 3; grid-row: 4; max-height: 100% !important; border-left: 1px solid #3a1010; border-top: none !important; }
    .desktop-hide { display: none !important; }
}

@media (max-width: 899px) {
    .desktop-only-sidebar { display: none; }
    .desktop-only-sidebar.open { display: flex; }
    .center-stage { display: flex; flex-direction: column; width: 100%; }
}

/* Top Header Bar */
.top-header { display:flex; justify-content:space-between; align-items:center; background:#1c0707; padding:12px 16px; border-bottom:1px solid #3a1010; }
.top-left { display:flex; align-items:center; gap:12px; }
.menu-btn { background:none; border:none; color:#fff; font-size:22px; cursor:pointer; }
.odi-logo { text-align:center; line-height:1; }
.odi-txt { font-size:10px; font-weight:bold; color:#fff; letter-spacing:1px; }
.casino-txt { font-size:14px; font-weight:900; color:#ef4444; letter-spacing:1.5px; font-style:italic; }

.deposit-btn { background:#facc15; color:#1a1a1a; border:none; padding:8px 18px; border-radius:8px; font-weight:900; font-size:14px; cursor:pointer; }
.chat-btn { background:#240c0c; border:1px solid #451515; color:#fff; padding:8px 12px; border-radius:8px; cursor:pointer; font-size:14px; }

/* Sub Header Aviator bar */
.aviator-subbar { display:flex; justify-content:space-between; align-items:center; padding:10px 16px; background:#1a0707; border-bottom:1px solid #3a1010; font-size:13px; }
.subbar-left { display:flex; align-items:center; gap:8px; }
.aviator-logo-txt { font-size:16px; font-weight:900; color:#ef4444; font-style:italic; }
.balance-display { color:#facc15; font-weight:bold; font-size:15px; }

/* History Bar */
.history-bar { display:flex; gap:6px; background:#1c0707; padding:8px 14px; overflow-x:auto; border-bottom:1px solid #3a1010; }
.pill-green { padding:3px 10px; border-radius:12px; font-size:12px; font-weight:bold; background:rgba(34,197,94,0.2); color:#22c55e; border:1px solid #22c55e; white-space:nowrap; }
.pill-red { padding:3px 10px; border-radius:12px; font-size:12px; font-weight:bold; background:rgba(239,68,68,0.2); color:#ef4444; border:1px solid #ef4444; white-space:nowrap; }

/* Game Screen */
.aviator-screen { position:relative; height:250px; background:radial-gradient(circle at center, #691515 0%, #2b0606 65%, #160202 100%); border-bottom:2px solid #5a1515; display:flex; flex-direction:column; justify-content:center; align-items:center; overflow:hidden; }
.multiplier-display { font-size:56px; font-weight:900; color:#fff; text-shadow:0 0 25px rgba(239,68,68,0.8); z-index:10; text-align:center; }
.status-msg { font-size:14px; color:#eab308; font-weight:bold; z-index:10; margin-top:4px; }

svg.flight-path { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 2; pointer-events: none; }
.plane-icon { position: absolute; font-size: 38px; z-index: 5; pointer-events: none; transform: translate(-30%, -70%) rotate(-12deg); filter: drop-shadow(0 0 10px rgba(239,68,68,0.9)); display: none; }

/* Side Menu Drawer */
.menu-drawer { position: absolute; top: 0; left: -280px; width: 280px; height: 100%; background: #1c0707; z-index: 100; transition: left 0.3s ease; border-right: 2px solid #5a1515; box-shadow: 5px 0 25px rgba(0,0,0,0.8); display: flex; flex-direction: column; }
.menu-drawer.open { left: 0; }
.menu-header { background: #2c0c0c; padding: 18px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #5a1515; }
.menu-items { padding: 10px 0; flex: 1; }
.menu-item { padding: 15px 20px; font-size: 15px; font-weight: bold; color: #d1d5db; cursor: pointer; border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; align-items: center; gap: 12px; }
.menu-item:hover { background: #3a1010; color: #facc15; }

/* Live Feed Section (800+ Users) */
.live-feed-section { background:#1c0707; border-top:1px solid #3a1010; padding:12px; max-height:260px; overflow-y:auto; }
.feed-header { font-size:12px; font-weight:bold; color:#eab308; margin-bottom:8px; display:flex; justify-content:space-between; }
.feed-item { display:flex; justify-content:space-between; align-items:center; padding:6px 10px; border-bottom:1px solid rgba(255,255,255,0.03); font-size:12px; }
.feed-item.self { background:rgba(234, 179, 8, 0.15); border-left:3px solid #eab308; }

/* Betting Panels Container */
.betting-container { padding:12px; display:flex; flex-direction:column; gap:12px; background:#160404; flex:1; }

.bet-card { background:#1c0707; border:1px solid #3a1010; border-radius:12px; padding:14px; }
.bet-tabs { display:flex; background:#120303; border-radius:8px; padding:3px; margin-bottom:10px; }
.bet-tab { flex:1; text-align:center; padding:6px; font-size:12px; font-weight:bold; color:#888; border-radius:6px; cursor:pointer; }
.bet-tab.active { background:#2c0c0c; color:#fff; }

.auto-box { display:none; margin-bottom:10px; font-size:12px; color:#9ca3af; }
.auto-box.active { display:block; }

.amount-row { display:flex; align-items:center; justify-content:space-between; margin-bottom:10px; }
.amt-btn { background:#2c0c0c; border:1px solid #4a1515; color:#fff; width:38px; height:38px; border-radius:50%; font-size:18px; font-weight:bold; cursor:pointer; display:flex; align-items:center; justify-content:center; }
.amt-value { font-size:20px; font-weight:900; color:#fff; letter-spacing:1px; }

.quick-stakes { display:grid; grid-template-columns:repeat(4, 1fr); gap:6px; margin-bottom:12px; }
.quick-btn { background:#240808; border:1px solid #4a1515; color:#d1d5db; padding:6px; border-radius:6px; font-size:12px; font-weight:bold; cursor:pointer; text-align:center; }
.quick-btn:hover { background:#3a1010; color:#fff; }

.action-btn { width:100%; padding:14px; border:none; border-radius:10px; background:#22c55e; color:white; font-weight:900; font-size:15px; cursor:pointer; text-transform:uppercase; box-shadow:0 4px 12px rgba(34,197,94,0.3); display:flex; flex-direction:column; align-items:center; justify-content:center; line-height:1.2; }
.action-btn.cashout { background:#dc2626; box-shadow:0 4px 12px rgba(220,38,38,0.3); }
.action-btn:disabled { opacity:0.4; cursor:not-allowed; box-shadow:none; }

.admin-banner { background:#7f1d1d; border:1px solid #ef4444; padding:8px 12px; border-radius:8px; display:flex; justify-content:space-between; align-items:center; font-weight:bold; color:#fca5a5; font-size:12px; margin:10px; }
.admin-val { color:#fff; font-size:15px; }

/* Modal overlay */
.modal-overlay { position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); z-index:200; display:none; justify-content:center; align-items:center; padding:20px; }
.modal-content { background:#240808; border:1px solid #5a1515; padding:24px; border-radius:12px; width:100%; max-width:380px; box-sizing:border-box; }
.modal-content h3 { color:#eab308; margin-top:0; }
.modal-content input { width:100%; padding:12px; margin:10px 0; background:#160404; border:1px solid #5a1515; color:#fff; border-radius:6px; box-sizing:border-box; font-size:15px; }
.modal-btns { display:flex; gap:10px; margin-top:10px; }
.modal-btns button { flex:1; padding:12px; border:none; border-radius:6px; font-weight:bold; cursor:pointer; font-size:15px; }
</style>
</head>
<body>

<div class="app-wrapper">
    <!-- Side Menu Drawer -->
    <div class="menu-drawer desktop-only-sidebar" id="menuDrawer">
        <div class="menu-header">
            <span style="font-weight:bold; color:#eab308; font-size:16px;">Odi Menu</span>
            <button class="desktop-hide" onclick="toggleMenu()" style="background:none; border:none; color:#fff; font-size:18px; cursor:pointer;">✕</button>
        </div>
        <div class="menu-items">
            <div class="menu-item" onclick="openDepositModal()">💳 Deposit (Min. KSh 200)</div>
            <div class="menu-item" onclick="openWithdrawModal()">💸 Withdraw (Min. KSh 1,000)</div>
            <div class="menu-item" onclick="showProfile()">👤 My Profile</div>
            <div class="menu-item" onclick="showHowToPlay()">📖 How to Play</div>
            <div class="menu-item" onclick="window.location.href='/logout'" style="color:#ef4444;">🚪 Logout</div>
        </div>
    </div>

    <!-- Top Header -->
    <div class="top-header">
        <div class="top-left">
            <button class="menu-btn desktop-hide" onclick="toggleMenu()">☰</button>
            <div class="odi-logo">
                <div class="odi-txt">odi</div>
                <div class="casino-txt">CASINO</div>
            </div>
        </div>
        <div style="display:flex; gap:10px; align-items:center;">
            <button class="deposit-btn" onclick="openDepositModal()">Deposit</button>
            <button class="chat-btn" id="soundToggle" onclick="toggleSound()">🔊</button>
        </div>
    </div>

    <!-- Center Stage -->
    <div class="center-stage">
        <!-- Aviator Bar -->
        <div class="aviator-subbar">
            <div class="subbar-left">
                <span class="aviator-logo-txt">Aviator</span>
            </div>
            <div>
                <span class="balance-display" id="lblBalance">0.00 KES</span>
            </div>
        </div>

        <!-- History Bar -->
        <div class="history-bar" id="historyBar"></div>

        <!-- Admin Panel -->
        <div id="adminPanel" class="admin-banner" style="display:none;">
            <span>ADMIN PREVIEW:</span>
            <span class="admin-val" id="lblNextCrash">--</span>
        </div>

        <!-- Game Screen -->
        <div class="aviator-screen" id="aviatorScreen">
            <svg class="flight-path" id="flightSvg" viewBox="0 0 400 250" preserveAspectRatio="none">
                <path id="areaPath" d="M 0 250 L 0 250 L 400 250 Z" fill="rgba(239, 68, 68, 0.2)" />
                <path id="curvePath" d="M 0 250 L 0 250" fill="none" stroke="#ef4444" stroke-width="5" stroke-linecap="round" />
            </svg>
            <div class="plane-icon" id="planeIcon">✈️</div>
            
            <div class="multiplier-display" id="lblMultiplier">1.00x</div>
            <div class="status-msg" id="lblStatusMsg">Waiting for next round...</div>
        </div>

        <!-- Betting Controls -->
        <div class="betting-container">
            <!-- Bet 1 -->
            <div class="bet-card">
                <div class="bet-tabs">
                    <div class="bet-tab active" id="tab1_bet" onclick="switchTab(1, 'bet')">Bet</div>
                    <div class="bet-tab" id="tab1_auto" onclick="switchTab(1, 'auto')">Auto</div>
                </div>
                <div class="auto-box" id="autoBox1">
                    <label>Auto Cashout Multiplier</label>
                    <input type="number" id="autoCashout1" step="0.1" value="2.00" min="1.01" style="width:100%; padding:8px; margin-top:4px; background:#160404; border:1px solid #5a1515; color:#fff; border-radius:4px;">
                </div>
                <div class="amount-row">
                    <button class="amt-btn" onclick="adjustAmount(1, -50)">-</button>
                    <div class="amt-value"><input type="number" id="betAmount1" value="200.00" step="50" style="background:transparent; border:none; color:#fff; font-size:20px; font-weight:900; width:110px; text-align:center;"></div>
                    <button class="amt-btn" onclick="adjustAmount(1, 50)">+</button>
                </div>
                <div class="quick-stakes">
                    <div class="quick-btn" onclick="setAmount(1, 200)">200</div>
                    <div class="quick-btn" onclick="setAmount(1, 500)">500</div>
                    <div class="quick-btn" onclick="setAmount(1, 1000)">1,000</div>
                    <div class="quick-btn" onclick="setAmount(1, 5000)">5,000</div>
                </div>
                <button class="action-btn" id="btnAction1" onclick="handleBet(1)">Bet 200.00 KES</button>
            </div>

            <!-- Bet 2 -->
            <div class="bet-card">
                <div class="bet-tabs">
                    <div class="bet-tab active" id="tab2_bet" onclick="switchTab(2, 'bet')">Bet</div>
                    <div class="bet-tab" id="tab2_auto" onclick="switchTab(2, 'auto')">Auto</div>
                </div>
                <div class="auto-box" id="autoBox2">
                    <label>Auto Cashout Multiplier</label>
                    <input type="number" id="autoCashout2" step="0.1" value="5.00" min="1.01" style="width:100%; padding:8px; margin-top:4px; background:#160404; border:1px solid #5a1515; color:#fff; border-radius:4px;">
                </div>
                <div class="amount-row">
                    <button class="amt-btn" onclick="adjustAmount(2, -50)">-</button>
                    <div class="amt-value"><input type="number" id="betAmount2" value="200.00" step="50" style="background:transparent; border:none; color:#fff; font-size:20px; font-weight:900; width:110px; text-align:center;"></div>
                    <button class="amt-btn" onclick="adjustAmount(2, 50)">+</button>
                </div>
                <div class="quick-stakes">
                    <div class="quick-btn" onclick="setAmount(2, 200)">200</div>
                    <div class="quick-btn" onclick="setAmount(2, 500)">500</div>
                    <div class="quick-btn" onclick="setAmount(2, 1000)">1,000</div>
                    <div class="quick-btn" onclick="setAmount(2, 5000)">5,000</div>
                </div>
                <button class="action-btn" id="btnAction2" onclick="handleBet(2)">Bet 200.00 KES</button>
            </div>
        </div>
    </div>

    <!-- Live Active Users Feed (800+ Users with User at Top) -->
    <div class="live-feed-section">
        <div class="feed-header">
            <span>LIVE ACTIVE USERS (~820)</span>
            <span id="activeBetsCount">Bets: 0</span>
        </div>
        <div id="liveFeedList"></div>
    </div>
</div>

<!-- Modal Dialog for Deposit (Prompt Link) & Withdraw -->
<div class="modal-overlay" id="walletModal">
    <div class="modal-content">
        <h3 id="modalTitle">Deposit Funds</h3>
        <p id="modalDesc" style="font-size:13px; color:#aaa;">Paste your M-Pesa payment prompt link or phone number:</p>
        <input type="text" id="modalInputLink" placeholder="https://pay.mpesa.co.ke/... or 2547XXXXXXXX">
        <label style="font-size:12px; color:#aaa;" id="amountLabel">Amount (Min. KSh 200):</label>
        <input type="number" id="modalInputAmount" value="500" min="200">
        <div class="modal-btns">
            <button onclick="closeModal()" style="background:#444; color:#fff;">Cancel</button>
            <button onclick="submitModalAction()" style="background:#22c55e; color:#fff;">Proceed</button>
        </div>
    </div>
</div>

<script>
let gameState = "BETTING";
let userBets = {};
let soundEnabled = true;
let audioCtx = null;
let modalType = 'deposit';
let autoModes = {1: false, 2: false};
let currentGlobalMultiplier = 1.00;

function initAudio() {
    if(!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
}

function playOdibetTakeoffSound() {
    if(!soundEnabled) return;
    try {
        initAudio();
        let now = audioCtx.currentTime;
        let osc = audioCtx.createOscillator();
        let gain = audioCtx.createGain();
        osc.type = "sawtooth";
        osc.frequency.setValueAtTime(80, now);
        osc.frequency.exponentialRampToValueAtTime(750, now + 1.2);
        
        gain.gain.setValueAtTime(0.12, now);
        gain.gain.linearRampToValueAtTime(0.001, now + 1.2);
        
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc.stop(now + 1.2);
    } catch(e) {}
}

function playOdibetCashoutSound() {
    if(!soundEnabled) return;
    try {
        initAudio();
        let now = audioCtx.currentTime;
        let osc = audioCtx.createOscillator();
        let gain = audioCtx.createGain();
        osc.type = "sine";
        osc.frequency.setValueAtTime(523.25, now);
        osc.frequency.setValueAtTime(783.99, now + 0.1);
        osc.frequency.setValueAtTime(1046.50, now + 0.2);
        
        gain.gain.setValueAtTime(0.2, now);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.35);
        
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.35);
    } catch(e) {}
}

function playOdibetCrashSound() {
    if(!soundEnabled) return;
    try {
        initAudio();
        let now = audioCtx.currentTime;
        let osc = audioCtx.createOscillator();
        let gain = audioCtx.createGain();
        osc.type = "sawtooth";
        osc.frequency.setValueAtTime(200, now);
        osc.frequency.linearRampToValueAtTime(35, now + 0.55);
        
        gain.gain.setValueAtTime(0.3, now);
        gain.gain.linearRampToValueAtTime(0.0001, now + 0.55);
        
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.55);
    } catch(e) {}
}

function toggleSound() {
    soundEnabled = !soundEnabled;
    let btn = document.getElementById("soundToggle");
    btn.innerText = soundEnabled ? "🔊" : "🔇";
}

function toggleMenu() {
    let drawer = document.getElementById("menuDrawer");
    if(window.innerWidth < 900) {
        drawer.classList.toggle("open");
    }
}

function showProfile() {
    alert("Logged in user account is active.\nMinimum Deposit: KSh 200\nMinimum Withdrawal: KSh 1,000");
    if(window.innerWidth < 900) toggleMenu();
}

function showHowToPlay() {
    alert("Aviator Rules:\n1. Place your bet before the round starts.\n2. Watch the plane fly and the multiplier increase.\n3. Cash out before the plane flies away to win your stake multiplied by the current multiplier!");
    if(window.innerWidth < 900) toggleMenu();
}

function switchTab(slot, mode) {
    let tabBet = document.getElementById(`tab${slot}_bet`);
    let tabAuto = document.getElementById(`tab${slot}_auto`);
    let autoBox = document.getElementById(`autoBox${slot}`);
    
    if(mode === 'bet') {
        tabBet.classList.add("active");
        tabAuto.classList.remove("active");
        autoBox.classList.remove("active");
        autoModes[slot] = false;
    } else {
        tabAuto.classList.add("active");
        tabBet.classList.remove("active");
        autoBox.classList.add("active");
        autoModes[slot] = true;
    }
}

function setAmount(slot, val) {
    document.getElementById("betAmount" + slot).value = val.toFixed(2);
    updateButtons();
}

function adjustAmount(slot, delta) {
    let inp = document.getElementById("betAmount" + slot);
    let cur = parseFloat(inp.value) || 0;
    let nxt = Math.max(50, cur + delta);
    inp.value = nxt.toFixed(2);
    updateButtons();
}

function openDepositModal() {
    modalType = 'deposit';
    document.getElementById("modalTitle").innerText = "Deposit Funds (Min. KSh 200)";
    document.getElementById("modalDesc").innerText = "Paste your M-Pesa payment prompt link or phone number:";
    document.getElementById("amountLabel").innerText = "Deposit Amount (KES):";
    document.getElementById("modalInputAmount").value = "500";
    document.getElementById("modalInputLink").value = "";
    document.getElementById("walletModal").style.display = "flex";
    if(window.innerWidth < 900) {
        document.getElementById("menuDrawer").classList.remove("open");
    }
}

function openWithdrawModal() {
    modalType = 'withdraw';
    document.getElementById("modalTitle").innerText = "Withdraw Funds (Min. KSh 1,000)";
    document.getElementById("modalDesc").innerText = "Enter your M-Pesa phone number for payout:";
    document.getElementById("amountLabel").innerText = "Withdrawal Amount (KES):";
    document.getElementById("modalInputAmount").value = "1000";
    document.getElementById("modalInputLink").value = "";
    document.getElementById("walletModal").style.display = "flex";
    if(window.innerWidth < 900) {
        document.getElementById("menuDrawer").classList.remove("open");
    }
}

function closeModal() {
    document.getElementById("walletModal").style.display = "none";
}

async function submitModalAction() {
    let amount = parseFloat(document.getElementById("modalInputAmount").value) || 0;
    let linkOrPhone = document.getElementById("modalInputLink").value.trim();
    
    if(modalType === 'deposit') {
        if(amount < 200) { alert("Minimum deposit is KSh 200."); return; }
        if(!linkOrPhone) { alert("Please paste your M-Pesa prompt link or enter your phone number."); return; }
        
        let res = await fetch('/api/confirm-deposit', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({amount: amount, link: linkOrPhone})
        });
        let d = await res.json();
        alert(d.message);
        if(d.success) closeModal();
        fetchState();
    } else {
        if(amount < 1000) { alert("Minimum withdrawal is KSh 1,000."); return; }
        if(!linkOrPhone) { alert("Please enter your M-Pesa phone number."); return; }
        
        let res = await fetch('/api/withdraw', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({amount: amount, phone: linkOrPhone})
        });
        let d = await res.json();
        alert(d.message);
        if(d.success) closeModal();
        fetchState();
    }
}

async function fetchState() {
    try {
        let res = await fetch('/api/state');
        if(res.status === 401) { window.location.href = '/login'; return; }
        let data = await res.json();
        
        let oldState = gameState;
        gameState = data.status;
        currentGlobalMultiplier = data.multiplier;
        
        document.getElementById("lblBalance").innerText = data.balance.toLocaleString(undefined, {minimumFractionDigits:2}) + " KES";
        
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
        document.getElementById("activeBetsCount").innerText = `Total: ${feed.length}`;
        
        feed.forEach(bet => {
            let statusBadge = "";
            let rowClass = bet.is_self ? "feed-item self" : "feed-item";
            
            if(bet.status === "ACTIVE") {
                statusBadge = `<span style="color:#eab308;">In Game</span>`;
            } else if(bet.status === "WON") {
                statusBadge = `<span style="color:#22c55e; font-weight:bold;">${bet.cashout_multiplier.toFixed(2)}x (+${bet.winnings.toLocaleString()})</span>`;
            } else {
                statusBadge = `<span style="color:#ef4444;">Crashed</span>`;
            }
            feedHtml += `<div class="${rowClass}"><span><b>${bet.username}</b> (KSh ${bet.amount.toLocaleString()})</span>${statusBadge}</div>`;
        });
        document.getElementById("liveFeedList").innerHTML = feedHtml;

        let planeEl = document.getElementById("planeIcon");
        let curvePath = document.getElementById("curvePath");
        let areaPath = document.getElementById("areaPath");

        if(gameState === "RUNNING") {
            if(oldState !== "RUNNING") {
                playOdibetTakeoffSound();
            }

            document.getElementById("lblMultiplier").innerText = data.multiplier.toFixed(2) + "x";
            document.getElementById("lblStatusMsg").innerText = "Fly away high!";
            document.getElementById("lblMultiplier").style.color = "#fff";
            
            planeEl.style.display = "block";
            
            let progress = Math.min((data.multiplier - 1.0) / 5.0, 1.0);
            let svgW = 400, svgH = 250;
            let targetX = 30 + (progress * 340);
            let targetY = 240 - (progress * 200);
            
            let pathString = `M 0 250 Q ${targetX * 0.5} ${250 - (targetY * 0.1)}, ${targetX} ${targetY}`;
            curvePath.setAttribute("d", pathString);
            areaPath.setAttribute("d", `${pathString} L ${targetX} 250 L 0 250 Z`);
            
            let screenBox = document.getElementById("aviatorScreen").getBoundingClientRect();
            let planeLeft = (targetX / svgW) * screenBox.width;
            let planeTop = (targetY / svgH) * screenBox.height;
            
            planeEl.style.left = planeLeft + "px";
            planeEl.style.top = planeTop + "px";
            planeEl.style.transform = `translate(-30%, -70%) rotate(${-12 - (progress * 22)}deg)`;

        } else if(gameState === "CRASHED") {
            if(oldState === "RUNNING") {
                playOdibetCrashSound();
            }
            document.getElementById("lblMultiplier").innerText = "FLEW AWAY!";
            document.getElementById("lblStatusMsg").innerText = `Crashed at ${data.crash_point.toFixed(2)}x`;
            document.getElementById("lblMultiplier").style.color = "#ef4444";
            
            setTimeout(() => { planeEl.style.display = "none"; }, 1200);

        } else {
            document.getElementById("lblMultiplier").innerText = "1.00x";
            document.getElementById("lblStatusMsg").innerText = "Place your bets!";
            document.getElementById("lblMultiplier").style.color = "#22c55e";
            curvePath.setAttribute("d", "M 0 250 L 0 250");
            areaPath.setAttribute("d", "M 0 250 L 0 250 L 400 250 Z");
            planeEl.style.display = "none";
        }

        userBets = data.bets || {};
        updateButtons();
    } catch(e) { console.error(e); }
}

function updateButtons() {
    for(let i=1; i<=2; i++) {
        let btn = document.getElementById("btnAction" + i);
        let bet = userBets[i];
        let amt = parseFloat(document.getElementById("betAmount" + i).value) || 0;
        
        if(bet && bet.status === "ACTIVE") {
            if(gameState === "RUNNING") {
                let liveWinnings = (amt * currentGlobalMultiplier).toFixed(2);
                btn.innerHTML = `CASHOUT<span style="font-size:12px; font-weight:normal; color:#fed7aa;">KES ${Number(liveWinnings).toLocaleString()}</span>`;
                btn.className = "action-btn cashout";
                btn.disabled = false;
            } else {
                btn.innerText = "WAITING...";
                btn.className = "action-btn";
                btn.disabled = true;
            }
        } else {
            if(gameState === "BETTING") {
                btn.innerText = `Bet ${amt.toFixed(2)} KES`;
                btn.className = "action-btn";
                btn.disabled = false;
            } else {
                btn.innerText = "BETTING CLOSED";
                btn.className = "action-btn";
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
        if(d.success) playOdibetCashoutSound();
        alert(d.message);
    } else {
        let amt = document.getElementById("betAmount" + betNum).value;
        let autoVal = autoModes[betNum] ? document.getElementById("autoCashout" + betNum).value : null;
        
        let res = await fetch('/api/bet', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({bet_number: betNum, amount: amt, auto_cashout: autoVal})
        });
        let d = await res.json();
        if(d.success) playOdibetTakeoffSound();
        alert(d.message);
    }
    fetchState();
}

setInterval(fetchState, 75);
</script>
</body>
</html>
