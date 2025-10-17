"""
ロギングユーティリティ
アプリケーション全体のログ管理
"""
import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(name: str, log_file: Path = None, level=logging.INFO):
    """
    ロガーをセットアップ
    
    Args:
        name: ロガー名
        log_file: ログファイルパス（Noneの場合はコンソールのみ）
        level: ログレベル
        
    Returns:
        設定済みのロガー
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 既存のハンドラをクリア
    logger.handlers.clear()
    
    # フォーマット設定
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # コンソールハンドラ
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # ファイルハンドラ（指定された場合）
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str):
    """
    既存のロガーを取得
    
    Args:
        name: ロガー名
        
    Returns:
        ロガーインスタンス
    """
    return logging.getLogger(name)


# アプリケーション用のデフォルトロガー
app_logger = setup_logger('App_request')


# テスト用
if __name__ == "__main__":
    logger = setup_logger('test', Path('test.log'))
    logger.info("これはテストログです")
    logger.warning("警告メッセージ")
    logger.error("エラーメッセージ")
