#!/usr/bin/env python3
"""
Daily Brief Generator - 从真实 RSS 源抓取新闻，AI 翻译成中文
"""
import datetime
import json
import pathlib
import xml.etree.ElementTree as ET
from urllib.request import urlopen, Request
from html import unescape
import re
import os

ROOT = pathlib.Path(__file__).parent.parent
DATA_DIR = ROOT / 'data'

# Anthropic API
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

def translate_with_ai(items):
    """用 Claude 翻译标题并生成中文简述"""
    if not ANTHROPIC_KEY or not items:
        return items
    
    prompt = "将以下新闻翻译成中文。对每条新闻：1) 翻译标题 2) 用一句话简述内容要点。\n\n"
    for i, item in enumerate(items):
        prompt += f"{i+1}. 标题: {item['title']}\n   原文: {item['desc']}\n\n"
    
    prompt += "返回 JSON 数组，格式: [{\"title\": \"中文标题\", \"desc\": \"一句话简述\"}]，只返回 JSON。"
    
    try:
        import urllib.request
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=json.dumps({
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1500,
                "messages": [{"role": "user", "content": prompt}]
            }).encode(),
            headers={
                "Content-Type": "application/json",
                "x-api-key": ANTHROPIC_KEY,
                "anthropic-version": "2023-06-01"
            }
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            text = result["content"][0]["text"]
            # 提取 JSON
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                translated = json.loads(match.group())
                for i, t in enumerate(translated):
                    if i < len(items):
                        items[i]["title"] = t.get("title", items[i]["title"])
                        items[i]["desc"] = t.get("desc", items[i]["desc"])
    except Exception as e:
        print(f"  ⚠️ 翻译失败: {e}")
    
    return items

# RSS 源配置
FEEDS = {
    "科技": [
        ("The Verge", "https://www.theverge.com/rss/index.xml", "atom"),
        ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/technology-lab", "rss"),
    ],
    "开发者": [
        ("Hacker News", "https://hnrss.org/frontpage", "rss"),
    ],
    "AI": [
        ("MIT Tech Review AI", "https://www.technologyreview.com/feed/", "rss"),
    ],
}

def fetch_feed(url):
    """抓取 RSS/Atom feed"""
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0 DailyBrief/1.0'})
    with urlopen(req, timeout=15) as resp:
        return resp.read().decode('utf-8')

def clean_text(text):
    """清理 HTML 和多余空白"""
    if not text:
        return ""
    text = unescape(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:200] + "..." if len(text) > 200 else text

def parse_atom(xml_str, source_name, limit=3):
    """解析 Atom feed"""
    items = []
    root = ET.fromstring(xml_str)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    
    for entry in root.findall('atom:entry', ns)[:limit]:
        title_el = entry.find('atom:title', ns)
        link_el = entry.find('atom:link[@rel="alternate"]', ns)
        if link_el is None:
            link_el = entry.find('atom:link', ns)
        summary_el = entry.find('atom:summary', ns)
        content_el = entry.find('atom:content', ns)
        
        title = clean_text(title_el.text if title_el is not None else "")
        url = link_el.get('href') if link_el is not None else ""
        desc = clean_text((summary_el.text if summary_el is not None else "") or 
                         (content_el.text if content_el is not None else ""))
        
        if title and url:
            items.append({
                "title": title,
                "desc": desc or "点击查看详情",
                "url": url,
                "source": source_name
            })
    return items

def parse_rss(xml_str, source_name, limit=3):
    """解析 RSS feed"""
    items = []
    root = ET.fromstring(xml_str)
    
    for item in root.findall('.//item')[:limit]:
        title_el = item.find('title')
        link_el = item.find('link')
        desc_el = item.find('description')
        
        title = clean_text(title_el.text if title_el is not None else "")
        url = link_el.text if link_el is not None else ""
        desc = clean_text(desc_el.text if desc_el is not None else "")
        
        if title and url:
            items.append({
                "title": title,
                "desc": desc or "点击查看详情",
                "url": url,
                "source": source_name
            })
    return items

def generate_daily():
    """生成今日报纸数据"""
    today = datetime.date.today().isoformat()
    sections = []
    
    for section_name, feeds in FEEDS.items():
        items = []
        for source_name, url, feed_type in feeds:
            try:
                xml_str = fetch_feed(url)
                if feed_type == "atom":
                    items.extend(parse_atom(xml_str, source_name))
                else:
                    items.extend(parse_rss(xml_str, source_name))
            except Exception as e:
                print(f"  ⚠️ {source_name} 抓取失败: {e}")
        
        if items:
            items = items[:5]  # 每个分类最多5条
            items = translate_with_ai(items)  # AI 翻译
            sections.append({
                "title": section_name,
                "items": items
            })
    
    data = {
        "date": today,
        "title": "每日科技速览",
        "sections": sections
    }
    
    # 保存今日数据
    DATA_DIR.mkdir(exist_ok=True)
    data_path = DATA_DIR / f"{today}.json"
    data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"✅ 已生成: {data_path}")
    
    # 更新索引
    update_index()
    return data_path

def update_index():
    """更新 index.json，保留最近7天"""
    json_files = sorted(DATA_DIR.glob("202*.json"), reverse=True)
    dates = [f.stem for f in json_files if f.stem != "index"][:7]
    
    index_path = DATA_DIR / "index.json"
    index_path.write_text(json.dumps({"dates": dates}, indent=2))
    print(f"✅ 索引已更新: {dates}")

if __name__ == "__main__":
    generate_daily()
