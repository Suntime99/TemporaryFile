"""各渠道数据抓取脚本 - 小区自管番外篇素材采集"""
import requests, re, json, time, urllib.parse, sys

S = requests.Session()
S.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
})

def clean(html):
    """去HTML标签提取正文"""
    html = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.S|re.I)
    text = re.sub(r'<[^>]+>', '\n', html)
    text = re.sub(r'\n{2,}', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def search_rednet(keyword):
    """红网百姓呼声搜索"""
    url = f"https://people.rednet.cn/search?keyword={urllib.parse.quote(keyword)}"
    r = S.get(url, timeout=15, allow_redirects=True)
    time.sleep(3)
    return r.status_code, r.text

def get(url):
    r = S.get(url, timeout=15, allow_redirects=True)
    time.sleep(2)
    return r.status_code, r.text

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"

    if mode in ("all", "rednet"):
        print("=" * 60)
        print("渠道二：红网百姓呼声")
        print("=" * 60)
        for kw in ["大学里小区", "金鼎物业", "大学里 停水", "大学里 承接查验"]:
            try:
                code, html = search_rednet(kw)
                text = clean(html)
                print(f"\n### 关键词: {kw} [{code}]")
                print(text[:3000])
            except Exception as e:
                print(f"  FAIL: {type(e).__name__} {e}")

    if mode in ("all", "fangtianxia"):
        print("\n" + "=" * 60)
        print("渠道四：房天下湘潭 - 大学里小区")
        print("=" * 60)
        # 搜索房天下小区
        url = "https://xfngd.fang.com/xiaoqu/"  # 湘潭二手房
        try:
            code, html = get("https://xt.esf.fang.com/house/")
            text = clean(html)
            print(f"[{code}]", text[:2000])
        except Exception as e:
            print(f"  FAIL: {type(e).__name__} {e}")
