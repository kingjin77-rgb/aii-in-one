"""
한국부동산원 부동산통계 수집 및 노션 동기화 프로그램

사용법:
    python -m reb_api.main --api-key YOUR_KEY --period 202406

환경변수:
    REB_API_KEY: 부동산원 API 키 (r-one 또는 data.go.kr)
"""
import argparse
import json
import sys
from datetime import datetime

from .config import STAT_TABLES
from .fetcher import fetch_all_stats, fetch_stat_table_list
from .notion_sync import build_summary_content, format_stat_for_notion


def main():
    parser = argparse.ArgumentParser(description="한국부동산원 부동산통계 수집 프로그램")
    parser.add_argument("--api-key", help="부동산원 API 키", required=True)
    parser.add_argument("--period", help="조회기간 (예: 202406)", default=datetime.now().strftime("%Y%m"))
    parser.add_argument("--list-tables", action="store_true", help="사용 가능한 통계표 목록 조회")
    parser.add_argument("--output", help="결과 JSON 파일 저장 경로")
    parser.add_argument("--stat", help="특정 통계만 수집 (통계명)", choices=list(STAT_TABLES.keys()))

    args = parser.parse_args()

    if args.list_tables:
        print("[조회] 통계표 목록을 가져오는 중...")
        try:
            tables = fetch_stat_table_list(api_key=args.api_key)
            print(json.dumps(tables, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"[오류] 통계표 목록 조회 실패: {e}")
            sys.exit(1)
        return

    print(f"[시작] 부동산원 데이터 수집 (기간: {args.period})")
    print(f"[대상] {len(STAT_TABLES)}개 통계표")
    print("=" * 60)

    if args.stat:
        from .fetcher import fetch_stat_data
        info = STAT_TABLES[args.stat]
        print(f"[수집] {args.stat}...")
        try:
            data = fetch_stat_data(
                stat_table_id=info["id"],
                cycle_code=info["cycle"],
                period=args.period,
                api_key=args.api_key,
            )
            results = {args.stat: {"status": "success", "description": info["description"], "data": data}}
        except Exception as e:
            results = {args.stat: {"status": "error", "description": info["description"], "error": str(e)}}
    else:
        results = fetch_all_stats(period=args.period, api_key=args.api_key)

    print("=" * 60)

    success = sum(1 for r in results.values() if r["status"] == "success")
    errors = sum(1 for r in results.values() if r["status"] == "error")
    print(f"[완료] 성공: {success}, 실패: {errors}")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        print(f"[저장] {args.output}")

    summary = build_summary_content(results, args.period)
    print("\n" + summary)

    return results


if __name__ == "__main__":
    main()
