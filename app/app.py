# app/app.py

from flask import Flask, request, render_template, render_template_string
import xmltodict

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/profile/update", methods=["POST"])
def update_profile():
    xml_payload = request.form.get("profileXML")
    parsed_data = xmltodict.parse(xml_payload)
    name_value = parsed_data["profile"]["name"]
    
    # 취약점: HTML Escape 없이 그대로 출력
    html_response = f"Hello {name_value}!"
    return render_template_string(html_response)
