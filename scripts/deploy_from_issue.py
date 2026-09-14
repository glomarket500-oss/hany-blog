import os, re, subprocess, json
from datetime import datetime

REPO = os.path.join(os.path.expanduser("~"), "Desktop", "hany-blog")
PUB = os.path.join(os.path.expanduser("~"), "Desktop", "MianAI知识库", "MianAI知识库", "vault", "hany博主", "已發布")
ART = os.path.join(REPO, "articles")
IMG = os.path.join(REPO, "images")

simple = "国业会区发过这时间个们为来从对开关内与产种样应该说话请让记认识变两万亿后里现进动问点岁车长门听见读写买卖贵价总经营员报导师学习电视机场馆饭楼层号节条约结订单货运输达选择称谢务账帮专极确实际议译药观觉览响语师"
trad = "國業會區發過這時間個們為來從對開關內與產種樣應該說話請讓記認識變兩萬億後裏現進動問題點歲車長門聽見讀寫買賣貴價總經營員報導師學習電視機場館飯樓層號節條約結訂單貨運輸送達選擇稱謝務賬幫專極確實際議譯藥觀覺覽響語師"
S2T = dict(zip(simple, trad))


def s2t(s):
    return "".join(S2T.get(c, c) for c in s)


def esc(s):
    return s.replace("&", "&").replace("<", "<").replace(">", ">").replace('"', '"')


def make_html(content, title, date_str, article_id):
    body = re.sub(r"^#\s+.*?\n", "", content, count=1)
    body = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", body)

    h2s = re.findall(r"^##\s+(.+)$", body, re.MULTILINE)
    toc = ""
    if h2s:
        items = "".join(
            '<li><a href="#sec' + str(i + 1) + '">' + esc(s2t(h)) + '</a></li>'
            for i, h in enumerate(h2s)
        )
        toc = '<nav class="toc"><h3>Contents</h3><ol>' + items + '</ol></nav>'

    parts = []
    idx = 0
    for p in body.strip().split("\n\n"):
        p = p.strip()
        if not p:
            continue
        if p.startswith("## "):
            idx += 1
            parts.append('<h2 id="sec' + str(idx) + '">' + esc(s2t(p[3:])) + '</h2>')
        elif p.startswith("### "):
            parts.append("<h3>" + esc(s2t(p[4:])) + "</h3>")
        elif p.startswith("> "):
            parts.append("<blockquote>" + esc(s2t(p[2:])) + "</blockquote>")
        else:
            parts.append("<p>" + esc(s2t(p)).replace("\n", "<br>") + "</p>")
    body_html = "\n".join(parts)

    em = re.search(r"^#\s+.+?\n\n(.+?)\n\n", content, re.DOTALL)
    desc = s2t(em.group(1)[:160]) if em else s2t(title)

    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": s2t(title),
        "datePublished": date_str,
        "dateModified": date_str,
        "author": {"@type": "Person", "name": "Hai Ge"},
        "inLanguage": "zh-HK",
        "description": desc
    }

    meta = (
        '<meta name="description" content="' + esc(desc) + '">\n'
        '  <meta property="og:title" content="' + esc(s2t(title)) + '">\n'
        '  <meta property="og:description" content="' + esc(desc) + '">\n'
        '  <meta property="og:type" content="article">\n'
        '  <meta property="og:url" content="https://glomarket.vercel.app/articles/' + article_id + '.html">\n'
        '  <link rel="canonical" href="https://glomarket.vercel.app/articles/' + article_id + '.html">\n'
        '  <script type="application/ld+json">\n  ' + json.dumps(schema, ensure_ascii=False, indent=2) + '\n  </script>'
    )

    css = (
        'body { font-family: "Noto Sans HK", sans-serif; max-width: 760px; margin: 0 auto; padding: 20px; line-height: 1.9; color: #2a2a2a; background: #fafafa; } '
        '.progress { position: fixed; top: 0; left: 0; height: 3px; background: #e94560; z-index: 1000; } '
        '.post-header { border-bottom: 2px solid #1a1a2e; padding-bottom: 20px; margin-bottom: 30px; } '
        'h1 { font-size: 1.9rem; color: #1a1a2e; margin-bottom: 12px; } '
        '.post-meta { font-size: 0.9rem; color: #888; } '
        '.toc { background: #fff; padding: 16px 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #e94560; } '
        '.toc h3 { margin: 0 0 10px; font-size: 1rem; } '
        '.toc ol { margin-left: 20px; } '
        'h2 { color: #1a1a2e; margin-top: 2em; font-size: 1.4rem; border-left: 4px solid #e94560; padding-left: 12px; scroll-margin-top: 20px; } '
        'h3 { color: #1a1a2e; margin-top: 1.4em; } '
        'blockquote { border-left: 4px solid #ddd; padding: 12px 16px; color: #555; background: #f5f5f7; } '
        '.cta-wa { display: inline-block; margin: 30px 0; padding: 14px 28px; background: #25D366; color: #fff; text-decoration: none; border-radius: 8px; font-weight: 600; } '
        '.back-top { display: none; position: fixed; bottom: 30px; right: 30px; width: 44px; height: 44px; background: #1a1a2e; color: #fff; border: none; border-radius: 50%; cursor: pointer; align-items: center; justify-content: center; font-size: 1.2rem; } '
        'footer { margin-top: 60px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #999; font-size: 0.85rem; } '
        '.back { display: inline-block; margin-bottom: 20px; padding: 8px 16px; background: #1a1a2e; color: #fff; text-decoration: none; border-radius: 6px; font-size: 0.9rem; }'
    )

    return (
        '<!DOCTYPE html>\n<html lang="zh-HK">\n<head>\n'
        '<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>' + esc(s2t(title)) + ' | Hai Ge Blog</title>\n'
        + meta + '\n'
        '<style>' + css + '</style>\n</head>\n<body>\n'
        '<div class="progress" id="progress"></div>\n'
        '<a href="/" class="back">home</a>\n'
        '<article class="post-header">\n<h1>' + esc(s2t(title)) + '</h1>\n'
        '<div class="post-meta">date: ' + date_str + ' | author: Hai Ge</div>\n</article>\n'
        + toc + '\n'
        '<div class="post-body">\n' + body_html + '\n</div>\n'
        '<a href="https://wa.me/85200000000" class="cta-wa" target="_blank">Chat on WhatsApp</a>\n'
        '<button class="back-top" id="backTop" onclick="window.scrollTo({top:0,behavior:\'smooth\'})">up</button>\n'
        '<footer><p>copyright 2026 Hai Ge</p></footer>\n'
        '<script>window.addEventListener("scroll", function() { var s = document.documentElement.scrollTop || 0; var max = (document.documentElement.scrollHeight - document.documentElement.clientHeight) || 1; document.getElementById("progress").style.width = (s / max * 100) + "%"; document.getElementById("backTop").style.display = s > 300 ? "flex" : "none"; });</script>\n'
        '</body>\n</html>'
    )


def publish_one(md_path):
    name = os.path.basename(md_path)
    base = name.replace(".md", ".html")
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
    m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    title = m.group(1).strip() if m else name.replace(".md", "")
    dm = re.search(r"(\d{4}-\d{2}-\d{2})", base)
    date_str = dm.group(1) if dm else datetime.now().strftime("%Y-%m-%d")
    article_id = base.replace(".html", "")
    html = make_html(content, title, date_str, article_id)
    out = os.path.join(ART, base)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print("created: " + base)


def main():
    issue_body = sys.argv[1] if len(sys.argv) > 1 else ""

    print("publishing all published articles...")

    if not os.path.exists(PUB):
        print("no published dir")
        return

    files = sorted([f for f in os.listdir(PUB) if f.endswith(".md")])
    print("found " + str(len(files)) + " articles")

    for f in files:
        publish_one(os.path.join(PUB, f))

    print("\ngit operations...")
    subprocess.run(["git", "-C", REPO, "add", "."], check=True)
    subprocess.run(["git", "-C", REPO, "commit", "-m", "Auto-deploy from issue"], check=True)
    r = subprocess.run(["git", "-C", REPO, "push", "origin", "master"], capture_output=True, text=True)
    if r.returncode == 0:
        print("pushed")
    else:
        print("push error: " + r.stderr)


if __name__ == "__main__":
    import sys
    main()
