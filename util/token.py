import requests
import sys

def token_input() -> str:
    """
    輸入token
    
    回傳：
        str: 使用者輸入的 Access Token 字串
             若使用者直接按 Enter，會回傳空字串
    """
    token = input("輸入 Access Token(完成後請按 Enter）：").strip()
    if not token:
        print("未偵測到Token，請重新執行程式並提供 Access Token")
        sys.exit(0)
    return token

def token_validate(token: str, base_url: str) -> dict:
    """
    驗證 Threads Access Token 是否有效

    參數：
        token (str): Threads Access Token。
        base_url (str): API 的 base URL，例如 "https://graph.threads.net/v1.0"

    回傳：
        dict: 驗證成功後回傳使用者基本資訊，例如：
        {
            "id": "XXXXX",
            "username": "XXXX",
            "name": "XXX"
        }
    """
    url = f"{base_url}/me"
    params = {"access_token": token, "fields": "id,username,name"}
    info = requests.get(url, params=params, timeout=30)
    if info.status_code != 200:
        raise RuntimeError(f"Token 驗證失敗: {info.status_code} {info.text}")
    return info.json()