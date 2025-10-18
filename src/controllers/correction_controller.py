"""
訂正依頼コントローラー
訂正依頼のCRUD操作とビジネスロジックを管理
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..database.db_manager import DatabaseManager
from ..controllers.log_controller import LogController
from ..utils.system_info import get_username, get_pc_name
from ..utils.logger import get_logger
from ..config import REQUEST_STATUS

logger = get_logger(__name__)


class CorrectionController:
    """訂正依頼を管理するコントローラー"""
    
    def __init__(self, db: DatabaseManager, log_controller: LogController):
        """
        初期化
        
        Args:
            db: DatabaseManagerインスタンス
            log_controller: LogControllerインスタンス
        """
        self.db = db
        self.log_controller = log_controller
    
    def create_correction(self, correction_data: Dict[str, Any]) -> int:
        """
        訂正依頼を作成
        
        Args:
            correction_data: 訂正依頼データ
                - request_type: 依頼種別
                - student_id: 生徒ID
                - course_id: 講座ID
                - target_date: 対象日付（出欠訂正の場合）
                - semester: 学期（評価評定変更の場合）
                - periods: 校時（出欠訂正の場合、カンマ区切り）
                - before_value: 訂正前
                - after_value: 訂正後
                - reason: 理由
                - requester: 依頼者
                
        Returns:
            作成された訂正依頼ID
        """
        pc_name = get_pc_name()
        
        correction_id = self.db.execute_insert(
            """
            INSERT INTO correction_requests
            (request_type, student_id, course_id, target_date, semester, periods,
             before_value, after_value, reason, requester_name, requester_pc)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                correction_data['request_type'],
                correction_data['student_id'],
                correction_data['course_id'],
                correction_data.get('target_date'),
                correction_data.get('semester'),
                correction_data.get('periods'),
                correction_data.get('before_value'),
                correction_data['after_value'],
                correction_data['reason'],
                correction_data['requester'],
                pc_name
            )
        )
        
        # ログ記録
        self.log_controller.log_operation(
            operation_type='作成',
            target_table='correction_requests',
            target_record_id=correction_id,
            after_data=correction_data,
            detail=f"訂正依頼を作成: {correction_data['request_type']} by {correction_data['requester']}"
        )
        
        logger.info(f"訂正依頼を作成しました: ID={correction_id}")
        return correction_id
    
    def get_correction(self, correction_id: int) -> Optional[Dict[str, Any]]:
        """
        訂正依頼を取得
        
        Args:
            correction_id: 訂正依頼ID
            
        Returns:
            訂正依頼データ
        """
        rows = self.db.execute_query(
            """
            SELECT cr.*, s.name as student_name, s.class_number, c.course_name
            FROM correction_requests cr
            LEFT JOIN students s ON cr.student_id = s.student_id
            LEFT JOIN courses c ON cr.course_id = c.course_id
            WHERE cr.correction_id = ? AND cr.is_deleted = 0
            """,
            (correction_id,)
        )
        return self.db.row_to_dict(rows[0]) if rows else None
    
    def get_corrections(
        self,
        status: Optional[str] = None,
        request_type: Optional[str] = None,
        is_locked: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        訂正依頼一覧を取得
        
        Args:
            status: ステータスでフィルタ
            request_type: 依頼種別でフィルタ
            is_locked: ロック状態でフィルタ
            limit: 取得件数
            offset: オフセット
            
        Returns:
            訂正依頼のリスト
        """
        query = """
            SELECT cr.*, s.name as student_name, s.class_number,
                   c.course_name, c.teacher_name
            FROM correction_requests cr
            LEFT JOIN students s ON cr.student_id = s.student_id
            LEFT JOIN courses c ON cr.course_id = c.course_id
            WHERE cr.is_deleted = 0
        """
        params = []
        
        if status:
            query += " AND cr.status = ?"
            params.append(status)
        
        if request_type:
            query += " AND cr.request_type = ?"
            params.append(request_type)
        
        if is_locked is not None:
            query += " AND cr.is_locked = ?"
            params.append(1 if is_locked else 0)
        
        query += " ORDER BY cr.request_datetime DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        rows = self.db.execute_query(query, tuple(params))
        return self.db.rows_to_dicts(rows)
    
    def update_correction(
        self,
        correction_id: int,
        update_data: Dict[str, Any]
    ) -> bool:
        """
        訂正依頼を更新
        
        Args:
            correction_id: 訂正依頼ID
            update_data: 更新データ
            
        Returns:
            更新成功したらTrue
        """
        before_data = self.get_correction(correction_id)
        if not before_data:
            logger.error(f"訂正依頼が見つかりません: ID={correction_id}")
            return False
        
        if before_data['is_locked']:
            logger.warning(f"ロックされた訂正依頼は更新できません: ID={correction_id}")
            return False
        
        set_clauses = []
        params = []
        
        for key, value in update_data.items():
            if key in ['request_type', 'target_date', 'semester', 'periods',
                      'before_value', 'after_value', 'reason', 'status']:
                set_clauses.append(f"{key} = ?")
                params.append(value)
        
        if not set_clauses:
            logger.warning("更新するデータがありません")
            return False
        
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        params.append(correction_id)
        
        query = f"""
            UPDATE correction_requests
            SET {', '.join(set_clauses)}
            WHERE correction_id = ? AND is_locked = 0 AND is_deleted = 0
        """
        
        affected = self.db.execute_update(query, tuple(params))
        
        if affected > 0:
            self.log_controller.log_operation(
                operation_type='更新',
                target_table='correction_requests',
                target_record_id=correction_id,
                before_data=before_data,
                after_data=update_data,
                detail="訂正依頼を更新"
            )
            logger.info(f"訂正依頼を更新しました: ID={correction_id}")
            return True
        
        return False
    
    def delete_correction(self, correction_id: int) -> bool:
        """
        訂正依頼を削除（論理削除）
        
        Args:
            correction_id: 訂正依頼ID
            
        Returns:
            削除成功したらTrue
        """
        before_data = self.get_correction(correction_id)
        if not before_data:
            logger.error(f"訂正依頼が見つかりません: ID={correction_id}")
            return False
        
        if before_data['is_locked']:
            logger.warning(f"ロックされた訂正依頼は削除できません: ID={correction_id}")
            return False
        
        affected = self.db.execute_update(
            """
            UPDATE correction_requests
            SET is_deleted = 1, updated_at = CURRENT_TIMESTAMP
            WHERE correction_id = ? AND is_locked = 0
            """,
            (correction_id,)
        )
        
        if affected > 0:
            self.log_controller.log_operation(
                operation_type='削除',
                target_table='correction_requests',
                target_record_id=correction_id,
                before_data=before_data,
                detail="訂正依頼を削除"
            )
            logger.info(f"訂正依頼を削除しました: ID={correction_id}")
            return True
        
        return False
    
    def lock_correction(self, correction_id: int) -> bool:
        """
        訂正依頼をロック
        
        Args:
            correction_id: 訂正依頼ID
            
        Returns:
            ロック成功したらTrue
        """
        username = get_username()
        
        affected = self.db.execute_update(
            """
            UPDATE correction_requests
            SET is_locked = 1, locked_by = ?, locked_datetime = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE correction_id = ? AND is_locked = 0 AND is_deleted = 0
            """,
            (username, correction_id)
        )
        
        if affected > 0:
            self.log_controller.log_operation(
                operation_type='ロック',
                target_table='correction_requests',
                target_record_id=correction_id,
                detail=f"訂正依頼をロック by {username}"
            )
            logger.info(f"訂正依頼をロックしました: ID={correction_id}")
            return True
        
        return False
    
    def unlock_correction(self, correction_id: int) -> bool:
        """
        訂正依頼のロックを解除
        
        Args:
            correction_id: 訂正依頼ID
            
        Returns:
            ロック解除成功したらTrue
        """
        username = get_username()
        
        affected = self.db.execute_update(
            """
            UPDATE correction_requests
            SET is_locked = 0, locked_by = NULL, locked_datetime = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE correction_id = ? AND is_locked = 1 AND is_deleted = 0
            """,
            (correction_id,)
        )
        
        if affected > 0:
            self.log_controller.log_operation(
                operation_type='ロック解除',
                target_table='correction_requests',
                target_record_id=correction_id,
                detail=f"訂正依頼のロックを解除 by {username}"
            )
            logger.info(f"訂正依頼のロックを解除しました: ID={correction_id}")
            return True
        
        return False
    
    def get_students(self, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """生徒一覧を取得"""
        query = "SELECT * FROM students WHERE 1=1"
        params = []
        
        if year:
            query += " AND year = ?"
            params.append(year)
        
        query += " ORDER BY year DESC, class_number, student_number"
        
        rows = self.db.execute_query(query, tuple(params) if params else None)
        return self.db.rows_to_dicts(rows)
    
    def get_courses(self, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """講座一覧を取得"""
        query = "SELECT * FROM courses WHERE 1=1"
        params = []
        
        if year:
            query += " AND year = ?"
            params.append(year)
        
        query += " ORDER BY year DESC, course_id"
        
        rows = self.db.execute_query(query, tuple(params) if params else None)
        return self.db.rows_to_dicts(rows)
