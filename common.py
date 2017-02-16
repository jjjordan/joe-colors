import colormath

from colormath.color_objects import sRGBColor, LabColor, HSLColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

diff_cache = {}
def colordiff(x, y):
    if (x.lower(), y.lower()) in diff_cache:
        return diff_cache[(x.lower(), y.lower())]
    result = delta_e_cie2000(convert_color(read_rgb(x), LabColor), convert_color(read_rgb(y), LabColor))
    diff_cache[(x.lower(), y.lower())] = result
    diff_cache[(y.lower(), x.lower())] = result
    return result

def read_rgb(rgb):
    rgb = rgb.lstrip('#').lstrip('$')
    return sRGBColor(int(rgb[0:2], 16) / 256, int(rgb[2:4], 16) / 256, int(rgb[4:6], 16) / 256)

def rgb2hsl(rgb):
    return convert_color(read_rgb(rgb), HSLColor)

xterm = ['#000000', '#cd0000', '#00cd00', '#cdcd00', '#0000ee', '#cd00cd', '#00cdcd', '#e5e5e5',
         '#777777', '#ff0000', '#00ff00', '#ffff00', '#5c5cff', '#ff00ff', '#00ffff', '#ffffff']

def ctermColors():
    colors = []

    # Extended colors
    extvals = [0x00, 0x5f, 0x87, 0xaf, 0xdf, 0xff]
    for r in extvals:
        for g in extvals:
            for b in extvals:
                colors.append((r, g, b))

    # Grayscale
    for v in [0x08, 0x12, 0x1c, 0x26, 0x30, 0x3a, 0x44, 0x4e, 0x58, 0x60, 0x66, 0x76,
              0x80, 0x8a, 0x94, 0x9e, 0xa8, 0xb2, 0xbc, 0xc6, 0xd0, 0xda, 0xe4, 0xee]:
        colors.append((v, v, v))

    # Convert colors to #RRGGBB
    return ["#%02x%02x%02x" % rgb for rgb in colors]

cterm = xterm + ctermColors()

def closeColor256(color):
    if color is None: return color
    best = None
    bestscore = 9999999
    for i in range(16, 256):
        delta = colordiff(cterm[i], color)
        if delta < bestscore:
            bestscore = delta
            best = i
    return best

def matchmaker(left, right):
    # Matchmaker's algorithm
    changes = True
    while changes:
        # Morning
        balconies = {k: [] for k in left}
        for c in right:
            if len(right[c]) > 0:
                balconies[right[c][0]].append(c)
        
        # Afternoon/evening
        changes = False
        for c in left:
            if len(balconies[c]) > 1:
                place = {suitor: idx for idx, suitor in enumerate(balconies[c])}
                balconies[c].sort(key=lambda x: place[x])
                for loser in balconies[c][1:]:
                    del right[loser][0]
                    changes = True
    
    balconies = {k: [] for k in left}
    for c in right:
        if len(right[c]) > 0:
            balconies[right[c][0]].append(c)
    
    tres = {k: balconies[k][0] for k in balconies if len(balconies[k]) > 0}
    
    return left, right
