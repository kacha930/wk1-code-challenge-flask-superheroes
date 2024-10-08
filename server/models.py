from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

# Defining naming convention for foreign keys 

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    super_name = db.Column(db.String, nullable=False)


    # add relationship
    # > relationship to HeroPower
    hero_powers = db.relationship('HeroPower', backref='hero', lazy=True, cascade='all, delete-orphan')

    # > Association proxy to get powers directly from Hero 
    powers = association_proxy('hero_powers', 'power')


    # add serialization rules
    serialize_rules = ('-hero_powers.hero',)

    def __repr__(self):
        return f'<Hero {self.id}: {self.name} ({self.super_name})>'
    



class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)


    # add relationship
    # > relationship to HeroPower

    hero_powers = db.relationship('HeroPower', backref='power', lazy=True, cascade='all, delete-orphan')

    # add serialization rules
    serialize_rules = ('-hero_powers.power',)

    # add validation
    @validates('name')
    def validate_name(self, key, name):
        if not name:
            raise ValueError("Name cannot be empty.")
        return name
    

    @validates('description')
    def validate_description(self, key, description):
        if not description:
            raise ValueError("Description must be present.")
        if len(description) < 20:
            raise ValueError("Description must be at least 20 characters long.")
        return description
    

    def __repr__(self):
        return f'<Power {self.id}: {self.name}>'


class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)

    # Relationships to Hero and Power
    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id', ondelete='CASCADE'), nullable=False)
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id', ondelete='CASCADE'), nullable=False)

    # Serialization rules
    serialize_rules = ('-hero.hero_powers', '-power.hero_powers')

    # Validation for strength field
    @validates('strength')
    def validate_strength(self, key, strength):
        valid_strengths = ['strong', 'weak', 'average']
        if strength not in valid_strengths:
            raise ValueError(f"Strength must be one of the following values: {valid_strengths}.")  
        return strength

 

    def __repr__(self):
        return f'<HeroPower {self.id}: Strength {self.strength}>'
    

    
