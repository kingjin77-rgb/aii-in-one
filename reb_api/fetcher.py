"""한국부동산원 API 데이터 수집 모듈 - 다중 소스 지원"""
import json
import time
import urllib.request
import urllib.parse
import urllib.error
import ssl
from typing import Optional
from .config import REB_API_KEY, STAT_TABLES


def _request_get(url: str, params: dict = None, timeout: int = 30) -> str:
    if params:
        query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        full_url = f"{url}?{query}"
    else:
        full_url = url

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(full_url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="replace")[:500]
        except Exception:
            pass
        raise Exception(f"HTTP {e.code} {e.reason} | URL: {full_url} | Body: {body}")
    except urllib.error.URLError as e:
        raise Exception(f"연결 실패: {e.reason} | URL: {full_url}")


# ── R-ONE API (reb.or.kr) ──

def fetch_stat_data_rone(
    stat_table_id: str,
    cycle_code: str,
    period: str,
    api_key: Optional[str] = None,
) -> dict:
    key = api_key or REB_API_KEY
    url = "https://www.reb.or.kr/r-one/openapi/SttsApiTblData.do"
    params = {
        "KEY": key,
        "STATBL_ID": stat_table_id,
        "DTACYCLE_CD": cycle_code,
        "WRTTIME_IDTFR_ID": period,
        "Type": "json",
    }
    text = _request_get(url, params)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw": text, "SttsApiTblData": []}


def fetch_table_list_rone(api_key: Optional[str] = None) -> dict:
    key = api_key or REB_API_KEY
    url = "https://www.reb.or.kr/r-one/openapi/SttsApiTbl.do"
    params = {"KEY": key, "Type": "json"}
    text = _request_get(url, params)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw": text}


# ── 공공데이터포털 API (data.go.kr) ──

DATA_GO_KR_ENDPOINTS = {
    "아파트매매실거래": {
        "url": "http://openapi.molit.go.kr/OpenAPI_ToolInstall498/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev",
        "description": "아파트 매매 실거래 상세 자료",
    },
    "아파트전월세실거래": {
        "url": "http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptRent",
        "description": "아파트 전월세 실거래 자료",
    },
    "단독다가구매매실거래": {
        "url": "http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcSHRent",
        "description": "단독/다가구 매매 실거래 자료",
    },
    "오피스텔매매실거래": {
        "url": "http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcOffiTrade",
        "description": "오피스텔 매매 실거래 자료",
    },
}


def fetch_stat_data_datagokr(
    endpoint_name: str,
    lawd_cd: str,
    deal_ymd: str,
    api_key: Optional[str] = None,
) -> dict:
    key = api_key or REB_API_KEY
    ep = DATA_GO_KR_ENDPOINTS.get(endpoint_name)
    if not ep:
        raise Exception(f"알 수 없는 엔드포인트: {endpoint_name}")

    params = {
        "serviceKey": key,
        "LAWD_CD": lawd_cd,
        "DEAL_YMD": deal_ymd,
        "numOfRows": "1000",
        "pageNo": "1",
    }
    text = _request_get(ep["url"], params)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # XML 응답일 수 있음
        return {"raw_xml": text}


# ── 통합 수집 ──

def fetch_all_stats(period: str, api_key: Optional[str] = None) -> dict:
    """R-ONE API로 모든 통계 데이터를 수집합니다."""
    results = {}
    for name, info in STAT_TABLES.items():
        try:
            print(f"[수집중] {name} ({info['description']})...")
            data = fetch_stat_data_rone(
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
            print(f"  [성공] {name}")
        except Exception as e:
            results[name] = {
                "status": "error",
                "description": info["description"],
                "error": str(e),
            }
            print(f"  [실패] {name}: {e}")
        time.sleep(0.5)
    return results


def fetch_stat_table_list(api_key: Optional[str] = None) -> dict:
    """통계표 목록을 조회합니다."""
    return fetch_table_list_rone(api_key)


def diagnose_api(api_key: Optional[str] = None) -> None:
    """API 연결 상태를 진단합니다."""
    key = api_key or REB_API_KEY
    print("=" * 60)
    print("[진단] API 연결 상태 확인")
    print(f"  API 키: {key[:8]}...{key[-4:]}")
    print("=" * 60)

    # 1) R-ONE 접속 테스트
    print("\n[1] R-ONE 사이트 접속 테스트...")
    try:
        _request_get("https://www.reb.or.kr/r-one/", timeout=10)
        print("  ✓ reb.or.kr 접속 성공")
    except Exception as e:
        print(f"  ✗ reb.or.kr 접속 실패: {e}")

    # 2) R-ONE API sample 키 테스트
    print("\n[2] R-ONE API sample 키 테스트...")
    try:
        text = _request_get(
            "https://www.reb.or.kr/r-one/openapi/SttsApiTblData.do",
            {"KEY": "sample", "STATBL_ID": "A_2024_00038", "DTACYCLE_CD": "MM",
             "WRTTIME_IDTFR_ID": "202405", "Type": "json"},
            timeout=10,
        )
        print(f"  ✓ sample 키 응답: {text[:200]}")
    except Exception as e:
        print(f"  ✗ sample 키 실패: {e}")

    # 3) R-ONE API 사용자 키 테스트
    print(f"\n[3] R-ONE API 사용자 키 테스트...")
    try:
        text = _request_get(
            "https://www.reb.or.kr/r-one/openapi/SttsApiTblData.do",
            {"KEY": key, "STATBL_ID": "A_2024_00038", "DTACYCLE_CD": "MM",
             "WRTTIME_IDTFR_ID": "202405", "Type": "json"},
            timeout=10,
        )
        print(f"  ✓ 사용자 키 응답: {text[:200]}")
    except Exception as e:
        print(f"  ✗ 사용자 키 실패: {e}")

    # 4) 통계표 목록 테스트
    print(f"\n[4] 통계표 목록 조회 테스트...")
    try:
        text = _request_get(
            "https://www.reb.or.kr/r-one/openapi/SttsApiTbl.do",
            {"KEY": key, "Type": "json"},
            timeout=10,
        )
        print(f"  ✓ 목록 응답: {text[:300]}")
    except Exception as e:
        print(f"  ✗ 목록 조회 실패: {e}")

    # 5) data.go.kr 테스트
    print(f"\n[5] data.go.kr API 테스트...")
    try:
        text = _request_get(
            "http://openapi.molit.go.kr/OpenAPI_ToolInstall498/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev",
            {"serviceKey": key, "LAWD_CD": "11110", "DEAL_YMD": "202405",
             "numOfRows": "5", "pageNo": "1"},
            timeout=10,
        )
        print(f"  ✓ data.go.kr 응답: {text[:300]}")
    except Exception as e:
        print(f"  ✗ data.go.kr 실패: {e}")

    print("\n" + "=" * 60)
    print("[진단 완료]")
