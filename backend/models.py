import datetime
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from werkzeug.security import generate_password_hash, check_password_hash

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if os.path.exists("/app/data"):
    DATABASE_URL = "sqlite:////app/data/users.db"
elif os.path.exists("/app") and os.access("/app", os.W_OK):
    DATABASE_URL = "sqlite:////app/users.db"
else:
    DATABASE_URL = f"sqlite:///{BASE_DIR}/users.db"

# Создаем движок базы данных и сессию
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- МОДЕЛЬ: ПОЛЬЗОВАТЕЛЬ (User) ---
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    fio = Column(String, nullable=False)
    class_group = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  # Здесь будет храниться хеш пароля
    phone = Column(String, nullable=True)
    avatar = Column(String, nullable=True)
    ip_address = Column(String, nullable=False)
    role = Column(String, default='candidate')  # Роли: 'candidate', 'user', 'admins'
    reg_time = Column(DateTime, default=datetime.datetime.utcnow)

    # Связи (Relationships)
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    vote = relationship("Vote", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def check_password(self, plain_password):
        return check_password_hash(self.password, plain_password)


# --- МОДЕЛЬ: МЕРОПРИЯТИЕ (Event) ---
class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    date_str = Column(String, nullable=False)
    location = Column(String, nullable=False)

    applications = relationship("Application", back_populates="event")


# --- МОДЕЛЬ: ЗАЯВКА НА УЧАСТИЕ (Application) ---
class Application(Base):
    __tablename__ = 'applications'

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, ForeignKey('users.email'), nullable=False)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    wishes = Column(String, nullable=True)
    status = Column(String, default='pending')  # Статусы: 'pending', 'approved', 'rejected'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="applications")
    event = relationship("Event", back_populates="applications")

    # Предотвращаем дубликат заявок: один пользователь не может подать две заявки на одно событие
    __table_args__ = (UniqueConstraint('user_email', 'event_id', name='_user_event_uc'),)


# --- МОДЕЛЬ: ГОЛОС ЗА МУЗЫКУ (Vote) ---
class Vote(Base):
    __tablename__ = 'votes'

    user_email = Column(String, ForeignKey('users.email'), primary_key=True)
    song_id = Column(Integer, nullable=False)

    user = relationship("User", back_populates="vote")


# --- ИНИЦИАЛИЗАЦИЯ И СИДИНГ БАЗЫ ДАННЫХ ---
def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Наполняем базу мероприятиями, если они отсутствуют
        if db.query(Event).count() == 0:
            events_list = [
                Event(id=1, title="Осенний Бал 2026", date_str="31 октября 2026 в 18:00", location="Главный Колонный Зал Трапезной"),
                Event(id=2, title="Мастер-класс по венскому вальсу", date_str="24 октября 2026 в 15:00", location="Малый репетиционный зал"),
                Event(id=3, title="Творческий вечер поэзии 'Листопад'", date_str="05 ноября 2026 в 19:00", location="Литературная гостиная")
            ]
            db.add_all(events_list)
            db.commit()

        # Создаем администратора по умолчанию
        admin_emails = ['admin@ball.ru', 'admin@admin.ru']
        for email in admin_emails:
            if db.query(User).filter(User.email == email).count() == 0:
                pwd = "1488" if email == 'admin@ball.ru' else "admin"
                admin_user = User(
                    fio='Главный Администратор' if email == 'admin@ball.ru' else 'Администратор Тест',
                    class_group='Оргкомитет',
                    email=email,
                    password=generate_password_hash(pwd),
                    phone='—',
                    ip_address='127.0.0.1',
                    role='admins'
                )
                db.add(admin_user)
                db.commit()
    finally:
        db.close()