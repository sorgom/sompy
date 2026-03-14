"""some formatting"""

def humanbytes(val:int, metric=False):
    """human readable bytes format with dynamic precision"""
    prefs = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    sig = ''
    if val < 0:
        sig = '-'
        val = -val
    pref = ''
    prec = 0
    div = 1
    fac = 1000 if metric else 1024
    for p in prefs:
        if val < div * fac: break
        div *= fac
        pref = p
    if div > 1:
        val = float(val) / div
        #   dynamic precision
        prec = max(1, 4 - len(str(int(val))))
    return f'{sig}{val:.0{prec}f} {pref}B'
