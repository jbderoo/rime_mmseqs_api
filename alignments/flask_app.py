from flask import Flask, Request, request, jsonify, send_file, abort
from datetime import datetime
import os
import subprocess
import shutil
import string
import random
from gevent.pywsgi import WSGIServer
import pickle
import socket
from copy import deepcopy

# some variables that may need changing (except `app`, this is a necessary predefinition)
app           = Flask(__name__)
LOCK_FILE     = "/home/csnow/alignments/tmp/job.lock"
allowed_hosts = ['frost', 'hail', 'sleet', 'rime', 'yeti', 'snow-gpu', 'icestorm', 'avalanche', 'riviera']




def generate_random_string(length=10):
    """Generate a random string of letters and numbers."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def acquire_lock(retry_interval=60, timeout=259200):
    """Try to acquire the lock by creating the lock file. Waits and retries if the lock exists. Times out after 3 days"""
    waited = 0
    while os.path.exists(LOCK_FILE):
        with open('run.log', 'a') as log:
            log.write(f"Lock file exists. Waiting for {retry_interval} seconds... (waited {waited}/{timeout} seconds)\n")
        time.sleep(retry_interval)
        waited += retry_interval
        if waited >= timeout:
            with open('run.log', 'a') as log:
                log.write(f"Timeout exceeded while waiting for lock. Exiting.\n")
            raise TimeoutError("Timeout exceeded while waiting for the lock.")

    # Acquire the lock by creating the file
    with open(LOCK_FILE, 'w') as lock:
        lock.write("Lock acquired.\n")
    with open('run.log', 'a') as log:
        log.write("Lock acquired.\n")


def release_lock():
    """Release the lock by deleting the lock file."""
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
        with open('run.log', 'a') as log:
            log.write(f"Lock released.\n")


@app.route('/')
def home():
    return "Hello, this is the MMSEQS alignment server via Rime!\n"


@app.before_request
def limit_remote_addr():
    if request.path == '/run_alignment':
        with open('connect_history.log', 'a') as log:
            try:
                hostname, _, ip = socket.gethostbyaddr(request.remote_addr)
                
            except socket.herror:
                hostname, _, ip = None, None, None

            matched_host = next((allowed_host for allowed_host in allowed_hosts if allowed_host in hostname), None)

            if matched_host:
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log.write(f'[{current_time}] {matched_host} sent a request.\n')
                log.flush()
                return

            else:
                log.write(f'[{current_time}] rejecting {request.remote_addr}')
                log.flush()
                abort(403)


@app.route('/run_alignment', methods=['POST'])
def run_alignment():
    # Get the uploaded file
    fasta_file = request.files['fasta']

    if not os.path.exists('/home/csnow/alignments/tmp'):
        os.mkdir('/home/csnow/alignments/tmp')


    # Save the file temporarily
    fasta_file_path = f'/home/csnow/alignments/tmp/{fasta_file.filename}'
    fasta_file.save(fasta_file_path)

    # Rime output dir
    tmp_name   = generate_random_string()
    output_dir = os.path.join('/home/csnow/alignments/tmp', tmp_name)
    os.mkdir(output_dir)

    # Acquire the lock to ensure only one instance runs at a time
    #acquire_lock()
       # Acquire the lock to ensure only one instance runs at a time
    try:
        acquire_lock()
    except TimeoutError:
        return jsonify({'error': 'Timeout exceeded while waiting for the lock. Try again later.'}), 500

    try:
    #if 1 == 1:
        # Run the alignment script using subprocess
        cmd    = f'/home/csnow/alignments/mmseqs_alignment.sh {fasta_file_path} {output_dir}'
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    
        # Log the result stdout and stderr
        with open('run.log', 'a') as log:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log.write(f'[{current_time}] result.stdout:\n{result.stdout}\n')
            log.write(f'result.stderr:\n{result.stderr}\n')
    
        # Check if the script was successful
        if result.returncode != 0:
            app.logger.error(f"Error running mmseqs_alignment.sh: {result.stderr}")
            with open('run.log', 'a') as log:
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log.write(f"[{current_time}] Error occurred: {result.stderr}\n")
            return jsonify({'error': result.stderr}), 500
    
        # Zip the output directory
        zip_file_path = f'{output_dir}.zip'
        shutil.make_archive(output_dir, 'zip', output_dir)
    
        # Send the zip file back to the user
        response = send_file(zip_file_path, as_attachment=True)
    
        # Clean up the temporary files and directories after the file is sent
        shutil.rmtree(output_dir)   # Deletes the output directory
        os.remove(fasta_file_path)  # Deletes the temporary FASTA file
        os.remove(zip_file_path)    # Deletes the zipped file
    
        return response


    finally:
        # Release the lock when done
        release_lock()

if __name__ == '__main__':
    # Listen from ANY ip address. For additional security, to be honest, we should specify here which machines are allowed to communicate with Rime like this; frost, hail, snow-gpu, sleet, yeti, etc
    # port = Defended 2024 June 24th
    # Run the server using Gevent for concurrency
    #app.run(debug=True)
    http_server = WSGIServer(('0.0.0.0', 24624), app)
    http_server.serve_forever()
