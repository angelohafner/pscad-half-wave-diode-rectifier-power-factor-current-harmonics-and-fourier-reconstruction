"""Find and verify fixed-energy GTO windows with specified fundamental displacement."""
from functools import lru_cache
from math import pi, radians, sin
from pathlib import Path
import sys

import numpy as np
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parent
PART5 = ROOT.parent / 'part-5-equal-energy-gtos'
sys.path.insert(0, str(PART5))
from study import GTO, TARGET, VRMS, R, HZ, PEAK, coefficients, quantities, verify


def primitive(theta):
    """Integral of twice the squared sine."""
    return theta - sin(2*theta)/2


@lru_cache(maxsize=2048)
def bounds(alpha):
    """Choose the turn-off edge for exactly five Joules in the positive half-cycle."""
    a = radians(alpha)
    target = primitive(a) + pi * TARGET / (VRMS**2/(R*HZ))
    b = brentq(lambda t: primitive(t) - target, pi/2, pi)
    return alpha, float(np.rad2deg(b))


LEAD_ALPHA = brentq(lambda a: quantities(bounds(a))['lag']+30, 0, GTO[0])
LEAD = bounds(LEAD_ALPHA)
LAG = (180-LEAD[1], 180-LEAD[0])
CASES = {'unity': GTO, 'lag': LAG, 'lead': LEAD}
VALUES = {key: quantities(pair) for key,pair in CASES.items()}


def check():
    for key, angle in [('unity', 0), ('lag', 30), ('lead', -30)]:
        ab = CASES[key]
        verify(ab)
        m = VALUES[key]
        assert abs(m['lag']-angle)<1e-8 and abs(m['energy']-10)<1e-9
        assert abs(m['p']-600)<1e-8 and abs(m['ip']-5)<1e-8
        assert abs(m['pf']-1/np.sqrt(2))<1e-10
        assert abs(m['q1']-600*np.tan(np.deg2rad(angle)))<1e-8
        print(key, 'gate angles:', *(round(x, 7) for x in (*ab,ab[0]+180,ab[1]+180)),
              'Q1:', round(m['q1'],5), 'THD:', round(m['thd'],8))
    for a in np.linspace(LEAD[0], LAG[0], 201):
        m=quantities(bounds(float(a)))
        assert abs(m['energy']-10)<1e-9 and abs(m['ip']-5)<1e-9
    assert np.allclose(abs(coefficients(LEAD)),abs(coefficients(LAG)),rtol=0,atol=2e-12)
    assert np.allclose(coefficients(LAG),-coefficients(LEAD).conj(),rtol=0,atol=2e-12)


if __name__ == '__main__':
    check()
