#!/usr/bin/env python3
"""擷取臺南市議會第 4 屆大會會議紀錄，計算現任候選人出席率。

口徑與臺北市大會試點相同：
- 分子：只出現在出席名單。
- 分母：只出席、只請假，或兩邊都沒有（缺席）。請假留在分母。
- 同一場同時出現在出席與請假：該人該場剔除。
- 委員會、聯席審查不計算。
- 納入標題為第 N 次會、市政總質詢、部門業務報告及質詢、專案報告的場次
  （頁首有出席議員／請假議員）。抽不出名單的場次整場不計。

依賴：pypdf（PDF 文字）。快取預設在 /tmp，不進版控。
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
INCUMBENTS_PATH = ROOT / "src" / "data" / "incumbents.json"
API = "https://bill.tncc.gov.tw/NoPaperMeeting_TNCC/api/WEB008_GetProMeetMinutesList.ashx"
PDF_API = "https://bill.tncc.gov.tw/NoPaperMeeting_TNCC/Api/WEB009_GenerateOneProMeetMinutes.ashx"
LIST_PAGE = "https://www.tncc.gov.tw/mtrecordlist.asp?orcaid=DCF819D7-D2F8-449B-AD87-59005E51F6A6"
REGULAR = "9d23fdb8-a4b3-42f0-bcb5-7f36b1378b68"
SPECIAL = "6abf9a5b-0217-4031-804c-62908a6c44b9"
UA = "vote2026-tainan-plenary/1.0 (attendance; civic archive)"
PARSER_VERSION = 2
MIN_ATTEND = 25

EXCLUDE = ("委員會", "聯席審查", "審查會", "分組審查", "程序會")
INCLUDE = ("次會", "質詢", "業務報告", "專案報告", "施政報告", "開幕", "預備")

ATTEND_RE = re.compile(r"出\s*席\s*議\s*員")
LEAVE_RE = re.compile(r"請\s*假\s*議\s*員")
END_RES = (
    re.compile(r"列\s*席\s*議\s*員"),
    re.compile(r"列\s*席\s*人\s*員"),
    re.compile(r"紀\s*錄\s*內\s*容"),
)


def fetch(url: str, timeout: int = 45) -> bytes:
    last_error: Exception | None = None
    for _ in range(2):
        try:
            result = subprocess.run(
                ["curl", "-fsSL", "--max-time", str(timeout), "-A", UA, url],
                check=True,
                capture_output=True,
            )
            return result.stdout
        except subprocess.CalledProcessError as exc:
            last_error = exc
    assert last_error is not None
    raise last_error


def normalize_name(name: str) -> str:
    text = unicodedata.normalize("NFKC", name)
    return re.sub(r"\s+", "", text)


def name_keys(name: str) -> set[str]:
    base = normalize_name(name)
    return {base, base.replace("黃", "黄"), base.replace("黄", "黃")}


def is_plenary_title(title: str) -> bool:
    if any(word in title for word in EXCLUDE):
        return False
    return any(word in title for word in INCLUDE)


def section(text: str, start: re.Pattern[str], extra_ends: tuple[re.Pattern[str], ...] = ()) -> str:
    match = start.search(text)
    if not match:
        return ""
    rest = text[match.end() :]
    cuts = []
    for pattern in (*END_RES, *extra_ends):
        found = pattern.search(rest)
        if found:
            cuts.append(found.start())
    # 請假段不能吃進出席段之後的下一個標題；出席段要在請假標題停下。
    return rest[: min(cuts)] if cuts else rest[:800]


def names_from_block(block: str) -> list[str]:
    text = unicodedata.normalize("NFKC", block)
    text = re.sub(r"[（(]\s*依席次排序\s*[）)]", " ", text)
    text = re.sub(r"([\u4e00-\u9fff])副議長([\u4e00-\u9fff]{1,3})", r"\1\2", text)
    text = re.sub(r"([\u4e00-\u9fff])議長([\u4e00-\u9fff]{1,3})", r"\1\2", text)
    text = text.replace("、", " ").replace("，", " ").replace(",", " ")
    names: list[str] = []
    for token in text.split():
        token = token.strip("．.。:：;；()（）")
        if re.fullmatch(r"[\u4e00-\u9fff]{2,4}", token):
            names.append(token)
    return names


def parse_minutes(raw: str) -> dict:
    text = unicodedata.normalize("NFKC", raw)
    if not ATTEND_RE.search(text):
        return {"ok": False, "reason": "沒有出席議員名單"}
    attended = names_from_block(section(text, ATTEND_RE, (LEAVE_RE,)))
    leave = names_from_block(section(text, LEAVE_RE))
    if len(attended) < MIN_ATTEND or len(attended) > 70:
        return {"ok": False, "reason": f"出席人數異常：{len(attended)}"}
    if len(leave) > 40:
        return {"ok": False, "reason": f"請假人數異常：{len(leave)}"}
    if len(attended) != len(set(attended)) or len(leave) != len(set(leave)):
        return {"ok": False, "reason": "同一名單出現重複姓名"}
    return {"ok": True, "attended": sorted(set(attended)), "leave": sorted(set(leave))}


def load_meetings() -> list[dict]:
    rows: list[dict] = []
    seen: set[str] = set()
    for kind, mgs in (("定期會", REGULAR), ("臨時會", SPECIAL)):
        times = json.loads(
            fetch(
                "https://bill.tncc.gov.tw/NoPaperMeeting_TNCC/Api/WEB006_GetProMeetTimesList.ashx"
                f"?grdno=4&mgsno={mgs}"
            )
        )
        for item in times:
            tim = str(item["TimNo"])
            page = 1
            while True:
                payload = json.loads(
                    fetch(f"{API}?topage={page}&pagerow=50&grdno=4&mgsno={mgs}&timno={tim}")
                )
                if not payload:
                    break
                for record in payload:
                    title = record.get("Title") or ""
                    if not is_plenary_title(title):
                        continue
                    url = record.get("PdfDownloadUrl") or ""
                    minno_match = re.search(r"minno=([0-9a-f-]+)", url)
                    if not minno_match:
                        continue
                    minno = minno_match.group(1)
                    if minno in seen:
                        continue
                    seen.add(minno)
                    rows.append(
                        {
                            "minno": minno,
                            "kind": kind,
                            "session": f"第4屆第{tim}次{kind}",
                            "title": title.strip(),
                            "date": record.get("SDate") or "",
                            "pdfUrl": f"{PDF_API}?minno={minno}&type=pdf",
                        }
                    )
                total = int(payload[0].get("PagesAll") or 1)
                if page >= total:
                    break
                page += 1
    return rows


def tainan_candidates(data: dict) -> list[dict]:
    people = []
    for key, entry in data.items():
        if not key.startswith("臺南市|") or not isinstance(entry, dict):
            continue
        if not entry.get("incumbency", {}).get("publish"):
            continue
        parts = key.split("|")
        roster = entry.get("incumbency", {}).get("rosterName") or parts[3]
        people.append(
            {
                "key": key,
                "name": normalize_name(parts[3]),
                "rosterName": normalize_name(roster),
                "district": parts[2],
            }
        )
    return people


def pdf_text(path: Path) -> str:
    reader = PdfReader(str(path))
    return "\n".join((page.extract_text() or "") for page in reader.pages[:2])


def download_one(meeting: dict, cache: Path) -> dict:
    minno = meeting["minno"]
    pdf_path = cache / f"{minno}.pdf"
    meta_path = cache / f"{minno}.json"
    if meta_path.exists():
        cached = json.loads(meta_path.read_text(encoding="utf-8"))
        if cached.get("parserVersion") == PARSER_VERSION:
            cached["meeting"] = meeting
            return cached
    try:
        if not pdf_path.exists() or pdf_path.stat().st_size < 100:
            pdf_path.write_bytes(fetch(meeting["pdfUrl"]))
        parsed = parse_minutes(pdf_text(pdf_path))
        result = {**parsed, "docUrl": meeting["pdfUrl"]}
    except Exception as exc:  # noqa: BLE001 — 單場失敗不中斷整批
        result = {"ok": False, "reason": f"下載或解析失敗：{exc}", "docUrl": meeting["pdfUrl"]}
    meta = {
        "parserVersion": PARSER_VERSION,
        "ok": result.get("ok", False),
        "reason": result.get("reason"),
        "attended": result.get("attended"),
        "leave": result.get("leave"),
        "docUrl": result.get("docUrl"),
        "session": meeting["session"],
        "title": meeting["title"],
        "date": meeting["date"],
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    meta["meeting"] = meeting
    return meta


def aggregate(meetings: list[dict], people: list[dict]) -> dict:
    scored = []
    skipped = []
    for person in people:
        keys = name_keys(person["name"]) | name_keys(person["rosterName"])
        attended = 0
        denominator = 0
        excluded_both = 0
        leave_only = 0
        absent = 0
        seen = False
        for meeting in meetings:
            if not meeting.get("ok"):
                continue
            present_names = {normalize_name(name) for name in meeting["attended"]}
            leave_names = {normalize_name(name) for name in meeting["leave"]}
            present = bool(keys & {alias for name in present_names for alias in name_keys(name)})
            leave = bool(keys & {alias for name in leave_names for alias in name_keys(name)})
            if present or leave:
                seen = True
            if present and leave:
                excluded_both += 1
                continue
            if present:
                attended += 1
                denominator += 1
            elif leave:
                leave_only += 1
                denominator += 1
            else:
                absent += 1
                denominator += 1
        if not seen or denominator == 0:
            skipped.append({**person, "reason": "議事錄名單從未出現此人，不估計"})
            continue
        rate = round(attended / denominator * 100 + 1e-9, 1)
        scored.append(
            {
                **person,
                "plenary": rate,
                "plenaryCounts": {
                    "attended": attended,
                    "denominator": denominator,
                    "excludedBothLists": excluded_both,
                    "leave": leave_only,
                    "absent": absent,
                },
            }
        )
    return {"scored": scored, "skipped": skipped}


def apply_incumbents(
    data: dict,
    scored: list[dict],
    checked_on: str,
    meetings_ok: int,
    meetings_total: int,
) -> int:
    reason = (
        f"第4屆大會會議紀錄：{meetings_total} 場中可解析 {meetings_ok} 場"
        "（下載失敗的場次整場不計，不當缺席）。"
        "出席場次÷應出席場次（請假與缺席留在分母；同一場同時列入出席與請假者不計）。"
        "含第 N 次會、市政總質詢、部門業務質詢與專案報告；委員會與聯席審查未計算。"
    )
    updated = 0
    for row in scored:
        entry = data[row["key"]]
        counts = row["plenaryCounts"]
        entry["attendance"] = {
            "status": "available",
            "plenary": row["plenary"],
            "committee": None,
            "plenaryCounts": {
                "attended": counts["attended"],
                "denominator": counts["denominator"],
                "excludedBothLists": counts["excludedBothLists"],
            },
            "reason": reason,
            "checkedOn": checked_on,
            "sourceUrl": LIST_PAGE,
        }
        updated += 1
    if "metadata" in data and isinstance(data["metadata"], dict):
        data["metadata"]["lastUpdated"] = checked_on
        note = data["metadata"].get("note") or ""
        extra = "臺南市大會出席率依第4屆會議紀錄試算，委員會與其餘縣市仍未計算。"
        note = note.replace("其他縣市與委員會仍未計算。", "委員會與其餘縣市仍未計算。")
        if extra not in note:
            data["metadata"]["note"] = (note + " " + extra).strip()
    return updated


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", type=Path, default=Path("/tmp/tncc-plenary-cache"))
    parser.add_argument("--apply", action="store_true", help="寫回 src/data/incumbents.json")
    parser.add_argument("--checked-on", default="2026-11-16")
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)

    meetings = load_meetings()
    print(f"大會場次 {len(meetings)}")
    parsed: list[dict] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(download_one, meeting, args.cache) for meeting in meetings]
        for index, future in enumerate(as_completed(futures), start=1):
            parsed.append(future.result())
            if index % 20 == 0 or index == len(futures):
                print(f"已處理 {index}/{len(futures)}")

    ok = [row for row in parsed if row.get("ok")]
    bad = [row for row in parsed if not row.get("ok")]
    print(f"可解析 {len(ok)}，整場剔除 {len(bad)}")
    for row in bad:
        print(f"  剔除 {row.get('date')} {row.get('session')} {row.get('title')}：{row.get('reason')}")

    data = json.loads(INCUMBENTS_PATH.read_text(encoding="utf-8"))
    people = tainan_candidates(data)
    result = aggregate(ok, people)
    print(f"寫入 {len(result['scored'])}，略過 {len(result['skipped'])}")
    for row in sorted(result["skipped"], key=lambda item: item["name"]):
        print(f"  略過 {row['name']}：{row['reason']}")

    summary_path = args.cache / "summary.json"
    summary_path.write_text(
        json.dumps(
            {
                "meetings": len(meetings),
                "parsed": len(ok),
                "excludedMeetings": [
                    {
                        "date": row.get("date"),
                        "session": row.get("session"),
                        "title": row.get("title"),
                        "reason": row.get("reason"),
                    }
                    for row in bad
                ],
                "scored": result["scored"],
                "skipped": result["skipped"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"摘要 {summary_path}")
    for row in sorted(result["scored"], key=lambda item: item["plenary"]):
        counts = row["plenaryCounts"]
        print(
            f"{row['name']} {row['plenary']}% "
            f"出席{counts['attended']}/分母{counts['denominator']} "
            f"請假{counts['leave']} 缺席{counts['absent']} 剔除{counts['excludedBothLists']}"
        )

    if args.apply:
        if len(ok) < 50 or len(result["scored"]) < 30:
            raise SystemExit("可解析場次或寫入人數過少，未寫入。")
        updated = apply_incumbents(
            data, result["scored"], args.checked_on, len(ok), len(meetings)
        )
        text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        INCUMBENTS_PATH.write_text(text + "\n", encoding="utf-8")
        print(f"已寫入 {updated} 筆到 {INCUMBENTS_PATH}")


if __name__ == "__main__":
    main()
