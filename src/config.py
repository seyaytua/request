"""
設定ファイル
アプリケーション全体の設定を管理
"""
import os
import sys
from pathlib import Path

# アプリケーション情報
APP_NAME = "訂正依頼システム"
APP_VERSION = "1.0.0"

# プロジェクトルートディレクトリ
if getattr(sys, 'frozen', False):
    # PyInstallerでビルドされた実行ファイルの場合
    BASE_DIR = Path(sys._MEIPASS)
    DATA_DIR = Path(os.path.dirname(sys.executable)) / "data"
else:
    # 開発環境の場合
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"

# データベースパス
DB_PATH = DATA_DIR / "corrections.db"

# リソースパス
RESOURCES_DIR = BASE_DIR / "src" / "resources"
ICONS_DIR = RESOURCES_DIR / "icons"
STYLES_DIR = RESOURCES_DIR / "styles"

# データディレクトリが存在しない場合は作成
DATA_DIR.mkdir(parents=True, exist_ok=True)

# システム設定
DEFAULT_ADMIN_PASSWORD = "admin123"  # 初期パスワード（後で変更推奨）

# UI設定
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800
LIST_WIDTH_RATIO = 0.65  # 左リストの幅比率

# ログ設定
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# データベース設定
DB_TIMEOUT = 30.0  # SQLiteタイムアウト（秒）
DB_WAL_MODE = True  # Write-Ahead Logging有効化

# 訂正依頼の種別
REQUEST_TYPES = {
    "ATTENDANCE": "出欠訂正",
    "GRADE": "評価評定変更"
}

# 訂正依頼のステータス
REQUEST_STATUS = {
    "PENDING": "未処理",
    "PROCESSING": "処理中",
    "COMPLETED": "完了",
    "REJECTED": "却下"
}

# 出欠の種別
ATTENDANCE_TYPES = ["出席", "欠席", "遅刻", "早退", "公欠"]

# 評価の種別
GRADE_TYPES = ["A", "B", "C", "D", "F"]

print(f"✅ Config loaded: DB_PATH={DB_PATH}")
