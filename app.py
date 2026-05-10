"""
SmartBrgy Backend API v2 — MySQL Edition
Barangay Anabu I-G, Imus City
Flask + MySQL (PyMySQL)
"""

from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import pymysql, pymysql.cursors
import os, uuid, json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# ─────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────
GMAIL_USER         = 'brgy.anabu.1g.imus@gmail.com'
GMAIL_APP_PASSWORD = 'kdxdkejttsgyzonp'
UPLOAD_FOLDER      = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTS       = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'heic', 'webp'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ─── MySQL Connection Settings ───────────
# I-lagay ang credentials ng iyong MySQL server dito
DB_CONFIG = {
    'host':        os.environ.get('DB_HOST', 'localhost'),
    'port':        int(os.environ.get('DB_PORT', 3306)),
    'user':        os.environ.get('DB_USER', 'root'),
    'password':    os.environ.get('DB_PASSWORD', ''),
    'database':    os.environ.get('DB_NAME', 'smartbrgy'),
    'charset':     'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
    'autocommit':  False,
}

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
        msg['To']   = to_email
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
    response.headers['Access-Control-Allow-Origin']  = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

@app.before_request
def handle_options():
    if request.method == 'OPTIONS':
        from flask import Response
        r = Response()
        r.headers['Access-Control-Allow-Origin']  = '*'
        r.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
        r.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        return r, 200

# ─────────────────────────────────────────
# DB HELPERS
# ─────────────────────────────────────────
def get_db():
    """Bumalik ng bagong MySQL connection."""
    conn = pymysql.connect(**DB_CONFIG)
    return conn

def calc_age(dob_str):
    try:
        dob   = datetime.strptime(dob_str, '%Y-%m-%d').date()
        today = date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    except:
        return 0

def add_audit(cursor, icon, category, action, detail, user='System'):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(
        "INSERT INTO audit_log (icon,category,action,detail,user,created_at) VALUES (%s,%s,%s,%s,%s,%s)",
        (icon, category, action, detail, user, now)
    )

def gen_id(prefix=''):
    return prefix + str(uuid.uuid4())[:8].upper()

# ─────────────────────────────────────────
# INIT DATABASE
# ─────────────────────────────────────────
def init_db():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS residents (
                id             VARCHAR(50)  PRIMARY KEY,
                name           VARCHAR(255) NOT NULL,
                purok          VARCHAR(100),
                dob            DATE,
                gender         VARCHAR(20),
                civil          VARCHAR(50),
                contact        VARCHAR(50),
                status         VARCHAR(30)  NOT NULL DEFAULT 'Active',
                household      VARCHAR(100),
                type           VARCHAR(50),
                address        TEXT,
                special_groups JSON,
                created_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
                               ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS resident_status (
                resident_id     VARCHAR(50) PRIMARY KEY,
                good_standing   TINYINT(1)  NOT NULL DEFAULT 1,
                blotter         TINYINT(1)  NOT NULL DEFAULT 0,
                blotter_details JSON,
                FOREIGN KEY (resident_id) REFERENCES residents(id)
                    ON DELETE CASCADE ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id          VARCHAR(50)  PRIMARY KEY,
                type        VARCHAR(100) NOT NULL,
                location    VARCHAR(255),
                date        DATE,
                reported_by VARCHAR(255),
                complainee  VARCHAR(255),
                status      VARCHAR(50)  NOT NULL DEFAULT 'Pending',
                severity    VARCHAR(30)  NOT NULL DEFAULT 'Medium',
                description TEXT,
                attachments JSON,
                created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS cert_requests (
                code        VARCHAR(50)  PRIMARY KEY,
                resident_id VARCHAR(50),
                name        VARCHAR(255) NOT NULL,
                type        VARCHAR(100) NOT NULL,
                cert_id     VARCHAR(50),
                purpose     TEXT,
                address     TEXT,
                contact     VARCHAR(50),
                email       VARCHAR(255),
                dob         DATE,
                status      VARCHAR(50)  NOT NULL DEFAULT 'Processing',
                via         VARCHAR(50)  NOT NULL DEFAULT 'Online',
                source      VARCHAR(50)  NOT NULL DEFAULT 'portal',
                attachment  TEXT,
                hidden      TINYINT(1)   NOT NULL DEFAULT 0,
                requested   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resident_id) REFERENCES residents(id)
                    ON DELETE SET NULL ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS rfid_tags (
                id        VARCHAR(50)  PRIMARY KEY,
                name      VARCHAR(255) NOT NULL,
                location  VARCHAR(255),
                type      VARCHAR(100),
                status    VARCHAR(50)  NOT NULL DEFAULT 'In Cabinet',
                last_scan DATETIME
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS cabinet_folders (
                id     VARCHAR(50)  PRIMARY KEY,
                name   VARCHAR(255) NOT NULL,
                rfid   VARCHAR(50),
                drawer VARCHAR(100),
                status VARCHAR(50)  NOT NULL DEFAULT 'In Cabinet',
                FOREIGN KEY (rfid) REFERENCES rfid_tags(id)
                    ON DELETE SET NULL ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS cabinet_log (
                id           INT          PRIMARY KEY AUTO_INCREMENT,
                drawer_id    VARCHAR(50),
                drawer_label VARCHAR(255),
                action       VARCHAR(255),
                user         VARCHAR(255),
                created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id         VARCHAR(50)  PRIMARY KEY,
                name       VARCHAR(255) NOT NULL,
                role       VARCHAR(100),
                access     VARCHAR(100) NOT NULL DEFAULT 'View Only',
                username   VARCHAR(100) UNIQUE,
                password   VARCHAR(255),
                face       TINYINT(1)   NOT NULL DEFAULT 0,
                rfid       TINYINT(1)   NOT NULL DEFAULT 0,
                status     VARCHAR(30)  NOT NULL DEFAULT 'Active',
                last_login DATETIME,
                created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id         INT          PRIMARY KEY AUTO_INCREMENT,
                icon       VARCHAR(100),
                category   VARCHAR(100),
                action     VARCHAR(500) NOT NULL,
                detail     TEXT,
                user       VARCHAR(255),
                created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS purok_data (
                key_name VARCHAR(100) PRIMARY KEY,
                label    VARCHAR(255),
                total    INT          NOT NULL DEFAULT 0,
                color    VARCHAR(50),
                pct      INT          NOT NULL DEFAULT 0
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS portal_terms_log (
                id        INT          PRIMARY KEY AUTO_INCREMENT,
                name      VARCHAR(255),
                contact   VARCHAR(50),
                ip        VARCHAR(45),
                agreed_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # Seed super admin
            cur.execute("""
                INSERT IGNORE INTO users
                    (id,name,role,access,username,password,face,rfid,status,last_login)
                VALUES
                    ('USR-001','Juan dela Cruz','Super Administrator','Full Access',
                     'admin','Admin@1234!',1,1,'Active',NULL)
            """)

            # Safe column migrations — add missing columns to existing tables
            cur.execute("""
                SELECT COUNT(*) AS cnt FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME   = 'cert_requests'
                  AND COLUMN_NAME  = 'attachment'
            """)
            if cur.fetchone()['cnt'] == 0:
                cur.execute("ALTER TABLE cert_requests ADD COLUMN attachment TEXT")

            cur.execute("""
                SELECT COUNT(*) AS cnt FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME   = 'cert_requests'
                  AND COLUMN_NAME  = 'dob'
            """)
            if cur.fetchone()['cnt'] == 0:
                cur.execute("ALTER TABLE cert_requests ADD COLUMN dob DATE")

            conn.commit()
    finally:
        conn.close()
    print("✅ Database initialized (MySQL)")


# ══════════════════════════════════════════
# RESIDENTS
# ══════════════════════════════════════════
@app.route('/api/residents', methods=['GET'])
def get_residents():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT r.*, rs.good_standing, rs.blotter, rs.blotter_details
                FROM residents r
                LEFT JOIN resident_status rs ON r.id = rs.resident_id
                ORDER BY r.name
            """)
            rows = cur.fetchall()
        result = []
        for r in rows:
            r['age'] = calc_age(str(r.get('dob') or ''))
            bd = r.get('blotter_details')
            r['blotter_details'] = json.loads(bd) if isinstance(bd, str) else (bd or [])
            # Serialize dates
            for k in ('dob', 'created_at', 'updated_at'):
                if isinstance(r.get(k), (datetime, date)):
                    r[k] = str(r[k])
            result.append(r)
        return jsonify(result)
    finally:
        conn.close()

@app.route('/api/residents/<rid>', methods=['GET'])
def get_resident(rid):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT r.*, rs.good_standing, rs.blotter, rs.blotter_details
                FROM residents r
                LEFT JOIN resident_status rs ON r.id = rs.resident_id
                WHERE r.id = %s
            """, (rid,))
            r = cur.fetchone()
        if not r:
            return jsonify({'error': 'Not found'}), 404
        r['age'] = calc_age(str(r.get('dob') or ''))
        bd = r.get('blotter_details')
        r['blotter_details'] = json.loads(bd) if isinstance(bd, str) else (bd or [])
        for k in ('dob', 'created_at', 'updated_at'):
            if isinstance(r.get(k), (datetime, date)):
                r[k] = str(r[k])
        return jsonify(r)
    finally:
        conn.close()

@app.route('/api/residents', methods=['POST'])
def add_resident():
    data = request.get_json()
    new_id = 'ANB-' + gen_id()
    special_groups = json.dumps(data.get('specialGroups') or [])
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO residents
                    (id,name,purok,dob,gender,civil,contact,status,household,type,address,special_groups)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (new_id, data['name'], data.get('purok',''), data.get('dob') or None,
                  data.get('gender',''), data.get('civil',''), data.get('contact',''),
                  data.get('status','Active'), data.get('household',''),
                  data.get('type',''), data.get('address',''), special_groups))
            cur.execute("""
                INSERT IGNORE INTO resident_status (resident_id,good_standing,blotter,blotter_details)
                VALUES (%s,1,0,%s)
            """, (new_id, json.dumps([])))
            add_audit(cur, '🧑', 'record', 'New Resident Registered',
                      f"{data['name']} — {new_id}", data.get('by','Staff'))
            conn.commit()
    finally:
        conn.close()
    return jsonify({'id': new_id, 'message': 'Resident added'}), 201

@app.route('/api/residents/<rid>', methods=['PUT'])
def update_resident(rid):
    data = request.get_json()
    special_groups = json.dumps(data.get('specialGroups') or [])
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE residents
                SET name=%s,purok=%s,dob=%s,gender=%s,civil=%s,contact=%s,
                    status=%s,household=%s,type=%s,address=%s,special_groups=%s
                WHERE id=%s
            """, (data['name'], data.get('purok'), data.get('dob') or None,
                  data.get('gender'), data.get('civil'), data.get('contact'),
                  data.get('status','Active'), data.get('household'),
                  data.get('type'), data.get('address',''), special_groups, rid))
            add_audit(cur, '✏️', 'record', 'Resident Record Updated',
                      f"{data['name']} — {rid}", data.get('by','Staff'))
            conn.commit()
    finally:
        conn.close()
    return jsonify({'message': 'Updated'})

@app.route('/api/residents/<rid>', methods=['DELETE'])
def delete_resident(rid):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM residents WHERE id=%s", (rid,))
            r = cur.fetchone()
            if not r:
                return jsonify({'error': 'Not found'}), 404
            cur.execute("DELETE FROM resident_status WHERE resident_id=%s", (rid,))
            cur.execute("DELETE FROM residents WHERE id=%s", (rid,))
            add_audit(cur, '🗑️', 'record', 'Resident Deleted',
                      f"{r['name']} — {rid}", 'Staff')
            conn.commit()
    finally:
        conn.close()
    return jsonify({'message': 'Deleted'})

@app.route('/api/residents/<rid>/status', methods=['PUT'])
def update_resident_status(rid):
    data = request.get_json()
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO resident_status (resident_id,good_standing,blotter,blotter_details)
                VALUES (%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                    good_standing=VALUES(good_standing),
                    blotter=VALUES(blotter),
                    blotter_details=VALUES(blotter_details)
            """, (rid,
                  1 if data.get('good_standing', True) else 0,
                  1 if data.get('blotter', False) else 0,
                  json.dumps(data.get('blotter_details', []))))
            add_audit(cur, '📋', 'record', 'Resident Status Updated', rid, data.get('by','Staff'))
            conn.commit()
    finally:
        conn.close()
    return jsonify({'message': 'Status updated'})


# ══════════════════════════════════════════
# CERT REQUESTS
# ══════════════════════════════════════════
@app.route('/api/cert-requests', methods=['GET'])
def get_cert_requests():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM cert_requests ORDER BY requested DESC")
            rows = cur.fetchall()
        for r in rows:
            for k in ('requested', 'dob'):
                if isinstance(r.get(k), (datetime, date)):
                    r[k] = str(r[k])
        return jsonify(rows)
    finally:
        conn.close()

@app.route('/api/cert-requests', methods=['POST'])
def submit_cert_request():
    data   = request.get_json()
    year   = datetime.now().strftime('%Y')
    conn   = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) AS cnt FROM cert_requests WHERE requested LIKE %s",
                (f'{year}%',)
            )
            count = cur.fetchone()['cnt']
            code  = f"REQ-{year}-{str(count+1).zfill(4)}"
            dob   = data.get('dob') or None
            cur.execute("""
                INSERT INTO cert_requests
                    (code,resident_id,name,type,cert_id,purpose,address,
                     contact,email,dob,status,via,source,attachment)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (code, data.get('resident_id') or None, data['name'], data['type'],
                  data.get('cert_id',''), data.get('purpose',''), data.get('address',''),
                  data.get('contact',''), data.get('email',''), dob,
                  'Processing', data.get('via','Online'), data.get('source','portal'),
                  data.get('attachment','')))
            add_audit(cur, '📨', 'cert', 'Certificate Request Submitted',
                      f"{code} — {data['name']} — {data['type']}", data.get('via','Portal'))
            conn.commit()
    finally:
        conn.close()
    if data.get('email'):
        send_email(data['email'])
    return jsonify({'code': code, 'message': 'Request submitted'}), 201

@app.route('/api/cert-requests/<code>/status', methods=['PUT'])
def update_cert_status(code):
    data = request.get_json()
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM cert_requests WHERE code=%s", (code,))
            r = cur.fetchone()
            if not r:
                return jsonify({'error': 'Not found'}), 404
            cur.execute("UPDATE cert_requests SET status=%s WHERE code=%s",
                        (data['status'], code))
            add_audit(cur, '📋', 'cert', f"Certificate Status → {data['status']}",
                      f"{code} — {r['name']}", data.get('user','Staff'))
            conn.commit()
    finally:
        conn.close()
    return jsonify({'message': 'Updated'})

@app.route('/api/cert-requests/<code>', methods=['DELETE'])
def delete_cert_request(code):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM cert_requests WHERE code=%s", (code,))
            conn.commit()
    finally:
        conn.close()
    return jsonify({'message': 'Deleted'})

@app.route('/api/cert-requests/<code>/hide', methods=['PUT'])
def hide_cert_request(code):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE cert_requests SET hidden=1 WHERE code=%s", (code,))
            conn.commit()
    finally:
        conn.close()
    return jsonify({'message': 'Hidden'})


# ══════════════════════════════════════════
# INCIDENTS
# ══════════════════════════════════════════
@app.route('/api/incidents', methods=['GET'])
def get_incidents():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM incidents ORDER BY created_at DESC")
            rows = cur.fetchall()
        for r in rows:
            for k in ('date', 'created_at'):
                if isinstance(r.get(k), (datetime, date)):
                    r[k] = str(r[k])
            att = r.get('attachments')
            if isinstance(att, list):
                pass
            elif isinstance(att, str):
                try:
                    parsed = json.loads(att)
                    if isinstance(parsed, list):
                        att = parsed
                    elif isinstance(parsed, str):
                        try:
                            parsed2 = json.loads(parsed)
                            att = parsed2 if isinstance(parsed2, list) else []
                        except Exception:
                            att = []
                    else:
                        att = []
                except Exception:
                    att = []
            else:
                att = []
            r['attachments'] = att
        return jsonify(rows)
    finally:
        conn.close()

@app.route('/api/incidents', methods=['POST'])
def add_incident():
    data = request.get_json()
    year = datetime.now().strftime('%Y')
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) AS cnt FROM incidents WHERE id LIKE %s",
                (f'INC-{year}%',)
            )
            count  = cur.fetchone()['cnt']
            new_id = f"INC-{year}-{str(count+1).zfill(3)}"
            inc_date = data.get('date') or None
            att = data.get('attachments') or []
            if isinstance(att, str):
                try: att = json.loads(att)
                except: att = []
            attachments = json.dumps(att)
            cur.execute("""
                INSERT INTO incidents
                    (id,type,location,date,reported_by,complainee,
                     status,severity,description,attachments)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (new_id, data['type'], data.get('location',''), inc_date,
                  data.get('reported_by','Anonymous'), data.get('complainee',''),
                  'Pending', data.get('severity','Medium'),
                  data.get('description',''), attachments))
            add_audit(cur, '🚨', 'incident', 'Incident Report Filed',
                      f"{new_id} — {data['type']}", data.get('reported_by','Staff'))
            conn.commit()
    finally:
        conn.close()
    return jsonify({'id': new_id, 'message': 'Incident filed'}), 201

@app.route('/api/incidents/<iid>', methods=['DELETE'])
def delete_incident(iid):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT type FROM incidents WHERE id=%s", (iid,))
            row = cur.fetchone()
            if not row:
                return jsonify({'error': 'Not found'}), 404
            cur.execute("DELETE FROM incidents WHERE id=%s", (iid,))
            add_audit(cur, '🗑️', 'incident', 'Incident Report Deleted', iid, 'Staff')
            conn.commit()
    finally:
        conn.close()
    return jsonify({'message': 'Deleted'})

@app.route('/api/incidents/<iid>/status', methods=['PUT'])
def update_incident_status(iid):
    data = request.get_json()
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE incidents SET status=%s WHERE id=%s",
                        (data['status'], iid))
            add_audit(cur, '🔄', 'incident', f"Incident → {data['status']}",
                      iid, data.get('user','Staff'))
            conn.commit()
    finally:
        conn.close()
    return jsonify({'message': 'Updated'})

@app.route('/api/incidents/<iid>', methods=['PUT'])
def update_incident(iid):
    data = request.get_json() or {}
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM incidents WHERE id=%s", (iid,))
            row = cur.fetchone()
            if not row:
                return jsonify({'error': 'Incident not found'}), 404
            att = data.get('attachments', row.get('attachments') or [])
            if isinstance(att, str):
                try: att = json.loads(att)
                except: att = []
            attachments = json.dumps(att if isinstance(att, list) else [])
            cur.execute("""
                UPDATE incidents
                SET type=%s,location=%s,date=%s,reported_by=%s,
                    complainee=%s,status=%s,severity=%s,description=%s,attachments=%s
                WHERE id=%s
            """, (
                data.get('type',        row['type']),
                data.get('location',    row['location']),
                data.get('date',        row['date']),
                data.get('reported_by', row['reported_by']),
                data.get('complainee',  row.get('complainee','')),
                data.get('status',      row['status']),
                data.get('severity',    row['severity']),
                data.get('description', row['description']),
                attachments,
                iid
            ))
            add_audit(cur, '✏️', 'incident', 'Incident Report Updated',
                      iid, data.get('user','Staff'))
            conn.commit()
    finally:
        conn.close()
    return jsonify({'message': 'Incident updated', 'id': iid})


# ══════════════════════════════════════════
# RFID TAGS
# ══════════════════════════════════════════
@app.route('/api/rfid', methods=['GET'])
def get_rfid():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM rfid_tags")
            rows = cur.fetchall()
        for r in rows:
            if isinstance(r.get('last_scan'), datetime):
                r['last_scan'] = str(r['last_scan'])
        return jsonify(rows)
    finally:
        conn.close()

@app.route('/api/rfid/<tag_id>/scan', methods=['POST'])
def scan_rfid(tag_id):
    data       = request.get_json()
    new_status = data.get('status','In Cabinet')
    now        = datetime.now().isoformat()
    conn       = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM rfid_tags WHERE id=%s", (tag_id,))
            tag = cur.fetchone()
            if not tag:
                return jsonify({'error': 'Not found'}), 404
            cur.execute("UPDATE rfid_tags SET status=%s,last_scan=%s WHERE id=%s",
                        (new_status, now, tag_id))
            add_audit(cur, '📡', 'rfid', f'RFID Scan — {new_status}',
                      f"{tag_id} — {tag['name']}", 'RFID Reader')
            conn.commit()
    finally:
        conn.close()
    return jsonify({'message': 'Updated', 'last_scan': now})


# ══════════════════════════════════════════
# CABINET FOLDERS
# ══════════════════════════════════════════
@app.route('/api/cabinet/folders', methods=['GET'])
def get_cabinet_folders():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM cabinet_folders")
            return jsonify(cur.fetchall())
    finally:
        conn.close()

@app.route('/api/cabinet/folders/<fid>/status', methods=['PUT'])
def update_folder_status(fid):
    data = request.get_json()
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM cabinet_folders WHERE id=%s", (fid,))
            f = cur.fetchone()
            if not f:
                return jsonify({'error': 'Not found'}), 404
            cur.execute("UPDATE cabinet_folders SET status=%s WHERE id=%s",
                        (data['status'], fid))
            add_audit(cur, '📁', 'rfid', f"Folder {data['status']}",
                      f"{fid} — {f['name']}", data.get('user','Staff'))
            conn.commit()
    finally:
        conn.close()
    return jsonify({'message': 'Updated'})

@app.route('/api/cabinet/log', methods=['GET'])
def get_cabinet_log():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM cabinet_log ORDER BY created_at DESC LIMIT 50")
            rows = cur.fetchall()
        for r in rows:
            if isinstance(r.get('created_at'), datetime):
                r['created_at'] = str(r['created_at'])
        return jsonify(rows)
    finally:
        conn.close()

@app.route('/api/cabinet/log', methods=['POST'])
def add_cabinet_log():
    data = request.get_json()
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO cabinet_log (drawer_id,drawer_label,action,user)
                VALUES (%s,%s,%s,%s)
            """, (data.get('drawer_id',''), data.get('drawer_label',''),
                  data.get('action',''), data.get('user','Staff')))
            conn.commit()
    finally:
        conn.close()
    return jsonify({'message': 'Logged'}), 201


# ══════════════════════════════════════════
# USERS
# ══════════════════════════════════════════
@app.route('/api/users', methods=['GET'])
def get_users():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id,name,role,access,username,password,face,rfid,
                       status,last_login,created_at
                FROM users ORDER BY created_at
            """)
            rows = cur.fetchall()
        for r in rows:
            for k in ('last_login','created_at'):
                if isinstance(r.get(k), datetime):
                    r[k] = str(r[k])
        return jsonify(rows)
    finally:
        conn.close()

@app.route('/api/users/login', methods=['POST', 'OPTIONS'])
def login_user():
    if request.method == 'OPTIONS':
        return '', 200
    data = request.get_json()
    username = data.get('username','').strip()
    password = data.get('password','')
    conn     = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id,name,role,access,username,face,rfid,status
                FROM users
                WHERE username=%s AND status='Active'
            """, (username,))
            user = cur.fetchone()
            if not user:
                # Try name-based username
                cur.execute("""
                    SELECT id,name,role,access,username,face,rfid,status
                    FROM users
                    WHERE LOWER(REPLACE(name,' ','.'))=%s
                      AND status='Active'
                """, (username.lower(),))
                user = cur.fetchone()
            if not user or not check_password_hash(user['password'], password):
                return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
            cur.execute("UPDATE users SET last_login=NOW() WHERE id=%s", (user['id'],))
            add_audit(cur, '🔐', 'auth', 'Login Successful',
                      f"{user['name']} — {user['role']}", user['name'])
            conn.commit()
        return jsonify({'success': True, 'user': user})
    finally:
        conn.close()

@app.route('/api/users', methods=['POST'])
def add_user():
    data = request.get_json()
    name = data.get('name','').strip()
    if not name:
        return jsonify({'error': 'Name required'}), 400
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM users")
            count  = cur.fetchone()['cnt']
            new_id = f"USR-{str(count+1).zfill(3)}"
            cur.execute("SELECT id FROM users WHERE id=%s", (new_id,))
            if cur.fetchone():
                new_id = 'USR-' + gen_id()
            cur.execute("""
                INSERT INTO users (id,name,role,access,username,password,face,rfid,status)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (new_id, name, data.get('role','Barangay Clerk'),
                  data.get('access','View Only'), data.get('username',''),
                  generate_password_hash(data.get('password','')),
                  1 if data.get('face') else 0,
                  1 if data.get('rfid') else 0, 'Active'))
            add_audit(cur, '👤', 'auth', 'New User Created',
                      f"{name} — {data.get('role')} — {new_id}", 'Admin')
            conn.commit()
    finally:
        conn.close()
    return jsonify({'id': new_id, 'message': 'User created'}), 201

@app.route('/api/users/<uid>', methods=['PUT'])
def update_user(uid):
    data = request.get_json()
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE users
                SET name=%s,role=%s,access=%s,username=%s,
                    face=%s,rfid=%s,status=%s
                WHERE id=%s
            """, (data['name'], data.get('role'), data.get('access'),
                  data.get('username'),
                  1 if data.get('face') else 0,
                  1 if data.get('rfid') else 0,
                  data.get('status','Active'), uid))
            add_audit(cur, '✏️', 'auth', 'User Updated',
                      f"{data['name']} — {uid}", 'Admin')
            conn.commit()
    finally:
        conn.close()
    return jsonify({'message': 'Updated'})

@app.route('/api/users/<uid>/suspend', methods=['PUT'])
def suspend_user(uid):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM users WHERE id=%s", (uid,))
            u = cur.fetchone()
            if not u:
                return jsonify({'error': 'Not found'}), 404
            cur.execute("UPDATE users SET status='Suspended' WHERE id=%s", (uid,))
            add_audit(cur, '🚫', 'security', 'User Suspended',
                      f"{u['name']} — {uid}", 'Admin')
            conn.commit()
    finally:
        conn.close()
    return jsonify({'message': 'Suspended'})

@app.route('/api/users/<uid>/activate', methods=['PUT'])
def activate_user(uid):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM users WHERE id=%s", (uid,))
            u = cur.fetchone()
            if not u:
                return jsonify({'error': 'Not found'}), 404
            cur.execute("UPDATE users SET status='Active' WHERE id=%s", (uid,))
            add_audit(cur, '✅', 'auth', 'User Activated',
                      f"{u['name']} — {uid}", 'Admin')
            conn.commit()
    finally:
        conn.close()
    return jsonify({'message': 'Activated'})


# ══════════════════════════════════════════
# AUDIT LOG
# ══════════════════════════════════════════
@app.route('/api/audit', methods=['GET'])
def get_audit():
    limit = int(request.args.get('limit', 100))
    conn  = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM audit_log ORDER BY created_at DESC LIMIT %s",
                (limit,)
            )
            rows = cur.fetchall()
        for r in rows:
            if isinstance(r.get('created_at'), datetime):
                r['created_at'] = str(r['created_at'])
        return jsonify(rows)
    finally:
        conn.close()

@app.route('/api/audit', methods=['POST'])
def post_audit():
    data = request.get_json()
    conn = get_db()
    try:
        with conn.cursor() as cur:
            add_audit(cur, data.get('icon','📌'), data.get('category','general'),
                      data['action'], data.get('detail',''), data.get('user','Staff'))
            conn.commit()
    finally:
        conn.close()
    return jsonify({'message': 'Logged'}), 201


# ══════════════════════════════════════════
# ELIGIBILITY CHECK
# ══════════════════════════════════════════
@app.route('/api/eligibility', methods=['POST'])
def check_eligibility():
    data        = request.get_json()
    resident_id = data.get('resident_id')
    cert_id     = data.get('cert_id')
    RULES = {
        'BC':   {'label':'Barangay Clearance',         'requiresActive':True,'needsGoodStanding':True, 'oneTimeOnly':False},
        'CR':   {'label':'Certificate of Residency',   'requiresActive':True,'needsGoodStanding':False,'oneTimeOnly':False},
        'CI':   {'label':'Certificate of Indigency',   'requiresActive':True,'needsGoodStanding':False,'oneTimeOnly':False},
        'BID':  {'label':'Barangay ID',                'requiresActive':True,'needsGoodStanding':False,'oneTimeOnly':False},
        'CTFJ': {'label':'First Time Jobseeker',       'requiresActive':True,'needsGoodStanding':False,'oneTimeOnly':True},
        'BBC':  {'label':'Business Clearance',         'requiresActive':True,'needsGoodStanding':True, 'oneTimeOnly':False},
    }
    rule = RULES.get(cert_id)
    if not rule:
        return jsonify({'eligible':False,'reasons':['Unknown document type.']}), 400
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM residents WHERE id=%s", (resident_id,))
            resident = cur.fetchone()
            cur.execute("SELECT * FROM resident_status WHERE resident_id=%s", (resident_id,))
            rs = cur.fetchone()
            if not resident:
                return jsonify({'eligible':False,'reasons':['Resident not found.']}), 404
            eligible = True
            reasons  = []
            if rule['requiresActive'] and resident['status'] != 'Active':
                eligible = False
                reasons.append('❌ Hindi aktibo ang residente.')
            if rule['needsGoodStanding']:
                # Check blotter flag
                if rs and rs.get('blotter'):
                    eligible = False
                    bd = rs.get('blotter_details')
                    bl = json.loads(bd) if isinstance(bd, str) else (bd or [])
                    reasons.append('❌ Naka-blotter ang residente: ' + (', '.join(bl) if bl else 'Tingnan sa records'))
                # Check good_standing flag
                if rs and not rs['good_standing']:
                    eligible = False
                    reasons.append('❌ Hindi nasa mabuting kalagayan ang residente.')
                # Check incident reports — resident named as complainee
                cur.execute(
                    "SELECT id, type, date FROM incidents WHERE LOWER(TRIM(complainee)) = LOWER(TRIM(%s))",
                    (resident['name'],)
                )
                inc_rows = cur.fetchall()
                if inc_rows:
                    eligible = False
                    inc_list = ', '.join(
                        f"{i['type']} — {str(i['date'])} ({i['id']})" for i in inc_rows
                    )
                    reasons.append(f"❌ Nakasangkot sa {len(inc_rows)} incident report bilang ine-reklamo: {inc_list}")
            if rule['oneTimeOnly']:
                cur.execute("""
                    SELECT code FROM cert_requests
                    WHERE cert_id=%s AND status='Completed'
                    AND (resident_id=%s OR (resident_id IS NULL AND LOWER(TRIM(name))=LOWER(TRIM(%s))))
                """, (cert_id, resident_id, resident['name']))
                prev = cur.fetchone()
                if prev:
                    eligible = False
                    reasons.append(f"❌ One-time only. Nakuha na noong code: {prev['code']}")
            if eligible:
                if rs and rs['good_standing']:
                    reasons.append('✅ Nasa mabuting kalagayan.')
                if resident['status'] == 'Active':
                    reasons.append('✅ Active na residente.')
            for k in ('dob','created_at','updated_at'):
                if isinstance(resident.get(k), (datetime, date)):
                    resident[k] = str(resident[k])
            return jsonify({'eligible':eligible,'reasons':reasons,
                            'resident':resident,'rule':rule})
    finally:
        conn.close()


# ══════════════════════════════════════════
# DASHBOARD STATS
# ══════════════════════════════════════════
@app.route('/api/dashboard/stats', methods=['GET'])
def dashboard_stats():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            def scalar(q, *args):
                cur.execute(q, args)
                row = cur.fetchone()
                return list(row.values())[0]

            total         = scalar("SELECT COUNT(*) FROM residents WHERE status='Active'")
            pending_req   = scalar("SELECT COUNT(*) FROM cert_requests WHERE status='Processing'")
            ready_req     = scalar("SELECT COUNT(*) FROM cert_requests WHERE status='Ready to Print'")
            total_req     = scalar("SELECT COUNT(*) FROM cert_requests")
            completed_req = scalar("SELECT COUNT(*) FROM cert_requests WHERE status='Completed'")
            pending_inc   = scalar("SELECT COUNT(*) FROM incidents WHERE status='Pending'")
            total_inc     = scalar("SELECT COUNT(*) FROM incidents")
            portal_req    = scalar("SELECT COUNT(*) FROM cert_requests WHERE source='portal'")

            cur.execute("SELECT dob FROM residents WHERE status='Active'")
            dobs    = cur.fetchall()
            seniors = sum(1 for r in dobs if calc_age(str(r.get('dob') or '')) >= 60)

        return jsonify({
            'total_residents':   total,
            'pending_requests':  pending_req,
            'ready_requests':    ready_req,
            'total_requests':    total_req,
            'completed_requests':completed_req,
            'pending_incidents': pending_inc,
            'total_incidents':   total_inc,
            'senior_count':      seniors,
            'portal_requests':   portal_req,
        })
    finally:
        conn.close()


# ══════════════════════════════════════════
# PUROK
# ══════════════════════════════════════════
@app.route('/api/purok', methods=['GET', 'POST'])
def get_purok():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            if request.method == 'POST':
                data     = request.get_json() or {}
                key_name = (data.get('key_name') or data.get('key') or '').strip()
                label    = (data.get('label') or key_name).strip()
                color    = (data.get('color') or 'var(--green-500)').strip()
                total    = int(data.get('total') or 0)
                pct      = int(data.get('pct') or 0)
                if not key_name:
                    return jsonify({'error': 'Purok name is required'}), 400
                cur.execute("SELECT key_name FROM purok_data WHERE LOWER(key_name)=LOWER(%s)", (key_name,))
                if cur.fetchone():
                    return jsonify({'error': 'Purok already exists'}), 409
                cur.execute(
                    "INSERT INTO purok_data (key_name,label,total,color,pct) VALUES (%s,%s,%s,%s,%s)",
                    (key_name, label, total, color, pct)
                )
                add_audit(cur, 'zone', 'record', 'Purok Added', key_name, data.get('by','Staff'))
                conn.commit()
                return jsonify({'key_name':key_name,'label':label,'total':total,'color':color,'pct':pct}), 201
            cur.execute("SELECT * FROM purok_data")
            return jsonify(cur.fetchall())
    finally:
        conn.close()

@app.route('/api/purok/<key_name>', methods=['PUT'])
def update_purok(key_name):
    data  = request.get_json() or {}
    label = data.get('label', key_name).strip()
    color = data.get('color', 'var(--green-500)').strip()
    conn  = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM purok_data WHERE key_name=%s", (key_name,))
            if not cur.fetchone():
                return jsonify({'error': 'Purok not found'}), 404
            cur.execute("UPDATE purok_data SET label=%s,color=%s WHERE key_name=%s",
                        (label, color, key_name))
            add_audit(cur, '✏️', 'record', 'Purok Updated',
                      f"{key_name} → {label}", data.get('by','Staff'))
            conn.commit()
    finally:
        conn.close()
    return jsonify({'key_name':key_name,'label':label,'color':color})

@app.route('/api/purok/<key_name>', methods=['DELETE'])
def delete_purok(key_name):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM purok_data WHERE key_name=%s", (key_name,))
            if not cur.fetchone():
                return jsonify({'error': 'Purok not found'}), 404
            cur.execute("SELECT COUNT(*) AS cnt FROM residents WHERE purok=%s", (key_name,))
            count = cur.fetchone()['cnt']
            if count > 0:
                return jsonify({'error': f'Hindi mabura — may {count} residente pa sa purok na ito.'}), 409
            cur.execute("DELETE FROM purok_data WHERE key_name=%s", (key_name,))
            add_audit(cur, '🗑️', 'record', 'Purok Deleted', key_name, 'Staff')
            conn.commit()
    finally:
        conn.close()
    return jsonify({'deleted': key_name})


# ══════════════════════════════════════════
# PORTAL
# ══════════════════════════════════════════
@app.route('/api/portal/check', methods=['POST'])
def portal_check_request():
    data = request.get_json()
    code = data.get('code','').strip().upper()
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM cert_requests WHERE UPPER(code)=%s", (code,))
            r = cur.fetchone()
        if not r:
            return jsonify({'found': False}), 404
        for k in ('requested','dob'):
            if isinstance(r.get(k), (datetime, date)):
                r[k] = str(r[k])
        return jsonify({'found': True, 'request': r})
    finally:
        conn.close()

@app.route('/api/portal/terms-agree', methods=['POST'])
def portal_terms_agree():
    data = request.get_json()
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO portal_terms_log (name,contact) VALUES (%s,%s)",
                (data.get('name',''), data.get('contact',''))
            )
            conn.commit()
    finally:
        conn.close()
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
    ext      = f.filename.rsplit('.', 1)[1].lower()
    filename = gen_id() + '_' + secure_filename(f.filename)
    f.save(os.path.join(UPLOAD_FOLDER, filename))
    return jsonify({'filename': filename, 'url': f'/uploads/{filename}'}), 201

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# ══════════════════════════════════════════
# STATIC FILES (HTML, JS, CSS)
# ══════════════════════════════════════════
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
@app.route('/index.html')
def serve_index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/portal')
@app.route('/portal.html')
def serve_portal():
    return send_from_directory(BASE_DIR, 'portal.html')

@app.route('/script.js')
def serve_script():
    return send_from_directory(BASE_DIR, 'script.js')

@app.route('/db-connector.js')
def serve_db_connector():
    return send_from_directory(BASE_DIR, 'db-connector.js')

@app.route('/style.css')
def serve_style():
    return send_from_directory(BASE_DIR, 'style.css')


# ══════════════════════════════════════════
# HEALTH
# ══════════════════════════════════════════
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status':'ok','system':'SmartBrgy API v2 (MySQL)','barangay':'Anabu I-G, Imus City'})


if __name__ == '__main__':
    init_db()
    print("🚀 SmartBrgy API v2 (MySQL) running on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
