"""
データベースマネージャー
SQLiteデータベースへの接続とCRUD操作を管理
"""
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

from ..config import DB_PATH, DB_TIMEOUT, DB_WAL_MODE
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """データベース接続とCRUD操作を管理するクラス"""
    
    def __init__(self, db_path: Path = DB_PATH):
        """
        初期化
        
        Args:
            db_path: データベースファイルのパス
        """
        self.db_path = db_path
        self.lock = threading.Lock()
        logger.info(f"DatabaseManager initialized: {db_path}")
    
    @contextmanager
    def get_connection(self):
        """
        データベース接続を取得（コンテキストマネージャー）
        自動的にコミット・ロールバック・クローズを管理
        """
        self.lock.acquire()
        conn = None
        try:
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=DB_TIMEOUT,
                check_same_thread=False
            )
            conn.row_factory = sqlite3.Row  # 辞書形式で結果取得
            
            # WALモード有効化（並行アクセス改善）
            if DB_WAL_MODE:
                conn.execute("PRAGMA journal_mode=WAL")
            
            yield conn
            conn.commit()
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
            self.lock.release()
    
    def execute_query(self, query: str, params: tuple = None) -> List[sqlite3.Row]:
        """
        SELECTクエリを実行
        
        Args:
            query: SQLクエリ
            params: パラメータ
            
        Returns:
            クエリ結果のリスト
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """
        INSERT/UPDATE/DELETEクエリを実行
        
        Args:
            query: SQLクエリ
            params: パラメータ
            
        Returns:
            影響を受けた行数
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.rowcount
    
    def execute_insert(self, query: str, params: tuple = None) -> int:
        """
        INSERTクエリを実行し、挿入されたIDを返す
        
        Args:
            query: SQLクエリ
            params: パラメータ
            
        Returns:
            挿入されたレコードのID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.lastrowid
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """
        複数のクエリを一括実行
        
        Args:
            query: SQLクエリ
            params_list: パラメータのリスト
            
        Returns:
            影響を受けた行数の合計
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            return cursor.rowcount
    
    def row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """
        sqlite3.Rowを辞書に変換
        
        Args:
            row: sqlite3.Row オブジェクト
            
        Returns:
            辞書形式のデータ
        """
        return dict(row) if row else {}
    
    def rows_to_dicts(self, rows: List[sqlite3.Row]) -> List[Dict[str, Any]]:
        """
        sqlite3.Rowのリストを辞書のリストに変換
        
        Args:
            rows: sqlite3.Row のリスト
            
        Returns:
            辞書のリスト
        """
        return [self.row_to_dict(row) for row in rows]


# テスト用
if __name__ == "__main__":
    from ..config import DATA_DIR
    
    # テスト用DBパス
    test_db = DATA_DIR / "test.db"
    
    # マネージャー作成
    db = DatabaseManager(test_db)
    
    # テーブル作成
    db.execute_update("""
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    """)
    
    # データ挿入
    insert_id = db.execute_insert(
        "INSERT INTO test_table (name) VALUES (?)",
        ("テストデータ",)
    )
    print(f"挿入されたID: {insert_id}")
    
    # データ取得
    rows = db.execute_query("SELECT * FROM test_table")
    print(f"取得データ: {db.rows_to_dicts(rows)}")
    
    print("✅ DatabaseManager テスト完了")
