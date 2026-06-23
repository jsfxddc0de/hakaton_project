import sys
import os

# Добавляем путь в самом-самом начале
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request, Form, File, UploadFile, Depends, status
# ... и только потом:
from models import init_db, SessionLocal, User, Event, Application, Vote

from fastapi import FastAPI, Request, Form, File, UploadFile, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import os
import shutil
import smtplib
import ssl
from email.message import EmailMessage
from jinja2 import pass_context

# Импортируем бд и SQLAlchemy модели
from models import init_db, SessionLocal, User, Event, Application, Vote

# Инициализируем FastAPI с кастомным адресом для документации Swagger
app = FastAPI(
    title="Осенний Бал 2026 API",
    description="Интерактивная спецификация API для управления участниками и заявками.",
    version="1.2.0",
    docs_url="/api/users/docs",         # Твой адрес документации Swagger!
    openapi_url="/api/users/swagger.json"
)

# Поддержка сессий (cookie-session)
app.add_middleware(SessionMiddleware, secret_key="super_secret_key_for_sessions_and_profile")

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

# Настройки шаблонов Jinja2
templates = Jinja2Templates(directory="templates")

# --- СОВМЕСТИМОСТЬ С ШАБЛОНАМИ FLASK (Flash & url_for) ---
def flash(request: Request, message: str, category: str = "info"):
    if "_flashes" not in request.session:
        request.session["_flashes"] = []
    request.session["_flashes"].append((category, message))

@pass_context
def get_flashed_messages(context):
    request = context.get('request')
    if not request or "_flashes" not in request.session:
        return []
    return request.session.pop("_flashes", [])

@pass_context
def compat_url_for(context, name: str, **pathparams):
    request = context['request']
    if name == 'static' and 'filename' in pathparams:
        pathparams['path'] = pathparams.pop('filename')
    return request.url_for(name, **pathparams)

# Регистрируем глобальные функции для Jinja2
templates.env.globals['get_flashed_messages'] = get_flashed_messages
templates.env.globals['url_for'] = compat_url_for

# Константы музыки
SONGS = {
    1: {"title": "Евгений Дога — Вальс (Мой ласковый и нежный зверь)", "desc": "Торжественный вальс.", "audio_url": "https://upload.wikimedia.org/wikipedia/commons/2/20/Chopin_Waltz_in_C_sharp_minor_Op._64_No._2_performed_by_Luke_Faulkner.mp3"},
    2: {"title": "Георгий Свиридов — Вальс (Метель)", "desc": "Кружащийся, яркий русский вальс.", "audio_url": "https://upload.wikimedia.org/wikipedia/commons/7/70/Tchaikovsky_-_Waltz_of_the_Flowers_-_Peabody_Symphony_Orchestra.mp3"},
    3: {"title": "П. И. Чайковский — Октябрь. Осенняя песнь", "desc": "Тихая грусть золотой осени.", "audio_url": "https://upload.wikimedia.org/wikipedia/commons/3/30/Chopin_Nocturne_Op._9_No._2_in_E_flat_major_performed_by_Luke_Faulkner.mp3"},
    4: {"title": "Антонио Вивальди — Осень (Времена года)", "desc": "Праздничное барокко.", "audio_url": "https://upload.wikimedia.org/wikipedia/commons/3/3d/07_-_Vivaldi_Autumn_mvt_1_Allegro_-_John_Harrison_violin.mp3"},
    5: {"title": "Ян Тирсен — Waltz of the Monsters", "desc": "Загадочный неоклассический вальс.", "audio_url": "https://upload.wikimedia.org/wikipedia/commons/e/ec/Erik_Satie_-_Gymnopedie_No._1_-_arr._violin_and_piano.mp3"}
}

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Настройки почты
EMAIL_SENDER = 'ВАШ_EMAIL@gmail.com'
EMAIL_PASSWORD = os.environ.get('EMAIL_APP_PASSWORD', 'ВАШ_ПАРОЛЬ_ПРИЛОЖЕНИЯ')
ADMIN_EMAIL = 'АДМИНИСТРАТОР_EMAIL@gmail.com'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Dependency для инъекции сессий БД в роуты
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def send_email(to_email, subject, body):
    if not EMAIL_PASSWORD or EMAIL_PASSWORD == 'ВАШ_ПАРОЛЬ_ПРИЛОЖЕНИЯ':
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
    body = f"Участник {fio} ({email}) подал заявку на мероприятие '{event_title}'.\nУправление доступно в админке: http://127.0.0.1:5000/admin"
    send_email(ADMIN_EMAIL, subject, body)

def notify_user_app_status(email, fio, event_title, status):
    status_ru = "ОДОБРЕНА" if status == 'approved' else "ОТКЛОНЕНА"
    subject = f"✉️ Обновление статуса заявки: {event_title}"
    body = f"Здравствуйте, {fio}!\n\nСтатус вашей заявки на мероприятие '{event_title}' был изменен на: {status_ru}.\nПосмотреть статус всех своих заявок вы можете в профиле: http://127.0.0.1:5000/profile"
    send_email(email, subject, body)


# --- REST API: СХЕМЫ ДАННЫХ (Pydantic) ДЛЯ SWAGGER ---
class ApplicationSchema(BaseModel):
    app_id: int
    event_title: str
    status: str
    created_at: str

class UserSchema(BaseModel):
    id: int
    fio: str
    class_group: str
    email: EmailStr
    phone: Optional[str] = None
    avatar_url: str
    registration_time: str
    role: str
    applications: List[ApplicationSchema]

def serialize_user(u: User, request: Request) -> dict:
    user_apps = [{
        'app_id': a.id,
        'event_title': a.event.title,
        'status': a.status,
        'created_at': a.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for a in u.applications]

    avatar_url = str(request.url_for('static', path=f'uploads/{u.avatar}')) if u.avatar else f"https://ui-avatars.com/api/?name={u.fio}&background=random&size=128"

    return {
        'id': u.id, 'fio': u.fio, 'class_group': u.class_group, 'email': u.email,
        'phone': u.phone, 'avatar_url': avatar_url, 'registration_time': u.reg_time.strftime('%Y-%m-%d %H:%M:%S'),
        'role': u.role, 'applications': user_apps
    }

def verify_admin(request: Request):
    return request.session.get('user_role') == 'admins'


# --- РОУТЫ И ОТОБРАЖЕНИЕ (HTML PAGES) ---

@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    user_email = request.session.get('user_email')
    user_fio = request.session.get('user_fio')
    user_role = request.session.get('user_role')
    user_avatar = None

    if user_email:
        user = db.query(User).filter(User.email == user_email).first()
        if user:
            user_avatar = user.avatar
            user_fio = user.fio
            user_role = user.role
            request.session['user_role'] = user.role

    # Музыкальные результаты
    total_votes = db.query(Vote).count()
    votes_raw = db.query(Vote.song_id, func.count(Vote.user_email)).group_by(Vote.song_id).all()
    votes_dict = {song_id: count for song_id, count in votes_raw}

    user_vote = db.query(Vote).filter(Vote.user_email == user_email).first() if user_email else None
    user_vote_id = user_vote.song_id if user_vote else None

    songs_stats = []
    for s_id, s_info in SONGS.items():
        count = votes_dict.get(s_id, 0)
        percent = round((count / total_votes * 100), 1) if total_votes > 0 else 0
        songs_stats.append({
            'id': s_id, 'title': s_info['title'], 'desc': s_info['desc'],
            'votes': count, 'percent': percent, 'is_current': (s_id == user_vote_id)
        })

    return templates.TemplateResponse("index.html", {
        "request": request, "user_email": user_email, "user_fio": user_fio,
        "user_role": user_role, "user_avatar": user_avatar, "songs": songs_stats, "total_votes": total_votes
    })

@app.post("/vote/{song_id}")
def vote(request: Request, song_id: int, db: Session = Depends(get_db)):
    user_email = request.session.get('user_email')
    user_role = request.session.get('user_role')
    if not user_email:
        flash(request, "Пожалуйста, войдите в систему!", "warning")
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    if user_role == 'candidate':
        flash(request, "Голосование доступно только подтвержденным участникам (роль User)!", "error")
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    vote_obj = db.query(Vote).filter(Vote.user_email == user_email).first()
    if vote_obj:
        vote_obj.song_id = song_id
    else:
        db.add(Vote(user_email=user_email, song_id=song_id))
    db.commit()
    flash(request, "Ваш голос успешно учтен!", "success")
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/register", response_class=HTMLResponse)
def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})

@app.post("/register")
def register_post(
    request: Request, fio: str = Form(...), class_group: str = Form(...),
    email: str = Form(...), password: str = Form(...), phone: str = Form(""),
    wishes: str = Form(""), db: Session = Depends(get_db)
):
    fio, class_group, email, phone, wishes = fio.strip(), class_group.strip(), email.strip(), phone.strip(), wishes.strip()
    ip_address = request.headers.get('X-Forwarded-For', request.client.host)

    if not fio or not class_group or not email or not password:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Пожалуйста, заполните все поля."})

    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse("register.html", {"request": request, "error": "Этот Email уже зарегистрирован."})

    from werkzeug.security import generate_password_hash
    hashed_password = generate_password_hash(password)
    new_user = User(fio=fio, class_group=class_group, email=email, password=hashed_password, phone=phone, ip_address=ip_address, role='candidate')
    db.add(new_user)
    db.flush()

    db.add(Application(user_email=email, event_id=1, wishes=wishes, status='pending'))
    db.commit()

    notify_admin_new_app(fio, "Осенний Бал 2026", email)
    request.session.update({'user_email': email, 'user_fio': fio, 'user_role': 'candidate'})
    flash(request, "Успешная регистрация! Заявка ожидает модерации.", "success")
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login")
def login_post(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email.strip()).first()
    if user and user.check_password(password):
        request.session.update({'user_email': user.email, 'user_fio': user.fio, 'user_role': user.role})
        flash(request, f"Рады видеть вас, {user.fio}!", "info")
        return RedirectResponse(url="/admin" if user.role == 'admins' else "/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Неверный Email или пароль."})

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    flash(request, "Вы вышли из системы.", "info")
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/profile", response_class=HTMLResponse)
def profile_get(request: Request, db: Session = Depends(get_db)):
    user_email = request.session.get('user_email')
    if not user_email:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    user = db.query(User).filter(User.email == user_email).first()
    user_apps = db.query(Application).filter(Application.user_email == user_email).order_by(Application.id.desc()).all()
    
    mapped_apps = []
    applied_ids = []
    for app_obj in user_apps:
        mapped_apps.append({
            "id": app_obj.id, "title": app_obj.event.title, "date": app_obj.event.date_str,
            "location": app_obj.event.location, "status": app_obj.status, "wishes": app_obj.wishes
        })
        applied_ids.append(app_obj.event_id)

    all_events = db.query(Event).filter(~Event.id.in_(applied_ids)).all() if applied_ids else db.query(Event).all()
    available_events = [{"id": e.id, "title": e.title, "date": e.date_str, "location": e.location} for e in all_events]

    return templates.TemplateResponse("profile.html", {
        "request": request, "user": user, "apps": mapped_apps, "available_events": available_events
    })

@app.post("/profile")
async def profile_post(
    request: Request, apply_event_id: Optional[int] = Form(None), wishes: str = Form(""),
    phone: str = Form(""), avatar: Optional[UploadFile] = File(None), db: Session = Depends(get_db)
):
    user_email = request.session.get('user_email')
    if not user_email:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    user = db.query(User).filter(User.email == user_email).first()

    if apply_event_id is not None:
        if db.query(Application).filter(Application.user_email == user_email, Application.event_id == apply_event_id).first():
            flash(request, "Вы уже подали заявку на это событие!", "error")
        else:
            db.add(Application(user_email=user_email, event_id=apply_event_id, wishes=wishes.strip(), status='pending'))
            db.commit()
            event_obj = db.query(Event).filter(Event.id == apply_event_id).first()
            notify_admin_new_app(user.fio, event_obj.title, user_email)
            flash(request, f"Ваша заявка на '{event_obj.title}' успешно отправлена!", "success")
    else:
        user.phone = phone.strip()
        if avatar and avatar.filename != '':
            if allowed_file(avatar.filename):
                ext = avatar.filename.rsplit('.', 1)[1].lower()
                from werkzeug.utils import secure_filename
                safe_prefix = secure_filename(user_email.replace('@', '_').replace('.', '_'))
                avatar_filename = f"avatar_{safe_prefix}.{ext}"
                filepath = os.path.join(UPLOAD_FOLDER, avatar_filename)
                
                with open(filepath, "wb") as buffer:
                    shutil.copyfileobj(avatar.file, buffer)
                user.avatar = avatar_filename
            else:
                flash(request, "Недопустимый формат аватарки!", "error")
        db.commit()
        flash(request, "Профиль обновлен!", "success")

    return RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)


# --- ПАНЕЛЬ МОДЕРИРОВАНИЯ (ADMIN) ---

@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request, db: Session = Depends(get_db)):
    if not verify_admin(request):
        flash(request, "У вас нет прав администратора.", "error")
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    apps_raw = db.query(Application).order_by(Application.id.desc()).all()
    apps = [{
        'id': a.id, 'fio': a.user.fio, 'class_group': a.user.class_group, 'email': a.user_email,
        'event_title': a.event.title, 'wishes': a.wishes, 'ip_address': a.user.ip_address,
        'created_at': a.created_at.strftime('%Y-%m-%d %H:%M:%S'), 'status': a.status,
        'avatar': a.user.avatar, 'role': a.user.role
    } for a in apps_raw]

    # Музыкальные результаты
    total_votes = db.query(Vote).count()
    votes_raw = db.query(Vote.song_id, func.count(Vote.user_email)).group_by(Vote.song_id).all()
    votes_dict = {song_id: count for song_id, count in votes_raw}

    stats = []
    for s_id, s_info in SONGS.items():
        count = votes_dict.get(s_id, 0)
        percent = round((count / total_votes * 100), 1) if total_votes > 0 else 0
        stats.append({'title': s_info['title'], 'votes': count, 'percent': percent})

    return templates.TemplateResponse("admin.html", {
        "request": request, "apps": apps, "stats": stats, "total_votes": total_votes
    })

@app.post("/admin/approve/{app_id}")
def admin_approve(request: Request, app_id: int, db: Session = Depends(get_db)):
    if not verify_admin(request):
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    app_obj = db.query(Application).filter(Application.id == app_id).first()
    if app_obj:
        app_obj.status = 'approved'
        user = db.query(User).filter(User.email == app_obj.user_email).first()
        if user and user.role == 'candidate':
            user.role = 'user'
        db.commit()
        notify_user_app_status(app_obj.user_email, user.fio, app_obj.event.title, 'approved')
        flash(request, f"Заявка #{app_id} одобрена! Роль пользователя обновлена до User.", "success")
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/admin/reject/{app_id}")
def admin_reject(request: Request, app_id: int, db: Session = Depends(get_db)):
    if not verify_admin(request):
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    app_obj = db.query(Application).filter(Application.id == app_id).first()
    if app_obj:
        app_obj.status = 'rejected'
        if app_obj.event_id == 1:
            db.query(Vote).filter(Vote.user_email == app_obj.user_email).delete()

        # Понижаем роль, если нет других одобренных мероприятий
        approved_count = db.query(Application).filter(Application.user_email == app_obj.user_email, Application.status == 'approved').count()
        user = db.query(User).filter(User.email == app_obj.user_email).first()
        if approved_count == 0 and user and user.role == 'user':
            user.role = 'candidate'

        db.commit()
        notify_user_app_status(app_obj.user_email, user.fio, app_obj.event.title, 'rejected')
        flash(request, f"Заявка #{app_id} отклонена.", "warning")
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)


# --- 📃 REST API (С ИНТЕГРАЦИЕЙ В SWAGGER) ---

@app.get('/api/users', response_model=List[UserSchema], tags=["Users API"])
def api_users(request: Request, db: Session = Depends(get_db)):
    if not verify_admin(request):
        return JSONResponse(status_code=401, content={'error': 'Unauthorized', 'message': 'Admin role required'})
    users = db.query(User).order_by(User.id.desc()).all()
    return [serialize_user(u, request) for u in users]

@app.get('/api/users/admins', response_model=List[UserSchema], tags=["Users API"])
def api_admins(request: Request, db: Session = Depends(get_db)):
    if not verify_admin(request):
        return JSONResponse(status_code=401, content={'error': 'Unauthorized', 'message': 'Admin role required'})
    users = db.query(User).filter(User.role == 'admins').order_by(User.id.desc()).all()
    return [serialize_user(u, request) for u in users]

@app.get('/api/users/users', response_model=List[UserSchema], tags=["Users API"])
def api_approved_users(request: Request, db: Session = Depends(get_db)):
    if not verify_admin(request):
        return JSONResponse(status_code=401, content={'error': 'Unauthorized', 'message': 'Admin role required'})
    users = db.query(User).filter(User.role == 'user').order_by(User.id.desc()).all()
    return [serialize_user(u, request) for u in users]

@app.get('/api/users/candidates', response_model=List[UserSchema], tags=["Users API"])
def api_candidates(request: Request, db: Session = Depends(get_db)):
    if not verify_admin(request):
        return JSONResponse(status_code=401, content={'error': 'Unauthorized', 'message': 'Admin role required'})
    users = db.query(User).filter(User.role == 'candidate').order_by(User.id.desc()).all()
    return [serialize_user(u, request) for u in users]


# Запуск инициализации бд при старте
init_db()

if __name__ == '__main__':
    import uvicorn
    import sys
    
    # Принудительно прописываем путь к текущей папке при старте
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Запускаем сервер напрямую
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)