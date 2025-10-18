"""
訂正依頼リストウィジェット v1.4.0
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView,
    QLineEdit, QComboBox, QPushButton, QLabel
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from ...config import REQUEST_TYPES, COLOR_ATTENDANCE, COLOR_GRADE
from ...utils.logger import get_logger

logger = get_logger(__name__)


class CorrectionListWidget(QWidget):
    """訂正依頼リストウィジェット"""
    
    refresh_requested = Signal()
    view_requested = Signal(int)
    delete_requested = Signal(int)
    export_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.corrections = []
        self.setup_ui()
    
    def setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout()
        
        # フィルタエリア
        filter_layout = QHBoxLayout()
        
        # 検索ボックス
        filter_layout.addWidget(QLabel("検索:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("生徒名、講座名で検索...")
        self.search_edit.textChanged.connect(self.filter_corrections)
        filter_layout.addWidget(self.search_edit)
        
        # 種別フィルタ
        filter_layout.addWidget(QLabel("種別:"))
        self.type_combo = QComboBox()
        self.type_combo.addItem("全て", None)
        for type_name in REQUEST_TYPES.values():
            self.type_combo.addItem(type_name, type_name)
        self.type_combo.currentIndexChanged.connect(self.filter_corrections)
        filter_layout.addWidget(self.type_combo)
        
        # ロックフィルタ
        filter_layout.addWidget(QLabel("ロック:"))
        self.lock_combo = QComboBox()
        self.lock_combo.addItem("全て", None)
        self.lock_combo.addItem("ロック済み", True)
        self.lock_combo.addItem("未ロック", False)
        self.lock_combo.currentIndexChanged.connect(self.filter_corrections)
        filter_layout.addWidget(self.lock_combo)
        
        layout.addLayout(filter_layout)
        
        # テーブル
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "種別", "生徒名", "組番号", "講座名", 
            "訂正内容", "理由", "依頼者", "ロック"
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        
        layout.addWidget(self.table)
        
        # ボタンエリア
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 更新")
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        button_layout.addWidget(refresh_btn)
        
        view_btn = QPushButton("👁️ 表示")
        view_btn.clicked.connect(self.on_view_clicked)
        button_layout.addWidget(view_btn)
        
        delete_btn = QPushButton("🗑️ 削除")
        delete_btn.clicked.connect(self.on_delete_clicked)
        button_layout.addWidget(delete_btn)
        
        export_btn = QPushButton("📤 エクスポート")
        export_btn.clicked.connect(self.export_requested.emit)
        button_layout.addWidget(export_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_corrections(self, corrections: list):
        """訂正依頼をロード"""
        self.corrections = corrections
        self.filter_corrections()
    
    def filter_corrections(self):
        """フィルタを適用"""
        search_text = self.search_edit.text().lower()
        request_type = self.type_combo.currentData()
        is_locked = self.lock_combo.currentData()
        
        self.table.setRowCount(0)
        
        for correction in self.corrections:
            # フィルタ条件チェック
            if request_type and correction['request_type'] != request_type:
                continue
            
            if is_locked is not None and correction['is_locked'] != is_locked:
                continue
            
            if search_text:
                student_name = correction.get('student_name', '').lower()
                course_name = correction.get('course_name', '').lower()
                if search_text not in student_name and search_text not in course_name:
                    continue
            
            # テーブルに追加
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # 背景色設定
            if correction['request_type'] == "出欠訂正":
                bg_color = QColor(COLOR_ATTENDANCE)
            else:
                bg_color = QColor(COLOR_GRADE)
            
            # データ設定
            id_item = QTableWidgetItem(str(correction['correction_id']))
            id_item.setBackground(bg_color)
            self.table.setItem(row, 0, id_item)
            
            type_item = QTableWidgetItem(correction['request_type'])
            type_item.setBackground(bg_color)
            self.table.setItem(row, 1, type_item)
            
            self.table.setItem(row, 2, QTableWidgetItem(correction.get('student_name', '')))
            self.table.setItem(row, 3, QTableWidgetItem(correction.get('class_number', '')))
            self.table.setItem(row, 4, QTableWidgetItem(correction.get('course_name', '')))
            
            correction_text = f"{correction.get('before_value', '')} → {correction.get('after_value', '')}"
            self.table.setItem(row, 5, QTableWidgetItem(correction_text))
            
            reason = correction.get('reason', '')[:50]
            if len(correction.get('reason', '')) > 50:
                reason += '...'
            self.table.setItem(row, 6, QTableWidgetItem(reason))
            
            self.table.setItem(row, 7, QTableWidgetItem(correction.get('requester_name', '')))
            
            lock_text = f"🔒 {correction.get('locked_by', '')}" if correction['is_locked'] else ""
            self.table.setItem(row, 8, QTableWidgetItem(lock_text))
    
    def on_view_clicked(self):
        """表示ボタンクリック"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        correction_id = int(self.table.item(row, 0).text())
        self.view_requested.emit(correction_id)
    
    def on_delete_clicked(self):
        """削除ボタンクリック"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        correction_id = int(self.table.item(row, 0).text())
        self.delete_requested.emit(correction_id)
