"""
メインウィンドウ v1.5.0
"""
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QMessageBox, QStatusBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent

from .correction_tab import CorrectionTab
from .notice_tab import NoticeTab
from .admin_tab import AdminTab
from .settings_tab import SettingsTab
from .dialogs.password_dialog import PasswordDialog
from ..database.db_manager import DatabaseManager
from ..database.init_db import initialize_database
from ..controllers.correction_controller import CorrectionController
from ..controllers.log_controller import LogController
from ..controllers.auth_controller import AuthController
from ..controllers.master_controller import MasterController
from ..utils.backup_manager import BackupManager
from ..config import APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, DB_PATH
from ..utils.logger import get_logger
from ..utils.system_info import get_user_identifier

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """メインウィンドウ"""
    
    def __init__(self):
        super().__init__()
        
        self.is_authenticated = False
        
        self.init_database()
        self.init_controllers()
        self.load_app_title()
        
        # 起動時に最大化
        self.showMaximized()
        
        self.setup_ui()
        self.setup_statusbar()
        
        # バックアップチェック
        self.check_backup()
        
        logger.info(f"アプリケーション起動: {get_user_identifier()}")
    
    def init_database(self):
        """データベースを初期化"""
        try:
            if not DB_PATH.exists():
                logger.info("データベースを新規作成します")
                initialize_database(DB_PATH)
            
            self.db = DatabaseManager(DB_PATH)
            logger.info(f"データベース接続: {DB_PATH}")
            
        except Exception as e:
            logger.error(f"データベース初期化エラー: {e}")
            QMessageBox.critical(
                self, "エラー", 
                f"データベースの初期化に失敗しました:\n{e}\n\n"
                "アプリケーションを終了します。"
            )
            raise
    
    def init_controllers(self):
        """コントローラーを初期化"""
        self.log_controller = LogController(self.db)
        self.auth_controller = AuthController(self.db)
        self.correction_controller = CorrectionController(
            self.db, self.log_controller
        )
        self.master_controller = MasterController(
            self.db, self.log_controller
        )
        self.backup_manager = BackupManager()
    
    def load_app_title(self):
        """アプリタイトルを読み込み"""
        try:
            app_title = self.auth_controller.get_setting('app_title')
            if app_title:
                self.setWindowTitle(app_title)
            else:
                self.setWindowTitle(APP_NAME)
        except Exception as e:
            logger.warning(f"アプリタイトルの読み込みに失敗: {e}")
            self.setWindowTitle(APP_NAME)
    
    def setup_ui(self):
        """UIをセットアップ"""
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        self.correction_tab = CorrectionTab(self.correction_controller)
        self.tabs.addTab(self.correction_tab, "📝 訂正入力")
        
        self.notice_tab = NoticeTab(self.auth_controller)
        self.tabs.addTab(self.notice_tab, "📢 お知らせ")
        
        self.admin_tab = AdminTab(
            self.correction_controller,
            self.log_controller,
            self.master_controller
        )
        self.tabs.addTab(self.admin_tab, "🔧 システム部管理")
        
        self.setCentralWidget(self.tabs)
    
    def setup_statusbar(self):
        """ステータスバーをセットアップ"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        user_info = get_user_identifier()
        self.statusbar.showMessage(f"ログイン: {user_info}")
    
    def check_backup(self):
        """バックアップをチェック"""
        try:
            # 起動回数を取得
            launch_count = int(self.auth_controller.get_setting('launch_count') or '0')
            launch_count += 1
            
            # 起動回数を更新
            self.auth_controller.set_setting('launch_count', str(launch_count))
            
            # バックアップ間隔を取得
            backup_interval = int(self.auth_controller.get_setting('backup_interval') or '5')
            
            # バックアップ実行
            if launch_count % backup_interval == 0:
                logger.info(f"バックアップを実行します（起動{launch_count}回目）")
                backup_path = self.backup_manager.create_backup()
                
                if backup_path:
                    self.statusbar.showMessage(f"バックアップを作成しました: {backup_path.name}", 5000)
                    
                    # 古いバックアップを削除
                    self.backup_manager.cleanup_old_backups(keep_count=10)
                else:
                    logger.warning("バックアップの作成に失敗しました")
        
        except Exception as e:
            logger.error(f"バックアップチェックに失敗: {e}")
    
    def on_tab_changed(self, index: int):
        """タブが変更された時"""
        if index == 2:  # システム部管理タブ
            if not self.is_authenticated:
                self.tabs.blockSignals(True)
                self.tabs.setCurrentIndex(0)
                self.tabs.blockSignals(False)
                
                if self.authenticate_admin():
                    self.tabs.setCurrentIndex(2)
                    self.setup_settings_tab()
    
    def authenticate_admin(self) -> bool:
        """管理者認証"""
        dialog = PasswordDialog(self)
        result = dialog.exec()
        
        if result == PasswordDialog.Accepted:
            password = dialog.get_password()
            
            if self.auth_controller.verify_admin_password(password):
                logger.info("管理者認証成功")
                self.is_authenticated = True
                self.statusbar.showMessage("管理者モード", 3000)
                
                self.admin_tab.load_data()
                
                return True
            else:
                QMessageBox.warning(
                    self, "認証失敗", 
                    "パスワードが正しくありません"
                )
                logger.warning("管理者認証失敗")
                return False
        
        return False
    
    def setup_settings_tab(self):
        """設定タブをセットアップ"""
        if not hasattr(self.admin_tab, 'settings_tab_added'):
            settings_tab = SettingsTab(self.auth_controller, self.backup_manager)
            settings_tab.title_changed.connect(self.on_title_changed)
            settings_tab.notice_changed.connect(self.on_notice_changed)
            
            self.admin_tab.tabs.addTab(settings_tab, "⚙️ 設定")
            self.admin_tab.settings_tab_added = True
    
    def on_title_changed(self, new_title: str):
        """タイトル変更時"""
        self.setWindowTitle(new_title)
    
    def on_notice_changed(self):
        """お知らせ変更時"""
        self.notice_tab.load_notice()
    
    def closeEvent(self, event: QCloseEvent):
        """ウィンドウを閉じる時"""
        reply = QMessageBox.question(
            self, "確認", 
            "アプリケーションを終了しますか？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            logger.info("アプリケーション終了")
            event.accept()
        else:
            event.ignore()
