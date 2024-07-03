from flask import Flask, request, render_template
import pandas as pd
from fuzzywuzzy import fuzz
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def upload_files():
    return render_template('upload.html')

@app.route('/match', methods=['POST'])
def match_data():
    file1 = request.files['file1']
    file2 = request.files['file2']

    filepath1 = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
    filepath2 = os.path.join(app.config['UPLOAD_FOLDER'], file2.filename)
    file1.save(filepath1)
    file2.save(filepath2)

    df1 = pd.read_csv(filepath1)
    df2 = pd.read_csv(filepath2)

    columns1 = df1.columns.tolist()
    columns2 = df2.columns.tolist()

    return render_template('match.html', columns1=columns1, columns2=columns2, file1=file1.filename, file2=file2.filename)

@app.route('/results', methods=['POST'])
def results():
    try:
        file1 = request.form['file1']
        file2 = request.form['file2']
        columns1 = request.form.getlist('columns1')
        columns2 = request.form.getlist('columns2')
        match_type = request.form['match_type']
        include_missing = 'include_missing' in request.form
        threshold = int(request.form.get('threshold', 80))

        filepath1 = os.path.join(app.config['UPLOAD_FOLDER'], file1)
        filepath2 = os.path.join(app.config['UPLOAD_FOLDER'], file2)

        df1 = pd.read_csv(filepath1)
        df2 = pd.read_csv(filepath2)

        if not include_missing:
            df1 = df1.dropna(subset=columns1)
            df2 = df2.dropna(subset=columns2)

        results = []

        if match_type == 'exact':
            merged = pd.merge(df1, df2, left_on=columns1, right_on=columns2, how='inner')
            for index, row in merged.iterrows():
                results.append({
                    'score': 100,
                    'dataset1': file1,
                    'data1': row.to_dict(),
                    'dataset2': file2,
                    'data2': row.to_dict()
                })
        else:
            for _, row1 in df1.iterrows():
                for _, row2 in df2.iterrows():
                    score = fuzz.ratio(str(row1[columns1[0]]), str(row2[columns2[0]]))
                    if score >= threshold:
                        results.append({
                            'score': score,
                            'dataset1': file1,
                            'data1': row1.to_dict(),
                            'dataset2': file2,
                            'data2': row2.to_dict()
                        })

        return render_template('results.html', results=results, columns1=columns1, columns2=columns2, file1=file1, file2=file2)

    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)












