
import re
import sys

import common
import jcffile

def main(infiles):
    for infile in infiles:
        print("Processing %s... " % infile, end="")
        sys.stdout.flush()
        jcf = jcffile.JCFFile().load(infile)
        guisect = jcf.getSection('*')
        
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
        
        sect256 = jcf.getSection('256')
        if sect256 is not None:
            sect256.content = newcontent
        else:
            sect256 = jcffile.JCFSection("256")
            sect256.colorline = ".colors 256\n"
            sect256.content = newcontent
            jcf.addSection(sect256)
        
        print("Writing output... ", end="")
        jcf.save(infile)
        print("Done.")
        
        print(checkDifferences(differences))


def getDifference(c1, c2):
    hsl1, hsl2 = [common.rgb2hsl(c).get_value_tuple() for c in [c1, c2]]
    hsldiff = [abs(x - y) for x, y in zip(hsl1, hsl2)]
    # Fix hue diff, since it's in degrees
    hsldiff[0] = min(hsldiff[0], 360 - hsldiff[0])
    return [common.colordiff(c1, c2)] + hsldiff

def checkDifferences(diffs):
    worst = [None, None, None, None]
    worstPairs = [None, None, None, None]
    for i in range(4):
        for k, v in diffs.items():
            if worst[i] is None or worst[i] < v[i]:
                worst[i] = v[i]
                worstPairs[i] = k
    
    return "\tWorst values: %s\n\tWorst pairs: %s" % (repr(worst), repr(worstPairs))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Convert RGB colors in JCF color scheme to xterm-256 palette")
    parser.add_argument('infiles', type=str, nargs='*', help="Input JCF files")

    args = parser.parse_args()
    sys.exit(0 if main(args.infiles) else 1)

