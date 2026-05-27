import os
import urllib.parse
import requests
from fastapi import FastAPI
import uvicorn  # ◀ 추가

app = FastAPI()

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "YOUR_DEFAULT_ID")          # ◀ 보안을 위해 환경변수 처리
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "YOUR_DEFAULT_SECRET") # ◀ 보안을 위해 환경변수 처리

FILTER_QUERIES = {
    "과학": "과학 (연구 OR 발견 OR 학술) -정치 -연예",
    "최신기술": "(인공지능 OR AI OR 반도체 OR 로봇 OR 바이오) 최신 기술",
    "한국교육이슈": "(수능 OR 늘봄학교 OR 의대증원 OR 교육부) 이슈"
}

def fetch_naver_news(search_keyword: str):
    enc_text = urllib.parse.quote(search_keyword)
    url = f"https://openapi.naver.com/v1/search/news.json?query={enc_text}&display=20&sort=date"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    response = requests.get(url, headers=headers)
    return response.json().get("items", []) if response.status_code == 200 else []

@app.get("/api/news/{user_filter}")
def get_personalized_news(user_filter: str):
    if user_filter not in FILTER_QUERIES:
        return {"error": "지원하지 않는 필터입니다."}
    raw_news = fetch_naver_news(FILTER_QUERIES[user_filter])
    cleaned_news = []
    for item in raw_news:
        cleaned_news.append({
            "title": item["title"].replace("<b>", "").replace("</b>", "").replace("&quot;", '"'),
            "link": item["originallink"] if item["originallink"] else item["link"],
            "description": item["description"].replace("<b>", "").replace("</b>", ""),
            "pub_date": item["pubDate"]
        })
    return {"filter": user_filter, "count": len(cleaned_news), "news": cleaned_news}

# ◀ 클라우드 서버 구동을 위한 메인 실행부 추가
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
