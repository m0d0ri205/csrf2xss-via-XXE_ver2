# XXE

---

## XXE(XML External Entity) :

XML을 Parsing하여 사용하는 서비스에 악의적인 XML 구문을 Parsing하도록 유도하여 공격자가 의도한 동작을 수행하도록 하는 공격

기본적으로 XML Parser가 위치한 곳에서 부터 영향력이 발생하기 때문에 가볍게는 SSRF 같이 내부망 접근부터, RCE까지 큰 영향력을 가질 수 있습니다

### **Offensive techniques**

심플하겐 XML Parse가 동작하는 구간을 찾아야합니다. 소스코드를 볼 수 있는 상황이라면 코드에서 검색하는 것이 가장 빠르고 효율적이며, 소스코드 없이 순수하게 동작만으로만 봐야한다면 .xml 파일을 인자값으로 받거나, 에러에서 XML Parsing 관련 에러를 뱉는 구간을 위주로 점검해야합니다.

아래와 같이 눈에 띄게 xml 형태를 처리할 것으로 보이는 구간이 XXE가 존재할 가능성이 높은 부분입니다.

```bash
GET /readRss?url=https://rss_service/feeds.xml
```

이 때 우리는 XXE 구문이 포함된 파일을 서비스의 XML Parser가 읽고 분석하도록 하여 XXE를 유도 할 수 있습니다. 만약 위 readRss 란 페이지가 XML을 읽어 사용자에게 보여주는 기능을 가졌다면, 아래와 공격 구문으로 XXE 여부를 체크할 수 있습니다.

```html
<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE foo [
  <!ELEMENT foo ANY >
  <!ENTITY xxe SYSTEM "https://your_oast_domain" >]>
<foo>&xxe;</foo>
```

위 구문이 Parsing되면 서비스는 XML 구문에 따라서 웹 요청을 발생시키기 위해 oast_domain으로 접근하게 됩니다. 우리는 이때 발생하는 HTTP Request와 DNS Qeury를 가지고 식별하면 됩니다. 이렇게 OAST, OOB 기반으로 식별하는 방법이 가장 여러 케이스에서 확인할 수 있는 좋은 방법입니다. (Blind XXE도 측정할 수 있죠)

다만 public oast 서비스는 2021년 log4j 사태 이후로 많은 서비스들에서 차단을 하고 있어서 직접 private한 oast 서비스를 구성하여 테스트하시는 것을 추천합니다.

만약 XML Parsing의 결과가 리턴된다면 단순하게 DTD 사용을 체크하는 것도 좋습니다.

```html
<!--?xml version="1.0" ?-->
<!DOCTYPE replace [<!ENTITY example "Doe"> ]>
 <userInfo>
  <firstName>John</firstName>
  <lastName>&example;</lastName>
 </userInfo>
```