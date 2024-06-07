# importing library and models to interact with Resources from FHIR Servers
from fhirclient import client
import fhirclient.models.patient as p
import fhirclient.models.evidence as e
import fhirclient.models.observation as o

# Connecting to Test FHIR Server at https://hapi.fhir.org/baseR4
settings = {
    'app_id': 'FHIR_Application',
    'api_base': 'https://hapi.fhir.org/baseR4'
}

# object for communication with FHIR Server
smart = client.FHIRClient(settings=settings)

#import library for Web-Application Development
from flask import Flask
from flask import render_template

# Initialise the "app" object of class "Flask"
app = Flask(__name__)

# route to the subpage "http://127.0.0.1:8080/index.html" of the web-application
@app.route("/index.html")
def index():
    return "This is an index page"

# route to the subpage "http://127.0.0.1:8080/ris.html" of the web-application
@app.route("/update_patient.html")
def updatePatient():
    return "<b>The patient was updated</b>"


# route to the subpage "http://127.0.0.1:8080/patient.html" of the web-application
@app.route("/patient.html")
def patient():
    patient = p.Patient.read('593210', smart.server)
    birthday = patient.birthDate.isostring
    name = smart.human_name(patient.name[0])
    return  render_template('patient.html',name = name,birthday=birthday)

# start the web-application
if '__main__' == __name__:
    app.run(debug=True, port=8000)