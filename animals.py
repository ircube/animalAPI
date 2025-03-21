import os
from urllib.parse import urlparse
import uuid
from datetime import datetime
from flask import Flask, request, send_from_directory
from flask_restx import Resource, Api, fields, Namespace
from werkzeug.utils import secure_filename
from marshmallow import Schema, fields as ma_fields
import redis
from dotenv import load_dotenv

load_dotenv()

redis_url = urlparse(os.environ.get("REDIS_URL"))

redis_client = redis.Redis(
    host=redis_url.hostname, 
    port=redis_url.port,
    password=redis_url.password,
    decode_responses=True,
    ssl=(redis_url.scheme == "rediss"), 
    ssl_cert_reqs=None
)

app = Flask(__name__)
api = Api(app, version='1.0', title='Animals API', description='Simple Animals API')


app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


ns = Namespace('animals', description='Animals operations')

# Define the model for API documentation
animal_model = ns.model('Animal', {
    'id': fields.String(readonly=True, description='The animal unique identifier', example='123e4567-e89b-12d3-a456-426614174000'),
    'name': fields.String(required=True, description='The animal name', example='Lion'),
    'description': fields.String(required=True, description='The animal description', example='The king of animals'),
    'animalClassification': fields.String(required=True, description='The animal classification', example='Feline'),
    'imageUrl': fields.String(readonly=True, description='The animal image URL', example='uploads/neon-alley-cat.png'),
    'timestamp': fields.String(readonly=True, description='The time the animal was added', example='2025-03-12T13:30:00')
})

# model for multipart/form-data
upload_parser = ns.parser()
upload_parser.add_argument('name', type=str, location='form', required=True, help='The animal name')
upload_parser.add_argument('description', type=str, location='form', required=True, help='The animal description')
upload_parser.add_argument('animalClassification', type=str, location='form', required=True, help='The animal classification')
upload_parser.add_argument('imageUrl', type='file', location='files', required=False, help='The animal image')

@ns.route('/')
class AnimalList(Resource):
    @ns.doc('list_animals')
    @ns.marshal_list_with(animal_model)
    def get(self):
        return self.__getAnimals()

    @ns.doc('create_animal')
    @ns.expect(upload_parser)  # Use the parser here
    @ns.marshal_with(animal_model, code=201)
    def post(self):
        name = request.form.get('name')
        description = request.form.get('description')
        animal_classification = request.form.get('animalClassification')
        file = request.files.get('imageUrl')

        imageUrl = f"{request.host_url}{'uploads/'}default.png";
        imageNewName = '';
        if file and allowed_file(file.filename):
            _, file_extension = os.path.splitext(secure_filename(file.filename));
            imageNewName = f"{str(uuid.uuid4())}{file_extension}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], imageNewName)
            file.save(file_path)
            imageUrl = f"{request.host_url}{'uploads/'}{imageNewName}"

        new_animal = animal_schema.load({
            "name": name,
            "description": description,
            "animalClassification": animal_classification,
            "imageUrl": imageUrl,
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat()
        })

        if self.__check_existing_animal_name( self.__getAnimals(), name):
            ns.abort(409, f"'{new_animal['name']}' already exists.")
        else :
            redis_client.hmset(f"animal:{new_animal['id']}", new_animal)
            return new_animal, 200

    def __getAnimals(self):
        all_animals = []
        for key in redis_client.keys('animal:*'):
            animal_data = redis_client.hgetall(key)
            all_animals.append(animal_data)
        all_animals.sort(key=lambda x: x['timestamp'], reverse=True)
        return all_animals

    def __check_existing_animal_name(self, animal_list, animal_name):
        for animal in animal_list:
            if animal['name'].lower() == animal_name.lower():
                return True
        return False

    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

api.add_namespace(ns)

class AnimalSchema(Schema):
    id = ma_fields.Str(required=False)
    name = ma_fields.Str(required=True)
    description = ma_fields.Str(required=True)
    animalClassification = ma_fields.Str(required=True)
    imageUrl = ma_fields.Str(required=False)
    timestamp = ma_fields.Str(required=False)

animal_schema = AnimalSchema()

if __name__ == '__main__':
    if os.environ.get("FLASK_ENV")=="DEV":
        app.run(host='0.0.0.0', port=5000, debug=True)
    else :
        app.run(debug=False)
