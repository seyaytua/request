"""
訂正依頼リストウィジェット
左側65%に表示される訂正依頼の一覧
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QComboBox, QLabel,
    QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal
from typing import List, Dict, Any


class CorrectionListWidget(QWidget):
    """訂正依頼リストウィジェット"""
    
    # シグナル定義
    correction_selected = Signal(int)  # 訂正依頼が選択された時
    refresh_requested = Signal()  # リフレッシュボタンが押された時
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.corrections = []
        self.setup_ui()
        
    def setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout()
        
        # フィルタエリア
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("ステータス:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["すべて", "未処理", "処理中", "完了"])
        self.status_filter.currentTextChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.status_filter)
        
        filter_layout.addWidget(QLabel("種別:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems(["すべて", "出欠訂正", "評価評定変更"])
        self.type_filter.currentTextChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.type_filter)
        
        filter_layout.addStretch()
        
        refresh_button = QPushButton("更新")
        refresh_button.clicked.connect(self.refresh_requested.emit)
        filter_layout.addWidget(refresh_button)
        
        layout.addLayout(filter_layout)
        
        # テーブル
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "種別", "生徒名", "組", "講座名", 
            "ステータス", "依頼日時", "ロック"
        ])
        
        # テーブル設定
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        
        # 列幅調整
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 種別
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # 生徒名
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 組
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # 講座名
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # ステータス
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # 依頼日時
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # ロック
        
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_corrections(self, corrections: List[Dict[str, Any]]):
        """訂正依頼をロード"""
        self.corrections = corrections
        self.update_table()
    
    def update_table(self):
        """テーブルを更新"""
        self.table.setRowCount(0)
        
        # フィルタ適用
        filtered = self._apply_filters()
        
        for correction in filtered:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, 
                QTableWidgetItem(str(correction['correction_id'])))
            self.table.setItem(row, 1, 
                QTableWidgetItem(correction['request_type']))
            self.table.setItem(row, 2, 
                QTableWidgetItem(correction.get('student_name', '')))
            self.table.setItem(row, 3, 
                QTableWidgetItem(correction.get('class_number', '')))
            self.table.setItem(row, 4, 
                QTableWidgetItem(correction.get('course_name', '')))
            self.table.setItem(row, 5, 
                QTableWidgetItem(correction['status']))
            self.table.setItem(row, 6, 
                QTableWidgetItem(correction['request_datetime'][:16]))
            self.table.setItem(row, 7, 
                QTableWidgetItem("🔒" if correction['is_locked'] else ""))
    
    def _apply_filters(self) -> List[Dict[str, Any]]:
        """フィルタを適用"""
        filtered = self.corrections
        
        # ステータスフィルタ
        status = self.status_filter.currentText()
        if status != "すべて":
            filtered = [c for c in filtered if c['status'] == status]
        
        # 種別フィルタ
        req_type = self.type_filter.currentText()
        if req_type != "すべて":
            filtered = [c for c in filtered if c['request_type'] == req_type]
        
        return filtered
    
    def on_filter_changed(self):
        """フィルタが変更された時"""
        self.update_table()
    
    def on_selection_changed(self):
        """選択が変更された時"""
        selected_items = self.table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            correction_id = int(self.table.item(row, 0).text())
            self.correction_selected.emit(correction_id)
    
    def get_selected_correction_id(self) -> int:
        """選択中の訂正依頼IDを取得"""
        selected_items = self.table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            return int(self.table.item(row, 0).text())
        return None
