-- 訂正依頼システム - データベーススキーマ v1.4.0
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- 生徒情報テーブル
CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    class_number TEXT NOT NULL,
    student_number TEXT,
    name TEXT NOT NULL,
    name_kana TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, class_number, student_number)
);

CREATE INDEX IF NOT EXISTS idx_students_year_class ON students(year, class_number);
CREATE INDEX IF NOT EXISTS idx_students_name ON students(name);

-- 講座情報テーブル
CREATE TABLE IF NOT EXISTS courses (
    course_id TEXT PRIMARY KEY,
    course_name TEXT NOT NULL,
    teacher_name TEXT,
    year INTEGER NOT NULL,
    semester TEXT,
    subject_code TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_courses_year ON courses(year);
CREATE INDEX IF NOT EXISTS idx_courses_name ON courses(course_name);

-- 訂正依頼テーブル（statusカラム削除）
CREATE TABLE IF NOT EXISTS correction_requests (
    correction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_type TEXT NOT NULL CHECK(request_type IN ('出欠訂正', '評価評定変更')),
    student_id INTEGER NOT NULL,
    course_id TEXT NOT NULL,
    target_date TEXT,
    semester TEXT,
    periods TEXT,
    before_value TEXT,
    after_value TEXT,
    reason TEXT NOT NULL,
    requester_name TEXT NOT NULL,
    requester_pc TEXT NOT NULL,
    request_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_locked BOOLEAN DEFAULT 0,
    locked_by TEXT,
    locked_datetime TIMESTAMP,
    is_deleted BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

CREATE INDEX IF NOT EXISTS idx_corrections_student ON correction_requests(student_id);
CREATE INDEX IF NOT EXISTS idx_corrections_course ON correction_requests(course_id);
CREATE INDEX IF NOT EXISTS idx_corrections_locked ON correction_requests(is_locked);
CREATE INDEX IF NOT EXISTS idx_corrections_date ON correction_requests(target_date);
CREATE INDEX IF NOT EXISTS idx_corrections_requester ON correction_requests(requester_name);
CREATE INDEX IF NOT EXISTS idx_corrections_deleted ON correction_requests(is_deleted);

-- 操作ログテーブル
CREATE TABLE IF NOT EXISTS operation_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    pc_name TEXT NOT NULL,
    operation_type TEXT NOT NULL,
    target_table TEXT NOT NULL,
    target_record_id INTEGER,
    before_data TEXT,
    after_data TEXT,
    operation_detail TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON operation_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_logs_username ON operation_logs(username);
CREATE INDEX IF NOT EXISTS idx_logs_operation ON operation_logs(operation_type);
CREATE INDEX IF NOT EXISTS idx_logs_target ON operation_logs(target_table, target_record_id);

-- システム設定テーブル
CREATE TABLE IF NOT EXISTS system_settings (
    setting_key TEXT PRIMARY KEY,
    setting_value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO system_settings (setting_key, setting_value) VALUES
('admin_password_hash', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'),
('app_title', '訂正依頼システム'),
('notice_message', '成績の訂正の場合は、教務に報告してからこちらの訂正依頼を申請してください。訂正依頼後は、成績入力シートなどのデータも忘れずに修正しておいてください。'),
('app_version', '1.4.0'),
('db_version', '1.4');
