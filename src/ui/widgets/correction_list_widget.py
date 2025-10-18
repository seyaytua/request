"""
訂正依頼リストウィジェット v1.5.0
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QLineEdit, QComboBox, QLabel
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from ...config import COLOR_ATTENDANCE, COLOR_GRADE
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
        
        # 検索・フィルタエリア
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("検索:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("生徒名（ひらがな可）・講座名で検索...")
        self.search_edit.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.search_edit)
        
        filter_layout.addWidget(QLabel("種別:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["全て", "出欠訂正", "評価評定変更"])
        self.type_combo.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.type_combo)
        
        filter_layout.addWidget(QLabel("ロック:"))
        self.lock_combo = QComboBox()
        self.lock_combo.addItems(["全て", "ロック済み", "未ロック"])
        self.lock_combo.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.lock_combo)
        
        layout.addLayout(filter_layout)
        
        # テーブル
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "種別", "生徒名", "講座名", "日時・学期", "訂正内容", "ロック"
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        for i in range(7):
            if i == 5:
                header.setSectionResizeMode(i, QHeaderView.Stretch)
            else:
                header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
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
        
        export_btn = QPushButton("📤 CSV出力")
        export_btn.clicked.connect(self.export_requested.emit)
        button_layout.addWidget(export_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_corrections(self, corrections: list):
        """訂正依頼をロード"""
        self.corrections = corrections
        self.apply_filters()
    
    def apply_filters(self):
        """フィルタを適用"""
        search_text = self.search_edit.text().lower()
        type_filter = self.type_combo.currentText()
        lock_filter = self.lock_combo.currentText()
        
        filtered = []
        for correction in self.corrections:
            # 種別フィルタ
            if type_filter != "全て" and correction['request_type'] != type_filter:
                continue
            
            # ロックフィルタ
            if lock_filter == "ロック済み" and not correction['is_locked']:
                continue
            if lock_filter == "未ロック" and correction['is_locked']:
                continue
            
            # 検索フィルタ（生徒名・ふりがな・講座名）
            if search_text:
                student_name = correction.get('student_name', '').lower()
                student_kana = correction.get('name_kana', '').lower()
                course_name = correction.get('course_name', '').lower()
                
                if (search_text not in student_name and 
                    search_text not in student_kana and 
                    search_text not in course_name):
                    continue
            
            filtered.append(correction)
        
        self.display_corrections(filtered)
    
    def display_corrections(self, corrections: list):
        """訂正依頼を表示"""
        self.table.setRowCount(0)
        
        for correction in corrections:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(correction['correction_id'])))
            
            type_item = QTableWidgetItem(correction['request_type'])
            if correction['request_type'] == '出欠訂正':
                type_item.setBackground(QColor(COLOR_ATTENDANCE))
            else:
                type_item.setBackground(QColor(COLOR_GRADE))
            self.table.setItem(row, 1, type_item)
            
            self.table.setItem(row, 2, QTableWidgetItem(correction.get('student_name', '')))
            self.table.setItem(row, 3, QTableWidgetItem(correction.get('course_name', '')))
            
            date_semester = ""
            if correction.get('target_date'):
                date_semester = correction['target_date']
            if correction.get('semester'):
                if date_semester:
                    date_semester += f" / {correction['semester']}"
                else:
                    date_semester = correction['semester']
            self.table.setItem(row, 4, QTableWidgetItem(date_semester))
            
            content = ""
            if correction.get('before_value'):
                content = f"{correction['before_value']} → {correction['after_value']}"
            else:
                content = correction['after_value']
            self.table.setItem(row, 5, QTableWidgetItem(content))
            
            lock_text = "🔒" if correction['is_locked'] else ""
            self.table.setItem(row, 6, QTableWidgetItem(lock_text))
    
    def on_view_clicked(self):
        """表示ボタンがクリックされた"""
        selected_items = self.table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            correction_id = int(self.table.item(row, 0).text())
            self.view_requested.emit(correction_id)
    
    def on_delete_clicked(self):
        """削除ボタンがクリックされた"""
        selected_items = self.table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            correction_id = int(self.table.item(row, 0).text())
            self.delete_requested.emit(correction_id)
