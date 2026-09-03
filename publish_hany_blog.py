#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鄭哥(hany)個人博客 - 全自動網站發布腳本
用法：python publish_hany_blog.py
"""

import os
import subprocess
import sys
import time
from pathlib import Path

# === 配置 ===
REPO_DIR = r"C:\Users\a\Desktop\MianAI知识库\MianAI知识库\vault\hany博主\个人网站草稿\框架"
VERCEL_URL = "https://hany-blog.vercel.app"


def run_cmd(cmd, cwd=None):
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=60)
    return result.returncode == 0, result.stdout, result.stderr


def git_push():
    """Git commit 并推送到 GitHub"""
    os.chdir(REPO_DIR)
    
    # 检查是否有变更
    ok, out, _ = run_cmd(["git", "status", "--short"])
    if not ok:
        return False, "无法获取 git status"
    if not out.strip():
        return True, "没有变更需要推送"
    
    # git add
    run_cmd(["git", "add", "-A"])
    
    # git commit
    ok, _, err = run_cmd(["git", "commit", "-m", "Update site content"])
    if not ok and "nothing to commit" not in err.lower():
        return False, f"commit 失败: {err}"
    
    # git push
    ok, _, err = run_cmd(["git", "push", "origin", "main"])
    if not ok:
        if "rejected" in err.lower():
            run_cmd(["git", "pull", "origin", "main", "--no-rebase"])
            ok, _, err = run_cmd(["git", "push", "origin", "main"])
            if not ok:
                return False, f"push 失败: {err}"
        else:
            return False, f"push 失败: {err}"
    
    # 获取 commit hash
    ok, out, _ = run_cmd(["git", "rev-parse", "--short", "HEAD"])
    commit = out.strip() if ok else "unknown"
    return True, f"已推送 (commit: {commit})"


def check_vercel_deploy(max_wait=120):
    """等待 Vercel 部署完成"""
    import urllib.request
    
    print(f"⏳ 等待 Vercel 部署（最多 {max_wait} 秒）...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            req = urllib.request.Request(VERCEL_URL, method='HEAD')
            req.add_header('User-Agent', 'Mozilla/5.0')
            resp = urllib.request.urlopen(req, timeout=10)
            if resp.status == 200:
                elapsed = time.time() - start_time
                return True, f"部署完成（约 {int(elapsed)} 秒）"
        except:
            pass
        time.sleep(5)
        print(f"  ... 已等待 {int(time.time() - start_time)} 秒")
    
    return False, f"等待超时（{max_wait} 秒）"


def main():
    print("🚀 鄭哥個人博客自動發布")
    print(f"   倉庫: {REPO_DIR}")
    print(f"   網址: {VERCEL_URL}")
    print()
    
    # Step 1: Git push
    print("📤 推送到 GitHub...")
    ok, msg = git_push()
    if not ok:
        print(f"   ❌ {msg}")
        return 1
    print(f"   ✅ {msg}")
    
    if msg == "没有变更需要推送":
        print("\nℹ️ 本地无变更，无需发布")
        return 0
    
    # Step 2: 检测 Vercel 部署
    print("\n🌐 检测 Vercel 部署...")
    ok, msg = check_vercel_deploy()
    if ok:
        print(f"   ✅ {msg}")
        print(f"\n🎉 发布成功！")
        print(f"   网站: {VERCEL_URL}")
        return 0
    else:
        print(f"   ⚠️ {msg}")
        print(f"\n⚠️ 代码已推送，Vercel 部署可能有延迟")
        print(f"   稍等片刻后访问: {VERCEL_URL}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
