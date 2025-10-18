"""
パスワード入力ダイアログ
システム部管理画面へのアクセス認証
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit
)
from PySide6.QtCore import Qt


class PasswordDialog(QDialog):
    """パスワード入力ダイアログ"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("システム部管理 - 認証")
        self.setModal(True)
        self.resize(350, 150)
        self.setup_ui()
    
    def setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout()
        
        # 説明
        info_label = QLabel("システム部管理画面にアクセスするには\nパスワードを入力してください")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # パスワード入力
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("パスワード:"))
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.returnPressed.connect(self.accept)
        password_layout.addWidget(self.password_edit)
        
        layout.addLayout(password_layout)
        
        # ボタン
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setDefault(True)
        
        cancel_btn = QPushButton("キャンセル")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # フォーカスをパスワード入力に
        self.password_edit.setFocus()
    
    def get_password(self) -> str:
        """入力されたパスワードを取得"""
        return self.password_edit.text()
