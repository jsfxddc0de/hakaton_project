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

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DATABASE = 'users.db'
ADMIN_PASSWORD = '1488'

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

# --- НАСТРОЙКИ ПОЧТЫ ---
EMAIL_SENDER = 'gika.savinov@gmail.com' # Почта отправителя (робот)
EMAIL_PASSWORD = os.environ.get('basr ksqv gbkq uvlv') # Пароль приложения
ADMIN_EMAIL = 'jsfxdd.c0de@gmail.com' # Почта, куда будут приходить новые заявки
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Функция отправки писем (общий хелпер)
def send_email(to_email, subject, body):
    if not EMAIL_PASSWORD or EMAIL_PASSWORD == 'basr ksqv gbkq uvlv':
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

# 1. Письмо Админу о новой заявке
def notify_admin_new_request(fio, class_group, email, phone, wishes):
    subject = f"🍁 Новая заявка на Осенний Бал: {fio}"
    body = f"""Уважаемый Администратор!

На сайт Осеннего Бала 2026 поступила новая заявка на участие.

Детали заявки:
- ФИО: {fio}
- Класс/Группа: {class_group}
- Email: {email}
- Телефон: {phone if phone else 'Не указан'}
- Пожелания: {wishes if wishes else 'Нет'}

Пожалуйста, перейдите в админ-панель для одобрения или отклонения заявки:
http://127.0.0.1:5000/admin
"""
    send_email(ADMIN_EMAIL, subject, body)

# 2. Письмо Юзеру об одобрении
def notify_user_approved(email, fio):
    subject = "🎉 Ваша заявка на Осенний Бал 2026 одобрена!"
    body = f"""Здравствуйте, {fio}!

Мы рады сообщить, что ваша заявка на участие в Осеннем Бале успешно одобрена организаторами!

Теперь вы можете войти в свой личный кабинет на сайте, используя ваш Email:
http://127.0.0.1:5000/login

В личном кабинете вы можете:
- Загрузить аватарку в настройках профиля.
- Отдать свой голос за открывающую бал музыкальную композицию!

С нетерпением ждем встречи с вами!
Оргкомитет Осеннего Бала.
"""
    send_email(email, subject, body)

# 3. Письмо Юзеру об отклонении
def notify_user_rejected(email, fio):
    subject = "✉️ Статус вашей заявки на Осенний Бал 2026"
    body = f"""Здравствуйте, {fio}.

К сожалению, ваша заявка на участие в Осеннем Бале была отклонена организаторами. 

Если у вас возникли вопросы или вы считаете, что произошла ошибка, пожалуйста, свяжитесь с оргкомитетом, ответив на это письмо.

С уважением,
Оргкомитет Осеннего Бала.
"""
    send_email(email, subject, body)


# Инициализация БД (Добавлено поле status default 'pending')
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
            avatar TEXT,
            ip_address TEXT NOT NULL,
            status TEXT DEFAULT 'pending', -- 'pending' (ожидает), 'approved' (одобрен), 'rejected' (отклонен)
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

    if user_email:
        cursor.execute('SELECT avatar, fio FROM users WHERE email = ?', (user_email,))
        row = cursor.fetchone()
        if row:
            user_avatar = row[0]
            user_fio = row[1]

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

# Регистрация
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
            # Записываем пользователя со статусом по умолчанию 'pending'
            cursor.execute(
                'INSERT INTO users (fio, class_group, email, password, phone, wishes, ip_address, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', 
                (fio, class_group, email, password, phone, wishes, ip_address, 'pending')
            )
            conn.commit()
            conn.close()
            
            # Отправляем уведомление администраторам
            notify_admin_new_request(fio, class_group, email, phone, wishes)
            
            flash("Ваша заявка успешно отправлена на модерацию! Уведомление о решении придет на ваш Email.", "success")
            return redirect(url_for('home'))
            
    return render_template('register.html', error=error)

# Вход (С проверкой статуса!)
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT fio, email, status FROM users WHERE email = ? AND password = ?', (email, password))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            fio, email, status = user_data
            
            # Проверяем одобрена ли заявка
            if status == 'pending':
                error = "Ваша заявка еще находится на рассмотрении администрации."
            elif status == 'rejected':
                error = "К сожалению, ваша заявка была отклонена администратором."
            elif status == 'approved':
                session['user_email'] = email
                session['user_fio'] = fio
                flash(f"Рады видеть вас снова, {fio}!", 'info')
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

# Профиль
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
        avatar_file = request.files.get('avatar')
        avatar_filename = None

        if avatar_file and avatar_file.filename != '':
            if allowed_file(avatar_file.filename):
                ext = avatar_file.filename.rsplit('.', 1)[1].lower()
                safe_email_prefix = secure_filename(user_email.replace('@', '_').replace('.', '_'))
                avatar_filename = f"avatar_{safe_email_prefix}.{ext}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], avatar_filename)
                avatar_file.save(filepath)
                cursor.execute('UPDATE users SET phone = ?, wishes = ?, avatar = ? WHERE email = ?', 
                               (new_phone, new_wishes, avatar_filename, user_email))
            else:
                flash("Недопустимый формат файла!", "error")
        else:
            cursor.execute('UPDATE users SET phone = ?, wishes = ? WHERE email = ?', (new_phone, new_wishes, user_email))
            
        conn.commit()
        flash("Профиль успешно сохранен!", 'success')

    cursor.execute('SELECT fio, class_group, email, phone, wishes, avatar FROM users WHERE email = ?', (user_email,))
    user_data = cursor.fetchone()
    conn.close()

    user_dict = {
        'fio': user_data[0], 'class_group': user_data[1], 'email': user_data[2],
        'phone': user_data[3] if user_data[3] else '', 'wishes': user_data[4] if user_data[4] else '',
        'avatar': user_data[5]
    }
    return render_template('profile.html', user=user_dict)


# --- ФУНКЦИИ АДМИНИСТРАТОРА (ОДОБРЕНИЕ / ОТКЛОНЕНИЕ) ---

# 1. Роут Одобрения заявки
@app.route('/admin/approve/<int:user_id>', methods=['POST'])
def admin_approve(user_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT email, fio FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    if user:
        email, fio = user
        cursor.execute("UPDATE users SET status = 'approved' WHERE id = ?", (user_id,))
        conn.commit()
        # Отправляем письмо с поздравлением на почту юзеру
        notify_user_approved(email, fio)
        flash(f"Заявка пользователя {fio} успешно одобрена. Уведомление отправлено на {email}!", "success")
    
    conn.close()
    return redirect(url_for('admin'))

# 2. Роут Отклонения заявки
@app.route('/admin/reject/<int:user_id>', methods=['POST'])
def admin_reject(user_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT email, fio FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    if user:
        email, fio = user
        cursor.execute("UPDATE users SET status = 'rejected' WHERE id = ?", (user_id,))
        # Удаляем также голос этого пользователя, если он успел проголосовать
        cursor.execute("DELETE FROM votes WHERE user_email = ?", (email,))
        conn.commit()
        # Отправляем письмо об отказе
        notify_user_rejected(email, fio)
        flash(f"Заявка пользователя {fio} отклонена. Уведомление отправлено на {email}.", "warning")
        
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

# Админка
@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
        
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Добавляем в выборку статус (status) пользователя
    cursor.execute('''
        SELECT u.id, u.fio, u.class_group, u.email, u.password, u.phone, u.wishes, u.ip_address, u.reg_time, v.song_id, u.avatar, u.status 
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
            'reg_time': u[8], 'voted_song': song_title, 'avatar': u[10], 
            'status': u[11] # Передаем статус
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

# API
@app.route('/api/users')
def api_users():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized', 'message': 'Admin login required'}), 401
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.id, u.fio, u.class_group, u.email, u.phone, u.wishes, u.reg_time, v.song_id, u.avatar, u.status 
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
        avatar_url = url_for('static', filename=f'uploads/{u[8]}', _external=True) if u[8] else f"https://ui-avatars.com/api/?name={u[1]}&background=random&size=128"

        users_json.append({
            'id': u[0], 'fio': u[1], 'class_group': u[2], 'email': u[3],
            'phone': u[4], 'wishes': u[5], 'registration_time': u[6],
            'voted_song_id': song_id, 'voted_song_title': song_title,
            'avatar_url': avatar_url,
            'status': u[9] # Передаем статус в API
        })
    
    return jsonify(users_json)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)