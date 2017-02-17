
class JCFFile:
    def __init__(self):
        self.sections = []
    
    def load(self, filename):
        with open(filename, 'r') as f:
            sections = [JCFSection(None)]
            lastSectionData = []
            for line in f:
                d = line.strip()
                if d.startswith('.colors'):
                    colors = d[len('.colors'):].strip()
                    sect = JCFSection(colors)
                    sections[-1].content = ''.join(lastSectionData)
                    sections.append(sect)
                    sect.colorline = line
                    lastSectionData = []
                else:
                    lastSectionData.append(line)
            sections[-1].content = ''.join(lastSectionData)
            
            self.sections = sections
            return self
    
    def save(self, filename):
        with open(filename, 'w') as f:
            for sect in self.sections:
                f.write(sect.colorline)
                f.write(sect.content)
                if not sect.content.endswith("\n\n"):
                    f.write("\n")
                    if not sect.content.endswith("\n"):
                        f.write("\n")
    
    def getSection(self, colors):
        return next((s for s in self.sections if s.colors == colors), None)
    
    def addSection(self, section):
        self.sections.append(section)

class JCFSection:
    def __init__(self, colors):
        self.colors = colors
        self.colorline = ""
        self.content = ""
    
    def __repr__(self):
        return "<JCF Section %s>" % repr(self.colors)
    
    def parse(self):
        result = {}
        for line in self.content.split('\n'):
            cmt = line.find('#')
            if cmt >= 0:
                line = line[:cmt]
            
            tokens = line.split()
            if len(tokens) == 0: continue
            if tokens[0].startswith('.'): continue
            
            spec = JCFSpec(key=tokens[0])
            if spec.key == '-term':
                spec.key += ' ' + tokens[1]
                remaining = tokens[2:]
            else:
                remaining = tokens[1:]
            
            for token in remaining:
                # This assumes:
                #  - No space between colors and '/'
                #  - fg_* and bg_* are not used.
                # These assumptions are wrong for general purpose,
                # but good enough for our use cases here.
                if '/' in token:
                    spec.fg, spec.bg = token.split('/')
                    if not spec.fg: spec.fg = None
                    if not spec.bg: spec.bg = None
                elif token.lower() in ('italic', 'underline', 'bold', 'dim', 'blink', 'reverse'):
                    spec.attrs.append(token.lower())
                elif token.startswith('+'):
                    spec.refs.append(token[1:])
                else:
                    spec.fg = token
            
            result[spec.key] = spec
        
        return result

class JCFSpec:
    def __init__(self, key=None, fg=None, bg=None, attrs=None, refs=None):
        self.key = key
        self.fg = fg
        self.bg = bg
        self.attrs = attrs or []
        self.refs = refs or []
    
    def __str__(self):
        result = self.key
        if self.refs:
            result += " ".join("+%s" % r for r in self.refs)
        else:
            if self.bg:
                result += " %s/%s" % (self.fg or '', self.bg or '')
            elif self.fg:
                result += " " + self.fg
            if self.attrs:
                result += ' ' + ' '.join(self.attrs)
        return result
    
    def __repr__(self):
        return "<JCFSpec: %s>" % str(self)
