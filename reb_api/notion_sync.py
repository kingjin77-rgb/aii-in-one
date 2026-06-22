"""부동산원 데이터를 노션에 동기화하는 모듈"""
import json
from datetime import datetime


def _extract_rows(data: dict) -> list:
    """R-ONE API 응답에서 실제 데이터 행을 추출합니다.

    응답 구조: {"SttsApiTblData": [{"head": [...]}, {"row": [...]}]}
    """
    if not isinstance(data, dict):
        return []

    tbl = data.get("SttsApiTblData", [])
    if not isinstance(tbl, list):
        return []

    for item in tbl:
        if isinstance(item, dict) and "row" in item:
            return item["row"]

    return []


def format_stat_for_notion(stat_name: str, stat_data: dict) -> dict:
    if stat_data["status"] == "error":
        return {
            "properties": {
                "통계명": stat_name,
                "상태": "오류",
                "설명": stat_data["description"],
                "수집일시": datetime.now().isoformat(),
                "비고": stat_data.get("error", ""),
            },
            "content": f"## {stat_name}\n\n오류 발생: {stat_data.get('error', '알 수 없는 오류')}",
        }

    data = stat_data.get("data", {})
    rows = _extract_rows(data)
    table_md = build_markdown_table(rows)

    return {
        "properties": {
            "통계명": stat_name,
            "상태": "성공",
            "설명": stat_data["description"],
            "수집일시": datetime.now().isoformat(),
            "데이터건수": str(len(rows)),
        },
        "content": f"## {stat_name}\n\n{stat_data['description']}\n\n수집 건수: {len(rows)}건\n\n{table_md}",
    }


def build_markdown_table(rows: list) -> str:
    if not rows:
        return "*데이터 없음*"

    if len(rows) > 50:
        rows = rows[:50]

    headers = list(rows[0].keys())
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        values = [str(row.get(h, "")).replace("|", "/") for h in headers]
        lines.append("| " + " | ".join(values) + " |")

    return "\n".join(lines)


def build_summary_content(results: dict, period: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    success_count = sum(1 for r in results.values() if r["status"] == "success")
    error_count = sum(1 for r in results.values() if r["status"] == "error")

    lines = [
        f"## 부동산원 데이터 수집 결과",
        f"",
        f"- **수집일시**: {now}",
        f"- **조회기간**: {period}",
        f"- **성공**: {success_count}건",
        f"- **실패**: {error_count}건",
        f"",
        f"---",
        f"",
    ]

    for name, data in results.items():
        status_icon = "✅" if data["status"] == "success" else "❌"
        lines.append(f"### {status_icon} {name}")
        lines.append(f"")
        lines.append(f"{data['description']}")
        lines.append(f"")

        if data["status"] == "success":
            raw_data = data.get("data", {})
            rows = _extract_rows(raw_data)
            lines.append(f"수집 건수: {len(rows)}건")
            if rows:
                table = build_markdown_table(rows[:10])
                lines.append(f"")
                lines.append(table)
        else:
            lines.append(f"오류: {data.get('error', '')}")

        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")

    return "\n".join(lines)
