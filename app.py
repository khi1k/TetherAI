import sqlite3
import csv
import io
import hashlib
import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

app = Flask(__name__)
app.secret_key = "tether_ai_secret_key"
DATABASE = "tether_universal.db"
#client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ==========================================
# OOP PARADIGM (Domain Models)
# ==========================================
class Business:
    def __init__(self, id, name, email, password):
        self.id = id
        self.name = name
        self.email = email
        self.password = password


class Product:
    def __init__(self, id, name, price, stock, is_infinite):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock
        self.is_infinite = is_infinite


# ==========================================
# DATABASE SETUP
# ==========================================
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS businesses (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT, has_seen_help INTEGER DEFAULT 0)")
        conn.execute(
            """CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, business_id INTEGER, name TEXT, price REAL, stock INTEGER, is_infinite BOOLEAN)""")
        conn.execute(
            "CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY, business_id INTEGER, total REAL, date TEXT)")
        conn.execute(
            """CREATE TABLE IF NOT EXISTS transaction_items (id INTEGER PRIMARY KEY, transaction_id INTEGER, product_id INTEGER, quantity INTEGER)""")


init_db()


# ==========================================
# HELPER: REAL AI PRICING ADVISOR (With Reasoning)
# ==========================================
def get_ai_pricing_advice(product_name, product_price):
    try:
        prompt = f"You are a small business consultant. Item: '{product_name}', Price: ${product_price:.2f}. Give a 1-sentence actionable pricing advice. Then on a new line, write 'Reason:' and explain why in 1 sentence."

        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful AI business consultant."},
                {"role": "user", "content": prompt}
            ],
            model="openai/gpt-oss-20b",
            temperature=0.7,
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Groq API Error: {e}")
        return f"Consider testing a higher price point for {product_name}.\nReason: Premium items often have inelastic demand, meaning customers will still buy if the perceived value is high."
# ==========================================
# ROUTES: AUTH & SETTINGS
# ==========================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        conn = get_db()
        user = conn.execute("SELECT * FROM businesses WHERE email = ? AND password = ?", (email, password)).fetchone()
        if user:
            session['business_id'] = user['id']
            session['business_name'] = user['name']
            if user['has_seen_help'] == 0:
                conn.execute("UPDATE businesses SET has_seen_help = 1 WHERE id = ?", (user['id'],))
                conn.commit()
                conn.close()
                return redirect(url_for('help_page'))
            conn.close()
            return redirect(url_for('dashboard'))
        conn.close()
        flash("Invalid credentials.", "error")
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        hashed_pw = hashlib.sha256(request.form['password'].encode()).hexdigest()
        conn = get_db()
        try:
            conn.execute("INSERT INTO businesses (name, email, password, has_seen_help) VALUES (?, ?, ?, 1)",
                         (name, email, hashed_pw))
            conn.commit()
            user = conn.execute("SELECT * FROM businesses WHERE email = ?", (email,)).fetchone()
            session['business_id'] = user['id']
            session['business_name'] = user['name']
            flash("Account created! Welcome to Tether AI.", "success")
            return redirect(url_for('help_page'))
        except sqlite3.IntegrityError:
            flash("Email already exists.", "error")
        finally:
            conn.close()
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'business_id' not in session: return redirect(url_for('login'))
    conn = get_db()
    bid = session['business_id']

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')

        # If they are trying to change the password
        if old_password or new_password:
            current_user = conn.execute("SELECT password FROM businesses WHERE id = ?", (bid,)).fetchone()
            old_hashed = hashlib.sha256(old_password.encode()).hexdigest()

            if old_hashed != current_user['password']:
                flash("Incorrect current password. Password not updated.", "error")
                return redirect(url_for('settings'))

            if not new_password:
                flash("You must enter a new password.", "error")
                return redirect(url_for('settings'))

            new_hashed = hashlib.sha256(new_password.encode()).hexdigest()
            conn.execute("UPDATE businesses SET name=?, email=?, password=? WHERE id=?", (name, email, new_hashed, bid))
        else:
            conn.execute("UPDATE businesses SET name=?, email=? WHERE id=?", (name, email, bid))

        conn.commit()
        session['business_name'] = name
        flash("Settings updated successfully.", "success")
        return redirect(url_for('settings'))

    business = conn.execute("SELECT * FROM businesses WHERE id = ?", (bid,)).fetchone()
    conn.close()
    return render_template('settings.html', business=business)
@app.route('/')
def home():
    if 'business_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')
# ==========================================
# ROUTES: DASHBOARD & HISTORY
# ==========================================
@app.route('/dashboard')
def dashboard():
    if 'business_id' not in session: return redirect(url_for('login'))
    bid = session['business_id']
    conn = get_db()
    products_rows = conn.execute("SELECT * FROM products WHERE business_id = ?", (bid,)).fetchall()
    products = [Product(r['id'], r['name'], r['price'], r['stock'], r['is_infinite']) for r in products_rows]

    low_stock_items = list(filter(lambda p: p.stock < 5 and not p.is_infinite, products))
    restock_alert = f"Running low on {', '.join([p.name for p in low_stock_items])}." if low_stock_items else None

    pricing_alert = None
    services = [p for p in products if p.is_infinite]
    if services:
        sample = services[0]
        pricing_alert = get_ai_pricing_advice(sample.name, sample.price)

    chart_dates = []
    chart_totals = []
    for i in range(6, -1, -1):
        date_str = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        chart_dates.append(date_str)
        total = conn.execute("SELECT SUM(total) FROM transactions WHERE business_id = ? AND date LIKE ?",
                             (bid, f"{date_str}%")).fetchone()[0]
        chart_totals.append(float(total) if total else 0.0)

    conn.close()
    return render_template('dashboard.html', restock_alert=restock_alert, pricing_alert=pricing_alert,
                           chart_dates=chart_dates, chart_totals=chart_totals)


@app.route('/history')
def history():
    if 'business_id' not in session: return redirect(url_for('login'))
    bid = session['business_id']
    conn = get_db()

    # Get the list of all transactions for the receipt table
    trans = conn.execute("SELECT * FROM transactions WHERE business_id = ? ORDER BY id DESC", (bid,)).fetchall()

    # --- BUILD THE FULL HISTORY CHART DATA ---
    chart_dates = []
    chart_totals = []

    # 1. Find the very first transaction date to know where to start the chart
    first_transaction = conn.execute("SELECT date FROM transactions WHERE business_id = ? ORDER BY date ASC LIMIT 1",
                                     (bid,)).fetchone()

    if first_transaction:
        start_date = datetime.strptime(first_transaction['date'][:10], "%Y-%m-%d")
        today = datetime.now()

        # 2. Loop from the start date to today, calculating revenue for each day
        current_date = start_date
        while current_date <= today:
            date_str = current_date.strftime("%Y-%m-%d")
            chart_dates.append(date_str)

            total = conn.execute("SELECT SUM(total) FROM transactions WHERE business_id = ? AND date LIKE ?",
                                 (bid, f"{date_str}%")).fetchone()[0]
            chart_totals.append(float(total) if total else 0.0)

            current_date += timedelta(days=1)

    conn.close()
    return render_template('history.html', transactions=trans, chart_dates=chart_dates, chart_totals=chart_totals)

@app.route('/help')
def help_page():
    if 'business_id' not in session: return redirect(url_for('login'))
    return render_template('help.html')


# ==========================================
# ROUTES: CATALOG (WITH EDIT/DELETE)
# ==========================================
@app.route('/catalog', methods=['GET', 'POST'])
def catalog():
    if 'business_id' not in session: return redirect(url_for('login'))
    bid = session['business_id']
    conn = get_db()

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'manual':
            name = request.form['name']
            price = float(request.form['price'])
            stock = 999999 if request.form.get('is_infinite') else int(request.form['stock'] or 0)
            is_inf = True if request.form.get('is_infinite') else False
            conn.execute("INSERT INTO products (business_id, name, price, stock, is_infinite) VALUES (?, ?, ?, ?, ?)",
                         (bid, name, price, stock, is_inf))
            flash(f"{name} added.", "success")
        elif action == 'csv':
            file = request.files['csv_file']
            if file and file.filename.endswith('.csv'):
                try:
                    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                    csv_input = csv.reader(stream)
                    next(csv_input)
                    for row in csv_input:
                        if len(row) >= 4:
                            is_inf = row[3].strip().lower() == 'true'
                            stock = 999999 if is_inf else int(row[2])
                            conn.execute(
                                "INSERT INTO products (business_id, name, price, stock, is_infinite) VALUES (?, ?, ?, ?, ?)",
                                (bid, row[0], float(row[1]), stock, is_inf))
                    flash("CSV Uploaded successfully!", "success")
                except Exception as e:
                    flash(f"CSV Error: {e}. Check formatting.", "error")
        conn.commit()

    products = conn.execute("SELECT * FROM products WHERE business_id = ?", (bid,)).fetchall()
    conn.close()
    return render_template('catalog.html', products=products)


@app.route('/delete_product/<int:product_id>')
def delete_product(product_id):
    if 'business_id' not in session: return redirect(url_for('login'))
    conn = get_db()
    conn.execute("DELETE FROM products WHERE id = ? AND business_id = ?", (product_id, session['business_id']))
    conn.commit()
    conn.close()
    flash("Product deleted.", "success")
    return redirect(url_for('catalog'))


@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if 'business_id' not in session: return redirect(url_for('login'))
    conn = get_db()
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        stock = int(request.form['stock'] or 0)
        is_inf = True if request.form.get('is_infinite') else False
        conn.execute("UPDATE products SET name=?, price=?, stock=?, is_infinite=? WHERE id=? AND business_id=?",
                     (name, price, stock, is_inf, product_id, session['business_id']))
        conn.commit()
        conn.close()
        flash("Product updated.", "success")
        return redirect(url_for('catalog'))
    product = conn.execute("SELECT * FROM products WHERE id = ? AND business_id = ?",
                           (product_id, session['business_id'])).fetchone()
    conn.close()
    return f"""
    <div class="card" style="max-width: 500px; margin: 2rem auto;">
        <h2>Edit Product</h2>
        <form method="POST">
            <label>Name</label><input type="text" name="name" value="{product['name']}" required>
            <label>Price</label><input type="number" step="0.01" name="price" value="{product['price']}" required>
            <label>Stock</label><input type="number" name="stock" value="{product['stock']}">
            <label><input type="checkbox" name="is_infinite" {'checked' if product['is_infinite'] else ''}> Unlimited</label>
            <button type="submit" style="width: 100%; margin-top: 1rem;">Update Item</button>
        </form>
    </div>
    """


# ==========================================
# ROUTES: PUBLIC DIRECTORY & CUSTOMER CHAT
# ==========================================
@app.route('/directory')
def directory():
    conn = get_db()
    businesses = conn.execute("SELECT id, name FROM businesses").fetchall()
    conn.close()
    return render_template('directory.html', businesses=businesses)


@app.route('/business/<int:business_id>', methods=['GET', 'POST'])
def public_business(business_id):
    conn = get_db()
    business = conn.execute("SELECT * FROM businesses WHERE id = ?", (business_id,)).fetchone()
    products = conn.execute("SELECT * FROM products WHERE business_id = ?", (business_id,)).fetchall()
    conn.close()

    if 'public_chat' not in session:
        session['public_chat'] = []

    if request.method == 'POST':
        user_msg = request.form['message']
        response = ""

        try:
            prompt = f"You are a customer service bot for {business['name']}. The menu is: {[p['name'] for p in products]}. Answer this customer politely and concisely: {user_msg}"

            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful customer service bot."},
                    {"role": "user", "content": prompt}
                ],
                model="openai/gpt-oss-20b",
                temperature=0.7,
            )
            response = chat_completion.choices[0].message.content.strip()

        except Exception as e:
            print(f"Chat API Error: {e}")
            # Fallback Logic
            user_msg_lower = user_msg.lower()
            if 'menu' in user_msg_lower or 'price' in user_msg_lower:
                item_list = list(map(lambda p: f"{p['name']} (${p['price']:.2f})", products))
                response = f"Here is our menu:\n" + "\n".join(item_list)
            elif 'hours' in user_msg_lower or 'open' in user_msg_lower:
                response = "We are open Monday to Friday from 9:00 AM to 6:00 PM."
            elif 'hello' in user_msg_lower or 'hi' in user_msg_lower:
                response = f"Hello! Welcome to {business['name']}. How can I help you?"
            else:
                response = "I'm having a slight connection issue, but you can ask me about our 'menu' or 'hours'!"

        history = session['public_chat']
        history.append({"role": "user", "text": user_msg})
        history.append({"role": "ai", "text": response})
        session['public_chat'] = history

    return render_template('public_business.html', business=business, products=products, history=session['public_chat'])

# ==========================================
# ROUTES: POS, CHECKOUT, RECEIPTS
# ==========================================
@app.route('/pos')
def pos():
    if 'business_id' not in session: return redirect(url_for('login'))
    conn = get_db()
    products = conn.execute("SELECT * FROM products WHERE business_id = ?", (session['business_id'],)).fetchall()
    conn.close()
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    for p_id, qty in cart.items():
        conn = get_db()
        p = conn.execute("SELECT * FROM products WHERE id = ?", (p_id,)).fetchone()
        conn.close()
        if p:
            cart_items.append(
                {"id": p['id'], "name": p['name'], "price": p['price'], "qty": qty, "subtotal": p['price'] * qty})
            total += p['price'] * qty
    return render_template('pos.html', products=products, cart=cart_items, total=total)


@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    conn = get_db()
    p = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()
    if not p: return redirect(url_for('pos'))
    cart = session.get('cart', {})
    current_qty = cart.get(str(product_id), 0)
    if not p['is_infinite'] and current_qty >= p['stock']:
        flash(f"Cannot add more {p['name']}. Only {p['stock']} in stock.", "error")
        return redirect(url_for('pos'))
    cart[str(product_id)] = current_qty + 1
    session['cart'] = cart
    return redirect(url_for('pos'))


@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        session['cart'] = cart
    return redirect(url_for('pos'))


@app.route('/checkout', methods=['POST'])
def checkout():
    if 'business_id' not in session or 'cart' not in session: return redirect(url_for('pos'))
    bid = session['business_id']
    cart = session['cart']
    conn = get_db()
    total = 0
    items_to_insert = []
    for p_id, qty in cart.items():
        p = conn.execute("SELECT * FROM products WHERE id = ?", (p_id,)).fetchone()
        if p:
            if not p['is_infinite'] and p['stock'] < qty:
                flash(f"Error: Not enough stock for {p['name']}.", "error")
                return redirect(url_for('pos'))
            total += p['price'] * qty
            items_to_insert.append((p_id, qty, not p['is_infinite']))

    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur = conn.cursor()
    cur.execute("INSERT INTO transactions (business_id, total, date) VALUES (?, ?, ?)", (bid, total, date))
    trans_id = cur.lastrowid
    for item in items_to_insert:
        p_id, qty, deduct_stock = item
        cur.execute("INSERT INTO transaction_items (transaction_id, product_id, quantity) VALUES (?, ?, ?)",
                    (trans_id, p_id, qty))
        if deduct_stock:
            cur.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, p_id))
    conn.commit()
    conn.close()
    session.pop('cart', None)
    flash(f"Payment Approved! Total: ${total:.2f}", "success")
    return redirect(url_for('transactions'))


@app.route('/transactions')
def transactions():
    if 'business_id' not in session: return redirect(url_for('login'))
    conn = get_db()
    trans = conn.execute("SELECT * FROM transactions WHERE business_id = ? ORDER BY id DESC",
                         (session['business_id'],)).fetchall()
    conn.close()
    return render_template('transactions.html', transactions=trans)


@app.route('/receipt/<int:trans_id>')
def receipt(trans_id):
    if 'business_id' not in session: return redirect(url_for('login'))
    conn = get_db()
    trans = conn.execute("SELECT * FROM transactions WHERE id = ?", (trans_id,)).fetchone()
    items = conn.execute(
        """SELECT p.name, p.price, ti.quantity FROM transaction_items ti JOIN products p ON ti.product_id = p.id WHERE ti.transaction_id = ?""",
        (trans_id,)).fetchall()
    conn.close()
    return render_template('receipt.html', trans=trans, items=items)


if __name__ == '__main__':
    app.run(debug=True)
