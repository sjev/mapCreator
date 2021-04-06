# -*- coding: utf-8 -*-
"""
Map creation script

"""
import sys
import os
from configparser import ConfigParser
import math
from PIL import Image
import urllib.request, urllib.parse, urllib.error


# tile positions, see https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Lon..2Flat._to_tile_numbers_2
def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return (xtile, ytile)


p = ConfigParser()
p.optionxform = str
p.read('settings.ini')


name = sys.argv[1] # section from ini

source =  p.get(name,'source')
zoom = p.getint(name,'zoom')

if not os.path.exists( p.get(name,'dest')):
    os.mkdir( p.get(name,'dest'))

dest = os.path.join( p.get(name,'dest') , "%s_zoom%i.jpeg" % (name,zoom))
tilestore = p.get(name,'tilestore')

# parse bounding box
txt = p.get(name,'bbox')
c = [float(v) for v in txt.split('"')[1::2]]
bbox = dict(list(zip(['e','n','s','w'], c)))

if not os.path.exists(tilestore):
    os.makedirs(tilestore)

top_left = deg2num(bbox['n'],bbox['w'], zoom)
bottom_right = deg2num(bbox['s'],bbox['e'], zoom)


# create tile list 
tiles = []

for x in range(top_left[0], bottom_right[0]):
    for y in range(top_left[1], bottom_right[1]):
        tiles.append((zoom,x,y))
        
print('Nr tiles: ', len(tiles))


# download tiles and make map


height = (bottom_right[1] - top_left[1]) * 256
width = (bottom_right[0] - top_left[0]) * 256
img = Image.new("RGB", (width,height))

for idx,tile in enumerate(tiles):
    
    zoom,x,y = tile
    fName = '_'.join([str(f) for f in tile]) + '.png'
    fName = os.path.join(tilestore, fName)
    print('[%i/%i] %s' % (idx+1,len(tiles),fName), end=' ')
    if not os.path.exists(fName):
        url = source.format(*tile)
        print(f'Requesting {url}    ', end='')
        urllib.request.urlretrieve(url,fName)
        print(' ok')
    else:
        print(' cached')
        
    # paste
    tmp = Image.open(fName)
    img.paste(tmp, (256 * (x - top_left[0]), 256 * (y - top_left[1])))
    
print('Saving to ', dest)
img.save(dest, "JPEG")