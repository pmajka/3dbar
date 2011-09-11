import scipy
import Image, ImageOps, ImageSequence
import os

commands =[\
        'wget http://www.ini.uzh.ch/~acardona/data/membranes-neurites-glia.tif.tar.bz2 -O atlases/tem/src/membranes-neurites-glia.tif.tar.bz2',
        'bunzip2 -f atlases/tem/src/membranes-neurites-glia.tif.tar.bz2',
        'tar -xvvf atlases/tem/src/membranes-neurites-glia.tif.tar -C atlases/tem/src/']

map(os.system, commands)

multiImage = scipy.misc.imread('atlases/tem/src/membranes-neurites-glia.tif')
multiImageList = multiImage.tolist()

index = 0
for frame in ImageSequence.Iterator(multiImageList):
    frame = ImageOps.expand(frame, border=4, fill=168)
    frame.save('atlases/tem/src/membranes-neurites-glia_%03d.tiff' % index)
    index += 1
