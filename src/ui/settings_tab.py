"""
設定タブ（システム部管理）
パスワード変更、アプリタイトル変更、お知らせ編集
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt, Signal

from ..controllers.auth_controller import AuthController
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SettingsTab(QWidget):
    """設定タブ"""
    
    title_changed = Signal(str)  # タイトル変更シグナル
    notice_changed = Signal()     # お知らせ変更シグナル
    
    def __init__(self, auth_controller: AuthController, parent=None):
        super().__init__(parent)
        self.auth_controller = auth_controller
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout()
        
        # パスワード変更グループ
        password_group = QGroupBox("パスワード変更")
        password_layout = QVBoxLayout()
        
        old_password_layout = QHBoxLayout()
        old_password_layout.addWidget(QLabel("現在のパスワード:"))
        self.old_password_edit = QLineEdit()
        self.old_password_edit.setEchoMode(QLineEdit.Password)
        old_password_layout.addWidget(self.old_password_edit)
        password_layout.addLayout(old_password_layout)
        
        new_password_layout = QHBoxLayout()
        new_password_layout.addWidget(QLabel("新しいパスワード:"))
        self.new_password_edit = QLineEdit()
        self.new_password_edit.setEchoMode(QLineEdit.Password)
        new_password_layout.addWidget(self.new_password_edit)
        password_layout.addLayout(new_password_layout)
        
        confirm_password_layout = QHBoxLayout()
        confirm_password_layout.addWidget(QLabel("パスワード確認:"))
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        confirm_password_layout.addWidget(self.confirm_password_edit)
        password_layout.addLayout(confirm_password_layout)
        
        change_password_btn = QPushButton("パスワードを変更")
        change_password_btn.clicked.connect(self.change_password)
        password_layout.addWidget(change_password_btn)
        
        password_group.setLayout(password_layout)
        layout.addWidget(password_group)
        
        # アプリタイトル変更グループ
        title_group = QGroupBox("アプリケーション設定")
        title_layout = QHBoxLayout()
        
        title_layout.addWidget(QLabel("アプリタイトル:"))
        self.title_edit = QLineEdit()
        title_layout.addWidget(self.title_edit)
        
        save_title_btn = QPushButton("保存")
        save_title_btn.clicked.connect(self.save_title)
        title_layout.addWidget(save_title_btn)
        
        title_group.setLayout(title_layout)
        layout.addWidget(title_group)
        
        # お知らせ編集グループ
        notice_group = QGroupBox("お知らせ編集")
        notice_layout = QVBoxLayout()
        
        self.notice_edit = QTextEdit()
        self.notice_edit.setPlaceholderText("お知らせ内容を入力してください...")
        notice_layout.addWidget(self.notice_edit)
        
        save_notice_btn = QPushButton("お知らせを保存")
        save_notice_btn.clicked.connect(self.save_notice)
        notice_layout.addWidget(save_notice_btn)
        
        notice_group.setLayout(notice_layout)
        layout.addWidget(notice_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def load_settings(self):
        """設定を読み込み"""
        try:
            app_title = self.auth_controller.get_setting('app_title')
            if app_title:
                self.title_edit.setText(app_title)
            
            notice_message = self.auth_controller.get_setting('notice_message')
            if notice_message:
                self.notice_edit.setPlainText(notice_message)
            
            logger.info("設定を読み込みました")
            
        except Exception as e:
            logger.error(f"設定の読み込みに失敗: {e}")
    
    def change_password(self):
        """パスワードを変更"""
        old_password = self.old_password_edit.text()
        new_password = self.new_password_edit.text()
        confirm_password = self.confirm_password_edit.text()
        
        if not old_password or not new_password or not confirm_password:
            QMessageBox.warning(self, "警告", "全てのフィールドを入力してください")
            return
        
        if new_password != confirm_password:
            QMessageBox.warning(self, "警告", "新しいパスワードが一致しません")
            return
        
        if len(new_password) < 6:
            QMessageBox.warning(self, "警告", "パスワードは6文字以上にしてください")
            return
        
        try:
            success = self.auth_controller.change_admin_password(old_password, new_password)
            
            if success:
                QMessageBox.information(self, "完了", "パスワードを変更しました")
                self.old_password_edit.clear()
                self.new_password_edit.clear()
                self.confirm_password_edit.clear()
            else:
                QMessageBox.warning(self, "失敗", "現在のパスワードが正しくありません")
        
        except Exception as e:
            logger.error(f"パスワード変更に失敗: {e}")
            QMessageBox.critical(self, "エラー", f"パスワード変更に失敗しました:\n{e}")
    
    def save_title(self):
        """アプリタイトルを保存"""
        new_title = self.title_edit.text().strip()
        
        if not new_title:
            QMessageBox.warning(self, "警告", "タイトルを入力してください")
            return
        
        try:
            self.auth_controller.set_setting('app_title', new_title)
            QMessageBox.information(self, "完了", "アプリタイトルを変更しました")
            self.title_changed.emit(new_title)
            logger.info(f"アプリタイトルを変更: {new_title}")
        
        except Exception as e:
            logger.error(f"タイトル変更に失敗: {e}")
            QMessageBox.critical(self, "エラー", f"タイトル変更に失敗しました:\n{e}")
    
    def save_notice(self):
        """お知らせを保存"""
        new_notice = self.notice_edit.toPlainText().strip()
        
        if not new_notice:
            QMessageBox.warning(self, "警告", "お知らせ内容を入力してください")
            return
        
        try:
            self.auth_controller.set_setting('notice_message', new_notice)
            QMessageBox.information(self, "完了", "お知らせを保存しました")
            self.notice_changed.emit()
            logger.info("お知らせを更新しました")
        
        except Exception as e:
            logger.error(f"お知らせ保存に失敗: {e}")
            QMessageBox.critical(self, "エラー", f"お知らせ保存に失敗しました:\n{e}")
