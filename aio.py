from __future__ import absolute_import, division, print_function
import io

import numpy as np
import scipy.io.wavfile as sciwav

FS = 44100

def _load_wave(f):
    rate, data = sciwav.read(f.stream)
    return data

def _load_text(f):
    data = np.loadtxt(f.stream, dtype='int16')
    return data

def _dump_wave(data):
    buf = io.BytesIO()
    sciwav.write(buf, FS, data)
    buf.seek(0)
    return buf, 'audio/vnd.wave'

def _dump_text(data):
    buf = io.BytesIO()
    np.savetxt(buf, data, fmt='%d')
    buf.seek(0)
    return buf, 'text/plain'

def load(f, ext):
    try:
        return DP[ext]['load'](f)
    except KeyError:
        raise ValueError('Unsupported file format')

def dump(data, ext):
    try:
        return DP[ext]['dump'](data)
    except KeyError:
        raise ValueError('Unsupported file format')

DP = {
    'wav': {'load': _load_wave, 'dump': _dump_wave},
    'txt': {'load': _load_text, 'dump': _dump_text},
}
