"""
確認ダイアログ
訂正依頼の内容を確認してから登録
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QFormLayout, QDialogButtonBox
)
from PySide6.QtCore import Qt
from typing import Dict, Any


class ConfirmationDialog(QDialog):
    """訂正内容確認ダイアログ"""
    
    def __init__(self, correction_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.correction_data = correction_data
        self.setWindowTitle("訂正内容の確認")
        self.setModal(True)
        self.setup_ui()
        
    def setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout()
        
        # タイトル
        title = QLabel("以下の内容で訂正依頼を登録します。よろしいですか？")
        title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title)
        
        # 訂正内容表示
        info_group = QGroupBox("訂正内容")
        form_layout = QFormLayout()
        
        form_layout.addRow("依頼種別:", 
            QLabel(self.correction_data.get('request_type', '')))
        form_layout.addRow("生徒名:", 
            QLabel(self.correction_data.get('student_name', '')))
        form_layout.addRow("講座名:", 
            QLabel(self.correction_data.get('course_name', '')))
        
        # 出欠訂正の場合は対象日付を表示
        if self.correction_data.get('target_date'):
            form_layout.addRow("対象日付:", 
                QLabel(self.correction_data['target_date']))
        
        # 評価評定変更の場合は学期を表示
        if self.correction_data.get('semester'):
            form_layout.addRow("学期:", 
                QLabel(str(self.correction_data['semester'])))
        
        if self.correction_data.get('before_value'):
            form_layout.addRow("訂正前:", 
                QLabel(self.correction_data['before_value']))
        
        form_layout.addRow("訂正後:", 
            QLabel(self.correction_data.get('after_value', '')))
        form_layout.addRow("理由:", 
            QLabel(self.correction_data.get('reason', '')))
        
        info_group.setLayout(form_layout)
        layout.addWidget(info_group)
        
        # ボタン
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.button(QDialogButtonBox.Ok).setText("登録")
        button_box.button(QDialogButtonBox.Cancel).setText("キャンセル")
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        self.setMinimumWidth(400)
