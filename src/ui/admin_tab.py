"""
システム部管理タブ
ロック管理、インポート/エクスポート、ログビューア、マスタ管理
"""
import csv
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMessageBox, QGroupBox, QFileDialog,
    QTabWidget
)
from PySide6.QtCore import Qt

from ..controllers.correction_controller import CorrectionController
from ..controllers.log_controller import LogController
from ..controllers.master_controller import MasterController
from ..utils.logger import get_logger

logger = get_logger(__name__)


class AdminTab(QWidget):
    """システム部管理タブ"""
    
    def __init__(
        self, 
        correction_controller: CorrectionController,
        log_controller: LogController,
        master_controller: MasterController,
        parent=None
    ):
        super().__init__(parent)
        self.correction_controller = correction_controller
        self.log_controller = log_controller
        self.master_controller = master_controller
        self.setup_ui()
        
    def setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout()
        
        # タブウィジェット
        tabs = QTabWidget()
        
        # 訂正依頼管理タブ
        correction_widget = self._create_correction_tab()
        tabs.addTab(correction_widget, "📝 訂正依頼管理")
        
        # 生徒情報管理タブ
        student_widget = self._create_student_tab()
        tabs.addTab(student_widget, "👨‍🎓 生徒情報管理")
        
        # 講座情報管理タブ
        course_widget = self._create_course_tab()
        tabs.addTab(course_widget, "📚 講座情報管理")
        
        # 操作ログタブ
        log_widget = self._create_log_tab()
        tabs.addTab(log_widget, "📊 操作ログ")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
    
    def _create_correction_tab(self):
        """訂正依頼管理タブを作成"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # データ管理エリア
        data_group = QGroupBox("データ管理")
        data_layout = QHBoxLayout()
        
        export_btn = QPushButton("📤 CSVエクスポート")
        export_btn.clicked.connect(self.export_corrections_to_csv)
        data_layout.addWidget(export_btn)
        
        import_btn = QPushButton("📥 CSVインポート")
        import_btn.clicked.connect(self.import_corrections_from_csv)
        data_layout.addWidget(import_btn)
        
        data_layout.addStretch()
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)
        
        # 訂正依頼管理エリア
        correction_group = QGroupBox("訂正依頼管理")
        correction_layout = QVBoxLayout()
        
        # ボタンエリア
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 更新")
        refresh_btn.clicked.connect(self.refresh_correction_list)
        button_layout.addWidget(refresh_btn)
        
        lock_btn = QPushButton("🔒 選択した依頼をロック")
        lock_btn.clicked.connect(self.lock_selected)
        button_layout.addWidget(lock_btn)
        
        unlock_btn = QPushButton("🔓 選択した依頼のロックを解除")
        unlock_btn.clicked.connect(self.unlock_selected)
        button_layout.addWidget(unlock_btn)
        
        button_layout.addStretch()
        correction_layout.addLayout(button_layout)
        
        # 訂正依頼リスト（詳細表示）
        self.correction_table = QTableWidget()
        self.correction_table.setColumnCount(13)
        self.correction_table.setHorizontalHeaderLabels([
            "ID", "種別", "生徒名", "組番号", "講座名", "対象日付", 
            "学期", "校時", "訂正前", "訂正後", "理由", "依頼者", "ロック者"
        ])
        self.correction_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.correction_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        header = self.correction_table.horizontalHeader()
        header.setStretchLastSection(True)
        for i in range(13):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        correction_layout.addWidget(self.correction_table)
        correction_group.setLayout(correction_layout)
        
        layout.addWidget(correction_group)
        widget.setLayout(layout)
        return widget
    
    def _create_student_tab(self):
        """生徒情報管理タブを作成"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # データ管理
        data_group = QGroupBox("データ管理")
        data_layout = QHBoxLayout()
        
        export_btn = QPushButton("📤 CSVエクスポート")
        export_btn.clicked.connect(self.export_students_to_csv)
        data_layout.addWidget(export_btn)
        
        import_btn = QPushButton("📥 CSVインポート（差替え）")
        import_btn.clicked.connect(self.import_students_from_csv)
        data_layout.addWidget(import_btn)
        
        refresh_btn = QPushButton("🔄 更新")
        refresh_btn.clicked.connect(self.refresh_student_list)
        data_layout.addWidget(refresh_btn)
        
        data_layout.addStretch()
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)
        
        # 生徒情報リスト
        self.student_table = QTableWidget()
        self.student_table.setColumnCount(6)
        self.student_table.setHorizontalHeaderLabels([
            "ID", "年度", "組番号", "出席番号", "氏名", "氏名カナ"
        ])
        self.student_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.student_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        header = self.student_table.horizontalHeader()
        header.setStretchLastSection(True)
        
        layout.addWidget(self.student_table)
        widget.setLayout(layout)
        return widget
    
    def _create_course_tab(self):
        """講座情報管理タブを作成"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # データ管理
        data_group = QGroupBox("データ管理")
        data_layout = QHBoxLayout()
        
        export_btn = QPushButton("📤 CSVエクスポート")
        export_btn.clicked.connect(self.export_courses_to_csv)
        data_layout.addWidget(export_btn)
        
        import_btn = QPushButton("📥 CSVインポート（差替え）")
        import_btn.clicked.connect(self.import_courses_from_csv)
        data_layout.addWidget(import_btn)
        
        refresh_btn = QPushButton("🔄 更新")
        refresh_btn.clicked.connect(self.refresh_course_list)
        data_layout.addWidget(refresh_btn)
        
        data_layout.addStretch()
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)
        
        # 講座情報リスト
        self.course_table = QTableWidget()
        self.course_table.setColumnCount(6)
        self.course_table.setHorizontalHeaderLabels([
            "講座ID", "講座名", "担当教員", "年度", "学期", "科目コード"
        ])
        self.course_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.course_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        header = self.course_table.horizontalHeader()
        header.setStretchLastSection(True)
        
        layout.addWidget(self.course_table)
        widget.setLayout(layout)
        return widget
    
    def _create_log_tab(self):
        """操作ログタブを作成"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # データ管理
        data_group = QGroupBox("データ管理")
        data_layout = QHBoxLayout()
        
        export_btn = QPushButton("📤 CSVエクスポート")
        export_btn.clicked.connect(self.export_logs_to_csv)
        data_layout.addWidget(export_btn)
        
        refresh_btn = QPushButton("🔄 更新")
        refresh_btn.clicked.connect(self.refresh_logs)
        data_layout.addWidget(refresh_btn)
        
        data_layout.addStretch()
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)
        
        # ログテーブル
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(6)
        self.log_table.setHorizontalHeaderLabels([
            "日時", "ユーザー", "PC名", "操作種別", "対象テーブル", "詳細"
        ])
        self.log_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.log_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        header = self.log_table.horizontalHeader()
        header.setStretchLastSection(True)
        
        layout.addWidget(self.log_table)
        widget.setLayout(layout)
        return widget
    
    def load_data(self):
        """データをロード"""
        self.refresh_correction_list()
        self.refresh_student_list()
        self.refresh_course_list()
        self.refresh_logs()
    
    def refresh_correction_list(self):
        """訂正依頼リストを更新"""
        try:
            corrections = self.correction_controller.get_corrections(limit=1000)
            
            self.correction_table.setRowCount(0)
            
            for correction in corrections:
                row = self.correction_table.rowCount()
                self.correction_table.insertRow(row)
                
                self.correction_table.setItem(row, 0, 
                    QTableWidgetItem(str(correction['correction_id'])))
                self.correction_table.setItem(row, 1, 
                    QTableWidgetItem(correction['request_type']))
                self.correction_table.setItem(row, 2, 
                    QTableWidgetItem(correction.get('student_name', '')))
                self.correction_table.setItem(row, 3, 
                    QTableWidgetItem(correction.get('class_number', '')))
                self.correction_table.setItem(row, 4, 
                    QTableWidgetItem(correction.get('course_name', '')))
                self.correction_table.setItem(row, 5, 
                    QTableWidgetItem(correction.get('target_date', '')))
                self.correction_table.setItem(row, 6, 
                    QTableWidgetItem(correction.get('semester', '')))
                self.correction_table.setItem(row, 7, 
                    QTableWidgetItem(correction.get('periods', '')))
                self.correction_table.setItem(row, 8, 
                    QTableWidgetItem(correction.get('before_value', '')))
                self.correction_table.setItem(row, 9, 
                    QTableWidgetItem(correction.get('after_value', '')))
                self.correction_table.setItem(row, 10, 
                    QTableWidgetItem(correction.get('reason', '')[:50]))
                self.correction_table.setItem(row, 11, 
                    QTableWidgetItem(correction.get('requester_name', '')))
                self.correction_table.setItem(row, 12, 
                    QTableWidgetItem(correction.get('locked_by', '') if correction.get('is_locked') else ''))
            
            logger.info(f"{len(corrections)}件の訂正依頼をロードしました")
            
        except Exception as e:
            logger.error(f"訂正依頼リストの更新に失敗: {e}")
            QMessageBox.critical(self, "エラー", 
                f"訂正依頼リストの更新に失敗しました:\n{e}")
    
    def refresh_student_list(self):
        """生徒情報リストを更新"""
        try:
            students = self.master_controller.get_students()
            
            self.student_table.setRowCount(0)
            
            for student in students:
                row = self.student_table.rowCount()
                self.student_table.insertRow(row)
                
                self.student_table.setItem(row, 0, 
                    QTableWidgetItem(str(student['student_id'])))
                self.student_table.setItem(row, 1, 
                    QTableWidgetItem(str(student['year'])))
                self.student_table.setItem(row, 2, 
                    QTableWidgetItem(student['class_number']))
                self.student_table.setItem(row, 3, 
                    QTableWidgetItem(student.get('student_number', '')))
                self.student_table.setItem(row, 4, 
                    QTableWidgetItem(student['name']))
                self.student_table.setItem(row, 5, 
                    QTableWidgetItem(student.get('name_kana', '')))
            
            logger.info(f"{len(students)}件の生徒情報をロードしました")
            
        except Exception as e:
            logger.error(f"生徒情報リストの更新に失敗: {e}")
            QMessageBox.critical(self, "エラー", 
                f"生徒情報リストの更新に失敗しました:\n{e}")
    
    def refresh_course_list(self):
        """講座情報リストを更新"""
        try:
            courses = self.master_controller.get_courses()
            
            self.course_table.setRowCount(0)
            
            for course in courses:
                row = self.course_table.rowCount()
                self.course_table.insertRow(row)
                
                self.course_table.setItem(row, 0, 
                    QTableWidgetItem(course['course_id']))
                self.course_table.setItem(row, 1, 
                    QTableWidgetItem(course['course_name']))
                self.course_table.setItem(row, 2, 
                    QTableWidgetItem(course.get('teacher_name', '')))
                self.course_table.setItem(row, 3, 
                    QTableWidgetItem(str(course['year'])))
                self.course_table.setItem(row, 4, 
                    QTableWidgetItem(course.get('semester', '')))
                self.course_table.setItem(row, 5, 
                    QTableWidgetItem(course.get('subject_code', '')))
            
            logger.info(f"{len(courses)}件の講座情報をロードしました")
            
        except Exception as e:
            logger.error(f"講座情報リストの更新に失敗: {e}")
            QMessageBox.critical(self, "エラー", 
                f"講座情報リストの更新に失敗しました:\n{e}")
    
    def lock_selected(self):
        """選択された訂正依頼をロック"""
        selected_items = self.correction_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "ロックする項目を選択してください")
            return
        
        row = selected_items[0].row()
        correction_id = int(self.correction_table.item(row, 0).text())
        
        reply = QMessageBox.question(
            self, "確認", 
            f"訂正依頼 ID:{correction_id} をロックしますか？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = self.correction_controller.lock_correction(correction_id)
                
                if success:
                    QMessageBox.information(self, "完了", "訂正依頼をロックしました")
                    self.refresh_correction_list()
                else:
                    QMessageBox.warning(self, "失敗", "ロックに失敗しました")
                    
            except Exception as e:
                logger.error(f"ロックに失敗: {e}")
                QMessageBox.critical(self, "エラー", 
                    f"ロックに失敗しました:\n{e}")
    
    def unlock_selected(self):
        """選択された訂正依頼のロックを解除"""
        selected_items = self.correction_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "ロック解除する項目を選択してください")
            return
        
        row = selected_items[0].row()
        correction_id = int(self.correction_table.item(row, 0).text())
        
        reply = QMessageBox.question(
            self, "確認", 
            f"訂正依頼 ID:{correction_id} のロックを解除しますか？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = self.correction_controller.unlock_correction(correction_id)
                
                if success:
                    QMessageBox.information(self, "完了", "ロックを解除しました")
                    self.refresh_correction_list()
                else:
                    QMessageBox.warning(self, "失敗", "ロックの解除に失敗しました")
                    
            except Exception as e:
                logger.error(f"ロック解除に失敗: {e}")
                QMessageBox.critical(self, "エラー", 
                    f"ロック解除に失敗しました:\n{e}")
    
    def export_corrections_to_csv(self):
        """訂正依頼CSVエクスポート"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "CSVエクスポート", "", "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            corrections = self.correction_controller.get_corrections(limit=10000)
            
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                writer.writerow([
                    'ID', '種別', '生徒ID', '生徒名', '組番号', 
                    '講座ID', '講座名', '対象日付', '学期', '校時',
                    '訂正前', '訂正後', '理由', '依頼者', '依頼者PC',
                    'ロック', 'ロック者', 'ロック日時', '依頼日時'
                ])
                
                for c in corrections:
                    writer.writerow([
                        c['correction_id'],
                        c['request_type'],
                        c['student_id'],
                        c.get('student_name', ''),
                        c.get('class_number', ''),
                        c['course_id'],
                        c.get('course_name', ''),
                        c.get('target_date', ''),
                        c.get('semester', ''),
                        c.get('periods', ''),
                        c.get('before_value', ''),
                        c.get('after_value', ''),
                        c.get('reason', ''),
                        c.get('requester_name', ''),
                        c.get('requester_pc', ''),
                        '○' if c['is_locked'] else '',
                        c.get('locked_by', ''),
                        c.get('locked_datetime', ''),
                        c.get('request_datetime', '')
                    ])
            
            QMessageBox.information(self, "完了", 
                f"{len(corrections)}件のデータをエクスポートしました\n{file_path}")
            logger.info(f"CSVエクスポート完了: {file_path}")
            
        except Exception as e:
            logger.error(f"CSVエクスポートに失敗: {e}")
            QMessageBox.critical(self, "エラー", 
                f"CSVエクスポートに失敗しました:\n{e}")
    
    def import_corrections_from_csv(self):
        """訂正依頼CSVインポート（差替え）"""
        reply = QMessageBox.warning(
            self, "警告", 
            "CSVインポートは既存のデータを全て削除して置き換えます。\n"
            "この操作は取り消せません。続行しますか？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "CSVインポート", "", "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            if len(rows) == 0:
                QMessageBox.information(self, "完了", 
                    "データ件数: 0件\n（タイトル行のみのため、データは削除されました）")
                self.correction_controller.db.execute_update(
                    "DELETE FROM correction_requests"
                )
                self.refresh_correction_list()
                return
            
            self.correction_controller.db.execute_update(
                "DELETE FROM correction_requests"
            )
            
            success_count = 0
            for row in rows:
                try:
                    correction_data = {
                        'request_type': row['種別'],
                        'student_id': int(row['生徒ID']),
                        'course_id': row['講座ID'],
                        'target_date': row['対象日付'] or None,
                        'semester': row['学期'] or None,
                        'periods': row['校時'] or None,
                        'before_value': row['訂正前'] or None,
                        'after_value': row['訂正後'],
                        'reason': row['理由'],
                        'requester': row['依頼者']
                    }
                    
                    self.correction_controller.create_correction(correction_data)
                    success_count += 1
                    
                except Exception as e:
                    logger.warning(f"行のインポートに失敗: {e}")
                    continue
            
            QMessageBox.information(self, "完了", 
                f"{success_count}件のデータをインポートしました")
            logger.info(f"CSVインポート完了: {success_count}件")
            
            self.refresh_correction_list()
            
        except Exception as e:
            logger.error(f"CSVインポートに失敗: {e}")
            QMessageBox.critical(self, "エラー", 
                f"CSVインポートに失敗しました:\n{e}")
    
    def export_students_to_csv(self):
        """生徒情報CSVエクスポート"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "生徒情報CSVエクスポート", "", "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            students = self.master_controller.get_students()
            
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                writer.writerow(['年度', '組番号', '出席番号', '氏名', '氏名カナ'])
                
                for s in students:
                    writer.writerow([
                        s['year'],
                        s['class_number'],
                        s.get('student_number', ''),
                        s['name'],
                        s.get('name_kana', '')
                    ])
            
            QMessageBox.information(self, "完了", 
                f"{len(students)}件のデータをエクスポートしました\n{file_path}")
            logger.info(f"生徒情報CSVエクスポート完了: {file_path}")
            
        except Exception as e:
            logger.error(f"生徒情報CSVエクスポートに失敗: {e}")
            QMessageBox.critical(self, "エラー", 
                f"生徒情報CSVエクスポートに失敗しました:\n{e}")
    
    def import_students_from_csv(self):
        """生徒情報CSVインポート（差替え）"""
        reply = QMessageBox.warning(
            self, "警告", 
            "CSVインポートは既存のデータを全て削除して置き換えます。\n"
            "この操作は取り消せません。続行しますか？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "生徒情報CSVインポート", "", "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            if len(rows) == 0:
                QMessageBox.information(self, "完了", 
                    "データ件数: 0件\n（タイトル行のみのため、データは削除されました）")
                self.master_controller.db.execute_update("DELETE FROM students")
                self.refresh_student_list()
                return
            
            self.master_controller.db.execute_update("DELETE FROM students")
            
            success_count = 0
            for row in rows:
                try:
                    student_data = {
                        'year': int(row['年度']),
                        'class_number': row['組番号'],
                        'student_number': row.get('出席番号', ''),
                        'name': row['氏名'],
                        'name_kana': row.get('氏名カナ', '')
                    }
                    
                    self.master_controller.create_student(student_data)
                    success_count += 1
                    
                except Exception as e:
                    logger.warning(f"行のインポートに失敗: {e}")
                    continue
            
            QMessageBox.information(self, "完了", 
                f"{success_count}件のデータをインポートしました")
            logger.info(f"生徒情報CSVインポート完了: {success_count}件")
            
            self.refresh_student_list()
            
        except Exception as e:
            logger.error(f"生徒情報CSVインポートに失敗: {e}")
            QMessageBox.critical(self, "エラー", 
                f"生徒情報CSVインポートに失敗しました:\n{e}")
    
    def export_courses_to_csv(self):
        """講座情報CSVエクスポート"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "講座情報CSVエクスポート", "", "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            courses = self.master_controller.get_courses()
            
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                writer.writerow(['講座ID', '講座名', '担当教員', '年度', '学期', '科目コード'])
                
                for c in courses:
                    writer.writerow([
                        c['course_id'],
                        c['course_name'],
                        c.get('teacher_name', ''),
                        c['year'],
                        c.get('semester', ''),
                        c.get('subject_code', '')
                    ])
            
            QMessageBox.information(self, "完了", 
                f"{len(courses)}件のデータをエクスポートしました\n{file_path}")
            logger.info(f"講座情報CSVエクスポート完了: {file_path}")
            
        except Exception as e:
            logger.error(f"講座情報CSVエクスポートに失敗: {e}")
            QMessageBox.critical(self, "エラー", 
                f"講座情報CSVエクスポートに失敗しました:\n{e}")
    
    def import_courses_from_csv(self):
        """講座情報CSVインポート（差替え）"""
        reply = QMessageBox.warning(
            self, "警告", 
            "CSVインポートは既存のデータを全て削除して置き換えます。\n"
            "この操作は取り消せません。続行しますか？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "講座情報CSVインポート", "", "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            if len(rows) == 0:
                QMessageBox.information(self, "完了", 
                    "データ件数: 0件\n（タイトル行のみのため、データは削除されました）")
                self.master_controller.db.execute_update("DELETE FROM courses")
                self.refresh_course_list()
                return
            
            self.master_controller.db.execute_update("DELETE FROM courses")
            
            success_count = 0
            for row in rows:
                try:
                    course_data = {
                        'course_id': row['講座ID'],
                        'course_name': row['講座名'],
                        'teacher_name': row.get('担当教員', ''),
                        'year': int(row['年度']),
                        'semester': row.get('学期', ''),
                        'subject_code': row.get('科目コード', '')
                    }
                    
                    self.master_controller.create_course(course_data)
                    success_count += 1
                    
                except Exception as e:
                    logger.warning(f"行のインポートに失敗: {e}")
                    continue
            
            QMessageBox.information(self, "完了", 
                f"{success_count}件のデータをインポートしました")
            logger.info(f"講座情報CSVインポート完了: {success_count}件")
            
            self.refresh_course_list()
            
        except Exception as e:
            logger.error(f"講座情報CSVインポートに失敗: {e}")
            QMessageBox.critical(self, "エラー", 
                f"講座情報CSVインポートに失敗しました:\n{e}")
    
    def export_logs_to_csv(self):
        """操作ログCSVエクスポート"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "操作ログCSVエクスポート", "", "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            logs = self.log_controller.get_logs(limit=10000)
            
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                writer.writerow(['日時', 'ユーザー', 'PC名', '操作種別', '対象テーブル', '対象レコードID', '詳細'])
                
                for log in logs:
                    writer.writerow([
                        log['timestamp'],
                        log['username'],
                        log['pc_name'],
                        log['operation_type'],
                        log['target_table'],
                        log.get('target_record_id', ''),
                        log.get('operation_detail', '')
                    ])
            
            QMessageBox.information(self, "完了", 
                f"{len(logs)}件のデータをエクスポートしました\n{file_path}")
            logger.info(f"操作ログCSVエクスポート完了: {file_path}")
            
        except Exception as e:
            logger.error(f"操作ログCSVエクスポートに失敗: {e}")
            QMessageBox.critical(self, "エラー", 
                f"操作ログCSVエクスポートに失敗しました:\n{e}")
    
    def refresh_logs(self):
        """操作ログを更新"""
        try:
            logs = self.log_controller.get_logs(limit=100)
            
            self.log_table.setRowCount(0)
            
            for log in logs:
                row = self.log_table.rowCount()
                self.log_table.insertRow(row)
                
                self.log_table.setItem(row, 0, 
                    QTableWidgetItem(log['timestamp'][:19]))
                self.log_table.setItem(row, 1, 
                    QTableWidgetItem(log['username']))
                self.log_table.setItem(row, 2, 
                    QTableWidgetItem(log['pc_name']))
                self.log_table.setItem(row, 3, 
                    QTableWidgetItem(log['operation_type']))
                self.log_table.setItem(row, 4, 
                    QTableWidgetItem(log['target_table']))
                self.log_table.setItem(row, 5, 
                    QTableWidgetItem(log.get('operation_detail', '')))
            
            logger.info(f"{len(logs)}件のログをロードしました")
            
        except Exception as e:
            logger.error(f"ログの更新に失敗: {e}")
            QMessageBox.critical(self, "エラー", 
                f"ログの更新に失敗しました:\n{e}")
