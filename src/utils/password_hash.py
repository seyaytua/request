"""
パスワードハッシュ化ユーティリティ
SHA256を使用したパスワードの安全な保存と検証
"""
import hashlib


def hash_password(password: str) -> str:
    """
    パスワードをSHA256でハッシュ化
    
    Args:
        password: 平文パスワード
        
    Returns:
        ハッシュ化されたパスワード（16進数文字列）
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """
    パスワードを検証
    
    Args:
        password: 入力された平文パスワード
        hashed: 保存されているハッシュ値
        
    Returns:
        パスワードが一致すればTrue
    """
    return hash_password(password) == hashed


# テスト用
if __name__ == "__main__":
    test_password = "admin123"
    hashed = hash_password(test_password)
    print(f"平文: {test_password}")
    print(f"ハッシュ: {hashed}")
    print(f"検証: {verify_password(test_password, hashed)}")
    print(f"誤検証: {verify_password('wrong', hashed)}")
