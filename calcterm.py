import math

from common import xterm, cterm, colordiff
from munkres import Munkres

def match_colors(tcolors, scolors):
    slen = len(scolors)
    n = max(len(tcolors), slen * math.ceil(len(tcolors) / slen))
    M = [[colordiff(tcolors[i], scolors[t % slen]) if i < len(tcolors) else 0 for t in range(n)] for i in range(n)]

    solution = Munkres().compute(M)
    return {tcolors[i]: scolors[t % slen] for i, t in solution if i < len(tcolors)}

def load_term(text, background, colors):
    # Is it light or dark?
    islight = colordiff(background, "#ffffff") + colordiff(text, "#000000")
    isdark = colordiff(background, "#000000") + colordiff(text, "#ffffff")
    
    tcolors = xterm[:]
    scolors = colors[:]
    
    if text in scolors: scolors.remove(text)
    if background in scolors: scolors.remove(background)
    
    if islight < isdark:
        del tcolors[0]
    else:
        del tcolors[0]
        del tcolors[7]
    
    match_result = match_colors(tcolors, scolors)
    mresult = [match_result[c] for c in tcolors if c in match_result]
    
    if islight < isdark:
        mresult.insert(0, text)
    else:
        mresult.insert(0, background)
        mresult.insert(7, text)
    
    return mresult
