from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import smtplib
import ssl
from email.message import EmailMessage
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_sessions_and_profile'
app.json.ensure_ascii = False  # Исправление кодировки кириллицы в JSON

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DATABASE = 'users.db'
ADMIN_PASSWORD = '1488'

# Список музыкальных композиций для голосования
SONGS = {
    1: {
        "title": "Евгений Дога — Вальс (Мой ласковый и нежный зверь)", 
        "desc": "Торжественный и эмоциональный вальс, ставший символом бальных открытий.",
        "audio_url": "https://upload.wikimedia.org/wikipedia/commons/2/20/Chopin_Waltz_in_C_sharp_minor_Op._64_No._2_performed_by_Luke_Faulkner.mp3"
    },
    2: {
        "title": "Георгий Свиридов — Вальс (Метель)", 
        "desc": "Кружащийся, яркий вальс с благородным и широким русским звучанием.",
        "audio_url": "https://upload.wikimedia.org/wikipedia/commons/7/70/Tchaikovsky_-_Waltz_of_the_Flowers_-_Peabody_Symphony_Orchestra.mp3"
    },
    3: {
        "title": "П. И. Чайковский — Октябрь. Осенняя песнь", 
        "desc": "Глубокая и поэтичная классика, передающая тихую грусть золотой осени.",
        "audio_url": "https://upload.wikimedia.org/wikipedia/commons/3/30/Chopin_Nocturne_Op._9_No._2_in_E_flat_major_performed_by_Luke_Faulkner.mp3"
    },
    4: {
        "title": "Антонио Вивальди — Осень (Времена года)", 
        "desc": "Энергичное и праздничное барокко, воспевающее сбор урожая и радость.",
        "audio_url": "https://upload.wikimedia.org/wikipedia/commons/3/3d/07_-_Vivaldi_Autumn_mvt_1_Allegro_-_John_Harrison_violin.mp3"
    },
    5: {
        "title": "Ян Тирсен — Waltz of the Monsters", 
        "desc": "Уютный, сказочный и немного загадочный неоклассический вальс.",
        "audio_url": "https://upload.wikimedia.org/wikipedia/commons/e/ec/Erik_Satie_-_Gymnopedie_No._1_-_arr._violin_and_piano.mp3"
    }
}

# Настройки почты (замени на свои данные)
EMAIL_SENDER = 'gika.savinov@gmail.com'
EMAIL_PASSWORD = os.environ.get('basr ksqv gbkq uvlv')
ADMIN_EMAIL = 'dydlikkbas@gmail.com'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_email(to_email, subject, body):
    if not EMAIL_PASSWORD or EMAIL_PASSWORD == 'ВАШ_ПАРОЛЬ_ПРИЛОЖЕНИЯ':
        print(f"Внимание: Настройка почты пропущена. Письмо на {to_email} не отправлено.")
        return False
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = to_email
    msg.set_content(body)
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT, context=context) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"Ошибка отправки почты: {e}")
        return False

# Письма-уведомления
def notify_admin_new_app(fio, event_title, email):
    subject = f"🔔 Новая заявка на {event_title}: {fio}"
    body = f"Участник {fio} ({email}) подал заявку на мероприятие '{event_title}'.\nУправление заявками доступно в админке: http://127.0.0.1:5000/admin"
    send_email(ADMIN_EMAIL, subject, body)

def notify_user_app_status(email, fio, event_title, status):
    status_ru = "ОДОБРЕНА" if status == 'approved' else "ОТКЛОНЕНА"
    subject = f"✉️ Обновление статуса заявки: {event_title}"
    body = f"Здравствуйте, {fio}!\n\nСтатус вашей заявки на мероприятие '{event_title}' был изменен на: {status_ru}.\nПосмотреть статус всех своих заявок вы можете в профиле: http://127.0.0.1:5000/profile"
    send_email(email, subject, body)

# Инициализация БД
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # 1. Таблица пользователей (Профили)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fio TEXT NOT NULL,
            class_group TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL, -- Будет содержать безопасный ХЕШ
            phone TEXT,
            avatar TEXT,
            ip_address TEXT NOT NULL,
            reg_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Таблица мероприятий (Events)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            date_str TEXT NOT NULL,
            location TEXT NOT NULL
        )
    ''')
    
    # 3. Таблица заявок (Applications)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            event_id INTEGER NOT NULL,
            wishes TEXT,
            status TEXT DEFAULT 'pending', -- 'pending' (Новая), 'approved' (Подтверждена), 'rejected' (Отклонена)
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_email) REFERENCES users(email),
            FOREIGN KEY(event_id) REFERENCES events(id),
            UNIQUE(user_email, event_id) -- Предотвращает дубли заявок
        )
    ''')
    
    # 4. Таблица голосов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            user_email TEXT PRIMARY KEY,
            song_id INTEGER NOT NULL,
            FOREIGN KEY(user_email) REFERENCES users(email)
        )
    ''')
    
    # Наполняем базу мероприятиями, если они отсутствуют
    cursor.execute('SELECT COUNT(*) FROM events')
    if cursor.fetchone()[0] == 0:
        events_list = [
            (1, "Осенний Бал 2026", "31 октября 2026 в 18:00", "Главный Колонный Зал Трапезной"),
            (2, "Мастер-класс по венскому вальсу", "24 октября 2026 в 15:00", "Малый репетиционный зал"),
            (3, "Творческий вечер поэзии 'Листопад'", "05 ноября 2026 в 19:00", "Литературная гостиная")
        ]
        cursor.executemany('INSERT INTO events (id, title, date_str, location) VALUES (?, ?, ?, ?)', events_list)

    conn.commit()
    conn.close()

# Главная страница
@app.route('/')
def home():
    user_email = session.get('user_email')
    user_fio = session.get('user_fio')
    user_avatar = None
    ball_approved = False

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if user_email:
        cursor.execute('SELECT avatar, fio FROM users WHERE email = ?', (user_email,))
        row = cursor.fetchone()
        if row:
            user_avatar = row[0]
            user_fio = row[1]
        
        # Проверяем, одобрена ли у пользователя заявка на Осенний Бал (ID: 1)
        cursor.execute("SELECT status FROM applications WHERE user_email = ? AND event_id = 1", (user_email,))
        app_status = cursor.fetchone()
        if app_status and app_status[0] == 'approved':
            ball_approved = True

    # Сбор результатов голосования
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
                           ball_approved=ball_approved, # Разрешено ли голосовать
                           songs=songs_data, 
                           total_votes=total_votes)

# Голосование
@app.route('/vote/<int:song_id>', methods=['POST'])
def vote(song_id):
    user_email = session.get('user_email')
    if not user_email:
        flash("Пожалуйста, войдите в систему!", "warning")
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Проверка: одобрена ли заявка на Осенний Бал
    cursor.execute("SELECT status FROM applications WHERE user_email = ? AND event_id = 1", (user_email,))
    app_status = cursor.fetchone()
    if not app_status or app_status[0] != 'approved':
        conn.close()
        flash("Голосование доступно только участникам с подтвержденной заявкой на Осенний Бал!", "error")
        return redirect(url_for('home'))

    cursor.execute('INSERT OR REPLACE INTO votes (user_email, song_id) VALUES (?, ?)', (user_email, song_id))
    conn.commit()
    conn.close()
    flash("Ваш голос успешно учтен!", "success")
    return redirect(url_for('home'))

# Регистрация (Хеширование пароля!)
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
            # 1. Хешируем пароль перед записью в базу!
            hashed_password = generate_password_hash(password)
            
            cursor.execute(
                'INSERT INTO users (fio, class_group, email, password, phone, ip_address) VALUES (?, ?, ?, ?, ?, ?)', 
                (fio, class_group, email, hashed_password, phone, ip_address)
            )
            
            # 2. Автоматически создаем первую заявку на Осенний Бал (ID: 1) со статусом 'pending'
            cursor.execute(
                'INSERT INTO applications (user_email, event_id, wishes, status) VALUES (?, 1, ?, ?)',
                (email, wishes, 'pending')
            )
            conn.commit()
            conn.close()
            
            # Отправка уведомлений
            notify_admin_new_app(fio, "Осенний Бал 2026", email)
            
            # Вход в аккаунт теперь доступен сразу, так как статус привязан к заявкам, а не к аккаунту!
            session['user_email'] = email
            session['user_fio'] = fio
            flash("Регистрация успешна! Заявка на Осенний Бал отправлена на рассмотрение.", "success")
            return redirect(url_for('home'))
            
    return render_template('register.html', error=error)

# Вход (Проверка хеша!)
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT fio, email, password FROM users WHERE email = ?', (email,))
        user_data = cursor.fetchone()
        conn.close()
        
        # Сравниваем введенный пароль с сохраненным хешем в бд
        if user_data and check_password_hash(user_data[2], password):
            session['user_email'] = user_data[1]
            session['user_fio'] = user_data[0]
            flash(f"Рады видеть вас снова, {user_data[0]}!", 'info')
            return redirect(url_for('home'))
        else:
            error = "Неверный Email или пароль."
    return render_template('login.html', error=error)

# Выход
@app.route('/logout')
def logout():
    session.pop('user_email', None)
    session.pop('user_fio', None)
    flash("Вы вышли из системы.", 'info')
    return redirect(url_for('home'))

# Профиль и Личный Кабинет Заявок
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('login'))

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    if request.method == 'POST':
        # 1. Клик по кнопке "Подать новую заявку"
        if 'apply_event_id' in request.form:
            event_id = request.form.get('apply_event_id')
            wishes = request.form.get('wishes', '').strip()
            try:
                cursor.execute('INSERT INTO applications (user_email, event_id, wishes, status) VALUES (?, ?, ?, ?)', 
                               (user_email, event_id, wishes, 'pending'))
                conn.commit()
                
                # Получаем инфо о событии и ФИО для писем
                cursor.execute('SELECT title FROM events WHERE id = ?', (event_id,))
                event_title = cursor.fetchone()[0]
                cursor.execute('SELECT fio FROM users WHERE email = ?', (user_email,))
                user_fio = cursor.fetchone()[0]
                
                notify_admin_new_app(user_fio, event_title, user_email)
                flash(f"Ваша заявка на '{event_title}' успешно отправлена!", 'success')
            except sqlite3.IntegrityError:
                flash("Вы уже подали заявку на это мероприятие!", 'error')
                
        # 2. Сохранение данных профиля (телефон, пожелания, аватар)
        else:
            new_phone = request.form.get('phone', '').strip()
            avatar_file = request.files.get('avatar')
            avatar_filename = None

            if avatar_file and avatar_file.filename != '':
                if allowed_file(avatar_file.filename):
                    ext = avatar_file.filename.rsplit('.', 1)[1].lower()
                    safe_email_prefix = secure_filename(user_email.replace('@', '_').replace('.', '_'))
                    avatar_filename = f"avatar_{safe_email_prefix}.{ext}"
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], avatar_filename)
                    avatar_file.save(filepath)
                    cursor.execute('UPDATE users SET phone = ?, avatar = ? WHERE email = ?', (new_phone, avatar_filename, user_email))
                else:
                    flash("Недопустимый формат файла!", "error")
            else:
                cursor.execute('UPDATE users SET phone = ? WHERE email = ?', (new_phone, user_email))
                
            conn.commit()
            flash("Профиль успешно обновлен!", 'success')

    # Получаем данные пользователя
    cursor.execute('SELECT fio, class_group, email, phone, avatar FROM users WHERE email = ?', (user_email,))
    user_data = cursor.fetchone()
    
    # Получаем список ЗАЯВОК пользователя с названиями мероприятий
    cursor.execute('''
        SELECT a.id, e.title, e.date_str, e.location, a.status, a.wishes 
        FROM applications a 
        JOIN events e ON a.event_id = e.id 
        WHERE a.user_email = ? 
        ORDER BY a.id DESC
    ''', (user_email,))
    user_apps = []
    applied_ids = []
    for app_row in cursor.fetchall():
        user_apps.append({
            'id': app_row[0], 'title': app_row[1], 'date': app_row[2], 
            'location': app_row[3], 'status': app_row[4], 'wishes': app_row[5]
        })
        # Собираем ID мероприятий, на которые заявка уже есть
        cursor.execute('SELECT id FROM events WHERE title = ?', (app_row[1],))
        applied_ids.append(cursor.fetchone()[0])

    # Доступные для записи мероприятия (на которые еще нет заявок)
    cursor.execute('SELECT id, title, date_str, location FROM events')
    all_events = cursor.fetchall()
    available_events = []
    for ev in all_events:
        if ev[0] not in applied_ids:
            available_events.append({'id': ev[0], 'title': ev[1], 'date': ev[2], 'location': ev[3]})

    conn.close()

    user_dict = {
        'fio': user_data[0], 'class_group': user_data[1], 'email': user_data[2],
        'phone': user_data[3] if user_data[3] else '', 'avatar': user_data[4]
    }
    return render_template('profile.html', user=user_dict, apps=user_apps, available_events=available_events)


# --- УПРАВЛЕНИЕ ЗАЯВКАМИ АДМИНОМ ---

@app.route('/admin/approve/<int:app_id>', methods=['POST'])
def admin_approve(app_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.email, u.fio, e.title 
        FROM applications a 
        JOIN users u ON a.user_email = u.email 
        JOIN events e ON a.event_id = e.id 
        WHERE a.id = ?
    ''', (app_id,))
    row = cursor.fetchone()
    
    if row:
        email, fio, event_title = row
        cursor.execute("UPDATE applications SET status = 'approved' WHERE id = ?", (app_id,))
        conn.commit()
        notify_user_app_status(email, fio, event_title, 'approved')
        flash(f"Заявка #{app_id} ({fio}) успешно подтверждена!", "success")
    
    conn.close()
    return redirect(url_for('admin'))

@app.route('/admin/reject/<int:app_id>', methods=['POST'])
def admin_reject(app_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.email, u.fio, e.title, a.event_id 
        FROM applications a 
        JOIN users u ON a.user_email = u.email 
        JOIN events e ON a.event_id = e.id 
        WHERE a.id = ?
    ''', (app_id,))
    row = cursor.fetchone()
    
    if row:
        email, fio, event_title, event_id = row
        cursor.execute("UPDATE applications SET status = 'rejected' WHERE id = ?", (app_id,))
        # Если отклонили заявку на Осенний Бал (ID: 1), удаляем и голос из голосования за музыку
        if event_id == 1:
            cursor.execute("DELETE FROM votes WHERE user_email = ?", (email,))
        conn.commit()
        notify_user_app_status(email, fio, event_title, 'rejected')
        flash(f"Заявка #{app_id} ({fio}) отклонена.", "warning")
        
    conn.close()
    return redirect(url_for('admin'))


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

# Админка (Модерация заявок)
@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
        
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Выбираем список всех ЗАЯВОК (Applications)
    cursor.execute('''
        SELECT a.id, u.fio, u.class_group, u.email, e.title, a.wishes, u.ip_address, a.created_at, a.status, u.avatar 
        FROM applications a 
        JOIN users u ON a.user_email = u.email 
        JOIN events e ON a.event_id = e.id 
        ORDER BY a.id DESC
    ''')
    apps_raw = cursor.fetchall()
    
    apps = []
    for a in apps_raw:
        apps.append({
            'id': a[0], 'fio': a[1], 'class_group': a[2], 'email': a[3],
            'event_title': a[4], 'wishes': a[5], 'ip_address': a[6],
            'created_at': a[7], 'status': a[8], 'avatar': a[9]
        })

    # Сбор музыкальной статистики
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
    return render_template('admin.html', apps=apps, stats=stats, total_votes=total_votes)

# API
@app.route('/api/users')
def api_users():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized', 'message': 'Admin login required'}), 401
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Выбираем пользователей
    cursor.execute('SELECT id, fio, class_group, email, phone, avatar, reg_time FROM users ORDER BY id DESC')
    users_raw = cursor.fetchall()
    
    users_json = []
    for u in users_raw:
        user_email = u[3]
        
        # Для каждого пользователя подгружаем его заявки
        cursor.execute('''
            SELECT a.id, e.title, a.status, a.created_at 
            FROM applications a 
            JOIN events e ON a.event_id = e.id 
            WHERE a.user_email = ?
        ''', (user_email,))
        apps_raw = cursor.fetchall()
        
        user_apps = []
        for app_row in apps_raw:
            user_apps.append({
                'app_id': app_row[0],
                'event_title': app_row[1],
                'status': app_row[2],
                'created_at': app_row[3]
            })

        avatar_url = url_for('static', filename=f'uploads/{u[5]}', _external=True) if u[5] else f"https://ui-avatars.com/api/?name={u[1]}&background=random&size=128"

        users_json.append({
            'id': u[0], 'fio': u[1], 'class_group': u[2], 'email': user_email,
            'phone': u[4], 'avatar_url': avatar_url, 'registration_time': u[6],
            'applications': user_apps # Список всех заявок вложенным JSON-массивом!
        })
        
    conn.close()
    return jsonify(users_json)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)