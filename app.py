
#!/usr/bin/env python

from flask import Flask, render_template, url_for, send_from_directory
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
import schedule
import time
import shutil

app = Flask(__name__)

# === Scheduler === #
executor = ThreadPoolExecutor()

def take_picture():
     print("Firing up camera...")

     # timestamp = time.ctime()
     timestamp = time.time()
     cmd = "raspistill -o /home/pi/timelapseIOT/static/captures/" + timestamp + ".jpeg"
     subprocess.call(cmd, shell=True)

     print("Snapped: " + timestamp)
     return

def start_interval():
     schedule.every().minute.do(take_picture)
     # schedule.every().hour.do(take_picture)

     while True:
          schedule.run_pending()
          time.sleep(1)

# Initiate scheduled task in a new thread that runs in background
executor.submit(start_interval)


# === App Functionality === #
PIC_DIR = './static/captures'

# Show all captured images
@app.route('/')
def display_all():
     image_list = os.listdir(PIC_DIR)

     return render_template('library.html', img_list=image_list)

# Download image
@app.route('/download/<string:filename>')
def download(filename):
     print("Image downloaded.")
     return send_from_directory(PIC_DIR, filename)


# Download all images
@app.route('/download/all')
def download_all():
     # Get oldest and latest image dates
     img_list = os.listdir(PIC_DIR)

     if not img_list:
          print("No images to download")
          return
     else:
          latest = img_list[1]
          oldest = img_list[-1]

     # Zip all the images
     zipFileName = oldest + " - " + latest
     destination = './archives'

     shutil.make_archive(zipFileName, 'zip', PIC_DIR)

     # Store zip file in archives directory
     zipFile = zipFileName + '.zip'
     shutil.move(zipFile, destination)

     # Delete all zipped images
     # @TODO:

     # Send zipped file to client
     return send_from_directory(destination, zipFile)

# Delete all
# @TODO: Probably dont need route for this. Only want to delete all if all were downloaded

# Delete Archives
# @TODO: Purge archives

# Run app on port 80
if __name__ == '__main__':
     app.run(port='80')