"""
simple type conversions (from CLI values)
"""
def toInt(val, default=0):
    "int from value"
    try:
        return int(val)
    except:
        return default

def toFloat(val, default=0.0):
    "float from value"
    try:
        return float(val)
    except:
        return default

def toBool(val):
    "bool from value"
    return True if val else False
