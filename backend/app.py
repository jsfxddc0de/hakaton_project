from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.utils import secure_filename
import smtplib
import ssl
from email.message import EmailMessage
import os

# Импортируем наши Модели и методы инициализации из models.py
from models import init_db, User, Event, Application, Vote

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_sessions_and_profile'
app.json.ensure_ascii = False

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

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
EMAIL_SENDER = 'ВАШ_EMAIL@gmail.com'
EMAIL_PASSWORD = os.environ.get('EMAIL_APP_PASSWORD', 'ВАШ_ПАРОЛЬ_ПРИЛОЖЕНИЯ')
ADMIN_EMAIL = 'АДМИНИСТРАТОР_EMAIL@gmail.com'
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

def notify_admin_new_app(fio, event_title, email):
    subject = f"🔔 Новая заявка на {event_title}: {fio}"
    body = f"Участник {fio} ({email}) подал заявку на мероприятие '{event_title}'.\nУправление заявками доступно в админке: http://127.0.0.1:5000/admin"
    send_email(ADMIN_EMAIL, subject, body)

def notify_user_app_status(email, fio, event_title, status):
    status_ru = "ОДОБРЕНА" if status == 'approved' else "ОТКЛОНЕНА"
    subject = f"✉️ Обновление статуса заявки: {event_title}"
    body = f"Здравствуйте, {fio}!\n\nСтатус вашей заявки на мероприятие '{event_title}' был изменен на: {status_ru}.\nПосмотреть статус всех своих заявок вы можете в профиле: http://127.0.0.1:5000/profile"
    send_email(email, subject, body)


# --- РОУТИНГ И КОНТРОЛЛЕРЫ (VIEWS) ---

@app.route('/')
def home():
    user_email = session.get('user_email')
    user_fio = session.get('user_fio')
    user_role = session.get('user_role')
    user_avatar = None
    
    if user_email:
        user = User.get_by_email(user_email)
        if user:
            user_avatar = user.avatar
            user_fio = user.fio
            user_role = user.role
            session['user_role'] = user.role

    # Музыкальная статистика
    songs_stats, total_votes = Vote.get_stats(SONGS)
    
    # Узнаем выбор текущего пользователя
    user_vote = Vote.get_user_vote(user_email) if user_email else None
    
    # Добавляем к каждой песне отметку о выборе
    for song in songs_stats:
        song['is_current'] = (song['id'] == user_vote)

    return render_template('index.html', 
                           user_email=user_email, 
                           user_fio=user_fio, 
                           user_role=user_role,
                           user_avatar=user_avatar,
                           songs=songs_stats, 
                           total_votes=total_votes)

@app.route('/vote/<int:song_id>', methods=['POST'])
def vote(song_id):
    user_email = session.get('user_email')
    user_role = session.get('user_role')
    
    if not user_email:
        flash("Пожалуйста, войдите в систему!", "warning")
        return redirect(url_for('login'))
    
    if user_role == 'candidate':
        flash("Голосование доступно только подтвержденным участникам (роль User)!", "error")
        return redirect(url_for('home'))

    Vote.set_vote(user_email, song_id)
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

        # Создаем пользователя через модель User
        success = User.create(fio, class_group, email, password, phone, ip_address)
        if not success:
            error = "Пользователь с таким Email уже зарегистрирован."
        else:
            # Создаем заявку на Осенний Бал через модель Application
            Application.create(email, 1, wishes, 'pending')
            notify_admin_new_app(fio, "Осенний Бал 2026", email)
            
            session['user_email'] = email
            session['user_fio'] = fio
            session['user_role'] = 'candidate'
            
            flash("Вы успешно зарегистрировались как кандидат! Заявка отправлена на модерацию.", "success")
            return redirect(url_for('home'))
            
    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']
        
        user = User.get_by_email(email)
        if user and user.check_password(password):
            session['user_email'] = user.email
            session['user_fio'] = user.fio
            session['user_role'] = user.role
            
            flash(f"Рады видеть вас, {user.fio}!", 'info')
            
            if user.role == 'admins':
                return redirect(url_for('admin'))
            return redirect(url_for('home'))
        else:
            error = "Неверный Email или пароль."
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    session.pop('user_fio', None)
    session.pop('user_role', None)
    flash("Вы вышли из системы.", 'info')
    return redirect(url_for('home'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('login'))

    user = User.get_by_email(user_email)
    
    if request.method == 'POST':
        # Подача заявки на другое событие
        if 'apply_event_id' in request.form:
            event_id = request.form.get('apply_event_id')
            wishes = request.form.get('wishes', '').strip()
            success = Application.create(user_email, event_id, wishes, 'pending')
            if success:
                # Получаем название события для отправки уведомления
                events = Event.get_all()
                event_title = next((e.title for e in events if e.id == int(event_id)), "Событие")
                notify_admin_new_app(user.fio, event_title, user_email)
                flash(f"Ваша заявка на '{event_title}' успешно отправлена!", 'success')
            else:
                flash("Вы уже подали заявку на это мероприятие!", 'error')
                
        # Сохранение настроек профиля (телефон, аватар)
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
                    user.update_profile(new_phone, avatar_filename)
                else:
                    flash("Недопустимый формат файла!", "error")
            else:
                user.update_profile(new_phone)
                
            flash("Профиль успешно обновлен!", 'success')

    # Получаем актуальные заявки и доступные мероприятия
    user_apps = Application.get_by_user(user_email)
    available_events = Event.get_available_for_user(user_email)

    return render_template('profile.html', user=user, apps=user_apps, available_events=available_events)


# --- ДЕЙСТВИЯ АДМИНИСТРАТОРА ---

@app.route('/admin/approve/<int:app_id>', methods=['POST'])
def admin_approve(app_id):
    if session.get('user_role') != 'admins':
        flash("Доступ запрещен!", "error")
        return redirect(url_for('home'))
    
    app_obj = Application.get_by_id(app_id)
    if app_obj:
        Application.update_status(app_id, 'approved')
        
        # Повышаем роль кандидата до 'user'
        user = User.get_by_email(app_obj.user_email)
        if user and user.role == 'candidate':
            user.update_role('user')
            
        notify_user_app_status(app_obj.user_email, app_obj.user_fio, app_obj.event_title, 'approved')
        flash(f"Заявка #{app_id} ({app_obj.user_fio}) подтверждена. Роль обновлена до User!", "success")
    
    return redirect(url_for('admin'))

@app.route('/admin/reject/<int:app_id>', methods=['POST'])
def admin_reject(app_id):
    if session.get('user_role') != 'admins':
        flash("Доступ запрещен!", "error")
        return redirect(url_for('home'))
    
    app_obj = Application.get_by_id(app_id)
    if app_obj:
        Application.update_status(app_id, 'rejected')
        
        # Если отклонили заявку на Осенний Бал (ID: 1), удаляем его музыкальный голос
        if app_obj.event_id == 1:
            Vote.delete_by_user(app_obj.user_email)
            
        # Если у пользователя нет больше ни одной одобренной заявки, понижаем роль обратно до 'candidate'
        approved_count = Application.get_approved_count_by_user(app_obj.user_email)
        if approved_count == 0:
            user = User.get_by_email(app_obj.user_email)
            if user and user.role == 'user':
                user.update_role('candidate')
                
        notify_user_app_status(app_obj.user_email, app_obj.user_fio, app_obj.event_title, 'rejected')
        flash(f"Заявка #{app_id} ({app_obj.user_fio}) отклонена.", "warning")
        
    return redirect(url_for('admin'))

@app.route('/admin')
def admin():
    if session.get('user_role') != 'admins':
        flash("Доступ запрещен! У вас нет прав администратора.", "error")
        return redirect(url_for('home'))
        
    apps = Application.get_all_detailed()
    songs_stats, total_votes = Vote.get_stats(SONGS)
    
    return render_template('admin.html', apps=apps, stats=songs_stats, total_votes=total_votes)


# --- 📃 ДОКУМЕНТАЦИЯ SWAGGER API ---

@app.route('/api/users/docs')
def swagger_ui():
    if session.get('user_role') != 'admins':
        flash("У вас нет прав для просмотра документации API.", "error")
        return redirect(url_for('home'))
    return render_template('swagger.html')

@app.route('/api/users/swagger.json')
def swagger_json():
    if session.get('user_role') != 'admins':
        return jsonify({'error': 'Unauthorized'}), 401
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Осенний Бал 2026 API",
            "description": "Документация API для управления участниками и их заявками.",
            "version": "1.1.0"
        },
        "servers": [{"url": "http://127.0.0.1:5000"}],
        "paths": {
            "/api/users": {
                "get": {
                    "summary": "Получить список участников",
                    "responses": {
                        "200": {
                            "description": "Успешный запрос.",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": { "$ref": "#/components/schemas/User" }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "properties": {
                        "id": { "type": "integer" },
                        "fio": { "type": "string" },
                        "role": { "type": "string", "enum": ["candidate", "user", "admins"] }
                    }
                }
            }
        }
    }
    return jsonify(spec)

# API-эндпоинт
@app.route('/api/users')
def api_users():
    if session.get('user_role') != 'admins':
        return jsonify({'error': 'Unauthorized', 'message': 'Admin role required'}), 401
    
    users_raw = User.get_all()
    users_json = []
    
    for u in users_raw:
        # Для каждого юзера подтягиваем его заявки через Application
        apps_raw = Application.get_by_user(u.email)
        user_apps = [{
            'app_id': a.id,
            'event_title': a.event_title,
            'status': a.status,
            'created_at': a.created_at
        } for a in apps_raw]

        avatar_url = url_for('static', filename=f'uploads/{u.avatar}', _external=True) if u.avatar else f"https://ui-avatars.com/api/?name={u.fio}&background=random&size=128"

        users_json.append({
            'id': u.id, 'fio': u.fio, 'class_group': u.class_group, 'email': u.email,
            'phone': u.phone, 'avatar_url': avatar_url, 'registration_time': u.reg_time,
            'role': u.role,
            'applications': user_apps
        })
        
    return jsonify(users_json)


if __name__ == '__main__':
    init_db()  # Инициализация переехала в models.py
    app.run(debug=True, host='0.0.0.0', port=5000)