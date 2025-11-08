from util.token import token_validate
import requests
import time

def fetch_posts(access_token: str, base_url: str, fields: list):
    """
    抓取所有貼文

    參數：
        access_token (str): Threads Access Token
        base_url (str): API 的 base URL，例如 "https://graph.threads.net/v1.0"
        fields (list): 要抓取貼文的內容，例如 ["id", "text", "media_type", "permalink", "created_time"]

    回傳：
        list[dict]: 每篇貼文的資訊清單，例如：
        [
            {
                "id": "123456789",
                "text": "這是一篇貼文",
                "media_type": "TEXT",
                "permalink": "https://www.threads.net/@user/post/123456",
                "created_time": "2025-11-01T12:00:00+0000"
            },
            ...
        ]

    """
    user_id = token_validate(access_token, base_url).get("id")
    
    url = f"{base_url}/{user_id}/threads"
    params = {
        "access_token": access_token,
        "fields": ",".join(fields),
        "limit": 100,
    }
     
    all_posts = []
    page = 1

    while True:
        r = requests.get(url, params=params, timeout=30)
        if r.status_code != 200:
            print("取貼文失敗:", r.status_code)
            break
        
        data = r.json()
        items = data.get("data")
        all_posts = all_posts + items
        
        print(f"分頁 {page}: 本頁 {len(items)} 則，累計 {len(all_posts)} 則")
        page += 1

        # --- 檢查是否還有下一頁 ---
        paging = data.get("paging")
        cursors = paging.get("cursors")
        after = cursors.get("after")

        if paging.get("next"):
            # 若有下一頁，就把它加入 params 進行下一次請求
            params["after"] = after
            time.sleep(0.2)  # 避免請求過快被限流
        else:
            break

    return all_posts

def fetch_metrics(access_token: str, base_url: str, media_id: str, metrics: list):
    """
    抓取單一貼文的互動數據取得指定貼文 (media_id) 的成效指標，例如觀看數、按讚數、回覆數、分享數等
    回傳的結果是一個 dict，key 為指標名稱，value 為對應數值

    參數：
        access_token (str): Threads Access Token。
        base_url (str): API 的 base URL，例如 "https://graph.threads.net/v1.0"
        media_id (str): 要查詢的貼文 ID。
        metrics (list): 要查詢的指標清單，例如 ["views", "likes", "replies", "reposts", "quotes", "shares"]。

    回傳：
        dict: 指標名稱與對應數值的字典，例如：
        {
            "views": 320,
            "likes": 25,
            "replies": 2,
            "shares": 3
        }
    """
    url = f"{base_url}/{media_id}/insights"
    params = {
        "access_token": access_token,
        "metric": ",".join(metrics),
    }
    r = requests.get(url, params=params, timeout=30)
    if r.status_code != 200:
        print(f"失敗 ID={media_id}: {r.status_code}")
        return {}

    resp = r.json()
    out = {}

    for index in resp.get("data"):
        name = index.get("name")
        values = index.get("values")
        if values:
            val = values[0].get("value")
            out[name] = val
    return out


