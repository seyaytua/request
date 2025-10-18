"""
お知らせタブ
システムからのお知らせを表示
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLabel
)
from PySide6.QtCore import Qt

from ..controllers.auth_controller import AuthController
from ..utils.logger import get_logger

logger = get_logger(__name__)


class NoticeTab(QWidget):
    """お知らせタブ"""
    
    def __init__(self, auth_controller: AuthController, parent=None):
        super().__init__(parent)
        self.auth_controller = auth_controller
        self.setup_ui()
        self.load_notice()
    
    def setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout()
        
        # タイトル
        title_label = QLabel("📢 お知らせ")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title_label)
        
        # お知らせ内容
        self.notice_text = QTextEdit()
        self.notice_text.setReadOnly(True)
        self.notice_text.setStyleSheet("""
            QTextEdit {
                background-color: #FFFEF0;
                border: 2px solid #FFD700;
                border-radius: 5px;
                padding: 15px;
                font-size: 14px;
                line-height: 1.6;
            }
        """)
        layout.addWidget(self.notice_text)
        
        self.setLayout(layout)
    
    def load_notice(self):
        """お知らせを読み込み"""
        try:
            message = self.auth_controller.get_setting('notice_message')
            if message:
                self.notice_text.setPlainText(message)
            else:
                from ..config import DEFAULT_NOTICE_MESSAGE
                self.notice_text.setPlainText(DEFAULT_NOTICE_MESSAGE)
            
            logger.info("お知らせを読み込みました")
            
        except Exception as e:
            logger.error(f"お知らせの読み込みに失敗: {e}")
            self.notice_text.setPlainText("お知らせの読み込みに失敗しました。")
