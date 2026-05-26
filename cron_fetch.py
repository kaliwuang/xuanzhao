#!/usr/bin/env python3
"""AI + Finance news tracker - cron job data fetcher"""
import urllib.request, urllib.error
import re, json, sys
from datetime import datetime
from html import unescape

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
TIMEOUT = 15

def fetch(url, timeout=TIMEOUT):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode('utf-8', 'ignore')
    except Exception as e:
        return f"[ERROR: {e}]"

def fetch_gbk(url, timeout=TIMEOUT):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            return raw.decode('gbk', 'ignore')
    except Exception as e:
        return f"[ERROR: {e}]"

def parse_rss_titles(content, max_items=10):
    items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
    results = []
    for it in items[:max_items]:
        t = re.search(r'<title>(.*?)</title>', it)
        d = re.search(r'<pubDate>(.*?)</pubDate>', it)
        if t:
            txt = re.sub(r'<[^>]+>', '', t.group(1)).strip()
            txt = unescape(txt)
            txt = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), txt)
            date = d.group(1)[:16] if d else ''
            results.append((txt, date))
    return results

def parse_rss_cdata(content, max_items=10):
    items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
    results = []
    for it in items[:max_items]:
        t = re.search(r'<title>(.*?)</title>', it)
        d = re.search(r'<pubDate>(.*?)</pubDate>', it)
        if t:
            txt = re.sub(r'<[^>]+>', '', t.group(1)).strip()
            txt = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', txt)
            txt = unescape(txt)
            date = d.group(1)[:16] if d else ''
            results.append((txt, date))
    return results

out = []

out.append("\n=== IT之家 RSS ===")
ithome = fetch("https://www.ithome.com/rss")
ithome_items = parse_rss_titles(ithome, 10)
for t, d in ithome_items:
    kl = any(k in t for k in ['AI','ai','智能','模型','芯片','GPT','大模型','算法','数据','自动驾驶','机器人','字节','百度','阿里','腾讯','华为','小米'])
    if kl:
        out.append(f"[AI] {t}")
    else:
        out.append(f"[科技] {t}")

out.append("")
out.append("=== Ars Technica ===")
ars = fetch("https://feeds.arstechnica.com/arstechnica/technology-lab")
ars_items = parse_rss_titles(ars, 8)
for t, d in ars_items:
    if any(k in t.lower() for k in ['ai','llm','gpt','model','openai','claude','neural','deep','agent','robot','chip','compute']):
        out.append(f"[AI] {t}")
if not ars_items:
    out.append("(empty)")

out.append("")
out.append("=== MIT Tech Review ===")
mit = fetch("https://www.technologyreview.com/feed/")
mit_items = parse_rss_cdata(mit, 6)
for t, d in mit_items:
    out.append(f"[MIT] {t}")

out.append("")
out.append("=== AI News RSS ===")
ainews = fetch("https://www.artificialintelligence-news.com/feed/")
ai_items = parse_rss_titles(ainews, 6)
for t, d in ai_items:
    out.append(t)

out.append("")
out.append("=== Market Data ===")
mkt = fetch_gbk("https://qt.gtimg.cn/q=sh000001,sz399001,hkHSI,usDJI,usNDX")
for line in mkt.strip().split(';'):
    if '=' in line and line.strip():
        parts = line.split('=')[1].strip().strip('"').split('~')
        if len(parts) >= 33:
            name = parts[1]
            price = parts[3]
            change = parts[32]
            out.append(f"{name}: {price} ({change}%)")
        else:
            out.append(f"p={parts[1] if len(parts)>1 else '?'}")

out.append("")
out.append("=== CNBC ===")
cnbc = fetch("https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114")
cnbc_items = parse_rss_titles(cnbc, 8)
for t, d in cnbc_items:
    out.append(t)

out.append("")
out.append("=== GitHub: Established ===")
try:
    content = fetch("https://api.github.com/search/repositories?q=AI+OR+LLM+OR+agent+language:python&sort=stars&per_page=8")
    if not content.startswith("[ERROR"):
        data = json.loads(content)
        for item in data.get('items', [])[:5]:
            out.append(f"{item['full_name']}: ★{item['stargazers_count']} | {item.get('description','')[:60]}")
    else:
        out.append(f"Error: {content}")
except Exception as e:
    out.append(f"Error: {e}")

out.append("")
out.append("=== GitHub: Today's new ===")
try:
    url = f"https://api.github.com/search/repositories?q=created:2026-05-26&sort=stars&order=desc&per_page=8"
    content = fetch(url)
    if not content.startswith("[ERROR"):
        data = json.loads(content)
        for item in data.get('items', [])[:5]:
            desc = item.get('description','') or ''
            out.append(f"{item['full_name']}: ★{item['stargazers_count']} | {desc[:60]}")
    else:
        out.append(f"Error: {content}")
except Exception as e:
    out.append(f"Error: {e}")

out.append("")
out.append("=== 36kr ===")
try:
    kr36 = fetch("https://36kr.com/feed", timeout=10)
    if not kr36.startswith("[ERROR"):
        items36 = re.findall(r'<item>(.*?)</item>', kr36, re.DOTALL)
        for it in items36[:10]:
            t = re.search(r'<title>(.*?)</title>', it)
            if t:
                txt = re.sub(r'<[^>]+>', '', t.group(1)).strip()
                txt = unescape(txt)
                out.append(txt)
    else:
        out.append(kr36)
except Exception as e:
    out.append(f"Error: {e}")

out.append("")
out.append("=== Hacker News (AI) ===")
try:
    hn = fetch("https://hn.algolia.com/api/v1/search?query=AI+OR+breakthrough+OR+LLM+OR+agent&tags=story&hitsPerPage=10")
    if not hn.startswith("[ERROR"):
        data = json.loads(hn)
        for h in data.get('hits', [])[:8]:
            out.append(h['title'])
    else:
        out.append(hn)
except Exception as e:
    out.append(f"Error: {e}")

out.append("")
out.append("=== WSJ Markets ===")
wsj = fetch("https://feeds.a.dj.com/rss/RSSMarketsMain.xml")
wsj_items = parse_rss_titles(wsj, 6)
for t, d in wsj_items:
    out.append(t)

out.append("")
out.append("=== VentureBeat ===")
vb = fetch("https://venturebeat.com/category/ai/feed/")
vb_items = parse_rss_titles(vb, 6)
for t, d in vb_items:
    out.append(t)

print('\n'.join(out))
