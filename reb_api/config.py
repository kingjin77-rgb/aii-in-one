"""한국부동산원 API 설정"""
import os

# 부동산원 R-ONE Open API
REB_API_BASE_URL = "https://www.reb.or.kr/r-one/openapi"
REB_API_KEY = os.environ.get("REB_API_KEY", "7e041d8f095346d58533ff1b12858ef1")

# 공공데이터포털 API (data.go.kr)
DATA_GO_KR_BASE_URL = "http://apis.data.go.kr/1613000"
DATA_GO_KR_KEY = os.environ.get("DATA_GO_KR_KEY", "")

# Notion
NOTION_PAGE_ID = "7e041d8f095346d58533ff1b12858ef1"

# 통계표 ID 목록 (한국부동산원 주요 통계)
STAT_TABLES = {
    "주택매매가격지수": {
        "id": "A_2024_00038",
        "cycle": "MM",
        "description": "전국 주택매매가격지수 (월별)"
    },
    "주택전세가격지수": {
        "id": "A_2024_00044",
        "cycle": "MM",
        "description": "전국 주택전세가격지수 (월별)"
    },
    "주택매매가격변동률": {
        "id": "A_2024_00001",
        "cycle": "MM",
        "description": "전국 주택매매가격 변동률 (월별)"
    },
    "주택전세가격변동률": {
        "id": "A_2024_00007",
        "cycle": "MM",
        "description": "전국 주택전세가격 변동률 (월별)"
    },
    "아파트매매가격지수": {
        "id": "A_2024_00039",
        "cycle": "MM",
        "description": "전국 아파트매매가격지수 (월별)"
    },
    "아파트전세가격지수": {
        "id": "A_2024_00045",
        "cycle": "MM",
        "description": "전국 아파트전세가격지수 (월별)"
    },
    "지가변동률": {
        "id": "A_2024_00900",
        "cycle": "QQ",
        "description": "전국 지가변동률 (분기별)"
    },
    "상업용부동산임대동향": {
        "id": "A_2024_00400",
        "cycle": "QQ",
        "description": "상업용부동산 임대동향 (분기별)"
    },
    "오피스텔매매가격동향": {
        "id": "A_2024_00200",
        "cycle": "MM",
        "description": "오피스텔 매매가격 동향 (월별)"
    },
    "부동산거래현황_매매": {
        "id": "A_2024_00700",
        "cycle": "MM",
        "description": "부동산 거래현황 매매 (월별)"
    },
}
