"""
訂正依頼システム - メインエントリーポイント
"""
import sys
from pathlib import Path

# srcディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.ui.main_window import MainWindow
from src.config import APP_NAME
from src.utils.logger import setup_logger

# ロガーセットアップ
logger = setup_logger('main', Path('data/app.log'))


def main():
    """メイン関数"""
    try:
        # アプリケーション作成
        app = QApplication(sys.argv)
        app.setApplicationName(APP_NAME)
        
        # High DPI対応
        app.setAttribute(Qt.AA_EnableHighDpiScaling)
        app.setAttribute(Qt.AA_UseHighDpiPixmaps)
        
        # メインウィンドウ表示
        window = MainWindow()
        window.show()
        
        logger.info("=" * 50)
        logger.info(f"{APP_NAME} 起動")
        logger.info("=" * 50)
        
        # イベントループ開始
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"アプリケーション起動エラー: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
