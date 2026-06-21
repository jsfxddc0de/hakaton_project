from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.utils import secure_filename
import sqlite3
import smtplib
import ssl
from email.message import EmailMessage
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_sessions_and_profile'
app.json.ensure_ascii = False  # Исправление кодировки кириллицы в JSON

# --- НАСТРОЙКИ ЗАГРУЗКИ ФАЙЛОВ (АВАТАРОК) ---
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # Ограничение размера файла: 2 МБ

# Создаем папку для аватарок, если её нет
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

# Проверка расширения файла
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_registration_email(recipient_email, recipient_fio):
    if not EMAIL_PASSWORD or EMAIL_PASSWORD == 'ВАШ_ПАРОЛЬ_ПРИЛОЖЕНИЯ':
        print("Внимание: Настройка почты не завершена. Письмо не отправлено.")
        return
    msg = EmailMessage()
    msg['Subject'] = 'Успешная регистрация на Осенний Бал 2026!'
    msg['From'] = EMAIL_SENDER
    msg['To'] = recipient_email
    msg.set_content(f"Здравствуйте, {recipient_fio}!\n\nВаша заявка на Осенний Бал успешно принята.\nВы можете войти на сайт, используя свой Email, настроить профиль (добавить аватарку) и проголосовать за любимую музыку!")
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT, context=context) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")

# Инициализация БД (добавлено поле avatar)
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
            avatar TEXT, -- Новое поле для хранения пути к файлу аватарки
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

# Главная страница
@app.route('/')
def home():
    user_email = session.get('user_email')
    user_fio = session.get('user_fio')
    user_avatar = None

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Получаем актуальную аватарку пользователя
    if user_email:
        cursor.execute('SELECT avatar, fio FROM users WHERE email = ?', (user_email,))
        row = cursor.fetchone()
        if row:
            user_avatar = row[0]
            user_fio = row[1] # Синхронизируем ФИО на случай изменений

    # Считаем голоса
    cursor.execute('SELECT song_id, COUNT(*) FROM votes GROUP BY song_id')
    votes_raw = cursor.fetchall()
    votes_dict = {song_id: count for song_id, count in votes_raw}

    cursor.execute('SELECT COUNT(*) FROM votes')
    total_votes = cursor.fetchone()[0]

    user_vote = None
    if user_email:
        cursor.execute('SELECT song_id FROM votes WHERE user_email = ?', (user_email,))
        row_vote = cursor.fetchone()
        if row_vote:
            user_vote = row_vote[0]

    conn.close()

    songs_data = []
    for s_id, s_info in SONGS.items():
        count = votes_dict.get(s_id, 0)
        percent = round((count / total_votes * 100), 1) if total_votes > 0 else 0
        songs_data.append({
            'id': s_id, 'title': s_info['title'], 'desc': s_info['desc'],
            'votes': count, 'percent': percent, 'is_current': (s_id == user_vote)
        })

    return render_template('index.html', 
                           user_email=user_email, 
                           user_fio=user_fio, 
                           user_avatar=user_avatar,
                           songs=songs_data, 
                           total_votes=total_votes)

@app.route('/vote/<int:song_id>', methods=['POST'])
def vote(song_id):
    user_email = session.get('user_email')
    if not user_email:
        flash("Чтобы проголосовать, войдите в систему!", "warning")
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO votes (user_email, song_id) VALUES (?, ?)', (user_email, song_id))
    conn.commit()
    conn.close()
    flash("Ваш голос успешно учтен!", "success")
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

# ОБНОВЛЕННЫЙ ПРОФИЛЬ (С ЗАГРУЗКОЙ АВАТАРКИ)
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
        
        # Обработка загрузки файла аватарки
        avatar_file = request.files.get('avatar')
        avatar_filename = None

        if avatar_file and avatar_file.filename != '':
            if allowed_file(avatar_file.filename):
                # Создаем безопасное уникальное имя файла на основе email пользователя
                ext = avatar_file.filename.rsplit('.', 1)[1].lower()
                safe_email_prefix = secure_filename(user_email.replace('@', '_').replace('.', '_'))
                avatar_filename = f"avatar_{safe_email_prefix}.{ext}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], avatar_filename)
                
                # Сохраняем файл в static/uploads
                avatar_file.save(filepath)
                
                # Записываем имя файла аватарки в БД
                cursor.execute('UPDATE users SET phone = ?, wishes = ?, avatar = ? WHERE email = ?', 
                               (new_phone, new_wishes, avatar_filename, user_email))
            else:
                flash("Недопустимый формат файла! Разрешены только: png, jpg, jpeg, gif", "error")
        else:
            # Если файл не загружали, обновляем только текстовые поля
            cursor.execute('UPDATE users SET phone = ?, wishes = ? WHERE email = ?', 
                           (new_phone, new_wishes, user_email))
            
        conn.commit()
        flash("Профиль успешно сохранен!", 'success')

    cursor.execute('SELECT fio, class_group, email, phone, wishes, avatar FROM users WHERE email = ?', (user_email,))
    user_data = cursor.fetchone()
    conn.close()

    user_dict = {
        'fio': user_data[0], 
        'class_group': user_data[1], 
        'email': user_data[2],
        'phone': user_data[3] if user_data[3] else '', 
        'wishes': user_data[4] if user_data[4] else '',
        'avatar': user_data[5] # Передаем имя файла аватарки
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
    
    cursor.execute('''
        SELECT u.id, u.fio, u.class_group, u.email, u.password, u.phone, u.wishes, u.ip_address, u.reg_time, v.song_id, u.avatar 
        FROM users u 
        LEFT JOIN votes v ON u.email = v.user_email 
        ORDER BY u.id DESC
    ''')
    users_raw = cursor.fetchall()
    
    users = []
    for u in users_raw:
        song_id = u[9]
        song_title = SONGS.get(song_id, {}).get('title', 'Не голосовал')
        users.append({
            'id': u[0], 'fio': u[1], 'class_group': u[2], 'email': u[3],
            'password': u[4], 'phone': u[5], 'wishes': u[6], 'ip_address': u[7],
            'reg_time': u[8], 'voted_song': song_title, 'avatar': u[10] # Передаем аватарку в админку
        })

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
            'title': s_info['title'], 'votes': count, 'percent': percent
        })

    conn.close()
    return render_template('admin.html', users=users, stats=stats, total_votes=total_votes)

# ОБНОВЛЕННЫЙ API (С АВАТАРКОЙ)
@app.route('/api/users')
def api_users():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized', 'message': 'Admin login required'}), 401
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.id, u.fio, u.class_group, u.email, u.phone, u.wishes, u.reg_time, v.song_id, u.avatar 
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
        
        # Формируем полный URL до аватарки, если она загружена
        avatar_url = url_for('static', filename=f'uploads/{u[8]}', _external=True) if u[8] else f"https://ui-avatars.com/api/?name={u[1]}&background=random&size=128"

        users_json.append({
            'id': u[0],
            'fio': u[1],
            'class_group': u[2],
            'email': u[3],
            'phone': u[4],
            'wishes': u[5],
            'registration_time': u[6],
            'voted_song_id': song_id,
            'voted_song_title': song_title,
            'avatar_url': avatar_url # Ссылка на аватарку в API
        })
    
    return jsonify(users_json)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)