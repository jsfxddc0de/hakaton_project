import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE = 'users.db'

# Хелпер для быстрого и безопасного подключения к БД
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Позволяет обращаться к полям по именам: row['email']
    return conn

# Инициализация структуры БД
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fio TEXT NOT NULL,
            class_group TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            phone TEXT,
            avatar TEXT,
            ip_address TEXT NOT NULL,
            role TEXT DEFAULT 'candidate', -- 'candidate', 'user', 'admins'
            reg_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Таблица мероприятий
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            date_str TEXT NOT NULL,
            location TEXT NOT NULL
        )
    ''')
    
    # 3. Таблица заявок
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            event_id INTEGER NOT NULL,
            wishes TEXT,
            status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_email) REFERENCES users(email),
            FOREIGN KEY(event_id) REFERENCES events(id),
            UNIQUE(user_email, event_id)
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
    
    # Наполнение мероприятий по умолчанию
    cursor.execute('SELECT COUNT(*) FROM events')
    if cursor.fetchone()[0] == 0:
        events_list = [
            (1, "Осенний Бал 2026", "31 октября 2026 в 18:00", "Главный Колонный Зал Трапезной"),
            (2, "Мастер-класс по венскому вальсу", "24 октября 2026 в 15:00", "Малый репетиционный зал"),
            (3, "Творческий вечер поэзии 'Листопад'", "05 ноября 2026 в 19:00", "Литературная гостиная")
        ]
        cursor.executemany('INSERT INTO events (id, title, date_str, location) VALUES (?, ?, ?, ?)', events_list)

    # Создание главного администратора по умолчанию
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admins'")
    if cursor.fetchone()[0] == 0:
        admin_pass_hash = generate_password_hash("1488")
        cursor.execute('''
            INSERT INTO users (fio, class_group, email, password, phone, ip_address, role) 
            VALUES ('Главный Администратор', 'Оргкомитет', 'admin@ball.ru', ?, '—', '127.0.0.1', 'admins')
        ''', (admin_pass_hash,))

    conn.commit()
    conn.close()


# --- КЛАСС/ОБЪЕКТ: ПОЛЬЗОВАТЕЛЬ (User) ---
class User:
    def __init__(self, db_row):
        self.id = db_row['id']
        self.fio = db_row['fio']
        self.class_group = db_row['class_group']
        self.email = db_row['email']
        self.password = db_row['password']
        self.phone = db_row['phone']
        self.avatar = db_row['avatar']
        self.ip_address = db_row['ip_address']
        self.role = db_row['role']
        self.reg_time = db_row['reg_time']

    @staticmethod
    def create(fio, class_group, email, plain_password, phone, ip_address, role='candidate'):
        conn = get_db()
        cursor = conn.cursor()
        hashed_password = generate_password_hash(plain_password)
        try:
            cursor.execute('''
                INSERT INTO users (fio, class_group, email, password, phone, ip_address, role) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (fio, class_group, email, hashed_password, phone, ip_address, role))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Email уже существует
        finally:
            conn.close()

    @staticmethod
    def get_by_email(email):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        conn.close()
        return User(row) if row else None

    @staticmethod
    def get_all():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY id DESC')
        rows = cursor.fetchall()
        conn.close()
        return [User(row) for row in rows]

    def check_password(self, plain_password):
        return check_password_hash(self.password, plain_password)

    def update_profile(self, phone, avatar_filename=None):
        conn = get_db()
        cursor = conn.cursor()
        if avatar_filename:
            cursor.execute('UPDATE users SET phone = ?, avatar = ? WHERE email = ?', (phone, avatar_filename, self.email))
        else:
            cursor.execute('UPDATE users SET phone = ? WHERE email = ?', (phone, self.email))
        conn.commit()
        conn.close()

    def update_role(self, new_role):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET role = ? WHERE email = ?', (new_role, self.email))
        conn.commit()
        conn.close()


# --- КЛАСС/ОБЪЕКТ: МЕРОПРИЯТИЕ (Event) ---
class Event:
    def __init__(self, db_row):
        self.id = db_row['id']
        self.title = db_row['title']
        self.date_str = db_row['date_str']
        self.location = db_row['location']

    @staticmethod
    def get_all():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM events')
        rows = cursor.fetchall()
        conn.close()
        return [Event(row) for row in rows]

    @staticmethod
    def get_available_for_user(user_email):
        # Показывает мероприятия, на которые у пользователя еще нет заявок
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM events 
            WHERE id NOT IN (SELECT event_id FROM applications WHERE user_email = ?)
        ''', (user_email,))
        rows = cursor.fetchall()
        conn.close()
        return [Event(row) for row in rows]


# --- КЛАСС/ОБЪЕКТ: ЗАЯВКА (Application) ---
class Application:
    def __init__(self, db_row):
        self.id = db_row['id']
        self.user_email = db_row['user_email']
        self.event_id = db_row['event_id']
        self.wishes = db_row['wishes']
        self.status = db_row['status']
        self.created_at = db_row['created_at']
        
        # Дополнительные свойства, которые подтягиваются при JOIN-запросах
        self.event_title = db_row.get('title') if 'title' in db_row.keys() else None
        self.event_date = db_row.get('date_str') if 'date_str' in db_row.keys() else None
        self.event_location = db_row.get('location') if 'location' in db_row.keys() else None
        
        # Данные пользователя для админ-панели
        self.user_fio = db_row.get('fio') if 'fio' in db_row.keys() else None
        self.user_class = db_row.get('class_group') if 'class_group' in db_row.keys() else None
        self.user_avatar = db_row.get('avatar') if 'avatar' in db_row.keys() else None
        self.user_role = db_row.get('role') if 'role' in db_row.keys() else None
        self.ip_address = db_row.get('ip_address') if 'ip_address' in db_row.keys() else None

    @staticmethod
    def create(user_email, event_id, wishes, status='pending'):
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO applications (user_email, event_id, wishes, status) 
                VALUES (?, ?, ?, ?)
            ''', (user_email, event_id, wishes, status))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    @staticmethod
    def get_by_id(app_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT a.*, u.fio, e.title 
            FROM applications a
            JOIN users u ON a.user_email = u.email
            JOIN events e ON a.event_id = e.id
            WHERE a.id = ?
        ''', (app_id,))
        row = cursor.fetchone()
        conn.close()
        return Application(row) if row else None

    @staticmethod
    def get_by_user(user_email):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT a.*, e.title, e.date_str, e.location 
            FROM applications a 
            JOIN events e ON a.event_id = e.id 
            WHERE a.user_email = ? 
            ORDER BY a.id DESC
        ''', (user_email,))
        rows = cursor.fetchall()
        conn.close()
        return [Application(row) for row in rows]

    @staticmethod
    def get_all_detailed():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT a.*, u.fio, u.class_group, e.title, u.ip_address, u.avatar, u.role 
            FROM applications a 
            JOIN users u ON a.user_email = u.email 
            JOIN events e ON a.event_id = e.id 
            ORDER BY a.id DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        return [Application(row) for row in rows]

    @staticmethod
    def update_status(app_id, new_status):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE applications SET status = ? WHERE id = ?', (new_status, app_id))
        conn.commit()
        conn.close()

    @staticmethod
    def has_approved_event(user_email, event_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM applications WHERE user_email = ? AND event_id = ? AND status = "approved"', (user_email, event_id))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0

    @staticmethod
    def get_approved_count_by_user(user_email):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM applications WHERE user_email = ? AND status = "approved"', (user_email,))
        count = cursor.fetchone()[0]
        conn.close()
        return count


# --- КЛАСС/ОБЪЕКТ: ГОЛОС (Vote) ---
class Vote:
    @staticmethod
    def set_vote(user_email, song_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO votes (user_email, song_id) VALUES (?, ?)', (user_email, song_id))
        conn.commit()
        conn.close()

    @staticmethod
    def get_user_vote(user_email):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT song_id FROM votes WHERE user_email = ?', (user_email,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    @staticmethod
    def delete_by_user(user_email):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM votes WHERE user_email = ?', (user_email,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_stats(songs_dict):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT song_id, COUNT(*) FROM votes GROUP BY song_id')
        votes_raw = cursor.fetchall()
        votes_dict = {row['song_id']: row['COUNT(*)'] for row in votes_raw}
        
        cursor.execute('SELECT COUNT(*) FROM votes')
        total_votes = cursor.fetchone()[0]
        conn.close()

        stats = []
        for s_id, s_info in songs_dict.items():
            count = votes_dict.get(s_id, 0)
            percent = round((count / total_votes * 100), 1) if total_votes > 0 else 0
            stats.append({
                'id': s_id,
                'title': s_info['title'],
                'desc': s_info['desc'],
                'votes': count,
                'percent': percent
            })
        return stats, total_votes