from pathlib import Path
import re
import xml.etree.ElementTree as ET
root=Path('prepared/00_framework_modern')
p=root/'core/src/main/java/com/bizzan/bitrade/util/Decimal128ToBigDecimalConverter.java'
if p.exists():
    s=p.read_text(encoding='utf-8',errors='ignore').replace('import com.mongodb.Mongo;\n','')
    p.write_text(s,encoding='utf-8')
mc=root/'admin/src/main/java/com/bizzan/bitrade/config/MongoConfig.java'
if mc.exists():
    s=mc.read_text(encoding='utf-8',errors='ignore')
    if 'import com.mongodb.Mongo;' not in s:
        s=s.replace('import com.mongodb.MongoClient;','import com.mongodb.Mongo;\nimport com.mongodb.MongoClient;')
    mc.write_text(s,encoding='utf-8')
ns='http://maven.apache.org/POM/4.0.0'; N={'m':ns}; ET.register_namespace('',ns)
ap=root/'admin/pom.xml'; t=ET.parse(ap); r=t.getroot(); deps=r.find('m:dependencies',N)
for d in list(deps.findall('m:dependency',N)):
    if d.findtext('m:groupId',default='',namespaces=N)=='org.mongodb' and d.findtext('m:artifactId',default='',namespaces=N)=='mongodb-driver-legacy': deps.remove(d)
present={(d.findtext('m:groupId',default='',namespaces=N),d.findtext('m:artifactId',default='',namespaces=N)) for d in deps.findall('m:dependency',N)}
if ('org.mongodb','mongo-java-driver') not in present:
    d=ET.SubElement(deps,f'{{{ns}}}dependency'); ET.SubElement(d,f'{{{ns}}}groupId').text='org.mongodb'; ET.SubElement(d,f'{{{ns}}}artifactId').text='mongo-java-driver'; ET.SubElement(d,f'{{{ns}}}version').text='3.12.14'
t.write(ap,encoding='utf-8',xml_declaration=True)
# Spring 6+ removed AbstractWebSocketMessageBrokerConfigurer; migrate retained configs without changing behavior.
for module in ('chat','market'):
    ws=root/module/'src/main/java/com/bizzan/bitrade/config/WebSocketConfig.java'
    if ws.exists():
        s=ws.read_text(encoding='utf-8',errors='ignore')
        s=s.replace('import org.springframework.web.socket.config.annotation.AbstractWebSocketMessageBrokerConfigurer;', 'import org.springframework.web.socket.config.annotation.WebSocketMessageBrokerConfigurer;')
        s=s.replace('extends AbstractWebSocketMessageBrokerConfigurer', 'implements WebSocketMessageBrokerConfigurer')
        ws.write_text(s,encoding='utf-8')
# Spring Kafka renamed the listener group attribute to groupId.
consumer=root/'market/src/main/java/com/bizzan/bitrade/consumer/DataDictionarySaveUpdateConsumer.java'
if consumer.exists():
    s=consumer.read_text(encoding='utf-8',errors='ignore')
    s=s.replace('group = ', 'groupId = ')
    consumer.write_text(s,encoding='utf-8')
# New Spring Messaging overloads make convertAndSend(destination, null) ambiguous.
push=root/'market/src/main/java/com/bizzan/bitrade/job/ExchangePushJob.java'
if push.exists():
    s=push.read_text(encoding='utf-8',errors='ignore')
    s=re.sub(r'(\.convertAndSend\([^,\n]+,)\s*null(\s*\))', r'\1 (Object) null\2', s)
    push.write_text(s,encoding='utf-8')
