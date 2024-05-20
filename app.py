from flask import Flask, request, render_template, jsonify
import pandas as pd
import os
from concurrent.futures import ThreadPoolExecutor
import logging
from utils.scraping import process_title
from utils.clustering import cluster_books, group_books_by_clusters

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Route definitions
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process_titles', methods=['POST'])
def process_titles():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        df = pd.read_excel(filepath, engine='openpyxl')

        max_threads = 5
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            results = list(executor.map(process_title, df['Title']))

        results = [res for res in results if res is not None]
        num_clusters = 5
        clusters = cluster_books(results, num_clusters)
        grouped_books = group_books_by_clusters(results, clusters)

        return jsonify(grouped_books), 200

if __name__ == "__main__":
    app.run(debug=True)


book_title_organizer/
│
├── app.py
├── uploads/
│   └── (uploaded files will be saved here)
├── templates/
│   ├── index.html
│   ├── results.html
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── scripts.js
├── utils/
│   ├── __init__.py
│   ├── clustering.py
│   ├── scraping.py
├── requirements.txt