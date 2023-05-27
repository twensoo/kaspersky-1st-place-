#!/usr/bin/env python

import os
from flask import Flask, make_response, send_file, request, jsonify
from werkzeug.utils import secure_filename
from hashlib import sha256

host_name = "0.0.0.0"
port = os.getenv("FILE_SERVER_PORT", default=5001)

UPLOAD_FOLDER = 'data'
ALLOWED_EXTENSIONS = {'py', 'json'}
CWD = os.path.dirname(__file__)
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_digest(file_name):
    BUF_SIZE = 65536
    digest = sha256()

    with open(file_name, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            digest.update(data)

    return digest.hexdigest()


@app.route('/get-digest/<path:filename>')
def get_digest(filename):
    error_message = f"malformed request {request.data}"
    try:
        update_pathname = os.path.join(CWD, app.config['UPLOAD_FOLDER'], secure_filename(filename) + '.json')
        digest = {
            'digest_alg': 'sha256',
            'digest': generate_digest(update_pathname)
        }
        
        return jsonify(digest)
    except:
        return error_message, 404
    # print("[info] requested digest")
    # update_archive_pathname = os.path.join(
    #     CWD, app.config['UPLOAD_FOLDER'], filename)
    # print("[info]", update_archive_pathname)
    # update_source_pathname = os.path.join(
    #     CWD, app.config['UPLOAD_FOLDER'], f"{filename}.py")
    # arcname = 'app.py'
    # try:
    #     # repack the source file for simplicity
    #     update_file = zipfile.ZipFile(
    #         update_archive_pathname, 'w', compression=zipfile.ZIP_DEFLATED)
    #     update_file.write(update_source_pathname,
    #                       arcname=arcname, compresslevel=1)
    #     update_file.close()

    #     digest = generate_digest(update_archive_pathname)
    #     return f"{digest} sha256 {filename}"
    # except FileNotFoundError as e:
    #     print("[error]", e, os.getcwd())
    #     abort(404)


@app.route('/download-update/<path:filename>')
def get_update(filename):
    error_message = f"malformed request {request.data}"
    try:
        update_pathname = os.path.join(CWD, app.config['UPLOAD_FOLDER'], secure_filename(filename) + '.json')
        response = make_response(
            send_file(
                path_or_file=update_pathname,
                mimetype='application/json',
                as_attachment=True,
                download_name=secure_filename(filename)
            )
        )
        response.headers['digest'] = generate_digest(update_pathname)
        response.headers['digest_alg'] = 'sha256'

        return response
    except:
        return error_message, 404
    # update_archive_pathname = os.path.join(
    #     CWD, app.config['UPLOAD_FOLDER'], f"{filename}.zip")
    # update_source_pathname = os.path.join(
    #     CWD, app.config['UPLOAD_FOLDER'], f"{filename}.py")
    # arcname = secure_filename(filename)

    # try:
    #     os.remove(update_archive_pathname)
    # except:
    #     pass

    # try:
    #     update_file = zipfile.ZipFile(
    #         update_archive_pathname, 'w', compression=zipfile.ZIP_DEFLATED)
    #     update_file.write(update_source_pathname,
    #                       arcname=arcname, compresslevel=1)
    #     update_file.close()

    #     response = make_response(
    #         send_file(
    #             path_or_file=update_archive_pathname,
    #             mimetype='zip',
    #             as_attachment=True,
    #             download_name=filename
    #         )
    #     )
    #     response.headers['digest'] = generate_digest(update_archive_pathname)
    #     response.headers['digest_alg'] = 'sha256'

    #     return response
    # except FileNotFoundError as e:
    #     print("[error]", e, os.getcwd())
    #     abort(404)


@app.route('/upload-update', methods=['POST'])
def upload_update():
    try:
        if 'file' not in request.files:
            error = "No file part"
            return jsonify({'error': error}), 400
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            error = "No file"
            return jsonify({'error': error}), 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            # remove existing file
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            except:
                pass

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return jsonify({'filename': filename}), 200
    except:
        return jsonify({'error': 'malformed request'}), 400


if __name__ == "__main__":        # on running python app.py
    app.run(port=port, host=host_name)
