import uuid
from datetime import datetime
from flask import Flask, request, jsonify
from flask_restx import Resource, Api, fields, Namespace
from marshmallow import Schema, fields as ma_fields, ValidationError

app = Flask(__name__)
api = Api(app, version='1.0', title='Animals API', description='Simple Animals API')

ns = Namespace('animals', description='Animals operations')

# Define the model for API documentation
animal_model = ns.model('Animal', {
    'id': fields.String(readonly=True, description='The animal unique identifier', example='123e4567-e89b-12d3-a456-426614174000'),
    'name': fields.String(required=True, description='The animal name', example='Lion'),
    'description': fields.String(required=True, description='The animal description', example='The king of animals'),
    'animalClassification': fields.String(required=True, description='The animal animalClassification', example='Feline'),
    'imageUrl': fields.String(readonly=True, description='the animal image', example='https://images.stockcake.com/public/d/c/0/dc00120b-2150-4708-8718-e461e0686de1_large/neon-alley-cat-stockcake.jpg'),
    'timestamp': fields.String(readonly=True, description='The time the animal was added', example='2025-03-12T13:30:00')
})

animals = []

@ns.route('/')
class AnimalList(Resource):
    @ns.doc('list_animals')
    @ns.marshal_list_with(animal_model)
    def get(self):
        return animals

    @ns.doc('create_animal')
    @ns.expect(animal_model, validate=True)
    @ns.marshal_with(animal_model, code=201)
    def post(self):
        try:
            new_animal = animal_schema.load(request.json)
            if not self.__check_existing_animal_name(animals, new_animal['name']):
                new_animal['id'] = str(uuid.uuid4())
                new_animal['timestamp'] = datetime.now().isoformat()
                new_animal['imageUrl'] = 'https://www.funny-emoticons.com/files/funny-animals/hybrid-animals/664-puggit.png'
                animals.append(new_animal)
                return new_animal, 201
            else:
                ns.abort(409, f"Animal with name '{new_animal['name']}' already exists.")

        except ValidationError as err:
            return jsonify(err.messages), 400

    def __check_existing_animal_name(self, animal_list, animal_name):
        for animal in animal_list:
            if animal['name'].lower() == animal_name.lower():
                return True
        return False

api.add_namespace(ns)

class AnimalSchema(Schema):
    name = ma_fields.Str(required=True)
    description = ma_fields.Str(required=True)
    animalClassification = ma_fields.Str(required=True)

animal_schema = AnimalSchema()

if __name__ == '__main__':
    app.run(debug=True)
