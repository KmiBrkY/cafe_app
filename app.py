import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # フラッシュメッセージ用

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

# 商品を追加する関数
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        price = request.form['price']

        # 入力チェック
        if not name or not category or not price:
            flash('すべての必須項目を入力してください。', 'error')
            return render_template('product_form.html')

        # SQLiteにデータを追加
        try:
            conn = sqlite3.connect("cafe_app.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO PRODUCT (name, description, category, price) VALUES (?, ?, ?, ?)",
                           (name, description, category, price))
            conn.commit()
            conn.close()
            flash('商品が追加されました！', 'success')
        except Exception as e:
            flash(f'エラーが発生しました: {e}', 'error')

        return redirect(url_for('show_products'))  # 商品一覧ページにリダイレクト

    return render_template('product_form.html')

# 商品を編集する関数
@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    # データベースから商品データを取得
    conn = sqlite3.connect("cafe_app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, category, price FROM PRODUCT WHERE id=?", (product_id,))
    product = cursor.fetchone()
    conn.close()

    if not product:
        flash('指定された商品が見つかりません。', 'error')
        return redirect(url_for('show_products'))  # 商品一覧ページにリダイレクト

    if request.method == 'POST':
        # フォームから送信されたデータを取得
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        price = request.form['price']

        # 入力チェック（必須項目）
        if not name or not category or not price:
            flash('すべての必須項目を入力してください。', 'error')
            return render_template('edit_product.html', product=product)

        # データベースを更新
        conn = sqlite3.connect("cafe_app.db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE PRODUCT
            SET name = ?, description = ?, category = ?, price = ?
            WHERE id = ?
        """, (name, description, category, price, product_id))
        conn.commit()
        conn.close()

        flash('商品が更新されました！', 'success')
        return redirect(url_for('show_products'))  # 商品一覧ページにリダイレクト

    return render_template('edit_product.html', product=product)  # 商品データをフォームに渡す

# 商品を削除する関数
@app.route('/delete_product/<int:product_id>', methods=['GET'])
def delete_product(product_id):
    conn = sqlite3.connect("cafe_app.db")
    cursor = conn.cursor()

    # 商品データを削除
    cursor.execute("DELETE FROM PRODUCT WHERE id=?", (product_id,))
    conn.commit()
    conn.close()

    flash('商品が削除されました！', 'success')
    return redirect(url_for('show_products'))  # 商品一覧ページにリダイレクト

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
        
        # 入力チェック
        if not quantity or not product_id:
            flash('商品と数量を入力してください。', 'error')
            return render_template('add_transaction.html', products=get_products())
        
        add_transaction(product_id, quantity, transaction_type, remarks)
        flash('取引が追加されました！', 'success')
        return redirect(url_for('show_transactions'))  # 取引履歴ページにリダイレクト

    products = get_products()  # 商品一覧を取得
    return render_template('add_transaction.html', products=products)

# 取引データの削除
@app.route('/delete_transaction/<int:transaction_id>', methods=['GET'])
def delete_transaction(transaction_id):
    conn = sqlite3.connect("cafe_app.db")
    cursor = conn.cursor()

    # 取引データを削除
    cursor.execute("DELETE FROM TRANSACTION_HISTORY WHERE id=?", (transaction_id,))
    conn.commit()
    conn.close()

    flash('取引が削除されました！', 'success')
    return redirect(url_for('show_transactions'))  # 取引一覧ページにリダイレクト

# 入出庫データの一覧を表示するページ
@app.route('/transactions')
def show_transactions():
    transactions = get_transactions()  # データ取得
    return render_template('transaction_list.html', transactions=transactions)

@app.route('/edit_transaction/<int:transaction_id>', methods=['GET', 'POST'])
def edit_transaction(transaction_id):
    conn = sqlite3.connect("cafe_app.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            TRANSACTION_HISTORY.id, 
            TRANSACTION_HISTORY.product_id, 
            TRANSACTION_HISTORY.quantity, 
            TRANSACTION_HISTORY.transaction_type, 
            TRANSACTION_HISTORY.transaction_date, 
            TRANSACTION_HISTORY.remarks
        FROM TRANSACTION_HISTORY
        WHERE TRANSACTION_HISTORY.id = ?
    """, (transaction_id,))
    transaction = cursor.fetchone()
    conn.close()

    if request.method == 'POST':
        product_id = request.form['product_id']
        quantity = request.form['quantity']
        transaction_type = request.form['transaction_type']
        remarks = request.form['remarks']

        # 入力チェック
        if not product_id or not quantity:
            flash('商品と数量を入力してください。', 'error')
            return render_template('edit_transaction.html', transaction=transaction, products=get_products())

        conn = sqlite3.connect("cafe_app.db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE TRANSACTION_HISTORY
            SET product_id = ?, quantity = ?, transaction_type = ?, remarks = ?
            WHERE id = ?
        """, (product_id, quantity, transaction_type, remarks, transaction_id))
        conn.commit()
        conn.close()

        flash('取引が更新されました！', 'success')
        return redirect(url_for('show_transactions'))  # 取引一覧ページにリダイレクト

    # GET リクエストの場合は、編集フォームを表示
    return render_template('edit_transaction.html', transaction=transaction, products=get_products())

if __name__ == '__main__':
    app.run(debug=True)
