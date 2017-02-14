
import json
import os.path
import vimreader

from common import closeColor256, cterm, xterm
from calcterm import load_term

def main(me, infile):
    with open(infile, 'r') as f:
        defs, links = vimreader.readFile(f)
    
    options = loadOverrides(infile)
    
    # Copyright output
    print()
    if options['copy']:
        for ln in options['copy']:
            print("# " + ln)
        print()
    
    # Overrides
    applyOverrides(options['overrides'])
    
    if 'no256' not in options['options']:
        if 'strict256' in options['options']:
            cols = assignColors(defs, take256, links)
        elif 'fromgui' in options['options']:
            cols = assignColors(defs, takegui256, links)
        else:
            cols = assignColors(defs, cvt256, links)
        
        cols.update(options['colors256'])
        applyTerm(cols, options['term256'] or options['term'], gui=False)
        writeout("256", cols)
    
    cols = assignColors(defs, cvtGui, links)
    cols.update(options['colorsgui'])
    applyTerm(cols, options['term'], gui=True)
    writeout("*", cols)
    
    return True

CONVERT = {
    "normal":		["-text"],
    "visual":		["-selection"],
    "statusline":	["-status"],
    "cursorline":	["-curlin"],
    "linenr":		["-linum"],
    "cursorlinenr":	["-curlinum"],
    "pmenusel":		["-menusel"],
    "cursor":		["-cursor"],
    
    "comment":		["=Comment"],
    "constant":		["=Constant"],
    "string":		["=String"],
    "character":	["=Character"],
    "number":		["=Number"],
    "boolean":		["=Boolean"],
    "float":		["=Float"],
    
    "identifier":	["=DefinedIdent"],
    "function":		["=DefinedFunction"],
    "statement":	["=Statement"],
    "conditional":	["=Conditional"],
    "repeat":		["=Loop"],
    "label":		["=Label"],
    # Exception
    "operator":		["=Operator"],
    "keyword":		["=Keyword"],
    "preproc":		["=Preproc"],
    "include":		["=IncSystem"],
    "precondit":	["=Precond"],
    "define":		["=Define"],
    "macro":		["=Macro"],
    "type":		["=Type"],
    "storageclass":	["=StorageClass"],
    "structure":	["=Structure"],
    "special":		["=Escape"],
    "specialchar":	["=StringEscape"],
    "error":		["=Bad"],
    "todo":		["=TODO"],
    
    "diffadd":		["=diff.AddLine"],
    "diffchange":	["=diff.ChgLine"],
    "diffdelete":	["=diff.DelLine"]
}

ORDER = [
    "-text", "-status", "-selection", "-linum", "-curlin", "-curlinum", "-menusel", "-cursor",
    "",
    "-term 0", "-term 1", "-term 2", "-term 3", "-term 4", "-term 5", "-term 6", "-term 7",
    "-term 8", "-term 9", "-term 10", "-term 11", "-term 12", "-term 13", "-term 14", "-term 15",
    "",
    ["=Idle"], "=Keyword", "=Operator", "=Type",
    "",
]

def assignColors(defs, convert, links):
    # Convert defs into colors.  Collect colors so we can
    # calculate terminal colors
    colors = {}
    allcolors = set()
    tcolreverse = {}
    outputs = {}
    
    for n, c in defs.items():
        fg, bg = convert(c)
        colors[n] = tocol(fg, bg) + attrs(c)
        for c in (fg, bg):
            if c is not None:
                guic = toGuiColor(c)
                tcolreverse[guic] = c
                allcolors.add(guic)
    
    # Calculate terminal colors
    text_fg, text_bg = convert(defs['normal'])
    for i, c in enumerate(load_term(toGuiColor(text_fg), toGuiColor(text_bg), list(allcolors))):
        outcolor = tcolreverse[c]
        if isinstance(outcolor, str):
            outputs['-term %d' % i] = '$' + outcolor.lstrip('#$').upper()
        else:
            outputs['-term %d' % i] = outcolor
    
    loc_links = {k: v for k, v in links}
    
    # Pull in attributes from links; either propagate or generate a link in the output
    for src, tgt in loc_links.items():
        if src in CONVERT:
            if tgt.link in CONVERT:
                s = next(filter(lambda x: x.startswith('='), CONVERT[src]), None)
                t = next(filter(lambda x: x.startswith('='), CONVERT[tgt.link]), None)
                if s and t:
                    # We can generate a link
                    outputs[s] = '+' + t.lstrip('=')
                    continue
            
            t = tgt.link
            while t in links and loc_links[t]:
                t = loc_links[t].link
            
            if t in colors:
                colors[src] = colors[t]
    
    for n, c in colors.items():
        if n in CONVERT:
            for k in CONVERT[n]:
                outputs[k] = c
        else:
            pass
    
    return outputs

def writeout(title, outputs):
    print(".colors " + title)
    print()
    
    # Print out stuff in order
    for o in ORDER:
        if o == "":
            print()
        elif isinstance(o, list):
            print(o[0])
        elif o in outputs:
            print("%s %s" % (o, outputs[o]))
            del outputs[o]
    
    dbl = {}
    for k, v in list(outputs.items()):
        if '.' in k:
            dbl[k] = v
            del outputs[k]
    
    for k in sorted(outputs.keys()):
        print("%s %s" % (k, outputs[k]))
    
    print()
    for k in sorted(dbl.keys()):
        print("%s %s" % (k, dbl[k]))
    
    print()

def parts(cdef):
    return {
        'fg': cdef.fg,
        'bg': cdef.bg,
        'cfg': cdef.cfg,
        'cbg': cdef.cbg,
        'bold': cdef.bold,
        'italic': cdef.italic,
        'underline': cdef.underline
    }

def cvt256(color):
    """Take 256 color if it's an extended color, otherwise convert from GUI"""
    if (color.cfg is not None and color.cfg > 15) or (color.cbg is not None and color.cbg > 15):
        return best256(color.cfg), best256(color.cbg)
    elif color.fg is not None or color.bg is not None:
        return closeColor256(color.fg), closeColor256(color.bg)
    else:
        return None, None

def take256(color):
    """Take 256 color only"""
    if color.cfg is not None or color.cbg is not None:
        return best256(color.cfg), best256(color.cbg)
    else:
        return None, None

def takegui256(color):
    """Convert GUI color to 256"""
    if color.fg is not None or color.bg is not None:
        return closeColor256(color.fg), closeColor256(color.bg)
    else:
        return None, None

def cvtGui(color):
    def pick(gui, ctc):
        if gui is not None:
            return gui
        if ctc is not None:
            return cterm[ctc]
    return pick(color.fg, color.cfg), pick(color.bg, color.cbg)

def tocol(fg, bg):
    result = ""
    if fg is not None:
        result = fmtcolor(fg)
    if bg is not None:
        result += "/" + fmtcolor(bg)
    return result

def best256(color):
    if color is None:
        return None
    if color > 15:
        return color
    return closeColor256(xterm[color])

def toGuiColor(color):
    if isinstance(color, int):
        return cterm[color]
    elif isinstance(color, str):
        return color
    else:
        return None

def attrs(cdef):
    result = ""
    if cdef.bold:
        result += "bold "
    if cdef.italic:
        result += "italic "
    if cdef.underline:
        result += "underline"
    
    if len(result) > 0:
        return " " + result.strip()
    else:
        return ""

def fmtcolor(c):
    if c is None: return ""
    if isinstance(c, int):
        return str(c)
    if c.startswith('#'):
        return '$' + c[1:]
    else:
        return c

def applyOverrides(overrides):
    for k, v in overrides.items():
        # Remove v from CONVERT
        for item in v:
            for ck, cv in CONVERT.items():
                if item in cv:
                    cv.remove(item)
        # Add k->v to CONVERT
        if k in CONVERT:
            CONVERT[k].extend(v)
        else:
            CONVERT[k] = v

def applyTerm(colors, termcolors, gui=True):
    for i in range(len(termcolors)):
        col = termcolors[i]
        if isinstance(col, int) and gui:
            col = '$' + cterm[col].lstrip('#')
        elif isinstance(col, str) and not gui:
            col = closeColor256(col)
        elif isinstance(col, str):
            col = '$' + col.lstrip('#')
        else:
            col = str(col)
        
        colors['-term %d' % i] = col

def loadOverrides(fname):
    with open("overrides.json", "r") as f:
        all_opts = json.load(f)
    name, ext = os.path.splitext(os.path.basename(fname))
    options = all_opts[name] if name in all_opts else {}
    
    dflt = {
        'options': [],
        'copy': [],
        'overrides': {},
        'colors256': {},
        'colorsgui': {},
        'term': [],
        'term256': []
    }
    
    for k, v in dflt.items():
        if k not in options:
            options[k] = v
    
    return options

if __name__ == '__main__':
    import sys
    sys.exit(0 if main(*sys.argv) else 1)
