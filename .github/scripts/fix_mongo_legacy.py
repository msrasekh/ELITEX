from pathlib import Path
import re
import xml.etree.ElementTree as ET
root=Path('prepared/00_framework_modern')
p=root/'core/src/main/java/com/bizzan/bitrade/util/Decimal128ToBigDecimalConverter.java'
if p.exists():
    s=p.read_text(encoding='utf-8',errors='ignore').replace('import com.mongodb.Mongo;\n',''); p.write_text(s,encoding='utf-8')
mc=root/'admin/src/main/java/com/bizzan/bitrade/config/MongoConfig.java'
if mc.exists():
    s=mc.read_text(encoding='utf-8',errors='ignore')
    if 'import com.mongodb.Mongo;' not in s: s=s.replace('import com.mongodb.MongoClient;','import com.mongodb.Mongo;\nimport com.mongodb.MongoClient;')
    mc.write_text(s,encoding='utf-8')
ns='http://maven.apache.org/POM/4.0.0'; N={'m':ns}; ET.register_namespace('',ns)
ap=root/'admin/pom.xml'; t=ET.parse(ap); r=t.getroot(); deps=r.find('m:dependencies',N)
for d in list(deps.findall('m:dependency',N)):
    if d.findtext('m:groupId',default='',namespaces=N)=='org.mongodb' and d.findtext('m:artifactId',default='',namespaces=N)=='mongodb-driver-legacy': deps.remove(d)
present={(d.findtext('m:groupId',default='',namespaces=N),d.findtext('m:artifactId',default='',namespaces=N)) for d in deps.findall('m:dependency',N)}
if ('org.mongodb','mongo-java-driver') not in present:
    d=ET.SubElement(deps,f'{{{ns}}}dependency'); ET.SubElement(d,f'{{{ns}}}groupId').text='org.mongodb'; ET.SubElement(d,f'{{{ns}}}artifactId').text='mongo-java-driver'; ET.SubElement(d,f'{{{ns}}}version').text='3.12.14'
t.write(ap,encoding='utf-8',xml_declaration=True)
for module in ('chat','market'):
    ws=root/module/'src/main/java/com/bizzan/bitrade/config/WebSocketConfig.java'
    if ws.exists():
        s=ws.read_text(encoding='utf-8',errors='ignore').replace('import org.springframework.web.socket.config.annotation.AbstractWebSocketMessageBrokerConfigurer;', 'import org.springframework.web.socket.config.annotation.WebSocketMessageBrokerConfigurer;').replace('extends AbstractWebSocketMessageBrokerConfigurer', 'implements WebSocketMessageBrokerConfigurer'); ws.write_text(s,encoding='utf-8')
consumer=root/'market/src/main/java/com/bizzan/bitrade/consumer/DataDictionarySaveUpdateConsumer.java'
if consumer.exists():
    s=consumer.read_text(encoding='utf-8',errors='ignore').replace('group = ', 'groupId = '); consumer.write_text(s,encoding='utf-8')
push=root/'market/src/main/java/com/bizzan/bitrade/job/ExchangePushJob.java'
if push.exists():
    lines=[]
    for line in push.read_text(encoding='utf-8',errors='ignore').splitlines(True):
        if '.convertAndSend(' in line and '(Object)' not in line:
            pos=line.find('.convertAndSend('); comma=line.find(',', pos)
            if comma >= 0: line=line[:comma+1]+' (Object) '+line[comma+1:].lstrip()
        lines.append(line)
    push.write_text(''.join(lines),encoding='utf-8')
for cfg in root.rglob('ApplicationConfig.java'):
    s=cfg.read_text(encoding='utf-8',errors='ignore'); s=re.sub(r'\s*super\.addResourceHandlers\([^;]+\);', '', s); s=re.sub(r'\s*super\.addFormatters\([^;]+\);', '', s); s=re.sub(r'\s*super\.addInterceptors\([^;]+\);', '', s); cfg.write_text(s,encoding='utf-8')
for cfg in root.rglob('RedisCacheConfig.java'):
    s=cfg.read_text(encoding='utf-8',errors='ignore'); s=re.sub(r'RedisCacheManager\s+cacheManager\s*=\s*new\s+RedisCacheManager\(redisTemplate\)\s*;', 'RedisCacheManager cacheManager = RedisCacheManager.create(redisTemplate.getConnectionFactory());', s); s=re.sub(r'\s*cacheManager\.setDefaultExpiration\([^;]+\);', '', s); cfg.write_text(s,encoding='utf-8')
# Tomcat servlet4preview namespace disappeared years ago; use the Jakarta Servlet API used by Spring 6/Boot 4.
for java in root.rglob('*.java'):
    s=java.read_text(encoding='utf-8',errors='ignore')
    n=s.replace('org.apache.catalina.servlet4preview.http.HttpServletRequest','jakarta.servlet.http.HttpServletRequest').replace('org.apache.catalina.servlet4preview.http.HttpServletResponse','jakarta.servlet.http.HttpServletResponse')
    if n!=s: java.write_text(n,encoding='utf-8')
