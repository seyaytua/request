"""
訂正依頼リストウィジェット
訂正依頼の一覧表示と操作
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QComboBox, QLineEdit, QLabel,
    QMessageBox
)
from PySide6.QtCore import Qt, Signal
from typing import List, Dict, Any

from ...config import REQUEST_TYPES, REQUEST_STATUS
from ...utils.logger import get_logger

logger = get_logger(__name__)


class CorrectionListWidget(QWidget):
    """訂正依頼リストウィジェット"""
    
    refresh_requested = Signal()
    edit_requested = Signal(int)
    delete_requested = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.corrections = []
        self.setup_ui()
    
    def setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout()
        
        # フィルタエリア
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("種別:"))
        self.type_filter = QComboBox()
        self.type_filter.addItem("全て", None)
        self.type_filter.addItem("出欠訂正", REQUEST_TYPES['ATTENDANCE'])
        self.type_filter.addItem("評価評定変更", REQUEST_TYPES['GRADE'])
        self.type_filter.currentIndexChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.type_filter)
        
        filter_layout.addWidget(QLabel("状態:"))
        self.status_filter = QComboBox()
        self.status_filter.addItem("全て", None)
        for status in REQUEST_STATUS.values():
            self.status_filter.addItem(status, status)
        self.status_filter.currentIndexChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.status_filter)
        
        filter_layout.addWidget(QLabel("検索:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("生徒名・講座名で検索")
        self.search_input.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.search_input)
        
        refresh_btn = QPushButton("🔄 更新")
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        filter_layout.addWidget(refresh_btn)
        
        layout.addLayout(filter_layout)
        
        # 操作ボタン
        action_layout = QHBoxLayout()
        
        edit_btn = QPushButton("✏️ 編集")
        edit_btn.clicked.connect(self.on_edit_clicked)
        action_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️ 削除")
        delete_btn.clicked.connect(self.on_delete_clicked)
        action_layout.addWidget(delete_btn)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        # テーブル
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "種別", "生徒名", "組番号", "講座名", 
            "対象日付/学期", "理由", "状態", "ロック"
        ])
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_corrections(self, corrections: List[Dict[str, Any]]):
        """訂正依頼をロード"""
        self.corrections = corrections
        self.apply_filters()
    
    def apply_filters(self):
        """フィルタを適用"""
        type_filter = self.type_filter.currentData()
        status_filter = self.status_filter.currentData()
        search_text = self.search_input.text().lower()
        
        self.table.setRowCount(0)
        
        for correction in self.corrections:
            # フィルタ適用
            if type_filter and correction['request_type'] != type_filter:
                continue
            
            if status_filter and correction['status'] != status_filter:
                continue
            
            if search_text:
                student_name = correction.get('student_name', '').lower()
                course_name = correction.get('course_name', '').lower()
                if search_text not in student_name and search_text not in course_name:
                    continue
            
            # 行を追加
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(correction['correction_id'])))
            self.table.setItem(row, 1, QTableWidgetItem(correction['request_type']))
            self.table.setItem(row, 2, QTableWidgetItem(correction.get('student_name', '')))
            self.table.setItem(row, 3, QTableWidgetItem(correction.get('class_number', '')))
            self.table.setItem(row, 4, QTableWidgetItem(correction.get('course_name', '')))
            
            # 対象日付/学期
            target = correction.get('target_date') or correction.get('semester', '')
            self.table.setItem(row, 5, QTableWidgetItem(target))
            
            self.table.setItem(row, 6, QTableWidgetItem(correction.get('reason', '')[:30] + '...'))
            self.table.setItem(row, 7, QTableWidgetItem(correction['status']))
            
            lock_status = "🔒" if correction['is_locked'] else ""
            self.table.setItem(row, 8, QTableWidgetItem(lock_status))
    
    def get_selected_correction_id(self) -> int:
        """選択された訂正依頼IDを取得"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return None
        
        row = selected_items[0].row()
        return int(self.table.item(row, 0).text())
    
    def get_selected_correction(self) -> Dict[str, Any]:
        """選択された訂正依頼を取得"""
        correction_id = self.get_selected_correction_id()
        if not correction_id:
            return None
        
        for correction in self.corrections:
            if correction['correction_id'] == correction_id:
                return correction
        
        return None
    
    def on_edit_clicked(self):
        """編集ボタンがクリックされた時"""
        correction = self.get_selected_correction()
        if not correction:
            QMessageBox.warning(self, "警告", "編集する項目を選択してください")
            return
        
        if correction['is_locked']:
            QMessageBox.warning(self, "警告", "ロックされた訂正依頼は編集できません")
            return
        
        self.edit_requested.emit(correction['correction_id'])
    
    def on_delete_clicked(self):
        """削除ボタンがクリックされた時"""
        correction = self.get_selected_correction()
        if not correction:
            QMessageBox.warning(self, "警告", "削除する項目を選択してください")
            return
        
        if correction['is_locked']:
            QMessageBox.warning(self, "警告", "ロックされた訂正依頼は削除できません")
            return
        
        self.delete_requested.emit(correction['correction_id'])
