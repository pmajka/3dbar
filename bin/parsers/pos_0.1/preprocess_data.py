import os, sys
import csv

def to_rgb(r, g, b):
    return '%02x%02x%02x' % (r, g, b)

label_desc_file = sys.argv[1]
output_fullname_file = sys.argv[2]
output_parents_file = sys.argv[3]

label_desc  = open(label_desc_file, "rb")
csv_reader = csv.reader(label_desc, delimiter=' ', quotechar='"', quoting=csv.QUOTE_ALL)

results = []
parents = []

for row in csv_reader:
    row = filter(None, row)

    # Skip lines which are comments
    if row[0][0] != "#":
        print row
        label_id = int(row[0])
        if label_id == 0 or label_id >= 200:
            continue

        r, g, b = tuple(map(int, row[1:4]))
        fullname = row[7].split("|")[0].replace('"', "")
        abbreviation = row[7].split("|")[1].replace('"', "")
        parent = row[7].split("|")[2].replace('"', "")

        results.append([to_rgb(label_id, label_id, label_id),
                        abbreviation, to_rgb(r, g, b), fullname])

        parents.append([abbreviation,parent])

writer = file(output_fullname_file, 'w')
for line in results:
    writer_string = "\t".join(map(str, line)) + "\n"
    writer.write(writer_string)

writer = file(output_parents_file, 'w')
for line in parents:
    writer_string = "\t".join(map(str, line)) + "\n"
    writer.write(writer_string)
