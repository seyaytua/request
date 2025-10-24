"""
設定ファイル v1.5.6
"""
import os
import sys
from pathlib import Path

APP_NAME = "訂正依頼システム"
APP_VERSION = "1.5.7"

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
    DATA_DIR = Path(os.path.dirname(sys.executable)) / "data"
else:
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"

DB_PATH = DATA_DIR / "corrections.db"
BACKUP_DIR = DATA_DIR / "backups"
RESOURCES_DIR = BASE_DIR / "src" / "resources"
ICONS_DIR = RESOURCES_DIR / "icons"
STYLES_DIR = RESOURCES_DIR / "styles"

DATA_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_ADMIN_PASSWORD = "admin123"
DEFAULT_NOTICE_MESSAGE = "成績の訂正の場合は、教務に報告してからこちらの訂正依頼を申請してください。訂正依頼後は、成績入力シートなどのデータも忘れずに修正しておいてください。"
DEFAULT_BACKUP_INTERVAL = 5  # 起動5回ごとにバックアップ

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800
LIST_WIDTH_RATIO = 0.65

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

DB_TIMEOUT = 30.0
DB_WAL_MODE = True

REQUEST_TYPES = {
    "ATTENDANCE": "出欠訂正",
    "GRADE": "評価評定変更"
}

ATTENDANCE_TYPES = ["出席", "欠席", "遅刻", "早退", "公欠", "カウントなし", "その他"]
GRADE_TYPES = ["A", "B", "C", "D", "F"]
SEMESTER_TYPES = ["前期中間", "前期期末", "後期中間", "仮評定", "後期期末", "評定"]
PERIOD_TYPES = [f"{i}限" for i in range(1, 13)]

COLOR_ATTENDANCE = "#E8F5E9"
COLOR_GRADE = "#FFF3E0"

print(f"✅ Config loaded: DB_PATH={DB_PATH}")
