import os
import Image, ImageOps

"""
This parser requires ImageMagick (http://www.imagemagick.org/) library.
You can install it by typing:
    sudo apt-get install imagemagick
"""

commands =[\
    'wget http://www.ini.uzh.ch/~acardona/data/membranes-neurites-glia.tif.tar.bz2 -O atlases/tem/src/membranes-neurites-glia.tif.tar.bz2',
    'bunzip2 -f atlases/tem/src/membranes-neurites-glia.tif.tar.bz2',
    'tar -xvvf atlases/tem/src/membranes-neurites-glia.tif.tar -C atlases/tem/src/',
    'convert atlases/tem/src/membranes-neurites-glia.tif -level 0,255 -depth 8 -type grayscale atlases/tem/src/membranes-neurites-glia.png']

map(os.system, commands)

for index in range(30):
    filename = 'atlases/tem/src/membranes-neurites-glia-%d.png' % index
    frame = Image.open(filename)
    frame  = ImageOps.expand(frame, border=4, fill=168)
    frame.save(filename)
