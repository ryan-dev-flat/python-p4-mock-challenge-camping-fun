#!/usr/bin/env python3

from models import *
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api=Api(app)


@app.route('/')
def home():
    return ''

class Campers(Resource):
    def get(self):
        campers_dict = [camper.to_dict(include_signups=False) for camper in Camper.query.all()]
        response = make_response(jsonify(campers_dict), 200)
        return response

    def post(self):
        data = request.get_json()
        try:
            new_camper = Camper(
                name=data.get('name'),
                age=data.get('age')
            )

            db.session.add(new_camper)
            db.session.commit()

            response_dict = new_camper.to_dict(include_signups=False)
            response = make_response(jsonify(response_dict), 201)
        except ValueError as e:
            response = make_response(jsonify({'errors': str(e)}), 400)

        return response

api.add_resource(Campers, '/campers')

class CamperByID(Resource):
    def get(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if camper:
            response_dict = camper.to_dict()
            response = make_response(jsonify(response_dict), 200)
        else:
            response = make_response(jsonify({'error':  'Camper not found'}), 404)
        return response

    def patch(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if camper:
            data = request.get_json()
            try:
                if 'name' in data:
                    camper.name = data['name']
                if 'age' in data:
                    camper.age = data['age']
                db.session.commit()
                response_dict = camper.to_dict()
                response = make_response(jsonify(response_dict), 202)
            except ValueError as e:
                response = make_response(jsonify({'errors': ['validation errors']}), 400)
        else:
            response = make_response(jsonify({'error': 'Camper not found'}), 404)
        return response

api.add_resource(CamperByID, '/campers/<int:id>')


class Activities(Resource):
    def get(self):
        activities_dict = [activity.to_dict() for activity in Activity().query.all()]
        response = make_response(jsonify(activities_dict), 200)
        return response
api.add_resource(Activities, '/activities')

class ActivityByID(Resource):
    def delete(self, id):
        activity = Activity.query.filter_by(id=id).first()
        if activity:
            db.session.delete(activity)
            db.session.commit()
            response = make_response(jsonify({'message': 'Activity deleted'}), 204)
        else:
            response = make_response(jsonify({'error': 'Activity not found'}), 404)
        return response

api.add_resource(ActivityByID, '/activities/<int:id>')


class Signups(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_signup = Signup(
                camper_id=data.get('camper_id'),
                activity_id=data.get('activity_id'),
                time=data.get('time')
            )
            db.session.add(new_signup)
            db.session.commit()
            response_dict = new_signup.to_dict()
            response = make_response(jsonify(response_dict), 201)
        except ValueError as e:
            response = make_response(jsonify({'errors': ['validation errors']}), 400)
        return response

api.add_resource(Signups, '/signups')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
