from __future__ import absolute_import, division, print_function

import json
import os.path as op

import six
import numpy as np
import scipy.signal as sig
import scipy.io.wavfile as sciwav

MAXINT16 = 2**15 - 1
FS = 44100
COEFF_DIR = op.join(op.dirname(op.abspath(__file__)), 'coeffs')

def normalize(data, maxamp=1):
    data *= maxamp / max(abs(data))

def load_coeffs(fname):
    with open(op.join(COEFF_DIR, fname)) as f:
        return json.load(f)

POTS_COEFFS = load_coeffs('pots.json')

def pots(data, snr=30, seed=None):
    if seed is not None:
        np.random.seed(seed)

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

    # pad start and end
    #leader_len = np.random.randint(0.1 * FS, 0.4 * FS)
    #trailer_len = 0.5 * FS - leader_len
    #data = np.concatenate([np.zeros(leader_len), data, np.zeros(trailer_len)])

    # do filtering
    for b, a in POTS_COEFFS['signal']:
        data = sig.lfilter(b, a, data)

    # add band-limited noise (filtered white noise)
    #np.random.seed(0)
    noise = 10**(-snr/20) * ((np.random.random(size=data.shape) * 2) - 1)
    for b, a in POTS_COEFFS['noiseband']:
        noise = sig.lfilter(b, a, noise)
    data += noise

    # renormalize and convert to 16-bit integers
    normalize(data, maxamp=MAXINT16)
    data = data.astype('int16')

    return data


class DigitalStreamFilter(object):
    mimes = {
        'wav': 'audio/vnd.wave',
        'txt': 'text/plain',
        'json': 'application/json',
    }
    output_suffix = 'filtered'

    def __init__(self, data=None, stream=None, filename=None, dtype=None):
        if dtype is None and filename is None:
            try:
                # werkzeug.FileStorage has 'filename', python files have 'name'
                filename = getattr(stream, 'filename', getattr(stream, 'name'))
            except AttributeError:
                raise ValueError("Can't determine type from stream. "
                        "Provide dtype or filename to infer type.")

        if dtype is None:
            dtype = filename.split('.')[-1]

        self.dtype = dtype
        self.filename = filename
        self.json_extra = {}

        if data is not None:
            self.data = np.array(data)
        elif stream is not None:
            self.load(stream)
        else:
            with open(filename, 'rb') as stream:
                self.load(stream)

    def load(self, stream):
        dispatcher = {
            'wav': self._load_wave,
            'txt': self._load_text,
            'json': self._load_json,
        }
        try:
            data = dispatcher[self.dtype](stream)
        except KeyError:
            raise TypeError('Unsupported input type: {} (accepts {})'.format(
                            self.dtype, ', '.join(dispatcher.keys())))

        self.data = np.array(data)

    def process(self, *args, **kwargs):
        raise NotImplementedError('abstract method')

    def dump(self, stream, dtype=None):
        if dtype is None:
            dtype = self.dtype

        {'wav': self._dump_wave,
         'txt': self._dump_text,
         'json': self._dump_json,
        }[dtype](stream)

    def suggested_name(self):
        parts = self.filename.split('.')[:-1]
        parts.extend([self.output_suffix, self.dtype])
        return '.'.join(parts)

    def mimetype(self):
        return self.mimes[self.dtype]

    def _load_wave(self, stream):
        rate, data = sciwav.read(stream)
        return data

    def _load_text(self, stream):
        return np.loadtxt(stream, dtype='int16')

    def _load_json(self, stream):
        return np.array(json.load(stream))

    def _dump_wave(self, stream):
        sciwav.write(stream, FS, self.data)

    def _dump_text(self, stream):
        np.savetxt(stream, self.data, fmt='%d')

    def _dump_json(self, stream):
        json.dump({'data': self.data.tolist(), 'rate': FS}, stream)


class POTSFilter(DigitalStreamFilter):
    output_suffix = 'pots-filtered'

    def process(self, *args, **kwargs):
        self.data = pots(self.data, *args, **kwargs)
