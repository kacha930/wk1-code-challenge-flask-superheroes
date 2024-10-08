#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

# Set up the database URI
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

# Initialize Flask app and configurations
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize extensions
migrate = Migrate(app, db)
db.init_app(app)

# Set up Flask-RESTful API
api = Api(app)

@app.route('/')
def index():
    return '<h1>Code challenge week 1</h1>'

# Route: GET /heroes
@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    return jsonify([hero.to_dict(only=('id', 'name', 'super_name')) for hero in heroes])

# Route: GET /heroes/:id
@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero(id):
    hero = Hero.query.get(id)
    if hero:
        hero_data = hero.to_dict(only=('id', 'name', 'super_name'))
        hero_powers = [
            {
                "hero_id": hp.hero_id,
                "id": hp.id,
                "power": hp.power.to_dict(only=('id', 'name', 'description')),
                "power_id": hp.power_id,
                "strength": hp.strength
            }
            for hp in hero.hero_powers
        ]
        hero_data['hero_powers'] = hero_powers
        return jsonify(hero_data)
    else:
        return jsonify({"error": "Hero not found"}), 404

# Route: GET /powers
@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    return jsonify([power.to_dict(only=('id', 'name', 'description')) for power in powers])

# Route: GET /powers/:id
@app.route('/powers/<int:id>', methods=['GET'])
def get_power(id):
    power = Power.query.get(id)
    if power:
        return jsonify(power.to_dict(only=('id', 'name', 'description')))
    else:
        return jsonify({"error": "Power not found"}), 404

# Route: PATCH /powers/:id
@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = Power.query.get(id)
    if power:
        data = request.get_json()
        description = data.get('description')

        if description:
            try:
                power.description = description
                db.session.commit()
                return jsonify(power.to_dict(only=('id', 'name', 'description')))
            except Exception as e:
                db.session.rollback()
                return jsonify({"errors": [str(e)]}), 400
        else:
            return jsonify({"errors": ["Validation errors"]}), 400
    else:
        return jsonify({"error": "Power not found"}), 404

# Route: POST /hero_powers
@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()
    
    strength = data.get('strength')
    power_id = data.get('power_id')
    hero_id = data.get('hero_id')

    try:
        new_hero_power = HeroPower(strength=strength, power_id=power_id, hero_id=hero_id)
        db.session.add(new_hero_power)
        db.session.commit()

        response_data = {
            "id": new_hero_power.id,
            "hero_id": new_hero_power.hero_id,
            "power_id": new_hero_power.power_id,
            "strength": new_hero_power.strength,
            "hero": {
                "id": new_hero_power.hero.id,
                "name": new_hero_power.hero.name,
                "super_name": new_hero_power.hero.super_name
            },
            "power": {
                "id": new_hero_power.power.id,
                "name": new_hero_power.power.name,
                "description": new_hero_power.power.description
            }
        }
        
        return jsonify(response_data), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"errors": [str(e)]}), 400

if __name__ == '__main__':
    app.run(port=5555, debug=True)