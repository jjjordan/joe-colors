
import vimreader

from common import closeColor256, cterm, xterm

def main(me, infile):
    with open(infile, 'r') as f:
        defs, links = vimreader.readFile(f)
    
    # 256 colors
    writeout("256", do256(defs), links)
    writeout("*", doGui(defs), links)
    return True

CONVERT = {
    "normal":		["-text"],
    "visual":		["-selection"],
    "statusline":	["-status"],
    "cursorline":	["-curlin"],
    "linenr":		["-linum"],
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
    # Conditional
    # Exception
    # Repeat
    # Label
    "operator":		["=Operator"],
    "keyword":		["=Keyword"],
    "preproc":		["=Preproc"],
    "include":		["=IncSystem"],
    # Define
    # Macro
    # PreCondit
    "type":		["=Type"],
    # StorageClass
    # Structure
    "special":		["=Escape"],
    "specialchar":	["=StringEscape"],
    "error":		["=Bad"],
    "todo":		["=TODO"],
    
    "diffadd":		["=diff.AddLine"],
    "diffchange":	["=diff.ChangeLine"],
    "diffdelete":	["=diff.DelLine"],
    "difftext":		["=diff.Text"],
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

def writeout(title, colors, links):
    print(".colors " + title)
    print()
    
    outputs = {}
    loc_colors = {k: v for k, v in colors}
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
            
            if t in loc_colors:
                loc_colors[src] = loc_colors[t]
    
    another = False
    for n, c in loc_colors.items():
        if n in CONVERT:
            for k in CONVERT[n]:
                outputs[k] = c
        else:
            pass
            #print("# Dropped: %s %s" % (n, c))
            #another = True
    
    if another: print()
    
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

def do256(colors):
    result = []
    for n, c in colors.items():
        if (c.cfg is not None and c.cfg > 15) or (c.cbg is not None and c.cbg > 15):
            # Cterm has good stuff here
            result.append((n, tocol(best256(c.cfg), best256(c.cbg)) + attrs(c)))
        elif c.fg is not None or c.bg is not None:
            result.append((n, tocol(closeColor256(c.fg), closeColor256(c.bg)) + attrs(c)))
    
    return result

def doGui(colors):
    result = []
    for n, c in colors.items():
        def pick(gui, ctc):
            if gui is not None:
                return gui
            if ctc is not None:
                return cterm[ctc]
        
        result.append((n, tocol(pick(c.fg, c.cfg), pick(c.bg, c.cbg)) + attrs(c)))
    
    return result

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

if __name__ == '__main__':
    import sys
    sys.exit(0 if main(*sys.argv) else 1)
