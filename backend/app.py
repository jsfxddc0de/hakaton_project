from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DATABASE = 'users.db'


# Функция для подключения к БД и создания таблицы
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            ip_address TEXT NOT NULL,
            reg_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


# Перенаправление с главной на регистрацию
@app.route('/')
def home():
    return redirect(url_for('register'))


# Страница регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # В реальных проектах пароли шифруют, но для теста оставим так

        # Получаем IP-адрес пользователя
        # Если запускаешь локально, у всех будет 127.0.0.1, но если зайдешь с телефона — будет локальный IP телефона
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)

        # Запись в базу данных
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (username, password, ip_address) VALUES (?, ?, ?)',
            (username, password, ip_address)
        )
        conn.commit()
        conn.close()

        return render_template('success.html', username=username)

    return render_template('register.html')


# Админ-панель
@app.route('/admin')
def admin():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, password, ip_address, reg_time FROM users ORDER BY id DESC')
    users = cursor.fetchall()
    conn.close()
    return render_template('admin.html', users=users)


if __name__ == '__main__':
    init_db()
    # host='0.0.0.0' позволяет заходить на сайт с других устройств в твоей Wi-Fi сети (например, с телефона)
    app.run(debug=True, host='0.0.0.0', port=5000)
