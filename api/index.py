# -*- coding: utf-8 -*-
import sys, os, traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_app():
    try:
        from app import create_app
        return create_app()
    except Exception as e:
        from flask import Flask
        app = Flask(__name__)
        @app.route("/", defaults={"path": ""})
        @app.route("/<path:path>")
        def show_error(path):
            return """<html><body style="font-family:monospace;padding:30px;background:#fff3cd">
<h2>Startup Error</h2>
<p><strong>""" + str(e) + """</strong></p>
<pre style="background:#222;color:#0f0;padding:15px;border-radius:8px;overflow-x:auto;font-size:12px">""" + traceback.format_exc() + """</pre>
</body></html>""", 500
        return app

app = get_app()