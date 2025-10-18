"""
訂正入力タブ v1.4.0
左65%にリスト、右35%に入力フォーム
"""
import csv
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QSplitter, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt

from .widgets.correction_list_widget import CorrectionListWidget
from .widgets.correction_input_widget import CorrectionInputWidget
from .dialogs.confirmation_dialog import ConfirmationDialog
from .dialogs.view_dialog import ViewDialog
from ..controllers.correction_controller import CorrectionController
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CorrectionTab(QWidget):
    """訂正入力タブ"""
    
    def __init__(self, correction_controller: CorrectionController, parent=None):
        super().__init__(parent)
        self.controller = correction_controller
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """UIをセットアップ"""
        layout = QHBoxLayout()
        
        splitter = QSplitter(Qt.Horizontal)
        
        self.list_widget = CorrectionListWidget()
        self.list_widget.refresh_requested.connect(self.refresh_list)
        self.list_widget.view_requested.connect(self.on_view_correction)
        self.list_widget.delete_requested.connect(self.on_delete_correction)
        self.list_widget.export_requested.connect(self.on_export_corrections)
        
        self.input_widget = CorrectionInputWidget()
        self.input_widget.submit_requested.connect(self.on_submit_corrections)
        
        splitter.addWidget(self.list_widget)
        splitter.addWidget(self.input_widget)
        
        splitter.setStretchFactor(0, 65)
        splitter.setStretchFactor(1, 35)
        
        layout.addWidget(splitter)
        self.setLayout(layout)
    
    def load_data(self):
        """データをロード"""
        try:
            students = self.controller.get_students(year=2024)
            courses = self.controller.get_courses(year=2024)
            
            self.input_widget.set_students(students)
            self.input_widget.set_courses(courses)
            
            self.refresh_list()
            
            logger.info("データをロードしました")
            
        except Exception as e:
            logger.error(f"データのロードに失敗: {e}")
            QMessageBox.critical(self, "エラー", 
                f"データのロードに失敗しました:\n{e}")
    
    def refresh_list(self):
        """訂正依頼リストを更新"""
        try:
            corrections = self.controller.get_corrections(limit=1000)
            self.list_widget.load_corrections(corrections)
            logger.info(f"{len(corrections)}件の訂正依頼をロードしました")
            
        except Exception as e:
            logger.error(f"訂正依頼リストの更新に失敗: {e}")
            QMessageBox.critical(self, "エラー", 
                f"訂正依頼リストの更新に失敗しました:\n{e}")
    
    def on_submit_corrections(self, corrections: list):
        """訂正依頼を送信"""
        success_count = 0
        
        for i, correction_data in enumerate(corrections):
            dialog = ConfirmationDialog(correction_data, self)
            result = dialog.exec()
            
            if result == ConfirmationDialog.Accepted:
                try:
                    correction_id = self.controller.create_correction(correction_data)
                    success_count += 1
                    logger.info(f"訂正依頼を登録しました: ID={correction_id}")
                    
                except Exception as e:
                    logger.error(f"訂正依頼の登録に失敗: {e}")
                    QMessageBox.critical(self, "エラー", 
                        f"訂正依頼の登録に失敗しました:\n{e}")
                    break
            else:
                remaining = len(corrections) - i
                if remaining > 1:
                    reply = QMessageBox.question(
                        self, "確認", 
                        f"残り{remaining}件の訂正をキャンセルしますか？",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if reply == QMessageBox.Yes:
                        break
                else:
                    break
        
        if success_count > 0:
            QMessageBox.information(
                self, "完了", 
                f"{success_count}件の訂正依頼を登録しました"
            )
            
            self.refresh_list()
            self.input_widget.clear_all()
    
    def on_view_correction(self, correction_id: int):
        """訂正依頼を表示/編集"""
        try:
            correction = self.controller.get_correction(correction_id)
            if not correction:
                QMessageBox.warning(self, "エラー", "訂正依頼が見つかりません")
                return
            
            students = self.controller.get_students(year=2024)
            courses = self.controller.get_courses(year=2024)
            
            dialog = ViewDialog(correction, students, courses, self)
            result = dialog.exec()
            
            if result == ViewDialog.Accepted and not correction['is_locked']:
                update_data = dialog.get_data()
                
                success = self.controller.update_correction(correction_id, update_data)
                
                if success:
                    QMessageBox.information(self, "完了", "訂正依頼を更新しました")
                    self.refresh_list()
                else:
                    QMessageBox.warning(self, "失敗", "訂正依頼の更新に失敗しました")
            
        except Exception as e:
            logger.error(f"訂正依頼の表示に失敗: {e}")
            QMessageBox.critical(self, "エラー", 
                f"訂正依頼の表示に失敗しました:\n{e}")
    
    def on_delete_correction(self, correction_id: int):
        """訂正依頼を削除"""
        try:
            correction = self.controller.get_correction(correction_id)
            if not correction:
                QMessageBox.warning(self, "エラー", "訂正依頼が見つかりません")
                return
            
            if correction['is_locked']:
                QMessageBox.warning(self, "エラー", 
                    "ロックされた訂正依頼は削除できません")
                return
            
            reply = QMessageBox.question(
                self, "確認", 
                f"訂正依頼 ID:{correction_id} を削除しますか？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success = self.controller.delete_correction(correction_id)
                
                if success:
                    QMessageBox.information(self, "完了", "訂正依頼を削除しました")
                    self.refresh_list()
                else:
                    QMessageBox.warning(self, "失敗", "訂正依頼の削除に失敗しました")
                    
        except Exception as e:
            logger.error(f"訂正依頼の削除に失敗: {e}")
            QMessageBox.critical(self, "エラー", 
                f"訂正依頼の削除に失敗しました:\n{e}")
    
    def on_export_corrections(self):
        """訂正依頼をCSVエクスポート"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "訂正依頼CSVエクスポート", "", "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            corrections = self.controller.get_corrections(limit=10000)
            
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                writer.writerow([
                    'ID', '種別', '生徒名', '組番号', '講座名', '対象日付', 
                    '学期', '校時', '訂正前', '訂正後', '理由', '依頼者', 
                    'ロック', 'ロック者', '依頼日時'
                ])
                
                for c in corrections:
                    writer.writerow([
                        c['correction_id'],
                        c['request_type'],
                        c.get('student_name', ''),
                        c.get('class_number', ''),
                        c.get('course_name', ''),
                        c.get('target_date', ''),
                        c.get('semester', ''),
                        c.get('periods', ''),
                        c.get('before_value', ''),
                        c.get('after_value', ''),
                        c.get('reason', ''),
                        c.get('requester_name', ''),
                        '○' if c['is_locked'] else '',
                        c.get('locked_by', ''),
                        c.get('request_datetime', '')
                    ])
            
            QMessageBox.information(self, "完了", 
                f"{len(corrections)}件のデータをエクスポートしました\n{file_path}")
            logger.info(f"訂正依頼CSVエクスポート完了: {file_path}")
            
        except Exception as e:
            logger.error(f"訂正依頼CSVエクスポートに失敗: {e}")
            QMessageBox.critical(self, "エラー", 
                f"訂正依頼CSVエクスポートに失敗しました:\n{e}")
