from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import sqlite3
import smtplib
import ssl
from email.message import EmailMessage
import os # Для получения Email-пароля из переменных окружения, безопаснее

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_sessions_and_profile' # Твой секретный ключ

# --- ДОБАВЬ ЭТУ СТРОКУ СЮДА ---
app.json.ensure_ascii = False 
# ------------------------------

DATABASE = 'users.db'
ADMIN_PASSWORD = '1488'

# --- НАСТРОЙКИ EMAIL ---
# ВАЖНО: В реальных проектах эти данные хранят в переменных окружения или файле конфигурации,
# а не прямо в коде! Для простоты демонстрации оставим тут.
# Для Gmail нужно будет включить "Пароли приложений" если включена 2ФА.
EMAIL_SENDER = 'gika.savinov@gmail.com' # Email, с которого будут отправляться письма
# Пароль для вашего email. Для Gmail это "Пароль приложения".
EMAIL_PASSWORD = os.environ.get('EMAIL_APP_PASSWORD', 'j012qewj12') 
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465 # SSL порт

# Функция для отправки Email
def send_registration_email(recipient_email, recipient_fio):
    if not EMAIL_PASSWORD:
        print("Ошибка: Пароль для отправки Email не задан. Письмо не будет отправлено.")
        return

    msg = EmailMessage()
    msg['Subject'] = 'Успешная регистрация на Осенний Бал 2026!'
    msg['From'] = EMAIL_SENDER
    msg['To'] = recipient_email
    
    msg.set_content(f"""
    Здравствуйте, {recipient_fio}!

    Поздравляем! Ваша заявка на участие в Осеннем Бале 2026 успешно принята.

    Дата: 31 октября 2026 года
    Время: 18:00
    Место: Главный Колонный Зал Торжеств

    Ваши данные для входа в личный кабинет:
    Email: {recipient_email}
    (Пароль тот, который вы указывали при регистрации)

    Вы можете изменить необязательные данные в своем профиле на сайте.

    До встречи на балу!
    С уважением,
    Оргкомитет Осеннего Бала
    """)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT, context=context) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"Email успешно отправлен на {recipient_email}")
    except Exception as e:
        print(f"Ошибка при отправке Email на {recipient_email}: {e}")

# Функция для подключения к БД и создания таблицы
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # Обновленная таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fio TEXT NOT NULL,
            class_group TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE, -- Email теперь уникальный и используется для входа
            password TEXT NOT NULL,
            phone TEXT,               -- Необязательное
            wishes TEXT,              -- Необязательное
            ip_address TEXT NOT NULL,
            reg_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# 1. Главная страница (Осенний бал)
@app.route('/')
def home():
    user_email = session.get('user_email')
    user_fio = session.get('user_fio')
    return render_template('index.html', user_email=user_email, user_fio=user_fio)

# 2. Регистрация участника
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        fio = request.form['fio'].strip()
        class_group = request.form['class_group'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        phone = request.form.get('phone', '').strip() # Необязательное поле
        wishes = request.form.get('wishes', '').strip() # Необязательное поле
        
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)

        # Проверка обязательных полей
        if not fio or not class_group or not email or not password:
            error = "Пожалуйста, заполните все обязательные поля (ФИО, Класс/Группа, Email, Пароль)."
            return render_template('register.html', error=error)

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Проверяем, существует ли уже пользователь с таким Email
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            error = "Пользователь с таким Email уже зарегистрирован."
            conn.close()
        else:
            try:
                # Вставляем нового пользователя со всеми полями
                cursor.execute(
                    '''INSERT INTO users (fio, class_group, email, password, phone, wishes, ip_address) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                    (fio, class_group, email, password, phone, wishes, ip_address)
                )
                conn.commit()
                
                # Отправляем уведомление на Email
                send_registration_email(email, fio)

                # Автоматически авторизуем пользователя после успешной регистрации
                session['user_email'] = email
                session['user_fio'] = fio # Сохраняем ФИО для отображения на главной
                flash(f"Заявка успешно принята, {fio}! Письмо с подтверждением отправлено на {email}.", 'success')
                return redirect(url_for('home'))
            except Exception as e:
                conn.rollback() # Откатываем изменения при ошибке
                error = f"Произошла ошибка при регистрации: {e}"
            finally:
                conn.close()
            
    return render_template('register.html', error=error)

# 3. Вход пользователя
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT fio, email FROM users WHERE email = ? AND password = ?', (email, password))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            session['user_email'] = user_data[1] # Сохраняем email в сессии
            session['user_fio'] = user_data[0] # Сохраняем ФИО в сессии
            flash(f"Добро пожаловать, {user_data[0]}!", 'info')
            return redirect(url_for('home'))
        else:
            error = "Неверный Email или пароль."
            
    return render_template('login.html', error=error)

# 4. Выход пользователя
@app.route('/logout')
def logout():
    session.pop('user_email', None)
    session.pop('user_fio', None)
    flash("Вы вышли из аккаунта.", 'info')
    return redirect(url_for('home'))

# 5. Профиль пользователя (просмотр и редактирование)
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_email = session.get('user_email')
    if not user_email:
        flash("Пожалуйста, войдите, чтобы получить доступ к профилю.", 'warning')
        return redirect(url_for('login'))

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    if request.method == 'POST':
        # Обновляем только необязательные поля
        new_phone = request.form.get('phone', '').strip()
        new_wishes = request.form.get('wishes', '').strip()
        
        try:
            cursor.execute(
                'UPDATE users SET phone = ?, wishes = ? WHERE email = ?',
                (new_phone, new_wishes, user_email)
            )
            conn.commit()
            flash("Ваш профиль успешно обновлен!", 'success')
        except Exception as e:
            conn.rollback()
            flash(f"Ошибка при обновлении профиля: {e}", 'error')

    # Всегда получаем актуальные данные пользователя для отображения
    cursor.execute('SELECT fio, class_group, email, phone, wishes FROM users WHERE email = ?', (user_email,))
    user_data = cursor.fetchone()
    conn.close()

    if not user_data: # Если по какой-то причине пользователь не найден (хотя должен быть)
        session.pop('user_email', None)
        session.pop('user_fio', None)
        flash("Ошибка: Ваш профиль не найден. Пожалуйста, войдите снова.", 'error')
        return redirect(url_for('login'))

    user_dict = {
        'fio': user_data[0],
        'class_group': user_data[1],
        'email': user_data[2],
        'phone': user_data[3] if user_data[3] else '', # Пустая строка вместо None
        'wishes': user_data[4] if user_data[4] else ''
    }
    return render_template('profile.html', user=user_dict)


# 6. Вход в админку (пароль 1488)
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        entered_password = request.form.get('password')
        if entered_password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            error = 'Неверный код-пароль!'
    return render_template('admin_login.html', error=error)

# 7. Выход из админки
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

# 8. Сама админка
@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
        
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # Выбираем все поля для админ-панели
    cursor.execute('SELECT id, fio, class_group, email, password, phone, wishes, ip_address, reg_time FROM users ORDER BY id DESC')
    users = cursor.fetchall()
    conn.close()
    return render_template('admin.html', users=users)

# 9. API для получения данных о пользователях в JSON (только для авторизованных админов)
@app.route('/api/users')
def api_users():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized', 'message': 'Admin login required'}), 401
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # Выбираем все поля, КРОМЕ ПАРОЛЯ И IP (безопасность)
    cursor.execute('SELECT id, fio, class_group, email, phone, wishes, reg_time FROM users ORDER BY id DESC')
    users_raw = cursor.fetchall()
    conn.close()

    users_json = []
    for user_tuple in users_raw:
        users_json.append({
            'id': user_tuple[0],
            'fio': user_tuple[1],
            'class_group': user_tuple[2],
            'email': user_tuple[3],
            'phone': user_tuple[4],
            'wishes': user_tuple[5],
            'registration_time': user_tuple[6]
        })
    
    return jsonify(users_json)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)