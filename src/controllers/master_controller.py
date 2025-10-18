"""
マスタコントローラー v1.5.0
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
        self.db = db
        self.log_controller = log_controller
    
    def get_students(self, year: Optional[int] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        生徒一覧を取得
        
        Args:
            year: 年度でフィルタ
            search: 検索文字列（氏名、ひらがなで検索）
        """
        query = "SELECT * FROM students WHERE 1=1"
        params = []
        
        if year:
            query += " AND year = ?"
            params.append(year)
        
        if search:
            query += " AND (name LIKE ? OR name_kana LIKE ?)"
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern])
        
        query += " ORDER BY year DESC, class_number"
        
        rows = self.db.execute_query(query, tuple(params) if params else None)
        return self.db.rows_to_dicts(rows)
    
    def create_student(self, student_data: Dict[str, Any]) -> str:
        """
        生徒情報を作成
        
        Args:
            student_data: 生徒データ
                - year: 年度
                - class_number: 組番号（5桁）
                - student_number: 学籍番号（7桁）
                - name: 氏名
                - name_kana: 氏名カナ
                - student_id: 任意（空の場合は年度-組番号を自動生成）
        
        Returns:
            生徒ID
        """
        # student_id が空の場合は自動生成
        student_id = student_data.get('student_id', '').strip()
        if not student_id:
            student_id = f"{student_data['year']}-{student_data['class_number']}"
        
        self.db.execute_insert(
            """
            INSERT OR REPLACE INTO students 
            (student_id, year, class_number, student_number, name, name_kana)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                student_id,
                student_data['year'],
                student_data['class_number'],
                student_data['student_number'],
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
        """
        講座情報を作成
        
        Args:
            course_data: 講座データ
                - year: 年度
                - course_number: 講座番号
                - course_name: 講座名
                - teacher_name: 担当教員
                - semester: 学期
                - subject_code: 科目コード
                - course_id: 任意（空の場合は年度-講座番号を自動生成）
        
        Returns:
            講座ID
        """
        # course_id が空の場合は自動生成
        course_id = course_data.get('course_id', '').strip()
        if not course_id:
            course_number = course_data.get('course_number', '')
            course_id = f"{course_data['year']}-{course_number}"
        
        self.db.execute_insert(
            """
            INSERT OR REPLACE INTO courses 
            (course_id, course_name, teacher_name, year, semester, subject_code)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                course_id,
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
            target_record_id=course_id,
            after_data=course_data,
            detail=f"講座情報を作成: {course_data['course_name']}"
        )
        
        logger.info(f"講座情報を作成しました: {course_id}")
        return course_id
