import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# データベースから商品一覧を取得する関数
def get_products():
    conn = sqlite3.connect("cafe_app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, category, price, description FROM PRODUCT")
    products = cursor.fetchall()
    conn.close()
    return products

# 商品一覧を表示するページ
@app.route('/products')
def show_products():
    products = get_products()  # 商品データを取得
    return render_template('product_list.html', products=products)

# データベースから入出庫データを取得する関数
def get_transactions():
    conn = sqlite3.connect("cafe_app.db")  # データベースに接続
    cursor = conn.cursor()
    
    # 入出庫データを取得（JOINして商品名も取得）
    cursor.execute("""
        SELECT 
            TRANSACTION_HISTORY.id, 
            PRODUCT.name, 
            TRANSACTION_HISTORY.quantity, 
            TRANSACTION_HISTORY.transaction_type, 
            TRANSACTION_HISTORY.transaction_date, 
            TRANSACTION_HISTORY.remarks
        FROM TRANSACTION_HISTORY
        JOIN PRODUCT ON TRANSACTION_HISTORY.product_id = PRODUCT.id
        ORDER BY TRANSACTION_HISTORY.transaction_date DESC
    """)
    
    transactions = cursor.fetchall()  # 取得したデータをリストとして格納
    conn.close()  # データベースを閉じる
    return transactions

# 入出庫データの一覧を表示するページ
@app.route('/transactions')
def show_transactions():
    transactions = get_transactions()  # データ取得
    return render_template('transaction_list.html', transactions=transactions)

# 入出庫データを追加する関数
def add_transaction(product_id, quantity, transaction_type, remarks):
    if transaction_type not in ['in', 'out']:
        transaction_type = 'in'  # デフォルトで 'in' に設定
    
    conn = sqlite3.connect("cafe_app.db", check_same_thread=False)
    cursor = conn.cursor()
    
    user_id = 1  # テストユーザーID（user_id = 1）
    
    cursor.execute("""
        INSERT INTO TRANSACTION_HISTORY (product_id, quantity, transaction_type, transaction_date, remarks, user_id)
        VALUES (?, ?, ?, datetime('now'), ?, ?)
    """, (product_id, quantity, transaction_type, remarks, user_id))
    
    conn.commit()
    conn.close()

# 入出庫データを追加するページ（フォーム表示）
@app.route('/add_transaction', methods=['GET', 'POST'])
def add_transaction_page():
    if request.method == 'POST':
        product_id = request.form['product_id']
        quantity = request.form['quantity']
        transaction_type = request.form['transaction_type']
        remarks = request.form['remarks']
        
        add_transaction(product_id, quantity, transaction_type, remarks)
        return redirect(url_for('show_transactions'))  # 追加後に一覧ページへリダイレクト

    products = get_products()  # 商品一覧を取得
    return render_template('add_transaction.html', products=products)

if __name__ == '__main__':
    app.run(debug=True)
