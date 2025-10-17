"""
パスワード入力ダイアログ
システム部管理画面へのアクセス時に使用
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt


class PasswordDialog(QDialog):
    """パスワード入力ダイアログ"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("システム部管理 - 認証")
        self.setModal(True)
        self.setup_ui()
        
    def setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout()
        
        # 説明ラベル
        label = QLabel("管理者パスワードを入力してください:")
        layout.addWidget(label)
        
        # パスワード入力
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("パスワード")
        self.password_input.returnPressed.connect(self.accept)
        layout.addWidget(self.password_input)
        
        # ボタン
        button_layout = QHBoxLayout()
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        
        cancel_button = QPushButton("キャンセル")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.setFixedWidth(300)
        
        # フォーカスをパスワード入力に
        self.password_input.setFocus()
    
    def get_password(self) -> str:
        """入力されたパスワードを取得"""
        return self.password_input.text()
