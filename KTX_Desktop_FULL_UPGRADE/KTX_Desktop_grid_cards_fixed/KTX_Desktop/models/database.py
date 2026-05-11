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
    building_offsets = {}
    for i, (student_id, fullname, gender, building_name) in enumerate(extra_students):
        exists = c.execute("SELECT id FROM students WHERE student_id=?", (student_id,)).fetchone()
        if exists:
            continue
        rooms = rooms_by_building.get(building_name) or []
        if not rooms:
            continue
        current_offset = building_offsets.get(building_name, 0)
        room = rooms[current_offset % len(rooms)]
        building_offsets[building_name] = current_offset + 1
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
    _migrate_core_schema(conn)

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

    _sync_all_beds(conn)
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
        SELECT b.*,
               (SELECT COUNT(*) FROM rooms r WHERE r.building_id=b.id) as total_rooms,
               (SELECT COUNT(*) FROM rooms r
                WHERE r.building_id=b.id
                  AND EXISTS (
                    SELECT 1 FROM students s
                    WHERE s.room_id=r.id AND s.status='active'
                  )) as occupied,
               (SELECT COUNT(*) FROM beds bd
                JOIN rooms r ON bd.room_id=r.id
                WHERE r.building_id=b.id) as total_beds,
               (SELECT COUNT(*) FROM beds bd
                JOIN rooms r ON bd.room_id=r.id
                WHERE r.building_id=b.id AND bd.status='occupied') as occupied_beds
        FROM buildings b ORDER BY b.name
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_building(name, floors, desc, manager_name='', manager_phone='', manager_email=''):
    conn = get_conn()
    conn.execute("""
        INSERT INTO buildings
            (name,floors,description,manager_name,manager_phone,manager_email)
        VALUES (?,?,?,?,?,?)
    """, (name, floors, desc, manager_name, manager_phone, manager_email))
    conn.commit(); conn.close()

def delete_building(bid):
    conn = get_conn()
    conn.execute("DELETE FROM buildings WHERE id=?", (bid,))
    conn.commit(); conn.close()

# ── ROOMS ──────────────────────────────────────────────
def get_rooms(building_id=None, status=None):
    conn = get_conn()
    q = """SELECT r.*, b.name as building_name,
               (SELECT COUNT(*) FROM students s WHERE s.room_id=r.id AND s.status='active') as current_occupants,
               (SELECT COUNT(*) FROM beds bd WHERE bd.room_id=r.id) as total_beds,
               (SELECT COUNT(*) FROM beds bd WHERE bd.room_id=r.id AND bd.status='occupied') as occupied_beds,
               (SELECT COUNT(*) FROM beds bd WHERE bd.room_id=r.id AND bd.status='empty') as empty_beds
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
    cur = conn.execute("INSERT INTO rooms (building_id,room_number,floor,capacity,type,price) VALUES (?,?,?,?,?,?)",
                       (building_id, room_number, floor, capacity, rtype, price))
    _sync_room_beds(conn, cur.lastrowid)
    conn.commit(); conn.close()

def delete_room(rid):
    conn = get_conn()
    conn.execute("DELETE FROM beds WHERE room_id=?", (rid,))
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

def add_student(student_id, fullname, gender, dob, phone, email, faculty, cls, room_id, checkin_date, status="active"):

    conn = get_conn()
    cur = conn.execute("""INSERT INTO students
        (student_id,fullname,gender,dob,phone,email,faculty,class,room_id,checkin_date,status)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (student_id, fullname, gender, dob, phone, email, faculty, cls, room_id or None, checkin_date, status))
    if room_id:
        _assign_student_to_bed(conn, cur.lastrowid, room_id)
        _refresh_room_status(conn, room_id)
    conn.commit(); conn.close()

def checkout_student(sid):
    from datetime import date
    conn = get_conn()
    s = conn.execute("SELECT room_id FROM students WHERE id=?", (sid,)).fetchone()
    conn.execute("UPDATE students SET status='checked_out', checkout_date=? WHERE id=?",
                 (date.today().isoformat(), sid))
    if s and s['room_id']:
        _clear_student_bed(conn, sid)
        _refresh_room_status(conn, s['room_id'])
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
    except sqlite3.IntegrityError:
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
    invoice_revenue = conn.execute(
        "SELECT COALESCE(SUM(total_amount),0) FROM invoices WHERE payment_status='paid' AND substr(created_date,1,7)=?",
        (month,)).fetchone()[0]
    payment_revenue = conn.execute(
        "SELECT COALESCE(SUM(amount),0) FROM payments WHERE status='paid' AND strftime('%Y-%m',paid_date)=?",
        (month,)).fetchone()[0]
    stats = {
        'total_students': conn.execute("SELECT COUNT(*) FROM students WHERE status='active'").fetchone()[0],
        'total_rooms': conn.execute("SELECT COUNT(*) FROM rooms").fetchone()[0],
        'occupied_rooms': conn.execute("SELECT COUNT(*) FROM rooms WHERE status='occupied'").fetchone()[0],
        'available_rooms': conn.execute("SELECT COUNT(*) FROM rooms WHERE status='available'").fetchone()[0],
        'pending_payments': conn.execute("SELECT COUNT(*) FROM payments WHERE status='pending'").fetchone()[0],
        'open_violations': conn.execute("SELECT COUNT(*) FROM violations WHERE status='open'").fetchone()[0],
        'monthly_revenue': invoice_revenue or payment_revenue,
        'pending_apps': conn.execute("SELECT COUNT(*) FROM applications WHERE status='pending'").fetchone()[0],
        'total_staff': conn.execute("SELECT COUNT(*) FROM users WHERE role='staff'").fetchone()[0],
    }
    conn.close()
    return stats

def get_revenue_chart():
    conn = get_conn()
    rows = conn.execute("""SELECT substr(created_date,1,7) as month,
        SUM(CASE WHEN payment_status='paid' THEN total_amount ELSE 0 END) as collected,
        SUM(total_amount) as total
        FROM invoices GROUP BY month ORDER BY month DESC LIMIT 6""").fetchall()
    if not rows:
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

def update_building(bid, name, floors, desc, manager_name=None, manager_phone=None, manager_email=None):
    conn = get_conn()
    if manager_name is None and manager_phone is None and manager_email is None:
        conn.execute("UPDATE buildings SET name=?, floors=?, description=? WHERE id=?", (name, floors, desc, bid))
    else:
        conn.execute("""
            UPDATE buildings
            SET name=?, floors=?, description=?,
                manager_name=?, manager_phone=?, manager_email=?
            WHERE id=?
        """, (name, floors, desc, manager_name or '', manager_phone or '', manager_email or '', bid))
    conn.commit(); conn.close()

def update_room(rid, room_number, floor, capacity, rtype, price, status):
    conn = get_conn()
    conn.execute("UPDATE rooms SET room_number=?,floor=?,capacity=?,type=?,price=?,status=? WHERE id=?",
                 (room_number, floor, capacity, rtype, price, status, rid))
    _sync_room_beds(conn, rid)
    if status != 'maintenance':
        _refresh_room_status(conn, rid)
    conn.commit(); conn.close()

def get_students_in_room(room_id):
    conn = get_conn()
    rows = conn.execute("""
        SELECT s.*, bd.bed_number
        FROM students s
        LEFT JOIN beds bd ON bd.student_id=s.id
        WHERE s.room_id=? AND s.status='active'
        ORDER BY COALESCE(CAST(bd.bed_number AS INTEGER), 999), s.fullname
    """, (room_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_student(sid, fullname, phone, email, faculty, cls, new_room_id=None):
    conn = get_conn()
    conn.execute("UPDATE students SET fullname=?,phone=?,email=?,faculty=?,class=? WHERE id=?",
                 (fullname, phone, email, faculty, cls, sid))
    if new_room_id:
        old = conn.execute("SELECT room_id FROM students WHERE id=?", (sid,)).fetchone()
        if old and old['room_id']:
            _clear_student_bed(conn, sid)
            _refresh_room_status(conn, old['room_id'])
        conn.execute("UPDATE students SET room_id=? WHERE id=?", (new_room_id, sid))
        _assign_student_to_bed(conn, sid, new_room_id)
        _refresh_room_status(conn, new_room_id)
    conn.commit(); conn.close()

def delete_student(sid):
    conn = get_conn()
    s = conn.execute("SELECT room_id FROM students WHERE id=?", (sid,)).fetchone()
    if s and s['room_id']:
        _clear_student_bed(conn, sid)
        _refresh_room_status(conn, s['room_id'])
    conn.execute("DELETE FROM students WHERE id=?", (sid,))
    conn.commit(); conn.close()


# ===== UPGRADE FEATURES =====


def _column_names(conn, table):
    return {row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}


def _ensure_column(conn, table, column, declaration):
    if column not in _column_names(conn, table):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {declaration}")


def _migrate_core_schema(conn):
    """Idempotent schema migration for managers, beds, and invoices."""
    _ensure_column(conn, "buildings", "manager_name", "TEXT")
    _ensure_column(conn, "buildings", "manager_phone", "TEXT")
    _ensure_column(conn, "buildings", "manager_email", "TEXT")
    _ensure_column(conn, "rooms", "floor", "INTEGER DEFAULT 1")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS beds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER,
            bed_number TEXT,
            status TEXT DEFAULT 'empty',
            student_id INTEGER,
            FOREIGN KEY (room_id) REFERENCES rooms(id),
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            room_fee REAL DEFAULT 0,
            electric_fee REAL DEFAULT 0,
            water_fee REAL DEFAULT 0,
            violation_fee REAL DEFAULT 0,
            total_amount REAL DEFAULT 0,
            payment_status TEXT DEFAULT 'unpaid',
            created_date TEXT DEFAULT CURRENT_TIMESTAMP,
            paid_date TEXT,
            note TEXT,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    """)

    _ensure_column(conn, "invoices", "room_fee", "REAL DEFAULT 0")
    _ensure_column(conn, "invoices", "electric_fee", "REAL DEFAULT 0")
    _ensure_column(conn, "invoices", "water_fee", "REAL DEFAULT 0")
    _ensure_column(conn, "invoices", "violation_fee", "REAL DEFAULT 0")
    _ensure_column(conn, "invoices", "total_amount", "REAL DEFAULT 0")
    _ensure_column(conn, "invoices", "payment_status", "TEXT DEFAULT 'unpaid'")
    _ensure_column(conn, "invoices", "created_date", "TEXT")
    _ensure_column(conn, "invoices", "paid_date", "TEXT")
    _ensure_column(conn, "invoices", "note", "TEXT")

    invoice_cols = _column_names(conn, "invoices")
    if "total" in invoice_cols:
        conn.execute("""
            UPDATE invoices
            SET total_amount=COALESCE(total, 0)
            WHERE total_amount IS NULL OR total_amount=0
        """)
    if "status" in invoice_cols:
        conn.execute("""
            UPDATE invoices
            SET payment_status=COALESCE(payment_status, status, 'unpaid')
            WHERE payment_status IS NULL OR payment_status=''
        """)
    if "created_at" in invoice_cols:
        conn.execute("""
            UPDATE invoices
            SET created_date=COALESCE(created_date, created_at, datetime('now'))
            WHERE created_date IS NULL OR created_date=''
        """)
    conn.execute("UPDATE invoices SET created_date=datetime('now') WHERE created_date IS NULL OR created_date=''")
    conn.execute("UPDATE invoices SET payment_status='unpaid' WHERE payment_status IS NULL OR payment_status=''")

    conn.execute("CREATE INDEX IF NOT EXISTS idx_beds_room ON beds(room_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_beds_student_lookup ON beds(student_id)")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_beds_room_number ON beds(room_id, bed_number)")
    try:
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_beds_one_student ON beds(student_id) WHERE student_id IS NOT NULL")
    except sqlite3.IntegrityError:
        pass
    conn.execute("CREATE INDEX IF NOT EXISTS idx_invoices_student ON invoices(student_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_invoices_month ON invoices(created_date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(payment_status)")

    conn.execute("""
        UPDATE buildings
        SET manager_name=(
            SELECT u.fullname
            FROM staff st JOIN users u ON u.id=st.user_id
            WHERE st.assigned_building=buildings.id
            ORDER BY st.id LIMIT 1
        ),
        manager_phone=(
            SELECT u.phone
            FROM staff st JOIN users u ON u.id=st.user_id
            WHERE st.assigned_building=buildings.id
            ORDER BY st.id LIMIT 1
        )
        WHERE (manager_name IS NULL OR manager_name='')
          AND EXISTS (SELECT 1 FROM staff st WHERE st.assigned_building=buildings.id)
    """)


def init_upgrade_tables():
    conn = get_conn()
    _migrate_core_schema(conn)
    _sync_all_beds(conn)
    conn.commit()
    conn.close()


def _refresh_room_status(conn, room_id):
    room = conn.execute("SELECT status FROM rooms WHERE id=?", (room_id,)).fetchone()
    if not room or room["status"] == "maintenance":
        return
    occupied = conn.execute("""
        SELECT COUNT(*) FROM students
        WHERE room_id=? AND status='active'
    """, (room_id,)).fetchone()[0]
    conn.execute(
        "UPDATE rooms SET status=? WHERE id=?",
        ("occupied" if occupied else "available", room_id)
    )


def _next_bed_number(conn, room_id):
    existing = conn.execute("SELECT bed_number FROM beds WHERE room_id=?", (room_id,)).fetchall()
    nums = []
    for row in existing:
        try:
            nums.append(int(row["bed_number"]))
        except (TypeError, ValueError):
            continue
    return str((max(nums) if nums else 0) + 1)


def _assign_student_to_bed(conn, student_id, room_id):
    current = conn.execute("SELECT id, room_id FROM beds WHERE student_id=?", (student_id,)).fetchone()
    if current and current["room_id"] == room_id:
        conn.execute("UPDATE beds SET status='occupied' WHERE id=?", (current["id"],))
        return
    if current:
        conn.execute("UPDATE beds SET student_id=NULL, status='empty' WHERE id=?", (current["id"],))

    bed = conn.execute("""
        SELECT id FROM beds
        WHERE room_id=? AND student_id IS NULL
        ORDER BY CAST(bed_number AS INTEGER), bed_number
        LIMIT 1
    """, (room_id,)).fetchone()
    if not bed:
        conn.execute("""
            INSERT INTO beds (room_id, bed_number, status)
            VALUES (?, ?, 'empty')
        """, (room_id, _next_bed_number(conn, room_id)))
        bed = conn.execute("""
            SELECT id FROM beds
            WHERE room_id=? AND student_id IS NULL
            ORDER BY CAST(bed_number AS INTEGER), bed_number
            LIMIT 1
        """, (room_id,)).fetchone()
    if bed:
        conn.execute(
            "UPDATE beds SET student_id=?, status='occupied' WHERE id=?",
            (student_id, bed["id"])
        )


def _clear_student_bed(conn, student_id):
    conn.execute(
        "UPDATE beds SET student_id=NULL, status='empty' WHERE student_id=?",
        (student_id,)
    )


def _sync_room_beds(conn, room_id):
    room = conn.execute("SELECT capacity FROM rooms WHERE id=?", (room_id,)).fetchone()
    if not room:
        return
    occupants = conn.execute("""
        SELECT id FROM students
        WHERE room_id=? AND status='active'
        ORDER BY id
    """, (room_id,)).fetchall()
    needed = max(int(room["capacity"] or 0), len(occupants))
    for num in range(1, needed + 1):
        conn.execute("""
            INSERT OR IGNORE INTO beds (room_id, bed_number, status)
            VALUES (?, ?, 'empty')
        """, (room_id, str(num)))

    occupant_ids = [row["id"] for row in occupants]
    if occupant_ids:
        marks = ",".join("?" for _ in occupant_ids)
        conn.execute(f"""
            UPDATE beds
            SET student_id=NULL, status='empty'
            WHERE room_id=? AND student_id IS NOT NULL
              AND student_id NOT IN ({marks})
        """, [room_id] + occupant_ids)
    else:
        conn.execute("UPDATE beds SET student_id=NULL, status='empty' WHERE room_id=?", (room_id,))

    for student in occupants:
        _assign_student_to_bed(conn, student["id"], room_id)
    conn.execute("""
        UPDATE beds
        SET status=CASE WHEN student_id IS NULL THEN 'empty' ELSE 'occupied' END
        WHERE room_id=?
    """, (room_id,))
    conn.execute("""
        DELETE FROM beds
        WHERE room_id=? AND student_id IS NULL AND status='empty'
          AND CAST(bed_number AS INTEGER)>?
    """, (room_id, needed))
    _refresh_room_status(conn, room_id)


def _sync_all_beds(conn):
    for room in conn.execute("SELECT id FROM rooms").fetchall():
        _sync_room_beds(conn, room["id"])


def get_building_detail(building_id):
    conn = get_conn()
    _sync_all_beds(conn)
    building = conn.execute("SELECT * FROM buildings WHERE id=?", (building_id,)).fetchone()
    if not building:
        conn.close()
        return None
    rooms = conn.execute("""
        SELECT r.*, b.name as building_name,
               (SELECT COUNT(*) FROM students s WHERE s.room_id=r.id AND s.status='active') as current_occupants,
               (SELECT COUNT(*) FROM beds bd WHERE bd.room_id=r.id) as total_beds,
               (SELECT COUNT(*) FROM beds bd WHERE bd.room_id=r.id AND bd.status='occupied') as occupied_beds,
               (SELECT COUNT(*) FROM beds bd WHERE bd.room_id=r.id AND bd.status='empty') as empty_beds
        FROM rooms r
        LEFT JOIN buildings b ON r.building_id=b.id
        WHERE r.building_id=?
        ORDER BY r.floor, r.room_number
    """, (building_id,)).fetchall()
    conn.commit()
    conn.close()

    floors = {}
    for room in [dict(r) for r in rooms]:
        floors.setdefault(room.get("floor") or 1, []).append(room)
    return {
        "building": dict(building),
        "floors": [{"floor": floor, "rooms": floors[floor]} for floor in sorted(floors)],
    }


def get_room_beds(room_id):
    conn = get_conn()
    _sync_room_beds(conn, room_id)
    rows = conn.execute("""
        SELECT bd.*, s.fullname, s.student_id as student_code
        FROM beds bd
        LEFT JOIN students s ON s.id=bd.student_id
        WHERE bd.room_id=?
        ORDER BY CAST(bd.bed_number AS INTEGER), bd.bed_number
    """, (room_id,)).fetchall()
    conn.commit()
    conn.close()
    return [dict(r) for r in rows]


def _money_value(value):
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def get_students_for_invoice():
    conn = get_conn()
    rows = conn.execute("""
        SELECT s.id, s.student_id, s.fullname, r.room_number, r.price,
               b.name as building_name,
               COALESCE((
                   SELECT SUM(v.fine)
                   FROM violations v
                   WHERE v.student_id=s.id AND v.status='open'
               ), 0) as open_violation_fines
        FROM students s
        LEFT JOIN rooms r ON s.room_id=r.id
        LEFT JOIN buildings b ON r.building_id=b.id
        WHERE s.status='active'
        ORDER BY s.fullname
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_invoice(student_id, room_fee=0, electric_fee=0, water_fee=0,
                violation_fee=0, payment_status='unpaid', created_date=None, note=''):
    from datetime import date
    room_fee = _money_value(room_fee)
    electric_fee = _money_value(electric_fee)
    water_fee = _money_value(water_fee)
    violation_fee = _money_value(violation_fee)
    total = room_fee + electric_fee + water_fee + violation_fee
    status = payment_status if payment_status in ("paid", "unpaid") else "unpaid"
    created = created_date or date.today().isoformat()

    conn = get_conn()
    cur = conn.execute("""
        INSERT INTO invoices
            (student_id, room_fee, electric_fee, water_fee, violation_fee,
             total_amount, payment_status, created_date, paid_date, note)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, CASE WHEN ?='paid' THEN date('now') ELSE NULL END, ?)
    """, (student_id, room_fee, electric_fee, water_fee, violation_fee,
          total, status, created, status, note))
    conn.commit()
    invoice_id = cur.lastrowid
    conn.close()
    return invoice_id


def generate_invoice(student_id, room_fee=0, electric_fee=0, water_fee=0, violation_fee=0):
    return add_invoice(student_id, room_fee, electric_fee, water_fee, violation_fee)


def get_invoices(month=None, status=None, search=''):
    conn = get_conn()
    q = """
        SELECT i.*, i.total_amount as total, i.payment_status as status,
               i.created_date as created_at,
               s.fullname, s.student_id as sid, r.room_number, b.name as building_name
        FROM invoices i
        JOIN students s ON i.student_id=s.id
        LEFT JOIN rooms r ON s.room_id=r.id
        LEFT JOIN buildings b ON r.building_id=b.id
        WHERE 1=1
    """
    p = []
    if month:
        q += " AND substr(i.created_date, 1, 7)=?"
        p.append(month)
    if status:
        q += " AND i.payment_status=?"
        p.append(status)
    if search:
        q += " AND (s.fullname LIKE ? OR s.student_id LIKE ?)"
        p += [f"%{search}%"] * 2
    q += " ORDER BY i.created_date DESC, i.id DESC"
    rows = conn.execute(q, p).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_invoice_summary(month):
    conn = get_conn()
    row = conn.execute("""
        SELECT
            COALESCE(SUM(CASE WHEN payment_status='paid' THEN total_amount ELSE 0 END), 0) as total_revenue,
            COALESCE(SUM(CASE WHEN payment_status='unpaid' THEN total_amount ELSE 0 END), 0) as unpaid_amount,
            COALESCE(SUM(CASE WHEN payment_status='paid' THEN 1 ELSE 0 END), 0) as paid_invoices,
            COALESCE(SUM(CASE WHEN payment_status='unpaid' THEN 1 ELSE 0 END), 0) as unpaid_invoices,
            COUNT(*) as total_invoices
        FROM invoices
        WHERE substr(created_date, 1, 7)=?
    """, (month,)).fetchone()
    conn.close()
    return dict(row)


def mark_invoice_paid(invoice_id):
    from datetime import date
    conn = get_conn()
    conn.execute("""
        UPDATE invoices
        SET payment_status='paid', paid_date=?
        WHERE id=?
    """, (date.today().isoformat(), invoice_id))
    conn.commit()
    conn.close()


def mark_invoice_unpaid(invoice_id):
    conn = get_conn()
    conn.execute("""
        UPDATE invoices
        SET payment_status='unpaid', paid_date=NULL
        WHERE id=?
    """, (invoice_id,))
    conn.commit()
    conn.close()


def get_revenue_by_building(month):
    conn = get_conn()
    rows = conn.execute("""
        SELECT COALESCE(b.name, 'Chua phan phong') as building_name,
               COALESCE(SUM(CASE WHEN i.payment_status='paid' THEN i.total_amount ELSE 0 END), 0) as revenue,
               COALESCE(SUM(CASE WHEN i.payment_status='unpaid' THEN i.total_amount ELSE 0 END), 0) as unpaid_amount,
               COALESCE(SUM(CASE WHEN i.payment_status='paid' THEN 1 ELSE 0 END), 0) as paid_invoices,
               COALESCE(SUM(CASE WHEN i.payment_status='unpaid' THEN 1 ELSE 0 END), 0) as unpaid_invoices,
               COUNT(i.id) as total_invoices
        FROM invoices i
        JOIN students s ON i.student_id=s.id
        LEFT JOIN rooms r ON s.room_id=r.id
        LEFT JOIN buildings b ON r.building_id=b.id
        WHERE substr(i.created_date, 1, 7)=?
        GROUP BY COALESCE(b.name, 'Chua phan phong')
        ORDER BY revenue DESC, building_name
    """, (month,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_revenue_report(month):
    return {
        "summary": get_invoice_summary(month),
        "by_building": get_revenue_by_building(month),
        "invoices": get_invoices(month=month),
    }


def get_monthly_revenue():
    conn = get_conn()
    rows = conn.execute("""
        SELECT substr(created_date,1,7) as month,
               COALESCE(SUM(CASE WHEN payment_status='paid' THEN total_amount ELSE 0 END), 0) as revenue
        FROM invoices
        GROUP BY month
        ORDER BY month DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]
