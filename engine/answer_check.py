"""
Lenient, forgiving answer comparison.
Fixes the 'correct answer marked wrong' bug: the old code did a raw
lower/strip string == string comparison, which fails on things like
'-5' vs '-5 ', 'x=5' vs '5', '3/4' vs '0.75', '12.0' vs '12', spacing
around exponents/operators, degree signs, units, etc.
"""
import re
from fractions import Fraction


def _clean(text):
    t = str(text).strip().lower()
    t = t.replace(" ", "")
    # strip a leading "x=" / "y=" / "answer=" style prefix
    t = re.sub(r'^[a-z]+=', '', t)
    # strip common trailing units/symbols the learner might type or skip
    t = re.sub(r'(cm2|cm²|cm3|cm³|cm|m2|m²|m|°|percent|%)$', '', t)
    return t


def _to_number(text):
    t = text.replace('°', '').replace('%', '')
    try:
        return float(Fraction(t))
    except Exception:
        pass
    try:
        return float(t)
    except Exception:
        return None


def answers_match(user_input, expected, tolerance=0.01):
    u = _clean(user_input)
    e = _clean(expected)

    if not u:
        return False

    if u == e:
        return True

    # Numeric / fractional comparison (handles 3/4 vs 0.75, 12 vs 12.0, etc.)
    un = _to_number(u)
    en = _to_number(e)
    if un is not None and en is not None:
        return abs(un - en) <= tolerance

    # Coordinate-pair style answers e.g. "(3,4)" vs "( 3 , 4 )"
    u_coords = re.findall(r'-?\d+\.?\d*', u)
    e_coords = re.findall(r'-?\d+\.?\d*', e)
    if u_coords and e_coords and len(u_coords) == len(e_coords) and ('(' in e or ',' in e):
        try:
            return all(abs(float(a) - float(b)) <= tolerance for a, b in zip(u_coords, e_coords))
        except ValueError:
            pass

    # Exponent style answers e.g. "3^6" vs "3^6" already covered by equality;
    # also accept "729" as correct if expected is "3^6"
    exp_match = re.match(r'^(-?\d+)\^(\d+)$', e)
    if exp_match:
        base, power = int(exp_match.group(1)), int(exp_match.group(2))
        if un is not None and abs(un - (base ** power)) <= tolerance:
            return True

    return False
