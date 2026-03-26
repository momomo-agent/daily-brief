#!/usr/bin/env python3
"""
Daily Brief Curator — 校验并写入最终 JSON
从 stdin 读取 JSON，校验 schema，写入 data/ 目录
"""
import json
import sys
import pathlib
import datetime

ROOT = pathlib.Path(__file__).parent.parent
DATA_DIR = ROOT / 'data'

# JSON Schema 定义
SCHEMA = {
    "required": ["date", "period", "title", "generated", "headline", "sections"],
    "headline_required": ["title", "desc", "url", "momo"],
    "item_required": ["title", "desc", "url", "source", "momo"],
    "section_required": ["title", "items"],
}


def validate(data):
    """校验 JSON 结构，返回错误列表"""
    errors = []

    # 顶层字段
    for key in SCHEMA["required"]:
        if key not in data:
            errors.append(f"缺少顶层字段: {key}")

    # headline
    if "headline" in data:
        for key in SCHEMA["headline_required"]:
            if key not in data["headline"]:
                errors.append(f"headline 缺少字段: {key}")
        if not data["headline"].get("title", "").startswith("🔥"):
            errors.append("headline.title 必须以 🔥 开头")

    # sections
    if "sections" in data:
        if not isinstance(data["sections"], list) or len(data["sections"]) == 0:
            errors.append("sections 必须是非空数组")
        for i, section in enumerate(data.get("sections", [])):
            for key in SCHEMA["section_required"]:
                if key not in section:
                    errors.append(f"sections[{i}] 缺少字段: {key}")
            for j, item in enumerate(section.get("items", [])):
                for key in SCHEMA["item_required"]:
                    if key not in item:
                        errors.append(f"sections[{i}].items[{j}] 缺少字段: {key}")

    return errors


def main():
    # 从文件参数或 stdin 读取 JSON
    try:
        if len(sys.argv) > 1 and pathlib.Path(sys.argv[1]).exists():
            raw = pathlib.Path(sys.argv[1]).read_text()
        else:
            raw = sys.stdin.read()
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析失败: {e}", file=sys.stderr)
        sys.exit(1)

    # 校验
    errors = validate(data)
    if errors:
        print("❌ Schema 校验失败:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    # 写入文件（ensure_ascii=True 防止特殊字符问题）
    date = data["date"]
    period = data.get("period", "pm")
    DATA_DIR.mkdir(exist_ok=True)

    # 带时段文件
    path = DATA_DIR / f"{date}-{period}.json"
    path.write_text(json.dumps(data, ensure_ascii=True, indent=2))

    # 当天最新文件
    latest = DATA_DIR / f"{date}.json"
    latest.write_text(json.dumps(data, ensure_ascii=True, indent=2))

    # 更新索引
    update_index()

    print(f"✅ 已写入: {path}")
    print(f"✅ 已写入: {latest}")
    total = sum(len(s.get("items", [])) for s in data.get("sections", []))
    print(f"📰 {len(data['sections'])} 个分类, {total} 条新闻")


def update_index():
    """更新索引，保留最近 14 天"""
    json_files = sorted(DATA_DIR.glob("202*.json"), reverse=True)
    dates = []
    seen = set()
    for f in json_files:
        date = f.stem[:10]
        if date not in seen and date != "index":
            seen.add(date)
            dates.append(date)
    dates = dates[:14]
    index_path = DATA_DIR / "index.json"
    index_path.write_text(json.dumps(dates, indent=2))


if __name__ == "__main__":
    main()
