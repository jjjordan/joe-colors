
import common
import re
import sys

def main(infiles):
    for infile in infiles:
        print("Processing %s... " % infile, end="")
        sys.stdout.flush()
        jcf = loadJCF(infile)
        guisect = next((sect for sect in jcf if sect.colors == '*'), None)
        
        if not guisect:
            print("No truecolor section, skipping.")
            continue
        
        differences = {}
        changes = {}
        for rgb in re.findall(r"\$[0-9a-fA-F]{6}", guisect.content):
            c = rgb.upper().lstrip('$')
            if c not in changes:
                c256 = common.closeColor256(c)
                changes[c] = str(c256)
                differences[(c, c256)] = getDifference(common.cterm[c256], c)
        
        newcontent = guisect.content
        for k, v in changes.items():
            newcontent = re.sub(r"\$" + k, v, newcontent, 0, re.I)
        
        sect256 = next((sect for sect in jcf if sect.colors == '256'), None)
        if sect256 is not None:
            sect256.content = newcontent
        else:
            sect256 = Section("256")
            sect256.colorline = ".colors 256\n"
            sect256.content = newcontent
            jcf.append(sect256)
        
        print("Writing output... ", end="")
        writeout(infile, jcf)
        print("Done.")
        
        print(checkDifferences(differences))

def loadJCF(infile):
    with open(infile, 'r') as f:
        sections = [Section(None)]
        lastSectionData = []
        for line in f:
            d = line.strip()
            if d.startswith('.colors'):
                colors = d[len('.colors'):].strip()
                sect = Section(colors)
                sections[-1].content = ''.join(lastSectionData)
                sections.append(sect)
                sect.colorline = line
                lastSectionData = []
            else:
                lastSectionData.append(line)
        sections[-1].content = ''.join(lastSectionData)

        return sections

def getDifference(c1, c2):
    hsl1, hsl2 = [common.rgb2hsl(c).get_value_tuple() for c in [c1, c2]]
    return [common.colordiff(c1, c2)] + list(abs(hsl1[i] - hsl2[i]) for i in range(3))

def checkDifferences(diffs):
    worst = [None, None, None, None]
    worstPairs = [None, None, None, None]
    for i in range(4):
        for k, v in diffs.items():
            if worst[i] is None or worst[i] < v[i]:
                worst[i] = v[i]
                worstPairs[i] = k
    
    return "\tWorst values: %s\n\tWorst pairs: %s" % (repr(worst), repr(worstPairs))

def writeout(outfile, jcf):
    with open(outfile, 'w') as f:
        for sect in jcf:
            f.write(sect.colorline)
            f.write(sect.content)
            if not sect.content.endswith("\n\n"):
                f.write("\n")
                if sect.content.endswith("\n"):
                    f.write("\n")

class Section:
    def __init__(self, colors):
        self.colors = colors
        self.colorline = ""
        self.content = ""

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Convert RGB colors in JCF color scheme to xterm-256 palette")
    parser.add_argument('infiles', type=str, nargs='*', help="Input JCF files")

    args = parser.parse_args()
    sys.exit(0 if main(args.infiles) else 1)

