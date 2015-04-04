from __future__ import absolute_import, division, print_function

import flask as fl

from . import filters

app = fl.Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
app.debug = True

@app.route('/')
def root():
    return fl.render_template('root.html')

@app.route('/pots/json', methods=['GET', 'POST'])
def pots_processor_json():
    if fl.request.method == 'POST':
        data = fl.request.get_json(cache=False)
        try:
            data = filters.pots(data)
            reply = {'data': data.tolist(), 'rate': 44100}
            status_code = 200

        except ValueError as e:
            reply = {'error': str(e)}
            status_code = 400

        resp = fl.jsonify(**reply)
        resp.status_code = status_code
        return resp

    else:
        return fl.redirect('/pots')

@app.route('/pots', methods=['GET', 'POST'])
def pots_processor():
    if fl.request.method == 'POST':
        file = fl.request.files['file']
        fext = file.filename.split('.')[-1]

        try:
            data = aio.load(file, ext=fext)
        except ValueError as e:
            return str(e), 400

        data = filters.pots(data)
        buf, mimetype = aio.dump(data, ext=fext)

        parts = file.filename.split('.')
        parts.insert(-1, 'pots-filtered')
        newname = '.'.join(parts)
        return fl.send_file(
                buf, mimetype=mimetype,
                as_attachment=True, attachment_filename=newname)

    else:
        return fl.render_template('pots.html')

if __name__ == '__main__':
    app.run()
