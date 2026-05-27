import os
import urllib.parse
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # ◀ 추후 프론트엔드 연동을 위해 추가
import uvicorn

app = FastAPI()

# 크로스 오리진 설정 (나중에 프론트엔드 웹사이트에서 이 API를 호출할 수 있게 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "YOUR_DEFAULT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "YOUR_DEFAULT_SECRET")

FILTER_QUERIES = {
    "과학": "과학 (연구 OR 발견 OR 학술) -정치 -연예",
    "최신기술": "(인공지능 OR AI OR 반도체 OR 로봇 OR 바이오) 최신 기술",
    "한국교육이슈": "(수능 OR 늘봄학교 OR 의대증원 OR 교육부) 이슈"
}

def fetch_naver_news(search_keyword: str, display_count: int = 20):
    enc_text = urllib.parse.quote(search_keyword)
    url = f"https://openapi.naver.com/v1/search/news.json?query={enc_text}&display={display_count}&sort=date"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    response = requests.get(url, headers=headers)
    return response.json().get("items", []) if response.status_code == 200 else []

def clean_news_data(raw_news):
    cleaned_news = []
    for item in raw_news:
        cleaned_news.append({
            "title": item["title"].replace("<b>", "").replace("</b>", "").replace("&quot;", '"'),
            "link": item["originallink"] if item["originallink"] else item["link"],
            "description": item["description"].replace("<b>", "").replace("</b>", "").replace("&quot;", '"'),
            "pub_date": item["pubDate"]
        })
    return cleaned_news

# 🌟 [변경 및 추가] 메인 화면용 API (세 카테고리의 최신 기사를 3개씩 모아서 전송)
@app.get("/api/news/main")
def get_main_dashboard():
    dashboard_data = {}
    
    for category, query in FILTER_QUERIES.items():
        # 메인 화면에는 무겁지 않게 카테고리당 딱 3개씩만 가져옴
        raw_news = fetch_naver_news(query, display_count=3)
        dashboard_data[category] = clean_news_data(raw_news)
        
    return {
        "message": "나의 뉴스 에이전트 메인 대시보드",
        "categories": list(FILTER_QUERIES.keys()),
        "data": dashboard_data
    }

# 기존 개별 카테고리 상세 보기 API (20개씩 가져옴)
@app.get("/api/news/{user_filter}")
def get_personalized_news(user_filter: str):
    if user_filter not in FILTER_QUERIES:
        return {"error": "지원하지 않는 필터입니다."}
    raw_news = fetch_naver_news(FILTER_QUERIES[user_filter], display_count=20)
    cleaned_news = clean_news_data(raw_news)
    return {"filter": user_filter, "count": len(cleaned_news), "news": cleaned_news}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
