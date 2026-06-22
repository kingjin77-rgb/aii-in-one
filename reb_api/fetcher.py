"""한국부동산원 API 데이터 수집 모듈"""
import requests
import time
from typing import Optional
from .config import REB_API_BASE_URL, REB_API_KEY, STAT_TABLES


def fetch_stat_data(
    stat_table_id: str,
    cycle_code: str,
    period: str,
    api_key: Optional[str] = None,
    output_type: str = "json"
) -> dict:
    """부동산통계정보시스템 API에서 통계 데이터를 조회합니다."""
    key = api_key or REB_API_KEY
    url = f"{REB_API_BASE_URL}/SttsApiTblData.do"
    params = {
        "KEY": key,
        "STATBL_ID": stat_table_id,
        "DTACYCLE_CD": cycle_code,
        "WRTTIME_IDTFR_ID": period,
        "Type": output_type,
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    if output_type == "json":
        return response.json()
    return {"raw": response.text}


def fetch_all_stats(period: str, api_key: Optional[str] = None) -> dict:
    """모든 등록된 통계표 데이터를 수집합니다."""
    results = {}
    for name, info in STAT_TABLES.items():
        try:
            print(f"[수집중] {name} ({info['description']})...")
            data = fetch_stat_data(
                stat_table_id=info["id"],
                cycle_code=info["cycle"],
                period=period,
                api_key=api_key,
            )
            results[name] = {
                "status": "success",
                "description": info["description"],
                "data": data,
            }
        except Exception as e:
            results[name] = {
                "status": "error",
                "description": info["description"],
                "error": str(e),
            }
        time.sleep(0.5)  # API 호출 간격
    return results


def fetch_stat_table_list(api_key: Optional[str] = None) -> dict:
    """사용 가능한 통계표 목록을 조회합니다."""
    key = api_key or REB_API_KEY
    url = f"{REB_API_BASE_URL}/SttsApiTblList.do"
    params = {
        "KEY": key,
        "Type": "json",
    }
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()
