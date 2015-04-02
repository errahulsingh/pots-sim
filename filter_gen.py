from __future__ import absolute_import, division, print_function
# rework as biquads with zeros/poles
import itertools
import json

import numpy as np
import scipy.signal as sig

FS = 44100

filtersets = {
    'signal': [
        {'func': sig.butter, 'N': 2, 'fn': 200, 'btype': 'high'},
        {'func': sig.butter, 'N': 2, 'fn': 300, 'btype': 'high'},
        {'func': sig.cheby2, 'N': 8, 'fn': 3900, 'rs': 50, 'btype': 'low'},
        {'func': sig.butter, 'N': 4, 'fn': 5000, 'btype': 'low'},
    ],
    'noiseband': [
        {'func': sig.butter, 'N': 4, 'fn': 4000, 'btype': 'low'},
    ],
}

def grouper(n, iterable):
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, n))
        if not chunk:
            return
        yield chunk

def generate_filter_coeffs(filters, fs, output='ba'):
    for filt in filters:
        kwa = filt.copy()
        fgen = kwa.pop('func')
        kwa['Wn'] = 2 * kwa.pop('fn') / fs
        kwa['output'] = output
        yield fgen(**kwa)

def make_biquads(filterset, fs=FS):
    ZPK = list(generate_filter_coeffs(filterset, fs, output='zpk'))

    biquads = []
    singles = []

    # pair off zeros/poles from each filter set and convert to transfer func
    for Z, P, K in ZPK:
        zeros = sorted(Z, key=lambda x: -abs(x.imag))
        poles = sorted(P, key=lambda x: -abs(x.imag))

        for zz, pp in zip(grouper(2, zeros), grouper(2, poles)):
            ba = sig.zpk2tf(zz, pp, K)
            if len(zz) == 2:
                biquads.append(ba)
            else:
                singles.append(ba)

    # convolve the spare singles together to make biquads
    for BA in grouper(2, singles):
        (b1, a1), (b2, a2) = BA
        b = sig.convolve(b1, b2)
        a = sig.convolve(a1, a2)
        biquads.append((b, a))

    return np.array(biquads)

def normalize(biquads, fnorm, fs=FS):
    # normalize to frequency
    tsamp = np.arange(fs) / fs
    test = np.cos(2 * np.pi * fnorm * tsamp)

    for b, a in biquads:
        d = sig.lfilter(b, a, test)
        gain = (max(d[fs//2:]) - min(d[fs//2:])) / 2
        #print(gain)
        b /= gain

def main():
    bqsets = {}
    for fls in filtersets:
        biquads = make_biquads(filtersets[fls])
        normalize(biquads, 1500)
        bqsets[fls] = biquads.tolist()

    with open('biquads.json', 'w') as f:
        json.dump(bqsets, f, indent=2)

if __name__ == '__main__':
    main()
