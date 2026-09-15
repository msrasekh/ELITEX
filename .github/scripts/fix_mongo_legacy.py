from pathlib import Path
import xml.etree.ElementTree as ET
root=Path('prepared/00_framework_modern')
# Decimal converter carried an unused legacy Mongo import; remove only there.
p=root/'core/src/main/java/com/bizzan/bitrade/util/Decimal128ToBigDecimalConverter.java'
if p.exists():
    s=p.read_text(encoding='utf-8',errors='ignore').replace('import com.mongodb.Mongo;\n','')
    p.write_text(s,encoding='utf-8')
# Admin uses Spring Data MongoDB 1.10.x whose AbstractMongoConfiguration contract
# is com.mongodb.Mongo; provide the matching 3.x driver instead of the 4.x legacy driver.
ns='http://maven.apache.org/POM/4.0.0'; N={'m':ns}; ET.register_namespace('',ns)
ap=root/'admin/pom.xml'; t=ET.parse(ap); r=t.getroot(); deps=r.find('m:dependencies',N)
for d in list(deps.findall('m:dependency',N)):
    if d.findtext('m:groupId',default='',namespaces=N)=='org.mongodb' and d.findtext('m:artifactId',default='',namespaces=N)=='mongodb-driver-legacy':
        deps.remove(d)
present={(d.findtext('m:groupId',default='',namespaces=N),d.findtext('m:artifactId',default='',namespaces=N)) for d in deps.findall('m:dependency',N)}
if ('org.mongodb','mongo-java-driver') not in present:
    d=ET.SubElement(deps,f'{{{ns}}}dependency')
    ET.SubElement(d,f'{{{ns}}}groupId').text='org.mongodb'
    ET.SubElement(d,f'{{{ns}}}artifactId').text='mongo-java-driver'
    ET.SubElement(d,f'{{{ns}}}version').text='3.12.14'
t.write(ap,encoding='utf-8',xml_declaration=True)
