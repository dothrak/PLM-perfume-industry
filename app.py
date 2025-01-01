from flask import Flask, request, redirect, url_for, render_template
import sqlite3

app = Flask(__name__)

# Fonction pour se connecter à la base de données
def connect_db():
    conn = sqlite3.connect('BDD.db')
    return conn

@app.route('/')
def index():
    return render_template('index.html')

# Route pour la page de création du produit
@app.route('/create-product', methods=['GET'])
def create_product():
    return render_template('create-product.html')

# Route pour ajouter le produit à la BDD
@app.route('/add_product', methods=['POST'])
def add_product():
    name = request.form['name']
    ingredient1 = request.form['ingredient1']
    ingredient2 = request.form['ingredient2']
    prix = request.form['price']

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO produit (name, ingredient1, ingredient2, prix)
        VALUES (?, ?, ?, ?)
    """, (name, ingredient1, ingredient2, prix))
    conn.commit()
    conn.close()

    return redirect(url_for('create_product'))

@app.route('/existing-products')
def existing_products():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, ingredient1, ingredient2, prix FROM produit ORDER BY id ASC")
    products = cursor.fetchall()
    conn.close()

    return render_template('existing-products.html', products=products)

@app.route('/delete-product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produit WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True)
