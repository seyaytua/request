"""
認証コントローラー
システム部管理画面のパスワード認証を管理
"""
from typing import Optional

from ..database.db_manager import DatabaseManager
from ..utils.password_hash import hash_password, verify_password
from ..utils.logger import get_logger

logger = get_logger(__name__)


class AuthController:
    """認証を管理するコントローラー"""
    
    def __init__(self, db: DatabaseManager):
        """
        初期化
        
        Args:
            db: DatabaseManagerインスタンス
        """
        self.db = db
    
    def verify_admin_password(self, password: str) -> bool:
        """
        管理者パスワードを検証
        
        Args:
            password: 入力されたパスワード
            
        Returns:
            パスワードが正しければTrue
        """
        stored_hash = self._get_admin_password_hash()
        
        if not stored_hash:
            logger.error("管理者パスワードが設定されていません")
            return False
        
        is_valid = verify_password(password, stored_hash)
        
        if is_valid:
            logger.info("管理者認証成功")
        else:
            logger.warning("管理者認証失敗")
        
        return is_valid
    
    def change_admin_password(self, old_password: str, new_password: str) -> bool:
        """
        管理者パスワードを変更
        
        Args:
            old_password: 現在のパスワード
            new_password: 新しいパスワード
            
        Returns:
            変更成功したらTrue
        """
        # 現在のパスワードを検証
        if not self.verify_admin_password(old_password):
            logger.warning("パスワード変更失敗: 現在のパスワードが間違っています")
            return False
        
        # 新しいパスワードをハッシュ化
        new_hash = hash_password(new_password)
        
        # データベース更新
        self.db.execute_update(
            """
            UPDATE system_settings
            SET setting_value = ?, updated_at = CURRENT_TIMESTAMP
            WHERE setting_key = 'admin_password_hash'
            """,
            (new_hash,)
        )
        
        logger.info("管理者パスワードを変更しました")
        return True
    
    def _get_admin_password_hash(self) -> Optional[str]:
        """
        管理者パスワードのハッシュ値を取得
        
        Returns:
            ハッシュ値
        """
        rows = self.db.execute_query(
            """
            SELECT setting_value FROM system_settings
            WHERE setting_key = 'admin_password_hash'
            """
        )
        return rows[0]['setting_value'] if rows else None
    
    def get_setting(self, key: str) -> Optional[str]:
        """
        システム設定を取得
        
        Args:
            key: 設定キー
            
        Returns:
            設定値
        """
        rows = self.db.execute_query(
            "SELECT setting_value FROM system_settings WHERE setting_key = ?",
            (key,)
        )
        return rows[0]['setting_value'] if rows else None
    
    def set_setting(self, key: str, value: str) -> None:
        """
        システム設定を保存
        
        Args:
            key: 設定キー
            value: 設定値
        """
        self.db.execute_update(
            """
            INSERT OR REPLACE INTO system_settings (setting_key, setting_value)
            VALUES (?, ?)
            """,
            (key, value)
        )
        logger.info(f"設定を保存しました: {key}")
