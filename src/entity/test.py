import xml.etree.ElementTree as ET
import pandas as pd
import csv
import re

csv_file = open("index.csv", "r")
f = csv.reader(csv_file)
header = next(f)

term_map = {}
for row in f:
    term =  row[0]
    if len(term) > 0:
        term_map[term] = len(term)

term_map = sorted(term_map.items(), key=lambda x:x[1], reverse=True)

f = open('bbp.xml')
data1 = f.read()  # ファイル終端まで全て読んだデータを返す
f.close()

for i in range(len(term_map)):
    obj = term_map[i]
    term = obj[0]
    data1 = data1.replace(term, "<name corresp=\"https://ja.wikipedia.org/wiki/"+str(i)+"\">" + term + "</name>")

for i in range(len(term_map)):
    ftext = '"https://ja.wikipedia.org/wiki/'+str(i)+'"'
    ttext = '"https://ja.wikipedia.org/wiki/'+term_map[i][0]+'"'
    data1 = data1.replace(ftext, ttext)

root = ET.fromstring(data1)

tree = ET.ElementTree(root)
ET.register_namespace('', "http://www.tei-c.org/ns/1.0")

tree.write("bbp2.xml", encoding="utf-8")