-- 訂正依頼システム データベーススキーマ
-- SQLite 3.x

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

-- 講座情報テーブル
CREATE TABLE IF NOT EXISTS courses (
    course_id TEXT PRIMARY KEY,
    course_name TEXT NOT NULL,
    teacher_name TEXT,
    year INTEGER NOT NULL,
    semester INTEGER,
    subject_code TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 訂正依頼テーブル
CREATE TABLE IF NOT EXISTS correction_requests (
    correction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_type TEXT NOT NULL,
    student_id INTEGER NOT NULL,
    course_id TEXT NOT NULL,
    target_date TEXT,
    semester INTEGER,
    before_value TEXT,
    after_value TEXT,
    reason TEXT NOT NULL,
    requester_name TEXT NOT NULL,
    requester_pc TEXT NOT NULL,
    request_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_locked BOOLEAN DEFAULT 0,
    locked_by TEXT,
    locked_datetime TIMESTAMP,
    status TEXT DEFAULT '未処理',
    is_deleted BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

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

-- システム設定テーブル
CREATE TABLE IF NOT EXISTS system_settings (
    setting_key TEXT PRIMARY KEY,
    setting_value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_students_year_class 
    ON students(year, class_number);

CREATE INDEX IF NOT EXISTS idx_corrections_student 
    ON correction_requests(student_id);

CREATE INDEX IF NOT EXISTS idx_corrections_course 
    ON correction_requests(course_id);

CREATE INDEX IF NOT EXISTS idx_corrections_status 
    ON correction_requests(status, is_locked);

CREATE INDEX IF NOT EXISTS idx_corrections_deleted 
    ON correction_requests(is_deleted);

CREATE INDEX IF NOT EXISTS idx_logs_timestamp 
    ON operation_logs(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_logs_user 
    ON operation_logs(username, pc_name);
