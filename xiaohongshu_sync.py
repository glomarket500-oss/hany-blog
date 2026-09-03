#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小紅書同步生成腳本
用法：python xiaohongshu_sync.py [文章標題]

將網站文章自動生成小紅書風格文案 + 3:4 長圖 HTML
輸出到 vault/小紅書同步/ 文件夾
"""

import os
import sys
import re
from datetime import datetime

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "小紅書同步")

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def extract_article_content(html_path):
    """從 blog.html 提取文章內容"""
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 提取所有文章標題同摘要
    articles = []
    # 匹配 post-card 內容
    import re
    posts = re.findall(r'<article class="post-card".*?\u003c/article>', content, re.DOTALL)
    for post in posts:
        title_match = re.search(r'<span class="cn">(.*?)</span>', post)
        excerpt_match = re.search(r'<p class="excerpt">.*?\u003cspan class="cn">(.*?)</span>', post, re.DOTALL)
        date_match = re.search(r'class="post-date">(.*?)</span>', post)
        tag_match = re.search(r'class="post-tag">.*?\u003cspan class="cn">(.*?)</span>', post)
        
        if title_match:
            articles.append({
                "title": title_match.group(1),
                "excerpt": excerpt_match.group(1) if excerpt_match else "",
                "date": date_match.group(1) if date_match else "",
                "tag": tag_match.group(1) if tag_match else ""
            })
    return articles

def generate_xhs_text(article):
    """生成小紅書文案"""
    title = article["title"]
    excerpt = article["excerpt"]
    tag = article["tag"]
    date = article["date"]
    
    # 小紅書文案模板
    text = f"""📖 {title}

{excerpt[:120]}...

🔍 呢個問題我經常被問到，今日同大家分享下我嘅經驗：

1️⃣ 做貿易最緊要係留住客，唔係搵客
2️⃣ 技術要變成錢先有用
3️⃣ 00後年輕人有膽識，值得投資

💡 如果你有類似經歷或者問題，歡迎喺下面留言傾下。

━━━━━━━━━━━━━━
📝 鄭哥Hany真實經歷
☀️ 七善門科技 · 星辰算力
📍 香港旺角花園街183號 · ALEXBI INC Long Beach CA
📱 WhatsApp +852 6641 7912
🔗 https://hany-blog.vercel.app
━━━━━━━━━━━━━━

#{tag} #國際貿易 #AI算力 #英偉達服務器 #跨境電商 #產品創新 #創業投資 #香港 #00後創業 #鄭哥Hany
"""
    return text

def generate_xhs_image_html(article):
    """生成小紅書 3:4 長圖 HTML"""
    title = article["title"]
    excerpt = article["excerpt"]
    date = article["date"]
    tag = article["tag"]
    
    # 3:4 比例 = 寬度 900px，高度 1200px
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  body {{ margin:0; padding:0; background:#f5f5f5; display:flex; justify-content:center; align-items:center; min-height:100vh; }}
  .card {{ 
    width: 900px; height: 1200px; background: linear-gradient(135deg, #fff5f5 0%, #ffffff 50%, #f8f8ff 100%);
    border-radius: 24px; padding: 60px; box-shadow: 0 20px 60px rgba(0,0,0,0.1);
    font-family: -apple-system, 'PingFang SC', 'Noto Sans SC', sans-serif;
    position: relative; overflow: hidden; box-sizing: border-box;
  }}
  .card::before {{ 
    content:''; position:absolute; top:0; left:60px; width: 120px; height: 8px; 
    background: linear-gradient(90deg, #c41e3a, #ff6b6b); border-radius: 0 0 8px 8px;
  }}
  .tag {{ 
    display:inline-block; background: linear-gradient(135deg, #c41e3a, #ff6b6b); 
    color: white; padding: 8px 20px; border-radius: 20px; font-size: 24px; font-weight: 600; margin-bottom: 30px;
  }}
  h1 {{ font-size: 52px; font-weight: 700; color: #1a1a1a; line-height: 1.3; margin-bottom: 30px; letter-spacing: -1px; }}
  .excerpt {{ font-size: 32px; color: #555; line-height: 1.8; margin-bottom: 40px; }}
  .divider {{ height: 3px; background: linear-gradient(90deg, #c41e3a, transparent); margin: 30px 0; border-radius: 2px; }}
  .tips {{ background: rgba(196,30,58,0.06); border-radius: 16px; padding: 30px; margin: 30px 0; }}
  .tips h3 {{ font-size: 28px; color: #c41e3a; margin-bottom: 15px; }}
  .tips p {{ font-size: 26px; color: #555; line-height: 1.8; margin: 8px 0; }}
  .footer {{ position: absolute; bottom: 60px; left: 60px; right: 60px; }}
  .footer-line {{ height: 2px; background: #e8e8e8; margin-bottom: 20px; }}
  .footer-text {{ font-size: 22px; color: #888; line-height: 1.8; }}
  .footer-brand {{ font-size: 26px; font-weight: 700; color: #1a1a1a; margin-top: 15px; }}
  .emoji {{ font-size: 1.2em; }}
</style>
</head>
<body>
  <div class="card">
    <div class="tag">{tag}</div>
    <h1>{title}</h1>
    <div class="excerpt">{excerpt[:200]}..."</div>
    <div class="divider"></div>
    <div class="tips">
      <h3><span class="emoji">💡</span> 鄭哥話你知</h3>
      <p><span class="emoji">1️⃣</span> 做貿易最緊要留住客</p>
      <p><span class="emoji">2️⃣</span> 技術要變成錢先有用</p>
      <p><span class="emoji">3️⃣</span> 00後年輕人有膽識</p>
    </div>
    <div class="footer">
      <div class="footer-line"></div>
      <div class="footer-text">
        📝 鄭哥Hany真實經歷 | ☀️ 七善門科技 · 星辰算力<br>
        📍 香港旺角花園街183號 · ALEXBI INC Long Beach CA<br>
        📱 WhatsApp +852 6641 7912<br>
        🔗 https://hany-blog.vercel.app
      </div>
      <div class="footer-brand">鄭哥 / Hany</div>
    </div>
  </div>
</body>
</html>
"""
    return html

def main():
    print("🎯 小紅書同步內容生成器")
    print("=" * 50)
    
    # 確保輸出目錄存在
    ensure_dir(OUTPUT_DIR)
    print(f"📁 輸出目錄: {OUTPUT_DIR}\n")
    
    # 讀取文章
    blog_html = os.path.join(os.path.dirname(__file__), "blog.html")
    if not os.path.exists(blog_html):
        print(f"❌ 找不到 {blog_html}")
        sys.exit(1)
    
    articles = extract_article_content(blog_html)
    print(f"📄 從 blog.html 提取到 {len(articles)} 篇文章\n")
    
    # 為每篇文章生成小紅書內容
    for i, article in enumerate(articles, 1):
        safe_title = re.sub(r'[^\w]', '_', article["title"])[:30]
        
        # 生成文案
        text_path = os.path.join(OUTPUT_DIR, f"xhs_{safe_title}_文案.txt")
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(generate_xhs_text(article))
        print(f"  ✅ 文案: xhs_{safe_title}_文案.txt")
        
        # 生成長圖 HTML
        html_path = os.path.join(OUTPUT_DIR, f"xhs_{safe_title}_長圖.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(generate_xhs_image_html(article))
        print(f"  ✅ 長圖: xhs_{safe_title}_長圖.html")
        print()
    
    print("=" * 50)
    print("🎉 小紅書同步內容生成完成！")
    print(f"📁 文件位置: {OUTPUT_DIR}")
    print()
    print("💡 使用說明:")
    print("   1. 打開長圖 HTML 文件")
    print("   2. 截圖保存為 PNG (建議 900x1200)")
    print("   3. 複製文案 txt 內容")
    print("   4. 到小紅書發布筆記")
    print("=" * 50)

if __name__ == "__main__":
    main()
