from pathlib import Path
import re, xml.etree.ElementTree as ET
root=Path('prepared/00_framework_modern')
ns='http://maven.apache.org/POM/4.0.0'; N={'m':ns}; ET.register_namespace('',ns)
versions={('org.elasticsearch','elasticsearch'):'6.2.4',('org.springframework.session','spring-session'):'1.3.5.RELEASE',('mysql','mysql-connector-java'):'8.0.11',('ch.qos.logback','logback-core'):'1.2.13',('ch.qos.logback','logback-classic'):'1.2.13',('org.slf4j','slf4j-api'):'1.7.36',('io.reactivex','rxjava'):'1.3.8'}
for p in root.rglob('pom.xml'):
    t=ET.parse(p); r=t.getroot(); ch=False
    for d in r.findall('.//m:dependencies/m:dependency',N):
        g=d.find('m:groupId',N); a=d.find('m:artifactId',N); v=d.find('m:version',N)
        key=((g.text or '').strip() if g is not None else '',(a.text or '').strip() if a is not None else '')
        if key in versions and v is None: ET.SubElement(d,f'{{{ns}}}version').text=versions[key]; ch=True
        sp=d.find('m:systemPath',N)
        if sp is not None and sp.text and re.match(r'^[A-Za-z]:/',sp.text):
            cand=list(root.rglob(Path(sp.text).name)); sp.text=str(cand[0].resolve()); ch=True
    if ch:t.write(p,encoding='utf-8',xml_declaration=True)
cp=root/'core/pom.xml'; t=ET.parse(cp); r=t.getroot(); build=r.find('m:build',N); plugins=build.find('m:plugins',N)
for pl in list(plugins.findall('m:plugin',N)):
    a=pl.find('m:artifactId',N)
    if a is not None and a.text=='apt-maven-plugin': plugins.remove(pl)
compiler=None
for pl in plugins.findall('m:plugin',N):
    a=pl.find('m:artifactId',N)
    if a is not None and a.text=='maven-compiler-plugin': compiler=pl; break
if compiler is None:
    compiler=ET.SubElement(plugins,f'{{{ns}}}plugin'); ET.SubElement(compiler,f'{{{ns}}}groupId').text='org.apache.maven.plugins'; ET.SubElement(compiler,f'{{{ns}}}artifactId').text='maven-compiler-plugin'; ET.SubElement(compiler,f'{{{ns}}}version').text='3.14.0'
conf=compiler.find('m:configuration',N)
if conf is None: conf=ET.SubElement(compiler,f'{{{ns}}}configuration')
for old in list(conf.findall('m:annotationProcessorPaths',N))+list(conf.findall('m:annotationProcessors',N)): conf.remove(old)
app=ET.SubElement(conf,f'{{{ns}}}annotationProcessorPaths')
for g,a,v,c in [('org.projectlombok','lombok','1.18.40',None),('com.querydsl','querydsl-apt','5.1.0','jakarta')]:
    path=ET.SubElement(app,f'{{{ns}}}path'); ET.SubElement(path,f'{{{ns}}}groupId').text=g; ET.SubElement(path,f'{{{ns}}}artifactId').text=a; ET.SubElement(path,f'{{{ns}}}version').text=v
    if c: ET.SubElement(path,f'{{{ns}}}classifier').text=c
aps=ET.SubElement(conf,f'{{{ns}}}annotationProcessors')
ET.SubElement(aps,f'{{{ns}}}annotationProcessor').text='lombok.launch.AnnotationProcessorHider$AnnotationProcessor'
ET.SubElement(aps,f'{{{ns}}}annotationProcessor').text='com.querydsl.apt.jpa.JPAAnnotationProcessor'
deps=r.find('m:dependencies',N); existing=set()
for d in deps.findall('m:dependency',N):
    g=d.find('m:groupId',N); a=d.find('m:artifactId',N)
    if g is not None and a is not None:
        key=(g.text,a.text); existing.add(key)
        if key in [('com.querydsl','querydsl-apt'),('com.querydsl','querydsl-jpa')]:
            c=d.find('m:classifier',N)
            if c is None:c=ET.SubElement(d,f'{{{ns}}}classifier')
            c.text='jakarta'
for g,a,v in [('jakarta.persistence','jakarta.persistence-api','3.1.0'),('jakarta.validation','jakarta.validation-api','3.0.2'),('org.dom4j','dom4j','2.1.4'),('org.apache.httpcomponents','httpcore','4.4.5')]:
    if (g,a) not in existing:
        d=ET.SubElement(deps,f'{{{ns}}}dependency'); ET.SubElement(d,f'{{{ns}}}groupId').text=g; ET.SubElement(d,f'{{{ns}}}artifactId').text=a; ET.SubElement(d,f'{{{ns}}}version').text=v
for p in root.rglob('*.java'):
    s=p.read_text(encoding='utf-8',errors='ignore'); n=s.replace('javax.validation.constraints.NotBlank','jakarta.validation.constraints.NotBlank').replace('javax.validation.constraints.NotEmpty','jakarta.validation.constraints.NotEmpty').replace('org.hibernate.validator.constraints.NotBlank','jakarta.validation.constraints.NotBlank').replace('org.hibernate.validator.constraints.NotEmpty','jakarta.validation.constraints.NotEmpty').replace('import sun.misc.BASE64Encoder;','import java.util.Base64;').replace('import com.mongodb.Mongo;\n',''); n=re.sub(r'new BASE64Encoder\(\)\.encode\(([^;]+)\)',r'Base64.getEncoder().encodeToString(\1)',n)
    if n!=s:p.write_text(n,encoding='utf-8')
t.write(cp,encoding='utf-8',xml_declaration=True)
