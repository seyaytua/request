"""
確認ダイアログ v1.5.0
訂正依頼の内容を確認してから登録
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel
)
from PySide6.QtCore import Qt

from ...config import COLOR_ATTENDANCE, COLOR_GRADE


class ConfirmationDialog(QDialog):
    """訂正依頼の確認ダイアログ"""
    
    def __init__(self, correction_data: dict, parent=None):
        super().__init__(parent)
        self.correction_data = correction_data
        self.setWindowTitle("訂正依頼の確認")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self.setup_ui()
    
    def setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout()
        
        # タイトル
        request_type = self.correction_data['request_type']
        title_label = QLabel(f"【{request_type}】")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        
        # 背景色を設定
        if request_type == '出欠訂正':
            title_label.setStyleSheet(f"""
                font-size: 18px; 
                font-weight: bold; 
                padding: 10px;
                background-color: {COLOR_ATTENDANCE};
            """)
        else:
            title_label.setStyleSheet(f"""
                font-size: 18px; 
                font-weight: bold; 
                padding: 10px;
                background-color: {COLOR_GRADE};
            """)
        
        layout.addWidget(title_label)
        
        # 確認内容
        content = QTextEdit()
        content.setReadOnly(True)
        content.setStyleSheet("font-size: 14px; padding: 10px;")
        
        # 内容を整形
        text_parts = []
        
        # 基本情報
        text_parts.append(f"訂正種別: {request_type}")
        text_parts.append(f"依頼者: {self.correction_data['requester']}")
        text_parts.append("")
        
        # 生徒情報
        student_name = self.correction_data.get('student_name', '不明')
        class_number = self.correction_data.get('class_number', '')
        text_parts.append(f"生徒: {student_name}")
        if class_number:
            text_parts.append(f"組番号: {class_number}")
        text_parts.append("")
        
        # 講座情報
        course_name = self.correction_data.get('course_name', '不明')
        teacher_name = self.correction_data.get('teacher_name', '')
        text_parts.append(f"講座: {course_name}")
        if teacher_name:
            text_parts.append(f"担当教員: {teacher_name}")
        text_parts.append("")
        
        # 訂正詳細
        if request_type == '出欠訂正':
            target_date = self.correction_data.get('target_date', '')
            periods = self.correction_data.get('periods', '')
            
            if target_date:
                text_parts.append(f"対象日付: {target_date}")
            if periods:
                text_parts.append(f"校時: {periods}")
        else:  # 評価評定変更
            semester = self.correction_data.get('semester', '')
            if semester:
                text_parts.append(f"学期: {semester}")
        
        text_parts.append("")
        
        # 訂正内容
        before_value = self.correction_data.get('before_value', '')
        after_value = self.correction_data.get('after_value', '')
        
        if before_value:
            text_parts.append(f"訂正前: {before_value}")
        text_parts.append(f"訂正後: {after_value}")
        text_parts.append("")
        
        # 理由
        reason = self.correction_data.get('reason', '')
        text_parts.append("理由:")
        text_parts.append(reason)
        
        content.setPlainText("\n".join(text_parts))
        layout.addWidget(content)
        
        # ボタン
        button_layout = QHBoxLayout()
        
        register_btn = QPushButton("登録")
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        register_btn.clicked.connect(self.accept)
        button_layout.addWidget(register_btn)
        
        cancel_btn = QPushButton("キャンセル")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
