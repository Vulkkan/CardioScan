from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import pandas as pd
import os
from helper import preprocessor, individualHelper, batchHelper
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/select-profile')
def select_profile():
    """Profile selection page"""
    return render_template('select_profile.html')

@app.route('/configuration', methods=['GET', 'POST'])
def configuration():
    """Configuration page for model and prediction type selection"""
    if request.method == 'POST':
        model_type = request.form.get('model_type', 'Random Forest')
        prediction_type = request.form.get('prediction_type', 'Single Patient')
        
        session['model_type'] = model_type
        session['prediction_type'] = prediction_type
        
        if prediction_type == 'Single Patient':
            return redirect(url_for('prediction'))
        else:
            return redirect(url_for('batch_prediction'))
    
    model_type = session.get('model_type', 'Random Forest')
    prediction_type = session.get('prediction_type', 'Single Patient')
    
    return render_template('configuration.html', 
                         model_type=model_type, 
                         prediction_type=prediction_type)

@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    """Single patient prediction page"""
    result = None
    patient = None
    
    if request.method == 'POST':
        patient = request.form.get('name', 'Unknown')
        
        data = pd.DataFrame({
            'age': [int(request.form.get('age', 0))],
            'sex': [1 if request.form.get('sex') == 'Male' else 0],
            'cp': [int(request.form.get('cp', 0))],
            'trestbps': [int(request.form.get('trestbps', 0))],
            'chol': [int(request.form.get('chol', 0))],
            'fbs': [int(request.form.get('fbs', 0))],
            'restecg': [int(request.form.get('restecg', 0))],
            'thalach': [int(request.form.get('thalach', 0))],
            'exang': [int(request.form.get('exang', 0))],
            'oldpeak': [float(request.form.get('oldpeak', 0))],
            'slope': [int(request.form.get('slope', 0))],
            'ca': [int(request.form.get('ca', 0))],
            'thal': [int(request.form.get('thal', 0))]
        })
        
        result = individualHelper.submitAndPredict(patient, data)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if result:
                return jsonify({
                    'success': True,
                    'patient': result[0],
                    'outcome': result[1],
                    'risk': result[2],
                    'health': result[3],
                    'insights': result[4]
                })
            return jsonify({'success': False, 'error': 'Prediction failed'})
    
    return render_template('prediction.html', 
                         result=result, 
                         patient=patient,
                         model_type=session.get('model_type', 'Random Forest'))

@app.route('/batch-prediction', methods=['GET', 'POST'])
def batch_prediction():
    """Batch prediction page"""
    results = None
    batch_data = None
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and file.filename.endswith('.csv'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                batch_data = pd.read_csv(filepath)
                results = batchHelper.submitAndPredictBatch(batch_data)
                
                # Clean up uploaded file
                os.remove(filepath)
                
            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Please upload a CSV file', 'error')
            return redirect(request.url)
    
    return render_template('batch_prediction.html', 
                         results=results, 
                         batch_data=batch_data)

@app.route('/data-creation', methods=['GET', 'POST'])
def data_creation():
    """Data creation page"""
    if request.method == 'POST':
        try:
            input_data = pd.DataFrame({
                'Name': [request.form.get('name', '')],
                'age': [int(request.form.get('age', 0))],
                'sex': [1 if request.form.get('sex') == 'Male' else 0],
                'cp': [int(request.form.get('cp', 0))],
                'trestbps': [int(request.form.get('trestbps', 0))],
                'chol': [int(request.form.get('chol', 0))],
                'fbs': [int(request.form.get('fbs', 0))],
                'restecg': [int(request.form.get('restecg', 0))],
                'thalach': [int(request.form.get('thalach', 0))],
                'exang': [int(request.form.get('exang', 0))],
                'oldpeak': [float(request.form.get('oldpeak', 0))],
                'slope': [int(request.form.get('slope', 0))],
                'ca': [int(request.form.get('ca', 0))],
                'thal': [int(request.form.get('thal', 0))]
            })
            
            csv_path = 'input-data/heart.csv'
            os.makedirs('input-data', exist_ok=True)
            
            if os.path.exists(csv_path):
                existing_data = pd.read_csv(csv_path)
                existing_data = pd.concat([existing_data, input_data], axis=0).reset_index(drop=True)
                existing_data.to_csv(csv_path, index=False)
            else:
                input_data.to_csv(csv_path, index=False)
            
            flash('Information has been saved successfully!', 'success')
            
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('data_creation.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
