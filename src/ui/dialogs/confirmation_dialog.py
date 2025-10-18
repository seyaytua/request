"""
確認ダイアログ
訂正依頼の内容を確認して登録
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTextEdit
)
from PySide6.QtCore import Qt
from typing import Dict, Any

from ...config import COLOR_ATTENDANCE, COLOR_GRADE


class ConfirmationDialog(QDialog):
    """確認ダイアログ"""
    
    def __init__(self, correction_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.correction_data = correction_data
        self.setWindowTitle("訂正依頼の確認")
        self.resize(500, 400)
        self.setup_ui()
    
    def setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout()
        
        # 背景色設定
        if self.correction_data['request_type'] == '出欠訂正':
            bg_color = COLOR_ATTENDANCE
        else:
            bg_color = COLOR_GRADE
        
        self.setStyleSheet(f"QDialog {{ background-color: {bg_color}; }}")
        
        # タイトル
        title = QLabel(f"【{self.correction_data['request_type']}】")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # 内容表示
        content = self._format_content()
        content_edit = QTextEdit()
        content_edit.setPlainText(content)
        content_edit.setReadOnly(True)
        layout.addWidget(content_edit)
        
        # ボタン
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton("登録")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setStyleSheet("font-size: 14px; padding: 10px;")
        
        cancel_btn = QPushButton("キャンセル")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("font-size: 14px; padding: 10px;")
        
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def _format_content(self) -> str:
        """内容をフォーマット"""
        lines = []
        lines.append(f"訂正種別: {self.correction_data['request_type']}")
        lines.append(f"依頼者: {self.correction_data['requester']}")
        lines.append("")
        
        if self.correction_data['request_type'] == '出欠訂正':
            lines.append(f"対象日付: {self.correction_data.get('target_date', '')}")
            periods = self.correction_data.get('periods', '').split(',')
            period_text = '、'.join([f"{p}限" for p in periods])
            lines.append(f"校時: {period_text}")
            lines.append(f"訂正前: {self.correction_data.get('before_value', '')}")
            lines.append(f"訂正後: {self.correction_data['after_value']}")
        else:
            lines.append(f"学期: {self.correction_data.get('semester', '')}")
            lines.append(f"訂正前: {self.correction_data.get('before_value', '')}")
            lines.append(f"訂正後: {self.correction_data['after_value']}")
        
        lines.append("")
        lines.append("理由:")
        lines.append(self.correction_data['reason'])
        
        return '\n'.join(lines)
