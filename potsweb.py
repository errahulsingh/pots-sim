#!/usr/bin/env python
from __future__ import absolute_import, division, print_function

import io

import flask as fl

import potsim

app = fl.Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
app.debug = True

@app.route('/')
def root():
    return fl.render_template('root.html')

@app.route('/pots/json', methods=['GET', 'POST'])
def pots_processor_json():
    if fl.request.method == 'POST':
        json_data = fl.request.get_json(cache=False)
        try:
            pfilt = potsim.POTSFilter(
                    data=json_data['data'],
                    dtype='json')
        except TypeError as e:
            return fl.jsonify({'error': str(e)}), 400

        kwa = {k: v for k, v in json_data.items() if k in ('snr', 'seed')}
        pfilt.process(**kwa)

        return fl.jsonify(data=pfilt.data.tolist(), rate=potsim.filters.FS)

    else:
        return fl.redirect('/pots')

@app.route('/pots', methods=['GET', 'POST'])
def pots_processor():
    if fl.request.method == 'POST':
        try:
            pfilt = potsim.POTSFilter(stream=fl.request.files['file'])
        except TypeError as e:
            return str(e), 400

        pfilt.process()

        sfa = {
            'filename_or_fp': io.BytesIO(),
            'attachment_filename': pfilt.suggested_name(),
            'as_attachment': True,
            'mimetype': pfilt.mimetype(),
        }
        pfilt.dump(sfa['filename_or_fp'])
        sfa['filename_or_fp'].seek(0)

        return fl.send_file(**sfa)

    else:
        return fl.render_template('pots.html')

if __name__ == '__main__':
    app.run()
