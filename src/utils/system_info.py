"""
システム情報取得ユーティリティ
PCユーザー名、PC名などを取得
"""
import os
import socket
import getpass
import platform
from datetime import datetime


def get_username():
    """PCのユーザー名を取得"""
    return getpass.getuser()


def get_pc_name():
    """PC名（ホスト名）を取得"""
    return socket.gethostname()


def get_system_info():
    """システム情報をまとめて取得"""
    return {
        'username': get_username(),
        'pc_name': get_pc_name(),
        'os': platform.system(),
        'os_version': platform.version(),
        'timestamp': datetime.now()
    }


def get_user_identifier():
    """ユーザー識別子を取得（ログ記録用）"""
    return f"{get_username()}@{get_pc_name()}"


# テスト用
if __name__ == "__main__":
    info = get_system_info()
    print("=== システム情報 ===")
    print(f"ユーザー名: {info['username']}")
    print(f"PC名: {info['pc_name']}")
    print(f"OS: {info['os']}")
    print(f"識別子: {get_user_identifier()}")
