from pathlib import Path
import re
import xml.etree.ElementTree as ET
root=Path('prepared/00_framework_modern')
ns='http://maven.apache.org/POM/4.0.0'; N={'m':ns}; ET.register_namespace('',ns)
for pom in root.rglob('pom.xml'):
    tree=ET.parse(pom); pr=tree.getroot(); changed=False
    for d in pr.findall('.//m:dependencies/m:dependency',N):
        if d.findtext('m:groupId',default='',namespaces=N)=='com.alibaba' and d.findtext('m:artifactId',default='',namespaces=N) in ('druid','druid-spring-boot-starter','druid-spring-boot-3-starter'):
            d.find('m:artifactId',N).text='druid-spring-boot-4-starter'; v=d.find('m:version',N)
            if v is None: v=ET.SubElement(d,f'{{{ns}}}version')
            v.text='1.2.28'; changed=True
    if changed: tree.write(pom,encoding='utf-8',xml_declaration=True)
for cfg in root.rglob('DruidConfig.java'):
    s=cfg.read_text(encoding='utf-8',errors='ignore')
    if 'com.alibaba.druid.support.http.StatViewServlet' in s or 'com.alibaba.druid.support.http.WebStatFilter' in s: cfg.rename(cfg.with_suffix('.java.boot2-legacy'))
p=root/'core/src/main/java/com/bizzan/bitrade/util/Decimal128ToBigDecimalConverter.java'
if p.exists(): p.write_text(p.read_text(encoding='utf-8',errors='ignore').replace('import com.mongodb.Mongo;\n',''),encoding='utf-8')
mc=root/'admin/src/main/java/com/bizzan/bitrade/config/MongoConfig.java'
if mc.exists():
    s=mc.read_text(encoding='utf-8',errors='ignore')
    if 'import com.mongodb.Mongo;' not in s: s=s.replace('import com.mongodb.MongoClient;','import com.mongodb.Mongo;\nimport com.mongodb.MongoClient;')
    mc.write_text(s,encoding='utf-8')
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
if consumer.exists(): consumer.write_text(consumer.read_text(encoding='utf-8',errors='ignore').replace('group = ', 'groupId = '),encoding='utf-8')
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
for java in root.rglob('*.java'):
    s=java.read_text(encoding='utf-8',errors='ignore')
    n=s.replace('org.apache.catalina.servlet4preview.http.HttpServletRequest','jakarta.servlet.http.HttpServletRequest').replace('org.apache.catalina.servlet4preview.http.HttpServletResponse','jakarta.servlet.http.HttpServletResponse').replace('org.hibernate.validator.constraints.Email','jakarta.validation.constraints.Email').replace('org.springframework.boot.autoconfigure.data.mongo.MongoDataAutoConfiguration','org.springframework.boot.data.mongodb.autoconfigure.DataMongoAutoConfiguration').replace('MongoDataAutoConfiguration.class','DataMongoAutoConfiguration.class').replace('org.springframework.boot.autoconfigure.mongo.MongoAutoConfiguration','org.springframework.boot.mongodb.autoconfigure.MongoAutoConfiguration')
    n=re.sub(r'^import com\.netflix\.discovery\.converters\.[^;]+;\s*$', '', n, flags=re.M)
    n=n.replace('ServletFileUpload.isMultipartContent(request)', '(request.getContentType() != null && request.getContentType().toLowerCase().startsWith("multipart/"))')
    if java.name=='LoginController.java' and 'AuthenticationException' in n and 'import org.apache.shiro.authc.AuthenticationException;' not in n:
        n=n.replace('package com.bizzan.bitrade.controller;','package com.bizzan.bitrade.controller;\n\nimport org.apache.shiro.authc.AuthenticationException;')
    if n!=s: java.write_text(n,encoding='utf-8')
