from flask import Flask, request, render_template
import requests
from datetime import datetime

app = Flask(__name__)

# Base URL for the HAPI FHIR server
base_url = "https://hapi.fhir.org/baseR4"


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submissionSuccess')
def intakeform():
    return render_template('submisionSUccess.html')

@app.route('/intakeform')
def submitSucess():
    return render_template('submissionSuces.html')

@app.route('/patient')
def patient():
    return render_template('patient.html')

@app.route('/diseasesearch')
def diseasesearch():
    return render_template('diseasesearch.html')

@app.route('/search', methods=['POST'])
def search():
    disease_code = request.form['disease_code']

    # Search for Observations with the specified code
    search_url = f"{base_url}/Observation"
    params = {'code': f'http://loinc.org|{disease_code}'}
    response = requests.get(search_url, params=params)
    observations = response.json().get('entry', [])

    # Extract unique patient references from the observations
    patient_references = set()
    for entry in observations:
        observation = entry.get('resource')
        subject = observation.get('subject')
        if subject:
            patient_references.add(subject.get('reference'))

    # Fetch patient details for each unique patient reference
    patients = []
    total_age = 0
    current_year = datetime.now().year

    for ref in patient_references:
        patient_url = f"{base_url}/{ref}"
        patient_response = requests.get(patient_url)
        if patient_response.status_code == 200:
            patient = patient_response.json()
            patients.append(patient)

            # Calculate age
            birth_date = patient.get('birthDate')
            if birth_date:
                birth_year = int(birth_date.split('-')[0])
                age = current_year - birth_year
                total_age += age

    # Calculate the total number of patients and the average age
    total_patients = len(patients)
    average_age = total_age / total_patients if total_patients > 0 else 0

    return render_template('results.html', patients=patients, total_patients=total_patients, average_age=average_age)


if __name__ == '__main__':
    app.run(debug=True)
