from flask import Flask, request, render_template_string
import requests
import re
import time

app = Flask(__name__)

HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>Z0H Z0H WALL TOOL</title>
    <style>
        body {
            background-color: #000000;
            color: #00ff00;
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
    if url.startswith("pfbid"):
        return url.split('/')[0]
    match = re.search(r'pfbid\w+|\d+', url)
    return match.group(0) if match else None

def get_profile_info(token_eaag):
    try:
        response = requests.get(f"https://graph.facebook.com/me?fields=id,name&access_token={token_eaag}")
        profile_info = response.json()
        return profile_info.get("name"), profile_info.get("id")
    except:
        return None, None

@app.route("/", methods=["GET", "POST"])
def index():
    result_log = ""
    if request.method == "POST":
        post_url = request.form["post_url"]
        hater_name = request.form["name"]
        delay = int(request.form["delay"])
        cookie = request.form["cookie"]
        comment_text = request.form["comments"]

        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Mobile) AppleWebKit/537.36 Chrome/103.0 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/375.1.0.28.111;]'
        }

        res = requests.get('https://business.facebook.com/business_locations', headers=headers, cookies={'Cookie': cookie})
        token_match = re.search(r'(EAAG\w+)', res.text)
        if not token_match:
            result_log += "[!] EAAG token not found in cookie response.\n"
            return render_template_string(HTML_FORM, result=result_log)

        token = token_match.group(1)
        target_id = extract_target_id(post_url)

        if not target_id:
            result_log += "[!] Invalid post URL or ID not found.\n"
            return render_template_string(HTML_FORM, result=result_log)

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
    app.run(debug=True, port=5000)
