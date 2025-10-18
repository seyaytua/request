"""
マスタコントローラー
生徒情報・講座情報のCRUD操作を管理
"""
from typing import Dict, Any, List, Optional

from ..database.db_manager import DatabaseManager
from ..controllers.log_controller import LogController
from ..utils.logger import get_logger

logger = get_logger(__name__)


class MasterController:
    """マスタデータを管理するコントローラー"""
    
    def __init__(self, db: DatabaseManager, log_controller: LogController):
        """
        初期化
        
        Args:
            db: DatabaseManagerインスタンス
            log_controller: LogControllerインスタンス
        """
        self.db = db
        self.log_controller = log_controller
    
    # 生徒情報管理
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
    
    def create_student(self, student_data: Dict[str, Any]) -> int:
        """生徒情報を作成"""
        student_id = self.db.execute_insert(
            """
            INSERT INTO students (year, class_number, student_number, name, name_kana)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                student_data['year'],
                student_data['class_number'],
                student_data.get('student_number', ''),
                student_data['name'],
                student_data.get('name_kana', '')
            )
        )
        
        self.log_controller.log_operation(
            operation_type='作成',
            target_table='students',
            target_record_id=student_id,
            after_data=student_data,
            detail=f"生徒情報を作成: {student_data['name']}"
        )
        
        logger.info(f"生徒情報を作成しました: ID={student_id}")
        return student_id
    
    # 講座情報管理
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
    
    def create_course(self, course_data: Dict[str, Any]) -> str:
        """講座情報を作成"""
        self.db.execute_insert(
            """
            INSERT INTO courses (course_id, course_name, teacher_name, year, semester, subject_code)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                course_data['course_id'],
                course_data['course_name'],
                course_data.get('teacher_name', ''),
                course_data['year'],
                course_data.get('semester', ''),
                course_data.get('subject_code', '')
            )
        )
        
        self.log_controller.log_operation(
            operation_type='作成',
            target_table='courses',
            target_record_id=None,
            after_data=course_data,
            detail=f"講座情報を作成: {course_data['course_name']}"
        )
        
        logger.info(f"講座情報を作成しました: {course_data['course_id']}")
        return course_data['course_id']
