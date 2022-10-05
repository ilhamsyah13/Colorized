from fileinput import filename
import numpy as np 
import cv2
import os
import wget
from flask import Flask, flash, request, redirect, url_for, render_template, send_file
from werkzeug.utils import secure_filename
app = Flask(__name__, template_folder='templates')

UPLOAD_FOLDER = './static/uploads/'

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True


url = "http://eecs.berkeley.edu/~rich.zhang/projects/2016_colorization/files/demo_v2/colorization_release_v2.caffemodel"
filename = wget.download(url, out='./models')

net = cv2.dnn.readNetFromCaffe('./models/colorization_deploy_v2.prototxt','./models/colorization_release_v2.caffemodel')
pts = np.load('./models/pts_in_hull.npy')

class8 = net.getLayerId("class8_ab")
conv8 = net.getLayerId("conv8_313_rh")
pts = pts.transpose().reshape(2,313,1,1)

net.getLayer(class8).blobs = [pts.astype("float32")]
net.getLayer(conv8).blobs = [np.full([1,313],2.606,dtype='float32')]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def gambar(filename):
    extension = os.path.splitext(filename)[1]
    input = 'awal' + extension
    image = cv2.imread('./static/uploads/'+ input)
    scaled = image.astype("float32")/255.0
    lab = cv2.cvtColor(scaled,cv2.COLOR_BGR2LAB)

    resized = cv2.resize(lab,(224,224))
    L = cv2.split(resized)[0]
    L -= 50

    net.setInput(cv2.dnn.blobFromImage(L))
    ab = net.forward()[0, :, :, :].transpose((1,2,0))

    ab = cv2.resize(ab, (image.shape[1],image.shape[0]))
    L = cv2.split(lab)[0]

    colorized = np.concatenate((L[:,:,np.newaxis], ab), axis=2)
    colorized = cv2.cvtColor(colorized,cv2.COLOR_LAB2BGR)
    colorized = np.clip(colorized,0,1)
    colorized = (255 * colorized).astype("uint8")
    output = 'rubah'+ extension
    hasil = cv2.imwrite('./static/uploads/'+output, colorized)
    return hasil

@app.route('/', methods=['GET'])
def start():
    return render_template('input.html')

@app.route('/', methods=['POST'])
def input():
    if 'file' not in request.files:
        flash('Tidak Ada File')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('Tidak Ada Gambar Untuk Diunggah')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        extension = os.path.splitext(filename)[1]
        filename = 'awal'+ extension
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        gambar(filename)
        return render_template('index.html', filename=filename)
    else:
        flash('Ekstensi Gambar yang Diperbolehkan Adalah -> png, jpg, jpeg')
        return redirect(request.url)

@app.route('/display/<filename>')
def display_image(filename):
    extension = os.path.splitext(filename)[1]
    filename = 'rubah' + extension
    # return render_template('index.html',filename=filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route('/download')
def download_file():
    # extension = filename.split('.')[1]
    file_ext = str(filename)
    extension = os.path.splitext(file_ext)[1]
    download = 'rubah' + extension
    file = 'static/uploads/' +'rubah.jpg'
    return send_file(file, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
