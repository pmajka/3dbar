import scipy
import Image
import os

commands =[\
        'wget http://www.ini.uzh.ch/~acardona/data/membranes-neurites-glia.tif.tar.bz2 -O atlases/tem/src/membranes-neurites-glia.tif.tar.bz2',
        'bunzip2 atlases/tem/src/membranes-neurites-glia.tif.tar.bz2',
        'tar -xvvf atlases/tem/src/membranes-neurites-glia.tif.tar -C atlases/tem/src/']

map(os.system, commands)

multiImage = scipy.misc.imread('atlases/tem/src/membranes-neurites-glia.tif')
multiImageList = multiImage.tolist()

for i in range(0,30):
    multiImageList.seek(i)
    multiImageList.save('atlases/tem/src/membranes-neurites-glia_%03d.tiff' % i)
