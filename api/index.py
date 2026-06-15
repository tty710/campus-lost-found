# -*- coding: utf-8 -*-
import sys, os, traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/db-test")
def db_test():
    try:
        import psycopg2
        import os
        db_url = os.environ.get(
            "DATABASE_URL",
            "postgresql://postgres.edagdtolpmspurnohxkw:140d2f33b3e22f522128643dd977ba4d@aws-0-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"
        )
        conn = psycopg2.connect(db_url + "&connect_timeout=5" if "?" in db_url else "?connect_timeout=5")
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.close()
        conn.close()
        return jsonify({"db": "connected"})
    except Exception as e:
        return jsonify({"db": "error", "detail": str(e)[:500]}), 200

@app.route("/")
@app.route("/<path:path>")
def catch_all(path=""):
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>校园失物招领平台</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
.card { background: white; border-radius: 16px; padding: 48px; max-width: 480px; width: 90%; box-shadow: 0 20px 60px rgba(0,0,0,0.3); text-align: center; }
h1 { font-size: 28px; color: #333; margin-bottom: 12px; }
p { color: #666; margin-bottom: 24px; line-height: 1.6; }
.status { display: inline-block; padding: 6px 16px; border-radius: 20px; font-size: 14px; margin: 8px; }
.online { background: #e6f9ed; color: #1a7f42; }
.offline { background: #fde8e8; color: #c81e1e; }
</style>
</head>
<body>
<div class="card">
<h1>校园失物招领平台</h1>
<p>发布失物信息、搜索物品、申请认领</p>
<div>
<span class="status online" id="health-status">检查中...</span>
<span class="status online" id="db-status">数据库检查中...</span>
</div>
<script>
fetch("/health").then(r=>r.json()).then(d=>{
    document.getElementById("health-status").textContent = "服务: 运行中";
    document.getElementById("health-status").className = "status online";
}).catch(()=>{
    document.getElementById("health-status").textContent = "服务: 异常";
    document.getElementById("health-status").className = "status offline";
});
fetch("/db-test").then(r=>r.json()).then(d=>{
    if(d.db==="connected") {
        document.getElementById("db-status").textContent = "数据库: 已连接";
        document.getElementById("db-status").className = "status online";
    } else {
        document.getElementById("db-status").textContent = "数据库: " + d.detail;
        document.getElementById("db-status").className = "status offline";
    }
}).catch(()=>{
    document.getElementById("db-status").textContent = "数据库: 连接失败";
    document.getElementById("db-status").className = "status offline";
});
</script>
</div>
</body>
</html>"""
