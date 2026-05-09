"""
SmartBrgy Backend API v2 — COMPLETE
Barangay Anabu I-G, Imus City
Flask + SQLite — Lahat ng modules naka-save na
"""

from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import sqlite3, os, uuid, json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, date

app = Flask(__name__)

# ─────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────
GMAIL_USER         = 'brgy.anabu.1g.imus@gmail.com'
GMAIL_APP_PASSWORD = 'kdxdkejttsgyzonp'
UPLOAD_FOLDER      = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTS       = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'heic', 'webp'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

EMAIL_SUBJECT = 'Barangay Anabu I-G — Natanggap ang inyong Request'
EMAIL_BODY = """\
Magandang araw!

Natanggap na po ng Barangay ANABU I-G ang inyong request at ito ay kasalukuyan nang pinoproseso. Mangyaring hintayin na lamang po ang susunod na abiso kaugnay ng status o release ng inyong hinihiling na dokumento.

Pinapaalalahanan din po kayo na magdala ng mga sumusunod sa pagkuha ng inyong dokumento:

• Valid ID
• Anumang patunay na kayo ay residente ng Brgy. Anabu I-G
• Kaukulang bayad para sa hinihiling na dokumento

Maraming salamat po.
"""

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTS

def send_email(to_email):
    if not to_email:
        print("[EMAIL] Walang email address — hindi pinadala.")
        return False
    print(f"[EMAIL] Sinusubukang magpadala kay: {to_email}")
    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = EMAIL_SUBJECT
        msg.attach(MIMEText(EMAIL_BODY, 'plain', 'utf-8'))
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            smtp.send_message(msg)
        print(f"[EMAIL] ✅ Matagumpay na napadala kay {to_email}")
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] ❌ {e}")
        return False

@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

@app.before_request
def handle_options():
    if request.method == 'OPTIONS':
        from flask import Response
        r = Response()
        r.headers['Access-Control-Allow-Origin'] = '*'
        r.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
        r.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        return r, 200

DB_PATH = os.path.join(os.path.dirname(__file__), 'smartbrgy.db')

# ─────────────────────────────────────────
# DB HELPERS
# ─────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def rows_to_list(rows):
    return [dict(r) for r in rows]

def calc_age(dob_str):
    try:
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        today = date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    except:
        return 0

def add_audit(db, icon, category, action, detail, user='System'):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.execute("INSERT INTO audit_log (icon,category,action,detail,user,created_at) VALUES (?,?,?,?,?,?)",
               (icon, category, action, detail, user, now))

def gen_id(prefix=''):
    return prefix + str(uuid.uuid4())[:8].upper()

# ─────────────────────────────────────────
# INIT DATABASE
# ─────────────────────────────────────────
def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS residents (
            id             TEXT PRIMARY KEY,
            name           TEXT NOT NULL,
            purok          TEXT,
            dob            TEXT,
            gender         TEXT,
            civil          TEXT,
            contact        TEXT,
            status         TEXT DEFAULT 'Active',
            household      TEXT,
            type           TEXT,
            address        TEXT,
            special_groups TEXT DEFAULT '[]',
            created_at     TEXT DEFAULT (datetime('now')),
            updated_at     TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS resident_status (
            resident_id     TEXT PRIMARY KEY,
            good_standing   INTEGER DEFAULT 1,
            blotter         INTEGER DEFAULT 0,
            blotter_details TEXT DEFAULT '[]',
            FOREIGN KEY (resident_id) REFERENCES residents(id)
        );

        CREATE TABLE IF NOT EXISTS incidents (
            id          TEXT PRIMARY KEY,
            type        TEXT NOT NULL,
            location    TEXT,
            date        TEXT,
            reported_by TEXT,
            complainee  TEXT,
            status      TEXT DEFAULT 'Pending',
            severity    TEXT DEFAULT 'Medium',
            description TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS cert_requests (
            code        TEXT PRIMARY KEY,
            resident_id TEXT,
            name        TEXT NOT NULL,
            type        TEXT NOT NULL,
            cert_id     TEXT,
            purpose     TEXT,
            address     TEXT,
            contact     TEXT,
            status      TEXT DEFAULT 'Processing',
            via         TEXT DEFAULT 'Online',
            requested   TEXT DEFAULT (datetime('now')),
            source      TEXT DEFAULT 'portal'
        );

        CREATE TABLE IF NOT EXISTS rfid_tags (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            location    TEXT,
            type        TEXT,
            status      TEXT DEFAULT 'In Cabinet',
            last_scan   TEXT
        );

        CREATE TABLE IF NOT EXISTS cabinet_folders (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            rfid        TEXT,
            drawer      TEXT,
            status      TEXT DEFAULT 'In Cabinet'
        );

        CREATE TABLE IF NOT EXISTS cabinet_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            drawer_id   TEXT,
            drawer_label TEXT,
            action      TEXT,
            user        TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS users (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            role        TEXT,
            access      TEXT DEFAULT 'View Only',
            username    TEXT,
            password    TEXT,
            face        INTEGER DEFAULT 0,
            rfid        INTEGER DEFAULT 0,
            status      TEXT DEFAULT 'Active',
            last_login  TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS audit_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            icon        TEXT,
            category    TEXT,
            action      TEXT NOT NULL,
            detail      TEXT,
            user        TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS purok_data (
            key_name    TEXT PRIMARY KEY,
            label       TEXT,
            total       INTEGER DEFAULT 0,
            color       TEXT,
            pct         INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS portal_terms_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT,
            contact     TEXT,
            agreed_at   TEXT DEFAULT (datetime('now')),
            ip          TEXT
        );
        """)

        # ── Migrate incidents: add missing columns for older databases ──
        for col_sql in [
            "ALTER TABLE incidents ADD COLUMN complainee TEXT",
            "ALTER TABLE incidents ADD COLUMN attachments TEXT DEFAULT '[]'",
        ]:
            try:
                db.execute(col_sql)
            except Exception:
                pass

        # ── Migrate residents: add missing columns for older databases ──
        for col_sql in [
            "ALTER TABLE residents ADD COLUMN address TEXT",
            "ALTER TABLE residents ADD COLUMN special_groups TEXT DEFAULT '[]'",
        ]:
            try:
                db.execute(col_sql)
            except Exception:
                pass

        # ── Migrate cert_requests: add missing columns for older databases ──
        for col_sql in [
            "ALTER TABLE cert_requests ADD COLUMN attachment TEXT",
            "ALTER TABLE cert_requests ADD COLUMN email TEXT",
            "ALTER TABLE cert_requests ADD COLUMN hidden INTEGER DEFAULT 0",
            "ALTER TABLE cert_requests ADD COLUMN dob TEXT",
        ]:
            try:
                db.execute(col_sql)
            except Exception:
                pass

        # ── Migrate purok_data: add missing columns for older databases ──
        for col_sql in [
            "ALTER TABLE purok_data ADD COLUMN color TEXT",
            "ALTER TABLE purok_data ADD COLUMN pct INTEGER DEFAULT 0",
            "ALTER TABLE purok_data ADD COLUMN label TEXT",
        ]:
            try:
                db.execute(col_sql)
            except Exception:
                pass

        # ── Seed super admin only ──
        sys_users = [
            ('USR-001','Juan dela Cruz','Super Administrator','Full Access','admin','Admin@1234!',1,1,'Active',''),
        ]
        db.executemany("INSERT OR IGNORE INTO users (id,name,role,access,username,password,face,rfid,status,last_login) VALUES (?,?,?,?,?,?,?,?,?,?)", sys_users)

        db.commit()
    print("✅ Database initialized:", DB_PATH)


# ══════════════════════════════════════════
# RESIDENTS
# ══════════════════════════════════════════
@app.route('/api/residents', methods=['GET'])
def get_residents():
    with get_db() as db:
        rows = db.execute("SELECT r.*, rs.good_standing, rs.blotter, rs.blotter_details FROM residents r LEFT JOIN resident_status rs ON r.id=rs.resident_id ORDER BY r.name").fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d['age'] = calc_age(d['dob'])
            d['blotter_details'] = json.loads(d.get('blotter_details') or '[]')
            result.append(d)
        return jsonify(result)

@app.route('/api/residents/<rid>', methods=['GET'])
def get_resident(rid):
    with get_db() as db:
        r = db.execute("SELECT r.*, rs.good_standing, rs.blotter, rs.blotter_details FROM residents r LEFT JOIN resident_status rs ON r.id=rs.resident_id WHERE r.id=?", (rid,)).fetchone()
        if not r: return jsonify({'error': 'Not found'}), 404
        d = dict(r)
        d['age'] = calc_age(d['dob'])
        d['blotter_details'] = json.loads(d.get('blotter_details') or '[]')
        return jsonify(d)

@app.route('/api/residents', methods=['POST'])
def add_resident():
    data = request.get_json()
    new_id = 'ANB-' + gen_id()
    special_groups = json.dumps(data.get('specialGroups') or [])
    with get_db() as db:
        db.execute(
            "INSERT INTO residents (id,name,purok,dob,gender,civil,contact,status,household,type,address,special_groups) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (new_id, data['name'], data.get('purok',''), data.get('dob',''), data.get('gender',''),
             data.get('civil',''), data.get('contact',''), data.get('status','Active'),
             data.get('household',''), data.get('type',''), data.get('address',''), special_groups))
        db.execute("INSERT OR IGNORE INTO resident_status (resident_id,good_standing,blotter,blotter_details) VALUES (?,1,0,'[]')", (new_id,))
        add_audit(db, '🧑', 'record', 'New Resident Registered', f"{data['name']} — {new_id}", data.get('by','Staff'))
        db.commit()
    return jsonify({'id': new_id, 'message': 'Resident added'}), 201

@app.route('/api/residents/<rid>', methods=['PUT'])
def update_resident(rid):
    data = request.get_json()
    special_groups = json.dumps(data.get('specialGroups') or [])
    with get_db() as db:
        db.execute(
            "UPDATE residents SET name=?,purok=?,dob=?,gender=?,civil=?,contact=?,status=?,household=?,type=?,address=?,special_groups=?,updated_at=datetime('now') WHERE id=?",
            (data['name'], data.get('purok'), data.get('dob'), data.get('gender'), data.get('civil'),
             data.get('contact'), data.get('status','Active'), data.get('household'), data.get('type'),
             data.get('address',''), special_groups, rid))
        add_audit(db, '✏️', 'record', 'Resident Record Updated', f"{data['name']} — {rid}", data.get('by','Staff'))
        db.commit()
    return jsonify({'message': 'Updated'})

@app.route('/api/residents/<rid>', methods=['DELETE'])
def delete_resident(rid):
    with get_db() as db:
        r = db.execute("SELECT name FROM residents WHERE id=?", (rid,)).fetchone()
        if not r: return jsonify({'error': 'Not found'}), 404
        db.execute("DELETE FROM residents WHERE id=?", (rid,))
        db.execute("DELETE FROM resident_status WHERE resident_id=?", (rid,))
        add_audit(db, '🗑️', 'record', 'Resident Deleted', f"{r['name']} — {rid}", 'Staff')
        db.commit()
    return jsonify({'message': 'Deleted'})

@app.route('/api/residents/<rid>/status', methods=['PUT'])
def update_resident_status(rid):
    data = request.get_json()
    with get_db() as db:
        db.execute("INSERT OR REPLACE INTO resident_status (resident_id,good_standing,blotter,blotter_details) VALUES (?,?,?,?)",
                   (rid, 1 if data.get('good_standing', True) else 0, 1 if data.get('blotter', False) else 0, json.dumps(data.get('blotter_details', []))))
        add_audit(db, '📋', 'record', 'Resident Status Updated', f"{rid}", data.get('by','Staff'))
        db.commit()
    return jsonify({'message': 'Status updated'})


# ══════════════════════════════════════════
# CERT REQUESTS
# ══════════════════════════════════════════
@app.route('/api/cert-requests', methods=['GET'])
def get_cert_requests():
    with get_db() as db:
        rows = db.execute("SELECT * FROM cert_requests ORDER BY requested DESC").fetchall()
        return jsonify(rows_to_list(rows))

@app.route('/api/cert-requests', methods=['POST'])
def submit_cert_request():
    data = request.get_json()
    year = datetime.now().strftime('%Y')
    count = get_db().execute("SELECT COUNT(*) FROM cert_requests WHERE requested LIKE ?", (f'{year}%',)).fetchone()[0]
    code = f"REQ-{year}-{str(count+1).zfill(4)}"
    attachment = data.get('attachment', '')
    email = data.get('email', '')
    dob = data.get('dob', '')
    print(f"[REQUEST] name={data.get('name','')} | dob={dob} | email={data.get('email','')}")
    with get_db() as db:
        db.execute("INSERT INTO cert_requests (code,resident_id,name,type,cert_id,purpose,address,contact,email,dob,status,via,source,attachment) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                   (code, data.get('resident_id',''), data['name'], data['type'], data.get('cert_id',''), data.get('purpose',''), data.get('address',''), data.get('contact',''), email, dob, 'Processing', data.get('via','Online'), data.get('source','portal'), attachment))
        add_audit(db, '📨', 'cert', 'Certificate Request Submitted', f"{code} — {data['name']} — {data['type']}", data.get('via','Portal'))
        db.commit()
    if email:
        send_email(email)
    return jsonify({'code': code, 'message': 'Request submitted'}), 201

@app.route('/api/cert-requests/<code>/status', methods=['PUT'])
def update_cert_status(code):
    data = request.get_json()
    with get_db() as db:
        r = db.execute("SELECT * FROM cert_requests WHERE code=?", (code,)).fetchone()
        if not r: return jsonify({'error': 'Not found'}), 404
        db.execute("UPDATE cert_requests SET status=? WHERE code=?", (data['status'], code))
        add_audit(db, '📋', 'cert', f"Certificate Status → {data['status']}", f"{code} — {r['name']}", data.get('user','Staff'))
        db.commit()
    return jsonify({'message': 'Updated'})

@app.route('/api/cert-requests/<code>', methods=['DELETE'])
def delete_cert_request(code):
    with get_db() as db:
        db.execute("DELETE FROM cert_requests WHERE code=?", (code,))
        db.commit()
    return jsonify({'message': 'Deleted'})

@app.route('/api/cert-requests/<code>/hide', methods=['PUT'])
def hide_cert_request(code):
    with get_db() as db:
        db.execute("UPDATE cert_requests SET hidden=1 WHERE code=?", (code,))
        db.commit()
    return jsonify({'message': 'Hidden'})


# ══════════════════════════════════════════
# INCIDENTS
# ══════════════════════════════════════════
@app.route('/api/incidents', methods=['GET'])
def get_incidents():
    with get_db() as db:
        rows = db.execute("SELECT * FROM incidents ORDER BY created_at DESC").fetchall()
        return jsonify(rows_to_list(rows))

@app.route('/api/incidents', methods=['POST'])
def add_incident():
    data = request.get_json()
    today = datetime.now().strftime('%b %d, %Y')
    year = datetime.now().strftime('%Y')
    count = get_db().execute("SELECT COUNT(*) FROM incidents WHERE id LIKE ?", (f'INC-{year}%',)).fetchone()[0]
    new_id = f"INC-{year}-{str(count+1).zfill(3)}"
    attachments = data.get('attachments', '[]')
    with get_db() as db:
        db.execute("INSERT INTO incidents (id,type,location,date,reported_by,complainee,status,severity,description,attachments) VALUES (?,?,?,?,?,?,?,?,?,?)",
                   (new_id, data['type'], data.get('location',''), today, data.get('reported_by','Anonymous'), data.get('complainee',''), 'Pending', data.get('severity','Medium'), data.get('description',''), attachments))
        add_audit(db, '🚨', 'incident', 'Incident Report Filed', f"{new_id} — {data['type']}", data.get('reported_by','Staff'))
        db.commit()
    return jsonify({'id': new_id, 'message': 'Incident filed'}), 201

@app.route('/api/incidents/<iid>', methods=['DELETE'])
def delete_incident(iid):
    with get_db() as db:
        row = db.execute("SELECT type FROM incidents WHERE id=?", (iid,)).fetchone()
        if not row: return jsonify({'error': 'Not found'}), 404
        db.execute("DELETE FROM incidents WHERE id=?", (iid,))
        add_audit(db, '🗑️', 'incident', 'Incident Report Deleted', iid, 'Staff')
        db.commit()
    return jsonify({'message': 'Deleted'})

@app.route('/api/incidents/<iid>/status', methods=['PUT'])
def update_incident_status(iid):
    data = request.get_json()
    with get_db() as db:
        db.execute("UPDATE incidents SET status=? WHERE id=?", (data['status'], iid))
        add_audit(db, '🔄', 'incident', f"Incident → {data['status']}", iid, data.get('user','Staff'))
        db.commit()
    return jsonify({'message': 'Updated'})

@app.route('/api/incidents/<iid>', methods=['PUT'])
def update_incident(iid):
    data = request.get_json() or {}
    with get_db() as db:
        row = db.execute("SELECT * FROM incidents WHERE id=?", (iid,)).fetchone()
        if not row:
            return jsonify({'error': 'Incident not found'}), 404
        db.execute("""
            UPDATE incidents
               SET type=?,
                   location=?,
                   date=?,
                   reported_by=?,
                   complainee=?,
                   status=?,
                   severity=?,
                   description=?,
                   attachments=?
             WHERE id=?
        """, (
            data.get('type', row['type']),
            data.get('location', row['location']),
            data.get('date', row['date']),
            data.get('reported_by', row['reported_by']),
            data.get('complainee', row['complainee'] if row['complainee'] else ''),
            data.get('status', row['status']),
            data.get('severity', row['severity']),
            data.get('description', row['description']),
            data.get('attachments', row['attachments'] if 'attachments' in row.keys() else '[]'),
            iid
        ))
        add_audit(db, '✏️', 'incident', 'Incident Report Updated', iid, data.get('user','Staff'))
        db.commit()
    return jsonify({'message': 'Incident updated', 'id': iid})


# ══════════════════════════════════════════
# RFID TAGS
# ══════════════════════════════════════════
@app.route('/api/rfid', methods=['GET'])
def get_rfid():
    with get_db() as db:
        return jsonify(rows_to_list(db.execute("SELECT * FROM rfid_tags").fetchall()))

@app.route('/api/rfid/<tag_id>/scan', methods=['POST'])
def scan_rfid(tag_id):
    data = request.get_json()
    new_status = data.get('status','In Cabinet')
    now = datetime.now().isoformat()
    with get_db() as db:
        tag = db.execute("SELECT * FROM rfid_tags WHERE id=?", (tag_id,)).fetchone()
        if not tag: return jsonify({'error': 'Not found'}), 404
        db.execute("UPDATE rfid_tags SET status=?,last_scan=? WHERE id=?", (new_status, now, tag_id))
        add_audit(db, '📡', 'rfid', f'RFID Scan — {new_status}', f"{tag_id} — {tag['name']}", 'RFID Reader')
        db.commit()
    return jsonify({'message': 'Updated', 'last_scan': now})


# ══════════════════════════════════════════
# CABINET FOLDERS
# ══════════════════════════════════════════
@app.route('/api/cabinet/folders', methods=['GET'])
def get_cabinet_folders():
    with get_db() as db:
        return jsonify(rows_to_list(db.execute("SELECT * FROM cabinet_folders").fetchall()))

@app.route('/api/cabinet/folders/<fid>/status', methods=['PUT'])
def update_folder_status(fid):
    data = request.get_json()
    with get_db() as db:
        f = db.execute("SELECT * FROM cabinet_folders WHERE id=?", (fid,)).fetchone()
        if not f: return jsonify({'error': 'Not found'}), 404
        db.execute("UPDATE cabinet_folders SET status=? WHERE id=?", (data['status'], fid))
        add_audit(db, '📁', 'rfid', f"Folder {data['status']}", f"{fid} — {f['name']}", data.get('user','Staff'))
        db.commit()
    return jsonify({'message': 'Updated'})

@app.route('/api/cabinet/log', methods=['GET'])
def get_cabinet_log():
    with get_db() as db:
        rows = db.execute("SELECT * FROM cabinet_log ORDER BY created_at DESC LIMIT 50").fetchall()
        return jsonify(rows_to_list(rows))

@app.route('/api/cabinet/log', methods=['POST'])
def add_cabinet_log():
    data = request.get_json()
    with get_db() as db:
        db.execute("INSERT INTO cabinet_log (drawer_id,drawer_label,action,user) VALUES (?,?,?,?)",
                   (data.get('drawer_id',''), data.get('drawer_label',''), data.get('action',''), data.get('user','Staff')))
        db.commit()
    return jsonify({'message': 'Logged'}), 201


# ══════════════════════════════════════════
# USERS
# ══════════════════════════════════════════
@app.route('/api/users', methods=['GET'])
def get_users():
    with get_db() as db:
        rows = db.execute("SELECT id,name,role,access,username,password,face,rfid,status,last_login,created_at FROM users ORDER BY created_at").fetchall()
        return jsonify(rows_to_list(rows))

@app.route('/api/users/login', methods=['POST'])
def login_user():
    """Check login credentials — returns user info if valid"""
    data = request.get_json()
    username = data.get('username','').strip()
    password = data.get('password','')
    emp_id   = data.get('emp_id','').strip()
    with get_db() as db:
        # Match by username + password, optionally by emp_id/user id
        user = db.execute(
            "SELECT id,name,role,access,username,face,rfid,status FROM users WHERE username=? AND password=? AND status='Active'",
            (username, password)
        ).fetchone()
        if not user:
            # Also try matching name-based username
            user = db.execute(
                "SELECT id,name,role,access,username,face,rfid,status FROM users WHERE LOWER(REPLACE(name,' ','.'))=? AND password=? AND status='Active'",
                (username.lower(), password)
            ).fetchone()
        if not user:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        # Update last login
        db.execute("UPDATE users SET last_login=datetime('now') WHERE id=?", (user['id'],))
        add_audit(db, '🔐', 'auth', 'Login Successful', f"{user['name']} — {user['role']}", user['name'])
        db.commit()
        return jsonify({'success': True, 'user': dict(user)})

@app.route('/api/users', methods=['POST'])
def add_user():
    data = request.get_json()
    name = data.get('name','').strip()
    if not name: return jsonify({'error': 'Name required'}), 400
    count = get_db().execute("SELECT COUNT(*) FROM users").fetchone()[0]
    new_id = f"USR-{str(count+1).zfill(3)}"
    with get_db() as db:
        # check duplicate
        existing = db.execute("SELECT id FROM users WHERE id=?", (new_id,)).fetchone()
        if existing:
            new_id = 'USR-' + gen_id()
        db.execute("INSERT INTO users (id,name,role,access,username,password,face,rfid,status) VALUES (?,?,?,?,?,?,?,?,?)",
                   (new_id, name, data.get('role','Barangay Clerk'), data.get('access','View Only'),
                    data.get('username',''), data.get('password',''), 1 if data.get('face') else 0,
                    1 if data.get('rfid') else 0, 'Active'))
        add_audit(db, '👤', 'auth', 'New User Created', f"{name} — {data.get('role')} — {new_id}", 'Admin')
        db.commit()
    return jsonify({'id': new_id, 'message': 'User created'}), 201

@app.route('/api/users/<uid>', methods=['PUT'])
def update_user(uid):
    data = request.get_json()
    with get_db() as db:
        db.execute("UPDATE users SET name=?,role=?,access=?,username=?,face=?,rfid=?,status=? WHERE id=?",
                   (data['name'], data.get('role'), data.get('access'), data.get('username'),
                    1 if data.get('face') else 0, 1 if data.get('rfid') else 0, data.get('status','Active'), uid))
        add_audit(db, '✏️', 'auth', 'User Updated', f"{data['name']} — {uid}", 'Admin')
        db.commit()
    return jsonify({'message': 'Updated'})

@app.route('/api/users/<uid>/suspend', methods=['PUT'])
def suspend_user(uid):
    with get_db() as db:
        u = db.execute("SELECT name FROM users WHERE id=?", (uid,)).fetchone()
        if not u: return jsonify({'error': 'Not found'}), 404
        db.execute("UPDATE users SET status='Suspended' WHERE id=?", (uid,))
        add_audit(db, '🚫', 'security', 'User Suspended', f"{u['name']} — {uid}", 'Admin')
        db.commit()
    return jsonify({'message': 'Suspended'})

@app.route('/api/users/<uid>/activate', methods=['PUT'])
def activate_user(uid):
    with get_db() as db:
        u = db.execute("SELECT name FROM users WHERE id=?", (uid,)).fetchone()
        if not u: return jsonify({'error': 'Not found'}), 404
        db.execute("UPDATE users SET status='Active' WHERE id=?", (uid,))
        add_audit(db, '✅', 'auth', 'User Activated', f"{u['name']} — {uid}", 'Admin')
        db.commit()
    return jsonify({'message': 'Activated'})


# ══════════════════════════════════════════
# AUDIT LOG
# ══════════════════════════════════════════
@app.route('/api/audit', methods=['GET'])
def get_audit():
    limit = int(request.args.get('limit', 100))
    with get_db() as db:
        rows = db.execute("SELECT * FROM audit_log ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return jsonify(rows_to_list(rows))

@app.route('/api/audit', methods=['POST'])
def post_audit():
    data = request.get_json()
    with get_db() as db:
        add_audit(db, data.get('icon','📌'), data.get('category','general'), data['action'], data.get('detail',''), data.get('user','Staff'))
        db.commit()
    return jsonify({'message': 'Logged'}), 201


# ══════════════════════════════════════════
# ELIGIBILITY CHECK
# ══════════════════════════════════════════
@app.route('/api/eligibility', methods=['POST'])
def check_eligibility():
    data = request.get_json()
    resident_id = data.get('resident_id')
    cert_id = data.get('cert_id')
    RULES = {
        'BC':   {'label':'Barangay Clearance','requiresActive':True,'needsGoodStanding':True,'oneTimeOnly':False},
        'CR':   {'label':'Certificate of Residency','requiresActive':True,'needsGoodStanding':False,'oneTimeOnly':False},
        'CI':   {'label':'Certificate of Indigency','requiresActive':True,'needsGoodStanding':False,'oneTimeOnly':False},
        'BID':  {'label':'Barangay ID','requiresActive':True,'needsGoodStanding':True,'oneTimeOnly':False},
        'CTFJ': {'label':'First Time Jobseeker','requiresActive':True,'needsGoodStanding':False,'oneTimeOnly':True},
        'BBC':  {'label':'Business Clearance','requiresActive':True,'needsGoodStanding':True,'oneTimeOnly':False},
    }
    rule = RULES.get(cert_id)
    if not rule: return jsonify({'eligible':False,'reasons':['Unknown document type.']}), 400
    with get_db() as db:
        resident = db.execute("SELECT * FROM residents WHERE id=?", (resident_id,)).fetchone()
        rs = db.execute("SELECT * FROM resident_status WHERE resident_id=?", (resident_id,)).fetchone()
        if not resident: return jsonify({'eligible':False,'reasons':['Resident not found.']}), 404
        eligible = True
        reasons = []
        if rule['requiresActive'] and resident['status'] != 'Active':
            eligible = False; reasons.append('❌ Hindi aktibo ang residente.')
        if rule['needsGoodStanding'] and rs and not rs['good_standing']:
            eligible = False
            bl = json.loads(rs['blotter_details'] or '[]')
            reasons.append('❌ May blotter record: ' + (', '.join(bl) if bl else 'Tingnan sa records'))
        if rule['oneTimeOnly']:
            prev = db.execute("SELECT code FROM cert_requests WHERE resident_id=? AND cert_id=? AND status='Completed'", (resident_id,cert_id)).fetchone()
            if prev:
                eligible = False; reasons.append(f"❌ One-time only. Nakuha na noong code: {prev['code']}")
        if eligible:
            if rs and rs['good_standing']: reasons.append('✅ Nasa mabuting kalagayan.')
            if resident['status'] == 'Active': reasons.append('✅ Active na residente.')
        return jsonify({'eligible':eligible,'reasons':reasons,'resident':dict(resident),'rule':rule})


# ══════════════════════════════════════════
# DASHBOARD STATS
# ══════════════════════════════════════════
@app.route('/api/dashboard/stats', methods=['GET'])
def dashboard_stats():
    with get_db() as db:
        total = db.execute("SELECT COUNT(*) FROM residents WHERE status='Active'").fetchone()[0]
        pending_req = db.execute("SELECT COUNT(*) FROM cert_requests WHERE status='Processing'").fetchone()[0]
        ready_req = db.execute("SELECT COUNT(*) FROM cert_requests WHERE status='Ready to Print'").fetchone()[0]
        total_req = db.execute("SELECT COUNT(*) FROM cert_requests").fetchone()[0]
        completed_req = db.execute("SELECT COUNT(*) FROM cert_requests WHERE status='Completed'").fetchone()[0]
        pending_inc = db.execute("SELECT COUNT(*) FROM incidents WHERE status='Pending'").fetchone()[0]
        total_inc = db.execute("SELECT COUNT(*) FROM incidents").fetchone()[0]
        dobs = db.execute("SELECT dob FROM residents WHERE status='Active'").fetchall()
        seniors = sum(1 for r in dobs if calc_age(r['dob']) >= 60)
        portal_req = db.execute("SELECT COUNT(*) FROM cert_requests WHERE source='portal'").fetchone()[0]
        return jsonify({'total_residents':total,'pending_requests':pending_req,'ready_requests':ready_req,
                        'total_requests':total_req,'completed_requests':completed_req,
                        'pending_incidents':pending_inc,'total_incidents':total_inc,
                        'senior_count':seniors,'portal_requests':portal_req})

@app.route('/api/purok', methods=['GET', 'POST'])
def get_purok():
    with get_db() as db:
        if request.method == 'POST':
            data = request.get_json() or {}
            key_name = (data.get('key_name') or data.get('key') or '').strip()
            label = (data.get('label') or key_name).strip()
            color = (data.get('color') or 'var(--green-500)').strip()
            total = int(data.get('total') or 0)
            pct = int(data.get('pct') or 0)
            if not key_name:
                return jsonify({'error': 'Purok name is required'}), 400
            exists = db.execute("SELECT key_name FROM purok_data WHERE LOWER(key_name)=LOWER(?)", (key_name,)).fetchone()
            if exists:
                return jsonify({'error': 'Purok already exists'}), 409
            db.execute(
                "INSERT INTO purok_data (key_name,label,total,color,pct) VALUES (?,?,?,?,?)",
                (key_name, label, total, color, pct)
            )
            add_audit(db, 'zone', 'record', 'Purok Added', key_name, data.get('by', 'Staff'))
            db.commit()
            return jsonify({'key_name': key_name, 'label': label, 'total': total, 'color': color, 'pct': pct}), 201
        return jsonify(rows_to_list(db.execute("SELECT * FROM purok_data").fetchall()))

@app.route('/api/purok/<key_name>', methods=['PUT'])
def update_purok(key_name):
    data = request.get_json() or {}
    label = data.get('label', key_name).strip()
    color = data.get('color', 'var(--green-500)').strip()
    with get_db() as db:
        existing = db.execute("SELECT * FROM purok_data WHERE key_name=?", (key_name,)).fetchone()
        if not existing:
            return jsonify({'error': 'Purok not found'}), 404
        db.execute("UPDATE purok_data SET label=?, color=? WHERE key_name=?", (label, color, key_name))
        add_audit(db, '✏️', 'record', 'Purok Updated', f"{key_name} → {label}", data.get('by', 'Staff'))
        db.commit()
    return jsonify({'key_name': key_name, 'label': label, 'color': color})

@app.route('/api/purok/<key_name>', methods=['DELETE'])
def delete_purok(key_name):
    with get_db() as db:
        existing = db.execute("SELECT * FROM purok_data WHERE key_name=?", (key_name,)).fetchone()
        if not existing:
            return jsonify({'error': 'Purok not found'}), 404
        # Check if residents are still assigned
        count = db.execute("SELECT COUNT(*) FROM residents WHERE purok=?", (key_name,)).fetchone()[0]
        if count > 0:
            return jsonify({'error': f'Hindi mabura — may {count} residente pa sa purok na ito.'}), 409
        db.execute("DELETE FROM purok_data WHERE key_name=?", (key_name,))
        add_audit(db, '🗑️', 'record', 'Purok Deleted', key_name, 'Staff')
        db.commit()
    return jsonify({'deleted': key_name})


# ══════════════════════════════════════════
# PORTAL (Resident Self-Service)
# ══════════════════════════════════════════
@app.route('/api/portal/check', methods=['POST'])
def portal_check_request():
    """Residents can check their request status by code"""
    data = request.get_json()
    code = data.get('code','').strip().upper()
    with get_db() as db:
        r = db.execute("SELECT * FROM cert_requests WHERE UPPER(code)=?", (code,)).fetchone()
        if not r: return jsonify({'found': False}), 404
        return jsonify({'found': True, 'request': dict(r)})

@app.route('/api/portal/terms-agree', methods=['POST'])
def portal_terms_agree():
    """Log that resident agreed to T&C"""
    data = request.get_json()
    with get_db() as db:
        db.execute("INSERT INTO portal_terms_log (name,contact) VALUES (?,?)",
                   (data.get('name',''), data.get('contact','')))
        db.commit()
    return jsonify({'message': 'Recorded'}), 201


# ══════════════════════════════════════════
# FILE UPLOAD
# ══════════════════════════════════════════
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    f = request.files['file']
    if not f or not f.filename:
        return jsonify({'error': 'No file selected'}), 400
    if not allowed_file(f.filename):
        return jsonify({'error': 'File type not allowed. Use JPG, PNG, PDF, or GIF.'}), 400
    ext = f.filename.rsplit('.', 1)[1].lower()
    filename = gen_id() + '_' + secure_filename(f.filename)
    f.save(os.path.join(UPLOAD_FOLDER, filename))
    return jsonify({'filename': filename, 'url': f'/uploads/{filename}'}), 201

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# ══════════════════════════════════════════
# HEALTH
# ══════════════════════════════════════════
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status':'ok','system':'SmartBrgy API v2','barangay':'Anabu I-G, Imus City'})


if __name__ == '__main__':
    init_db()
    print("🚀 SmartBrgy API v2 running on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
