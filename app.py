from flask import Flask, request, jsonify, render_template
import sqlite3
import json
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Функция для подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# Инициализация базы данных
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            clicks INTEGER DEFAULT 0,
            gems INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Страница входа
@app.route('/login')
def login_page():
    return render_template('login.html')

# Страница регистрации
@app.route('/register')
def register_page():
    return render_template('register.html')

# Страница магазина
@app.route('/shop')
def shop_page():
    return render_template('shop.html')

# Регистрация пользователя
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']
    
    hashed_password = generate_password_hash(password)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('INSERT INTO users (username, password, clicks, gems) VALUES (?, ?, ?, ?)', (username, hashed_password, 0, 0))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Регистрация успешна!'})

# Вход пользователя
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    user = cursor.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    
    if user and check_password_hash(user['password'], password):
        return jsonify({'success': True, 'message': 'Вход успешен!', 'clicks': user['clicks'], 'gems': user['gems']})
    else:
        return jsonify({'success': False, 'message': 'Неверное имя пользователя или пароль'})

# Получение акций
@app.route('/actions', methods=['GET'])
def actions():
    with open('actions.json', 'r', encoding='utf-8') as file:
        actions = json.load(file)
    return jsonify(actions)

# Покупка акции
@app.route('/buy-action', methods=['POST'])
def buy_action():
    data = request.json
    username = data['username']
    action_index = data['actionIndex']
    
    # Получаем данные о пользователе
    conn = get_db_connection()
    cursor = conn.cursor()
    user = cursor.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    
    if user:
        with open('actions.json', 'r', encoding='utf-8') as file:
            actions = json.load(file)
        
        action = actions[action_index]
        action_type = action['type']
        action_price = action['price']
        action_count = action['count']
        
        if action_type == 'click':
            if user['gems'] >= action_price:
                new_gems = user['gems'] - action_price
                new_clicks = user['clicks'] + action_count
                cursor.execute('UPDATE users SET gems = ?, clicks = ? WHERE username = ?',
                (new_gems, new_clicks, username))
                conn.commit()
                return jsonify({'success': True, 'message': 'Покупка успешна!'})
            else:
                return jsonify({'success': False, 'message': 'Недостаточно кристаллов для покупки!'})
        
        elif action_type == 'gems':
            if user['clicks'] >= action_price:
                new_clicks = user['clicks'] - action_price
                new_gems = user['gems'] + action_count
                cursor.execute('UPDATE users SET clicks = ?, gems = ? WHERE username = ?', (new_clicks, new_gems, username))
                conn.commit()
                return jsonify({'success': True, 'message': 'Покупка успешна!'})
            else:
                return jsonify({'success': False, 'message': 'Недостаточно кликов для покупки!'})
    conn.close()
    return jsonify({'success': False, 'message': 'Пользователь не найден!'})

# Обработка клика
@app.route('/click', methods=['POST'])
def click():
    data = request.json
    username = data['username']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    user = cursor.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    
    if user:
        new_clicks = user['clicks'] + 1  # Увеличиваем только клики
        cursor.execute('UPDATE users SET clicks = ? WHERE username = ?', (new_clicks, username))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'clicks': new_clicks, 'gems': user['gems']})  # Возвращаем текущее количество кликов и кристаллов
    
    conn.close()
    return jsonify({'success': False, 'message': 'Пользователь не найден!'})

if __name__ == '__main__':
    init_db()  # Инициализация базы данных
    app.run(host='0.0.0.0', port=5000, debug=False)
