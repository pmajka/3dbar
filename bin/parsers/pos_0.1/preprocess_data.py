import os
import csv

def to_rgb(r,g,b):
    return '%02x%02x%02x' % (r, g, b)

ifile  = open('label_descriptions.txt', "rb")
reader = csv.reader(ifile, delimiter=' ', quotechar='"', quoting=csv.QUOTE_ALL)

results = []

for row in reader:
    row = filter(None, row)
    lid = int(row[0])
    r,g,b = tuple(map(int, row[1:4]))
    n = row[7].replace('"',"")
    abbr = n[0:2]
    if lid < 100:
        print lid, abbr, to_rgb(r,g,b), n
        results.append([to_rgb(lid,lid,lid), abbr, to_rgb(r,g,b), n])

w = file('fullnames.txt','w')
for l in results:
    wstr = "\t".join(map(str, l)) + "\n"
    w.write(wstr)
