from pathlib import Path
import re, xml.etree.ElementTree as ET
root=Path('prepared/00_framework_modern')
ns='http://maven.apache.org/POM/4.0.0'; N={'m':ns}; ET.register_namespace('',ns)
versions={('org.elasticsearch','elasticsearch'):'6.2.4',('org.springframework.session','spring-session'):'1.3.5.RELEASE',('mysql','mysql-connector-java'):'8.0.11',('ch.qos.logback','logback-core'):'1.2.13',('ch.qos.logback','logback-classic'):'1.2.13',('org.slf4j','slf4j-api'):'1.7.36',('io.reactivex','rxjava'):'1.3.8'}
for p in root.rglob('pom.xml'):
    t=ET.parse(p); r=t.getroot(); ch=False
    for d in r.findall('.//m:dependencies/m:dependency',N):
        g=d.find('m:groupId',N); a=d.find('m:artifactId',N); v=d.find('m:version',N); key=((g.text or '').strip() if g is not None else '',(a.text or '').strip() if a is not None else '')
        if key in versions and v is None: ET.SubElement(d,f'{{{ns}}}version').text=versions[key]; ch=True
        sp=d.find('m:systemPath',N)
        if sp is not None and sp.text and re.match(r'^[A-Za-z]:/',sp.text):
            cand=list(root.rglob(Path(sp.text).name)); sp.text=str(cand[0].resolve()); ch=True
    build=r.find('m:build',N)
    if build is not None:
        plugins=build.find('m:plugins',N)
        if plugins is not None:
            for pl in list(plugins.findall('m:plugin',N)):
                a=pl.find('m:artifactId',N)
                if a is not None and a.text=='apt-maven-plugin': plugins.remove(pl); ch=True
    if ch:t.write(p,encoding='utf-8',xml_declaration=True)
cp=root/'core/pom.xml'; t=ET.parse(cp); r=t.getroot(); build=r.find('m:build',N); plugins=build.find('m:plugins',N)
compiler=next(pl for pl in plugins.findall('m:plugin',N) if pl.find('m:artifactId',N) is not None and pl.find('m:artifactId',N).text=='maven-compiler-plugin')
conf=compiler.find('m:configuration',N); proc=conf.find('m:proc',N)
if proc is None: proc=ET.SubElement(conf,f'{{{ns}}}proc')
proc.text='full'
for old in list(conf.findall('m:annotationProcessorPaths',N))+list(conf.findall('m:annotationProcessors',N)): conf.remove(old)
app=ET.SubElement(conf,f'{{{ns}}}annotationProcessorPaths')
for g,a,v,c in [('org.projectlombok','lombok','1.18.40',None),('com.querydsl','querydsl-apt','5.1.0','jakarta'),('jakarta.persistence','jakarta.persistence-api','3.1.0',None),('jakarta.annotation','jakarta.annotation-api','2.1.1',None)]:
    path=ET.SubElement(app,f'{{{ns}}}path'); ET.SubElement(path,f'{{{ns}}}groupId').text=g; ET.SubElement(path,f'{{{ns}}}artifactId').text=a; ET.SubElement(path,f'{{{ns}}}version').text=v
    if c: ET.SubElement(path,f'{{{ns}}}classifier').text=c
deps=r.find('m:dependencies',N); existing=set()
for d in deps.findall('m:dependency',N):
    g=d.find('m:groupId',N); a=d.find('m:artifactId',N)
    if g is not None and a is not None:
        key=(g.text,a.text); existing.add(key)
        if key in [('com.querydsl','querydsl-apt'),('com.querydsl','querydsl-jpa')]:
            c=d.find('m:classifier',N)
            if c is None:c=ET.SubElement(d,f'{{{ns}}}classifier')
            c.text='jakarta'
for g,a,v in [('jakarta.persistence','jakarta.persistence-api','3.1.0'),('jakarta.validation','jakarta.validation-api','3.0.2'),('javax.servlet','javax.servlet-api','4.0.1'),('org.dom4j','dom4j','2.1.4'),('org.apache.httpcomponents','httpcore','4.3.3')]:
    if (g,a) not in existing:
        d=ET.SubElement(deps,f'{{{ns}}}dependency'); ET.SubElement(d,f'{{{ns}}}groupId').text=g; ET.SubElement(d,f'{{{ns}}}artifactId').text=a; ET.SubElement(d,f'{{{ns}}}version').text=v
for p in root.rglob('*.java'):
    s=p.read_text(encoding='utf-8',errors='ignore'); n=s.replace('javax.validation.constraints.NotBlank','jakarta.validation.constraints.NotBlank').replace('javax.validation.constraints.NotEmpty','jakarta.validation.constraints.NotEmpty').replace('org.hibernate.validator.constraints.NotBlank','jakarta.validation.constraints.NotBlank').replace('org.hibernate.validator.constraints.NotEmpty','jakarta.validation.constraints.NotEmpty').replace('import sun.misc.BASE64Encoder;','import java.util.Base64;').replace('import com.mongodb.Mongo;\n','').replace('import com.mongodb.Cursor;\n','').replace('import org.apache.shiro.util.Assert;','import org.springframework.util.Assert;').replace('org.apache.shiro.util.Assert.','org.springframework.util.Assert.').replace('import org.apache.shiro.util.ByteSource;','import org.apache.shiro.lang.util.ByteSource;')
    n=re.sub(r'new BASE64Encoder\(\)\.encode\(([^;]+)\)',r'Base64.getEncoder().encodeToString(\1)',n)
    if 'org.springframework.util.Base64Utils' in n:
        n=n.replace('import org.springframework.util.Base64Utils;','import java.util.Base64;').replace('Base64Utils.encodeToString(', 'Base64.getEncoder().encodeToString(').replace('Base64Utils.decodeFromString(', 'Base64.getDecoder().decode(')
    if n!=s:p.write_text(n,encoding='utf-8')
# Spring Data Redis 3 / Spring 6 compatibility for retained admin cache config.
p=root/'admin/src/main/java/com/bizzan/bitrade/config/RedisCacheConfig.java'
if p.exists():
    s=p.read_text(encoding='utf-8',errors='ignore')
    s=re.sub(r'RedisCacheManager\s+cacheManager\s*=\s*new\s+RedisCacheManager\(redisTemplate\)\s*;', 'RedisCacheManager cacheManager = RedisCacheManager.create(redisTemplate.getConnectionFactory());', s)
    s=re.sub(r'\s*cacheManager\.setDefaultExpiration\([^;]+\);', '', s)
    p.write_text(s,encoding='utf-8')
# Commons FileUpload 1.x accepts javax servlet requests; use content-type detection with Jakarta request.
p=root/'admin/src/main/java/com/bizzan/bitrade/controller/common/UploadController.java'
if p.exists():
    s=p.read_text(encoding='utf-8',errors='ignore')
    s=s.replace('ServletFileUpload.isMultipartContent(request)', '(request.getContentType() != null && request.getContentType().toLowerCase().startsWith("multipart/"))')
    p.write_text(s,encoding='utf-8')
# Spring Data MongoDB removed the legacy single-object overload exposed by this retained repository signature.
p=root/'admin/src/main/java/com/bizzan/bitrade/job/MemberStatisticsJob.java'
if p.exists():
    s=p.read_text(encoding='utf-8',errors='ignore')
    s=re.sub(r'(memberLogDao|memberLogRepository)\.save\(([^;]+)\);', r'\1.saveAll(java.util.Collections.singletonList(\2));', s)
    p.write_text(s,encoding='utf-8')
# WebMvcConfigurer default methods must not be invoked through super in the migrated configuration.
p=root/'admin/src/main/java/com/bizzan/bitrade/config/ApplicationConfig.java'
if p.exists():
    s=p.read_text(encoding='utf-8',errors='ignore')
    s=re.sub(r'\s*super\.addResourceHandlers\([^;]+\);', '', s)
    s=re.sub(r'\s*super\.addFormatters\([^;]+\);', '', s)
    s=re.sub(r'\s*super\.addInterceptors\([^;]+\);', '', s)
    p.write_text(s,encoding='utf-8')
# MongoDB 4.x legacy compatibility API for retained MongoConfig.
ap=root/'admin/pom.xml'; at=ET.parse(ap); ar=at.getroot(); adeps=ar.find('m:dependencies',N)
if adeps is not None:
    present={(d.findtext('m:groupId',default='',namespaces=N),d.findtext('m:artifactId',default='',namespaces=N)) for d in adeps.findall('m:dependency',N)}
    if ('org.mongodb','mongodb-driver-legacy') not in present:
        d=ET.SubElement(adeps,f'{{{ns}}}dependency'); ET.SubElement(d,f'{{{ns}}}groupId').text='org.mongodb'; ET.SubElement(d,f'{{{ns}}}artifactId').text='mongodb-driver-legacy'; ET.SubElement(d,f'{{{ns}}}version').text='4.11.5'
    at.write(ap,encoding='utf-8',xml_declaration=True)
for name in ['MemberInviteStasticDao.java','MemberInviteStasticRankDao.java']:
    p=next(root.rglob(name)); s=p.read_text(); s=s.replace(' findById(Long id)', ' findLegacyById(Long id)'); p.write_text(s)
p=next(root.rglob('MemberInviteStasticService.java')); s=p.read_text().replace('memberInviteStasticDao.findById(id)','memberInviteStasticDao.findLegacyById(id)').replace('memberInviteStasticRankDao.findById(id)','memberInviteStasticRankDao.findLegacyById(id)'); p.write_text(s)
p=next(root.rglob('TopBaseService.java')); s=p.read_text().replace('Sort.by(pagenation.getPageParam().getDirection(), pagenation.getPageParam().getOrders())','Sort.by(pagenation.getPageParam().getDirection(), pagenation.getPageParam().getOrders().toArray(new String[0]))'); p.write_text(s)
p=next(root.rglob('MongoBaseService.java')); s=p.read_text().replace('Sort.by(pageParam.getDirection(),pageParam.getOrders())','Sort.by(pageParam.getDirection(),pageParam.getOrders().toArray(new String[0]))'); p.write_text(s)
p=next(root.rglob('Criteria.java')); s=p.read_text().replace('new Sort.Order(f);','new Sort.Order(Sort.Direction.ASC, f);'); p.write_text(s)
p=next(root.rglob('SmartHttpSessionStrategy.java')); s=p.read_text().replace('jakarta.servlet.http.HttpServletRequest','javax.servlet.http.HttpServletRequest').replace('jakarta.servlet.http.HttpServletResponse','javax.servlet.http.HttpServletResponse'); p.write_text(s)
p=next(root.rglob('AliyunUtil.java')); s=p.read_text().replace('BASE64Encoder b64Encoder = new BASE64Encoder();\n            encodeStr = b64Encoder.encode(md5Bytes);','encodeStr = Base64.getEncoder().encodeToString(md5Bytes);').replace('(new BASE64Encoder()).encode(rawHmac)','Base64.getEncoder().encodeToString(rawHmac)'); p.write_text(s)
p=root/'admin/src/main/java/com/bizzan/bitrade/controller/finance/FinanceStatisticsController.java'
if p.exists():
    s=p.read_text(encoding='utf-8',errors='ignore'); lines=s.splitlines(True)
    if len(lines)>=115 and '\\\\' in lines[114]: lines[114]=lines[114].replace('\\\\"','\\"'); s=''.join(lines)
    p.write_text(s,encoding='utf-8')
p=root/'core/src/test/java/com/bizzan/bitrade/test/BaseTest.java'
if p.exists():
    s=p.read_text().replace('import org.springframework.test.context.transaction.TransactionConfiguration;','import org.springframework.transaction.annotation.Transactional;\nimport org.springframework.test.annotation.Rollback;').replace('@TransactionConfiguration(transactionManager = "transactionManager", defaultRollback = false)','@Transactional(transactionManager = "transactionManager")\n@Rollback(false)'); p.write_text(s)
p=root/'core/src/test/java/com/bizzan/bitrade/test/JUnit4ClassRunner.java'
if p.exists():
    s=p.read_text().replace('import org.springframework.util.Log4jConfigurer;\n',''); s=re.sub(r'\n    static \{.*?\n    \}\n','\n',s,flags=re.S); p.write_text(s)
t.write(cp,encoding='utf-8',xml_declaration=True)
