import numpy as np
import flask as fl

import aio
import filters

app = fl.Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
app.debug = True

@app.route('/')
def root():
    return fl.render_template('root.html')

@app.route('/pots', methods=['GET', 'POST'])
def pots_process():
    if fl.request.method == 'POST':
        file = fl.request.files['file']
        fext = file.filename.split('.')[-1]

        try:
            data = aio.load(file, ext=fext)
        except ValueError as e:
            return fl.abort(415)

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
