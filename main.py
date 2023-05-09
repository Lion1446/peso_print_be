from flask import Flask, make_response, request
import os
from math import log2
import json
from time import sleep
from pdf2image import convert_from_path
import io
import base64
from models import *
from functions import *
import shutil
from flask_sock import Sock                            ## pip3 install flask-sock


## ======================= GLOBALS =================================

flash_drive_path = 'E:'  # Replace 'E:' with the drive letter of your flash drive
basedir = os.path.abspath(os.path.dirname(__file__))
destination_path = f"{basedir}\\Uploads"

queue_number = 1
queue_char = 'A'



## ======================= STARTUPS ================================

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
sock = Sock(app)    
    
with app.app_context():
    db.create_all()  

## ======================= ENDPOINTS ===============================

@app.route('/')
def index():
    return "Hello World"

@app.route('/create_tables')
def create_tables():
    resp = make_response({"status": 200, "result": "Created Tables"})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route('/get_flash_drive_structure', methods=['GET'])
def get_flash_drive_structure():
    # Check if the flash drive path exists
    if os.path.exists(flash_drive_path):
        # Get the file system structure of the flash drive
        flash_drive_structure = get_directory_structure(flash_drive_path)
        # Convert the file system structure to JSON
        resp = make_response(flash_drive_structure)
    else:
        # resp = make_response({"result": f"Flash drive not found at path: {flash_drive_path}", "status": 404})
        resp = make_response(flash_drive_structure)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    sleep(1)
    return resp

@app.route('/upload_file_from_drive', methods=['POST'])
def upload_file_from_drive():
    global queue_number, queue_char
    request_data = request.data
    request_data = json.loads(request_data.decode('utf-8')) 

    absolute_file_path = rf"{flash_drive_path}{request_data['file_path']}".replace('/', '\\')
    poppler_path = r"D:\\Lion\\Non-School-Stuffs\\Downloads\\poppler-23.01.0\\Library\bin"
    images = convert_from_path(absolute_file_path, poppler_path=poppler_path)
    
    stream_images = []
    for image in images:
        stream = io.BytesIO()
        image.save(stream, format="PNG")
        stream_image = stream.getvalue()
        base64_image = base64.b64encode(stream_image).decode('utf8')
        stream_images.append(base64_image)
    
    

    resp = make_response({"absolute_file_path": absolute_file_path, "page_count": len(images), "pages": stream_images})

    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route('/create_print_job_flashdrive', methods=['POST'])
def create_print_job():
    global queue_char, queue_number, destination_path
    request_data = request.data
    request_data = json.loads(request_data.decode('utf-8'))
    formatted_num = '{:02d}'.format(queue_number)
    queue_code =  f"{queue_char}{formatted_num}"
    if queue_number < 100:
        queue_number = queue_number + 1
    else:
        queue_number = 1
        queue_char = chr(ord(queue_char) + 1)


    pjs = len(PrintJob.query.all())
    filename = request_data["absolute_file_path"].split("\\")[-1]
    filename = f"{pjs+1}(separator)" + filename
    os.makedirs(os.path.dirname(f"{destination_path}\\{filename}"), exist_ok=True)
    shutil.copy(request_data["absolute_file_path"], f"{destination_path}\\{filename}")
    print_job = PrintJob(
        queue_code = queue_code,
        absolute_file_path = filename,
        amount_payable = request_data["amount_payable"],
        copies = request_data["copies"],
        is_colored = request_data["is_colored"],
        pages_to_print = request_data["pages_to_print"],
        paper_size = request_data["paper_size"]
    )
    
    db.session.add(print_job)
    db.session.commit()
    
    resp = make_response({"status": 200, "result": "Print job created", "queue_code": queue_code})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

## wscat -c ws://127.0.0.1:5000/print_job_stream
@sock.route("/print_job_stream")
def print_job_stream(ws):
    while True:
        print_jobs = PrintJob.query.filter_by(datetime_deleted=None).order_by(PrintJob.datetime_created.asc()).all()
        job_data = []
        for job in print_jobs:
            job_data.append(job.to_map())
        data = json.dumps({"print_jobs": job_data})
        ws.send(data)

## ======================= ENDPOINTS ===============================


if __name__ == '__main__':
    app.run(debug=True)





