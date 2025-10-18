#!/bin/bash

echo "🔧 訂正依頼システムの更新を開始します..."

# 1. データベーススキーマの更新
echo "📝 データベーススキーマを更新中..."
cat > src/database/schema.sql << 'EOF'
-- 訂正依頼システム - データベーススキーマ
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

-- 訂正依頼テーブル
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
    status TEXT DEFAULT '未処理' CHECK(status IN ('未処理', '処理中', '完了')),
    is_deleted BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

CREATE INDEX IF NOT EXISTS idx_corrections_student ON correction_requests(student_id);
CREATE INDEX IF NOT EXISTS idx_corrections_course ON correction_requests(course_id);
CREATE INDEX IF NOT EXISTS idx_corrections_status ON correction_requests(status, is_locked);
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
('app_version', '1.0.0'),
('db_version', '1.0');
EOF

echo "✅ データベーススキーマを更新しました"

# 2. 設定ファイルの更新
echo "📝 設定ファイルを更新中..."
cat > src/config.py << 'EOF'
"""
設定ファイル
"""
import os
import sys
from pathlib import Path

APP_NAME = "訂正依頼システム"
APP_VERSION = "1.0.0"

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
    DATA_DIR = Path(os.path.dirname(sys.executable)) / "data"
else:
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"

DB_PATH = DATA_DIR / "corrections.db"
RESOURCES_DIR = BASE_DIR / "src" / "resources"
ICONS_DIR = RESOURCES_DIR / "icons"
STYLES_DIR = RESOURCES_DIR / "styles"

DATA_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_ADMIN_PASSWORD = "admin123"

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800
LIST_WIDTH_RATIO = 0.65

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

DB_TIMEOUT = 30.0
DB_WAL_MODE = True

REQUEST_TYPES = {
    "ATTENDANCE": "出欠訂正",
    "GRADE": "評価評定変更"
}

REQUEST_STATUS = {
    "PENDING": "未処理",
    "PROCESSING": "処理中",
    "COMPLETED": "完了",
    "REJECTED": "却下"
}

ATTENDANCE_TYPES = ["出席", "欠席", "遅刻", "早退", "公欠"]
GRADE_TYPES = ["A", "B", "C", "D", "F"]
SEMESTER_TYPES = ["前期中間", "前期期末", "後期中間", "仮評定", "後期期末", "評定"]
PERIOD_TYPES = [f"{i}限" for i in range(1, 13)]

COLOR_ATTENDANCE = "#E8F5E9"
COLOR_GRADE = "#FFF3E0"

print(f"✅ Config loaded: DB_PATH={DB_PATH}")
EOF

echo "✅ 設定ファイルを更新しました"

echo ""
echo "🎉 更新が完了しました！"
echo ""
echo "次のコマンドを実行してください："
echo ""
echo "1. データベースを再初期化:"
echo "   python -c 'from src.database.init_db import initialize_database; from src.config import DB_PATH; initialize_database(DB_PATH, force=True)'"
echo ""
echo "2. アプリケーションを起動:"
echo "   python main.py"
echo ""
echo "管理者パスワード: admin123"

