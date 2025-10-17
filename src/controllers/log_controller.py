"""
ログコントローラー
操作ログの記録と取得を管理
"""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..database.db_manager import DatabaseManager
from ..utils.system_info import get_username, get_pc_name
from ..utils.logger import get_logger

logger = get_logger(__name__)


class LogController:
    """操作ログを管理するコントローラー"""
    
    def __init__(self, db: DatabaseManager):
        """
        初期化
        
        Args:
            db: DatabaseManagerインスタンス
        """
        self.db = db
    
    def log_operation(
        self,
        operation_type: str,
        target_table: str,
        target_record_id: Optional[int] = None,
        before_data: Optional[Dict[str, Any]] = None,
        after_data: Optional[Dict[str, Any]] = None,
        detail: Optional[str] = None
    ) -> int:
        """
        操作をログに記録
        
        Args:
            operation_type: 操作種別（'作成'/'更新'/'削除'/'ロック'/'ロック解除'）
            target_table: 対象テーブル名
            target_record_id: 対象レコードID
            before_data: 変更前データ
            after_data: 変更後データ
            detail: 操作詳細
            
        Returns:
            挿入されたログID
        """
        username = get_username()
        pc_name = get_pc_name()
        
        # JSONシリアライズ
        before_json = json.dumps(before_data, ensure_ascii=False) if before_data else None
        after_json = json.dumps(after_data, ensure_ascii=False) if after_data else None
        
        log_id = self.db.execute_insert(
            """
            INSERT INTO operation_logs
            (username, pc_name, operation_type, target_table, target_record_id,
             before_data, after_data, operation_detail)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (username, pc_name, operation_type, target_table, target_record_id,
             before_json, after_json, detail)
        )
        
        logger.info(
            f"ログ記録: {operation_type} - {target_table} "
            f"(ID:{target_record_id}) by {username}@{pc_name}"
        )
        
        return log_id
    
    def get_logs(
        self,
        limit: int = 100,
        offset: int = 0,
        username: Optional[str] = None,
        operation_type: Optional[str] = None,
        target_table: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        ログを取得（フィルタ・ページネーション対応）
        
        Args:
            limit: 取得件数
            offset: オフセット
            username: ユーザー名でフィルタ
            operation_type: 操作種別でフィルタ
            target_table: テーブル名でフィルタ
            start_date: 開始日時
            end_date: 終了日時
            
        Returns:
            ログのリスト
        """
        query = "SELECT * FROM operation_logs WHERE 1=1"
        params = []
        
        if username:
            query += " AND username = ?"
            params.append(username)
        
        if operation_type:
            query += " AND operation_type = ?"
            params.append(operation_type)
        
        if target_table:
            query += " AND target_table = ?"
            params.append(target_table)
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())
        
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        rows = self.db.execute_query(query, tuple(params))
        return self.db.rows_to_dicts(rows)
    
    def get_log_by_id(self, log_id: int) -> Optional[Dict[str, Any]]:
        """
        ログIDでログを取得
        
        Args:
            log_id: ログID
            
        Returns:
            ログデータ
        """
        rows = self.db.execute_query(
            "SELECT * FROM operation_logs WHERE log_id = ?",
            (log_id,)
        )
        return self.db.row_to_dict(rows[0]) if rows else None
    
    def get_logs_count(
        self,
        username: Optional[str] = None,
        operation_type: Optional[str] = None,
        target_table: Optional[str] = None
    ) -> int:
        """
        ログの総数を取得
        
        Args:
            username: ユーザー名でフィルタ
            operation_type: 操作種別でフィルタ
            target_table: テーブル名でフィルタ
            
        Returns:
            ログの総数
        """
        query = "SELECT COUNT(*) as count FROM operation_logs WHERE 1=1"
        params = []
        
        if username:
            query += " AND username = ?"
            params.append(username)
        
        if operation_type:
            query += " AND operation_type = ?"
            params.append(operation_type)
        
        if target_table:
            query += " AND target_table = ?"
            params.append(target_table)
        
        rows = self.db.execute_query(query, tuple(params))
        return rows[0]['count'] if rows else 0
