#!/usr/bin/env python3
"""
Daily Brief Generator v2 — 高质量 RSS 源 + 中文解读
半天一次，抓取最新内容
"""
import datetime
import json
import pathlib
import xml.etree.ElementTree as ET
from urllib.request import urlopen, Request
from html import unescape
from email.utils import parsedate_to_datetime
import re
import sys

ROOT = pathlib.Path(__file__).parent.parent
DATA_DIR = ROOT / 'data'

# ============================================================
# RSS 源配置 — 基于 HN 2025 最热门博客 + kenefe 关注领域
# ============================================================
FEEDS = {
    "AI / 机器学习": [
        # 博客
        ("Simon Willison", "https://simonwillison.net/atom/everything/", "atom"),
        ("Gary Marcus", "https://garymarcus.substack.com/feed", "rss"),
        ("minimaxir", "https://minimaxir.com/index.xml", "rss"),
        # 社区
        ("Hacker News", "https://hnrss.org/frontpage", "rss"),
        ("r/LocalLLaMA", "https://www.reddit.com/r/LocalLLaMA/hot.rss", "atom"),
        ("MIT Tech Review", "https://www.technologyreview.com/feed/", "rss"),
    ],
    "图形 / 渲染": [
        # 博客
        ("Fabien Sanglard", "https://fabiensanglard.net/rss.xml", "rss"),
        ("Ken Righto", "https://www.righto.com/feeds/posts/default", "rss"),
        # 社区
        ("r/GraphicsProgramming", "https://www.reddit.com/r/GraphicsProgramming/hot.rss", "atom"),
        ("r/webgpu", "https://www.reddit.com/r/webgpu/hot.rss", "atom"),
        ("r/opengl", "https://www.reddit.com/r/opengl/hot.rss", "atom"),
    ],
    "系统 / 编程": [
        # 博客（HN 热门）
        ("antirez", "http://antirez.com/rss", "rss"),
        ("Mitchell Hashimoto", "https://mitchellh.com/feed.xml", "rss"),
        ("matklad", "https://matklad.github.io/feed.xml", "rss"),
        ("Rachel by the Bay", "https://rachelbythebay.com/w/atom.xml", "atom"),
        ("Armin Ronacher", "https://lucumr.pocoo.org/feed.atom", "atom"),
        ("Xe Iaso", "https://xeiaso.net/blog.rss", "rss"),
        ("Eli Bendersky", "https://eli.thegreenplace.net/feeds/all.atom.xml", "atom"),
        ("Old New Thing", "https://devblogs.microsoft.com/oldnewthing/feed", "rss"),
    ],
    "设计 / 前端": [
        # 博客
        ("overreacted (Dan Abramov)", "https://overreacted.io/rss.xml", "rss"),
        ("Jim Nielsen", "https://blog.jim-nielsen.com/feed.xml", "rss"),
        ("Geoffrey Litt", "https://www.geoffreylitt.com/feed.xml", "rss"),
        ("Smashing Magazine", "https://www.smashingmagazine.com/feed/", "rss"),
        # 社区
        ("r/web_design", "https://www.reddit.com/r/web_design/hot.rss", "atom"),
    ],
    "Apple / iOS": [
        ("Daring Fireball", "https://daringfireball.net/feeds/main", "rss"),
        ("r/apple", "https://www.reddit.com/r/apple/hot.rss", "atom"),
        ("r/iOSProgramming", "https://www.reddit.com/r/iOSProgramming/hot.rss", "atom"),
    ],
    "互联网 / 科技": [
        # 博客
        ("Paul Graham", "http://www.aaronsw.com/2002/feeds/pgessays.rss", "rss"),
        ("Cory Doctorow", "https://pluralistic.net/feed/", "rss"),
        ("Dwarkesh Patel", "https://www.dwarkeshpatel.com/feed", "rss"),
        ("Krebs on Security", "https://krebsonsecurity.com/feed/", "rss"),
        # 媒体
        ("The Verge", "https://www.theverge.com/rss/index.xml", "atom"),
        ("r/technology", "https://www.reddit.com/r/technology/hot.rss", "atom"),
    ],
}

# 每个分类最多保留的条目数
MAX_PER_SECTION = 8
# 只保留最近 N 天的内容
MAX_AGE_DAYS = 2

def fetch_feed(url, timeout=8):
    """抓取 RSS/Atom feed，缩短超时避免整体卡住"""
    req = Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh) DailyBrief/2.0',
        'Accept': 'application/rss+xml, application/atom+xml, application/xml, text/xml',
    })
    try:
        with urlopen(req, timeout=timeout) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        raise Exception(f"fetch timeout/error: {e}")

def clean_text(text):
    if not text:
        return ""
    text = unescape(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:300] + "..." if len(text) > 300 else text

def parse_date(date_str):
    """尝试解析各种日期格式"""
    if not date_str:
        return None
    try:
        return parsedate_to_datetime(date_str).replace(tzinfo=None)
    except:
        pass
    # ISO 格式
    for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d'):
        try:
            return datetime.datetime.strptime(date_str[:19], fmt)
        except:
            continue
    return None

def parse_atom(xml_str, source_name, limit=10, max_age_days=MAX_AGE_DAYS):
    items = []
    cutoff = datetime.datetime.now() - datetime.timedelta(days=max_age_days)
    try:
        root = ET.fromstring(xml_str)
    except ET.ParseError:
        return items
    
    # 自动检测命名空间
    ns = {}
    if root.tag.startswith('{'):
        ns_uri = root.tag.split('}')[0] + '}'
        ns = {'ns': ns_uri.strip('{}')}
        prefix = 'ns:'
    else:
        prefix = ''
    
    entries = root.findall(f'{prefix}entry', ns) if ns else root.findall('entry')
    
    for entry in entries[:limit * 2]:
        if len(items) >= limit:
            break
        
        # 日期过滤
        updated = entry.find(f'{prefix}updated', ns) if ns else entry.find('updated')
        published = entry.find(f'{prefix}published', ns) if ns else entry.find('published')
        date_el = published if published is not None else updated
        if date_el is not None and date_el.text:
            dt = parse_date(date_el.text)
            if dt and dt < cutoff:
                continue
        
        title_el = entry.find(f'{prefix}title', ns) if ns else entry.find('title')
        link_el = None
        for l in (entry.findall(f'{prefix}link', ns) if ns else entry.findall('link')):
            if l.get('rel', 'alternate') == 'alternate':
                link_el = l
                break
        if link_el is None:
            links = entry.findall(f'{prefix}link', ns) if ns else entry.findall('link')
            link_el = links[0] if links else None
        
        summary_el = entry.find(f'{prefix}summary', ns) if ns else entry.find('summary')
        content_el = entry.find(f'{prefix}content', ns) if ns else entry.find('content')
        
        title = clean_text(title_el.text if title_el is not None else "")
        url = link_el.get('href', '') if link_el is not None else ""
        desc = clean_text((summary_el.text if summary_el is not None else "") or
                         (content_el.text if content_el is not None else ""))
        
        if title and url:
            items.append({"title": title, "desc": desc or "", "url": url, "source": source_name})
    return items

def parse_rss(xml_str, source_name, limit=10, max_age_days=MAX_AGE_DAYS):
    items = []
    cutoff = datetime.datetime.now() - datetime.timedelta(days=max_age_days)
    try:
        root = ET.fromstring(xml_str)
    except ET.ParseError:
        return items
    
    for item in root.findall('.//item'):
        if len(items) >= limit:
            break
        
        pub_date_el = item.find('pubDate')
        if pub_date_el is not None and pub_date_el.text:
            dt = parse_date(pub_date_el.text)
            if dt and dt < cutoff:
                continue
        
        title = clean_text((item.find('title').text if item.find('title') is not None else ""))
        url = item.find('link').text if item.find('link') is not None else ""
        desc = clean_text((item.find('description').text if item.find('description') is not None else ""))
        
        if url and (title or desc):
            items.append({
                "title": title or desc[:60],
                "desc": desc or "",
                "url": url,
                "source": source_name
            })
    return items

def generate():
    """抓取所有源，生成 JSON 数据"""
    now = datetime.datetime.now()
    # 文件名：日期 + 时段（am/pm）
    period = "am" if now.hour < 15 else "pm"
    file_date = now.strftime("%Y-%m-%d")
    filename = f"{file_date}-{period}"
    
    sections = []
    total = 0
    
    for section_name, feeds in FEEDS.items():
        items = []
        for source_name, url, feed_type in feeds:
            try:
                xml_str = fetch_feed(url)
                if feed_type == "atom":
                    parsed = parse_atom(xml_str, source_name)
                else:
                    parsed = parse_rss(xml_str, source_name)
                items.extend(parsed)
                if parsed:
                    print(f"  ✅ {source_name}: {len(parsed)} 条")
                else:
                    print(f"  ⚠️ {source_name}: 0 条（无新内容或解析失败）")
            except Exception as e:
                print(f"  ❌ {source_name}: {e}")
        
        if items:
            # 去重（按 URL）
            seen = set()
            unique = []
            for item in items:
                if item['url'] not in seen:
                    seen.add(item['url'])
                    unique.append(item)
            items = unique[:MAX_PER_SECTION]
            total += len(items)
            sections.append({"title": section_name, "items": items})
    
    data = {
        "date": file_date,
        "period": period,
        "title": "每日科技速览",
        "generated": now.isoformat(),
        "sections": sections
    }
    
    DATA_DIR.mkdir(exist_ok=True)
    
    # 保存带时段的文件
    path = DATA_DIR / f"{filename}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"\n✅ 已生成: {path} ({total} 条)")
    
    # 同时保存为当天最新（兼容旧前端）
    latest = DATA_DIR / f"{file_date}.json"
    latest.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    
    update_index()
    return path

def update_index():
    """更新索引，保留最近 14 天"""
    json_files = sorted(DATA_DIR.glob("202*.json"), reverse=True)
    # 只取日期文件（不含 -am/-pm）
    dates = []
    seen = set()
    for f in json_files:
        date = f.stem[:10]  # YYYY-MM-DD
        if date not in seen and date != "index":
            seen.add(date)
            dates.append(date)
    dates = dates[:14]
    
    index_path = DATA_DIR / "index.json"
    index_path.write_text(json.dumps(dates, indent=2))
    print(f"✅ 索引: {dates[:5]}...")

if __name__ == "__main__":
    generate()
