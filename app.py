from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    budget = request.form['budget']
    city = request.form['city']
    property_type = request.form['property_type']
    period = request.form['period']
    command = ['python', 'PredictedLocation.py', budget, city, property_type, period]
    output = subprocess.check_output(command)
    return output.decode('utf-8')

if __name__ == '__main__':
    app.run(debug=True)
