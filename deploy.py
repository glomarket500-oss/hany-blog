#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鄭哥博客全自動部署腳本（GitHub API 版）
用法：python deploy.py
"""

import os
import sys
import base64
import json
import urllib.request
import urllib.error

REPO = "glomarket500-oss/hany-blog"
TOKEN_FILE = os.path.join(os.path.dirname(__file__), ".github_token")
FILES = ["index.html", "about.html", "blog.html", "contact.html"]

def get_token():
    # 1. 检查命令行参数
    if len(sys.argv) > 1:
        return sys.argv[1].strip()
    # 2. 检查环境变量
    env_tok = os.environ.get("GITHUB_TOKEN", "").strip()
    if env_tok:
        return env_tok
    # 3. 检查本地文件
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    print("=" * 50)
    print("需要 GitHub Personal Access Token")
    print("1. 打开 https://github.com/settings/tokens")
    print("2. Generate new token (classic)")
    print("3. 勾选 repo")
    print("4. 复制 token")
    print("=" * 50)
    print("用法: python deploy.py YOUR_TOKEN")
    print("  或: set GITHUB_TOKEN=your_token && python deploy.py")
    sys.exit(1)

def api_request(url, token, data=None, method=None):
    headers = {
        "Authorization": f"token {token}",
        "User-Agent": "hany-blog-deploy",
        "Accept": "application/vnd.github+json"
    }
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, headers=headers, method=method)
    if data is not None:
        req.data = data.encode("utf-8")
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return True, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            err = json.loads(body)
            return False, err.get("message", body)
        except:
            return False, body
    except Exception as e:
        return False, str(e)

def get_file_sha(token, path):
    url = f"https://api.github.com/repos/{REPO}/contents/{path}"
    ok, data = api_request(url, token)
    if not ok:
        return None, data
    return data.get("sha"), None

def update_file(token, path, content, message):
    sha, err = get_file_sha(token, path)
    if sha is None:
        print(f"   ⚠️ 获取 {path} SHA 失败: {err}")
        return False
    url = f"https://api.github.com/repos/{REPO}/contents/{path}"
    payload = json.dumps({
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
        "sha": sha
    })
    ok, data = api_request(url, token, payload, "PUT")
    if not ok:
        print(f"   ❌ 上传 {path} 失败: {data}")
        return False
    return True

def main():
    print("🚀 鄭哥博客全自動部署（GitHub API）")
    print(f"   倉庫: {REPO}\n")

    token = get_token()
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    success = 0

    for filename in FILES:
        filepath = os.path.join(repo_dir, filename)
        if not os.path.exists(filepath):
            print(f"⚠️ 跳过 {filename}（文件不存在）")
            continue
        print(f"📤 上传 {filename}...")
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        if update_file(token, filename, content, f"Auto deploy: {filename}"):
            print(f"   ✅ {filename} 上传成功")
            success += 1
        else:
            print(f"   ❌ {filename} 上传失败")

    print(f"\n{'='*50}")
    if success == len(FILES):
        print(f"🎉 全部 {success} 個文件上傳成功！")
        print("   Vercel 會自動部署（約 10-30 秒）")
        print("   https://hany-blog.vercel.app")
    else:
        print(f"⚠️ {success}/{len(FILES)} 個文件上傳成功")
    print("="*50)

if __name__ == "__main__":
    main()
