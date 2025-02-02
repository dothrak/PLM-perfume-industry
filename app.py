from flask import Flask, request, redirect, url_for, render_template, flash, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = 'my_secret_key'

def connect_db():
    conn = sqlite3.connect('BDD.db')
    conn.row_factory = sqlite3.Row 
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/product')
def product():
    return render_template('product.html')

@app.route('/product-women')
def product_women():
    return render_template('product-women.html')

@app.route('/product-men')
def product_men():
    return render_template('product-men.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        role = get_user_role(email, password)
        
        if role == 'client':
            return redirect(url_for('client'))
        elif role == 'chemist':
            return redirect(url_for('chemist'))
        elif role == 'creator':
            return redirect(url_for('creator'))
        elif role == 'supplier':
            return redirect(url_for('supplier'))
        elif role == 'chief-product':
            return redirect(url_for('project_list'))
        else:
            return "Invalid credentials or role not found", 401
    return render_template('login.html')

def get_user_role(email, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM credentials WHERE email=? AND password=?", (email, password))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return None

@app.route('/client')
def client():
    return render_template('client.html')

@app.route('/order')
def order():
    return render_template('order.html')

@app.route('/chemist')
def chemist():
    return render_template('chemist.html')

@app.route('/creator')
def creator():
    return render_template('create-product.html')

@app.route('/supplier')
def supplier():
    return render_template('supplier.html')

@app.route('/create-product', methods=['GET'])
def create_product():
    return render_template('create-product.html')

@app.route('/add_product', methods=['POST'])
def add_product():
    name = request.form['name']
    ingredient1 = request.form['ingredient1']
    ingredient2 = request.form['ingredient2']
    price = request.form['price']

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (name, ingredient1, ingredient2, price)
        VALUES (?, ?, ?, ?)
    """, (name, ingredient1, ingredient2, price))
    conn.commit()
    conn.close()

    return redirect(url_for('create_product'))

@app.route('/existing-products')
def existing_products():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, ingredient1, ingredient2, price FROM products ORDER BY id ASC")
    products = cursor.fetchall()
    conn.close()

    return render_template('existing-products.html', products=products)

@app.route('/cp-products')
def cp_products():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, ingredient1, ingredient2, price FROM products ORDER BY id ASC")
    products = cursor.fetchall()
    conn.close()

    return render_template('cp-products.html', products=products)

@app.route('/delete-product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    return jsonify(success=True)

def get_ingredient_quantity(ingredient_name):
    conn = sqlite3.connect('BDD.db')
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM ingredient WHERE name=?", (ingredient_name,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def update_ingredient_quantity(ingredient_name, quantity):
    conn = sqlite3.connect('BDD.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE ingredient SET quantity = quantity - ? WHERE name = ?", (quantity, ingredient_name))
    conn.commit()
    conn.close()

def add_production(product_name, quantity):
    conn = sqlite3.connect('BDD.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO production (product, quantity, status) VALUES (?, ?, ?)", (product_name, quantity, 'in progress'))
    conn.commit()
    conn.close()

@app.route('/chemist', methods=['POST'])
def launch_production():
    product_name = request.form['ingredient1']
    quantity = int(request.form['ingredient2'])

    conn = sqlite3.connect('BDD.db')
    cursor = conn.cursor()
    cursor.execute("SELECT ingredient1, ingredient2 FROM products WHERE name=?", (product_name,))
    result = cursor.fetchone()
    conn.close()

    if result:
        ingredient1 = result[0]
        ingredient2 = result[1]
        
        ingredient1_quantity = get_ingredient_quantity(ingredient1)
        ingredient2_quantity = get_ingredient_quantity(ingredient2)

        if ingredient1_quantity >= quantity and ingredient2_quantity >= quantity:
            update_ingredient_quantity(ingredient1, quantity)
            update_ingredient_quantity(ingredient2, quantity)
            add_production(product_name, quantity)
            return render_template('chemist.html', message="Production launched successfully!", message_type="success")
        else:
            return render_template('chemist.html', message="Not enough ingredients to launch production.", message_type="error")
    else:
        return render_template('chemist.html', message="Product not found.", message_type="error")

def get_productions():
    conn = sqlite3.connect('BDD.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM production WHERE status = 'in progress'")
    in_progress = cursor.fetchall()

    cursor.execute("SELECT * FROM production WHERE status = 'completed'")
    completed = cursor.fetchall()

    conn.close()

    return {
        'inProgress': [{'id': row[0], 'name': row[1], 'quantity': row[2]} for row in in_progress],
        'completed': [{'id': row[0], 'name': row[1], 'quantity': row[2]} for row in completed]
    }

@app.route('/production-status')
def production_status():
    productions_data = get_productions()
    return render_template('production-status.html', productions=productions_data)

@app.route('/cp-status')
def cp_status():
    productions_data = get_productions()
    return render_template('cp-status.html', productions=productions_data)

@app.route('/update-production-status', methods=['POST'])
def update_production_status():
    production_id = request.form.get('productionId')
    new_status = request.form.get('status')

    conn = sqlite3.connect('BDD.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE production SET status = ? WHERE id = ?", (new_status, production_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True})

def get_ingredients():
    conn = sqlite3.connect('BDD.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM ingredient")
    ingredients = cursor.fetchall()

    conn.close()

    return [{'id': row[0], 'name': row[1], 'quantity': row[2]} for row in ingredients]

@app.route('/inventory')
def inventory():
    ingredients_data = get_ingredients()
    return render_template('inventory.html', ingredients=ingredients_data)

@app.route('/cp-stock')
def cp_stock():
    ingredients_data = get_ingredients()
    return render_template('cp-stock.html', ingredients=ingredients_data)

@app.route('/cp-order', methods=['GET'])
def show_orders():
    conn = sqlite3.connect('BDD.db')
    cursor = conn.cursor()

    email = request.args.get('email')
    status = request.args.get('status')

    query = "SELECT * FROM orders WHERE 1=1"
    params = []

    if email:
        query += " AND email_client = ?"
        params.append(email)

    if status:
        query += " AND status = ?"
        params.append(status)

    cursor.execute(query, params)
    orders = cursor.fetchall()

    ongoing_orders = [order for order in orders if order[2] != 'delivered']
    order_history = [order for order in orders if order[2] == 'delivered']

    conn.close()

    return render_template('cp-order.html', ongoing_orders=ongoing_orders, order_history=order_history)

@app.route('/chief-product')
def project_list():
    conn = sqlite3.connect('BDD.db')
    conn.row_factory = sqlite3.Row
    projects = conn.execute('SELECT * FROM projects ORDER BY status').fetchall()
    conn.close()
    
    return render_template('chief-product.html', projects=projects)

@app.route('/update_status/<int:id>', methods=['POST'])
def update_status(id):
    new_status = request.form['status']
    conn = sqlite3.connect('BDD.db')
    conn.execute('UPDATE projects SET status = ? WHERE id = ?', (new_status, id))
    conn.commit()
    conn.close()
    
    return redirect('/chief-product')

@app.route('/delete_project/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()
    return redirect('/chief-product')


@app.route('/create-project', methods=['GET', 'POST'])
def create_project():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        chief = request.form['chief']
        creator = request.form['creator']
        chemist = request.form['chemist']

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO projects (name, description, chief, creator, chemist)
            VALUES (?, ?, ?, ?, ?)
        """, (name, description, chief, creator, chemist))

        conn.commit()
        conn.close()

        return redirect(url_for('create_project'))

    chiefs = ['Elise Perrin', 'Marie Lefevre', 'Lucie Durand']
    chemists = ['Bernard Martin', 'David Bernard', 'Paul Dubois', 'Sophie Lambert', 'Julien Moret']
    creators = ['Alice Dupont', 'Pierre Laurent', 'Camille Richard']
    return render_template('create-project.html', chiefs=chiefs, chemists=chemists, creators=creators)

@app.route('/edit-product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    conn = connect_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        ingredient1 = request.form['ingredient1']
        ingredient2 = request.form['ingredient2']
        price = request.form['price']

        cursor.execute("""
            UPDATE products 
            SET name = ?, ingredient1 = ?, ingredient2 = ?, price = ? 
            WHERE id = ?
        """, (name, ingredient1, ingredient2, price, product_id))
        conn.commit()
        conn.close()

        return redirect(url_for('existing_products'))

    cursor.execute("SELECT name, ingredient1, ingredient2, price FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()

    return render_template('edit-product.html', product=product, product_id=product_id)

if __name__ == '__main__':
    app.run(debug=True)
