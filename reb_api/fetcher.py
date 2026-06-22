"""한국부동산원 API 데이터 수집 모듈 - 다중 소스 지원"""
import json
import time
import urllib.request
import urllib.parse
import urllib.error
import ssl
from typing import Optional
from .config import REB_API_BASE_URL, REB_API_KEY, STAT_TABLES


def _request_get(url: str, params: dict, timeout: int = 30) -> str:
    query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    full_url = f"{url}?{query}"

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        req = urllib.request.Request(full_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        raise Exception(f"HTTP {e.code}: {e.reason} for {full_url}")
    except urllib.error.URLError as e:
        raise Exception(f"URL Error: {e.reason} for {full_url}")


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

    text = _request_get(url, params)

    if output_type == "json":
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"raw": text, "SttsApiTblData": []}
    return {"raw": text}


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
            print(f"[성공] {name}")
        except Exception as e:
            results[name] = {
                "status": "error",
                "description": info["description"],
                "error": str(e),
            }
            print(f"[실패] {name}: {e}")
        time.sleep(0.5)
    return results


def fetch_stat_table_list(api_key: Optional[str] = None) -> dict:
    """사용 가능한 통계표 목록을 조회합니다."""
    key = api_key or REB_API_KEY
    url = f"{REB_API_BASE_URL}/SttsApiTblList.do"
    params = {"KEY": key, "Type": "json"}
    text = _request_get(url, params)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw": text}
