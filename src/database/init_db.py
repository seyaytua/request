"""
データベース初期化スクリプト
テーブル作成と初期データ投入
"""
from pathlib import Path
from .db_manager import DatabaseManager
from ..config import DB_PATH, DEFAULT_ADMIN_PASSWORD
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
    # 強制再作成の場合は既存ファイルを削除
    if force and db_path.exists():
        db_path.unlink()
        logger.warning(f"既存のデータベースを削除しました: {db_path}")
    
    # スキーマファイルのパス
    schema_path = Path(__file__).parent / "schema.sql"
    
    # スキーマファイルを読み込み
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # データベースマネージャー作成
    db = DatabaseManager(db_path)
    
    # スキーマ実行（複数のSQL文を分割して実行）
    with db.get_connection() as conn:
        conn.executescript(schema_sql)
    
    logger.info("データベーススキーマを作成しました")
    
    # 初期データ投入
    _insert_initial_data(db)
    
    logger.info(f"データベース初期化完了: {db_path}")
    return db


def _insert_initial_data(db: DatabaseManager):
    """初期データを投入"""
    
    # システム設定: 管理者パスワード
    admin_password_hash = hash_password(DEFAULT_ADMIN_PASSWORD)
    
    try:
        db.execute_insert(
            """
            INSERT INTO system_settings (setting_key, setting_value)
            VALUES (?, ?)
            """,
            ('admin_password_hash', admin_password_hash)
        )
        logger.info(f"初期管理者パスワードを設定しました（パスワード: {DEFAULT_ADMIN_PASSWORD}）")
    except Exception as e:
        # 既に存在する場合はスキップ
        logger.debug(f"初期データは既に存在します: {e}")
    
    # サンプルデータ（開発用）
    _insert_sample_data(db)


def _insert_sample_data(db: DatabaseManager):
    """サンプルデータを投入（開発・テスト用）"""
    
    try:
        # サンプル生徒データ
        sample_students = [
            (2024, "1-A", "01", "山田太郎", "やまだたろう"),
            (2024, "1-A", "02", "佐藤花子", "さとうはなこ"),
            (2024, "1-B", "01", "鈴木一郎", "すずきいちろう"),
        ]
        
        for student in sample_students:
            db.execute_insert(
                """
                INSERT OR IGNORE INTO students 
                (year, class_number, student_number, name, name_kana)
                VALUES (?, ?, ?, ?, ?)
                """,
                student
            )
        
        # サンプル講座データ
        sample_courses = [
            ("2024-MATH-01", "数学I", "田中先生", 2024, 1, "MATH"),
            ("2024-ENG-01", "英語I", "佐々木先生", 2024, 1, "ENG"),
            ("2024-SCI-01", "理科I", "高橋先生", 2024, 1, "SCI"),
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


# テスト用
if __name__ == "__main__":
    from ..config import DATA_DIR
    
    # テスト用DBパス
    test_db = DATA_DIR / "test_init.db"
    
    # 初期化実行
    db = initialize_database(test_db, force=True)
    
    # 確認
    students = db.execute_query("SELECT * FROM students")
    courses = db.execute_query("SELECT * FROM courses")
    settings = db.execute_query("SELECT * FROM system_settings")
    
    print(f"\n生徒数: {len(students)}")
    print(f"講座数: {len(courses)}")
    print(f"設定数: {len(settings)}")
    
    print("\n✅ データベース初期化テスト完了")
