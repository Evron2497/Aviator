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
# # # CONFIGURATION & RULES
# # # ============================================================

# # DB_NAME = "aviator_live.db"

# # BETTING_WINDOW = 5.0
# # MAX_BETS = 2
# # MIN_DEPOSIT = 200.0
# # MIN_WITHDRAWAL = 1000.0
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

# #     conn.execute("""
# #         CREATE TABLE IF NOT EXISTS password_resets (
# #             phone_number TEXT PRIMARY KEY,
# #             code TEXT NOT NULL,
# #             expires_at REAL NOT NULL
# #         )
# #     """)

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
# # # GAME ENGINE & ODIBET ACCELERATION CURVE
# # # ============================================================

# # def generate_crash_point():
# #     value = random.random()
# #     if value < 0.03:
# #         return round(random.uniform(1.00, 1.10), 2)
# #     elif value < 0.20:
# #         return round(random.uniform(1.11, 2.05), 2)
# #     elif value < 0.60:
# #         return round(random.uniform(2.06, 5.00), 2)
# #     elif value < 0.88:
# #         return round(random.uniform(5.01, 20.00), 2)
# #     return round(random.uniform(20.00, 200.00), 2)


# # def calculate_multiplier(elapsed):
# #     multiplier = 1.0 + (elapsed * 0.45) + ((elapsed ** 1.65) * 0.12)
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

# # FIRST_NAMES = [
# #     "alex", "brian", "coll", "david", "eric", "frank", "grace", "harr", "ian", "john",
# #     "kevin", "lucy", "mike", "nick", "oliver", "peter", "queen", "ray", "sam", "tom",
# #     "victor", "wendy", "xav", "yves", "zack", "kelv", "sylv", "mash", "kip", "wanj",
# #     "njeri", "ochi", "otien", "maina", "chep", "kiprot", "kibet", "kipko", "cherot",
# #     "jelag", "baras", "mutiso", "odhi", "korir", "kipng", "chepk", "kipke", "kipch"
# # ]

# # def generate_bot_bets():
# #     bets = []
# #     count = random.randint(780, 840)
# #     for i in range(count):
# #         prefix = random.choice(FIRST_NAMES)
# #         masked = prefix[:3] + "***" + str(random.randint(0, 9))
# #         amount = round(random.choice([50, 100, 200, 500, 1000, 2500, 5000, 10000]), 2)
# #         target_cashout = round(random.uniform(1.10, 15.00), 2) if random.random() > 0.12 else None
        
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


# # def process_auto_cashouts_and_bets_locked():
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
# #             if random.random() < 0.05:
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
# #         process_auto_cashouts_and_bets_locked()

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
# #         time.sleep(0.025)


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


# # def mask_username(username):
# #     if len(username) <= 3:
# #         return username + "***"
# #     return username[:3] + "***" + str(len(username))


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
# #             return False, "Betting closed for this round. Wait for next round."

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
# #                 return False, f"Bet {bet_number} already placed for this round."

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
# #             return True, f"Bet {bet_number} placed successfully!"
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


# # @app.route("/forgot-password", methods=["GET", "POST"])
# # def forgot_password():
# #     step = request.form.get("step", "request")
# #     error = None
# #     success = None
# #     phone = request.form.get("phone_number", "").strip()

# #     if request.method == "POST":
# #         conn = get_db()
# #         if step == "request":
# #             user = conn.execute("SELECT * FROM users WHERE phone_number = ?", (phone,)).fetchone()
# #             if user:
# #                 code = f"{random.randint(1000, 9999)}"
# #                 expires = time.time() + 300
# #                 conn.execute("INSERT OR REPLACE INTO password_resets (phone_number, code, expires_at) VALUES (?, ?, ?)", (phone, code, expires))
# #                 conn.commit()
# #                 success = f"Verification code sent to {phone}. (Simulation Code: {code})"
# #                 step = "verify"
# #             else:
# #                 error = "Phone number not found in records."
# #             conn.close()

# #         elif step == "verify":
# #             code = request.form.get("code", "").strip()
# #             new_pass = request.form.get("new_password", "").strip()
# #             record = conn.execute("SELECT * FROM password_resets WHERE phone_number = ?", (phone,)).fetchone()

# #             if record and record["code"] == code and time.time() < record["expires_at"]:
# #                 if new_pass:
# #                     hashed = hash_password(new_pass)
# #                     conn.execute("UPDATE users SET password = ? WHERE phone_number = ?", (hashed, phone))
# #                     conn.execute("DELETE FROM password_resets WHERE phone_number = ?", (phone,))
# #                     conn.commit()
# #                     conn.close()
# #                     return redirect("/login?reset=success")
# #                 else:
# #                     error = "Enter a new password."
# #                     step = "verify"
# #             else:
# #                 error = "Invalid or expired verification code."
# #                 step = "verify"
# #             conn.close()

# #     return render_template_string(FORGOT_HTML, step=step, error=error, success=success, phone=phone)


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
# #         masked_self = mask_username(username)

# #         conn = get_db()
# #         history_rows = conn.execute("SELECT crash_point FROM rounds WHERE ended_at IS NOT NULL ORDER BY id DESC LIMIT 25").fetchall()
# #         history = [float(r["crash_point"]) for r in history_rows][::-1]

# #         bet_rows = conn.execute("SELECT bet_number, amount, auto_cashout, cashout_multiplier, winnings, status FROM bets WHERE username = ? AND round_id = ?", (username, GAME["round_id"])).fetchall()
# #         conn.close()

# #         user_bets = {}
# #         all_live_bets = []

# #         for r in bet_rows:
# #             user_bets[str(r["bet_number"])] = dict(r)
# #             all_live_bets.append({
# #                 "id": f"real_{r['bet_number']}",
# #                 "username": masked_self + " (You)",
# #                 "amount": r["amount"],
# #                 "auto_cashout": r["auto_cashout"],
# #                 "status": r["status"],
# #                 "cashout_multiplier": r["cashout_multiplier"],
# #                 "winnings": r["winnings"],
# #                 "is_self": True
# #             })

# #         for b in GAME["bot_bets"]:
# #             all_live_bets.append(b)

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
# #     success, msg = place_bet_for_user(
# #         session["username"],
# #         int(data.get("bet_number", 1)),
# #         data.get("amount", 0),
# #         data.get("auto_cashout")
# #     )
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
    
# #     if amount < MIN_DEPOSIT:
# #         return jsonify({"success": False, "message": f"Minimum deposit amount is KSh {MIN_DEPOSIT:,.2f}."})
    
# #     add_balance(session["username"], amount)
# #     return jsonify({"success": True, "message": f"Successfully deposited KSh {amount:,.2f} via M-Pesa prompt link!"})


# # @app.route("/api/withdraw", methods=["POST"])
# # def api_withdraw():
# #     if "username" not in session:
# #         return jsonify({"success": False, "message": "Unauthorized"}), 401
# #     data = request.get_json() or {}
# #     try:
# #         amount = float(data.get("amount", 0))
# #     except ValueError:
# #         return jsonify({"success": False, "message": "Invalid amount."})
    
# #     if amount < MIN_WITHDRAWAL:
# #         return jsonify({"success": False, "message": f"Minimum withdrawal amount is KSh {MIN_WITHDRAWAL:,.2f}."})
    
# #     username = session["username"]
# #     user = get_user(username)
# #     if user["balance"] < amount:
# #         return jsonify({"success": False, "message": "Insufficient balance for this withdrawal."})
    
# #     if deduct_balance(username, amount):
# #         return jsonify({"success": True, "message": f"Withdrawal request of KSh {amount:,.2f} sent to {user['phone_number']}. Processing via M-Pesa..."})
# #     return jsonify({"success": False, "message": "Withdrawal failed."})


# # # ============================================================
# # # TEMPLATES (LIVE CASH-OUT WINNINGS PREVIEW ON BUTTON)
# # # ============================================================

# # LOGIN_HTML = r"""
# # <!DOCTYPE html>
# # <html lang="en">
# # <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Aviator - Login</title>
# # <style>
# # body { margin:0; min-height:100vh; display:flex; justify-content:center; align-items:center; background:#1b0606; font-family:Arial,sans-serif; color:white; }
# # .box { width:100%; max-width:380px; padding:30px; border-radius:14px; background:#2c0c0c; border:1px solid #5a1515; box-shadow:0 10px 25px rgba(0,0,0,0.7); box-sizing:border-box; margin:15px; }
# # h2 { text-align:center; color:#eab308; }
# # input { width:100%; padding:12px; font-size:16px; margin-top:8px; margin-bottom:15px; border-radius:8px; border:1px solid #5a1515; background:#1b0606; color:white; box-sizing:border-box; }
# # button { width:100%; padding:12px; font-size:16px; border:none; border-radius:8px; background:#eab308; color:#1b0606; font-weight:bold; cursor:pointer; }
# # button:hover { background:#ca8a04; }
# # .error { color:#ef4444; text-align:center; margin-bottom:10px; font-size:14px; }
# # .success { color:#22c55e; text-align:center; margin-bottom:10px; font-size:14px; }
# # p { text-align:center; font-size:14px; color:#9ca3af; }
# # a { color:#eab308; text-decoration:none; }
# # </style>
# # </head>
# # <body>
# # <div class="box">
# #     <h2>✈️ AVIATOR LOGIN</h2>
# #     {% if request.args.get('reset') == 'success' %}
# #     <div class="success">Password reset successful! Please log in.</div>
# #     {% endif %}
# #     {% if error %}<div class="error">{{ error }}</div>{% endif %}
# #     <form method="POST">
# #         <label>Username</label>
# #         <input type="text" name="username" required>
# #         <label>Password</label>
# #         <input type="password" name="password" required>
# #         <button type="submit">LOG IN</button>
# #     </form>
# #     <p><a href="/forgot-password">Forgot Password?</a></p>
# #     <p>No account? <a href="/register">Register</a></p>
# # </div>
# # </body>
# # </html>
# # """

# # FORGOT_HTML = r"""
# # <!DOCTYPE html>
# # <html lang="en">
# # <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Aviator - Reset Password</title>
# # <style>
# # body { margin:0; min-height:100vh; display:flex; justify-content:center; align-items:center; background:#1b0606; font-family:Arial,sans-serif; color:white; }
# # .box { width:100%; max-width:380px; padding:30px; border-radius:14px; background:#2c0c0c; border:1px solid #5a1515; box-shadow:0 10px 25px rgba(0,0,0,0.7); box-sizing:border-box; margin:15px; }
# # h2 { text-align:center; color:#eab308; }
# # input { width:100%; padding:12px; font-size:16px; margin-top:8px; margin-bottom:15px; border-radius:8px; border:1px solid #5a1515; background:#1b0606; color:white; box-sizing:border-box; }
# # button { width:100%; padding:12px; font-size:16px; border:none; border-radius:8px; background:#eab308; color:#1b0606; font-weight:bold; cursor:pointer; }
# # .error { color:#ef4444; text-align:center; margin-bottom:10px; font-size:14px; }
# # .success { color:#22c55e; text-align:center; margin-bottom:10px; font-size:14px; }
# # p { text-align:center; font-size:14px; color:#9ca3af; }
# # a { color:#eab308; text-decoration:none; }
# # </style>
# # </head>
# # <body>
# # <div class="box">
# #     <h2>🔒 RESET PASSWORD</h2>
# #     {% if error %}<div class="error">{{ error }}</div>{% endif %}
# #     {% if success %}<div class="success">{{ success }}</div>{% endif %}
    
# #     <form method="POST">
# #         {% if step == 'request' %}
# #         <input type="hidden" name="step" value="request">
# #         <label>Registered Phone Number</label>
# #         <input type="text" name="phone_number" placeholder="254712345678" required>
# #         <button type="submit">SEND VERIFICATION CODE</button>
# #         {% elif step == 'verify' %}
# #         <input type="hidden" name="step" value="verify">
# #         <input type="hidden" name="phone_number" value="{{ phone }}">
# #         <label>Enter 4-Digit Code Sent to SMS</label>
# #         <input type="text" name="code" placeholder="1234" required>
# #         <label>New Password</label>
# #         <input type="password" name="new_password" required>
# #         <button type="submit">UPDATE PASSWORD</button>
# #         {% endif %}
# #     </form>
# #     <p><a href="/login">Back to Login</a></p>
# # </div>
# # </body>
# # </html>
# # """

# # REGISTER_HTML = r"""
# # <!DOCTYPE html>
# # <html lang="en">
# # <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Aviator - Register</title>
# # <style>
# # body { margin:0; min-height:100vh; display:flex; justify-content:center; align-items:center; background:#1b0606; font-family:Arial,sans-serif; color:white; }
# # .box { width:100%; max-width:380px; padding:30px; border-radius:14px; background:#2c0c0c; border:1px solid #5a1515; box-shadow:0 10px 25px rgba(0,0,0,0.7); box-sizing:border-box; margin:15px; }
# # h2 { text-align:center; color:#eab308; }
# # input { width:100%; padding:12px; font-size:16px; margin-top:8px; margin-bottom:15px; border-radius:8px; border:1px solid #5a1515; background:#1b0606; color:white; box-sizing:border-box; }
# # button { width:100%; padding:12px; font-size:16px; border:none; border-radius:8px; background:#eab308; color:#1b0606; font-weight:bold; cursor:pointer; }
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
# #         <label>Phone Number (Withdrawals & Recovery)</label>
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
# # <title>Odi Casino Aviator</title>
# # <style>
# # * { box-sizing:border-box; }
# # body { margin:0; font-family:-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background:#0f0f0f; color:#fff; display:flex; justify-content:center; }

# # .app-wrapper { 
# #     width:100%; 
# #     max-width:480px; 
# #     background:#160404; 
# #     min-height:100vh; 
# #     display:flex; 
# #     flex-direction:column; 
# #     border-left:1px solid #331010; 
# #     border-right:1px solid #331010; 
# #     position:relative; 
# #     transition: all 0.3s ease;
# # }

# # /* Desktop Responsive Layout */
# # @media (min-width: 900px) {
# #     body { background: #080202; align-items: center; padding: 20px 0; }
# #     .app-wrapper { max-width: 1150px; border: 1px solid #4a1515; border-radius: 16px; overflow: hidden; box-shadow: 0 15px 40px rgba(0,0,0,0.9); min-height: 850px; display: grid; grid-template-columns: 280px 1fr 340px; grid-template-rows: auto auto 1fr; }
    
# #     .top-header { grid-column: 1 / -1; }
# #     .aviator-subbar { grid-column: 1 / -1; }
# #     .history-bar { grid-column: 1 / -1; }
    
# #     .menu-drawer { position: relative !important; left: 0 !important; width: 100% !important; height: 100% !important; box-shadow: none !important; border-right: 1px solid #3a1010 !important; grid-row: 4 / 6; display: flex !important; }
# #     .menu-header button { display: none !important; }
    
# #     .center-stage { grid-column: 2; grid-row: 4; display: flex; flex-direction: column; }
# #     .aviator-screen { height: 360px !important; }
# #     .betting-container { flex-direction: row !important; gap: 12px; }
# #     .bet-card { flex: 1; }

# #     .live-feed-section { grid-column: 3; grid-row: 4; max-height: 100% !important; border-left: 1px solid #3a1010; border-top: none !important; }
# #     .desktop-hide { display: none !important; }
# # }

# # @media (max-width: 899px) {
# #     .desktop-only-sidebar { display: none; }
# #     .desktop-only-sidebar.open { display: flex; }
# #     .center-stage { display: flex; flex-direction: column; width: 100%; }
# # }

# # /* Top Header Bar */
# # .top-header { display:flex; justify-content:space-between; align-items:center; background:#1c0707; padding:12px 16px; border-bottom:1px solid #3a1010; }
# # .top-left { display:flex; align-items:center; gap:12px; }
# # .menu-btn { background:none; border:none; color:#fff; font-size:22px; cursor:pointer; }
# # .odi-logo { text-align:center; line-height:1; }
# # .odi-txt { font-size:10px; font-weight:bold; color:#fff; letter-spacing:1px; }
# # .casino-txt { font-size:14px; font-weight:900; color:#ef4444; letter-spacing:1.5px; font-style:italic; }

# # .deposit-btn { background:#facc15; color:#1a1a1a; border:none; padding:8px 18px; border-radius:8px; font-weight:900; font-size:14px; cursor:pointer; }
# # .chat-btn { background:#240c0c; border:1px solid #451515; color:#fff; padding:8px 12px; border-radius:8px; cursor:pointer; font-size:14px; }

# # /* Sub Header Aviator bar */
# # .aviator-subbar { display:flex; justify-content:space-between; align-items:center; padding:10px 16px; background:#1a0707; border-bottom:1px solid #3a1010; font-size:13px; }
# # .subbar-left { display:flex; align-items:center; gap:8px; }
# # .aviator-logo-txt { font-size:16px; font-weight:900; color:#ef4444; font-style:italic; }
# # .balance-display { color:#facc15; font-weight:bold; font-size:15px; }

# # /* History Bar */
# # .history-bar { display:flex; gap:6px; background:#1c0707; padding:8px 14px; overflow-x:auto; border-bottom:1px solid #3a1010; }
# # .pill-green { padding:3px 10px; border-radius:12px; font-size:12px; font-weight:bold; background:rgba(34,197,94,0.2); color:#22c55e; border:1px solid #22c55e; white-space:nowrap; }
# # .pill-red { padding:3px 10px; border-radius:12px; font-size:12px; font-weight:bold; background:rgba(239,68,68,0.2); color:#ef4444; border:1px solid #ef4444; white-space:nowrap; }

# # /* Game Screen */
# # .aviator-screen { position:relative; height:250px; background:radial-gradient(circle at center, #691515 0%, #2b0606 65%, #160202 100%); border-bottom:2px solid #5a1515; display:flex; flex-direction:column; justify-content:center; align-items:center; overflow:hidden; }
# # .multiplier-display { font-size:56px; font-weight:900; color:#fff; text-shadow:0 0 25px rgba(239,68,68,0.8); z-index:10; text-align:center; }
# # .status-msg { font-size:14px; color:#eab308; font-weight:bold; z-index:10; margin-top:4px; }

# # svg.flight-path { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 2; pointer-events: none; }
# # .plane-icon { position: absolute; font-size: 38px; z-index: 5; pointer-events: none; transform: translate(-30%, -70%) rotate(-12deg); filter: drop-shadow(0 0 10px rgba(239,68,68,0.9)); display: none; }

# # /* Side Menu Drawer */
# # .menu-drawer { position: absolute; top: 0; left: -280px; width: 280px; height: 100%; background: #1c0707; z-index: 100; transition: left 0.3s ease; border-right: 2px solid #5a1515; box-shadow: 5px 0 25px rgba(0,0,0,0.8); display: flex; flex-direction: column; }
# # .menu-drawer.open { left: 0; }
# # .menu-header { background: #2c0c0c; padding: 18px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #5a1515; }
# # .menu-items { padding: 10px 0; flex: 1; }
# # .menu-item { padding: 15px 20px; font-size: 15px; font-weight: bold; color: #d1d5db; cursor: pointer; border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; align-items: center; gap: 12px; }
# # .menu-item:hover { background: #3a1010; color: #facc15; }

# # /* Live Feed Section (800+ Users) */
# # .live-feed-section { background:#1c0707; border-top:1px solid #3a1010; padding:12px; max-height:260px; overflow-y:auto; }
# # .feed-header { font-size:12px; font-weight:bold; color:#eab308; margin-bottom:8px; display:flex; justify-content:space-between; }
# # .feed-item { display:flex; justify-content:space-between; align-items:center; padding:6px 10px; border-bottom:1px solid rgba(255,255,255,0.03); font-size:12px; }
# # .feed-item.self { background:rgba(234, 179, 8, 0.15); border-left:3px solid #eab308; }

# # /* Betting Panels Container */
# # .betting-container { padding:12px; display:flex; flex-direction:column; gap:12px; background:#160404; flex:1; }

# # .bet-card { background:#1c0707; border:1px solid #3a1010; border-radius:12px; padding:14px; }
# # .bet-tabs { display:flex; background:#120303; border-radius:8px; padding:3px; margin-bottom:10px; }
# # .bet-tab { flex:1; text-align:center; padding:6px; font-size:12px; font-weight:bold; color:#888; border-radius:6px; cursor:pointer; }
# # .bet-tab.active { background:#2c0c0c; color:#fff; }

# # .auto-box { display:none; margin-bottom:10px; font-size:12px; color:#9ca3af; }
# # .auto-box.active { display:block; }

# # .amount-row { display:flex; align-items:center; justify-content:space-between; margin-bottom:10px; }
# # .amt-btn { background:#2c0c0c; border:1px solid #4a1515; color:#fff; width:38px; height:38px; border-radius:50%; font-size:18px; font-weight:bold; cursor:pointer; display:flex; align-items:center; justify-content:center; }
# # .amt-value { font-size:20px; font-weight:900; color:#fff; letter-spacing:1px; }

# # .quick-stakes { display:grid; grid-template-columns:repeat(4, 1fr); gap:6px; margin-bottom:12px; }
# # .quick-btn { background:#240808; border:1px solid #4a1515; color:#d1d5db; padding:6px; border-radius:6px; font-size:12px; font-weight:bold; cursor:pointer; text-align:center; }
# # .quick-btn:hover { background:#3a1010; color:#fff; }

# # .action-btn { width:100%; padding:14px; border:none; border-radius:10px; background:#22c55e; color:white; font-weight:900; font-size:15px; cursor:pointer; text-transform:uppercase; box-shadow:0 4px 12px rgba(34,197,94,0.3); display:flex; flex-direction:column; align-items:center; justify-content:center; line-height:1.2; }
# # .action-btn.cashout { background:#dc2626; box-shadow:0 4px 12px rgba(220,38,38,0.3); }
# # .action-btn:disabled { opacity:0.4; cursor:not-allowed; box-shadow:none; }

# # .admin-banner { background:#7f1d1d; border:1px solid #ef4444; padding:8px 12px; border-radius:8px; display:flex; justify-content:space-between; align-items:center; font-weight:bold; color:#fca5a5; font-size:12px; margin:10px; }
# # .admin-val { color:#fff; font-size:15px; }

# # /* Modal overlay */
# # .modal-overlay { position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); z-index:200; display:none; justify-content:center; align-items:center; padding:20px; }
# # .modal-content { background:#240808; border:1px solid #5a1515; padding:24px; border-radius:12px; width:100%; max-width:380px; box-sizing:border-box; }
# # .modal-content h3 { color:#eab308; margin-top:0; }
# # .modal-content input { width:100%; padding:12px; margin:10px 0; background:#160404; border:1px solid #5a1515; color:#fff; border-radius:6px; box-sizing:border-box; font-size:15px; }
# # .modal-btns { display:flex; gap:10px; margin-top:10px; }
# # .modal-btns button { flex:1; padding:12px; border:none; border-radius:6px; font-weight:bold; cursor:pointer; font-size:15px; }
# # </style>
# # </head>
# # <body>

# # <div class="app-wrapper">
# #     <!-- Side Menu Drawer -->
# #     <div class="menu-drawer desktop-only-sidebar" id="menuDrawer">
# #         <div class="menu-header">
# #             <span style="font-weight:bold; color:#eab308; font-size:16px;">Odi Menu</span>
# #             <button class="desktop-hide" onclick="toggleMenu()" style="background:none; border:none; color:#fff; font-size:18px; cursor:pointer;">✕</button>
# #         </div>
# #         <div class="menu-items">
# #             <div class="menu-item" onclick="openDepositModal()">💳 Deposit (Min. KSh 200)</div>
# #             <div class="menu-item" onclick="openWithdrawModal()">💸 Withdraw (Min. KSh 1,000)</div>
# #             <div class="menu-item" onclick="showProfile()">👤 My Profile</div>
# #             <div class="menu-item" onclick="showHowToPlay()">📖 How to Play</div>
# #             <div class="menu-item" onclick="window.location.href='/logout'" style="color:#ef4444;">🚪 Logout</div>
# #         </div>
# #     </div>

# #     <!-- Top Header -->
# #     <div class="top-header">
# #         <div class="top-left">
# #             <button class="menu-btn desktop-hide" onclick="toggleMenu()">☰</button>
# #             <div class="odi-logo">
# #                 <div class="odi-txt">odi</div>
# #                 <div class="casino-txt">CASINO</div>
# #             </div>
# #         </div>
# #         <div style="display:flex; gap:10px; align-items:center;">
# #             <button class="deposit-btn" onclick="openDepositModal()">Deposit</button>
# #             <button class="chat-btn" id="soundToggle" onclick="toggleSound()">🔊</button>
# #         </div>
# #     </div>

# #     <!-- Center Stage -->
# #     <div class="center-stage">
# #         <!-- Aviator Bar -->
# #         <div class="aviator-subbar">
# #             <div class="subbar-left">
# #                 <span class="aviator-logo-txt">Aviator</span>
# #             </div>
# #             <div>
# #                 <span class="balance-display" id="lblBalance">0.00 KES</span>
# #             </div>
# #         </div>

# #         <!-- History Bar -->
# #         <div class="history-bar" id="historyBar"></div>

# #         <!-- Admin Panel -->
# #         <div id="adminPanel" class="admin-banner" style="display:none;">
# #             <span>ADMIN PREVIEW:</span>
# #             <span class="admin-val" id="lblNextCrash">--</span>
# #         </div>

# #         <!-- Game Screen -->
# #         <div class="aviator-screen" id="aviatorScreen">
# #             <svg class="flight-path" id="flightSvg" viewBox="0 0 400 250" preserveAspectRatio="none">
# #                 <path id="areaPath" d="M 0 250 L 0 250 L 400 250 Z" fill="rgba(239, 68, 68, 0.2)" />
# #                 <path id="curvePath" d="M 0 250 L 0 250" fill="none" stroke="#ef4444" stroke-width="5" stroke-linecap="round" />
# #             </svg>
# #             <div class="plane-icon" id="planeIcon">✈️</div>
            
# #             <div class="multiplier-display" id="lblMultiplier">1.00x</div>
# #             <div class="status-msg" id="lblStatusMsg">Waiting for next round...</div>
# #         </div>

# #         <!-- Betting Controls -->
# #         <div class="betting-container">
# #             <!-- Bet 1 -->
# #             <div class="bet-card">
# #                 <div class="bet-tabs">
# #                     <div class="bet-tab active" id="tab1_bet" onclick="switchTab(1, 'bet')">Bet</div>
# #                     <div class="bet-tab" id="tab1_auto" onclick="switchTab(1, 'auto')">Auto</div>
# #                 </div>
# #                 <div class="auto-box" id="autoBox1">
# #                     <label>Auto Cashout Multiplier</label>
# #                     <input type="number" id="autoCashout1" step="0.1" value="2.00" min="1.01" style="width:100%; padding:8px; margin-top:4px; background:#160404; border:1px solid #5a1515; color:#fff; border-radius:4px;">
# #                 </div>
# #                 <div class="amount-row">
# #                     <button class="amt-btn" onclick="adjustAmount(1, -50)">-</button>
# #                     <div class="amt-value"><input type="number" id="betAmount1" value="200.00" step="50" style="background:transparent; border:none; color:#fff; font-size:20px; font-weight:900; width:110px; text-align:center;"></div>
# #                     <button class="amt-btn" onclick="adjustAmount(1, 50)">+</button>
# #                 </div>
# #                 <div class="quick-stakes">
# #                     <div class="quick-btn" onclick="setAmount(1, 200)">200</div>
# #                     <div class="quick-btn" onclick="setAmount(1, 500)">500</div>
# #                     <div class="quick-btn" onclick="setAmount(1, 1000)">1,000</div>
# #                     <div class="quick-btn" onclick="setAmount(1, 5000)">5,000</div>
# #                 </div>
# #                 <button class="action-btn" id="btnAction1" onclick="handleBet(1)">Bet 200.00 KES</button>
# #             </div>

# #             <!-- Bet 2 -->
# #             <div class="bet-card">
# #                 <div class="bet-tabs">
# #                     <div class="bet-tab active" id="tab2_bet" onclick="switchTab(2, 'bet')">Bet</div>
# #                     <div class="bet-tab" id="tab2_auto" onclick="switchTab(2, 'auto')">Auto</div>
# #                 </div>
# #                 <div class="auto-box" id="autoBox2">
# #                     <label>Auto Cashout Multiplier</label>
# #                     <input type="number" id="autoCashout2" step="0.1" value="5.00" min="1.01" style="width:100%; padding:8px; margin-top:4px; background:#160404; border:1px solid #5a1515; color:#fff; border-radius:4px;">
# #                 </div>
# #                 <div class="amount-row">
# #                     <button class="amt-btn" onclick="adjustAmount(2, -50)">-</button>
# #                     <div class="amt-value"><input type="number" id="betAmount2" value="200.00" step="50" style="background:transparent; border:none; color:#fff; font-size:20px; font-weight:900; width:110px; text-align:center;"></div>
# #                     <button class="amt-btn" onclick="adjustAmount(2, 50)">+</button>
# #                 </div>
# #                 <div class="quick-stakes">
# #                     <div class="quick-btn" onclick="setAmount(2, 200)">200</div>
# #                     <div class="quick-btn" onclick="setAmount(2, 500)">500</div>
# #                     <div class="quick-btn" onclick="setAmount(2, 1000)">1,000</div>
# #                     <div class="quick-btn" onclick="setAmount(2, 5000)">5,000</div>
# #                 </div>
# #                 <button class="action-btn" id="btnAction2" onclick="handleBet(2)">Bet 200.00 KES</button>
# #             </div>
# #         </div>
# #     </div>

# #     <!-- Live Active Users Feed (800+ Users with User at Top) -->
# #     <div class="live-feed-section">
# #         <div class="feed-header">
# #             <span>LIVE ACTIVE USERS (~820)</span>
# #             <span id="activeBetsCount">Bets: 0</span>
# #         </div>
# #         <div id="liveFeedList"></div>
# #     </div>
# # </div>

# # <!-- Modal Dialog for Deposit (Prompt Link) & Withdraw -->
# # <div class="modal-overlay" id="walletModal">
# #     <div class="modal-content">
# #         <h3 id="modalTitle">Deposit Funds</h3>
# #         <p id="modalDesc" style="font-size:13px; color:#aaa;">Paste your M-Pesa payment prompt link or phone number:</p>
# #         <input type="text" id="modalInputLink" placeholder="https://pay.mpesa.co.ke/... or 2547XXXXXXXX">
# #         <label style="font-size:12px; color:#aaa;" id="amountLabel">Amount (Min. KSh 200):</label>
# #         <input type="number" id="modalInputAmount" value="500" min="200">
# #         <div class="modal-btns">
# #             <button onclick="closeModal()" style="background:#444; color:#fff;">Cancel</button>
# #             <button onclick="submitModalAction()" style="background:#22c55e; color:#fff;">Proceed</button>
# #         </div>
# #     </div>
# # </div>

# # <script>
# # let gameState = "BETTING";
# # let userBets = {};
# # let soundEnabled = true;
# # let audioCtx = null;
# # let modalType = 'deposit';
# # let autoModes = {1: false, 2: false};
# # let currentGlobalMultiplier = 1.00;

# # function initAudio() {
# #     if(!audioCtx) {
# #         audioCtx = new (window.AudioContext || window.webkitAudioContext)();
# #     }
# # }

# # function playOdibetTakeoffSound() {
# #     if(!soundEnabled) return;
# #     try {
# #         initAudio();
# #         let now = audioCtx.currentTime;
# #         let osc = audioCtx.createOscillator();
# #         let gain = audioCtx.createGain();
# #         osc.type = "sawtooth";
# #         osc.frequency.setValueAtTime(80, now);
# #         osc.frequency.exponentialRampToValueAtTime(750, now + 1.2);
        
# #         gain.gain.setValueAtTime(0.12, now);
# #         gain.gain.linearRampToValueAtTime(0.001, now + 1.2);
        
# #         osc.connect(gain);
# #         gain.connect(audioCtx.destination);
# #         osc.start(now);
# #         osc.stop(now + 1.2);
# #     } catch(e) {}
# # }

# # function playOdibetCashoutSound() {
# #     if(!soundEnabled) return;
# #     try {
# #         initAudio();
# #         let now = audioCtx.currentTime;
# #         let osc = audioCtx.createOscillator();
# #         let gain = audioCtx.createGain();
# #         osc.type = "sine";
# #         osc.frequency.setValueAtTime(523.25, now);
# #         osc.frequency.setValueAtTime(783.99, now + 0.1);
# #         osc.frequency.setValueAtTime(1046.50, now + 0.2);
        
# #         gain.gain.setValueAtTime(0.2, now);
# #         gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.35);
        
# #         osc.connect(gain);
# #         gain.connect(audioCtx.destination);
# #         osc.start(now);
# #         osc.stop(now + 0.35);
# #     } catch(e) {}
# # }

# # function playOdibetCrashSound() {
# #     if(!soundEnabled) return;
# #     try {
# #         initAudio();
# #         let now = audioCtx.currentTime;
# #         let osc = audioCtx.createOscillator();
# #         let gain = audioCtx.createGain();
# #         osc.type = "sawtooth";
# #         osc.frequency.setValueAtTime(200, now);
# #         osc.frequency.linearRampToValueAtTime(35, now + 0.55);
        
# #         gain.gain.setValueAtTime(0.3, now);
# #         gain.gain.linearRampToValueAtTime(0.0001, now + 0.55);
        
# #         osc.connect(gain);
# #         gain.connect(audioCtx.destination);
# #         osc.start(now);
# #         osc.stop(now + 0.55);
# #     } catch(e) {}
# # }

# # function toggleSound() {
# #     soundEnabled = !soundEnabled;
# #     let btn = document.getElementById("soundToggle");
# #     btn.innerText = soundEnabled ? "🔊" : "🔇";
# # }

# # function toggleMenu() {
# #     let drawer = document.getElementById("menuDrawer");
# #     if(window.innerWidth < 900) {
# #         drawer.classList.toggle("open");
# #     }
# # }

# # function showProfile() {
# #     alert("Logged in user account is active.\nMinimum Deposit: KSh 200\nMinimum Withdrawal: KSh 1,000");
# #     if(window.innerWidth < 900) toggleMenu();
# # }

# # function showHowToPlay() {
# #     alert("Aviator Rules:\n1. Place your bet before the round starts.\n2. Watch the plane fly and the multiplier increase.\n3. Cash out before the plane flies away to win your stake multiplied by the current multiplier!");
# #     if(window.innerWidth < 900) toggleMenu();
# # }

# # function switchTab(slot, mode) {
# #     let tabBet = document.getElementById(`tab${slot}_bet`);
# #     let tabAuto = document.getElementById(`tab${slot}_auto`);
# #     let autoBox = document.getElementById(`autoBox${slot}`);
    
# #     if(mode === 'bet') {
# #         tabBet.classList.add("active");
# #         tabAuto.classList.remove("active");
# #         autoBox.classList.remove("active");
# #         autoModes[slot] = false;
# #     } else {
# #         tabAuto.classList.add("active");
# #         tabBet.classList.remove("active");
# #         autoBox.classList.add("active");
# #         autoModes[slot] = true;
# #     }
# # }

# # function setAmount(slot, val) {
# #     document.getElementById("betAmount" + slot).value = val.toFixed(2);
# #     updateButtons();
# # }

# # function adjustAmount(slot, delta) {
# #     let inp = document.getElementById("betAmount" + slot);
# #     let cur = parseFloat(inp.value) || 0;
# #     let nxt = Math.max(50, cur + delta);
# #     inp.value = nxt.toFixed(2);
# #     updateButtons();
# # }

# # function openDepositModal() {
# #     modalType = 'deposit';
# #     document.getElementById("modalTitle").innerText = "Deposit Funds (Min. KSh 200)";
# #     document.getElementById("modalDesc").innerText = "Paste your M-Pesa payment prompt link or phone number:";
# #     document.getElementById("amountLabel").innerText = "Deposit Amount (KES):";
# #     document.getElementById("modalInputAmount").value = "500";
# #     document.getElementById("modalInputLink").value = "";
# #     document.getElementById("walletModal").style.display = "flex";
# #     if(window.innerWidth < 900) {
# #         document.getElementById("menuDrawer").classList.remove("open");
# #     }
# # }

# # function openWithdrawModal() {
# #     modalType = 'withdraw';
# #     document.getElementById("modalTitle").innerText = "Withdraw Funds (Min. KSh 1,000)";
# #     document.getElementById("modalDesc").innerText = "Enter your M-Pesa phone number for payout:";
# #     document.getElementById("amountLabel").innerText = "Withdrawal Amount (KES):";
# #     document.getElementById("modalInputAmount").value = "1000";
# #     document.getElementById("modalInputLink").value = "";
# #     document.getElementById("walletModal").style.display = "flex";
# #     if(window.innerWidth < 900) {
# #         document.getElementById("menuDrawer").classList.remove("open");
# #     }
# # }

# # function closeModal() {
# #     document.getElementById("walletModal").style.display = "none";
# # }

# # async function submitModalAction() {
# #     let amount = parseFloat(document.getElementById("modalInputAmount").value) || 0;
# #     let linkOrPhone = document.getElementById("modalInputLink").value.trim();
    
# #     if(modalType === 'deposit') {
# #         if(amount < 200) { alert("Minimum deposit is KSh 200."); return; }
# #         if(!linkOrPhone) { alert("Please paste your M-Pesa prompt link or enter your phone number."); return; }
        
# #         let res = await fetch('/api/confirm-deposit', {
# #             method: 'POST',
# #             headers: {'Content-Type': 'application/json'},
# #             body: JSON.stringify({amount: amount, link: linkOrPhone})
# #         });
# #         let d = await res.json();
# #         alert(d.message);
# #         if(d.success) closeModal();
# #         fetchState();
# #     } else {
# #         if(amount < 1000) { alert("Minimum withdrawal is KSh 1,000."); return; }
# #         if(!linkOrPhone) { alert("Please enter your M-Pesa phone number."); return; }
        
# #         let res = await fetch('/api/withdraw', {
# #             method: 'POST',
# #             headers: {'Content-Type': 'application/json'},
# #             body: JSON.stringify({amount: amount, phone: linkOrPhone})
# #         });
# #         let d = await res.json();
# #         alert(d.message);
# #         if(d.success) closeModal();
# #         fetchState();
# #     }
# # }

# # async function fetchState() {
# #     try {
# #         let res = await fetch('/api/state');
# #         if(res.status === 401) { window.location.href = '/login'; return; }
# #         let data = await res.json();
        
# #         let oldState = gameState;
# #         gameState = data.status;
# #         currentGlobalMultiplier = data.multiplier;
        
# #         document.getElementById("lblBalance").innerText = data.balance.toLocaleString(undefined, {minimumFractionDigits:2}) + " KES";
        
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
# #         document.getElementById("activeBetsCount").innerText = `Total: ${feed.length}`;
        
# #         feed.forEach(bet => {
# #             let statusBadge = "";
# #             let rowClass = bet.is_self ? "feed-item self" : "feed-item";
            
# #             if(bet.status === "ACTIVE") {
# #                 statusBadge = `<span style="color:#eab308;">In Game</span>`;
# #             } else if(bet.status === "WON") {
# #                 statusBadge = `<span style="color:#22c55e; font-weight:bold;">${bet.cashout_multiplier.toFixed(2)}x (+${bet.winnings.toLocaleString()})</span>`;
# #             } else {
# #                 statusBadge = `<span style="color:#ef4444;">Crashed</span>`;
# #             }
# #             feedHtml += `<div class="${rowClass}"><span><b>${bet.username}</b> (KSh ${bet.amount.toLocaleString()})</span>${statusBadge}</div>`;
# #         });
# #         document.getElementById("liveFeedList").innerHTML = feedHtml;

# #         let planeEl = document.getElementById("planeIcon");
# #         let curvePath = document.getElementById("curvePath");
# #         let areaPath = document.getElementById("areaPath");

# #         if(gameState === "RUNNING") {
# #             if(oldState !== "RUNNING") {
# #                 playOdibetTakeoffSound();
# #             }

# #             document.getElementById("lblMultiplier").innerText = data.multiplier.toFixed(2) + "x";
# #             document.getElementById("lblStatusMsg").innerText = "Fly away high!";
# #             document.getElementById("lblMultiplier").style.color = "#fff";
            
# #             planeEl.style.display = "block";
            
# #             let progress = Math.min((data.multiplier - 1.0) / 5.0, 1.0);
# #             let svgW = 400, svgH = 250;
# #             let targetX = 30 + (progress * 340);
# #             let targetY = 240 - (progress * 200);
            
# #             let pathString = `M 0 250 Q ${targetX * 0.5} ${250 - (targetY * 0.1)}, ${targetX} ${targetY}`;
# #             curvePath.setAttribute("d", pathString);
# #             areaPath.setAttribute("d", `${pathString} L ${targetX} 250 L 0 250 Z`);
            
# #             let screenBox = document.getElementById("aviatorScreen").getBoundingClientRect();
# #             let planeLeft = (targetX / svgW) * screenBox.width;
# #             let planeTop = (targetY / svgH) * screenBox.height;
            
# #             planeEl.style.left = planeLeft + "px";
# #             planeEl.style.top = planeTop + "px";
# #             planeEl.style.transform = `translate(-30%, -70%) rotate(${-12 - (progress * 22)}deg)`;

# #         } else if(gameState === "CRASHED") {
# #             if(oldState === "RUNNING") {
# #                 playOdibetCrashSound();
# #             }
# #             document.getElementById("lblMultiplier").innerText = "FLEW AWAY!";
# #             document.getElementById("lblStatusMsg").innerText = `Crashed at ${data.crash_point.toFixed(2)}x`;
# #             document.getElementById("lblMultiplier").style.color = "#ef4444";
            
# #             setTimeout(() => { planeEl.style.display = "none"; }, 1200);

# #         } else {
# #             document.getElementById("lblMultiplier").innerText = "1.00x";
# #             document.getElementById("lblStatusMsg").innerText = "Place your bets!";
# #             document.getElementById("lblMultiplier").style.color = "#22c55e";
# #             curvePath.setAttribute("d", "M 0 250 L 0 250");
# #             areaPath.setAttribute("d", "M 0 250 L 0 250 L 400 250 Z");
# #             planeEl.style.display = "none";
# #         }

# #         userBets = data.bets || {};
# #         updateButtons();
# #     } catch(e) { console.error(e); }
# # }

# # function updateButtons() {
# #     for(let i=1; i<=2; i++) {
# #         let btn = document.getElementById("btnAction" + i);
# #         let bet = userBets[i];
# #         let amt = parseFloat(document.getElementById("betAmount" + i).value) || 0;
        
# #         if(bet && bet.status === "ACTIVE") {
# #             if(gameState === "RUNNING") {
# #                 let liveWinnings = (amt * currentGlobalMultiplier).toFixed(2);
# #                 btn.innerHTML = `CASHOUT<span style="font-size:12px; font-weight:normal; color:#fed7aa;">KES ${Number(liveWinnings).toLocaleString()}</span>`;
# #                 btn.className = "action-btn cashout";
# #                 btn.disabled = false;
# #             } else {
# #                 btn.innerText = "WAITING...";
# #                 btn.className = "action-btn";
# #                 btn.disabled = true;
# #             }
# #         } else {
# #             if(gameState === "BETTING") {
# #                 btn.innerText = `Bet ${amt.toFixed(2)} KES`;
# #                 btn.className = "action-btn";
# #                 btn.disabled = false;
# #             } else {
# #                 btn.innerText = "BETTING CLOSED";
# #                 btn.className = "action-btn";
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
# #         if(d.success) playOdibetCashoutSound();
# #         alert(d.message);
# #     } else {
# #         let amt = document.getElementById("betAmount" + betNum).value;
# #         let autoVal = autoModes[betNum] ? document.getElementById("autoCashout" + betNum).value : null;
        
# #         let res = await fetch('/api/bet', {
# #             method: 'POST',
# #             headers: {'Content-Type': 'application/json'},
# #             body: JSON.stringify({bet_number: betNum, amount: amt, auto_cashout: autoVal})
# #         });
# #         let d = await res.json();
# #         if(d.success) playOdibetTakeoffSound();
# #         alert(d.message);
# #     }
# #     fetchState();
# # }

# # setInterval(fetchState, 75);
# # </script>
# # </body>
# # </html>

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
# # CONFIGURATION & RULES
# # ============================================================

# DB_NAME = "aviator_live.db"

# BETTING_WINDOW = 5.0
# MAX_BETS = 2
# MIN_DEPOSIT = 200.0
# MIN_WITHDRAWAL = 1000.0
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
# # GAME ENGINE & ODIBET ACCELERATION CURVE
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
#     multiplier = 1.0 + (elapsed * 0.45) + ((elapsed ** 1.65) * 0.12)
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

# FIRST_NAMES = [
#     "alex", "brian", "coll", "david", "eric", "frank", "grace", "harr", "ian", "john",
#     "kevin", "lucy", "mike", "nick", "oliver", "peter", "queen", "ray", "sam", "tom",
#     "victor", "wendy", "xav", "yves", "zack", "kelv", "sylv", "mash", "kip", "wanj",
#     "njeri", "ochi", "otien", "maina", "chep", "kiprot", "kibet", "kipko", "cherot",
#     "jelag", "baras", "mutiso", "odhi", "korir", "kipng", "chepk", "kipke", "kipch"
# ]

# def generate_bot_bets():
#     bets = []
#     count = random.randint(780, 840)
#     for i in range(count):
#         prefix = random.choice(FIRST_NAMES)
#         masked = prefix[:3] + "***" + str(random.randint(0, 9))
#         amount = round(random.choice([50, 100, 200, 500, 1000, 2500, 5000, 10000]), 2)
#         target_cashout = round(random.uniform(1.10, 15.00), 2) if random.random() > 0.12 else None
        
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


# def process_auto_cashouts_and_bets_locked():
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
#             if random.random() < 0.05:
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
#         process_auto_cashouts_and_bets_locked()

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


# def mask_username(username):
#     if len(username) <= 3:
#         return username + "***"
#     return username[:3] + "***" + str(len(username))


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
#             return False, "Betting closed for this round. Wait for next round."

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
#                 return False, f"Bet {bet_number} already placed for this round."

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
#             return True, f"Bet {bet_number} placed successfully!"
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
#                 error = "Phone number not found in records."
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
#         masked_self = mask_username(username)

#         conn = get_db()
#         history_rows = conn.execute("SELECT crash_point FROM rounds WHERE ended_at IS NOT NULL ORDER BY id DESC LIMIT 25").fetchall()
#         history = [float(r["crash_point"]) for r in history_rows][::-1]

#         bet_rows = conn.execute("SELECT bet_number, amount, auto_cashout, cashout_multiplier, winnings, status FROM bets WHERE username = ? AND round_id = ?", (username, GAME["round_id"])).fetchall()
#         conn.close()

#         user_bets = {}
#         all_live_bets = []

#         for r in bet_rows:
#             user_bets[str(r["bet_number"])] = dict(r)
#             all_live_bets.append({
#                 "id": f"real_{r['bet_number']}",
#                 "username": masked_self + " (You)",
#                 "amount": r["amount"],
#                 "auto_cashout": r["auto_cashout"],
#                 "status": r["status"],
#                 "cashout_multiplier": r["cashout_multiplier"],
#                 "winnings": r["winnings"],
#                 "is_self": True
#             })

#         for b in GAME["bot_bets"]:
#             all_live_bets.append(b)

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
#     success, msg = place_bet_for_user(
#         session["username"],
#         int(data.get("bet_number", 1)),
#         data.get("amount", 0),
#         data.get("auto_cashout")
#     )
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
    
#     if amount < MIN_DEPOSIT:
#         return jsonify({"success": False, "message": f"Minimum deposit amount is KSh {MIN_DEPOSIT:,.2f}."})
    
#     add_balance(session["username"], amount)
#     return jsonify({"success": True, "message": f"Successfully deposited KSh {amount:,.2f} via M-Pesa prompt link!"})


# @app.route("/api/withdraw", methods=["POST"])
# def api_withdraw():
#     if "username" not in session:
#         return jsonify({"success": False, "message": "Unauthorized"}), 401
#     data = request.get_json() or {}
#     try:
#         amount = float(data.get("amount", 0))
#     except ValueError:
#         return jsonify({"success": False, "message": "Invalid amount."})
    
#     if amount < MIN_WITHDRAWAL:
#         return jsonify({"success": False, "message": f"Minimum withdrawal amount is KSh {MIN_WITHDRAWAL:,.2f}."})
    
#     username = session["username"]
#     user = get_user(username)
#     if user["balance"] < amount:
#         return jsonify({"success": False, "message": "Insufficient balance for this withdrawal."})
    
#     if deduct_balance(username, amount):
#         return jsonify({"success": True, "message": f"Withdrawal request of KSh {amount:,.2f} sent to {user['phone_number']}. Processing via M-Pesa..."})
#     return jsonify({"success": False, "message": "Withdrawal failed."})


# # ============================================================
# # TEMPLATES (LIVE CASH-OUT WINNINGS PREVIEW ON BUTTON)
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
# <title>Odi Casino Aviator</title>
# <style>
# * { box-sizing:border-box; }
# body { margin:0; font-family:-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background:#0f0f0f; color:#fff; display:flex; justify-content:center; }

# .app-wrapper { 
#     width:100%; 
#     max-width:480px; 
#     background:#160404; 
#     min-height:100vh; 
#     display:flex; 
#     flex-direction:column; 
#     border-left:1px solid #331010; 
#     border-right:1px solid #331010; 
#     position:relative; 
#     transition: all 0.3s ease;
# }

# /* Desktop Responsive Layout */
# @media (min-width: 900px) {
#     body { background: #080202; align-items: center; padding: 20px 0; }
#     .app-wrapper { max-width: 1150px; border: 1px solid #4a1515; border-radius: 16px; overflow: hidden; box-shadow: 0 15px 40px rgba(0,0,0,0.9); min-height: 850px; display: grid; grid-template-columns: 280px 1fr 340px; grid-template-rows: auto auto 1fr; }
    
#     .top-header { grid-column: 1 / -1; }
#     .aviator-subbar { grid-column: 1 / -1; }
#     .history-bar { grid-column: 1 / -1; }
    
#     .menu-drawer { position: relative !important; left: 0 !important; width: 100% !important; height: 100% !important; box-shadow: none !important; border-right: 1px solid #3a1010 !important; grid-row: 4 / 6; display: flex !important; }
#     .menu-header button { display: none !important; }
    
#     .center-stage { grid-column: 2; grid-row: 4; display: flex; flex-direction: column; }
#     .aviator-screen { height: 360px !important; }
#     .betting-container { flex-direction: row !important; gap: 12px; }
#     .bet-card { flex: 1; }

#     .live-feed-section { grid-column: 3; grid-row: 4; max-height: 100% !important; border-left: 1px solid #3a1010; border-top: none !important; }
#     .desktop-hide { display: none !important; }
# }

# @media (max-width: 899px) {
#     .desktop-only-sidebar { display: none; }
#     .desktop-only-sidebar.open { display: flex; }
#     .center-stage { display: flex; flex-direction: column; width: 100%; }
# }

# /* Top Header Bar */
# .top-header { display:flex; justify-content:space-between; align-items:center; background:#1c0707; padding:12px 16px; border-bottom:1px solid #3a1010; }
# .top-left { display:flex; align-items:center; gap:12px; }
# .menu-btn { background:none; border:none; color:#fff; font-size:22px; cursor:pointer; }
# .odi-logo { text-align:center; line-height:1; }
# .odi-txt { font-size:10px; font-weight:bold; color:#fff; letter-spacing:1px; }
# .casino-txt { font-size:14px; font-weight:900; color:#ef4444; letter-spacing:1.5px; font-style:italic; }

# .deposit-btn { background:#facc15; color:#1a1a1a; border:none; padding:8px 18px; border-radius:8px; font-weight:900; font-size:14px; cursor:pointer; }
# .chat-btn { background:#240c0c; border:1px solid #451515; color:#fff; padding:8px 12px; border-radius:8px; cursor:pointer; font-size:14px; }

# /* Sub Header Aviator bar */
# .aviator-subbar { display:flex; justify-content:space-between; align-items:center; padding:10px 16px; background:#1a0707; border-bottom:1px solid #3a1010; font-size:13px; }
# .subbar-left { display:flex; align-items:center; gap:8px; }
# .aviator-logo-txt { font-size:16px; font-weight:900; color:#ef4444; font-style:italic; }
# .balance-display { color:#facc15; font-weight:bold; font-size:15px; }

# /* History Bar */
# .history-bar { display:flex; gap:6px; background:#1c0707; padding:8px 14px; overflow-x:auto; border-bottom:1px solid #3a1010; }
# .pill-green { padding:3px 10px; border-radius:12px; font-size:12px; font-weight:bold; background:rgba(34,197,94,0.2); color:#22c55e; border:1px solid #22c55e; white-space:nowrap; }
# .pill-red { padding:3px 10px; border-radius:12px; font-size:12px; font-weight:bold; background:rgba(239,68,68,0.2); color:#ef4444; border:1px solid #ef4444; white-space:nowrap; }

# /* Game Screen */
# .aviator-screen { position:relative; height:250px; background:radial-gradient(circle at center, #691515 0%, #2b0606 65%, #160202 100%); border-bottom:2px solid #5a1515; display:flex; flex-direction:column; justify-content:center; align-items:center; overflow:hidden; }
# .multiplier-display { font-size:56px; font-weight:900; color:#fff; text-shadow:0 0 25px rgba(239,68,68,0.8); z-index:10; text-align:center; }
# .status-msg { font-size:14px; color:#eab308; font-weight:bold; z-index:10; margin-top:4px; }

# svg.flight-path { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 2; pointer-events: none; }
# .plane-icon { position: absolute; font-size: 38px; z-index: 5; pointer-events: none; transform: translate(-30%, -70%) rotate(-12deg); filter: drop-shadow(0 0 10px rgba(239,68,68,0.9)); display: none; }

# /* Side Menu Drawer */
# .menu-drawer { position: absolute; top: 0; left: -280px; width: 280px; height: 100%; background: #1c0707; z-index: 100; transition: left 0.3s ease; border-right: 2px solid #5a1515; box-shadow: 5px 0 25px rgba(0,0,0,0.8); display: flex; flex-direction: column; }
# .menu-drawer.open { left: 0; }
# .menu-header { background: #2c0c0c; padding: 18px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #5a1515; }
# .menu-items { padding: 10px 0; flex: 1; }
# .menu-item { padding: 15px 20px; font-size: 15px; font-weight: bold; color: #d1d5db; cursor: pointer; border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; align-items: center; gap: 12px; }
# .menu-item:hover { background: #3a1010; color: #facc15; }

# /* Live Feed Section (800+ Users) */
# .live-feed-section { background:#1c0707; border-top:1px solid #3a1010; padding:12px; max-height:260px; overflow-y:auto; }
# .feed-header { font-size:12px; font-weight:bold; color:#eab308; margin-bottom:8px; display:flex; justify-content:space-between; }
# .feed-item { display:flex; justify-content:space-between; align-items:center; padding:6px 10px; border-bottom:1px solid rgba(255,255,255,0.03); font-size:12px; }
# .feed-item.self { background:rgba(234, 179, 8, 0.15); border-left:3px solid #eab308; }

# /* Betting Panels Container */
# .betting-container { padding:12px; display:flex; flex-direction:column; gap:12px; background:#160404; flex:1; }

# .bet-card { background:#1c0707; border:1px solid #3a1010; border-radius:12px; padding:14px; }
# .bet-tabs { display:flex; background:#120303; border-radius:8px; padding:3px; margin-bottom:10px; }
# .bet-tab { flex:1; text-align:center; padding:6px; font-size:12px; font-weight:bold; color:#888; border-radius:6px; cursor:pointer; }
# .bet-tab.active { background:#2c0c0c; color:#fff; }

# .auto-box { display:none; margin-bottom:10px; font-size:12px; color:#9ca3af; }
# .auto-box.active { display:block; }

# .amount-row { display:flex; align-items:center; justify-content:space-between; margin-bottom:10px; }
# .amt-btn { background:#2c0c0c; border:1px solid #4a1515; color:#fff; width:38px; height:38px; border-radius:50%; font-size:18px; font-weight:bold; cursor:pointer; display:flex; align-items:center; justify-content:center; }
# .amt-value { font-size:20px; font-weight:900; color:#fff; letter-spacing:1px; }

# .quick-stakes { display:grid; grid-template-columns:repeat(4, 1fr); gap:6px; margin-bottom:12px; }
# .quick-btn { background:#240808; border:1px solid #4a1515; color:#d1d5db; padding:6px; border-radius:6px; font-size:12px; font-weight:bold; cursor:pointer; text-align:center; }
# .quick-btn:hover { background:#3a1010; color:#fff; }

# .action-btn { width:100%; padding:14px; border:none; border-radius:10px; background:#22c55e; color:white; font-weight:900; font-size:15px; cursor:pointer; text-transform:uppercase; box-shadow:0 4px 12px rgba(34,197,94,0.3); display:flex; flex-direction:column; align-items:center; justify-content:center; line-height:1.2; }
# .action-btn.cashout { background:#dc2626; box-shadow:0 4px 12px rgba(220,38,38,0.3); }
# .action-btn:disabled { opacity:0.4; cursor:not-allowed; box-shadow:none; }

# .admin-banner { background:#7f1d1d; border:1px solid #ef4444; padding:8px 12px; border-radius:8px; display:flex; justify-content:space-between; align-items:center; font-weight:bold; color:#fca5a5; font-size:12px; margin:10px; }
# .admin-val { color:#fff; font-size:15px; }

# /* Modal overlay */
# .modal-overlay { position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); z-index:200; display:none; justify-content:center; align-items:center; padding:20px; }
# .modal-content { background:#240808; border:1px solid #5a1515; padding:24px; border-radius:12px; width:100%; max-width:380px; box-sizing:border-box; }
# .modal-content h3 { color:#eab308; margin-top:0; }
# .modal-content input { width:100%; padding:12px; margin:10px 0; background:#160404; border:1px solid #5a1515; color:#fff; border-radius:6px; box-sizing:border-box; font-size:15px; }
# .modal-btns { display:flex; gap:10px; margin-top:10px; }
# .modal-btns button { flex:1; padding:12px; border:none; border-radius:6px; font-weight:bold; cursor:pointer; font-size:15px; }
# </style>
# </head>
# <body>

# <div class="app-wrapper">
#     <!-- Side Menu Drawer -->
#     <div class="menu-drawer desktop-only-sidebar" id="menuDrawer">
#         <div class="menu-header">
#             <span style="font-weight:bold; color:#eab308; font-size:16px;">Odi Menu</span>
#             <button class="desktop-hide" onclick="toggleMenu()" style="background:none; border:none; color:#fff; font-size:18px; cursor:pointer;">✕</button>
#         </div>
#         <div class="menu-items">
#             <div class="menu-item" onclick="openDepositModal()">💳 Deposit (Min. KSh 200)</div>
#             <div class="menu-item" onclick="openWithdrawModal()">💸 Withdraw (Min. KSh 1,000)</div>
#             <div class="menu-item" onclick="showProfile()">👤 My Profile</div>
#             <div class="menu-item" onclick="showHowToPlay()">📖 How to Play</div>
#             <div class="menu-item" onclick="window.location.href='/logout'" style="color:#ef4444;">🚪 Logout</div>
#         </div>
#     </div>

#     <!-- Top Header -->
#     <div class="top-header">
#         <div class="top-left">
#             <button class="menu-btn desktop-hide" onclick="toggleMenu()">☰</button>
#             <div class="odi-logo">
#                 <div class="odi-txt">odi</div>
#                 <div class="casino-txt">CASINO</div>
#             </div>
#         </div>
#         <div style="display:flex; gap:10px; align-items:center;">
#             <button class="deposit-btn" onclick="openDepositModal()">Deposit</button>
#             <button class="chat-btn" id="soundToggle" onclick="toggleSound()">🔊</button>
#         </div>
#     </div>

#     <!-- Center Stage -->
#     <div class="center-stage">
#         <!-- Aviator Bar -->
#         <div class="aviator-subbar">
#             <div class="subbar-left">
#                 <span class="aviator-logo-txt">Aviator</span>
#             </div>
#             <div>
#                 <span class="balance-display" id="lblBalance">0.00 KES</span>
#             </div>
#         </div>

#         <!-- History Bar -->
#         <div class="history-bar" id="historyBar"></div>

#         <!-- Admin Panel -->
#         <div id="adminPanel" class="admin-banner" style="display:none;">
#             <span>ADMIN PREVIEW:</span>
#             <span class="admin-val" id="lblNextCrash">--</span>
#         </div>

#         <!-- Game Screen -->
#         <div class="aviator-screen" id="aviatorScreen">
#             <svg class="flight-path" id="flightSvg" viewBox="0 0 400 250" preserveAspectRatio="none">
#                 <path id="areaPath" d="M 0 250 L 0 250 L 400 250 Z" fill="rgba(239, 68, 68, 0.2)" />
#                 <path id="curvePath" d="M 0 250 L 0 250" fill="none" stroke="#ef4444" stroke-width="5" stroke-linecap="round" />
#             </svg>
#             <div class="plane-icon" id="planeIcon">✈️</div>
            
#             <div class="multiplier-display" id="lblMultiplier">1.00x</div>
#             <div class="status-msg" id="lblStatusMsg">Waiting for next round...</div>
#         </div>

#         <!-- Betting Controls -->
#         <div class="betting-container">
#             <!-- Bet 1 -->
#             <div class="bet-card">
#                 <div class="bet-tabs">
#                     <div class="bet-tab active" id="tab1_bet" onclick="switchTab(1, 'bet')">Bet</div>
#                     <div class="bet-tab" id="tab1_auto" onclick="switchTab(1, 'auto')">Auto</div>
#                 </div>
#                 <div class="auto-box" id="autoBox1">
#                     <label>Auto Cashout Multiplier</label>
#                     <input type="number" id="autoCashout1" step="0.1" value="2.00" min="1.01" style="width:100%; padding:8px; margin-top:4px; background:#160404; border:1px solid #5a1515; color:#fff; border-radius:4px;">
#                 </div>
#                 <div class="amount-row">
#                     <button class="amt-btn" onclick="adjustAmount(1, -50)">-</button>
#                     <div class="amt-value"><input type="number" id="betAmount1" value="200.00" step="50" style="background:transparent; border:none; color:#fff; font-size:20px; font-weight:900; width:110px; text-align:center;"></div>
#                     <button class="amt-btn" onclick="adjustAmount(1, 50)">+</button>
#                 </div>
#                 <div class="quick-stakes">
#                     <div class="quick-btn" onclick="setAmount(1, 200)">200</div>
#                     <div class="quick-btn" onclick="setAmount(1, 500)">500</div>
#                     <div class="quick-btn" onclick="setAmount(1, 1000)">1,000</div>
#                     <div class="quick-btn" onclick="setAmount(1, 5000)">5,000</div>
#                 </div>
#                 <button class="action-btn" id="btnAction1" onclick="handleBet(1)">Bet 200.00 KES</button>
#             </div>

#             <!-- Bet 2 -->
#             <div class="bet-card">
#                 <div class="bet-tabs">
#                     <div class="bet-tab active" id="tab2_bet" onclick="switchTab(2, 'bet')">Bet</div>
#                     <div class="bet-tab" id="tab2_auto" onclick="switchTab(2, 'auto')">Auto</div>
#                 </div>
#                 <div class="auto-box" id="autoBox2">
#                     <label>Auto Cashout Multiplier</label>
#                     <input type="number" id="autoCashout2" step="0.1" value="5.00" min="1.01" style="width:100%; padding:8px; margin-top:4px; background:#160404; border:1px solid #5a1515; color:#fff; border-radius:4px;">
#                 </div>
#                 <div class="amount-row">
#                     <button class="amt-btn" onclick="adjustAmount(2, -50)">-</button>
#                     <div class="amt-value"><input type="number" id="betAmount2" value="200.00" step="50" style="background:transparent; border:none; color:#fff; font-size:20px; font-weight:900; width:110px; text-align:center;"></div>
#                     <button class="amt-btn" onclick="adjustAmount(2, 50)">+</button>
#                 </div>
#                 <div class="quick-stakes">
#                     <div class="quick-btn" onclick="setAmount(2, 200)">200</div>
#                     <div class="quick-btn" onclick="setAmount(2, 500)">500</div>
#                     <div class="quick-btn" onclick="setAmount(2, 1000)">1,000</div>
#                     <div class="quick-btn" onclick="setAmount(2, 5000)">5,000</div>
#                 </div>
#                 <button class="action-btn" id="btnAction2" onclick="handleBet(2)">Bet 200.00 KES</button>
#             </div>
#         </div>
#     </div>

#     <!-- Live Active Users Feed (800+ Users with User at Top) -->
#     <div class="live-feed-section">
#         <div class="feed-header">
#             <span>LIVE ACTIVE USERS (~820)</span>
#             <span id="activeBetsCount">Bets: 0</span>
#         </div>
#         <div id="liveFeedList"></div>
#     </div>
# </div>

# <!-- Modal Dialog for Deposit (Prompt Link) & Withdraw -->
# <div class="modal-overlay" id="walletModal">
#     <div class="modal-content">
#         <h3 id="modalTitle">Deposit Funds</h3>
#         <p id="modalDesc" style="font-size:13px; color:#aaa;">Paste your M-Pesa payment prompt link or phone number:</p>
#         <input type="text" id="modalInputLink" placeholder="https://pay.mpesa.co.ke/... or 2547XXXXXXXX">
#         <label style="font-size:12px; color:#aaa;" id="amountLabel">Amount (Min. KSh 200):</label>
#         <input type="number" id="modalInputAmount" value="500" min="200">
#         <div class="modal-btns">
#             <button onclick="closeModal()" style="background:#444; color:#fff;">Cancel</button>
#             <button onclick="submitModalAction()" style="background:#22c55e; color:#fff;">Proceed</button>
#         </div>
#     </div>
# </div>

# <script>
# let gameState = "BETTING";
# let userBets = {};
# let soundEnabled = true;
# let audioCtx = null;
# let modalType = 'deposit';
# let autoModes = {1: false, 2: false};
# let currentGlobalMultiplier = 1.00;

# function initAudio() {
#     if(!audioCtx) {
#         audioCtx = new (window.AudioContext || window.webkitAudioContext)();
#     }
# }

# function playOdibetTakeoffSound() {
#     if(!soundEnabled) return;
#     try {
#         initAudio();
#         let now = audioCtx.currentTime;
#         let osc = audioCtx.createOscillator();
#         let gain = audioCtx.createGain();
#         osc.type = "sawtooth";
#         osc.frequency.setValueAtTime(80, now);
#         osc.frequency.exponentialRampToValueAtTime(750, now + 1.2);
        
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
#         osc.frequency.setValueAtTime(200, now);
#         osc.frequency.linearRampToValueAtTime(35, now + 0.55);
        
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
#     btn.innerText = soundEnabled ? "🔊" : "🔇";
# }

# function toggleMenu() {
#     let drawer = document.getElementById("menuDrawer");
#     if(window.innerWidth < 900) {
#         drawer.classList.toggle("open");
#     }
# }

# function showProfile() {
#     alert("Logged in user account is active.\nMinimum Deposit: KSh 200\nMinimum Withdrawal: KSh 1,000");
#     if(window.innerWidth < 900) toggleMenu();
# }

# function showHowToPlay() {
#     alert("Aviator Rules:\n1. Place your bet before the round starts.\n2. Watch the plane fly and the multiplier increase.\n3. Cash out before the plane flies away to win your stake multiplied by the current multiplier!");
#     if(window.innerWidth < 900) toggleMenu();
# }

# function switchTab(slot, mode) {
#     let tabBet = document.getElementById(`tab${slot}_bet`);
#     let tabAuto = document.getElementById(`tab${slot}_auto`);
#     let autoBox = document.getElementById(`autoBox${slot}`);
    
#     if(mode === 'bet') {
#         tabBet.classList.add("active");
#         tabAuto.classList.remove("active");
#         autoBox.classList.remove("active");
#         autoModes[slot] = false;
#     } else {
#         tabAuto.classList.add("active");
#         tabBet.classList.remove("active");
#         autoBox.classList.add("active");
#         autoModes[slot] = true;
#     }
# }

# function setAmount(slot, val) {
#     document.getElementById("betAmount" + slot).value = val.toFixed(2);
#     updateButtons();
# }

# function adjustAmount(slot, delta) {
#     let inp = document.getElementById("betAmount" + slot);
#     let cur = parseFloat(inp.value) || 0;
#     let nxt = Math.max(50, cur + delta);
#     inp.value = nxt.toFixed(2);
#     updateButtons();
# }

# function openDepositModal() {
#     modalType = 'deposit';
#     document.getElementById("modalTitle").innerText = "Deposit Funds (Min. KSh 200)";
#     document.getElementById("modalDesc").innerText = "Paste your M-Pesa payment prompt link or phone number:";
#     document.getElementById("amountLabel").innerText = "Deposit Amount (KES):";
#     document.getElementById("modalInputAmount").value = "500";
#     document.getElementById("modalInputLink").value = "";
#     document.getElementById("walletModal").style.display = "flex";
#     if(window.innerWidth < 900) {
#         document.getElementById("menuDrawer").classList.remove("open");
#     }
# }

# function openWithdrawModal() {
#     modalType = 'withdraw';
#     document.getElementById("modalTitle").innerText = "Withdraw Funds (Min. KSh 1,000)";
#     document.getElementById("modalDesc").innerText = "Enter your M-Pesa phone number for payout:";
#     document.getElementById("amountLabel").innerText = "Withdrawal Amount (KES):";
#     document.getElementById("modalInputAmount").value = "1000";
#     document.getElementById("modalInputLink").value = "";
#     document.getElementById("walletModal").style.display = "flex";
#     if(window.innerWidth < 900) {
#         document.getElementById("menuDrawer").classList.remove("open");
#     }
# }

# function closeModal() {
#     document.getElementById("walletModal").style.display = "none";
# }

# async function submitModalAction() {
#     let amount = parseFloat(document.getElementById("modalInputAmount").value) || 0;
#     let linkOrPhone = document.getElementById("modalInputLink").value.trim();
    
#     if(modalType === 'deposit') {
#         if(amount < 200) { alert("Minimum deposit is KSh 200."); return; }
#         if(!linkOrPhone) { alert("Please paste your M-Pesa prompt link or enter your phone number."); return; }
        
#         let res = await fetch('/api/confirm-deposit', {
#             method: 'POST',
#             headers: {'Content-Type': 'application/json'},
#             body: JSON.stringify({amount: amount, link: linkOrPhone})
#         });
#         let d = await res.json();
#         alert(d.message);
#         if(d.success) closeModal();
#         fetchState();
#     } else {
#         if(amount < 1000) { alert("Minimum withdrawal is KSh 1,000."); return; }
#         if(!linkOrPhone) { alert("Please enter your M-Pesa phone number."); return; }
        
#         let res = await fetch('/api/withdraw', {
#             method: 'POST',
#             headers: {'Content-Type': 'application/json'},
#             body: JSON.stringify({amount: amount, phone: linkOrPhone})
#         });
#         let d = await res.json();
#         alert(d.message);
#         if(d.success) closeModal();
#         fetchState();
#     }
# }

# async function fetchState() {
#     try {
#         let res = await fetch('/api/state');
#         if(res.status === 401) { window.location.href = '/login'; return; }
#         let data = await res.json();
        
#         let oldState = gameState;
#         gameState = data.status;
#         currentGlobalMultiplier = data.multiplier;
        
#         document.getElementById("lblBalance").innerText = data.balance.toLocaleString(undefined, {minimumFractionDigits:2}) + " KES";
        
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
#         document.getElementById("activeBetsCount").innerText = `Total: ${feed.length}`;
        
#         feed.forEach(bet => {
#             let statusBadge = "";
#             let rowClass = bet.is_self ? "feed-item self" : "feed-item";
            
#             if(bet.status === "ACTIVE") {
#                 statusBadge = `<span style="color:#eab308;">In Game</span>`;
#             } else if(bet.status === "WON") {
#                 statusBadge = `<span style="color:#22c55e; font-weight:bold;">${bet.cashout_multiplier.toFixed(2)}x (+${bet.winnings.toLocaleString()})</span>`;
#             } else {
#                 statusBadge = `<span style="color:#ef4444;">Crashed</span>`;
#             }
#             feedHtml += `<div class="${rowClass}"><span><b>${bet.username}</b> (KSh ${bet.amount.toLocaleString()})</span>${statusBadge}</div>`;
#         });
#         document.getElementById("liveFeedList").innerHTML = feedHtml;

#         let planeEl = document.getElementById("planeIcon");
#         let curvePath = document.getElementById("curvePath");
#         let areaPath = document.getElementById("areaPath");

#         if(gameState === "RUNNING") {
#             if(oldState !== "RUNNING") {
#                 playOdibetTakeoffSound();
#             }

#             document.getElementById("lblMultiplier").innerText = data.multiplier.toFixed(2) + "x";
#             document.getElementById("lblStatusMsg").innerText = "Fly away high!";
#             document.getElementById("lblMultiplier").style.color = "#fff";
            
#             planeEl.style.display = "block";
            
#             let progress = Math.min((data.multiplier - 1.0) / 5.0, 1.0);
#             let svgW = 400, svgH = 250;
#             let targetX = 30 + (progress * 340);
#             let targetY = 240 - (progress * 200);
            
#             let pathString = `M 0 250 Q ${targetX * 0.5} ${250 - (targetY * 0.1)}, ${targetX} ${targetY}`;
#             curvePath.setAttribute("d", pathString);
#             areaPath.setAttribute("d", `${pathString} L ${targetX} 250 L 0 250 Z`);
            
#             let screenBox = document.getElementById("aviatorScreen").getBoundingClientRect();
#             let planeLeft = (targetX / svgW) * screenBox.width;
#             let planeTop = (targetY / svgH) * screenBox.height;
            
#             planeEl.style.left = planeLeft + "px";
#             planeEl.style.top = planeTop + "px";
#             planeEl.style.transform = `translate(-30%, -70%) rotate(${-12 - (progress * 22)}deg)`;

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
#             curvePath.setAttribute("d", "M 0 250 L 0 250");
#             areaPath.setAttribute("d", "M 0 250 L 0 250 L 400 250 Z");
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
#         let amt = parseFloat(document.getElementById("betAmount" + i).value) || 0;
        
#         if(bet && bet.status === "ACTIVE") {
#             if(gameState === "RUNNING") {
#                 let liveWinnings = (amt * currentGlobalMultiplier).toFixed(2);
#                 btn.innerHTML = `CASHOUT<span style="font-size:12px; font-weight:normal; color:#fed7aa;">KES ${Number(liveWinnings).toLocaleString()}</span>`;
#                 btn.className = "action-btn cashout";
#                 btn.disabled = false;
#             } else {
#                 btn.innerText = "WAITING...";
#                 btn.className = "action-btn";
#                 btn.disabled = true;
#             }
#         } else {
#             if(gameState === "BETTING") {
#                 btn.innerText = `Bet ${amt.toFixed(2)} KES`;
#                 btn.className = "action-btn";
#                 btn.disabled = false;
#             } else {
#                 btn.innerText = "BETTING CLOSED";
#                 btn.className = "action-btn";
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
#         let autoVal = autoModes[betNum] ? document.getElementById("autoCashout" + betNum).value : null;
        
#         let res = await fetch('/api/bet', {
#             method: 'POST',
#             headers: {'Content-Type': 'application/json'},
#             body: JSON.stringify({bet_number: betNum, amount: amt, auto_cashout: autoVal})
#         });
#         let d = await res.json();
#         if(d.success) playOdibetTakeoffSound();
#         alert(d.message);
#     }
#     fetchState();
# }

# setInterval(fetchState, 75);
# </script>
# </body>
# </html>

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
# # CONFIGURATION & RULES
# # ============================================================

# DB_NAME = "aviator_live.db"

# BETTING_WINDOW = 5.0
# MAX_BETS = 2
# MIN_DEPOSIT = 200.0
# MIN_WITHDRAWAL = 1000.0
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
# # GAME ENGINE & ODIBET ACCELERATION CURVE
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
#     multiplier = 1.0 + (elapsed * 0.45) + ((elapsed ** 1.65) * 0.12)
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

# FIRST_NAMES = [
#     "alex", "brian", "coll", "david", "eric", "frank", "grace", "harr", "ian", "john",
#     "kevin", "lucy", "mike", "nick", "oliver", "peter", "queen", "ray", "sam", "tom",
#     "victor", "wendy", "xav", "yves", "zack", "kelv", "sylv", "mash", "kip", "wanj",
#     "njeri", "ochi", "otien", "maina", "chep", "kiprot", "kibet", "kipko", "cherot",
#     "jelag", "baras", "mutiso", "odhi", "korir", "kipng", "chepk", "kipke", "kipch"
# ]

# def generate_bot_bets():
#     bets = []
#     count = random.randint(780, 840)
#     for i in range(count):
#         prefix = random.choice(FIRST_NAMES)
#         masked = prefix[:3] + "***" + str(random.randint(0, 9))
#         amount = round(random.choice([50, 100, 200, 500, 1000, 2500, 5000, 10000]), 2)
#         target_cashout = round(random.uniform(1.10, 15.00), 2) if random.random() > 0.12 else None
        
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


# def process_auto_cashouts_and_bets_locked():
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
#             if random.random() < 0.05:
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
#         process_auto_cashouts_and_bets_locked()

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


# def mask_username(username):
#     if len(username) <= 3:
#         return username + "***"
#     return username[:3] + "***" + str(len(username))


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
#             return False, "Betting closed for this round. Wait for next round."

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
#                 return False, f"Bet {bet_number} already placed for this round."

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
#             return True, f"Bet {bet_number} placed successfully!"
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
#                 error = "Phone number not found in records."
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
#         masked_self = mask_username(username)

#         conn = get_db()
#         history_rows = conn.execute("SELECT crash_point FROM rounds WHERE ended_at IS NOT NULL ORDER BY id DESC LIMIT 25").fetchall()
#         history = [float(r["crash_point"]) for r in history_rows][::-1]

#         bet_rows = conn.execute("SELECT bet_number, amount, auto_cashout, cashout_multiplier, winnings, status FROM bets WHERE username = ? AND round_id = ?", (username, GAME["round_id"])).fetchall()
#         conn.close()

#         user_bets = {}
#         all_live_bets = []

#         for r in bet_rows:
#             user_bets[str(r["bet_number"])] = dict(r)
#             all_live_bets.append({
#                 "id": f"real_{r['bet_number']}",
#                 "username": masked_self + " (You)",
#                 "amount": r["amount"],
#                 "auto_cashout": r["auto_cashout"],
#                 "status": r["status"],
#                 "cashout_multiplier": r["cashout_multiplier"],
#                 "winnings": r["winnings"],
#                 "is_self": True
#             })

#         for b in GAME["bot_bets"]:
#             all_live_bets.append(b)

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
#     success, msg = place_bet_for_user(
#         session["username"],
#         int(data.get("bet_number", 1)),
#         data.get("amount", 0),
#         data.get("auto_cashout")
#     )
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
    
#     if amount < MIN_DEPOSIT:
#         return jsonify({"success": False, "message": f"Minimum deposit amount is KSh {MIN_DEPOSIT:,.2f}."})
    
#     add_balance(session["username"], amount)
#     return jsonify({"success": True, "message": f"Successfully deposited KSh {amount:,.2f} via M-Pesa prompt link!"})


# @app.route("/api/withdraw", methods=["POST"])
# def api_withdraw():
#     if "username" not in session:
#         return jsonify({"success": False, "message": "Unauthorized"}), 401
#     data = request.get_json() or {}
#     try:
#         amount = float(data.get("amount", 0))
#     except ValueError:
#         return jsonify({"success": False, "message": "Invalid amount."})
    
#     if amount < MIN_WITHDRAWAL:
#         return jsonify({"success": False, "message": f"Minimum withdrawal amount is KSh {MIN_WITHDRAWAL:,.2f}."})
    
#     username = session["username"]
#     user = get_user(username)
#     if user["balance"] < amount:
#         return jsonify({"success": False, "message": "Insufficient balance for this withdrawal."})
    
#     if deduct_balance(username, amount):
#         return jsonify({"success": True, "message": f"Withdrawal request of KSh {amount:,.2f} sent to {user['phone_number']}. Processing via M-Pesa..."})
#     return jsonify({"success": False, "message": "Withdrawal failed."})


# # ============================================================
# # TEMPLATES
# # ============================================================

# LOGIN_HTML = """<!DOCTYPE html>
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
# </html>"""

# FORGOT_HTML = """<!DOCTYPE html>
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
# </html>"""

# REGISTER_HTML = """<!DOCTYPE html>
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
# </html>"""

# HTML = """<!DOCTYPE html>
# <html lang="en">
# <head>
# <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
# <title>Odi Casino Aviator</title>
# <style>
# * { box-sizing:border-box; }
# body { margin:0; font-family:-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background:#0f0f0f; color:#fff; display:flex; justify-content:center; }

# .app-wrapper { 
#     width:100%; 
#     max-width:480px; 
#     background:#160404; 
#     min-height:100vh; 
#     display:flex; 
#     flex-direction:column; 
#     border-left:1px solid #331010; 
#     border-right:1px solid #331010; 
#     position:relative; 
#     transition: all 0.3s ease;
# }

# @media (min-width: 900px) {
#     body { background: #080202; align-items: center; padding: 20px 0; }
#     .app-wrapper { max-width: 1150px; border: 1px solid #4a1515; border-radius: 16px; overflow: hidden; box-shadow: 0 15px 40px rgba(0,0,0,0.9); min-height: 850px; display: grid; grid-template-columns: 280px 1fr 340px; grid-template-rows: auto auto 1fr; }
    
#     .top-header { grid-column: 1 / -1; }
#     .aviator-subbar { grid-column: 1 / -1; }
#     .history-bar { grid-column: 1 / -1; }
    
#     .menu-drawer { position: relative !important; left: 0 !important; width: 100% !important; height: 100% !important; box-shadow: none !important; border-right: 1px solid #3a1010 !important; grid-row: 4 / 6; display: flex !important; }
#     .menu-header button { display: none !important; }
    
#     .center-stage { grid-column: 2; grid-row: 4; display: flex; flex-direction: column; }
#     .aviator-screen { height: 360px !important; }
#     .betting-container { flex-direction: row !important; gap: 12px; }
#     .bet-card { flex: 1; }

#     .live-feed-section { grid-column: 3; grid-row: 4; max-height: 100% !important; border-left: 1px solid #3a1010; border-top: none !important; }
#     .desktop-hide { display: none !important; }
# }

# @media (max-width: 899px) {
#     .desktop-only-sidebar { display: none; }
#     .desktop-only-sidebar.open { display: flex; }
#     .center-stage { display: flex; flex-direction: column; width: 100%; }
# }

# .top-header { display:flex; justify-content:space-between; align-items:center; background:#1c0707; padding:12px 16px; border-bottom:1px solid #3a1010; }
# .top-left { display:flex; align-items:center; gap:12px; }
# .menu-btn { background:none; border:none; color:#fff; font-size:22px; cursor:pointer; }
# .odi-logo { text-align:center; line-height:1; }
# .odi-txt { font-size:10px; font-weight:bold; color:#fff; letter-spacing:1px; }
# .casino-txt { font-size:14px; font-weight:900; color:#ef4444; letter-spacing:1.5px; font-style:italic; }

# .deposit-btn { background:#facc15; color:#1a1a1a; border:none; padding:8px 18px; border-radius:8px; font-weight:900; font-size:14px; cursor:pointer; }
# .chat-btn { background:#240c0c; border:1px solid #451515; color:#fff; padding:8px 12px; border-radius:8px; cursor:pointer; font-size:14px; }

# .aviator-subbar { display:flex; justify-content:space-between; align-items:center; padding:10px 16px; background:#1a0707; border-bottom:1px solid #3a1010; font-size:13px; }
# .subbar-left { display:flex; align-items:center; gap:8px; }
# .aviator-logo-txt { font-size:16px; font-weight:900; color:#ef4444; font-style:italic; }
# .balance-display { color:#facc15; font-weight:bold; font-size:15px; }

# .history-bar { display:flex; gap:6px; background:#1c0707; padding:8px 14px; overflow-x:auto; border-bottom:1px solid #3a1010; }
# .pill-green { padding:3px 10px; border-radius:12px; font-size:12px; font-weight:bold; background:rgba(34,197,94,0.2); color:#22c55e; border:1px solid #22c55e; white-space:nowrap; }
# .pill-red { padding:3px 10px; border-radius:12px; font-size:12px; font-weight:bold; background:rgba(239,68,68,0.2); color:#ef4444; border:1px solid #ef4444; white-space:nowrap; }

# .aviator-screen { position:relative; height:250px; background:radial-gradient(circle at center, #691515 0%, #2b0606 65%, #160202 100%); border-bottom:2px solid #5a1515; display:flex; flex-direction:column; justify-content:center; align-items:center; overflow:hidden; }
# .multiplier-display { font-size:56px; font-weight:900; color:#fff; text-shadow:0 0 25px rgba(239,68,68,0.8); z-index:10; text-align:center; }
# .status-msg { font-size:14px; color:#eab308; font-weight:bold; z-index:10; margin-top:4px; }

# svg.flight-path { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 2; pointer-events: none; }
# .plane-icon { position: absolute; font-size: 38px; z-index: 5; pointer-events: none; transform: translate(-30%, -70%) rotate(-12deg); filter: drop-shadow(0 0 10px rgba(239,68,68,0.9)); display: none; }

# .menu-drawer { position: absolute; top: 0; left: -280px; width: 280px; height: 100%; background: #1c0707; z-index: 100; transition: left 0.3s ease; border-right: 2px solid #5a1515; box-shadow: 5px 0 25px rgba(0,0,0,0.8); display: flex; flex-direction: column; }
# .menu-drawer.open { left: 0; }
# .menu-header { background: #2c0c0c; padding: 18px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #5a1515; }
# .menu-items { padding: 10px 0; flex: 1; }
# .menu-item { padding: 15px 20px; font-size: 15px; font-weight: bold; color: #d1d5db; cursor: pointer; border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; align-items: center; gap: 12px; }
# .menu-item:hover { background: #3a1010; color: #facc15; }

# .live-feed-section { background:#1c0707; border-top:1px solid #3a1010; padding:12px; max-height:260px; overflow-y:auto; }
# .feed-header { font-size:12px; font-weight:bold; color:#eab308; margin-bottom:8px; display:flex; justify-content:space-between; }
# .feed-item { display:flex; justify-content:space-between; align-items:center; padding:6px 10px; border-bottom:1px solid rgba(255,255,255,0.03); font-size:12px; }
# .feed-item.self { background:rgba(234, 179, 8, 0.15); border-left:3px solid #eab308; }

# .betting-container { padding:12px; display:flex; flex-direction:column; gap:12px; background:#160404; flex:1; }

# .bet-card { background:#1c0707; border:1px solid #3a1010; border-radius:12px; padding:14px; }
# .bet-tabs { display:flex; background:#120303; border-radius:8px; padding:3px; margin-bottom:10px; }
# .bet-tab { flex:1; text-align:center; padding:6px; font-size:12px; font-weight:bold; color:#888; border-radius:6px; cursor:pointer; }
# .bet-tab.active { background:#2c0c0c; color:#fff; }

# .auto-box { display:none; margin-bottom:10px; font-size:12px; color:#9ca3af; }
# .auto-box.active { display:block; }

# .amount-row { display:flex; align-items:center; justify-content:space-between; margin-bottom:10px; }
# .amt-btn { background:#2c0c0c; border:1px solid #4a1515; color:#fff; width:38px; height:38px; border-radius:50%; font-size:18px; font-weight:bold; cursor:pointer; display:flex; align-items:center; justify-content:center; }
# .amt-value { font-size:20px; font-weight:900; color:#fff; letter-spacing:1px; }

# .quick-stakes { display:grid; grid-template-columns:repeat(4, 1fr); gap:6px; margin-bottom:12px; }
# .quick-btn { background:#240808; border:1px solid #4a1515; color:#d1d5db; padding:6px; border-radius:6px; font-size:12px; font-weight:bold; cursor:pointer; text-align:center; }
# .quick-btn:hover { background:#3a1010; color:#fff; }

# .action-btn { width:100%; padding:14px; border:none; border-radius:10px; background:#22c55e; color:white; font-weight:900; font-size:15px; cursor:pointer; text-transform:uppercase; box-shadow:0 4px 12px rgba(34,197,94,0.3); display:flex; flex-direction:column; align-items:center; justify-content:center; line-height:1.2; }
# .action-btn.cashout { background:#dc2626; box-shadow:0 4px 12px rgba(220,38,38,0.3); }
# .action-btn:disabled { opacity:0.4; cursor:not-allowed; box-shadow:none; }

# .admin-banner { background:#7f1d1d; border:1px solid #ef4444; padding:8px 12px; border-radius:8px; display:flex; justify-content:space-between; align-items:center; font-weight:bold; color:#fca5a5; font-size:12px; margin:10px; }
# .admin-val { color:#fff; font-size:15px; }

# .modal-overlay { position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); z-index:200; display:none; justify-content:center; align-items:center; padding:20px; }
# .modal-content { background:#240808; border:1px solid #5a1515; padding:24px; border-radius:12px; width:100%; max-width:380px; box-sizing:border-box; }
# .modal-content h3 { color:#eab308; margin-top:0; }
# .modal-content input { width:100%; padding:12px; margin:10px 0; background:#160404; border:1px solid #5a1515; color:#fff; border-radius:6px; box-sizing:border-box; font-size:15px; }
# .modal-btns { display:flex; gap:10px; margin-top:10px; }
# .modal-btns button { flex:1; padding:12px; border:none; border-radius:6px; font-weight:bold; cursor:pointer; font-size:15px; }
# </style>
# </head>
# <body>

# <div class="app-wrapper">
#     <div class="menu-drawer desktop-only-sidebar" id="menuDrawer">
#         <div class="menu-header">
#             <span style="font-weight:bold; color:#eab308; font-size:16px;">Odi Menu</span>
#             <button class="desktop-hide" onclick="toggleMenu()" style="background:none; border:none; color:#fff; font-size:18px; cursor:pointer;">✕</button>
#         </div>
#         <div class="menu-items">
#             <div class="menu-item" onclick="openDepositModal()">💳 Deposit (Min. KSh 200)</div>
#             <div class="menu-item" onclick="openWithdrawModal()">💸 Withdraw (Min. KSh 1,000)</div>
#             <div class="menu-item" onclick="showProfile()">👤 My Profile</div>
#             <div class="menu-item" onclick="showHowToPlay()">📖 How to Play</div>
#             <div class="menu-item" onclick="window.location.href='/logout'" style="color:#ef4444;">🚪 Logout</div>
#         </div>
#     </div>

#     <div class="top-header">
#         <div class="top-left">
#             <button class="menu-btn desktop-hide" onclick="toggleMenu()">☰</button>
#             <div class="odi-logo">
#                 <div class="odi-txt">odi</div>
#                 <div class="casino-txt">CASINO</div>
#             </div>
#         </div>
#         <div style="display:flex; gap:10px; align-items:center;">
#             <button class="deposit-btn" onclick="openDepositModal()">Deposit</button>
#             <button class="chat-btn" id="soundToggle" onclick="toggleSound()">🔊</button>
#         </div>
#     </div>

#     <div class="center-stage">
#         <div class="aviator-subbar">
#             <div class="subbar-left">
#                 <span class="aviator-logo-txt">Aviator</span>
#             </div>
#             <div>
#                 <span class="balance-display" id="lblBalance">0.00 KES</span>
#             </div>
#         </div>

#         <div class="history-bar" id="historyBar"></div>

#         <div id="adminPanel" class="admin-banner" style="display:none;">
#             <span>ADMIN PREVIEW:</span>
#             <span class="admin-val" id="lblNextCrash">--</span>
#         </div>

#         <div class="aviator-screen" id="aviatorScreen">
#             <svg class="flight-path" id="flightSvg" viewBox="0 0 400 250" preserveAspectRatio="none">
#                 <path id="areaPath" d="M 0 250 L 0 250 L 400 250 Z" fill="rgba(239, 68, 68, 0.2)" />
#                 <path id="curvePath" d="M 0 250 L 0 250" fill="none" stroke="#ef4444" stroke-width="5" stroke-linecap="round" />
#             </svg>
#             <div class="plane-icon" id="planeIcon">✈️</div>
            
#             <div class="multiplier-display" id="lblMultiplier">1.00x</div>
#             <div class="status-msg" id="lblStatusMsg">Waiting for next round...</div>
#         </div>

#         <div class="betting-container">
#             <div class="bet-card">
#                 <div class="bet-tabs">
#                     <div class="bet-tab active" id="tab1_bet" onclick="switchTab(1, 'bet')">Bet</div>
#                     <div class="bet-tab" id="tab1_auto" onclick="switchTab(1, 'auto')">Auto</div>
#                 </div>
#                 <div class="auto-box" id="autoBox1">
#                     <label>Auto Cashout Multiplier</label>
#                     <input type="number" id="autoCashout1" step="0.1" value="2.00" min="1.01" style="width:100%; padding:8px; margin-top:4px; background:#160404; border:1px solid #5a1515; color:#fff; border-radius:4px;">
#                 </div>
#                 <div class="amount-row">
#                     <button class="amt-btn" onclick="adjustAmount(1, -50)">-</button>
#                     <div class="amt-value"><input type="number" id="betAmount1" value="200.00" step="50" style="background:transparent; border:none; color:#fff; font-size:20px; font-weight:900; width:110px; text-align:center;"></div>
#                     <button class="amt-btn" onclick="adjustAmount(1, 50)">+</button>
#                 </div>
#                 <div class="quick-stakes">
#                     <div class="quick-btn" onclick="setAmount(1, 200)">200</div>
#                     <div class="quick-btn" onclick="setAmount(1, 500)">500</div>
#                     <div class="quick-btn" onclick="setAmount(1, 1000)">1,000</div>
#                     <div class="quick-btn" onclick="setAmount(1, 5000)">5,000</div>
#                 </div>
#                 <button class="action-btn" id="btnAction1" onclick="handleBet(1)">Bet 200.00 KES</button>
#             </div>

#             <div class="bet-card">
#                 <div class="bet-tabs">
#                     <div class="bet-tab active" id="tab2_bet" onclick="switchTab(2, 'bet')">Bet</div>
#                     <div class="bet-tab" id="tab2_auto" onclick="switchTab(2, 'auto')">Auto</div>
#                 </div>
#                 <div class="auto-box" id="autoBox2">
#                     <label>Auto Cashout Multiplier</label>
#                     <input type="number" id="autoCashout2" step="0.1" value="5.00" min="1.01" style="width:100%; padding:8px; margin-top:4px; background:#160404; border:1px solid #5a1515; color:#fff; border-radius:4px;">
#                 </div>
#                 <div class="amount-row">
#                     <button class="amt-btn" onclick="adjustAmount(2, -50)">-</button>
#                     <div class="amt-value"><input type="number" id="betAmount2" value="200.00" step="50" style="background:transparent; border:none; color:#fff; font-size:20px; font-weight:900; width:110px; text-align:center;"></div>
#                     <button class="amt-btn" onclick="adjustAmount(2, 50)">+</button>
#                 </div>
#                 <div class="quick-stakes">
#                     <div class="quick-btn" onclick="setAmount(2, 200)">200</div>
#                     <div class="quick-btn" onclick="setAmount(2, 500)">500</div>
#                     <div class="quick-btn" onclick="setAmount(2, 1000)">1,000</div>
#                     <div class="quick-btn" onclick="setAmount(2, 5000)">5,000</div>
#                 </div>
#                 <button class="action-btn" id="btnAction2" onclick="handleBet(2)">Bet 200.00 KES</button>
#             </div>
#         </div>
#     </div>

#     <div class="live-feed-section">
#         <div class="feed-header">
#             <span>LIVE ACTIVE USERS (~820)</span>
#             <span id="activeBetsCount">Bets: 0</span>
#         </div>
#         <div id="liveFeedList"></div>
#     </div>
# </div>

# <div class="modal-overlay" id="walletModal">
#     <div class="modal-content">
#         <h3 id="modalTitle">Deposit Funds</h3>
#         <p id="modalDesc" style="font-size:13px; color:#aaa;">Paste your M-Pesa payment prompt link or phone number:</p>
#         <input type="text" id="modalInputLink" placeholder="https://pay.mpesa.co.ke/... or 2547XXXXXXXX">
#         <label style="font-size:12px; color:#aaa;" id="amountLabel">Amount (Min. KSh 200):</label>
#         <input type="number" id="modalInputAmount" value="500" min="200">
#         <div class="modal-btns">
#             <button onclick="closeModal()" style="background:#444; color:#fff;">Cancel</button>
#             <button onclick="submitModalAction()" style="background:#22c55e; color:#fff;">Proceed</button>
#         </div>
#     </div>
# </div>

# <script>
# let gameState = "BETTING";
# let userBets = {};
# let soundEnabled = true;
# let audioCtx = null;
# let modalType = 'deposit';
# let autoModes = {1: false, 2: false};
# let currentGlobalMultiplier = 1.00;

# function initAudio() {
#     if(!audioCtx) {
#         audioCtx = new (window.AudioContext || window.webkitAudioContext)();
#     }
# }

# function playOdibetTakeoffSound() {
#     if(!soundEnabled) return;
#     try {
#         initAudio();
#         let now = audioCtx.currentTime;
#         let osc = audioCtx.createOscillator();
#         let gain = audioCtx.createGain();
#         osc.type = "sawtooth";
#         osc.frequency.setValueAtTime(80, now);
#         osc.frequency.exponentialRampToValueAtTime(750, now + 1.2);
        
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
#         osc.frequency.setValueAtTime(200, now);
#         osc.frequency.linearRampToValueAtTime(35, now + 0.55);
        
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
#     btn.innerText = soundEnabled ? "🔊" : "🔇";
# }

# function toggleMenu() {
#     let drawer = document.getElementById("menuDrawer");
#     if(window.innerWidth < 900) {
#         drawer.classList.toggle("open");
#     }
# }

# function showProfile() {
#     alert("Logged in user account is active.\\nMinimum Deposit: KSh 200\\nMinimum Withdrawal: KSh 1,000");
#     if(window.innerWidth < 900) toggleMenu();
# }

# function showHowToPlay() {
#     alert("Aviator Rules:\\n1. Place your bet before the round starts.\\n2. Watch the plane fly and the multiplier increase.\\n3. Cash out before the plane flies away to win your stake multiplied by the current multiplier!");
#     if(window.innerWidth < 900) toggleMenu();
# }

# function switchTab(slot, mode) {
#     let tabBet = document.getElementById(`tab${slot}_bet`);
#     let tabAuto = document.getElementById(`tab${slot}_auto`);
#     let autoBox = document.getElementById(`autoBox${slot}`);
    
#     if(mode === 'bet') {
#         tabBet.classList.add("active");
#         tabAuto.classList.remove("active");
#         autoBox.classList.remove("active");
#         autoModes[slot] = false;
#     } else {
#         tabAuto.classList.add("active");
#         tabBet.classList.remove("active");
#         autoBox.classList.add("active");
#         autoModes[slot] = true;
#     }
# }

# function setAmount(slot, val) {
#     document.getElementById("betAmount" + slot).value = val.toFixed(2);
#     updateButtons();
# }

# function adjustAmount(slot, delta) {
#     let inp = document.getElementById("betAmount" + slot);
#     let cur = parseFloat(inp.value) || 0;
#     let nxt = Math.max(50, cur + delta);
#     inp.value = nxt.toFixed(2);
#     updateButtons();
# }

# function openDepositModal() {
#     modalType = 'deposit';
#     document.getElementById("modalTitle").innerText = "Deposit Funds (Min. KSh 200)";
#     document.getElementById("modalDesc").innerText = "Paste your M-Pesa payment prompt link or phone number:";
#     document.getElementById("amountLabel").innerText = "Deposit Amount (KES):";
#     document.getElementById("modalInputAmount").value = "500";
#     document.getElementById("modalInputLink").value = "";
#     document.getElementById("walletModal").style.display = "flex";
#     if(window.innerWidth < 900) {
#         document.getElementById("menuDrawer").classList.remove("open");
#     }
# }

# function openWithdrawModal() {
#     modalType = 'withdraw';
#     document.getElementById("modalTitle").innerText = "Withdraw Funds (Min. KSh 1,000)";
#     document.getElementById("modalDesc").innerText = "Enter your M-Pesa phone number for payout:";
#     document.getElementById("amountLabel").innerText = "Withdrawal Amount (KES):";
#     document.getElementById("modalInputAmount").value = "1000";
#     document.getElementById("modalInputLink").value = "";
#     document.getElementById("walletModal").style.display = "flex";
#     if(window.innerWidth < 900) {
#         document.getElementById("menuDrawer").classList.remove("open");
#     }
# }

# function closeModal() {
#     document.getElementById("walletModal").style.display = "none";
# }

# async function submitModalAction() {
#     let amount = parseFloat(document.getElementById("modalInputAmount").value) || 0;
#     let linkOrPhone = document.getElementById("modalInputLink").value.trim();
    
#     if(modalType === 'deposit') {
#         if(amount < 200) { alert("Minimum deposit is KSh 200."); return; }
#         if(!linkOrPhone) { alert("Please paste your M-Pesa prompt link or enter your phone number."); return; }
        
#         let res = await fetch('/api/confirm-deposit', {
#             method: 'POST',
#             headers: {'Content-Type': 'application/json'},
#             body: JSON.stringify({amount: amount, link: linkOrPhone})
#         });
#         let d = await res.json();
#         alert(d.message);
#         if(d.success) closeModal();
#         fetchState();
#     } else {
#         if(amount < 1000) { alert("Minimum withdrawal is KSh 1,000."); return; }
#         if(!linkOrPhone) { alert("Please enter your M-Pesa phone number."); return; }
        
#         let res = await fetch('/api/withdraw', {
#             method: 'POST',
#             headers: {'Content-Type': 'application/json'},
#             body: JSON.stringify({amount: amount, phone: linkOrPhone})
#         });
#         let d = await res.json();
#         alert(d.message);
#         if(d.success) closeModal();
#         fetchState();
#     }
# }

# async function fetchState() {
#     try {
#         let res = await fetch('/api/state');
#         if(res.status === 401) { window.location.href = '/login'; return; }
#         let data = await res.json();
        
#         let oldState = gameState;
#         gameState = data.status;
#         currentGlobalMultiplier = data.multiplier;
        
#         document.getElementById("lblBalance").innerText = data.balance.toLocaleString(undefined, {minimumFractionDigits:2}) + " KES";
        
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
#         document.getElementById("activeBetsCount").innerText = `Total: ${feed.length}`;
        
#         feed.forEach(bet => {
#             let statusBadge = "";
#             let rowClass = bet.is_self ? "feed-item self" : "feed-item";
            
#             if(bet.status === "ACTIVE") {
#                 statusBadge = `<span style="color:#eab308;">In Game</span>`;
#             } else if(bet.status === "WON") {
#                 statusBadge = `<span style="color:#22c55e; font-weight:bold;">${bet.cashout_multiplier.toFixed(2)}x (+${bet.winnings.toLocaleString()})</span>`;
#             } else {
#                 statusBadge = `<span style="color:#ef4444;">Crashed</span>`;
#             }
#             feedHtml += `<div class="${rowClass}"><span><b>${bet.username}</b> (KSh ${bet.amount.toLocaleString()})</span>${statusBadge}</div>`;
#         });
#         document.getElementById("liveFeedList").innerHTML = feedHtml;

#         let planeEl = document.getElementById("planeIcon");
#         let curvePath = document.getElementById("curvePath");
#         let areaPath = document.getElementById("areaPath");

#         if(gameState === "RUNNING") {
#             if(oldState !== "RUNNING") {
#                 playOdibetTakeoffSound();
#             }

#             document.getElementById("lblMultiplier").innerText = data.multiplier.toFixed(2) + "x";
#             document.getElementById("lblStatusMsg").innerText = "Fly away high!";
#             document.getElementById("lblMultiplier").style.color = "#fff";
            
#             planeEl.style.display = "block";
            
#             let progress = Math.min((data.multiplier - 1.0) / 5.0, 1.0);
#             let svgW = 400, svgH = 250;
#             let targetX = 30 + (progress * 340);
#             let targetY = 240 - (progress * 200);
            
#             let pathString = `M 0 250 Q ${targetX * 0.5} ${250 - (targetY * 0.1)}, ${targetX} ${targetY}`;
#             curvePath.setAttribute("d", pathString);
#             areaPath.setAttribute("d", `${pathString} L ${targetX} 250 L 0 250 Z`);
            
#             let screenBox = document.getElementById("aviatorScreen").getBoundingClientRect();
#             let planeLeft = (targetX / svgW) * screenBox.width;
#             let planeTop = (targetY / svgH) * screenBox.height;
            
#             planeEl.style.left = planeLeft + "px";
#             planeEl.style.top = planeTop + "px";
#             planeEl.style.transform = `translate(-30%, -70%) rotate(${-12 - (progress * 22)}deg)`;

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
#             curvePath.setAttribute("d", "M 0 250 L 0 250");
#             areaPath.setAttribute("d", "M 0 250 L 0 250 L 400 250 Z");
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
#         let amt = parseFloat(document.getElementById("betAmount" + i).value) || 0;
        
#         if(bet && bet.status === "ACTIVE") {
#             if(gameState === "RUNNING") {
#                 let liveWinnings = (amt * currentGlobalMultiplier).toFixed(2);
#                 btn.innerHTML = `CASHOUT<span style="font-size:12px; font-weight:normal; color:#fed7aa;">KES ${Number(liveWinnings).toLocaleString()}</span>`;
#                 btn.className = "action-btn cashout";
#                 btn.disabled = false;
#             } else {
#                 btn.innerText = "WAITING...";
#                 btn.className = "action-btn";
#                 btn.disabled = true;
#             }
#         } else {
#             if(gameState === "BETTING") {
#                 btn.innerText = `Bet ${amt.toFixed(2)} KES`;
#                 btn.className = "action-btn";
#                 btn.disabled = false;
#             } else {
#                 btn.innerText = "BETTING CLOSED";
#                 btn.className = "action-btn";
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
#         let autoVal = autoModes[betNum] ? document.getElementById("autoCashout" + betNum).value : null;
        
#         let res = await fetch('/api/bet', {
#             method: 'POST',
#             headers: {'Content-Type': 'application/json'},
#             body: JSON.stringify({bet_number: betNum, amount: amt, auto_cashout: autoVal})
#         });
#         let d = await res.json();
#         if(d.success) playOdibetTakeoffSound();
#         alert(d.message);
#     }
#     fetchState();
# }

# setInterval(fetchState, 75);
# </script>
# </body>
# </html>"""

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

BETTING_WINDOW = 3.0
MAX_BETS = 2
MIN_DEPOSIT = 100.0
MIN_WITHDRAWAL = 100.0
CRASH_DISPLAY_TIME = 1.0
STARTING_BALANCE = 10000.0

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
            balance REAL DEFAULT 10000.0,
            role TEXT DEFAULT 'USER',
            created_at TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS rounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crash_point REAL NOT NULL,
            server_seed TEXT NOT NULL,
            client_seed TEXT NOT NULL,
            hash TEXT NOT NULL,
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
            auto_bet_enabled INTEGER DEFAULT 0,
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

    # Verify column existence for auto_bet_enabled (Schema migration safety)
    cursor = conn.execute("PRAGMA table_info(bets)")
    columns = [col[1] for col in cursor.fetchall()]
    if "auto_bet_enabled" not in columns:
        conn.execute("ALTER TABLE bets ADD COLUMN auto_bet_enabled INTEGER DEFAULT 0")

    admin = conn.execute("SELECT id FROM users WHERE username = ?", ("EVRON",)).fetchone()
    if not admin:
        conn.execute("""
            INSERT INTO users (username, password, phone_number, balance, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "EVRON",
            hash_password("61782497"),
            "254700000000",
            100000.0,
            "ADMIN",
            datetime.now().isoformat()
        ))
    else:
        conn.execute("UPDATE users SET role = 'ADMIN' WHERE username = ?", ("EVRON",))

    conn.commit()
    conn.close()


# ============================================================
# GAME ENGINE & ACCELERATION CURVE
# ============================================================

def generate_provably_fair_round():
    server_seed = secrets.token_hex(16)
    client_seed = secrets.token_hex(8)
    combined = f"{server_seed}-{client_seed}".encode('utf-8')
    hash_hex = hashlib.sha256(combined).hexdigest()
    
    # Calculate crash point deterministically from hash prefix
    hash_int = int(hash_hex[:8], 16)
    if hash_int % 33 == 0:
        crash_point = 1.00
    else:
        crash_point = round(max(1.00, (100.0 * (2**32) - hash_int) / ((2**32) - hash_int + 1) / 100.0), 2)
        if crash_point > 100.0:
            crash_point = round(random.uniform(25.0, 150.0), 2)
            
    return round(crash_point, 2), server_seed, client_seed, hash_hex


def calculate_multiplier(elapsed):
    multiplier = 1.0 + (elapsed * 0.45) + ((elapsed ** 1.65) * 0.12)
    return round(multiplier, 2)


# Initialize first seed pair
cp_init, ss_init, cs_init, h_init = generate_provably_fair_round()
cp_next, ss_next, cs_next, h_next = generate_provably_fair_round()

GAME = {
    "round_id": None,
    "crash_point": cp_init,
    "server_seed": ss_init,
    "client_seed": cs_init,
    "hash": h_init,
    "next_crash_points": [cp_next],
    "next_seeds": [{"server_seed": ss_next, "client_seed": cs_next, "hash": h_next}],
    "status": "WAITING",
    "betting_start": None,
    "run_start": None,
    "current_multiplier": 1.00,
    "crash_time": None,
    "multiplier_history": [2.45, 1.12, 5.80, 1.02, 3.14, 1.45, 12.40, 1.00, 2.10, 4.35],
    "bot_bets": []
}

FIRST_NAMES = [
    "alex", "brian", "coll", "david", "eric", "frank", "grace", "harr", "ian", "john",
    "kevin", "lucy", "mike", "nick", "oliver", "peter", "queen", "ray", "sam", "tom",
    "victor", "wendy", "xav", "yves", "zack", "kelv", "sylv", "mash", "kip", "wanj",
    "njeri", "ochi", "otien", "maina", "chep", "kiprot", "kibet", "kipko", "cherot"
]

def generate_bot_bets():
    bets = []
    count = random.randint(35, 55)
    for i in range(count):
        prefix = random.choice(FIRST_NAMES)
        masked = prefix[:3] + "***" + str(random.randint(0, 9))
        amount = round(random.choice([50, 100, 200, 500, 1000, 2500, 5000]), 2)
        target_cashout = round(random.uniform(1.10, 12.00), 2) if random.random() > 0.15 else None
        
        bets.append({
            "id": f"bot_{i}",
            "username": masked,
            "amount": amount,
            "auto_cashout": target_cashout,
            "status": "ACTIVE",
            "cashout_multiplier": None,
            "winnings": 0.0,
            "cashedOut": False,
            "cashoutAmount": 0.0
        })
    return bets


def create_round_locked():
    if GAME["next_seeds"]:
        next_data = GAME["next_seeds"].pop(0)
        crash_point = GAME["next_crash_points"].pop(0)
        server_seed = next_data["server_seed"]
        client_seed = next_data["client_seed"]
        hash_hex = next_data["hash"]
    else:
        crash_point, server_seed, client_seed, hash_hex = generate_provably_fair_round()

    cp_new, ss_new, cs_new, h_new = generate_provably_fair_round()
    GAME["next_crash_points"].append(cp_new)
    GAME["next_seeds"].append({"server_seed": ss_new, "client_seed": cs_new, "hash": h_new})

    now = datetime.now().isoformat()
    conn = get_db()
    cursor = conn.execute("""
        INSERT INTO rounds (crash_point, server_seed, client_seed, hash, started_at) 
        VALUES (?, ?, ?, ?, ?)
    """, (crash_point, server_seed, client_seed, hash_hex, now))
    round_id = cursor.lastrowid
    
    # Process Auto Bets for active users
    active_auto_bets = conn.execute("""
        SELECT b.username, b.bet_number, b.amount, b.auto_cashout, u.balance 
        FROM bets b 
        JOIN users u ON b.username = u.username 
        WHERE b.auto_bet_enabled = 1
        GROUP BY b.username, b.bet_number
    """).fetchall()

    for ab in active_auto_bets:
        if ab["balance"] >= ab["amount"]:
            conn.execute("UPDATE users SET balance = balance - ? WHERE username = ?", (ab["amount"], ab["username"]))
            conn.execute("""
                INSERT INTO bets (username, round_id, bet_number, amount, auto_cashout, auto_bet_enabled, status, created_at)
                VALUES (?, ?, ?, ?, ?, 1, 'ACTIVE', ?)
            """, (ab["username"], round_id, ab["bet_number"], ab["amount"], ab["auto_cashout"], now))

    conn.commit()
    conn.close()

    GAME["round_id"] = round_id
    GAME["crash_point"] = crash_point
    GAME["server_seed"] = server_seed
    GAME["client_seed"] = client_seed
    GAME["hash"] = hash_hex
    GAME["status"] = "WAITING"
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
    if GAME["status"] != "WAITING":
        return
    GAME["status"] = "FLYING"
    GAME["run_start"] = time.time()
    GAME["current_multiplier"] = 1.00


def process_auto_cashouts_and_bets_locked():
    if GAME["status"] != "FLYING":
        return

    multiplier = GAME["current_multiplier"]
    crash_point = GAME["crash_point"]
    round_id = GAME["round_id"]

    if multiplier >= crash_point:
        return

    for bot in GAME["bot_bets"]:
        if not bot["cashedOut"] and bot["auto_cashout"] and bot["auto_cashout"] <= multiplier and bot["auto_cashout"] < crash_point:
            bot["cashedOut"] = True
            bot["cashout_multiplier"] = bot["auto_cashout"]
            bot["cashoutAmount"] = round(bot["amount"] * bot["auto_cashout"], 2)

    for bot in GAME["bot_bets"]:
        if not bot["cashedOut"] and not bot["auto_cashout"] and multiplier > 1.20:
            if random.random() < 0.06:
                bot["cashedOut"] = True
                bot["cashout_multiplier"] = multiplier
                bot["cashoutAmount"] = round(bot["amount"] * multiplier, 2)

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

    GAME["multiplier_history"].append(GAME["crash_point"])
    if len(GAME["multiplier_history"]) > 20:
        GAME["multiplier_history"].pop(0)

    for bot in GAME["bot_bets"]:
        if not bot["cashedOut"]:
            bot["status"] = "LOST"

    conn = get_db()
    conn.execute("UPDATE bets SET status = 'LOST' WHERE round_id = ? AND status = 'ACTIVE'", (GAME["round_id"],))
    conn.execute("UPDATE rounds SET ended_at = ? WHERE id = ?", (datetime.now().isoformat(), GAME["round_id"]))
    conn.commit()
    conn.close()


def tick_game_locked():
    initialize_game()
    now = time.time()

    if GAME["status"] == "WAITING":
        elapsed = now - GAME["betting_start"]
        GAME["current_multiplier"] = 1.00
        if elapsed >= BETTING_WINDOW:
            start_running_locked()

    elif GAME["status"] == "FLYING":
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
        time.sleep(0.03)


threading.Thread(target=game_loop, daemon=True).start()
init_db()


# ============================================================
# FLASK API & TEMPLATE ROUTING
# ============================================================

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.json or {}
    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()
    password = data.get("pass", "").strip()

    if not name or not phone or not password:
        return jsonify({"success": False, "message": "All fields are required."}), 400

    conn = get_db()
    existing = conn.execute("SELECT id FROM users WHERE phone_number = ? OR username = ?", (phone, name)).fetchone()
    if existing:
        conn.close()
        return jsonify({"success": False, "message": "User or phone number already registered."}), 400

    hashed = hash_password(password)
    now = datetime.now().isoformat()
    conn.execute("""
        INSERT INTO users (username, password, phone_number, balance, role, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, hashed, phone, STARTING_BALANCE, "USER", now))
    conn.commit()
    user = conn.execute("SELECT username, phone_number, balance, role FROM users WHERE username = ?", (name,)).fetchone()
    conn.close()

    session["username"] = user["username"]
    return jsonify({
        "success": True,
        "user": {
            "name": user["username"],
            "phone": user["phone_number"],
            "balance": user["balance"],
            "isAdmin": user["role"] == "ADMIN"
        }
    })


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json or {}
    user_inp = data.get("user", "").strip()
    pass_inp = data.get("pass", "").strip()

    if not user_inp or not pass_inp:
        return jsonify({"success": False, "message": "Invalid username or password."}), 400

    conn = get_db()
    user = conn.execute("""
        SELECT * FROM users WHERE username = ? OR phone_number = ?
    """, (user_inp, user_inp)).fetchone()
    conn.close()

    if not user or not verify_password(pass_inp, user["password"]):
        return jsonify({"success": False, "message": "Invalid credentials."}), 400

    session["username"] = user["username"]
    return jsonify({
        "success": True,
        "user": {
            "name": user["username"],
            "phone": user["phone_number"],
            "balance": user["balance"],
            "isAdmin": user["role"] == "ADMIN"
        }
    })


@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.pop("username", None)
    return jsonify({"success": True})


@app.route("/api/state", methods=["GET"])
def api_state():
    username = session.get("username")
    user_data = {"balance": STARTING_BALANCE, "name": "Player", "isAdmin": False}
    
    user_bets = []
    if username:
        conn = get_db()
        u = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if u:
            user_data = {
                "name": u["username"],
                "phone": u["phone_number"],
                "balance": u["balance"],
                "isAdmin": u["role"] == "ADMIN"
            }
        
        with GAME_LOCK:
            current_round = GAME["round_id"]
        
        if current_round:
            b_rows = conn.execute("SELECT * FROM bets WHERE username = ? AND round_id = ?", (username, current_round)).fetchall()
            for br in b_rows:
                user_bets.append({
                    "betNumber": br["bet_number"],
                    "amount": br["amount"],
                    "autoEnabled": br["auto_cashout"] is not None,
                    "autoMultiplier": br["auto_cashout"] or 2.0,
                    "autoBet": bool(br["auto_bet_enabled"]),
                    "active": br["status"] == "ACTIVE",
                    "cashedOut": br["status"] == "WON",
                    "cashoutValue": br["winnings"]
                })
        conn.close()

    with GAME_LOCK:
        game_payload = {
            "roundId": GAME["round_id"],
            "status": GAME["status"],
            "currentMultiplier": GAME["current_multiplier"],
            "crashPoint": GAME["crash_point"] if GAME["status"] == "CRASHED" else None,
            "serverSeed": GAME["server_seed"],
            "clientSeed": GAME["client_seed"],
            "hash": GAME["hash"],
            "history": GAME["multiplier_history"],
            "botBets": GAME["bot_bets"],
            "nextPreview": GAME["next_crash_points"][0]
        }

    return jsonify({
        "success": True,
        "user": user_data,
        "userBets": user_bets,
        "game": game_payload
    })


@app.route("/api/bet", methods=["POST"])
def api_bet():
    username = session.get("username")
    if not username:
        return jsonify({"success": False, "message": "Not logged in."}), 401

    data = request.json or {}
    bet_number = int(data.get("betNumber", 1))
    amount = float(data.get("amount", 10.0))
    auto_enabled = bool(data.get("autoEnabled", False))
    auto_mult = float(data.get("autoMultiplier", 2.0))
    auto_bet = bool(data.get("autoBet", False))

    with GAME_LOCK:
        if GAME["status"] == "CRASHED":
            return jsonify({"success": False, "message": "Round has ended. Wait for next round."}), 400
        round_id = GAME["round_id"]

    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if not user or user["balance"] < amount:
        conn.close()
        return jsonify({"success": False, "message": "Insufficient balance."}), 400

    existing_bet = conn.execute("SELECT * FROM bets WHERE username = ? AND round_id = ? AND bet_number = ?", (username, round_id, bet_number)).fetchone()
    
    if existing_bet:
        if existing_bet["status"] == "ACTIVE":
            # Refund & cancel bet
            conn.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (existing_bet["amount"], username))
            conn.execute("DELETE FROM bets WHERE id = ?", (existing_bet["id"],))
            conn.commit()
            conn.close()
            return jsonify({"success": True, "action": "CANCELLED"})
        else:
            conn.close()
            return jsonify({"success": False, "message": "Bet already settled."}), 400

    # Place new bet
    conn.execute("UPDATE users SET balance = balance - ? WHERE username = ?", (amount, username))
    now = datetime.now().isoformat()
    conn.execute("""
        INSERT INTO bets (username, round_id, bet_number, amount, auto_cashout, auto_bet_enabled, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, round_id, bet_number, amount, auto_mult if auto_enabled else None, 1 if auto_bet else 0, "ACTIVE", now))
    conn.commit()
    
    updated_user = conn.execute("SELECT balance FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()

    return jsonify({"success": True, "action": "PLACED", "balance": updated_user["balance"]})


@app.route("/api/cashout", methods=["POST"])
def api_cashout():
    username = session.get("username")
    if not username:
        return jsonify({"success": False, "message": "Not logged in."}), 401

    data = request.json or {}
    bet_number = int(data.get("betNumber", 1))

    with GAME_LOCK:
        if GAME["status"] != "FLYING":
            return jsonify({"success": False, "message": "Flight is not active."}), 400
        current_mult = GAME["current_multiplier"]
        round_id = GAME["round_id"]

    conn = get_db()
    bet = conn.execute("""
        SELECT * FROM bets WHERE username = ? AND round_id = ? AND bet_number = ? AND status = 'ACTIVE'
    """, (username, round_id, bet_number)).fetchone()

    if not bet:
        conn.close()
        return jsonify({"success": False, "message": "Active bet not found."}), 400

    winnings = round(bet["amount"] * current_mult, 2)
    conn.execute("""
        UPDATE bets
        SET status = 'WON', cashout_multiplier = ?, winnings = ?
        WHERE id = ?
    """, (current_mult, winnings, bet["id"]))
    conn.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (winnings, username))
    conn.commit()

    updated_user = conn.execute("SELECT balance FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()

    return jsonify({"success": True, "winnings": winnings, "multiplier": current_mult, "balance": updated_user["balance"]})


@app.route("/api/deposit", methods=["POST"])
def api_deposit():
    username = session.get("username")
    if not username:
        return jsonify({"success": False, "message": "Not logged in."}), 401

    data = request.json or {}
    amount = float(data.get("amount", 1000.0))

    if amount < MIN_DEPOSIT:
        return jsonify({"success": False, "message": f"Minimum deposit amount is {MIN_DEPOSIT} KES."}), 400

    conn = get_db()
    conn.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (amount, username))
    user = conn.execute("SELECT balance FROM users WHERE username = ?", (username,)).fetchone()
    conn.commit()
    conn.close()

    return jsonify({"success": True, "balance": user["balance"]})


@app.route("/api/withdraw", methods=["POST"])
def api_withdraw():
    username = session.get("username")
    if not username:
        return jsonify({"success": False, "message": "Not logged in."}), 401

    data = request.json or {}
    amount = float(data.get("amount", 1000.0))

    if amount < MIN_WITHDRAWAL:
        return jsonify({"success": False, "message": f"Minimum withdrawal amount is {MIN_WITHDRAWAL} KES."}), 400

    conn = get_db()
    user = conn.execute("SELECT balance FROM users WHERE username = ?", (username,)).fetchone()
    if not user or user["balance"] < amount:
        conn.close()
        return jsonify({"success": False, "message": "Insufficient balance."}), 400

    conn.execute("UPDATE users SET balance = balance - ? WHERE username = ?", (amount, username))
    updated = conn.execute("SELECT balance FROM users WHERE username = ?", (username,)).fetchone()
    conn.commit()
    conn.close()

    return jsonify({"success": True, "balance": updated["balance"]})


@app.route("/api/admin/override", methods=["POST"])
def api_admin_override():
    username = session.get("username")
    if not username:
        return jsonify({"success": False, "message": "Unauthorized."}), 401

    conn = get_db()
    user = conn.execute("SELECT role FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()

    if not user or user["role"] != "ADMIN":
        return jsonify({"success": False, "message": "Admin access required."}), 403

    data = request.json or {}
    val = float(data.get("multiplier", 2.0))

    with GAME_LOCK:
        GAME["next_crash_points"][0] = val

    return jsonify({"success": True, "nextMultiplier": val})


# ============================================================
# FRONTEND HTML TEMPLATE
# ============================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aviator Live Casino</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        darkBg: '#0b0e14',
                        panelBg: '#121824',
                        cardBg: '#1a2233',
                        accentRed: '#e53e3e',
                        accentGreen: '#319795',
                        brandYellow: '#ecc94b'
                    }
                }
            }
        }
    </script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #0b0e14; color: #f7fafc; overflow-x: hidden; }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #121824; }
        ::-webkit-scrollbar-thumb { background: #2a374d; border-radius: 3px; }
        .flight-glow { text-shadow: 0 0 25px rgba(236, 201, 75, 0.6); }
    </style>
</head>
<body class="min-h-screen flex flex-col justify-between bg-darkBg text-white">

    <!-- AUTH MODAL -->
    <div id="auth-modal" class="fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center p-4">
        <div class="bg-panelBg border border-gray-700 w-full max-w-md rounded-3xl p-6 shadow-2xl flex flex-col space-y-5">
            <div class="flex items-center justify-between pb-3 border-b border-gray-800">
                <div class="flex items-center space-x-3">
                    <div class="bg-red-600 p-2 rounded-xl text-white font-black text-lg flex items-center justify-center">
                        <i class="fa-solid fa-plane-up"></i>
                    </div>
                    <h2 id="auth-title" class="font-black text-lg text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-red-500">AVIATOR LOGIN</h2>
                </div>
            </div>

            <div class="grid grid-cols-2 bg-cardBg p-1 rounded-xl border border-gray-700 text-xs font-bold">
                <button onclick="switchAuthTab('login')" id="auth-tab-login" class="py-2.5 rounded-lg bg-blue-600 text-white transition">Login</button>
                <button onclick="switchAuthTab('register')" id="auth-tab-register" class="py-2.5 rounded-lg text-gray-400 hover:text-white transition">Register</button>
            </div>

            <!-- LOGIN FORM -->
            <div id="form-login" class="flex flex-col space-y-4">
                <div class="flex flex-col space-y-1">
                    <label class="text-xs text-gray-400 font-medium">Username or Phone Number (Admin: EVRON):</label>
                    <input id="login-user" type="text" placeholder="e.g. EVRON or 0712345678" class="bg-cardBg border border-gray-700 rounded-xl px-3 py-2.5 text-xs text-white focus:outline-none">
                </div>
                <div class="flex flex-col space-y-1">
                    <label class="text-xs text-gray-400 font-medium">Password:</label>
                    <input id="login-pass" type="password" placeholder="••••••••" class="bg-cardBg border border-gray-700 rounded-xl px-3 py-2.5 text-xs text-white focus:outline-none">
                </div>
                <button onclick="submitLogin()" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3 rounded-xl shadow-lg transition text-sm uppercase">
                    Login to Flight
                </button>
            </div>

            <!-- REGISTER FORM -->
            <div id="form-register" class="flex flex-col space-y-4 hidden">
                <div class="flex flex-col space-y-1">
                    <label class="text-xs text-gray-400 font-medium">Username:</label>
                    <input id="reg-name" type="text" placeholder="JohnDoe" class="bg-cardBg border border-gray-700 rounded-xl px-3 py-2.5 text-xs text-white focus:outline-none">
                </div>
                <div class="flex flex-col space-y-1">
                    <label class="text-xs text-gray-400 font-medium">M-PESA Phone Number:</label>
                    <input id="reg-phone" type="text" placeholder="+254 712 345 678" class="bg-cardBg border border-gray-700 rounded-xl px-3 py-2.5 text-xs text-white focus:outline-none">
                </div>
                <div class="flex flex-col space-y-1">
                    <label class="text-xs text-gray-400 font-medium">Create Password:</label>
                    <input id="reg-pass" type="password" placeholder="••••••••" class="bg-cardBg border border-gray-700 rounded-xl px-3 py-2.5 text-xs text-white focus:outline-none">
                </div>
                <button onclick="submitRegister()" class="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-xl shadow-lg transition text-sm uppercase">
                    Register Account & Get 10,000 KES
                </button>
            </div>
        </div>
    </div>

    <!-- HEADER -->
    <header class="bg-panelBg border-b border-gray-800 px-4 py-3 flex items-center justify-between shadow-lg relative z-40">
        <div class="flex items-center space-x-3">
            <div class="bg-red-600 p-2 rounded-xl text-white font-black text-xl flex items-center justify-center shadow-md">
                <i class="fa-solid fa-plane-up"></i>
            </div>
            <div>
                <h1 class="font-black text-lg tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-red-500">AVIATOR</h1>
                <p id="header-user-tag" class="text-xs text-gray-400">Welcome, Player</p>
            </div>
        </div>
        <div class="flex items-center space-x-3">
            <div class="bg-cardBg px-3 py-1.5 rounded-xl border border-gray-700 flex items-center space-x-2 shadow-inner">
                <span class="text-xs text-gray-400 font-medium">Balance:</span>
                <span id="user-balance" class="font-bold text-yellow-400 text-sm md:text-base">10,000.00 KES</span>
            </div>
            <button onclick="openDepositModal()" class="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs px-3 py-2 rounded-xl transition shadow flex items-center space-x-1">
                <i class="fa-solid fa-plus-circle"></i>
                <span class="hidden sm:inline">Deposit</span>
            </button>
            <button onclick="toggleMenu()" class="bg-cardBg hover:bg-gray-700 border border-gray-700 p-2.5 rounded-xl text-gray-300 transition shadow">
                <i class="fa-solid fa-bars"></i>
            </button>
        </div>

        <!-- DROPDOWN MENU -->
        <div id="dropdown-menu" class="hidden absolute top-16 right-4 w-64 bg-panelBg border border-gray-700 rounded-2xl shadow-2xl p-3 flex flex-col space-y-2 z-50">
            <div class="flex items-center justify-between pb-2 border-b border-gray-800">
                <span class="font-bold text-sm text-gray-200">Menu</span>
                <button onclick="toggleMenu()" class="text-gray-400 hover:text-white"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <button onclick="openProvablyFairModal()" class="flex items-center space-x-3 px-3 py-2.5 rounded-xl hover:bg-cardBg text-gray-300 transition text-sm font-medium">
                <i class="fa-solid fa-shield-halved text-emerald-400 w-5"></i>
                <span>Provably Fair Seeds</span>
            </button>
            <button onclick="openWithdrawModal()" class="flex items-center space-x-3 px-3 py-2.5 rounded-xl hover:bg-cardBg text-gray-300 transition text-sm font-medium">
                <i class="fa-solid fa-wallet text-emerald-400 w-5"></i>
                <span>Withdraw Funds</span>
            </button>
            <button id="admin-menu-btn" onclick="openAdminModal()" class="hidden flex items-center space-x-3 px-3 py-2.5 rounded-xl hover:bg-cardBg text-yellow-400 transition text-sm font-bold border border-yellow-800/40">
                <i class="fa-solid fa-lock w-5"></i>
                <span>Admin Override Panel</span>
            </button>
            <button onclick="logoutUser()" class="flex items-center space-x-3 px-3 py-2.5 rounded-xl hover:bg-red-950/40 text-red-400 transition text-sm font-medium border-t border-gray-800 mt-2">
                <i class="fa-solid fa-right-from-bracket w-5"></i>
                <span>Logout</span>
            </button>
        </div>
    </header>

    <!-- MAIN GAME AREA -->
    <main class="flex-1 max-w-7xl w-full mx-auto p-2 sm:p-4 grid grid-cols-1 lg:grid-cols-12 gap-4">
        
        <section class="lg:col-span-8 flex flex-col space-y-4">
            
            <!-- HISTORY BAR -->
            <div id="history-bar" class="bg-panelBg rounded-xl border border-gray-800 px-3 py-2 flex items-center space-x-2 overflow-x-auto whitespace-nowrap shadow-md">
                <span class="text-xs text-gray-500 font-semibold uppercase tracking-wider mr-1">History:</span>
            </div>

            <!-- CANVAS FLIGHT ARENA -->
            <div class="relative bg-gradient-to-b from-panelBg via-cardBg to-panelBg rounded-2xl border border-gray-800 h-[300px] sm:h-[380px] flex flex-col items-center justify-center overflow-hidden shadow-2xl">
                <div class="absolute inset-0 opacity-10 bg-[radial-gradient(#e53e3e_1px,transparent_1px)] [background-size:16px_16px]"></div>
                <canvas id="flight-canvas" class="absolute inset-0 w-full h-full z-0"></canvas>

                <div id="game-status-container" class="z-10 flex flex-col items-center justify-center text-center p-4">
                    <div id="multiplier-display" class="text-5xl sm:text-7xl font-black flight-glow text-yellow-400 tracking-tight transition-all duration-75">
                        1.00x
                    </div>
                    <div id="flight-status-text" class="mt-2 text-sm sm:text-lg font-bold uppercase tracking-widest text-emerald-400 bg-emerald-950/60 px-4 py-1.5 rounded-full border border-emerald-800/50 shadow">
                        WAITING FOR NEXT ROUND
                    </div>
                </div>
            </div>

            <!-- DUAL BET PANELS -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                
                <!-- BET PANEL 1 -->
                <div class="bg-panelBg rounded-2xl border border-gray-800 p-4 flex flex-col space-y-3 shadow-xl">
                    <div class="flex items-center justify-between">
                        <span class="font-bold text-sm text-gray-200">BET 1</span>
                        <div class="flex items-center space-x-1 bg-cardBg p-1 rounded-lg border border-gray-700 text-xs">
                            <button onclick="setTab(1, 'manual')" id="bet1-tab-manual" class="px-3 py-1 rounded-md bg-blue-600 text-white font-bold transition">Manual</button>
                            <button onclick="setTab(1, 'auto')" id="bet1-tab-auto" class="px-3 py-1 rounded-md text-gray-400 font-bold hover:text-white transition">Auto</button>
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-2">
                        <div class="flex flex-col space-y-1">
                            <label class="text-[10px] uppercase font-bold text-gray-400">Amount (KES)</label>
                            <input id="bet1-amount" type="number" value="100" class="bg-cardBg border border-gray-700 rounded-xl px-3 py-2 text-sm font-bold text-yellow-400 focus:outline-none">
                        </div>
                        <div class="flex flex-col space-y-1">
                            <label class="text-[10px] uppercase font-bold text-gray-400">Auto Cashout</label>
                            <input id="bet1-auto-mult" type="number" step="0.1" value="2.00" class="bg-cardBg border border-gray-700 rounded-xl px-3 py-2 text-sm font-bold text-emerald-400 focus:outline-none">
                        </div>
                    </div>

                    <div class="flex items-center justify-between text-xs text-gray-400">
                        <label class="flex items-center space-x-2 cursor-pointer">
                            <input id="bet1-auto-cash-check" type="checkbox" class="rounded bg-cardBg border-gray-700 text-emerald-500 focus:ring-0">
                            <span>Auto Cashout</span>
                        </label>
                        <label id="bet1-autobet-container" class="hidden flex items-center space-x-2 cursor-pointer">
                            <input id="bet1-autobet-check" type="checkbox" class="rounded bg-cardBg border-gray-700 text-blue-500 focus:ring-0">
                            <span>Auto Bet</span>
                        </label>
                    </div>

                    <button id="bet1-action-btn" onclick="triggerBet(1)" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-black py-3 rounded-xl shadow-lg transition text-base uppercase">
                        PLACE BET
                    </button>
                </div>

                <!-- BET PANEL 2 -->
                <div class="bg-panelBg rounded-2xl border border-gray-800 p-4 flex flex-col space-y-3 shadow-xl">
                    <div class="flex items-center justify-between">
                        <span class="font-bold text-sm text-gray-200">BET 2</span>
                        <div class="flex items-center space-x-1 bg-cardBg p-1 rounded-lg border border-gray-700 text-xs">
                            <button onclick="setTab(2, 'manual')" id="bet2-tab-manual" class="px-3 py-1 rounded-md bg-blue-600 text-white font-bold transition">Manual</button>
                            <button onclick="setTab(2, 'auto')" id="bet2-tab-auto" class="px-3 py-1 rounded-md text-gray-400 font-bold hover:text-white transition">Auto</button>
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-2">
                        <div class="flex flex-col space-y-1">
                            <label class="text-[10px] uppercase font-bold text-gray-400">Amount (KES)</label>
                            <input id="bet2-amount" type="number" value="200" class="bg-cardBg border border-gray-700 rounded-xl px-3 py-2 text-sm font-bold text-yellow-400 focus:outline-none">
                        </div>
                        <div class="flex flex-col space-y-1">
                            <label class="text-[10px] uppercase font-bold text-gray-400">Auto Cashout</label>
                            <input id="bet2-auto-mult" type="number" step="0.1" value="1.50" class="bg-cardBg border border-gray-700 rounded-xl px-3 py-2 text-sm font-bold text-emerald-400 focus:outline-none">
                        </div>
                    </div>

                    <div class="flex items-center justify-between text-xs text-gray-400">
                        <label class="flex items-center space-x-2 cursor-pointer">
                            <input id="bet2-auto-cash-check" type="checkbox" class="rounded bg-cardBg border-gray-700 text-emerald-500 focus:ring-0">
                            <span>Auto Cashout</span>
                        </label>
                        <label id="bet2-autobet-container" class="hidden flex items-center space-x-2 cursor-pointer">
                            <input id="bet2-autobet-check" type="checkbox" class="rounded bg-cardBg border-gray-700 text-blue-500 focus:ring-0">
                            <span>Auto Bet</span>
                        </label>
                    </div>

                    <button id="bet2-action-btn" onclick="triggerBet(2)" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-black py-3 rounded-xl shadow-lg transition text-base uppercase">
                        PLACE BET
                    </button>
                </div>

            </div>
        </section>

        <!-- LIVE BETS FEED -->
        <section class="lg:col-span-4 bg-panelBg rounded-2xl border border-gray-800 p-4 flex flex-col h-[520px] lg:h-auto shadow-xl">
            <div class="flex items-center justify-between pb-3 border-b border-gray-800">
                <h3 class="font-bold text-sm text-gray-200">Live Bets</h3>
                <span id="live-bets-count" class="bg-cardBg text-gray-400 border border-gray-700 px-2 py-0.5 rounded-full text-xs font-semibold">0 Bets</span>
            </div>

            <div class="grid grid-cols-3 text-[11px] font-bold text-gray-500 py-2 border-b border-gray-800 uppercase">
                <span>User</span>
                <span class="text-center">Bet</span>
                <span class="text-right">Cashout</span>
            </div>

            <div id="live-bets-list" class="flex-1 overflow-y-auto space-y-1.5 pt-2">
                <!-- Dynamically populated bets -->
            </div>
        </section>

    </main>

    <!-- PROVABLY FAIR MODAL -->
    <div id="pf-modal" class="hidden fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center p-4">
        <div class="bg-panelBg border border-gray-700 w-full max-w-lg rounded-3xl p-6 shadow-2xl flex flex-col space-y-4">
            <div class="flex items-center justify-between pb-3 border-b border-gray-800">
                <h3 class="font-black text-lg text-emerald-400">Provably Fair Seeds</h3>
                <button onclick="closeProvablyFairModal()" class="text-gray-400 hover:text-white"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div class="space-y-3 text-xs">
                <div>
                    <label class="text-gray-400 font-semibold block mb-1">Server Seed (SHA-256):</label>
                    <input id="pf-server-seed" readonly type="text" class="w-full bg-cardBg border border-gray-700 rounded-xl p-2.5 font-mono text-yellow-400">
                </div>
                <div>
                    <label class="text-gray-400 font-semibold block mb-1">Client Seed:</label>
                    <input id="pf-client-seed" readonly type="text" class="w-full bg-cardBg border border-gray-700 rounded-xl p-2.5 font-mono text-blue-400">
                </div>
                <div>
                    <label class="text-gray-400 font-semibold block mb-1">Combined Verification Hash:</label>
                    <input id="pf-hash" readonly type="text" class="w-full bg-cardBg border border-gray-700 rounded-xl p-2.5 font-mono text-emerald-400">
                </div>
            </div>
        </div>
    </div>

    <!-- ADMIN OVERRIDE MODAL -->
    <div id="admin-modal" class="hidden fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center p-4">
        <div class="bg-panelBg border border-gray-700 w-full max-w-md rounded-3xl p-6 shadow-2xl flex flex-col space-y-4">
            <div class="flex items-center justify-between pb-3 border-b border-gray-800">
                <h3 class="font-black text-lg text-yellow-400">Admin Crash Control</h3>
                <button onclick="closeAdminModal()" class="text-gray-400 hover:text-white"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div class="flex flex-col space-y-2">
                <label class="text-xs text-gray-400 font-medium">Set Target Crash Multiplier for Next Round:</label>
                <input id="admin-crash-input" type="number" step="0.01" value="2.50" class="bg-cardBg border border-gray-700 rounded-xl p-3 text-base font-bold text-yellow-400 focus:outline-none">
            </div>
            <button onclick="submitAdminOverride()" class="w-full bg-yellow-500 hover:bg-yellow-400 text-black font-black py-3 rounded-xl shadow-lg transition uppercase text-sm">
                Override Next Round Target
            </button>
        </div>
    </div>

    <!-- DEPOSIT MODAL -->
    <div id="deposit-modal" class="hidden fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center p-4">
        <div class="bg-panelBg border border-gray-700 w-full max-w-md rounded-3xl p-6 shadow-2xl flex flex-col space-y-4">
            <div class="flex items-center justify-between pb-3 border-b border-gray-800">
                <h3 class="font-black text-lg text-emerald-400">Deposit Funds</h3>
                <button onclick="closeDepositModal()" class="text-gray-400 hover:text-white"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div class="flex flex-col space-y-2">
                <label class="text-xs text-gray-400 font-medium">Amount to Deposit (KES):</label>
                <input id="deposit-amount-input" type="number" value="1000" class="bg-cardBg border border-gray-700 rounded-xl p-3 text-base font-bold text-emerald-400 focus:outline-none">
            </div>
            <button onclick="submitDeposit()" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-black py-3 rounded-xl shadow-lg transition uppercase text-sm">
                Confirm Deposit
            </button>
        </div>
    </div>

    <!-- WITHDRAW MODAL -->
    <div id="withdraw-modal" class="hidden fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center p-4">
        <div class="bg-panelBg border border-gray-700 w-full max-w-md rounded-3xl p-6 shadow-2xl flex flex-col space-y-4">
            <div class="flex items-center justify-between pb-3 border-b border-gray-800">
                <h3 class="font-black text-lg text-emerald-400">Withdraw Funds</h3>
                <button onclick="closeWithdrawModal()" class="text-gray-400 hover:text-white"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div class="flex flex-col space-y-2">
                <label class="text-xs text-gray-400 font-medium">Amount to Withdraw (KES):</label>
                <input id="withdraw-amount-input" type="number" value="1000" class="bg-cardBg border border-gray-700 rounded-xl p-3 text-base font-bold text-yellow-400 focus:outline-none">
            </div>
            <button onclick="submitWithdraw()" class="w-full bg-blue-600 hover:bg-blue-500 text-white font-black py-3 rounded-xl shadow-lg transition uppercase text-sm">
                Request Withdrawal
            </button>
        </div>
    </div>

    <!-- FRONTEND JAVASCRIPT ENGINE -->
    <script>
        let currentUser = null;
        let gameStatus = 'WAITING';
        let currentBetState = { 1: null, 2: null };

        // CANVAS ENGINE
        const canvas = document.getElementById('flight-canvas');
        const ctx = canvas.getContext('2d');

        function resizeCanvas() {
            canvas.width = canvas.parentElement.clientWidth;
            canvas.height = canvas.parentElement.clientHeight;
        }
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        function drawFlightCurve(multiplier) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            if (gameStatus !== 'FLYING' && gameStatus !== 'CRASHED') return;

            const w = canvas.width;
            const h = canvas.height;

            const progress = Math.min((multiplier - 1.0) / 10.0, 1.0);
            const targetX = w * 0.15 + (w * 0.7) * progress;
            const targetY = h * 0.85 - (h * 0.65) * progress;

            ctx.beginPath();
            ctx.moveTo(w * 0.1, h * 0.9);
            ctx.quadraticCurveTo(targetX * 0.5, h * 0.9, targetX, targetY);
            ctx.lineWidth = 4;
            ctx.strokeStyle = gameStatus === 'CRASHED' ? '#e53e3e' : '#ecc94b';
            ctx.stroke();

            // Gradient Fill
            ctx.lineTo(targetX, h * 0.9);
            ctx.lineTo(w * 0.1, h * 0.9);
            const grad = ctx.createLinearGradient(0, targetY, 0, h * 0.9);
            grad.addColorStop(0, gameStatus === 'CRASHED' ? 'rgba(229, 62, 62, 0.3)' : 'rgba(236, 201, 75, 0.3)');
            grad.addColorStop(1, 'transparent');
            ctx.fillStyle = grad;
            ctx.fill();
        }

        // POLLING LOOP
        async function fetchState() {
            try {
                const res = await fetch('/api/state');
                const data = await res.json();
                if (!data.success) return;

                if (data.user && data.user.name !== 'Player') {
                    currentUser = data.user;
                    document.getElementById('auth-modal').classList.add('hidden');
                    document.getElementById('header-user-tag').innerText = `Welcome, ${data.user.name}`;
                    document.getElementById('user-balance').innerText = `${data.user.balance.toFixed(2)} KES`;
                    
                    if (data.user.isAdmin) {
                        document.getElementById('admin-menu-btn').classList.remove('hidden');
                    }
                }

                updateGameUI(data.game);
                updateUserBetsUI(data.userBets);
            } catch (err) {
                console.error("State sync error:", err);
            }
        }

        function updateGameUI(game) {
            gameStatus = game.status;

            // Update Multiplier Display
            const multDisplay = document.getElementById('multiplier-display');
            const statusText = document.getElementById('flight-status-text');

            if (game.status === 'WAITING') {
                multDisplay.innerText = '1.00x';
                multDisplay.className = 'text-5xl sm:text-7xl font-black text-yellow-400';
                statusText.innerText = 'WAITING FOR NEXT ROUND';
                statusText.className = 'mt-2 text-sm sm:text-lg font-bold uppercase tracking-widest text-emerald-400 bg-emerald-950/60 px-4 py-1.5 rounded-full border border-emerald-800/50 shadow';
                ctx.clearRect(0, 0, canvas.width, canvas.height);
            } else if (game.status === 'FLYING') {
                multDisplay.innerText = `${game.currentMultiplier.toFixed(2)}x`;
                multDisplay.className = 'text-5xl sm:text-7xl font-black flight-glow text-yellow-400';
                statusText.innerText = 'FLEW AWAY...';
                statusText.className = 'mt-2 text-sm sm:text-lg font-bold uppercase tracking-widest text-yellow-400 bg-yellow-950/60 px-4 py-1.5 rounded-full border border-yellow-800/50 shadow hidden';
                drawFlightCurve(game.currentMultiplier);
            } else if (game.status === 'CRASHED') {
                multDisplay.innerText = `${game.crashPoint.toFixed(2)}x`;
                multDisplay.className = 'text-5xl sm:text-7xl font-black text-red-500';
                statusText.innerText = 'FLEW AWAY!';
                statusText.className = 'mt-2 text-sm sm:text-lg font-bold uppercase tracking-widest text-red-400 bg-red-950/60 px-4 py-1.5 rounded-full border border-red-800/50 shadow';
                drawFlightCurve(game.crashPoint);
            }

            // Update Provably Fair Modal Inputs
            document.getElementById('pf-server-seed').value = game.serverSeed || '';
            document.getElementById('pf-client-seed').value = game.clientSeed || '';
            document.getElementById('pf-hash').value = game.hash || '';

            // Render History
            const historyBar = document.getElementById('history-bar');
            historyBar.innerHTML = '<span class="text-xs text-gray-500 font-semibold uppercase tracking-wider mr-1">History:</span>';
            game.history.slice().reverse().forEach(val => {
                const tag = document.createElement('span');
                tag.className = `px-2 py-0.5 rounded-lg text-xs font-bold ${val >= 2.0 ? 'bg-blue-900/60 text-blue-300 border border-blue-700/50' : 'bg-red-900/60 text-red-300 border border-red-700/50'}`;
                tag.innerText = `${val.toFixed(2)}x`;
                historyBar.appendChild(tag);
            });

            // Render Live Bot Bets
            const list = document.getElementById('live-bets-list');
            list.innerHTML = '';
            document.getElementById('live-bets-count').innerText = `${game.botBets.length} Bets`;

            game.botBets.forEach(bot => {
                const row = document.createElement('div');
                row.className = 'grid grid-cols-3 text-xs py-1.5 border-b border-gray-800/50 items-center';
                
                const userCol = `<span class="text-gray-300 font-medium">${bot.username}</span>`;
                const betCol = `<span class="text-center font-bold text-yellow-400">${bot.amount} KES</span>`;
                let cashCol = `<span class="text-right text-gray-500 font-semibold">-</span>`;

                if (bot.cashedOut) {
                    cashCol = `<span class="text-right text-emerald-400 font-bold">${bot.cashoutAmount} KES (${bot.cashout_multiplier}x)</span>`;
                } else if (game.status === 'CRASHED') {
                    cashCol = `<span class="text-right text-red-400 font-bold">Crashed</span>`;
                }

                row.innerHTML = userCol + betCol + cashCol;
                list.appendChild(row);
            });
        }

        function updateUserBetsUI(bets) {
            [1, 2].forEach(num => {
                const bet = bets.find(b => b.betNumber === num);
                const btn = document.getElementById(`bet${num}-action-btn`);

                if (bet && bet.active) {
                    if (gameStatus === 'FLYING') {
                        btn.innerText = 'CASHOUT';
                        btn.className = 'w-full bg-yellow-500 hover:bg-yellow-400 text-black font-black py-3 rounded-xl shadow-lg transition text-base uppercase animate-pulse';
                    } else {
                        btn.innerText = 'CANCEL BET';
                        btn.className = 'w-full bg-red-600 hover:bg-red-500 text-white font-black py-3 rounded-xl shadow-lg transition text-base uppercase';
                    }
                } else {
                    btn.innerText = 'PLACE BET';
                    btn.className = 'w-full bg-emerald-600 hover:bg-emerald-500 text-white font-black py-3 rounded-xl shadow-lg transition text-base uppercase';
                }
            });
        }

        // ACTIONS
        async function triggerBet(num) {
            const btn = document.getElementById(`bet${num}-action-btn`);
            const amount = parseFloat(document.getElementById(`bet${num}-amount`).value);
            const autoEnabled = document.getElementById(`bet${num}-auto-cash-check`).checked;
            const autoMult = parseFloat(document.getElementById(`bet${num}-auto-mult`).value);
            const autoBet = document.getElementById(`bet${num}-autobet-check`).checked;

            if (btn.innerText === 'CASHOUT') {
                const res = await fetch('/api/cashout', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ betNumber: num })
                });
                const data = await res.json();
                if (data.success) fetchState();
            } else {
                const res = await fetch('/api/bet', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        betNumber: num,
                        amount: amount,
                        autoEnabled: autoEnabled,
                        autoMultiplier: autoMult,
                        autoBet: autoBet
                    })
                });
                const data = await res.json();
                if (data.success) fetchState();
            }
        }

        function setTab(num, mode) {
            const container = document.getElementById(`bet${num}-autobet-container`);
            const btnManual = document.getElementById(`bet${num}-tab-manual`);
            const btnAuto = document.getElementById(`bet${num}-tab-auto`);

            if (mode === 'auto') {
                container.classList.remove('hidden');
                btnAuto.className = 'px-3 py-1 rounded-md bg-blue-600 text-white font-bold transition';
                btnManual.className = 'px-3 py-1 rounded-md text-gray-400 font-bold hover:text-white transition';
            } else {
                container.classList.add('hidden');
                btnManual.className = 'px-3 py-1 rounded-md bg-blue-600 text-white font-bold transition';
                btnAuto.className = 'px-3 py-1 rounded-md text-gray-400 font-bold hover:text-white transition';
            }
        }

        // AUTH & MODALS
        function switchAuthTab(tab) {
            if (tab === 'login') {
                document.getElementById('form-login').classList.remove('hidden');
                document.getElementById('form-register').classList.add('hidden');
                document.getElementById('auth-tab-login').className = 'py-2.5 rounded-lg bg-blue-600 text-white transition';
                document.getElementById('auth-tab-register').className = 'py-2.5 rounded-lg text-gray-400 hover:text-white transition';
            } else {
                document.getElementById('form-register').classList.remove('hidden');
                document.getElementById('form-login').classList.add('hidden');
                document.getElementById('auth-tab-register').className = 'py-2.5 rounded-lg bg-blue-600 text-white transition';
                document.getElementById('auth-tab-login').className = 'py-2.5 rounded-lg text-gray-400 hover:text-white transition';
            }
        }

        async function submitLogin() {
            const user = document.getElementById('login-user').value;
            const pass = document.getElementById('login-pass').value;
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ user, pass })
            });
            const data = await res.json();
            if (data.success) fetchState();
        }

        async function submitRegister() {
            const name = document.getElementById('reg-name').value;
            const phone = document.getElementById('reg-phone').value;
            const pass = document.getElementById('reg-pass').value;
            const res = await fetch('/api/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ name, phone, pass })
            });
            const data = await res.json();
            if (data.success) fetchState();
        }

        async function logoutUser() {
            await fetch('/api/logout', { method: 'POST' });
            window.location.reload();
        }

        function toggleMenu() {
            document.getElementById('dropdown-menu').classList.toggle('hidden');
        }

        function openProvablyFairModal() {
            document.getElementById('pf-modal').classList.remove('hidden');
            toggleMenu();
        }
        function closeProvablyFairModal() {
            document.getElementById('pf-modal').classList.add('hidden');
        }

        function openAdminModal() {
            document.getElementById('admin-modal').classList.remove('hidden');
            toggleMenu();
        }
        function closeAdminModal() {
            document.getElementById('admin-modal').classList.add('hidden');
        }

        async function submitAdminOverride() {
            const mult = parseFloat(document.getElementById('admin-crash-input').value);
            await fetch('/api/admin/override', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ multiplier: mult })
            });
            closeAdminModal();
        }

        function openDepositModal() {
            document.getElementById('deposit-modal').classList.remove('hidden');
        }
        function closeDepositModal() {
            document.getElementById('deposit-modal').classList.add('hidden');
        }

        async function submitDeposit() {
            const amount = parseFloat(document.getElementById('deposit-amount-input').value);
            await fetch('/api/deposit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ amount })
            });
            closeDepositModal();
            fetchState();
        }

        function openWithdrawModal() {
            document.getElementById('withdraw-modal').classList.remove('hidden');
        }
        function closeWithdrawModal() {
            document.getElementById('withdraw-modal').classList.add('hidden');
        }

        async function submitWithdraw() {
            const amount = parseFloat(document.getElementById('withdraw-amount-input').value);
            await fetch('/api/withdraw', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ amount })
            });
            closeWithdrawModal();
            fetchState();
        }

        // Start Sync Loop
        setInterval(fetchState, 150);
        fetchState();
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)





