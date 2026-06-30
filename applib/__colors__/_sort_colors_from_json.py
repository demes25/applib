from netlib.filecaster import Filecaster, here
from netlib import logs
import math
from coloraide import Color

logs.init(filepath=None)
directory = here()

def to_rgb(color : str) -> tuple[int, int, int]:
    color = color.removeprefix('#')
    r = int(color[:2], 16) / 255
    g = int(color[2:4], 16) / 255
    b = int(color[4:6], 16) / 255
    return r,g,b


sorted_colors = {
    'red' : {},
    'orange' : {},
    'yellow' : {},
    'green' : {},
    'cyan' : {},
    'blue' : {},
    'purple' : {},
    'magenta' : {},
    'gray' : {}
}

def oklch(colorstr):
    rgb = to_rgb(colorstr)
    return Color('srgb', rgb).convert("oklch")


def divide(item):
    key, val = item
    
    h = oklch(val)['h']

    if math.isnan(h):
        d = sorted_colors['gray']  

    elif 10 < h < 32:
        d = sorted_colors['red']
    
    elif 32 < h < 75:
        d = sorted_colors['orange']
    
    elif 50 < h < 114:
        d = sorted_colors['yellow']

    elif 95 < h < 178:
        d = sorted_colors['green']

    elif 170 < h < 210:
        d = sorted_colors['cyan']
    
    elif 210 < h < 285:
        d = sorted_colors['blue']
    
    elif 275 < h < 345:
        d = sorted_colors['purple']
    else:
        d = sorted_colors['magenta']
    
    d[key] = val
    

def sort_key(item):
    _, val = item 
    h, l = oklch(val)["h"], oklch(val)["l"]
    return 361 if math.isnan(h) else h, l


f = Filecaster(directory=directory, name='colors', ext='json', separator='!', mode='r')

dct = f.read()

f.exit()

for item in dct.items():
    divide(item)


f = Filecaster(directory=directory, name='sorted_colors', ext='json', indent=2)

for color, cdct in sorted_colors.items():
    sorted_items = sorted(cdct.items(), key=sort_key)
    sorted_colors[color] = dict(sorted_items)

f.cast(sorted_colors)
f.exit()






