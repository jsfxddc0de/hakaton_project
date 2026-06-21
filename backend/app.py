from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import sqlite3
import smtplib
import ssl
from email.message import EmailMessage
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_sessions_and_profile'
app.json.ensure_ascii = False  # Исправление кодировки кириллицы в JSON

DATABASE = 'users.db'
ADMIN_PASSWORD = '1488'

SONGS = {
    1: {"title": "Евгений Дога — Вальс (Мой ласковый и нежный зверь)", "desc": "Торжественный и эмоциональный вальс, ставший символом бальных открытий."},
    2: {"title": "Георгий Свиридов — Вальс (Метель)", "desc": "Кружащийся, яркий вальс с благородным и широким русским звучанием."},
    3: {"title": "П. И. Чайковский — Октябрь. Осенняя песнь", "desc": "Глубокая и поэтичная классика, передающая тихую грусть золотой осени."},
    4: {"title": "Антонио Вивальди — Осень (Времена года)", "desc": "Энергичное и праздничное барокко, воспевающее сбор урожая и радость."},
    5: {"title": "Ян Тирсен — Waltz of the Monsters", "desc": "Уютный, сказочный и немного загадочный неоклассический вальс."}
}

EMAIL_SENDER = 'ВАШ_EMAIL@gmail.com'
EMAIL_PASSWORD = os.environ.get('EMAIL_APP_PASSWORD', 'ВАШ_ПАРОЛЬ_ПРИЛОЖЕНИЯ')
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465

def send_registration_email(recipient_email, recipient_fio):
    if not EMAIL_PASSWORD or EMAIL_PASSWORD == 'ВАШ_ПАРОЛЬ_ПРИЛОЖЕНИЯ':
        print("Внимание: Настройка почты не завершена. Письмо не отправлено.")
        return
    msg = EmailMessage()
    msg['Subject'] = 'Успешная регистрация на Осенний Бал 2026!'
    msg['From'] = EMAIL_SENDER
    msg['To'] = recipient_email
    msg.set_content(f"Здравствуйте, {recipient_fio}!\n\nВаша заявка на Осенний Бал успешно принята.\nВы можете войти на сайт, используя свой Email и проголосовать за любимую музыку!")
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT, context=context) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fio TEXT NOT NULL,
            class_group TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            phone TEXT,
            wishes TEXT,
            ip_address TEXT NOT NULL,
            reg_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            user_email TEXT PRIMARY KEY,
            song_id INTEGER NOT NULL,
            FOREIGN KEY(user_email) REFERENCES users(email)
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    user_email = session.get('user_email')
    user_fio = session.get('user_fio')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('SELECT song_id, COUNT(*) FROM votes GROUP BY song_id')
    votes_raw = cursor.fetchall()
    votes_dict = {song_id: count for song_id, count in votes_raw}

    cursor.execute('SELECT COUNT(*) FROM votes')
    total_votes = cursor.fetchone()[0]

    user_vote = None
    if user_email:
        cursor.execute('SELECT song_id FROM votes WHERE user_email = ?', (user_email,))
        row = cursor.fetchone()
        if row:
            user_vote = row[0]

    conn.close()

    songs_data = []
    for s_id, s_info in SONGS.items():
        count = votes_dict.get(s_id, 0)
        percent = round((count / total_votes * 100), 1) if total_votes > 0 else 0
        songs_data.append({
            'id': s_id,
            'title': s_info['title'],
            'desc': s_info['desc'],
            'votes': count,
            'percent': percent,
            'is_current': (s_id == user_vote)
        })

    return render_template('index.html', 
                           user_email=user_email, 
                           user_fio=user_fio, 
                           songs=songs_data, 
                           total_votes=total_votes)

@app.route('/vote/<int:song_id>', methods=['POST'])
def vote(song_id):
    user_email = session.get('user_email')
    if not user_email:
        flash("Чтобы проголосовать, войдите в систему или зарегистрируйтесь!", "warning")
        return redirect(url_for('login'))
    
    if song_id not in SONGS:
        flash("Неверный выбор песни.", "error")
        return redirect(url_for('home'))

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO votes (user_email, song_id) VALUES (?, ?)', (user_email, song_id))
    conn.commit()
    conn.close()

    flash(f"Ваш голос за '{SONGS[song_id]['title']}' успешно учтен!", "success")
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        fio = request.form['fio'].strip()
        class_group = request.form['class_group'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        phone = request.form.get('phone', '').strip()
        wishes = request.form.get('wishes', '').strip()
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)

        if not fio or not class_group or not email or not password:
            error = "Пожалуйста, заполните все обязательные поля."
            return render_template('register.html', error=error)

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            error = "Пользователь с таким Email уже зарегистрирован."
            conn.close()
        else:
            cursor.execute(
                'INSERT INTO users (fio, class_group, email, password, phone, wishes, ip_address) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                (fio, class_group, email, password, phone, wishes, ip_address)
            )
            conn.commit()
            conn.close()
            
            send_registration_email(email, fio)
            session['user_email'] = email
            session['user_fio'] = fio
            flash("Вы успешно зарегистрировались!", "success")
            return redirect(url_for('home'))
            
    return render_template('register.html', error=error)

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
            session['user_email'] = user_data[1]
            session['user_fio'] = user_data[0]
            flash(f"Рады видеть вас снова, {user_data[0]}!", 'info')
            return redirect(url_for('home'))
        else:
            error = "Неверный Email или пароль."
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    session.pop('user_fio', None)
    flash("Вы вышли из системы.", 'info')
    return redirect(url_for('home'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('login'))

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    if request.method == 'POST':
        new_phone = request.form.get('phone', '').strip()
        new_wishes = request.form.get('wishes', '').strip()
        cursor.execute('UPDATE users SET phone = ?, wishes = ? WHERE email = ?', (new_phone, new_wishes, user_email))
        conn.commit()
        flash("Профиль успешно сохранен!", 'success')

    cursor.execute('SELECT fio, class_group, email, phone, wishes FROM users WHERE email = ?', (user_email,))
    user_data = cursor.fetchone()
    conn.close()

    user_dict = {
        'fio': user_data[0], 'class_group': user_data[1], 'email': user_data[2],
        'phone': user_data[3] if user_data[3] else '', 'wishes': user_data[4] if user_data[4] else ''
    }
    return render_template('profile.html', user=user_dict)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            error = 'Неверный пароль admin.'
    return render_template('admin_login.html', error=error)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

# ОБНОВЛЕННАЯ АДМИНКА
@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
        
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # 1. Загружаем пользователей И их голоса (LEFT JOIN)
    cursor.execute('''
        SELECT u.id, u.fio, u.class_group, u.email, u.password, u.phone, u.wishes, u.ip_address, u.reg_time, v.song_id 
        FROM users u 
        LEFT JOIN votes v ON u.email = v.user_email 
        ORDER BY u.id DESC
    ''')
    users_raw = cursor.fetchall()
    
    # Конвертируем сырые данные пользователей в удобный список словарей
    users = []
    for u in users_raw:
        song_id = u[9]
        song_title = SONGS.get(song_id, {}).get('title', 'Не голосовал')
        users.append({
            'id': u[0], 'fio': u[1], 'class_group': u[2], 'email': u[3],
            'password': u[4], 'phone': u[5], 'wishes': u[6], 'ip_address': u[7],
            'reg_time': u[8], 'voted_song': song_title
        })

    # 2. Вычисляем общую статистику голосов для отображения в админке
    cursor.execute('SELECT song_id, COUNT(*) FROM votes GROUP BY song_id')
    votes_raw = cursor.fetchall()
    votes_dict = {song_id: count for song_id, count in votes_raw}
    
    cursor.execute('SELECT COUNT(*) FROM votes')
    total_votes = cursor.fetchone()[0]
    
    stats = []
    for s_id, s_info in SONGS.items():
        count = votes_dict.get(s_id, 0)
        percent = round((count / total_votes * 100), 1) if total_votes > 0 else 0
        stats.append({
            'title': s_info['title'],
            'votes': count,
            'percent': percent
        })

    conn.close()
    return render_template('admin.html', users=users, stats=stats, total_votes=total_votes)

# ОБНОВЛЕННОЕ API
@app.route('/api/users')
def api_users():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized', 'message': 'Admin login required'}), 401
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # LEFT JOIN для получения информации о песне
    cursor.execute('''
        SELECT u.id, u.fio, u.class_group, u.email, u.phone, u.wishes, u.reg_time, v.song_id 
        FROM users u 
        LEFT JOIN votes v ON u.email = v.user_email 
        ORDER BY u.id DESC
    ''')
    users_raw = cursor.fetchall()
    conn.close()

    users_json = []
    for u in users_raw:
        song_id = u[7]
        song_title = SONGS.get(song_id, {}).get('title') if song_id else None
        
        users_json.append({
            'id': u[0],
            'fio': u[1],
            'class_group': u[2],
            'email': u[3],
            'phone': u[4],
            'wishes': u[5],
            'registration_time': u[6],
            'voted_song_id': song_id,          # ID проголосованной композиции (или null)
            'voted_song_title': song_title     # Название проголосованной композиции (или null)
        })
    
    return jsonify(users_json)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)