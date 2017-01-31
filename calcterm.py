import common

def match_colors(left, right):
    def gen_map(primary, secondary):
        return {c: sorted(secondary, key=lambda x: common.colordiff(c, x)) for x in primary}
    
    leftresult, rightresult = common.matchmaker(gen_map(left, right), gen_map(right, left))
    return {c: v[0] if len(leftresult) > 0 else None for c, v in leftresult.items()}

def load_term(text, background, colors):
    # Is it light or dark?
    islight = common.colordiff(background, "#ffffff") + common.colordiff(text, "#000000")
    isdark = common.colordiff(background, "#000000") + common.colordiff(text, "#ffffff")
    
    tcolors = xterm[:]
    scolors = colors[:]
    
    if text in scolors: scolors.remove(text)
    if background in scolors: scolors.remove(background)
    
    if islight > isdark:
        del tcolors[0]
    else:
        del tcolors[0]
        del tcolors[7]
    
    match_result = match_colors(tcolors, scolors)
    mresult = [match_result[c][0] if len(match_result[c]) > 0 else None for c in tcolors]
    
    if islight > isdark:
        mresult.insert(0, text)
    else:
        mresult.insert(0, background)
        mresult.insert(7, text)
    
    return mresult
