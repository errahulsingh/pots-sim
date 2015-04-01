from __future__ import absolute_import, division, print_function

import json

import numpy as np
import scipy.signal as sig

with open('biquads.json', 'r') as f:
    biquads = json.load(f)

def _validate(data):
    if data.dtype != 'int16':
        raise ValueError('wrong format')

def pots(data, snr=30):
    _validate(data)

    # normalize to abs peak of 1
    data = data.astype('float')
    data /= max(abs(data))
    for b, a in biquads['signal']:
        data = sig.lfilter(b, a, data)

    noise = 10**(-snr/20) * ((np.random.random(size=data.shape) * 2) - 1)
    for b, a in biquads['noiseband']:
        noise = sig.lfilter(b, a, noise)

    data += noise

    # renormalize and convert to 16-bit integers
    data *= (2**15 - 1) / max(abs(data))
    data = data.astype('int16')

    return data
