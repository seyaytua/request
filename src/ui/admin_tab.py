"""
システム部管理タブ
ロック解除とログビューア
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMessageBox, QLabel, QGroupBox
)
from PySide6.QtCore import Qt

from ..controllers.correction_controller import CorrectionController
from ..controllers.log_controller import LogController
from ..utils.logger import get_logger

logger = get_logger(__name__)


class AdminTab(QWidget):
    """システム部管理タブ"""
    
    def __init__(
        self, 
        correction_controller: CorrectionController,
        log_controller: LogController,
        parent=None
    ):
        super().__init__(parent)
        self.correction_controller = correction_controller
        self.log_controller = log_controller
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout()
        
        # ロック管理エリア
        lock_group = QGroupBox("ロック管理")
        lock_layout = QVBoxLayout()
        
        # ボタンエリア
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("更新")
        refresh_btn.clicked.connect(self.refresh_locked_list)
        button_layout.addWidget(refresh_btn)
        
        unlock_btn = QPushButton("🔓 選択したロックを解除")
        unlock_btn.clicked.connect(self.unlock_selected)
        button_layout.addWidget(unlock_btn)
        
        button_layout.addStretch()
        lock_layout.addLayout(button_layout)
        
        # ロックされた訂正依頼リスト
        self.locked_table = QTableWidget()
        self.locked_table.setColumnCount(6)
        self.locked_table.setHorizontalHeaderLabels([
            "ID", "種別", "生徒名", "講座名", "ロック者", "ロック日時"
        ])
        self.locked_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.locked_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        header = self.locked_table.horizontalHeader()
        header.setStretchLastSection(True)
        
        lock_layout.addWidget(self.locked_table)
        lock_group.setLayout(lock_layout)
        
        layout.addWidget(lock_group)
        
        # 操作ログエリア
        log_group = QGroupBox("操作ログ")
        log_layout = QVBoxLayout()
        
        log_button_layout = QHBoxLayout()
        refresh_log_btn = QPushButton("ログ更新")
        refresh_log_btn.clicked.connect(self.refresh_logs)
        log_button_layout.addWidget(refresh_log_btn)
        log_button_layout.addStretch()
        
        log_layout.addLayout(log_button_layout)
        
        # ログテーブル
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(6)
        self.log_table.setHorizontalHeaderLabels([
            "日時", "ユーザー", "PC名", "操作種別", "対象テーブル", "詳細"
        ])
        self.log_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.log_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        log_header = self.log_table.horizontalHeader()
        log_header.setStretchLastSection(True)
        
        log_layout.addWidget(self.log_table)
        log_group.setLayout(log_layout)
        
        layout.addWidget(log_group)
        
        self.setLayout(layout)
    
    def load_data(self):
        """データをロード"""
        self.refresh_locked_list()
        self.refresh_logs()
    
    def refresh_locked_list(self):
        """ロックされた訂正依頼リストを更新"""
        try:
            locked_corrections = self.correction_controller.get_corrections(
                is_locked=True, limit=1000
            )
            
            self.locked_table.setRowCount(0)
            
            for correction in locked_corrections:
                row = self.locked_table.rowCount()
                self.locked_table.insertRow(row)
                
                self.locked_table.setItem(row, 0, 
                    QTableWidgetItem(str(correction['correction_id'])))
                self.locked_table.setItem(row, 1, 
                    QTableWidgetItem(correction['request_type']))
                self.locked_table.setItem(row, 2, 
                    QTableWidgetItem(correction.get('student_name', '')))
                self.locked_table.setItem(row, 3, 
                    QTableWidgetItem(correction.get('course_name', '')))
                self.locked_table.setItem(row, 4, 
                    QTableWidgetItem(correction.get('locked_by', '')))
                self.locked_table.setItem(row, 5, 
                    QTableWidgetItem(correction.get('locked_datetime', '')[:16] 
                                   if correction.get('locked_datetime') else ''))
            
            logger.info(f"{len(locked_corrections)}件のロック済み訂正依頼をロードしました")
            
        except Exception as e:
            logger.error(f"ロックリストの更新に失敗: {e}")
            QMessageBox.critical(self, "エラー", 
                f"ロックリストの更新に失敗しました:\n{e}")
    
    def unlock_selected(self):
        """選択された訂正依頼のロックを解除"""
        selected_items = self.locked_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "ロック解除する項目を選択してください")
            return
        
        row = selected_items[0].row()
        correction_id = int(self.locked_table.item(row, 0).text())
        
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
                    self.refresh_locked_list()
                    self.refresh_logs()
                else:
                    QMessageBox.warning(self, "失敗", "ロックの解除に失敗しました")
                    
            except Exception as e:
                logger.error(f"ロック解除に失敗: {e}")
                QMessageBox.critical(self, "エラー", 
                    f"ロック解除に失敗しました:\n{e}")
    
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
