import os, sys
import csv

def to_rgb(r ,g, b):
    return '%02x%02x%02x' % (r, g, b)

label_desc_file = sys.argv[1]
output_fullname_file = sys.argv[2]
label_desc  = open(label_desc_file, "rb")
csv_reader = csv.reader(label_desc, delimiter=' ', quotechar='"', quoting=csv.QUOTE_ALL)

results = []

for row in csv_reader:
    row = filter(None, row)

    # Skip lines which are comments
    if row[0][0] != "#":
        label_id = int(row[0])
        r, g, b = tuple(map(int, row[1:4]))
        fullname = row[7].replace('"', "")
        abbreviation = fullname[0:2]

        # Remvoe labels above 100 as they are not related
        # to anatomy
        if label_id < 100:
            results.append([to_rgb(label_id, label_id, label_id),
                            abbreviation, to_rgb(r,g,b), fullname])

writer = file(output_fullname_file, 'w')
for line in results:
    writer_string = "\t".join(map(str, line)) + "\n"
    writer.write(writer_string)
