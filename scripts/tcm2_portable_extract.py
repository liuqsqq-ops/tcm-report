#!/usr/bin/env python3
"""
TCM2 portable extractor for Windows-oriented skill delivery.

用途：
- 单班稳定提取 TCM2 闯关报告
- 由 PowerShell 包装器或 agent 调用
- 核心逻辑跨平台，但交付默认面向 Windows

依赖：
    py -m pip install websocket-client

示例：
    python tcm2_portable_extract.py --class-id 60018 --class-name QV848 --total 26
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import websocket  # type: ignore

CDP_HTTP = "http://127.0.0.1:9222"
CLASS_META = {
    "QV848": {"class_id": "60018", "total": 26, "stage": "大侠7段 + 书童2段"},
    "JJ014": {"class_id": "60024", "total": 21, "stage": "少侠6段 + 书童1段"},
    "VD241": {"class_id": "60056", "total": 26, "stage": "少侠6段 + 书童1段"},
    "RB881": {"class_id": "120003", "total": 20, "stage": "少侠6段 + 书童1段"},
    "RL526": {"class_id": "180020", "total": 25, "stage": "少侠4段"},
}


@dataclass
class CDPSession:
    ws: Any
    msg_id: int = 0

    def call(self, method: str, params: Optional[dict] = None, *, return_value: bool = False):
        self.msg_id += 1
        self.ws.send(json.dumps({"id": self.msg_id, "method": method, "params": params or {}}))
        while True:
            raw = json.loads(self.ws.recv())
            if raw.get("id") == self.msg_id:
                if return_value:
                    return raw.get("result", {}).get("result", {}).get("value")
                return raw.get("result")

    def eval(self, expression: str):
        return self.call("Runtime.evaluate", {"expression": expression, "returnByValue": True}, return_value=True)


def http_json(url: str):
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.loads(r.read())


def get_targets() -> list:
    return http_json(f"{CDP_HTTP}/json")


def new_target(url: str) -> dict:
    encoded = urllib.parse.quote(url, safe="")
    return http_json(f"{CDP_HTTP}/json/new?{encoded}")


def close_target(target_id: str):
    if not target_id:
        return
    try:
        urllib.request.urlopen(f"{CDP_HTTP}/json/close/{target_id}", timeout=10).read()
    except Exception:
        pass


def attach_target(target: dict) -> CDPSession:
    ws = websocket.create_connection(target["webSocketDebuggerUrl"], timeout=15)
    ws.settimeout(15)
    sess = CDPSession(ws)
    sess.call("Page.enable")
    sess.call("Runtime.enable")
    return sess


def parse_cookie_user_id(cookie: str) -> Optional[str]:
    m = re.search(r"(?:^|;\s*)user_id=([^;]+)", cookie)
    return m.group(1) if m else None


def compute_window(now: Optional[datetime] = None) -> Tuple[datetime, str]:
    now = now or datetime.now()
    if now.hour < 12:
        start = now.replace(hour=17, minute=0, second=0, microsecond=0) - timedelta(days=1)
    elif now.hour < 17:
        start = now.replace(hour=12, minute=0, second=0, microsecond=0)
    else:
        start = now.replace(hour=17, minute=0, second=0, microsecond=0)
    win = f"{start.month}月{start.day}日 {start.strftime('%H:%M')} → 现在"
    return start, win


def wait_for_detail_ready(sess: CDPSession, class_name: str, *, retries: int = 2) -> bool:
    check_js = f"""
    (function(){{
      var body=(document.body&&document.body.innerText||'');
      var tabs=document.querySelectorAll('.el-tabs__item').length;
      var levels=document.querySelectorAll('button.level').length;
      return JSON.stringify({{
        hash: location.hash,
        tabs: tabs,
        levels: levels,
        hasClass: body.indexOf('{class_name}') >= 0,
        hasRoster: body.indexOf('战队花名册') >= 0,
        bodyPreview: body.slice(0, 300)
      }});
    }})()
    """
    for attempt in range(retries + 1):
        time.sleep(4 if attempt == 0 else 5)
        raw = sess.eval(check_js)
        try:
            info = json.loads(raw)
        except Exception:
            info = {}
        ok = info.get("tabs", 0) > 0 and info.get("hasClass") and info.get("hasRoster")
        if ok:
            return True
        sess.call("Page.reload", {"ignoreCache": True})
    return False


def click_record_tab(sess: CDPSession) -> bool:
    js = """
    (function(){
      var tabs=document.querySelectorAll('.el-tabs__item');
      for(var i=0;i<tabs.length;i++){
        if((tabs[i].textContent||'').indexOf('闯关记录')>=0){tabs[i].click();return true;}
      }
      return false;
    })()
    """
    ok = bool(sess.eval(js))
    if ok:
        time.sleep(3)
    return ok


def get_week_label(sess: CDPSession) -> str:
    txt = sess.eval("document.querySelector('.week-item.is-active .el-radio-button__inner')?.textContent?.trim() || ''") or ""
    m = re.search(r"第\d+周", txt)
    return m.group(0) if m else "第?周"


def get_level_buttons(sess: CDPSession) -> List[str]:
    raw = sess.eval("JSON.stringify(Array.from(document.querySelectorAll('button.level')).filter(function(b){return b.offsetParent!==null}).map(function(b){return b.textContent.trim()}))")
    return json.loads(raw or "[]")


def click_level(sess: CDPSession, level_label: str) -> bool:
    safe = level_label.replace("'", "\\'")
    js = f"""
    (function(){{
      var bs=document.querySelectorAll('button.level');
      for(var i=0;i<bs.length;i++){{
        var t=(bs[i].textContent||'').trim();
        if(t.indexOf('{safe}')>=0){{bs[i].click();return true;}}
      }}
      return false;
    }})()
    """
    return bool(sess.eval(js))


def parse_level_meta(btn_text: str) -> Tuple[str, str, str]:
    m = re.match(r"(.+?)#(第\d+关卡)\(([^)]*)\)", btn_text)
    if not m:
        return "未知阶段", btn_text, "?%"
    return m.group(1), m.group(2), m.group(3)


def read_visible_table_payload(sess: CDPSession) -> dict:
    js = """
    (function(){
      var ts=document.querySelectorAll('.el-table');
      for(var i=0;i<ts.length;i++){
        if(ts[i].offsetParent===null) continue;
        var vm=ts[i].__vue__;
        var p=vm && vm.$parent;
        var rows=(p && p.list) || (vm && vm.tableData) || [];
        return JSON.stringify({
          rows: rows,
          lessonId: p && p.query ? p.query.lessonId : null,
          classId: p && p.query ? p.query.classId : null,
          startDate: p && p.query ? p.query.startDate : null
        });
      }
      return JSON.stringify({rows:[]});
    })()
    """
    raw = sess.eval(js) or '{"rows":[]}'
    return json.loads(raw)


def normalize_rows(payload: dict) -> List[dict]:
    out = []
    for r in payload.get("rows", []) or []:
        if not isinstance(r, list) or len(r) < 7:
            continue
        out.append({
            "userCode": str(r[0]).strip() if len(r) > 0 and r[0] is not None else "",
            "name": str(r[1]).strip() if len(r) > 1 and r[1] is not None else "",
            "en": str(r[2]).strip() if len(r) > 2 and r[2] is not None else "",
            "status": str(r[3]).strip() if len(r) > 3 and r[3] is not None else "",
            "detail": str(r[4]).strip() if len(r) > 4 and r[4] is not None else "",
            "start": str(r[5]).strip() if len(r) > 5 and r[5] is not None else "",
            "end": str(r[6]).strip() if len(r) > 6 and r[6] is not None else "",
            "userId": str(r[11]).strip() if len(r) > 11 and r[11] is not None else "",
        })
    return out


def row_signature(rows: List[dict]) -> str:
    slim = [(r["name"], r["en"], r["status"], r["end"]) for r in rows]
    return json.dumps(slim, ensure_ascii=False, sort_keys=False)


def classify_counts(rows: List[dict]) -> Tuple[int, int, int]:
    done = sum(1 for r in rows if r["status"] == "已完成")
    ing = sum(1 for r in rows if r["status"] == "闯关中")
    noty = sum(1 for r in rows if r["status"] == "未闯关")
    return done, ing, noty


def stable_extract_level(sess: CDPSession, btn_text: str, total_students: int, *, attempts: int = 5) -> List[dict]:
    good: List[List[dict]] = []
    sigs: List[str] = []
    if not click_level(sess, btn_text):
        return []
    for _ in range(attempts):
        time.sleep(1.4)
        a = normalize_rows(read_visible_table_payload(sess))
        time.sleep(1.2)
        b = normalize_rows(read_visible_table_payload(sess))
        for rows in (a, b):
            if not rows:
                continue
            done, ing, noty = classify_counts(rows)
            if done + ing + noty != len(rows):
                continue
            if total_students and len(rows) not in (total_students, 0):
                continue
            good.append(rows)
            sigs.append(row_signature(rows))
        if len(sigs) >= 2 and sigs[-1] == sigs[-2]:
            return good[-1]
    if not good:
        return []
    winner = Counter(sigs).most_common(1)[0][0]
    for rows in good:
        if row_signature(rows) == winner:
            return rows
    return good[-1]


def parse_dt(s: str) -> Optional[datetime]:
    s = (s or "").strip()
    if not s or s == "--":
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s[:19], fmt)
        except Exception:
            pass
    return None


def build_report(class_name: str, stage_text: str, total_students: int, week_label: str, all_data: List[dict]) -> str:
    start, win = compute_window()
    title = f"📊 **{class_name} {stage_text}（{total_students}人）| {datetime.now().strftime('%m月%d日')} {win} | {week_label}**"
    lines = [title, ""]
    active_best: Dict[str, dict] = {}

    stages: Dict[str, List[dict]] = {}
    for item in all_data:
        stages.setdefault(item["stage"], []).append(item)

    def level_num(x: dict) -> int:
        m = re.search(r'第(\d+)关卡', x['level'])
        return int(m.group(1)) if m else 0

    for stage in stages:
        stages[stage].sort(key=level_num)

    for stage in sorted(stages.keys(), key=lambda s: ('书童' in s, s)):
        prev_fail_count = None
        prev_fail_names: set = set()
        for idx, item in enumerate(stages[stage]):
            rows = item["rows"]
            done, ing, noty = classify_counts(rows)
            lines.append(f"**{stage}#{item['level']}（{item['pct']}）：** ✅{done} 🔄{ing} ❌{noty}")

            show_names = idx == 0 or ((prev_fail_count or 0) < 10)
            if show_names:
                ing_names = [f"{r['name']}({r['en']})" for r in rows if r['status'] == '闯关中' and f"{r['name']}({r['en']})" not in prev_fail_names]
                not_names = [f"{r['name']}({r['en']})" for r in rows if r['status'] == '未闯关' and f"{r['name']}({r['en']})" not in prev_fail_names]
                if ing_names:
                    lines.append(f"  🔄 闯关中：{'、'.join(ing_names)}")
                if not_names:
                    lines.append(f"  ❌ 未闯关：{'、'.join(not_names)}")
                prev_fail_names = set(ing_names + not_names)
            prev_fail_count = noty

            lvl = level_num(item)
            for r in rows:
                dt = parse_dt(r["end"])
                if not dt or dt < start:
                    continue
                key = r["name"] + "|" + r["en"]
                cand = {
                    "student": f"{r['name']}（{r['en']}）",
                    "level": item["level"],
                    "status": r["status"],
                    "time": r["end"],
                    "lvl_num": lvl,
                }
                old = active_best.get(key)
                if old is None:
                    active_best[key] = cand
                elif cand["status"] == "闯关中" and old["status"] != "闯关中":
                    active_best[key] = cand
                elif cand["status"] == old["status"] and cand["lvl_num"] > old["lvl_num"]:
                    active_best[key] = cand
                elif cand["status"] == old["status"] and cand["lvl_num"] == old["lvl_num"] and cand["time"] > old["time"]:
                    active_best[key] = cand
            lines.append("")

    lines.append("### 🟢 活跃学生")
    lines.append("| 学生 | 关卡 | 状态 | 更新时间 |")
    lines.append("|------|------|------|----------|")
    if active_best:
        for a in sorted(active_best.values(), key=lambda x: (x["lvl_num"], x["student"])):
            lines.append(f"| {a['student']} | {a['level']} | {a['status']} | {a['time']} |")
    else:
        lines.append("| 无 | - | - | - |")

    return "\n".join(lines)


def open_detail_page(emp_id: str, class_id: str, class_name: str) -> dict:
    my_url = f"https://tcm2.dayuan1997.com/#/class/my/{emp_id}"
    try:
        _ = new_target(my_url)
    except Exception:
        pass
    detail_url = f"https://tcm2.dayuan1997.com/#/class/detail/{class_id}?$tag={class_name}"
    return new_target(detail_url)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--class-id", required=True)
    ap.add_argument("--class-name", required=True)
    ap.add_argument("--total", type=int, default=0)
    ap.add_argument("--stage", default="")
    args = ap.parse_args()

    try:
        targets = get_targets()
    except Exception as e:
        print(f"ERROR: cannot reach {CDP_HTTP}/json : {e}", file=sys.stderr)
        sys.exit(2)

    if not targets:
        print("ERROR: no CDP targets found", file=sys.stderr)
        sys.exit(2)

    tcm2 = next((t for t in targets if 'tcm2.dayuan1997.com' in t.get('url', '')), None)
    if not tcm2:
        tcm2 = new_target('https://tcm2.dayuan1997.com/')
        time.sleep(3)

    base = attach_target(tcm2)
    cookie = base.eval("document.cookie") or ""
    if "user_id=" not in cookie or "token=" not in cookie:
        print("ERROR: TCM2 not logged in; document.cookie missing user_id/token", file=sys.stderr)
        sys.exit(3)
    emp_id = parse_cookie_user_id(cookie)
    if not emp_id:
        print("ERROR: cannot parse user_id from cookie", file=sys.stderr)
        sys.exit(3)

    target = open_detail_page(emp_id, args.class_id, args.class_name)
    sess = attach_target(target)
    try:
        if not wait_for_detail_ready(sess, args.class_name, retries=2):
            print(f"ERROR: detail page not ready for {args.class_name}", file=sys.stderr)
            sys.exit(4)
        if not click_record_tab(sess):
            print("ERROR: cannot click 闯关记录 tab", file=sys.stderr)
            sys.exit(5)

        week_label = get_week_label(sess)
        levels = get_level_buttons(sess)
        if not levels:
            print("ERROR: no visible button.level found", file=sys.stderr)
            sys.exit(6)

        stage_text = args.stage or CLASS_META.get(args.class_name, {}).get("stage", "")
        total = args.total or CLASS_META.get(args.class_name, {}).get("total", 0)

        all_data = []
        for btn in levels:
            rows = stable_extract_level(sess, btn, total_students=total, attempts=5)
            if not rows:
                continue
            stage, level, pct = parse_level_meta(btn)
            all_data.append({"stage": stage, "level": level, "pct": pct, "rows": rows})

        if not all_data:
            print("ERROR: extracted zero level datasets", file=sys.stderr)
            sys.exit(7)

        print(build_report(args.class_name, stage_text, total, week_label, all_data))
    finally:
        try:
            sess.ws.close()
        except Exception:
            pass
        close_target(target.get("id", ""))


if __name__ == "__main__":
    main()
