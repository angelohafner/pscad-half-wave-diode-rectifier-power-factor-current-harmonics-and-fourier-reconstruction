"""Design a centered GTO window and verify the ideal SCR and GTO waveforms."""
from math import pi, sin, sqrt
from pathlib import Path
import json
import numpy as np
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parent
VRMS, R, HZ, TARGET = 120.0, 12.0, 60.0, 10.0
PEAK = sqrt(2) * VRMS / R
FULL_ENERGY = VRMS**2 / (R * HZ)
WIDTH = brentq(lambda w: (w + sin(w)) / pi - TARGET / FULL_ENERGY, 0, pi)
ALPHA, BETA = np.rad2deg([(pi - WIDTH) / 2, (pi + WIDTH) / 2])
SCR = (90.0, 180.0)
GTO = (ALPHA, BETA)


def coefficients(bounds, last=50):
    """Peak complex phasors with cosine reference for both half cycles."""
    a, b = np.deg2rad(bounds)

    def integral(order):
        if order == 0:
            return b - a
        return (np.exp(-1j * order * b) - np.exp(-1j * order * a)) / (-1j * order)

    c = np.zeros(last + 1, dtype=complex)
    for h in range(1, last + 1, 2):
        c[h] = PEAK / (1j * pi) * (integral(h - 1) - integral(h + 1))
    return c


def quantities(bounds):
    a, b = np.deg2rad(bounds)
    fraction = (b - a - (sin(2*b) - sin(2*a)) / 2) / pi
    current = VRMS / R * sqrt(fraction)
    p = R * current**2
    c1 = coefficients(bounds, 1)[1]
    active_i = -c1.imag / sqrt(2)
    reactive_i = -c1.real / sqrt(2)
    reactive_i = 0.0 if abs(reactive_i) < 1e-12 else reactive_i
    i1 = abs(c1) / sqrt(2)
    ih = sqrt(current**2 - i1**2)
    return dict(energy=p/HZ, p=p, s=VRMS*current, i=current, i1=i1,
                ip=active_i, iq=reactive_i, ih=ih, q1=VRMS*reactive_i,
                lag=float(np.rad2deg(np.arctan2(reactive_i, active_i))),
                thd=ih/i1, pf=p/(VRMS*current))


def verify(bounds):
    """Independent midpoint integration, with sample cells split at physical edges."""
    a, b = np.deg2rad(bounds)
    nodes = np.unique([0., a, b, pi, pi+a, pi+b, 2*pi])
    t, weights = [], []
    for lo, hi in zip(nodes[:-1], nodes[1:]):
        n = max(1, round((hi-lo)*32_000))
        t.extend(lo + (np.arange(n)+.5)*(hi-lo)/n)
        weights.extend(np.full(n, (hi-lo)/(n*2*pi)))
    t, weights = np.array(t), np.array(weights)
    on = (t % pi >= a) & (t % pi < b)
    voltage = sqrt(2)*VRMS*np.sin(t)
    current = np.where(on, voltage/R, 0.0)
    m = quantities(bounds)
    assert abs(np.sum(weights*current**2)*R/HZ - m['energy']) < 2e-8
    assert abs(np.sum(weights*voltage*current) - m['p']) < 2e-6
    coeff = coefficients(bounds)
    for n, expected in enumerate(coeff):
        measured = np.sum(weights*current*np.exp(-1j*n*t)) * (2 if n else 1)
        assert abs(measured - expected) < 5e-8
    assert abs(m['ip']**2 + m['iq']**2 + m['ih']**2 - m['i']**2) < 1e-10
    assert abs(m['pf'] - m['p']/m['s']) < 1e-12


if __name__ == '__main__':
    for bounds in (SCR, GTO):
        verify(bounds)
    g, s = quantities(GTO), quantities(SCR)
    assert abs(g['energy'] - TARGET) < 1e-10 and abs(g['lag']) < 1e-10
    assert abs(g['pf'] - s['pf']) < 1e-10 and abs(g['thd'] - 1) < 1e-10
    print(json.dumps({'angles_deg': [*GTO, ALPHA+180, BETA+180], 'GTO': g, 'SCR': s}, indent=2))
