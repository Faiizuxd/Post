from flask import Flask, request, render_template_string
import requests
import re
import time
import os

app = Flask(__name__)

HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>Z0H Z0H WALL TOOL</title>
    <style>
        body {
            background-color: #000;
            color: #0f0;
            font-family: monospace;
            padding: 30px;
        }
        input, textarea {
            width: 100%;
            padding: 10px;
            margin-top: 10px;
            background-color: #111;
            border: 1px solid #444;
            color: #0f0;
        }
        button {
            background: #ff0040;
            color: white;
            padding: 10px 25px;
            margin-top: 15px;
            border: none;
            cursor: pointer;
        }
        .log {
            margin-top: 20px;
            background: #111;
            padding: 15px;
            border: 1px solid #555;
        }
    </style>
</head>
<body>
    <h2>★ Z0H Z0H WALL TOOL ★</h2>
    <form method="POST">
        <label>FB Post URL:</label>
        <input type="text" name="post_url" required>

        <label>Hater Name:</label>
        <input type="text" name="name" required>

        <label>Delay Between Comments (seconds):</label>
        <input type="number" name="delay" value="2" required>

        <label>Facebook Cookie:</label>
        <textarea name="cookie" rows="3" required></textarea>

        <label>Comments (one per line):</label>
        <textarea name="comments" rows="6" required></textarea>

        <button type="submit">🔥 Start Commenting</button>
    </form>
    {% if result %}
    <div class="log">
        <h3>Console Log:</h3>
        <pre>{{ result }}</pre>
    </div>
    {% endif %}
</body>
</html>
"""

def extract_target_id(url):
    """Extracts Facebook post ID or pfbid"""
    if url.startswith("pfbid"):
        return url.split('/')[0]
    match = re.search(r'pfbid\w+|\d+', url)
    return match.group(0) if match else None

def get_eaag_token(cookie):
    """Gets EAAG token from business.facebook.com"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Mobile) AppleWebKit/537.36 Chrome/103.0 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/375.1.0.28.111;]'
    }
    try:
        res = requests.get('https://business.facebook.com/business_locations', headers=headers, cookies={'Cookie': cookie})
        token_match = re.search(r'(EAAG\w+)', res.text)
        return token_match.group(1) if token_match else None
    except:
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    result_log = ""
    if request.method == "POST":
        post_url = request.form.get("post_url", "").strip()
        hater_name = request.form.get("name", "").strip()
        delay = int(request.form.get("delay", "2"))
        cookie = request.form.get("cookie", "").strip()
        comment_text = request.form.get("comments", "").strip()

        if not all([post_url, hater_name, cookie, comment_text]):
            return render_template_string(HTML_FORM, result="[!] Please fill in all fields.")

        token = get_eaag_token(cookie)
        if not token:
            return render_template_string(HTML_FORM, result="[!] EAAG token not found. Invalid or expired cookie.")

        target_id = extract_target_id(post_url)
        if not target_id:
            return render_template_string(HTML_FORM, result="[!] Invalid Facebook post URL.")

        comments = comment_text.splitlines()
        for idx, line in enumerate(comments):
            comment = f"{hater_name}: {line.strip()}"
            data = {
                'message': comment,
                'access_token': token
            }
            try:
                r = requests.post(f"https://graph.facebook.com/{target_id}/comments/", data=data, cookies={'Cookie': cookie})
                res_json = r.json()
                if 'id' in res_json:
                    result_log += f"[{idx+1}] ✅ Sent: {comment}\n"
                else:
                    result_log += f"[{idx+1}] ❌ Failed: {res_json}\n"
                time.sleep(delay)
            except Exception as e:
                result_log += f"[{idx+1}] ❌ Error: {e}\n"
                time.sleep(3)

    return render_template_string(HTML_FORM, result=result_log)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Compatible with Render/Heroku
    app.run(debug=True, host="0.0.0.0", port=port)
