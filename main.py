import sys
import time
from datetime import datetime
from util import token_input, fetch_posts, fetch_metrics, export_excel, export_tw_time

BASE_URL = "https://graph.threads.net/v1.0"
POST_FIELDS = ["id", "text", "media_type", "media_url", "timestamp", "permalink"]
INSIGHT_METRICS = ["views", "likes", "replies", "reposts", "quotes", "shares"]

def main():
    # 輸入與驗證 Token
    token = token_input()

    # 抓取貼文
    print("開始抓取貼文...")
    posts = fetch_posts(token, BASE_URL, POST_FIELDS)
    if not posts:
        print("沒有抓到貼文")
        sys.exit(0)
    print(f"共取得 {len(posts)} 則貼文")

    # 抓取貼文成效
    rows = []
    total = len(posts)
    for i, post in enumerate(posts, start=1):
        media_id = post.get("id", "")
        if post.get("media_type") == "REPOST_FACADE":
            print(f"[{i}/{total}] 不處理：ID={media_id} 為轉發貼文")
            continue

        metrics = fetch_metrics(token, BASE_URL, media_id, INSIGHT_METRICS)

        row = {
            "id": post.get("id", ""),
            "created_time": export_tw_time(post.get("timestamp", "")),
            "text": (post.get("text") or "").replace("\r\n", "\n").strip(),
            "views": metrics.get("views", ""),
            "likes": metrics.get("likes", ""),
            "replies": metrics.get("replies", ""),
            "reposts": metrics.get("reposts", ""),
            "quotes": metrics.get("quotes", ""),
            "shares": metrics.get("shares", ""),
            "permalink": post.get("permalink", "")
        }
        rows.append(row)

        print(f"[{i}/{total}] 已處理：ID={media_id} | 讚={row['likes']} 回覆={row['replies']} 觀看={row['views']}")
        time.sleep(0.15)

    # 匯出 Excel
    stamp = datetime.now().strftime("%Y%m%d")
    out_file = f"threads_posts_{stamp}.xlsx"
    try:
        export_excel(rows, out_file)
    except Exception as e:
        print(e)
        print(f"若有打開{out_file}，請關閉再重新跑一次程式 !")

if __name__ == "__main__":
    main()
    input("\n按下 Enter 鍵以結束程式...")