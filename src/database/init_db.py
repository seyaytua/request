"""
データベース初期化スクリプト v1.5.0
テーブル作成と初期データ投入
"""
from pathlib import Path
from .db_manager import DatabaseManager
from ..config import DB_PATH, DEFAULT_ADMIN_PASSWORD, DEFAULT_NOTICE_MESSAGE, DEFAULT_BACKUP_INTERVAL
from ..utils.password_hash import hash_password
from ..utils.logger import get_logger

logger = get_logger(__name__)


def initialize_database(db_path: Path = DB_PATH, force: bool = False):
    """
    データベースを初期化
    
    Args:
        db_path: データベースファイルのパス
        force: 既存のDBを削除して再作成するか
    """
    if force and db_path.exists():
        db_path.unlink()
        logger.warning(f"既存のデータベースを削除しました: {db_path}")
    
    schema_path = Path(__file__).parent / "schema.sql"
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    db = DatabaseManager(db_path)
    
    with db.get_connection() as conn:
        conn.executescript(schema_sql)
    
    logger.info("データベーススキーマを作成しました")
    
    _insert_initial_data(db)
    
    logger.info(f"データベース初期化完了: {db_path}")
    return db


def _insert_initial_data(db: DatabaseManager):
    """初期データを投入"""
    admin_password_hash = hash_password(DEFAULT_ADMIN_PASSWORD)
    
    try:
        # 既存の設定を確認
        existing = db.execute_query(
            "SELECT setting_key FROM system_settings WHERE setting_key = 'admin_password_hash'"
        )
        
        if not existing:
            # 初期設定を挿入
            settings = [
                ('admin_password_hash', admin_password_hash),
                ('app_version', '1.5.0'),
                ('db_version', '1.5'),
                ('app_title', '訂正依頼システム'),
                ('notice_message', DEFAULT_NOTICE_MESSAGE),
                ('backup_interval', str(DEFAULT_BACKUP_INTERVAL)),
                ('launch_count', '0')
            ]
            
            for key, value in settings:
                db.execute_insert(
                    "INSERT OR IGNORE INTO system_settings (setting_key, setting_value) VALUES (?, ?)",
                    (key, value)
                )
            
            logger.info(f"初期管理者パスワードを設定しました（パスワード: {DEFAULT_ADMIN_PASSWORD}）")
        else:
            logger.info("システム設定は既に存在します")
    
    except Exception as e:
        logger.error(f"初期データ投入エラー: {e}")
    
    _insert_sample_data(db)


def _insert_sample_data(db: DatabaseManager):
    """サンプルデータを投入（開発・テスト用）"""
    try:
        # サンプル生徒データ（新しいID構造）
        sample_students = [
            ("2024-F1221", 2024, "F1221", "1234567", "山田太郎", "やまだたろう"),
            ("2024-F1222", 2024, "F1222", "1234568", "佐藤花子", "さとうはなこ"),
            ("2024-J2123", 2024, "J2123", "1234569", "鈴木一郎", "すずきいちろう"),
        ]
        
        for student in sample_students:
            db.execute_insert(
                """
                INSERT OR IGNORE INTO students 
                (student_id, year, class_number, student_number, name, name_kana)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                student
            )
        
        # サンプル講座データ（新しいID構造）
        sample_courses = [
            ("2024-MATH-01", "数学I", "田中先生", 2024, "前期中間", "MATH"),
            ("2024-ENG-01", "英語I", "佐々木先生", 2024, "前期期末", "ENG"),
            ("2024-SCI-01", "理科I", "高橋先生", 2024, "後期中間", "SCI"),
        ]
        
        for course in sample_courses:
            db.execute_insert(
                """
                INSERT OR IGNORE INTO courses 
                (course_id, course_name, teacher_name, year, semester, subject_code)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                course
            )
        
        logger.info("サンプルデータを投入しました")
        
    except Exception as e:
        logger.warning(f"サンプルデータの投入に失敗しました: {e}")


if __name__ == "__main__":
    from ..config import DATA_DIR
    
    test_db = DATA_DIR / "test_init.db"
    db = initialize_database(test_db, force=True)
    
    students = db.execute_query("SELECT * FROM students")
    courses = db.execute_query("SELECT * FROM courses")
    settings = db.execute_query("SELECT * FROM system_settings")
    
    print(f"\n生徒数: {len(students)}")
    print(f"講座数: {len(courses)}")
    print(f"設定数: {len(settings)}")
    
    print("\n✅ データベース初期化テスト完了")
