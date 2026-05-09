import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ktx.db"))

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def _seed_security_staff(c):
    staff_rows = [
        ("baove_a", "bv123", "Trần Văn Bảo", "0912000001", "Bảo vệ", "Ca đêm (22h-6h)", "Tòa A"),
        ("baove_b", "bv123", "Nguyễn Thị An", "0912000002", "Bảo vệ", "Ca sáng (6h-14h)", "Tòa B"),
        ("baove_cd", "bv123", "Lê Minh Trực", "0912000003", "Bảo vệ", "Ca chiều (14h-22h)", None),
    ]
    for username, password, fullname, phone, position, shift, building_name in staff_rows:
        c.execute("""INSERT OR IGNORE INTO users
            (username,password,role,fullname,phone) VALUES (?,?,?,?,?)""",
            (username, generate_password_hash(password), "staff", fullname, phone))
        user = c.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
        if not user:
            continue
        building_id = None
        if building_name:
            b = c.execute("SELECT id FROM buildings WHERE name=?", (building_name,)).fetchone()
            building_id = b["id"] if b else None
        exists = c.execute("SELECT id FROM staff WHERE user_id=?", (user["id"],)).fetchone()
        if not exists:
            c.execute("""INSERT INTO staff
                (user_id,position,shift,assigned_building) VALUES (?,?,?,?)""",
                (user["id"], position, shift, building_id))

def _seed_students_for_remaining_buildings(c):
    extra_students = [
        ("SVB2024001", "Phạm Thị Ngọc Anh", "Nữ", "Tòa B"),
        ("SVB2024002", "Võ Thị Thanh Trúc", "Nữ", "Tòa B"),
        ("SVB2024003", "Huỳnh Mai Chi", "Nữ", "Tòa B"),
        ("SVB2024004", "Đặng Thảo Vy", "Nữ", "Tòa B"),
        ("SVB2024005", "Trương Khánh Linh", "Nữ", "Tòa B"),
        ("SVB2024006", "Mai Phương Nhi", "Nữ", "Tòa B"),
        ("SVC2024001", "Phan Quốc Đạt", "Nam", "Tòa C"),
        ("SVC2024002", "Tạ Minh Nhật", "Nam", "Tòa C"),
        ("SVC2024003", "Hồ Anh Tuấn", "Nam", "Tòa C"),
        ("SVC2024004", "Nguyễn Đức Tài", "Nam", "Tòa C"),
        ("SVC2024005", "Võ Gia Huy", "Nam", "Tòa C"),
        ("SVC2024006", "Trần Hoàng Phúc", "Nam", "Tòa C"),
        ("SVD2024001", "Lâm Thị Bích Ngân", "Nữ", "Tòa D"),
        ("SVD2024002", "Ngô Thị Cẩm Tú", "Nữ", "Tòa D"),
        ("SVD2024003", "Đỗ Minh Châu", "Nữ", "Tòa D"),
        ("SVD2024004", "Bùi Khánh Hòa", "Nữ", "Tòa D"),
        ("SVD2024005", "Lê Nhật Hạ", "Nữ", "Tòa D"),
        ("SVD2024006", "Dương Thùy Dung", "Nữ", "Tòa D"),
    ]
    faculties = ["Công nghệ thông tin", "Kinh tế", "Kỹ thuật điện", "Cơ khí", "Xây dựng", "Ngoại ngữ"]
    rooms_by_building = {}
    for _, _, _, building_name in extra_students:
        if building_name not in rooms_by_building:
            rooms_by_building[building_name] = c.execute("""
                SELECT r.id FROM rooms r
                JOIN buildings b ON r.building_id=b.id
                WHERE b.name=?
                ORDER BY r.floor, r.room_number
                LIMIT 30
            """, (building_name,)).fetchall()
    building_offsets = {"Tòa B": 0, "Tòa C": 0, "Tòa D": 0}
    for i, (student_id, fullname, gender, building_name) in enumerate(extra_students):
        exists = c.execute("SELECT id FROM students WHERE student_id=?", (student_id,)).fetchone()
        if exists:
            continue
        rooms = rooms_by_building.get(building_name) or []
        if not rooms:
            continue
        room = rooms[building_offsets[building_name] % len(rooms)]
        building_offsets[building_name] += 1
        faculty = faculties[i % len(faculties)]
        c.execute("""INSERT INTO students
            (student_id,fullname,gender,phone,faculty,class,room_id,checkin_date,status)
            VALUES (?,?,?,?,?,?,?,?,?)""",
            (student_id, fullname, gender, f"0924{i+1:06d}", faculty,
             f"KTX2024{building_name[-1]}", room["id"], "2024-09-01", "active"))
        c.execute("UPDATE rooms SET status='occupied' WHERE id=?", (room["id"],))

def seed_additional_demo_data():
    conn = get_conn()
    c = conn.cursor()
    _seed_security_staff(c)
    _seed_students_for_remaining_buildings(c)
    conn.commit()
    conn.close()

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'staff',
            fullname TEXT,
            phone TEXT
        );
        CREATE TABLE IF NOT EXISTS buildings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            floors INTEGER DEFAULT 5,
            description TEXT
        );
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            building_id INTEGER,
            room_number TEXT NOT NULL,
            floor INTEGER DEFAULT 1,
            capacity INTEGER DEFAULT 4,
            type TEXT DEFAULT 'standard',
            price REAL DEFAULT 500000,
            status TEXT DEFAULT 'available',
            FOREIGN KEY (building_id) REFERENCES buildings(id)
        );
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            fullname TEXT NOT NULL,
            gender TEXT DEFAULT 'Nam',
            dob TEXT,
            phone TEXT,
            email TEXT,
            faculty TEXT,
            class TEXT,
            room_id INTEGER,
            checkin_date TEXT,
            checkout_date TEXT,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (room_id) REFERENCES rooms(id)
        );
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            amount REAL,
            month TEXT,
            status TEXT DEFAULT 'pending',
            paid_date TEXT,
            note TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id)
        );
        CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            type TEXT,
            description TEXT,
            severity TEXT DEFAULT 'minor',
            fine REAL DEFAULT 0,
            status TEXT DEFAULT 'open',
            reported_by INTEGER,
            reported_at TEXT DEFAULT CURRENT_TIMESTAMP,
            resolved_at TEXT,
            FOREIGN KEY (student_id) REFERENCES students(id)
        );
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            student_id TEXT,
            gender TEXT,
            phone TEXT,
            email TEXT,
            faculty TEXT,
            reason TEXT,
            preferred_room_type TEXT DEFAULT 'standard',
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            note TEXT
        );
        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            position TEXT,
            shift TEXT,
            assigned_building INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)
    c.execute("PRAGMA foreign_keys = OFF")
    c.execute("DELETE FROM payments")
    c.execute("DELETE FROM violations")
    c.execute("DELETE FROM staff")
    c.execute("DELETE FROM students")
    c.execute("DELETE FROM applications")
    c.execute("DELETE FROM rooms")
    c.execute("DELETE FROM buildings")
    c.execute("PRAGMA foreign_keys = ON")
    conn.commit()

    # Seed admin
    c.execute("INSERT OR IGNORE INTO users (username,password,role,fullname) VALUES (?,?,?,?)",
              ('admin', generate_password_hash('admin123'), 'admin', 'Quản trị viên'))
    # Seed buildings chuẩn A B C D
    building_map = [
        ('Tòa A', 10, 'Khu nam - VIP 4 người/phòng - 1 triệu/tháng'),
        ('Tòa B', 10, 'Khu nữ - VIP 4 người/phòng - 1 triệu/tháng'),
        ('Tòa C', 10, 'Khu nam - Thường 6 người/phòng - 600k/tháng'),
        ('Tòa D', 10, 'Khu nữ - Thường 6 người/phòng - 600k/tháng')
    ]
    for b in building_map:
        ex = c.execute("SELECT id FROM buildings WHERE name=?", (b[0],)).fetchone()
        if ex:
            c.execute("UPDATE buildings SET floors=?, description=? WHERE id=?", (b[1], b[2], ex['id']))
        else:
            c.execute("INSERT INTO buildings (name,floors,description) VALUES (?,?,?)", b)
    conn.commit()
    _seed_security_staff(c)
    conn.commit()

    # Seed rooms 10 tầng mỗi tầng 10 phòng
    for building in c.execute("SELECT id, name FROM buildings").fetchall():
        count = c.execute("SELECT COUNT(*) as n FROM rooms WHERE building_id=?", (building['id'],)).fetchone()['n']
        if count < 100:
            for floor in range(1, 11):
                for num in range(1, 11):
                    room_number = f"{floor:02d}{num:02d}"
                    exists = c.execute("SELECT id FROM rooms WHERE building_id=? AND room_number=?", (building['id'], room_number)).fetchone()
                    if not exists:
                        is_vip = building['name'] in ['Tòa A', 'Tòa B']
                        capacity = 4 if is_vip else 6
                        price = 1000000 if is_vip else 600000
                        room_type = 'VIP' if is_vip else 'Standard'
                        c.execute("INSERT INTO rooms (building_id,room_number,floor,capacity,type,price,status) VALUES (?,?,?,?,?,?,?)",
                                  (building['id'], room_number, floor, capacity, room_type, price, 'available'))
    conn.commit()

    # Seed demo students
    c.execute("SELECT COUNT(*) as n FROM students")
    if c.fetchone()['n'] == 0:
        import random
        names_m = ['Nguyễn Văn An','Trần Minh Khoa','Lê Quốc Hùng','Phạm Văn Đức',
                   'Hoàng Trung Nam','Đỗ Văn Bình','Vũ Mạnh Cường','Bùi Thanh Tùng',
                   'Đinh Văn Long','Ngô Quang Huy','Dương Văn Thắng','Lý Minh Tuấn']
        names_f = ['Nguyễn Thị Lan','Trần Thị Mai','Lê Thị Hoa','Phạm Thị Thu',
                   'Hoàng Thị Nga','Đỗ Thị Linh','Vũ Thị Hương','Bùi Thị Yến',
                   'Đinh Thị Thảo','Ngô Thị Phương','Dương Thị Nhung','Lý Thị Trang']
        faculties = ['Công nghệ thông tin','Kinh tế','Kỹ thuật điện','Cơ khí','Xây dựng','Ngoại ngữ']
        rooms = c.execute("SELECT id, capacity FROM rooms LIMIT 20").fetchall()
        for i, name in enumerate(names_m + names_f):
            sid = f"SV2024{i+1:04d}"
            gender = 'Nam' if i < len(names_m) else 'Nữ'
            room = rooms[i % len(rooms)]
            faculty = random.choice(faculties)
            c.execute("""INSERT OR IGNORE INTO students
                (student_id,fullname,gender,phone,faculty,class,room_id,checkin_date,status)
                VALUES (?,?,?,?,?,?,?,?,?)""",
                (sid, name, gender, f"09{random.randint(10000000,99999999)}",
                 faculty, f"{faculty[:2].upper()}2024A", room['id'], '2024-09-01', 'active'))
            c.execute("UPDATE rooms SET status='occupied' WHERE id=?", (room['id'],))
        _seed_students_for_remaining_buildings(c)
        conn.commit()

        # Seed payments
        for month in ['2024-09','2024-10','2024-11','2024-12']:
            students = c.execute("SELECT s.id, r.price FROM students s JOIN rooms r ON s.room_id=r.id WHERE s.status='active'").fetchall()
            for s in students:
                import random as r2
                status = 'paid' if r2.random() > 0.3 else 'pending'
                paid_date = f"{month}-{r2.randint(1,28):02d}" if status == 'paid' else None
                c.execute("INSERT INTO payments (student_id,amount,month,status,paid_date) VALUES (?,?,?,?,?)",
                          (s['id'], s['price'], month, status, paid_date))
        conn.commit()

        # Seed violations
        vtypes = ['Ồn ào quá giờ','Hút thuốc','Khách trái phép','Vi phạm giờ giới nghiêm','Phá hoại tài sản']
        students = c.execute("SELECT id FROM students LIMIT 8").fetchall()
        for s in students[:5]:
            import random as r3
            c.execute("""INSERT INTO violations (student_id,type,description,severity,fine,status,reported_at)
                VALUES (?,?,?,?,?,?,?)""",
                (s['id'], r3.choice(vtypes), 'Ghi nhận từ bảo vệ ca đêm.',
                 r3.choice(['minor','medium','severe']),
                 r3.choice([0, 50000, 100000, 200000]),
                 r3.choice(['open','resolved']),
                 '2024-11-15 22:30:00'))
        conn.commit()

    conn.close()

def login(username, password):
    conn = get_conn()
    u = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    if u and check_password_hash(u['password'], password):
        return dict(u)
    return None

# ── BUILDINGS ──────────────────────────────────────────
def get_buildings():
    conn = get_conn()
    rows = conn.execute("""
        SELECT b.*, COUNT(r.id) as total_rooms,
               SUM(CASE WHEN r.status='occupied' THEN 1 ELSE 0 END) as occupied
        FROM buildings b LEFT JOIN rooms r ON b.id=r.building_id
        GROUP BY b.id ORDER BY b.name
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_building(name, floors, desc):
    conn = get_conn()
    conn.execute("INSERT INTO buildings (name,floors,description) VALUES (?,?,?)", (name, floors, desc))
    conn.commit(); conn.close()

def delete_building(bid):
    conn = get_conn()
    conn.execute("DELETE FROM buildings WHERE id=?", (bid,))
    conn.commit(); conn.close()

# ── ROOMS ──────────────────────────────────────────────
def get_rooms(building_id=None, status=None):
    conn = get_conn()
    q = """SELECT r.*, b.name as building_name,
               (SELECT COUNT(*) FROM students s WHERE s.room_id=r.id AND s.status='active') as current_occupants
           FROM rooms r LEFT JOIN buildings b ON r.building_id=b.id WHERE 1=1"""
    p = []
    if building_id: q += " AND r.building_id=?"; p.append(building_id)
    if status: q += " AND r.status=?"; p.append(status)
    q += " ORDER BY b.name, r.floor, r.room_number"
    rows = conn.execute(q, p).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_room(building_id, room_number, floor, capacity, rtype, price):
    conn = get_conn()
    conn.execute("INSERT INTO rooms (building_id,room_number,floor,capacity,type,price) VALUES (?,?,?,?,?,?)",
                 (building_id, room_number, floor, capacity, rtype, price))
    conn.commit(); conn.close()

def delete_room(rid):
    conn = get_conn()
    conn.execute("DELETE FROM rooms WHERE id=?", (rid,))
    conn.commit(); conn.close()

def get_available_rooms():
    conn = get_conn()
    rows = conn.execute("""
        SELECT r.*, b.name as building_name,
               (r.capacity - (SELECT COUNT(*) FROM students s WHERE s.room_id=r.id AND s.status='active')) as free_slots
        FROM rooms r LEFT JOIN buildings b ON r.building_id=b.id
        GROUP BY r.id HAVING free_slots > 0 ORDER BY b.name, r.room_number
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── STUDENTS ───────────────────────────────────────────
def get_students(search='', status='active'):
    conn = get_conn()
    q = """SELECT s.*, r.room_number, b.name as building_name
           FROM students s
           LEFT JOIN rooms r ON s.room_id=r.id
           LEFT JOIN buildings b ON r.building_id=b.id
           WHERE s.status=?"""
    p = [status]
    if search:
        q += " AND (s.fullname LIKE ? OR s.student_id LIKE ? OR s.phone LIKE ? OR s.faculty LIKE ?)"
        p += [f'%{search}%']*4
    q += " ORDER BY s.id DESC"
    rows = conn.execute(q, p).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_student(student_id, fullname, gender, dob, phone, email, faculty, cls, room_id, checkin_date):
    conn = get_conn()
    conn.execute("""INSERT INTO students
        (student_id,fullname,gender,dob,phone,email,faculty,class,room_id,checkin_date,status)
        VALUES (?,?,?,?,?,?,?,?,?,?,'active')""",
        (student_id, fullname, gender, dob, phone, email, faculty, cls, room_id or None, checkin_date))
    if room_id:
        conn.execute("UPDATE rooms SET status='occupied' WHERE id=?", (room_id,))
    conn.commit(); conn.close()

def checkout_student(sid):
    from datetime import date
    conn = get_conn()
    s = conn.execute("SELECT room_id FROM students WHERE id=?", (sid,)).fetchone()
    conn.execute("UPDATE students SET status='checked_out', checkout_date=? WHERE id=?",
                 (date.today().isoformat(), sid))
    if s and s['room_id']:
        occupied = conn.execute("SELECT COUNT(*) as n FROM students WHERE room_id=? AND status='active'", (s['room_id'],)).fetchone()['n']
        if occupied <= 1:
            conn.execute("UPDATE rooms SET status='available' WHERE id=?", (s['room_id'],))
    conn.commit(); conn.close()

def get_student_detail(sid):
    conn = get_conn()
    s = conn.execute("""SELECT s.*, r.room_number, r.price, b.name as building_name
        FROM students s LEFT JOIN rooms r ON s.room_id=r.id LEFT JOIN buildings b ON r.building_id=b.id
        WHERE s.id=?""", (sid,)).fetchone()
    conn.close()
    return dict(s) if s else None

# ── PAYMENTS ───────────────────────────────────────────
def get_payments(month=None, status=None, search=''):
    conn = get_conn()
    q = """SELECT p.*, s.fullname, s.student_id as sid, r.room_number, b.name as building_name
           FROM payments p JOIN students s ON p.student_id=s.id
           LEFT JOIN rooms r ON s.room_id=r.id LEFT JOIN buildings b ON r.building_id=b.id WHERE 1=1"""
    p = []
    if month: q += " AND p.month=?"; p.append(month)
    if status: q += " AND p.status=?"; p.append(status)
    if search:
        q += " AND (s.fullname LIKE ? OR s.student_id LIKE ?)"; p += [f'%{search}%']*2
    q += " ORDER BY p.created_at DESC"
    rows = conn.execute(q, p).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_payment_summary(month):
    conn = get_conn()
    r = conn.execute("""SELECT
        SUM(CASE WHEN status='paid' THEN amount ELSE 0 END) as collected,
        SUM(CASE WHEN status='pending' THEN amount ELSE 0 END) as pending,
        COUNT(*) as total FROM payments WHERE month=?""", (month,)).fetchone()
    conn.close()
    return dict(r)

def mark_paid(pid):
    from datetime import date
    conn = get_conn()
    conn.execute("UPDATE payments SET status='paid', paid_date=? WHERE id=?", (date.today().isoformat(), pid))
    conn.commit(); conn.close()

def mark_pending_payments_paid(month):
    from datetime import date
    conn = get_conn()
    r = conn.execute("""
        SELECT COUNT(*) as count, COALESCE(SUM(amount),0) as total
        FROM payments WHERE month=? AND status='pending'
    """, (month,)).fetchone()
    conn.execute("""
        UPDATE payments SET status='paid', paid_date=?
        WHERE month=? AND status='pending'
    """, (date.today().isoformat(), month))
    conn.commit(); conn.close()
    return dict(r)

def generate_payments(month):
    conn = get_conn()
    students = conn.execute("""SELECT s.id, r.price FROM students s
        JOIN rooms r ON s.room_id=r.id WHERE s.status='active'""").fetchall()
    count = 0
    for s in students:
        ex = conn.execute("SELECT id FROM payments WHERE student_id=? AND month=?", (s['id'], month)).fetchone()
        if not ex:
            conn.execute("INSERT INTO payments (student_id,amount,month,status) VALUES (?,?,?,'pending')",
                         (s['id'], s['price'], month))
            count += 1
    conn.commit(); conn.close()
    return count

def add_payment(student_id, amount, month, note=''):
    conn = get_conn()
    conn.execute("INSERT INTO payments (student_id,amount,month,status,note) VALUES (?,?,?,'pending',?)",
                 (student_id, amount, month, note))
    conn.commit(); conn.close()

def get_students_for_payment():
    conn = get_conn()
    rows = conn.execute("""
        SELECT s.id, s.student_id, s.fullname, r.room_number, r.price, b.name as building_name
        FROM students s
        LEFT JOIN rooms r ON s.room_id=r.id
        LEFT JOIN buildings b ON r.building_id=b.id
        WHERE s.status='active'
        ORDER BY s.fullname
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── VIOLATIONS ─────────────────────────────────────────
def get_violations(status=None, search=''):
    conn = get_conn()
    q = """SELECT v.*, s.fullname as student_name, s.student_id as sid, u.fullname as reporter_name
           FROM violations v JOIN students s ON v.student_id=s.id
           LEFT JOIN users u ON v.reported_by=u.id WHERE 1=1"""
    p = []
    if status: q += " AND v.status=?"; p.append(status)
    if search:
        q += " AND (s.fullname LIKE ? OR s.student_id LIKE ?)"; p += [f'%{search}%']*2
    q += " ORDER BY v.reported_at DESC"
    rows = conn.execute(q, p).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_violation(student_id, vtype, description, severity, fine, reported_by):
    conn = get_conn()
    conn.execute("""INSERT INTO violations (student_id,type,description,severity,fine,reported_by,status)
        VALUES (?,?,?,?,?,?,'open')""", (student_id, vtype, description, severity, fine, reported_by))
    conn.commit(); conn.close()

def resolve_violation(vid):
    from datetime import datetime
    conn = get_conn()
    conn.execute("UPDATE violations SET status='resolved', resolved_at=? WHERE id=?",
                 (datetime.now().isoformat(), vid))
    conn.commit(); conn.close()

# ── STAFF ──────────────────────────────────────────────
def get_staff():
    conn = get_conn()
    rows = conn.execute("""SELECT u.*, st.position, st.shift, b.name as building_name
        FROM users u LEFT JOIN staff st ON u.id=st.user_id
        LEFT JOIN buildings b ON st.assigned_building=b.id
        WHERE u.role='staff' ORDER BY u.fullname""").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_staff(username, password, fullname, phone, position, shift, building_id):
    from werkzeug.security import generate_password_hash
    conn = get_conn()
    try:
        conn.execute("INSERT INTO users (username,password,role,fullname,phone) VALUES (?,?,?,?,?)",
                     (username, generate_password_hash(password), 'staff', fullname, phone))
        uid = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()['id']
        conn.execute("INSERT INTO staff (user_id,position,shift,assigned_building) VALUES (?,?,?,?)",
                     (uid, position, shift, building_id or None))
        conn.commit(); conn.close()
        return True
    except:
        conn.close()
        return False

def delete_staff(uid):
    conn = get_conn()
    conn.execute("DELETE FROM staff WHERE user_id=?", (uid,))
    conn.execute("DELETE FROM users WHERE id=?", (uid,))
    conn.commit(); conn.close()

# ── APPLICATIONS ───────────────────────────────────────
def get_applications(status=None):
    conn = get_conn()
    q = "SELECT * FROM applications WHERE 1=1"
    p = []
    if status: q += " AND status=?"; p.append(status)
    q += " ORDER BY created_at DESC"
    rows = conn.execute(q, p).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_application(fullname, student_id, gender, phone, email, faculty, reason, preferred):
    conn = get_conn()
    conn.execute("""INSERT INTO applications (fullname,student_id,gender,phone,email,faculty,reason,preferred_room_type)
        VALUES (?,?,?,?,?,?,?,?)""", (fullname, student_id, gender, phone, email, faculty, reason, preferred))
    conn.commit(); conn.close()

def update_application_status(aid, status, note=''):
    conn = get_conn()
    conn.execute("UPDATE applications SET status=?, note=? WHERE id=?", (status, note, aid))
    conn.commit(); conn.close()

# ── DASHBOARD STATS ────────────────────────────────────
def get_dashboard_stats():
    conn = get_conn()
    from datetime import datetime
    month = datetime.now().strftime('%Y-%m')
    stats = {
        'total_students': conn.execute("SELECT COUNT(*) FROM students WHERE status='active'").fetchone()[0],
        'total_rooms': conn.execute("SELECT COUNT(*) FROM rooms").fetchone()[0],
        'occupied_rooms': conn.execute("SELECT COUNT(*) FROM rooms WHERE status='occupied'").fetchone()[0],
        'available_rooms': conn.execute("SELECT COUNT(*) FROM rooms WHERE status='available'").fetchone()[0],
        'pending_payments': conn.execute("SELECT COUNT(*) FROM payments WHERE status='pending'").fetchone()[0],
        'open_violations': conn.execute("SELECT COUNT(*) FROM violations WHERE status='open'").fetchone()[0],
        'monthly_revenue': conn.execute(
            "SELECT COALESCE(SUM(amount),0) FROM payments WHERE status='paid' AND strftime('%Y-%m',paid_date)=?",
            (month,)).fetchone()[0],
        'pending_apps': conn.execute("SELECT COUNT(*) FROM applications WHERE status='pending'").fetchone()[0],
        'total_staff': conn.execute("SELECT COUNT(*) FROM users WHERE role='staff'").fetchone()[0],
    }
    conn.close()
    return stats

def get_revenue_chart():
    conn = get_conn()
    rows = conn.execute("""SELECT month,
        SUM(CASE WHEN status='paid' THEN amount ELSE 0 END) as collected,
        SUM(amount) as total
        FROM payments GROUP BY month ORDER BY month DESC LIMIT 6""").fetchall()
    conn.close()
    return [dict(r) for r in rows][::-1]

def get_occupancy_by_building():
    conn = get_conn()
    rows = conn.execute("""SELECT b.name,
        COUNT(r.id) as total_rooms,
        SUM(CASE WHEN r.status='occupied' THEN 1 ELSE 0 END) as occupied,
        COUNT(s.id) as total_students
        FROM buildings b LEFT JOIN rooms r ON b.id=r.building_id
        LEFT JOIN students s ON r.id=s.room_id AND s.status='active'
        GROUP BY b.id""").fetchall()
    conn.close()
    return [dict(r) for r in rows]
def unmark_paid(pid):
    conn = get_conn()
    conn.execute("UPDATE payments SET status='pending', paid_date=NULL WHERE id=?", (pid,))
    conn.commit(); conn.close()

def update_building(bid, name, floors, desc):
    conn = get_conn()
    conn.execute("UPDATE buildings SET name=?, floors=?, description=? WHERE id=?", (name, floors, desc, bid))
    conn.commit(); conn.close()

def update_room(rid, room_number, floor, capacity, rtype, price, status):
    conn = get_conn()
    conn.execute("UPDATE rooms SET room_number=?,floor=?,capacity=?,type=?,price=?,status=? WHERE id=?",
                 (room_number, floor, capacity, rtype, price, status, rid))
    conn.commit(); conn.close()

def get_students_in_room(room_id):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM students WHERE room_id=? AND status='active' ORDER BY fullname", (room_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_student(sid, fullname, phone, email, faculty, cls, new_room_id=None):
    conn = get_conn()
    conn.execute("UPDATE students SET fullname=?,phone=?,email=?,faculty=?,class=? WHERE id=?",
                 (fullname, phone, email, faculty, cls, sid))
    if new_room_id:
        old = conn.execute("SELECT room_id FROM students WHERE id=?", (sid,)).fetchone()
        if old and old['room_id']:
            conn.execute("UPDATE rooms SET status='available' WHERE id=?", (old['room_id'],))
        conn.execute("UPDATE students SET room_id=? WHERE id=?", (new_room_id, sid))
        conn.execute("UPDATE rooms SET status='occupied' WHERE id=?", (new_room_id,))
    conn.commit(); conn.close()

def delete_student(sid):
    conn = get_conn()
    s = conn.execute("SELECT room_id FROM students WHERE id=?", (sid,)).fetchone()
    if s and s['room_id']:
        conn.execute("UPDATE rooms SET status='available' WHERE id=?", (s['room_id'],))
    conn.execute("DELETE FROM students WHERE id=?", (sid,))
    conn.commit(); conn.close()

# ── EXTRA FUNCTIONS ─────────────────────────────────────
def unmark_paid(pid):
    conn = get_conn()
    conn.execute("UPDATE payments SET status='pending', paid_date=NULL WHERE id=?", (pid,))
    conn.commit(); conn.close()

def update_building(bid, name, floors, description):
    conn = get_conn()
    conn.execute("UPDATE buildings SET name=?, floors=?, description=? WHERE id=?",
                 (name, floors, description, bid))
    conn.commit(); conn.close()

def update_room(rid, room_number, floor, capacity, rtype, price, status):
    conn = get_conn()
    conn.execute("""UPDATE rooms SET room_number=?, floor=?, capacity=?,
                    type=?, price=?, status=? WHERE id=?""",
                 (room_number, floor, capacity, rtype, price, status, rid))
    conn.commit(); conn.close()

def get_students_in_room(room_id):
    conn = get_conn()
    rows = conn.execute("""SELECT * FROM students WHERE room_id=? AND status='active'
                           ORDER BY fullname""", (room_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_student(sid, fullname, phone, email, faculty, cls, new_room_id=None):
    conn = get_conn()
    conn.execute("""UPDATE students SET fullname=?, phone=?, email=?, faculty=?, class=?
                    WHERE id=?""", (fullname, phone, email, faculty, cls, sid))
    if new_room_id:
        conn.execute("UPDATE students SET room_id=? WHERE id=?", (new_room_id, sid))
        conn.execute("UPDATE rooms SET status='occupied' WHERE id=?", (new_room_id,))
    conn.commit(); conn.close()

def delete_student(sid):
    conn = get_conn()
    s = conn.execute("SELECT room_id FROM students WHERE id=?", (sid,)).fetchone()
    conn.execute("DELETE FROM students WHERE id=?", (sid,))
    if s and s['room_id']:
        remaining = conn.execute(
            "SELECT COUNT(*) FROM students WHERE room_id=? AND status='active'",
            (s['room_id'],)).fetchone()[0]
        if remaining == 0:
            conn.execute("UPDATE rooms SET status='available' WHERE id=?", (s['room_id'],))
    conn.commit(); conn.close()
