import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import traceback

try:
    from app import create_app
    app = create_app()
except Exception as e:
    from flask import Flask
    app = Flask(__name__)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def show_error(path):
        return f"""<html><body style="font-family:monospace;padding:40px;background:#fff3cd">
<h2>Deployment Error</h2>
<p><strong>Error:</strong> {str(e)}</p>
<pre style="background:#f5f5f5;padding:15px;border-radius:8px;overflow-x:auto">{traceback.format_exc()}</pre>
<p>Check your <code>DATABASE_URL</code> environment variable in Vercel Settings → Environment Variables.</p>
</body></html>""", 500

    @app.route("/health")
    def health():
        return "ERROR: " + str(e), 500
