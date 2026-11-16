#!/usr/bin/env python3
"""擷取臺北市議會第 14 屆「大會」會議紀錄，計算現任候選人出席率。

口徑（試點）：
- 只算類別為「大會」的場次。談話會、或抽不出出席／請假名單的場次，整場不計。
- 分子：只出現在出席名單。
- 分母：只出席、只請假，或兩邊都沒有（缺席）。請假留在分母。
- 同一場同時出現在出席與請假：該人該場剔除，不拆日。
- 委員會不計算。其他縣市不改。

依賴：macOS textutil（.doc → 文字）。快取預設在 /tmp，不進版控。
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INCUMBENTS_PATH = ROOT / "src" / "data" / "incumbents.json"
LIST_URL = (
    "https://www.tcc.gov.tw/MeetingMinutes.aspx"
    "?n=13534&kind=2&subkind=816652133AE2F06E&page=1&PageSize=200"
)
LIST_PAGE = "https://www.tcc.gov.tw/MeetingMinutes.aspx?n=13534&kind=2&subkind=816652133AE2F06E"
TERM_URL = "https://www.tcc.gov.tw/TermIntro1.aspx?Term_SN=30&n=13513"
TERM_START = (2022, 12, 25)  # 第14屆就職 111/12/25
UA = "vote2026-taipei-plenary/1.0 (attendance pilot; civic archive)"
PARSER_VERSION = 2

ROW_RE = re.compile(
    r'data-title="屆次會別"[^>]*><span>([^<]*)</span>.*?'
    r'data-title="類別"[^>]*><span>([^<]*)</span>.*?'
    r'href="(MeetingMinutesDetail[^"]+)"[^>]*>([^<]*)</a>.*?'
    r'data-title="資料日期"[^>]*><span>([^<]*)</span>',
    re.S,
)
DOC_RE = re.compile(
    r"https://obasfront\.tcc\.gov\.tw/Agenda/DownloadFile\.aspx\?FileName=([^\"&]+\.doc)&amp;FilePath=([^\"&]+)&amp;FileGrpKind=2"
    r"|https://obasfront\.tcc\.gov\.tw/Agenda/DownloadFile\.aspx\?FileName=([^\"&]+\.doc)&FilePath=([^\"&]+)&FileGrpKind=2"
)
ATTEND_RE = re.compile(r"出席議員[：:](.+?)計\s*(\d+)\s*位", re.S)
LEAVE_RE = re.compile(r"請假議員[：:](.+?)計\s*(\d+)\s*位", re.S)
LEAVE_NONE_RE = re.compile(r"請假議員[：:]\s*無")
NAME_RE = re.compile(r"^[\u4e00-\u9fff]{2,4}$")


def fetch(url: str, timeout: int = 60) -> bytes:
    # 系統 curl 用 macOS 憑證庫；此機的 Python ssl 缺少中間憑證。
    result = subprocess.run(
        ["curl", "-fsSL", "--max-time", str(timeout), "-A", UA, url],
        check=True,
        capture_output=True,
    )
    return result.stdout


def roc_date(text: str) -> tuple[int, int, int]:
    year, month, day = (int(part) for part in text.strip().split("/"))
    return (year + 1911, month, day)


def normalize_name(name: str) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", name))


def names_from_block(block: str) -> list[str]:
    text = unicodedata.normalize("NFKC", block)
    text = re.sub(r"[（(][^）)]*[）)]", " ", text)
    text = text.replace("、", " ").replace("，", " ").replace(",", " ")
    names: list[str] = []
    unknown: list[str] = []
    for token in text.split():
        token = token.strip("　.．、，,;；")
        if not token or token in {"無", "計"}:
            continue
        if NAME_RE.fullmatch(token):
            names.append(token)
            continue
        found = re.findall(r"[\u4e00-\u9fff]{2,4}", token)
        if len(found) == 1 and token == found[0]:
            names.append(found[0])
        else:
            unknown.append(token)
    if unknown:
        raise ValueError("無法拆開的姓名：" + "、".join(unknown))
    return names


def parse_minutes(text: str) -> dict:
    text = unicodedata.normalize("NFKC", text)
    if "談話會" in text[:400]:
        return {"ok": False, "reason": "談話會"}
    attend_match = ATTEND_RE.search(text)
    if not attend_match:
        return {"ok": False, "reason": "沒有可解析的出席議員名單"}
    attended = names_from_block(attend_match.group(1))
    attend_expected = int(attend_match.group(2))
    if len(attended) != attend_expected:
        return {
            "ok": False,
            "reason": f"出席人數不符：解析 {len(attended)}、紀錄計 {attend_expected}",
        }
    # 有的場次無人請假，正文不設「請假議員」段，出席名單後直接接「列席」。
    if LEAVE_NONE_RE.search(text) or "請假" not in text:
        leave: list[str] = []
    else:
        leave_match = LEAVE_RE.search(text)
        if not leave_match:
            return {"ok": False, "reason": "沒有可解析的請假議員名單"}
        leave = names_from_block(leave_match.group(1))
        leave_expected = int(leave_match.group(2))
        if len(leave) != leave_expected:
            return {
                "ok": False,
                "reason": f"請假人數不符：解析 {len(leave)}、紀錄計 {leave_expected}",
            }
    attend_set = set(attended)
    leave_set = set(leave)
    if len(attend_set) != len(attended) or len(leave_set) != len(leave):
        return {"ok": False, "reason": "同一名單出現重複姓名"}
    return {
        "ok": True,
        "attended": sorted(attend_set),
        "leave": sorted(leave_set),
    }


def doc_url_from_detail(html: str) -> str | None:
    match = DOC_RE.search(html)
    if not match:
        return None
    filename = match.group(1) or match.group(3)
    file_path = match.group(2) or match.group(4)
    return (
        "https://obasfront.tcc.gov.tw/Agenda/DownloadFile.aspx"
        f"?FileName={filename}&FilePath={file_path}&FileGrpKind=2"
    )


def doc_to_text(doc_path: Path, txt_path: Path) -> str:
    if txt_path.exists() and txt_path.stat().st_size > 0:
        return txt_path.read_text(encoding="utf-8")
    subprocess.run(
        ["textutil", "-convert", "txt", "-output", str(txt_path), str(doc_path)],
        check=True,
        capture_output=True,
    )
    return txt_path.read_text(encoding="utf-8")


def load_meetings() -> list[dict]:
    html = fetch(LIST_URL).decode("utf-8", "replace")
    rows = []
    seen: set[str] = set()
    for session, kind, href, title, date in ROW_RE.findall(html):
        if kind != "大會":
            continue
        # 談話會與就職典禮不是定期／臨時大會場次。
        if any(word in session or word in title for word in ("談話會", "就職")):
            continue
        sn_match = re.search(r"FileGrpKindSN=([A-F0-9]+)", href)
        if not sn_match:
            continue
        sn = sn_match.group(1)
        if sn in seen:
            continue
        seen.add(sn)
        rows.append(
            {
                "session": session.strip(),
                "title": title.strip(),
                "date": date.strip(),
                "isoDate": roc_date(date),
                "sn": sn,
                "detailUrl": "https://www.tcc.gov.tw/" + href,
            }
        )
    return rows


def original_members() -> set[str]:
    html = fetch(TERM_URL).decode("utf-8", "replace")
    cells = re.findall(r"<td[^>]*>(.*?)</td>", html, re.S)
    texts: list[str] = []
    for cell in cells:
        text = re.sub(r"<[^>]+>", "", cell)
        text = re.sub(r"\s+", "", unicodedata.normalize("NFKC", text))
        texts.append(text)
    start = next(index for index, text in enumerate(texts) if text in {"議員：", "議員:"})
    end = next(index for index, text in enumerate(texts) if index > start and text in {"備註：", "備註:"})
    names = [text for text in texts[start + 1 : end] if NAME_RE.fullmatch(text)]
    # 議長、副議長列在名單欄外，但仍是該屆議員，任期與頁面起迄日相同。
    for label in ("議長", "副議長"):
        index = next(i for i, text in enumerate(texts) if text in {f"{label}：", f"{label}:"})
        officer = next(text for text in texts[index + 1 : index + 4] if NAME_RE.fullmatch(text))
        names.append(officer)
    if len(names) < 50:
        raise SystemExit(f"第14屆議員名單過短：{len(names)}")
    return set(names)


def taipei_candidates(data: dict) -> list[dict]:
    people = []
    for key, entry in data.items():
        if not key.startswith("臺北市|") or not isinstance(entry, dict):
            continue
        if not entry.get("incumbency", {}).get("publish"):
            continue
        parts = key.split("|")
        roster = entry.get("incumbency", {}).get("rosterName") or parts[3]
        people.append(
            {
                "key": key,
                "name": normalize_name(parts[3]),
                "rosterName": normalize_name(roster) if roster else normalize_name(parts[3]),
                "district": parts[2],
            }
        )
    return people


def download_one(meeting: dict, cache: Path) -> dict:
    sn = meeting["sn"]
    doc_path = cache / f"{sn}.doc"
    txt_path = cache / f"{sn}.txt"
    meta_path = cache / f"{sn}.json"
    if meta_path.exists():
        cached = json.loads(meta_path.read_text(encoding="utf-8"))
        if cached.get("parserVersion") == PARSER_VERSION:
            cached["meeting"] = meeting
            return cached
    try:
        if txt_path.exists() and txt_path.stat().st_size > 0 and doc_path.exists():
            text = txt_path.read_text(encoding="utf-8")
            url = None
            if meta_path.exists():
                url = json.loads(meta_path.read_text(encoding="utf-8")).get("docUrl")
            parsed = parse_minutes(text)
            result = {**parsed, "docUrl": url}
        else:
            detail_html = fetch(meeting["detailUrl"]).decode("utf-8", "replace")
            url = doc_url_from_detail(detail_html)
            if not url:
                result = {"ok": False, "reason": "詳細頁沒有 .doc", "docUrl": None}
            else:
                if not doc_path.exists() or doc_path.stat().st_size < 100:
                    doc_path.write_bytes(fetch(url))
                text = doc_to_text(doc_path, txt_path)
                parsed = parse_minutes(text)
                result = {**parsed, "docUrl": url}
    except Exception as exc:  # noqa: BLE001 — 單場失敗不中斷整批
        result = {"ok": False, "reason": f"下載或解析失敗：{exc}", "docUrl": None}
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
        "detailUrl": meeting["detailUrl"],
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    meta["meeting"] = meeting
    return meta


def aggregate(meetings: list[dict], people: list[dict], originals: set[str]) -> dict:
    scored = []
    skipped = []
    for person in people:
        names = {person["name"], person["rosterName"]}
        if not names & originals:
            skipped.append({**person, "reason": "不在第14屆官網議員名單，就任日無法確定"})
            continue
        attended = 0
        denominator = 0
        excluded_both = 0
        leave_only = 0
        absent = 0
        for meeting in meetings:
            if not meeting.get("ok"):
                continue
            if tuple(meeting["meeting"]["isoDate"]) < TERM_START:
                continue
            present = names & set(meeting["attended"])
            leave = names & set(meeting["leave"])
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
        if denominator == 0 or attended + leave_only + excluded_both == 0:
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


def apply_incumbents(data: dict, scored: list[dict], checked_on: str) -> int:
    by_key = {row["key"]: row for row in scored}
    reason = (
        "第14屆大會議事錄：出席場次÷應出席場次（請假與缺席留在分母；"
        "同一場同時列入出席與請假者不計）。委員會未計算。"
    )
    updated = 0
    for key, row in by_key.items():
        entry = data[key]
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
        extra = "臺北市大會出席率依第14屆會議紀錄試算，其他縣市與委員會仍未計算。"
        if extra not in note:
            data["metadata"]["note"] = (note + " " + extra).strip()
    return updated


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", type=Path, default=Path("/tmp/tcc-plenary-cache"))
    parser.add_argument("--apply", action="store_true", help="寫回 src/data/incumbents.json")
    parser.add_argument("--checked-on", default="2026-11-16")
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)

    meetings = load_meetings()
    print(f"大會場次 {len(meetings)}")
    originals = original_members()
    print(f"第14屆官網名單 {len(originals)} 人")

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
    people = taipei_candidates(data)
    result = aggregate(ok, people, originals)
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
                        "detailUrl": row.get("detailUrl"),
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

    for row in sorted(result["scored"], key=lambda item: item["plenary"])[:8]:
        counts = row["plenaryCounts"]
        print(
            f"{row['name']} {row['plenary']}% "
            f"出席{counts['attended']}/分母{counts['denominator']} "
            f"請假{counts['leave']} 缺席{counts['absent']} 剔除{counts['excludedBothLists']}"
        )

    if args.apply:
        updated = apply_incumbents(data, result["scored"], args.checked_on)
        INCUMBENTS_PATH.write_text(
            json.dumps(data, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        print(f"已寫入 {updated} 筆到 {INCUMBENTS_PATH}")


if __name__ == "__main__":
    main()
