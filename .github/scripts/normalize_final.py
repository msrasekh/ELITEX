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
        if key in versions and v is None:
            ET.SubElement(d,f'{{{ns}}}version').text=versions[key]; ch=True
        sp=d.find('m:systemPath',N)
        if sp is not None and sp.text and re.match(r'^[A-Za-z]:/',sp.text):
            cand=list(root.rglob(Path(sp.text).name))
            if not cand: raise RuntimeError('missing system jar '+Path(sp.text).name)
            sp.text=str(cand[0].resolve()); ch=True
        if key in [('com.querydsl','querydsl-apt'),('com.querydsl','querydsl-jpa')]:
            c=d.find('m:classifier',N)
            if c is not None: d.remove(c); ch=True
    if ch: t.write(p,encoding='utf-8',xml_declaration=True)
cp=root/'core/pom.xml'; t=ET.parse(cp); r=t.getroot(); build=r.find('m:build',N); plugins=build.find('m:plugins',N)
for pl in list(plugins.findall('m:plugin',N)):
    a=pl.find('m:artifactId',N)
    if a is not None and a.text=='apt-maven-plugin': plugins.remove(pl)
deps=r.find('m:dependencies',N)
existing={(d.find('m:groupId',N).text,d.find('m:artifactId',N).text) for d in deps.findall('m:dependency',N) if d.find('m:groupId',N) is not None and d.find('m:artifactId',N) is not None}
for g,a,v in [('javax.validation','validation-api','2.0.1.Final'),('org.dom4j','dom4j','2.1.4')]:
    if (g,a) not in existing:
        d=ET.SubElement(deps,f'{{{ns}}}dependency'); ET.SubElement(d,f'{{{ns}}}groupId').text=g; ET.SubElement(d,f'{{{ns}}}artifactId').text=a; ET.SubElement(d,f'{{{ns}}}version').text=v
# Force a compatible httpcore carrying legacy annotations.
for d in deps.findall('m:dependency',N):
    g=d.find('m:groupId',N); a=d.find('m:artifactId',N)
    if g is not None and a is not None and g.text=='org.apache.httpcomponents' and a.text=='httpcore':
        v=d.find('m:version',N)
        if v is None: v=ET.SubElement(d,f'{{{ns}}}version')
        v.text='4.4.6'
t.write(cp,encoding='utf-8',xml_declaration=True)
for p in root.rglob('*.java'):
    s=p.read_text(encoding='utf-8',errors='ignore')
    n=s.replace('org.hibernate.validator.constraints.NotBlank','javax.validation.constraints.NotBlank').replace('org.hibernate.validator.constraints.NotEmpty','javax.validation.constraints.NotEmpty').replace('import sun.misc.BASE64Encoder;','import java.util.Base64;').replace('import com.mongodb.Mongo;\n','')
    n=re.sub(r'new BASE64Encoder\(\)\.encode\(([^;]+)\)',r'Base64.getEncoder().encodeToString(\1)',n)
    if n!=s: p.write_text(n,encoding='utf-8')
