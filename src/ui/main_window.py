"""
メインウィンドウ
タブで訂正入力とシステム部管理を切り替え
"""
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QMessageBox, QStatusBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent

from .correction_tab import CorrectionTab
from .admin_tab import AdminTab
from .dialogs.password_dialog import PasswordDialog
from ..database.db_manager import DatabaseManager
from ..database.init_db import initialize_database
from ..controllers.correction_controller import CorrectionController
from ..controllers.log_controller import LogController
from ..controllers.auth_controller import AuthController
from ..config import APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, DB_PATH
from ..utils.logger import get_logger
from ..utils.system_info import get_user_identifier

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """メインウィンドウ"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)  # バージョン表記を削除
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # 認証済みフラグ
        self.is_authenticated = False
        
        # データベース初期化
        self.init_database()
        
        # コントローラー初期化
        self.init_controllers()
        
        # UI構築
        self.setup_ui()
        
        # ステータスバー
        self.setup_statusbar()
        
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
    
    def setup_ui(self):
        """UIをセットアップ"""
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # 訂正入力タブ
        self.correction_tab = CorrectionTab(self.correction_controller)
        self.tabs.addTab(self.correction_tab, "📝 訂正入力")
        
        # システム部管理タブ
        self.admin_tab = AdminTab(
            self.correction_controller,
            self.log_controller
        )
        self.tabs.addTab(self.admin_tab, "🔧 システム部管理")
        
        self.setCentralWidget(self.tabs)
    
    def setup_statusbar(self):
        """ステータスバーをセットアップ"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        user_info = get_user_identifier()
        self.statusbar.showMessage(f"ログイン: {user_info}")
    
    def on_tab_changed(self, index: int):
        """タブが変更された時"""
        if index == 1:  # システム部管理タブ
            if not self.is_authenticated:
                # 訂正入力タブに戻す
                self.tabs.blockSignals(True)
                self.tabs.setCurrentIndex(0)
                self.tabs.blockSignals(False)
                
                # 認証ダイアログを表示
                if self.authenticate_admin():
                    # 認証成功したらシステム部管理タブに遷移
                    self.tabs.setCurrentIndex(1)
    
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
                
                # 管理タブのデータを更新
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
