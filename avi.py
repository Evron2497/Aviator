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




<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aviator Flight Game</title>
    <!-- Tailwind CSS CDN -->
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
    <!-- FontAwesome for Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #0b0e14;
            color: #f7fafc;
            overflow-x: hidden;
        }
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #121824;
        }
        ::-webkit-scrollbar-thumb {
            background: #2a374d;
            border-radius: 3px;
        }
        .flight-glow {
            text-shadow: 0 0 25px rgba(236, 201, 75, 0.6);
        }
    </style>
</head>
<body class="min-h-screen flex flex-col justify-between bg-darkBg text-white">

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

            <!-- TAB SWITCHER -->
            <div class="grid grid-cols-2 bg-cardBg p-1 rounded-xl border border-gray-700 text-xs font-bold">
                <button onclick="switchAuthTab('login')" id="auth-tab-login" class="py-2.5 rounded-lg bg-blue-600 text-white transition">Login</button>
                <button onclick="switchAuthTab('register')" id="auth-tab-register" class="py-2.5 rounded-lg text-gray-400 hover:text-white transition">Register</button>
            </div>

            <!-- LOGIN FORM -->
            <div id="form-login" class="flex flex-col space-y-4">
                <div class="flex flex-col space-y-1">
                    <label class="text-xs text-gray-400 font-medium">Username or Phone Number:</label>
                    <input id="login-user" type="text" placeholder="e.g. 0712345678 or admin" class="bg-cardBg border border-gray-700 rounded-xl px-3 py-2.5 text-xs text-white focus:outline-none">
                </div>
                <div class="flex flex-col space-y-1">
                    <label class="text-xs text-gray-400 font-medium">Password:</label>
                    <input id="login-pass" type="password" placeholder="••••••••" class="bg-cardBg border border-gray-700 rounded-xl px-3 py-2.5 text-xs text-white focus:outline-none">
                </div>
                <div class="flex justify-end">
                    <button onclick="switchAuthTab('forgot')" class="text-xs text-blue-400 hover:underline">Forgot Password?</button>
                </div>
                <button onclick="submitLogin()" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3 rounded-xl shadow-lg transition text-sm uppercase">
                    Login to Flight
                </button>
            </div>

            <!-- REGISTER FORM -->
            <div id="form-register" class="flex flex-col space-y-4 hidden">
                <div class="flex flex-col space-y-1">
                    <label class="text-xs text-gray-400 font-medium">Full Name:</label>
                    <input id="reg-name" type="text" placeholder="John Doe" class="bg-cardBg border border-gray-700 rounded-xl px-3 py-2.5 text-xs text-white focus:outline-none">
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

            <!-- FORGOT PASSWORD FORM (USSD) -->
            <div id="form-forgot" class="flex flex-col space-y-4 hidden">
                <div class="flex flex-col space-y-1">
                    <label class="text-xs text-gray-400 font-medium">Enter Registered Phone Number:</label>
                    <input id="forgot-phone" type="text" placeholder="+254 712 345 678" class="bg-cardBg border border-gray-700 rounded-xl px-3 py-2.5 text-xs text-white focus:outline-none">
                </div>
                <button onclick="requestUssdReset()" class="w-full bg-purple-600 hover:bg-purple-500 text-white font-bold py-3 rounded-xl shadow-lg transition text-sm uppercase">
                    Send USSD Reset Code
                </button>
                <div id="ussd-simulation-box" class="hidden bg-cardBg border border-purple-800/60 p-3 rounded-xl text-xs space-y-2">
                    <div class="font-bold text-purple-300"><i class="fa-solid fa-mobile-screen"></i> USSD Gateway Simulator</div>
                    <div id="ussd-message-text" class="text-gray-300 font-mono bg-black/40 p-2 rounded border border-gray-800"></div>
                    <div class="flex space-x-2">
                        <input id="ussd-input-pin" type="text" placeholder="Enter new password" class="w-full bg-gray-900 border border-gray-700 px-2 py-1.5 rounded text-white">
                        <button onclick="confirmUssdReset()" class="bg-emerald-600 hover:bg-emerald-500 px-3 py-1.5 rounded font-bold text-white">Confirm</button>
                    </div>
                </div>
                <div class="flex justify-center">
                    <button onclick="switchAuthTab('login')" class="text-xs text-gray-400 hover:text-white"><i class="fa-solid fa-arrow-left"></i> Back to Login</button>
                </div>
            </div>
        </div>
    </div>

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
            <!-- Hamburger Menu Button -->
            <button onclick="toggleMenu()" class="bg-cardBg hover:bg-gray-700 border border-gray-700 p-2.5 rounded-xl text-gray-300 transition shadow">
                <i class="fa-solid fa-bars"></i>
            </button>
        </div>

        <!-- Dropdown Menu -->
        <div id="dropdown-menu" class="hidden absolute top-16 right-4 w-64 bg-panelBg border border-gray-700 rounded-2xl shadow-2xl p-3 flex flex-col space-y-2 z-50">
            <div class="flex items-center justify-between pb-2 border-b border-gray-800">
                <span class="font-bold text-sm text-gray-200">Menu</span>
                <button onclick="toggleMenu()" class="text-gray-400 hover:text-white"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <button onclick="openProfileModal()" class="flex items-center space-x-3 px-3 py-2.5 rounded-xl hover:bg-cardBg text-gray-300 transition text-sm font-medium">
                <i class="fa-solid fa-user text-blue-400 w-5"></i>
                <span>Profile & Stats</span>
            </button>
            <button onclick="openWithdrawModal()" class="flex items-center space-x-3 px-3 py-2.5 rounded-xl hover:bg-cardBg text-gray-300 transition text-sm font-medium">
                <i class="fa-solid fa-wallet text-emerald-400 w-5"></i>
                <span>Withdraw Funds</span>
            </button>
            <button id="admin-menu-btn" onclick="openAdminModal()" class="hidden flex items-center space-x-3 px-3 py-2.5 rounded-xl hover:bg-cardBg text-yellow-400 transition text-sm font-bold border border-yellow-800/40">
                <i class="fa-solid fa-shield-halved w-5"></i>
                <span>Admin Dashboard</span>
            </button>
            <div class="flex items-center justify-between px-3 py-2.5 rounded-xl hover:bg-cardBg text-gray-300 text-sm font-medium">
                <div class="flex items-center space-x-3">
                    <i class="fa-solid fa-volume-high text-yellow-400 w-5"></i>
                    <span>Sound Effects</span>
                </div>
                <input type="checkbox" id="sound-toggle" checked onchange="toggleSound()" class="accent-blue-600 w-4 h-4 cursor-pointer">
            </div>
            <div class="flex items-center justify-between px-3 py-2.5 rounded-xl hover:bg-cardBg text-gray-300 text-sm font-medium">
                <div class="flex items-center space-x-3">
                    <i class="fa-solid fa-music text-purple-400 w-5"></i>
                    <span>Flight Music</span>
                </div>
                <input type="checkbox" id="music-toggle" checked onchange="toggleMusic()" class="accent-blue-600 w-4 h-4 cursor-pointer">
            </div>
            <button onclick="logoutUser()" class="flex items-center space-x-3 px-3 py-2.5 rounded-xl hover:bg-red-950/40 text-red-400 transition text-sm font-medium border-t border-gray-800 mt-2">
                <i class="fa-solid fa-right-from-bracket w-5"></i>
                <span>Logout</span>
            </button>
        </div>
    </header>

    <main class="flex-1 max-w-7xl w-full mx-auto p-2 sm:p-4 grid grid-cols-1 lg:grid-cols-12 gap-4">
        
        <!-- Main Flight Area & Multiplier Display (Takes 8 cols on large screens) -->
        <section class="lg:col-span-8 flex flex-col space-y-4">
            
            <!-- Multiplier History Bar -->
            <div id="history-bar" class="bg-panelBg rounded-xl border border-gray-800 px-3 py-2 flex items-center space-x-2 overflow-x-auto whitespace-nowrap shadow-md">
                <span class="text-xs text-gray-500 font-semibold uppercase tracking-wider mr-1">History:</span>
                <!-- Multipliers injected here -->
            </div>

            <!-- Canvas Flight Arena -->
            <div class="relative bg-gradient-to-b from-panelBg via-cardBg to-panelBg rounded-2xl border border-gray-800 h-[300px] sm:h-[380px] flex flex-col items-center justify-center overflow-hidden shadow-2xl">
                <!-- Grid pattern background overlay -->
                <div class="absolute inset-0 opacity-10 bg-[radial-gradient(#e53e3e_1px,transparent_1px)] [background-size:16px_16px]"></div>

                <!-- Canvas for Flight Curve Animation -->
                <canvas id="flight-canvas" class="absolute inset-0 w-full h-full z-0"></canvas>

                <!-- Center Game Status Message / Multiplier -->
                <div id="game-status-container" class="z-10 flex flex-col items-center justify-center text-center p-4">
                    <div id="multiplier-display" class="text-5xl sm:text-7xl font-black flight-glow text-yellow-400 tracking-tight transition-all duration-75">
                        1.00x
                    </div>
                    <div id="flight-status-text" class="mt-2 text-sm sm:text-lg font-bold uppercase tracking-widest text-emerald-400 bg-emerald-950/60 px-4 py-1.5 rounded-full border border-emerald-800/50 shadow">
                        WAITING FOR NEXT ROUND
                    </div>
                </div>

                <!-- Airplane Icon/Animation indicator -->
                <div id="airplane-indicator" class="absolute z-20 text-yellow-400 text-3xl sm:text-4xl transition-all duration-75 hidden">
                    <i class="fa-solid fa-plane animate-bounce"></i>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                
                <!-- BET PANEL 1 -->
                <div class="bg-panelBg rounded-2xl border border-gray-800 p-4 flex flex-col space-y-3 shadow-xl">
                    <div class="flex items-center justify-between">
                        <span class="font-bold text-sm text-gray-200">BET 1</span>
                        <div class="flex items-center space-x-1 bg-cardBg p-1 rounded-lg border border-gray-700 text-xs">
                            <button onclick="setTab('bet1', 'manual')" id="bet1-tab-manual" class="px-3 py-1 rounded-md bg-blue-600 text-white font-semibold transition">Manual</button>
                            <button onclick="setTab('bet1', 'auto')" id="bet1-tab-auto" class="px-3 py-1 rounded-md text-gray-400 hover:text-white transition">Auto</button>
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-3">
                        <!-- Amount Control -->
                        <div class="flex flex-col space-y-1">
                            <div class="flex justify-between text-xs text-gray-400 font-medium">
                                <span>Amount (KES)</span>
                                <span class="cursor-pointer text-blue-400 hover:underline" onclick="adjustBet('bet1', 100)">+100</span>
                            </div>
                            <div class="flex items-center bg-cardBg rounded-xl border border-gray-700 overflow-hidden px-3 py-2">
                                <button onclick="changeBetAmount('bet1', -10)" class="text-gray-400 hover:text-white px-1 font-bold"><i class="fa-solid fa-minus text-xs"></i></button>
                                <input id="bet1-amount" type="number" value="10.00" min="10" step="10" class="w-full bg-transparent text-center font-bold text-white focus:outline-none text-sm">
                                <button onclick="changeBetAmount('bet1', 10)" class="text-gray-400 hover:text-white px-1 font-bold"><i class="fa-solid fa-plus text-xs"></i></button>
                            </div>
                        </div>

                        <!-- Auto Cashout Control -->
                        <div class="flex flex-col space-y-1">
                            <div class="flex items-center justify-between text-xs text-gray-400 font-medium">
                                <span>Auto Cash Out</span>
                                <input type="checkbox" id="bet1-auto-enabled" class="accent-blue-600 rounded cursor-pointer">
                            </div>
                            <div class="flex items-center bg-cardBg rounded-xl border border-gray-700 overflow-hidden px-3 py-2">
                                <input id="bet1-auto-multiplier" type="number" value="2.00" min="1.01" step="0.1" class="w-full bg-transparent text-center font-bold text-white focus:outline-none text-sm">
                                <span class="text-xs text-gray-500 font-semibold pr-1">x</span>
                            </div>
                        </div>
                    </div>

                    <!-- Quick Preset Buttons -->
                    <div class="grid grid-cols-4 gap-1.5 pt-1">
                        <button onclick="setPresetBet('bet1', 50)" class="bg-cardBg hover:bg-gray-700/60 text-xs py-1.5 rounded-lg font-semibold border border-gray-700 text-gray-300 transition">50</button>
                        <button onclick="setPresetBet('bet1', 100)" class="bg-cardBg hover:bg-gray-700/60 text-xs py-1.5 rounded-lg font-semibold border border-gray-700 text-gray-300 transition">100</button>
                        <button onclick="setPresetBet('bet1', 500)" class="bg-cardBg hover:bg-gray-700/60 text-xs py-1.5 rounded-lg font-semibold border border-gray-700 text-gray-300 transition">500</button>
                        <button onclick="setPresetBet('bet1', 1000)" class="bg-cardBg hover:bg-gray-700/60 text-xs py-1.5 rounded-lg font-semibold border border-gray-700 text-gray-300 transition">1000</button>
                    </div>

                    <!-- Action Button 1 (Green top / Red bottom styling requested) -->
                    <div class="flex flex-col space-y-1">
                        <div class="text-[10px] text-emerald-400 font-bold uppercase tracking-wider text-center">Secure Entry</div>
                        <button id="bet1-action-btn" onclick="handleBetClick(1)" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3.5 rounded-xl shadow-lg transition tracking-wide text-sm flex items-center justify-center space-x-2 uppercase">
                            <span>BET</span>
                        </button>
                        <div class="text-[10px] text-red-400 font-bold uppercase tracking-wider text-center">High Risk Exit</div>
                    </div>
                    <div id="bet1-live-win" class="hidden text-center text-xs text-yellow-400 font-bold bg-yellow-950/40 py-1.5 rounded-lg border border-yellow-800/40">
                        Live Winnings: <span id="bet1-win-amount">0.00</span> KES (<span id="bet1-live-mult">1.00x</span>)
                    </div>
                </div>

                <!-- BET PANEL 2 -->
                <div class="bg-panelBg rounded-2xl border border-gray-800 p-4 flex flex-col space-y-3 shadow-xl">
                    <div class="flex items-center justify-between">
                        <span class="font-bold text-sm text-gray-200">BET 2</span>
                        <div class="flex items-center space-x-1 bg-cardBg p-1 rounded-lg border border-gray-700 text-xs">
                            <button onclick="setTab('bet2', 'manual')" id="bet2-tab-manual" class="px-3 py-1 rounded-md bg-blue-600 text-white font-semibold transition">Manual</button>
                            <button onclick="setTab('bet2', 'auto')" id="bet2-tab-auto" class="px-3 py-1 rounded-md text-gray-400 hover:text-white transition">Auto</button>
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-3">
                        <!-- Amount Control -->
                        <div class="flex flex-col space-y-1">
                            <div class="flex justify-between text-xs text-gray-400 font-medium">
                                <span>Amount (KES)</span>
                                <span class="cursor-pointer text-blue-400 hover:underline" onclick="adjustBet('bet2', 100)">+100</span>
                            </div>
                            <div class="flex items-center bg-cardBg rounded-xl border border-gray-700 overflow-hidden px-3 py-2">
                                <button onclick="changeBetAmount('bet2', -10)" class="text-gray-400 hover:text-white px-1 font-bold"><i class="fa-solid fa-minus text-xs"></i></button>
                                <input id="bet2-amount" type="number" value="10.00" min="10" step="10" class="w-full bg-transparent text-center font-bold text-white focus:outline-none text-sm">
                                <button onclick="changeBetAmount('bet2', 10)" class="text-gray-400 hover:text-white px-1 font-bold"><i class="fa-solid fa-plus text-xs"></i></button>
                            </div>
                        </div>

                        <!-- Auto Cashout Control -->
                        <div class="flex flex-col space-y-1">
                            <div class="flex items-center justify-between text-xs text-gray-400 font-medium">
                                <span>Auto Cash Out</span>
                                <input type="checkbox" id="bet2-auto-enabled" class="accent-blue-600 rounded cursor-pointer">
                            </div>
                            <div class="flex items-center bg-cardBg rounded-xl border border-gray-700 overflow-hidden px-3 py-2">
                                <input id="bet2-auto-multiplier" type="number" value="2.00" min="1.01" step="0.1" class="w-full bg-transparent text-center font-bold text-white focus:outline-none text-sm">
                                <span class="text-xs text-gray-500 font-semibold pr-1">x</span>
                            </div>
                        </div>
                    </div>

                    <!-- Quick Preset Buttons -->
                    <div class="grid grid-cols-4 gap-1.5 pt-1">
                        <button onclick="setPresetBet('bet2', 50)" class="bg-cardBg hover:bg-gray-700/60 text-xs py-1.5 rounded-lg font-semibold border border-gray-700 text-gray-300 transition">50</button>
                        <button onclick="setPresetBet('bet2', 100)" class="bg-cardBg hover:bg-gray-700/60 text-xs py-1.5 rounded-lg font-semibold border border-gray-700 text-gray-300 transition">100</button>
                        <button onclick="setPresetBet('bet2', 500)" class="bg-cardBg hover:bg-gray-700/60 text-xs py-1.5 rounded-lg font-semibold border border-gray-700 text-gray-300 transition">500</button>
                        <button onclick="setPresetBet('bet2', 1000)" class="bg-cardBg hover:bg-gray-700/60 text-xs py-1.5 rounded-lg font-semibold border border-gray-700 text-gray-300 transition">1000</button>
                    </div>

                    <!-- Action Button 2 (Green top / Red bottom styling requested) -->
                    <div class="flex flex-col space-y-1">
                        <div class="text-[10px] text-emerald-400 font-bold uppercase tracking-wider text-center">Secure Entry</div>
                        <button id="bet2-action-btn" onclick="handleBetClick(2)" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3.5 rounded-xl shadow-lg transition tracking-wide text-sm flex items-center justify-center space-x-2 uppercase">
                            <span>BET</span>
                        </button>
                        <div class="text-[10px] text-red-400 font-bold uppercase tracking-wider text-center">High Risk Exit</div>
                    </div>
                    <div id="bet2-live-win" class="hidden text-center text-xs text-yellow-400 font-bold bg-yellow-950/40 py-1.5 rounded-lg border border-yellow-800/40">
                        Live Winnings: <span id="bet2-win-amount">0.00</span> KES (<span id="bet2-live-mult">1.00x</span>)
                    </div>
                </div>

            </div>

        </section>

        <!-- Live Players & User Bets Sidebar -->
        <section class="lg:col-span-4 bg-panelBg rounded-2xl border border-gray-800 p-4 flex flex-col h-[350px] lg:h-auto shadow-xl">
            <div class="flex items-center justify-between pb-3 border-b border-gray-800">
                <h2 class="font-bold text-sm uppercase tracking-wider text-gray-300 flex items-center space-x-2">
                    <i class="fa-solid fa-users text-blue-400"></i>
                    <span>All Bets & Players</span>
                </h2>
                <span id="live-count" class="bg-blue-900/60 text-blue-300 text-xs px-2 py-0.5 rounded-full font-semibold">42 Online</span>
            </div>
            
            <!-- Player Bets Feed Header -->
            <div class="grid grid-cols-3 text-xs text-gray-400 font-semibold py-2 border-b border-gray-800/50">
                <span>User</span>
                <span class="text-center">Bet (KES)</span>
                <span class="text-right">Cashed Out</span>
            </div>

            <!-- Scrollable Player List -->
            <div id="live-players-list" class="flex-1 overflow-y-auto space-y-2 py-2 pr-1 text-xs">
                <!-- Dynamically populated -->
            </div>
        </section>

    </main>

    <!-- Deposit Modal with Prompt Link -->
    <div id="deposit-modal" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-panelBg border border-gray-700 w-full max-w-md rounded-2xl p-6 shadow-2xl flex flex-col space-y-4">
            <div class="flex items-center justify-between pb-3 border-b border-gray-800">
                <h3 class="font-bold text-base text-white flex items-center space-x-2">
                    <i class="fa-solid fa-wallet text-emerald-400"></i>
                    <span>Deposit Funds (KES)</span>
                </h3>
                <button onclick="closeDepositModal()" class="text-gray-400 hover:text-white"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div class="flex flex-col space-y-2">
                <label class="text-xs text-gray-400 font-medium">Paste Payment Prompt Link / M-PESA Code:</label>
                <input id="deposit-prompt-link" type="text" placeholder="https://pay.gateway.com/prompt/... or QG89XYZ123" class="bg-cardBg border border-gray-700 rounded-xl px-3 py-2.5 text-xs text-white focus:outline-none font-mono">
            </div>
            <div class="flex flex-col space-y-2">
                <label class="text-xs text-gray-400 font-medium">Amount to Deposit (KES):</label>
                <input id="deposit-amount-input" type="number" value="1000" min="100" step="100" class="bg-cardBg border border-gray-700 rounded-xl px-3 py-2.5 text-sm font-bold text-white focus:outline-none">
            </div>
            <div class="grid grid-cols-3 gap-2">
                <button onclick="setDepositAmount(500)" class="bg-cardBg hover:bg-gray-700 border border-gray-700 py-1.5 rounded-lg text-xs font-semibold">500</button>
                <button onclick="setDepositAmount(1000)" class="bg-cardBg hover:bg-gray-700 border border-gray-700 py-1.5 rounded-lg text-xs font-semibold">1,000</button>
                <button onclick="setDepositAmount(5000)" class="bg-cardBg hover:bg-gray-700 border border-gray-700 py-1.5 rounded-lg text-xs font-semibold">5,000</button>
            </div>
            <button onclick="submitDeposit()" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3 rounded-xl shadow-lg transition text-sm uppercase">
                Confirm & Deposit
            </button>
        </div>
    </div>

    <!-- Withdraw Modal -->
    <div id="withdraw-modal" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-panelBg border border-gray-700 w-full max-w-md rounded-2xl p-6 shadow-2xl flex flex-col space-y-4">
            <div class="flex items-center justify-between pb-3 border-b border-gray-800">
                <h3 class="font-bold text-base text-white flex items-center space-x-2">
                    <i class="fa-solid fa-money-bill-transfer text-blue-400"></i>
                    <span>Withdraw Funds (KES)</span>
                </h3>
                <button onclick="closeWithdrawModal()" class="text-gray-400 hover:text-white"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div class="flex flex-col space-y-2">
                <label class="text-xs text-gray-400 font-medium">M-PESA Phone Number:</label>
                <input id="withdraw-phone" type="text" value="+254 712 345 678" class="bg-cardBg border border-gray-700 rounded-xl px-3 py-2.5 text-xs text-white focus:outline-none font-mono">
            </div>
            <div class="flex flex-col space-y-2">
                <label class="text-xs text-gray-400 font-medium">Withdrawal Amount (KES):</label>
                <input id="withdraw-amount-input" type="number" value="1000" min="100" class="bg-cardBg border border-gray-700 rounded-xl px-3 py-2.5 text-sm font-bold text-white focus:outline-none">
            </div>
            <button onclick="submitWithdraw()" class="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-xl shadow-lg transition text-sm uppercase">
                Proceed Withdrawal
            </button>
        </div>
    </div>

    <!-- Profile Modal -->
    <div id="profile-modal" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-panelBg border border-gray-700 w-full max-w-md rounded-2xl p-6 shadow-2xl flex flex-col space-y-4">
            <div class="flex items-center justify-between pb-3 border-b border-gray-800">
                <h3 class="font-bold text-base text-white flex items-center space-x-2">
                    <i class="fa-solid fa-user-gear text-yellow-400"></i>
                    <span>User Profile & Statistics</span>
                </h3>
                <button onclick="closeProfileModal()" class="text-gray-400 hover:text-white"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div class="grid grid-cols-2 gap-3 text-xs">
                <div class="bg-cardBg p-3 rounded-xl border border-gray-700">
                    <div class="text-gray-400">Total Wagered</div>
                    <div id="stat-wagered" class="text-sm font-bold text-white mt-1">0.00 KES</div>
                </div>
                <div class="bg-cardBg p-3 rounded-xl border border-gray-700">
                    <div class="text-gray-400">Total Won</div>
                    <div id="stat-won" class="text-sm font-bold text-emerald-400 mt-1">0.00 KES</div>
                </div>
                <div class="bg-cardBg p-3 rounded-xl border border-gray-700">
                    <div class="text-gray-400">Rounds Played</div>
                    <div id="stat-rounds" class="text-sm font-bold text-white mt-1">0</div>
                </div>
                <div class="bg-cardBg p-3 rounded-xl border border-gray-700">
                    <div class="text-gray-400">Highest Multiplier</div>
                    <div id="stat-highest" class="text-sm font-bold text-yellow-400 mt-1">1.00x</div>
                </div>
            </div>
            <button onclick="closeProfileModal()" class="w-full bg-gray-700 hover:bg-gray-600 text-white font-bold py-2.5 rounded-xl transition text-xs uppercase">
                Close
            </button>
        </div>
    </div>

    <!-- Admin Dashboard Modal (Next 2 rounds preview) -->
    <div id="admin-modal" class="fixed inset-0 bg-black/80 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
        <div class="bg-panelBg border border-yellow-600/60 w-full max-w-lg rounded-3xl p-6 shadow-2xl flex flex-col space-y-5">
            <div class="flex items-center justify-between pb-3 border-b border-gray-800">
                <h3 class="font-black text-base text-yellow-400 flex items-center space-x-2">
                    <i class="fa-solid fa-shield-halved"></i>
                    <span>Admin Control Dashboard</span>
                </h3>
                <button onclick="closeAdminModal()" class="text-gray-400 hover:text-white"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div class="bg-cardBg p-4 rounded-2xl border border-yellow-800/40 space-y-3">
                <div class="text-xs text-yellow-300 font-bold uppercase tracking-wider"><i class="fa-solid fa-eye"></i> Upcoming Flight Multiplier Previews:</div>
                <div class="grid grid-cols-2 gap-3 text-center">
                    <div class="bg-black/40 p-3 rounded-xl border border-gray-800">
                        <div class="text-xs text-gray-400">Next Round (Round +1)</div>
                        <div id="admin-preview-1" class="text-xl font-black text-yellow-400 mt-1">--</div>
                    </div>
                    <div class="bg-black/40 p-3 rounded-xl border border-gray-800">
                        <div class="text-xs text-gray-400">Following Round (Round +2)</div>
                        <div id="admin-preview-2" class="text-xl font-black text-yellow-400 mt-1">--</div>
                    </div>
                </div>
            </div>
            <div class="flex flex-col space-y-2">
                <label class="text-xs text-gray-400 font-medium">Override Next Multiplier (Admin Control):</label>
                <div class="flex space-x-2">
                    <input id="admin-override-val" type="number" step="0.1" placeholder="e.g. 5.00" class="w-full bg-cardBg border border-gray-700 rounded-xl px-3 py-2 text-xs text-white">
                    <button onclick="applyAdminOverride()" class="bg-yellow-600 hover:bg-yellow-500 font-bold px-4 py-2 rounded-xl text-gray-950 text-xs">Set</button>
                </div>
            </div>
            <button onclick="closeAdminModal()" class="w-full bg-gray-800 hover:bg-gray-700 text-white font-bold py-2.5 rounded-xl transition text-xs uppercase">
                Close Dashboard
            </button>
        </div>
    </div>

    <!-- Notification Toast -->
    <div id="notification-box" class="fixed bottom-6 right-6 z-50 transform translate-y-20 opacity-0 transition-all duration-300 bg-cardBg border border-gray-700 text-white px-5 py-3 rounded-xl shadow-2xl flex items-center space-x-3">
        <div id="notification-icon" class="text-emerald-400 text-lg"><i class="fa-solid fa-circle-check"></i></div>
        <div>
            <h4 id="notification-title" class="font-bold text-sm">Success</h4>
            <p id="notification-text" class="text-xs text-gray-300">Action completed successfully.</p>
        </div>
    </div>

    <script>
        // User & Auth State
        let currentUser = null;
        let registeredUsers = JSON.parse(localStorage.getItem('aviator_users') || '[]');
        
        // Game State Variables
        let userBalance = 10000.00;
        let gameState = 'WAITING'; // WAITING, FLYING, CRASHED
        let currentMultiplier = 1.00;
        let crashMultiplier = 1.00;
        let nextMultipliers = [2.45, 1.80]; // Queue for next 2 rounds
        let flightStartTime = 0;
        let flightDuration = 0;
        let multiplierHistory = [2.45, 1.12, 5.80, 1.02, 3.14, 1.45, 12.40, 1.00, 2.10, 4.35];
        
        // Stats
        let stats = { wagered: 0, won: 0, rounds: 0, highestMultiplier: 1.00 };

        // Audio Settings
        let soundEnabled = true;
        let musicEnabled = true;
        let audioCtx = null;

        // Bet States
        const bets = {
            1: { active: false, cashedOut: false, amount: 10, autoEnabled: false, autoMultiplier: 2.00, mode: 'manual' },
            2: { active: false, cashedOut: false, amount: 10, autoEnabled: false, autoMultiplier: 2.00, mode: 'manual' }
        };

        // Simulated Live Players List
        let livePlayers = [];
        const botNames = ['John_K', 'Wanjiru_99', 'Kiptoo_Pro', 'Amina_X', 'Otieno_B', 'Cheruiyot', 'Maina_Bet', 'Naliaka', 'Omondi_Fly', 'Kimani_001'];

        // --- AUTHENTICATION & USSD FUNCTIONS ---
        function switchAuthTab(tab) {
            document.getElementById('form-login').classList.add('hidden');
            document.getElementById('form-register').classList.add('hidden');
            document.getElementById('form-forgot').classList.add('hidden');
            document.getElementById('auth-tab-login').className = "py-2.5 rounded-lg text-gray-400 hover:text-white transition";
            document.getElementById('auth-tab-register').className = "py-2.5 rounded-lg text-gray-400 hover:text-white transition";

            if (tab === 'login') {
                document.getElementById('form-login').classList.remove('hidden');
                document.getElementById('auth-tab-login').className = "py-2.5 rounded-lg bg-blue-600 text-white transition";
                document.getElementById('auth-title').innerText = "AVIATOR LOGIN";
            } else if (tab === 'register') {
                document.getElementById('form-register').classList.remove('hidden');
                document.getElementById('auth-tab-register').className = "py-2.5 rounded-lg bg-blue-600 text-white transition";
                document.getElementById('auth-title').innerText = "CREATE ACCOUNT";
            } else if (tab === 'forgot') {
                document.getElementById('form-forgot').classList.remove('hidden');
                document.getElementById('auth-title').innerText = "USSD PASSWORD RESET";
            }
        }

        function submitRegister() {
            const name = document.getElementById('reg-name').value.trim();
            const phone = document.getElementById('reg-phone').value.trim();
            const pass = document.getElementById('reg-pass').value.trim();

            if (!name || !phone || !pass) {
                showNotification('Registration Error', 'Please fill in all registration fields.', 'error');
                return;
            }

            const existing = registeredUsers.find(u => u.phone === phone);
            if (existing) {
                showNotification('Phone Registered', 'An account with this phone number already exists. Please login.', 'error');
                switchAuthTab('login');
                return;
            }

            const newUser = { name, phone, pass, balance: 10000.00, isAdmin: false };
            registeredUsers.push(newUser);
            localStorage.setItem('aviator_users', JSON.stringify(registeredUsers));

            loginSuccessful(newUser);
        }

        function submitLogin() {
            const userInp = document.getElementById('login-user').value.trim();
            const passInp = document.getElementById('login-pass').value.trim();

            if (!userInp || !passInp) {
                showNotification('Login Error', 'Please enter your username/phone and password.', 'error');
                return;
            }

            // Check if Admin Login
            if ((userInp === 'admin' || userInp === 'admin@aviator.com') && passInp === 'admin123') {
                const adminUser = { name: 'Admin Principal', phone: '+254700000000', balance: 50000.00, isAdmin: true };
                loginSuccessful(adminUser);
                return;
            }

            const user = registeredUsers.find(u => (u.phone === userInp || u.name.toLowerCase() === userInp.toLowerCase()) && u.pass === passInp);
            if (!user) {
                showNotification('Login Failed', 'Invalid credentials. Please check your username or password.', 'error');
                return;
            }

            loginSuccessful(user);
        }

        function loginSuccessful(user) {
            currentUser = user;
            userBalance = user.balance || 10000.00;
            document.getElementById('header-user-tag').innerText = `${user.name} (${user.isAdmin ? 'Admin' : 'Player'})`;
            document.getElementById('auth-modal').classList.add('hidden');
            updateBalanceDisplay();

            if (user.isAdmin) {
                document.getElementById('admin-menu-btn').classList.remove('hidden');
            } else {
                document.getElementById('admin-menu-btn').classList.add('hidden');
            }

            showNotification('Welcome!', `Logged in successfully as ${user.name}`);
        }

        function logoutUser() {
            currentUser = null;
            document.getElementById('auth-modal').classList.remove('hidden');
            switchAuthTab('login');
            showNotification('Logged Out', 'You have been successfully logged out.');
        }

        function requestUssdReset() {
            const phone = document.getElementById('forgot-phone').value.trim();
            const user = registeredUsers.find(u => u.phone === phone);
            
            if (!user) {
                showNotification('USSD Error', 'Phone number not found in registry.', 'error');
                return;
            }

            document.getElementById('ussd-simulation-box').classList.remove('hidden');
            document.getElementById('ussd-message-text').innerText = `USSD Code Sent to ${phone}:\nDial *483*88# to verify reset for ${user.name}. Enter new PIN below:`;
            showNotification('USSD Sent', 'USSD reset prompt dispatched to your phone.');
        }

        function confirmUssdReset() {
            const phone = document.getElementById('forgot-phone').value.trim();
            const newPass = document.getElementById('ussd-input-pin').value.trim();
            
            if (!newPass) {
                showNotification('Error', 'Please enter a new password.', 'error');
                return;
            }

            const user = registeredUsers.find(u => u.phone === phone);
            if (user) {
                user.pass = newPass;
                localStorage.setItem('aviator_users', JSON.stringify(registeredUsers));
                showNotification('Success', 'Password reset via USSD confirmed! You can now login.');
                switchAuthTab('login');
            }
        }

        // --- AUDIO & SOUNDS ---
        function initAudioContext() {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            }
            if (audioCtx.state === 'suspended') {
                audioCtx.resume();
            }
        }

        function playBeep(freq, type, duration) {
            if (!soundEnabled) return;
            try {
                initAudioContext();
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = type;
                osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
                gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start();
                osc.stop(audioCtx.currentTime + duration);
            } catch(e) {}
        }

        function playCashoutSound() {
            playBeep(587.33, 'sine', 0.1);
            setTimeout(() => playBeep(880, 'sine', 0.2), 100);
        }

        function playCrashSound() {
            playBeep(120, 'sawtooth', 0.5);
        }

        function toggleSound() {
            soundEnabled = document.getElementById('sound-toggle').checked;
        }

        function toggleMusic() {
            musicEnabled = document.getElementById('music-toggle').checked;
        }

        function toggleMenu() {
            const menu = document.getElementById('dropdown-menu');
            menu.classList.toggle('hidden');
        }

        // --- MODALS & BANKING ---
        function openDepositModal() {
            document.getElementById('deposit-modal').classList.remove('hidden');
        }
        function closeDepositModal() {
            document.getElementById('deposit-modal').classList.add('hidden');
        }
        function setDepositAmount(amt) {
            document.getElementById('deposit-amount-input').value = amt;
        }
        function submitDeposit() {
            const amt = parseFloat(document.getElementById('deposit-amount-input').value) || 1000;
            const promptLink = document.getElementById('deposit-prompt-link').value;
            userBalance += amt;
            updateBalanceDisplay();
            closeDepositModal();
            showNotification('Deposit Successful', `Added ${amt.toLocaleString()} KES via prompt link reference.`);
        }

        function openWithdrawModal() {
            document.getElementById('withdraw-modal').classList.remove('hidden');
        }
        function closeWithdrawModal() {
            document.getElementById('withdraw-modal').classList.add('hidden');
        }
        function submitWithdraw() {
            const amt = parseFloat(document.getElementById('withdraw-amount-input').value) || 1000;
            if (amt > userBalance) {
                showNotification('Withdrawal Error', 'Insufficient balance for this withdrawal.', 'error');
                return;
            }
            userBalance -= amt;
            updateBalanceDisplay();
            closeWithdrawModal();
            showNotification('Withdrawal Requested', `Successfully initiated withdrawal of ${amt.toLocaleString()} KES.`);
        }

        function openProfileModal() {
            document.getElementById('stat-wagered').innerText = stats.wagered.toFixed(2) + ' KES';
            document.getElementById('stat-won').innerText = stats.won.toFixed(2) + ' KES';
            document.getElementById('stat-rounds').innerText = stats.rounds;
            document.getElementById('stat-highest').innerText = stats.highestMultiplier.toFixed(2) + 'x';
            document.getElementById('profile-modal').classList.remove('hidden');
            toggleMenu();
        }
        function closeProfileModal() {
            document.getElementById('profile-modal').classList.add('hidden');
        }

        function openAdminModal() {
            document.getElementById('admin-preview-1').innerText = nextMultipliers[0].toFixed(2) + 'x';
            document.getElementById('admin-preview-2').innerText = nextMultipliers[1].toFixed(2) + 'x';
            document.getElementById('admin-modal').classList.remove('hidden');
            toggleMenu();
        }
        function closeAdminModal() {
            document.getElementById('admin-modal').classList.add('hidden');
        }
        function applyAdminOverride() {
            const val = parseFloat(document.getElementById('admin-override-val').value);
            if (!isNaN(val) && val >= 1.0) {
                nextMultipliers[0] = val;
                document.getElementById('admin-preview-1').innerText = nextMultipliers[0].toFixed(2) + 'x';
                showNotification('Admin Override Set', `Next round multiplier set to ${val.toFixed(2)}x`);
            }
        }

        // --- MULTIPLAYER & LIVE PLAYERS FEED ---
        function initLivePlayers() {
            livePlayers = botNames.map(name => {
                const betAmount = (Math.floor(Math.random() * 50) + 1) * 10;
                return {
                    name: name,
                    bet: betAmount,
                    cashedOut: false,
                    cashoutAmount: 0
                };
            });
            renderLivePlayers();
        }

        function renderLivePlayers() {
            const container = document.getElementById('live-players-list');
            let html = '';

            // Render Player's Own Active / Recent Bets on Top
            [1, 2].forEach(id => {
                const bet = bets[id];
                if (bet.active || bet.cashedOut) {
                    html += `
                        <div class="grid grid-cols-3 py-1.5 px-2 rounded-lg bg-blue-950/40 border border-blue-800/50 items-center">
                            <span class="text-blue-300 font-bold truncate">You (Bet ${id})</span>
                            <span class="text-center font-mono text-gray-200">${bet.amount.toFixed(2)}</span>
                            <span class="text-right font-bold ${bet.cashedOut ? 'text-emerald-400' : 'text-yellow-400'}">
                                ${bet.cashedOut ? (bet.cashoutValue || 0).toFixed(2) + ' KES' : 'Running...'}
                            </span>
                        </div>
                    `;
                }
            });

            // Render Bot Players (Showing cashed out amount in KES instead of multiplier)
            html += livePlayers.map(p => `
                <div class="grid grid-cols-3 py-1.5 px-2 rounded-lg hover:bg-cardBg/50 items-center border-b border-gray-800/30">
                    <span class="text-gray-300 font-medium truncate">${p.name}</span>
                    <span class="text-center font-mono text-gray-400">${p.bet.toFixed(2)}</span>
                    <span class="text-right font-bold ${p.cashedOut ? 'text-emerald-400' : 'text-gray-500'}">
                        ${p.cashedOut ? p.cashoutAmount.toFixed(2) + ' KES' : '...'}
                    </span>
                </div>
            `).join('');

            container.innerHTML = html;
        }

        function updateBalanceDisplay() {
            document.getElementById('user-balance').innerText = userBalance.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' KES';
        }

        function showNotification(title, text, type = 'success') {
            const box = document.getElementById('notification-box');
            const icon = document.getElementById('notification-icon');
            document.getElementById('notification-title').innerText = title;
            document.getElementById('notification-text').innerText = text;
            
            if(type === 'success') {
                icon.innerHTML = '<i class="fa-solid fa-circle-check text-emerald-400"></i>';
            } else {
                icon.innerHTML = '<i class="fa-solid fa-circle-exclamation text-red-400"></i>';
            }

            box.classList.remove('translate-y-20', 'opacity-0');
            setTimeout(() => {
                box.classList.add('translate-y-20', 'opacity-0');
            }, 3000);
        }

        function setTab(betId, mode) {
            bets[betId].mode = mode;
            const manualBtn = document.getElementById(`bet${betId}-tab-manual`);
            const autoBtn = document.getElementById(`bet${betId}-tab-auto`);
            if(mode === 'manual') {
                manualBtn.className = "px-3 py-1 rounded-md bg-blue-600 text-white font-semibold transition";
                autoBtn.className = "px-3 py-1 rounded-md text-gray-400 hover:text-white transition";
            } else {
                autoBtn.className = "px-3 py-1 rounded-md bg-blue-600 text-white font-semibold transition";
                manualBtn.className = "px-3 py-1 rounded-md text-gray-400 hover:text-white transition";
            }
        }

        function adjustBet(betId, delta) {
            const input = document.getElementById(`bet${betId}-amount`);
            let val = parseFloat(input.value) || 10;
            val = Math.max(10, val + delta);
            input.value = val.toFixed(2);
        }

        function setPresetBet(betId, amount) {
            document.getElementById(`bet${betId}-amount`).value = amount.toFixed(2);
        }

        function handleBetClick(betId) {
            initAudioContext();
            const bet = bets[betId];
            const amountInput = document.getElementById(`bet${betId}-amount`);
            const actionBtn = document.getElementById(`bet${betId}-action-btn`);
            const autoEnabledCheckbox = document.getElementById(`bet${betId}-auto-enabled`);
            const autoMultInput = document.getElementById(`bet${betId}-auto-multiplier`);

            bet.amount = parseFloat(amountInput.value) || 10;
            bet.autoEnabled = autoEnabledCheckbox.checked;
            bet.autoMultiplier = parseFloat(autoMultInput.value) || 2.00;

            if (!bet.active) {
                if (gameState === 'CRASHED') {
                    showNotification('Round Ended', 'Please wait for the next round to place bets.', 'error');
                    return;
                }
                if (userBalance < bet.amount) {
                    showNotification('Insufficient Funds', 'Your balance is too low for this bet amount.', 'error');
                    return;
                }

                userBalance -= bet.amount;
                updateBalanceDisplay();
                bet.active = true;
                bet.cashedOut = false;
                stats.wagered += bet.amount;

                if (gameState === 'FLYING') {
                    actionBtn.className = "w-full bg-yellow-600 hover:bg-yellow-500 text-white font-bold py-3.5 rounded-xl shadow-lg transition tracking-wide text-sm flex items-center justify-center space-x-2 uppercase";
                    actionBtn.innerHTML = `<span>CANCEL (NEXT)</span>`;
                } else {
                    actionBtn.className = "w-full bg-red-600 hover:bg-red-500 text-white font-bold py-3.5 rounded-xl shadow-lg transition tracking-wide text-sm flex items-center justify-center space-x-2 uppercase";
                    actionBtn.innerHTML = `<span>CANCEL BET</span>`;
                    amountInput.disabled = true;
                }
                showNotification('Bet Placed', `Successfully placed ${bet.amount.toFixed(2)} KES on Bet ${betId}.`);
            } else {
                if (gameState === 'WAITING') {
                    userBalance += bet.amount;
                    updateBalanceDisplay();
                    bet.active = false;
                    stats.wagered -= bet.amount;
                    actionBtn.className = "w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3.5 rounded-xl shadow-lg transition tracking-wide text-sm flex items-center justify-center space-x-2 uppercase";
                    actionBtn.innerHTML = `<span>BET</span>`;
                    amountInput.disabled = false;
                    showNotification('Bet Cancelled', 'Your bet has been refunded.');
                } else if (gameState === 'FLYING' && bet.active && !bet.cashedOut) {
                    cashOutBet(betId);
                }
            }
            renderLivePlayers();
        }

        function cashOutBet(betId) {
            const bet = bets[betId];
            if (!bet.active || bet.cashedOut) return;

            bet.cashedOut = true;
            const winnings = bet.amount * currentMultiplier;
            bet.cashoutValue = winnings;
            userBalance += winnings;
            stats.won += winnings;
            updateBalanceDisplay();
            playCashoutSound();

            const actionBtn = document.getElementById(`bet${betId}-action-btn`);
            actionBtn.className = "w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3.5 rounded-xl shadow-lg transition tracking-wide text-sm flex items-center justify-center space-x-2 uppercase";
            actionBtn.innerHTML = `<span>WON ${winnings.toFixed(2)} KES</span>`;

            showNotification('Cashed Out!', `You won ${winnings.toFixed(2)} KES at ${currentMultiplier.toFixed(2)}x!`);
            renderLivePlayers();
        }

        function renderHistoryBar() {
            const bar = document.getElementById('history-bar');
            let html = '<span class="text-xs text-gray-500 font-semibold uppercase tracking-wider mr-1">History:</span>';
            multiplierHistory.slice(-8).reverse().forEach(m => {
                let colorClass = 'text-gray-300 bg-cardBg border-gray-700';
                if(m >= 2.0 && m < 10.0) colorClass = 'text-blue-400 bg-blue-950/40 border-blue-800/50';
                if(m >= 10.0) colorClass = 'text-yellow-400 bg-yellow-950/40 border-yellow-800/50';
                html += `<span class="px-2.5 py-1 rounded-lg text-xs font-bold border ${colorClass}">${m.toFixed(2)}x</span>`;
            });
            bar.innerHTML = html;
        }

        // Canvas Setup & Rendering Loop
        const canvas = document.getElementById('flight-canvas');
        const ctx = canvas.getContext('2d');

        function resizeCanvas() {
            const container = canvas.parentElement;
            canvas.width = container.clientWidth;
            canvas.height = container.clientHeight;
        }
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        function drawFlightCurve(progress) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            if (gameState === 'WAITING') return;

            const width = canvas.width;
            const height = canvas.height;

            ctx.beginPath();
            ctx.moveTo(0, height);

            const curveX = width * 0.8 * Math.min(progress, 1);
            const curveY = height - (height * 0.7 * Math.pow(progress, 2));

            ctx.quadraticCurveTo(curveX * 0.5, height, curveX, curveY);
            ctx.lineTo(curveX, height);
            ctx.closePath();

            const gradient = ctx.createLinearGradient(0, 0, 0, height);
            gradient.addColorStop(0, 'rgba(229, 62, 62, 0.3)');
            gradient.addColorStop(1, 'rgba(229, 62, 62, 0.0)');
            ctx.fillStyle = gradient;
            ctx.fill();

            ctx.beginPath();
            ctx.moveTo(0, height);
            ctx.quadraticCurveTo(curveX * 0.5, height, curveX, curveY);
            ctx.strokeStyle = '#e53e3e';
            ctx.lineWidth = 3;
            ctx.stroke();

            const planeIndicator = document.getElementById('airplane-indicator');
            planeIndicator.style.left = `${Math.min(curveX, width - 40)}px`;
            planeIndicator.style.top = `${Math.max(curveY - 20, 20)}px`;
            planeIndicator.classList.remove('hidden');
        }

        function startWaitingPhase() {
            gameState = 'WAITING';
            currentMultiplier = 1.00;
            stats.rounds++;
            document.getElementById('multiplier-display').innerText = '1.00x';
            document.getElementById('multiplier-display').className = 'text-5xl sm:text-7xl font-black flight-glow text-yellow-400 tracking-tight';
            
            const statusText = document.getElementById('flight-status-text');
            statusText.innerText = 'WAITING FOR NEXT ROUND';
            statusText.className = 'mt-2 text-sm sm:text-lg font-bold uppercase tracking-widest text-emerald-400 bg-emerald-950/60 px-4 py-1.5 rounded-full border border-emerald-800/50 shadow';

            document.getElementById('airplane-indicator').classList.add('hidden');
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            [1, 2].forEach(id => {
                document.getElementById(`bet${id}-live-win`).classList.add('hidden');
                const bet = bets[id];
                const actionBtn = document.getElementById(`bet${id}-action-btn`);
                const amountInput = document.getElementById(`bet${id}-amount`);
                
                if (bet.active && !bet.cashedOut) {
                    actionBtn.className = "w-full bg-yellow-500 hover:bg-yellow-400 text-gray-950 font-black py-3.5 rounded-xl shadow-lg transition tracking-wide text-sm flex items-center justify-center space-x-2 uppercase";
                    actionBtn.innerHTML = `<span>CASH OUT</span>`;
                    document.getElementById(`bet${id}-live-win`).classList.remove('hidden');
                } else if (!bet.active) {
                    actionBtn.className = "w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3.5 rounded-xl shadow-lg transition tracking-wide text-sm flex items-center justify-center space-x-2 uppercase";
                    actionBtn.innerHTML = `<span>BET</span>`;
                    amountInput.disabled = false;
                }
            });

            initLivePlayers();

            let countdown = 3;
            statusText.innerText = `NEXT ROUND IN ${countdown}s`;
            
            const timer = setInterval(() => {
                countdown--;
                if(countdown > 0) {
                    statusText.innerText = `NEXT ROUND IN ${countdown}s`;
                } else {
                    clearInterval(timer);
                    startFlightPhase();
                }
            }, 1000);
        }

        function startFlightPhase() {
            gameState = 'FLYING';
            flightStartTime = Date.now();
            
            // Pop next crash multiplier from queue and replenish queue
            crashMultiplier = nextMultipliers.shift();
            const upcomingRand = parseFloat((1.01 + (Math.random() * Math.random() * 20)).toFixed(2));
            nextMultipliers.push(upcomingRand);

            if (crashMultiplier > stats.highestMultiplier) {
                stats.highestMultiplier = crashMultiplier;
            }

            flightDuration = (crashMultiplier - 1) * 1500 + 2000;
            if(flightDuration < 1500) flightDuration = 1500;

            const statusText = document.getElementById('flight-status-text');
            statusText.innerText = 'FLIGHT IS FLYING';
            statusText.className = 'mt-2 text-sm sm:text-lg font-bold uppercase tracking-widest text-blue-400 bg-blue-950/60 px-4 py-1.5 rounded-full border border-blue-800/50 shadow';

            [1, 2].forEach(id => {
                const bet = bets[id];
                const actionBtn = document.getElementById(`bet${id}-action-btn`);
                if (bet.active) {
                    actionBtn.className = "w-full bg-yellow-500 hover:bg-yellow-400 text-gray-950 font-black py-3.5 rounded-xl shadow-lg transition tracking-wide text-sm flex items-center justify-center space-x-2 uppercase";
                    actionBtn.innerHTML = `<span>CASH OUT</span>`;
                    document.getElementById(`bet${id}-live-win`).classList.remove('hidden');
                }
            });

            requestAnimationFrame(flightTick);
        }

        function flightTick() {
            if (gameState !== 'FLYING') return;

            const elapsed = Date.now() - flightStartTime;
            const progress = Math.min(elapsed / flightDuration, 1);

            if (progress >= 1 || currentMultiplier >= crashMultiplier) {
                currentMultiplier = crashMultiplier;
                triggerCrash();
                return;
            }

            currentMultiplier = 1.00 + (crashMultiplier - 1.00) * Math.pow(progress, 1.8);
            if (currentMultiplier > crashMultiplier) currentMultiplier = crashMultiplier;

            document.getElementById('multiplier-display').innerText = currentMultiplier.toFixed(2) + 'x';
            
            [1, 2].forEach(id => {
                const bet = bets[id];
                if (bet.active && !bet.cashedOut) {
                    const potentialWin = bet.amount * currentMultiplier;
                    document.getElementById(`bet${id}-win-amount`).innerText = potentialWin.toFixed(2);
                    document.getElementById(`bet${id}-live-mult`).innerText = currentMultiplier.toFixed(2) + 'x';
                }
            });

            drawFlightCurve(progress);

            [1, 2].forEach(id => {
                const bet = bets[id];
                if (bet.active && !bet.cashedOut && bet.autoEnabled && currentMultiplier >= bet.autoMultiplier) {
                    cashOutBet(id);
                }
            });

            livePlayers.forEach(p => {
                if (!p.cashedOut && Math.random() < 0.03 && currentMultiplier > 1.2) {
                    if (currentMultiplier < (p.bet > 300 ? 2.5 : 8.0)) {
                        p.cashedOut = true;
                        p.cashoutAmount = p.bet * currentMultiplier;
                    }
                }
            });
            renderLivePlayers();

            requestAnimationFrame(flightTick);
        }

        function triggerCrash() {
            gameState = 'CRASHED';
            playCrashSound();
            document.getElementById('multiplier-display').innerText = crashMultiplier.toFixed(2) + 'x';
            document.getElementById('multiplier-display').className = 'text-5xl sm:text-7xl font-black flight-glow text-red-500 tracking-tight';

            const statusText = document.getElementById('flight-status-text');
            statusText.innerText = 'FLED / CRASHED';
            statusText.className = 'mt-2 text-sm sm:text-lg font-bold uppercase tracking-widest text-red-400 bg-red-950/60 px-4 py-1.5 rounded-full border border-red-800/50 shadow';

            document.getElementById('airplane-indicator').classList.add('hidden');

            [1, 2].forEach(id => {
                const bet = bets[id];
                const actionBtn = document.getElementById(`bet${id}-action-btn`);
                const amountInput = document.getElementById(`bet${id}-amount`);
                document.getElementById(`bet${id}-live-win`).classList.add('hidden');

                if (bet.active && !bet.cashedOut) {
                    bet.cashedOut = true;
                    actionBtn.className = "w-full bg-gray-700 text-gray-400 font-bold py-3.5 rounded-xl shadow-lg transition tracking-wide text-sm flex items-center justify-center space-x-2 uppercase cursor-not-allowed";
                    actionBtn.innerHTML = `<span>LOST</span>`;
                }
                
                bet.active = false;
                bet.cashedOut = false;
                amountInput.disabled = false;
            });

            multiplierHistory.push(crashMultiplier);
            renderHistoryBar();
            renderLivePlayers();

            setTimeout(() => {
                startWaitingPhase();
            }, 4000);
        }

        window.onload = function() {
            updateBalanceDisplay();
            renderHistoryBar();
            initLivePlayers();
            startWaitingPhase();
        };
    </script>
</body>
</html>
