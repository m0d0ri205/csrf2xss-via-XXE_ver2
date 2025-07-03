#!/usr/bin/python3
from flask import Flask, request, render_template, render_template_string
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import xmltodict
import urllib
import os

app = Flask(__name__)
app.secret_key = os.urandom(32)

try:
    FLAG = open("./flag.txt", "r").read()
except:
    FLAG = "[**FLAG**]"


def read_url(url, cookie={"name": "name", "value": "value"}):
    cookie.update({"domain": "127.0.0.1"})
    try:
        service = Service(executable_path="/usr/bin/chromedriver")
        options = webdriver.ChromeOptions()
        for _ in [
            "headless",
            "window-size=1920x1080",
            "disable-gpu",
            "no-sandbox",
            "disable-dev-shm-usage",
        ]:
            options.add_argument(_)
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(3)
        driver.set_page_load_timeout(3)
        driver.get("http://127.0.0.1:8000/")
        driver.add_cookie(cookie)
        driver.get(url)
    except Exception as e:
        driver.quit()
        print(str(e))
        return False
    driver.quit()
    return True


def check_csrf(param, cookie={"name": "name", "value": "value"}):
    url = f"http://127.0.0.1:8000/vuln?param={urllib.parse.quote(param)}"
    return read_url(url, cookie)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/vuln")
def vuln():
    param = request.args.get("param", "").lower()
    xss_filter = ["frame", "script", "on"]
    for _ in xss_filter:
        param = param.replace(_, "*")
    return param


@app.route("/flag", methods=["GET", "POST"])
def flag():
    if request.method == "GET":
        return render_template("flag.html")
    elif request.method == "POST":
        param = request.form.get("param", "")
        if not check_csrf(param):
            return '<script>alert("wrong??");history.go(-1);</script>'

        return '<script>alert("good");history.go(-1);</script>'


memo_text = ""


@app.route("/memo")
def memo():
    global memo_text
    text = request.args.get("memo", None)
    if text:
        memo_text += text
    return render_template("memo.html", memo=memo_text)


@app.route("/admin/notice_flag")
def admin_notice_flag():
    global memo_text
    if request.remote_addr != "127.0.0.1":
        return "Access Denied"
    if request.args.get("userid", "") != "admin":
        return "Access Denied 2"
    memo_text += f"[Notice] flag is {FLAG}\n"
    return "Ok"


@app.route("/upload_xml", methods=["GET", "POST"])
def upload_xml():
    if request.method == "GET":
        return '''
            <h2>Upload XML</h2>
            <form action="/upload_xml" method="post">
                <textarea name="xml_data" rows="15" cols="80"></textarea><br>
                <input type="submit" value="Upload">
            </form>
        '''
    elif request.method == "POST":
        xml_payload = request.form.get("xml_data", "")
        try:
            parsed_data = xmltodict.parse(xml_payload)
            text_content = parsed_data["svg"]["text"]
        except Exception as e:
            return f"<h3>Parsing Error:</h3> {str(e)}"

        # HTML Escape 없이 출력 → XSS 가능
        return render_template_string(f"""
            <h2>Upload Result</h2>
            <div>{text_content}</div>
        """)


app.run(host="0.0.0.0", port=8000)
