from flask import Flask, render_template, request, send_file, url_for
import pandas as pd
import random
import uuid
import os
import threading
import time
from datetime import datetime

app = Flask(__name__)
TEMP_FOLDER = "temp"
os.makedirs(TEMP_FOLDER, exist_ok=True)

def delete_after_delay(filepath, delay):
    time.sleep(delay)
    if os.path.exists(filepath):
        os.remove(filepath)

@app.route('/')
def index():
    return render_template("index.html", year=datetime.now().year)

@app.route('/result', methods=['POST'])
def result():
    sets = int(request.form['sets'])
    exponent = int(request.form['exponent'])
    rolls_per_set = 6 ** exponent
    averages = []

    start = time.time()
    for _ in range(sets):
        rolls = [random.randint(1, 6) for _ in range(rolls_per_set)]
        avg = sum(rolls) / rolls_per_set
        averages.append(avg)
    end = time.time()

    overall_avg = sum(averages) / len(averages)
    duration = round(end - start, 3)
    total_rolls = sets * rolls_per_set
    speed = round(total_rolls / (end - start), 3)

    file_id = uuid.uuid4().hex
    filename = f"dice_{file_id}.xlsx"
    filepath = os.path.join(TEMP_FOLDER, filename)

    df = pd.DataFrame({
        "Set": list(range(1, sets + 1)),
        "Average": averages
    })
    df.to_excel(filepath, index=False)

    threading.Thread(target=delete_after_delay, args=(filepath, 120)).start()

    return render_template("result.html",
        sets=sets,
        average=round(overall_avg, 15),
        total_rolls=total_rolls,
        duration=round(duration, 3),
        speed=round(speed, 3),
        filename=filename,
        year=datetime.now().year
    )

@app.route('/download/<filename>')
def download_file(filename):
    filepath = os.path.join(TEMP_FOLDER, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return render_template("expired.html", year=datetime.now().year)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
