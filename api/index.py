# -*- coding: utf-8 -*-
import traceback, sys, os

try:
    from app import create_app
    app = create_app()
except Exception as e:
    from flask import Flask
    app = Flask(__name__)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def show_error(path):
        env_vars = {k: v[:20] + "..." if len(v) > 20 else v
                    for k, v in sorted(os.environ.items())
                    if any(x in k.upper() for x in ["DATABASE", "SECRET", "SUPABASE", "VERCEL"])}
        return """<html><body style="font-family:monospace;padding:30px;background:#fff3cd">
<h2>Deployment Error</h2>
<p><strong>""" + str(e) + """</strong></p>
<pre style="background:#222;color:#0f0;padding:15px;border-radius:8px;overflow-x:auto;font-size:12px">""" + traceback.format_exc() + """</pre>
<h3>Environment (filtered):</h3>
<pre>""" + str(env_vars) + """</pre>
</body></html>""", 500