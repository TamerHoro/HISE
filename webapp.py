from flask import Flask, request, render_template
import requests
from datetime import datetime
from fhirclient import client
import fhirclient.models.patient as p
import fhirclient.models.evidence as e
import fhirclient.models.observation as o
from fhirclient.models.humanname import HumanName
from fhirclient.models.contactpoint import ContactPoint
from fhirclient.models.address import Address

app = Flask(__name__)

# Base URL for the HAPI FHIR server

settings = {
    'app_id': 'FHIR_Application',
    'api_base': 'https://hapi.fhir.org/baseR4'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submissionSuccess', methods=['POST'])
def submitSucess():
    # Extract form data
    form_data = request.form
    
    #Create FHIR Patient resource
    patient = p.Patient()
   
    
    # Set the patient's name
    name = HumanName()
    name.family = 'Doe'
    name.given = ['John']
    patient.name = [name]

    # Set the patient's gender
    patient.gender = 'male'

    # Set the patient's birth date
    patient.birthDate = '1990-01-01'

    # Set the patient's contact information
    contact =  ContactPoint()
    contact.system = 'phone'
    contact.value = '555-555-5555'
    contact.use = 'mobile'
    patient.telecom = [contact]

    # Set the patient's address
    address = Address()
    address.line = ['123 Main St']
    address.city = 'Somewhere'
    address.state = 'CA'
    address.postalCode = '12345'
    patient.address = [address]
    
    # Save the patient resource to the FHIR server
    patient.create(base_url)
    
    
    return render_template('submissionSuccess.html')

@app.route('/intakeform')
def intakeform():
    return render_template('intakeform.html')

@app.route('/sheduleAppointment')
def patient():
    return render_template('/sheduleAppointment.html')

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
