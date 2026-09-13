"""搜狗搜索抓取器 - 用于发现渠道二/渠道五的URL"""
import requests, re, time, sys, json, urllib.parse

S = requests.Session()
S.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
})

def search_sogou(query, page=1):
    url = f"https://www.sogou.com/web?query={urllib.parse.quote(query)}&page={page}"
    r = S.get(url, timeout=15, allow_redirects=True)
    time.sleep(2)
    return r

def extract_results(html):
    """从搜狗结果页提取 (title, url, snippet)"""
    results = []
    # 搜狗结果块: div.vrwrap / div.txt-box
    blocks = re.findall(r'<div class="vrwrap".*?</div>\s*</div>', html, re.S)
    for b in blocks:
        title_m = re.search(r'<u>(.*?)</u>|<em>(.*?)</em>', b)
        title = re.sub(r'<[^>]+>', '', (title_m.group(1) if title_m and title_m.group(1) else title_m.group(2)) if title_m else "")
        url_m = re.search(r'href="(/?link\?u=|/url\?&amp;query=|/url\?q=|/w[^\s]*?k=[^&]*)([^&"]*)', b)
        snippet_m = re.search(r'class="space-txt[^"]*"[^>]*>(.*?)</div>', b, re.S)
        snippet = re.sub(r'<[^>]+>', '', snippet_m.group(1))[:150] if snippet_m else ""
        results.append({"title": title[:100], "url": url_m.group(0) if url_m else "", "snippet": snippet})
    if not results:
        # 备用提取
        links = re.findall(r'<a[^>]*href="([^"]*sogou[^"]*|/link[^"]*)"[^>]*>([^<]{8,80})</a>', html)
        for href, t in links:
            results.append({"title": t, "url": href, "snippet": ""})
    return results

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "湘潭 大学里 物业"
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    all_results = []
    for p in range(1, max_pages + 1):
        r = search_sogou(query, p)
        print(f"--- page {p} [{r.status_code}] len={len(r.text)}")
        results = extract_results(r.text)
        all_results.extend(results)
        for i, res in enumerate(results[:10]):
            print(f"  {i+1}. {res['title'][:60]}")
            print(f"     {res['url'][:100]}")
            print(f"     {res['snippet'][:100]}")
    json.dump(all_results, open("output/sogou_results.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\nTotal: {len(all_results)} results, saved to output/sogou_results.json")
