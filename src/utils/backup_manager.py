"""
バックアップマネージャー
データベースの定期バックアップを管理
"""
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

from ..config import DB_PATH, BACKUP_DIR
from ..utils.logger import get_logger

logger = get_logger(__name__)


class BackupManager:
    """データベースバックアップを管理"""
    
    def __init__(self, db_path: Path = DB_PATH, backup_dir: Path = BACKUP_DIR):
        self.db_path = db_path
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self) -> Optional[Path]:
        """
        バックアップを作成
        
        Returns:
            バックアップファイルのパス
        """
        try:
            if not self.db_path.exists():
                logger.warning("データベースファイルが存在しません")
                return None
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"corrections_backup_{timestamp}.db"
            backup_path = self.backup_dir / backup_filename
            
            shutil.copy2(self.db_path, backup_path)
            
            logger.info(f"バックアップを作成しました: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"バックアップ作成に失敗: {e}")
            return None
    
    def get_backup_list(self) -> list:
        """
        バックアップファイルのリストを取得
        
        Returns:
            バックアップファイルのリスト（新しい順）
        """
        backups = sorted(
            self.backup_dir.glob("corrections_backup_*.db"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        return backups
    
    def cleanup_old_backups(self, keep_count: int = 10):
        """
        古いバックアップを削除
        
        Args:
            keep_count: 保持するバックアップ数
        """
        backups = self.get_backup_list()
        
        if len(backups) > keep_count:
            for backup in backups[keep_count:]:
                try:
                    backup.unlink()
                    logger.info(f"古いバックアップを削除: {backup}")
                except Exception as e:
                    logger.error(f"バックアップ削除に失敗: {e}")
    
    def restore_backup(self, backup_path: Path) -> bool:
        """
        バックアップから復元
        
        Args:
            backup_path: 復元するバックアップファイルのパス
            
        Returns:
            復元成功したらTrue
        """
        try:
            if not backup_path.exists():
                logger.error("バックアップファイルが存在しません")
                return False
            
            # 現在のDBをバックアップ
            if self.db_path.exists():
                emergency_backup = self.db_path.parent / f"{self.db_path.stem}_emergency.db"
                shutil.copy2(self.db_path, emergency_backup)
                logger.info(f"緊急バックアップを作成: {emergency_backup}")
            
            # 復元
            shutil.copy2(backup_path, self.db_path)
            logger.info(f"バックアップから復元しました: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"バックアップ復元に失敗: {e}")
            return False


if __name__ == "__main__":
    manager = BackupManager()
    backup_path = manager.create_backup()
    if backup_path:
        print(f"✅ バックアップ作成: {backup_path}")
    
    backups = manager.get_backup_list()
    print(f"📦 バックアップ数: {len(backups)}")
