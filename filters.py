from __future__ import absolute_import, division, print_function

import json

import numpy as np
import scipy.signal as sig

MAXINT16 = 2**15 - 1

with open('biquads.json', 'r') as f:
    biquads = json.load(f)

def normalize(data, maxamp=1):
    data *= maxamp / max(abs(data))

def pots(data, snr=30):
    data = np.array(data)

    # ensure mono
    if data.ndim != 1:
        data = data[:,0]

    # convert to float, but simulate 16-bit quantization if needed
    orig_dtype = data.dtype
    data = data.astype('float')
    if orig_dtype != 'int16':
        normalize(data, maxamp=MAXINT16)
        np.around(data, out=data)
    normalize(data)

    # do filtering
    for b, a in biquads['signal']:
        data = sig.lfilter(b, a, data)

    # add band-limited noise (filtered white noise)
    np.random.seed(0)
    noise = 10**(-snr/20) * ((np.random.random(size=data.shape) * 2) - 1)
    for b, a in biquads['noiseband']:
        noise = sig.lfilter(b, a, noise)
    data += noise

    # renormalize and convert to 16-bit integers
    normalize(data, maxamp=MAXINT16)
    data = data.astype('int16')

    return data
