from datetime import datetime
import os
from flask_login import UserMixin
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2.types import Geometry
from shapely.geometry import Point
from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKTElement
from geoalchemy2.functions import ST_DWithin
from geoalchemy2.types import Geography
from sqlalchemy.sql.expression import cast
from geoalchemy2.shape import from_shape
import hashlib

db = SQLAlchemy()

'''
setup_db(app):
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app):
    database_path = os.getenv('DATABASE_URL', 'DATABASE_URL_WAS_NOT_SET?!')

    # https://stackoverflow.com/questions/62688256/sqlalchemy-exc-nosuchmoduleerror-cant-load-plugin-sqlalchemy-dialectspostgre
    database_path = database_path.replace('postgres://', 'postgresql://')

    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)

'''
    drops the database tables and starts fresh
    can be used to initialize a clean database
'''
def db_drop_and_create_all():
    db.drop_all()
    db.create_all()

    # Initial sample data:
    insert_sample_locations()

def insert_sample_locations():
    # We need to start with an user to be able to relate initial locations to them
    admin_user = User(
        full_name="Administrator",
        display_name="admin",
        email="admin@dummy.mail",
        password=hashlib.md5("admin".encode()).hexdigest()
    )
    admin_user.insert()
    
    loc1 = SampleLocation(
        description='Brandenburger Tor',
        geom=SampleLocation.point_representation(
            latitude=52.516247, 
            longitude=13.377711
        ),
        learner_or_mentor='Learner'
    )
    loc1.user = admin_user
    loc1.insert()

    loc2 = SampleLocation(
        description='Schloss Charlottenburg',
        geom=SampleLocation.point_representation(
            latitude=52.520608, 
            longitude=13.295581
        ),
        learner_or_mentor='Mentor'
    )
    loc2.user = admin_user
    loc2.insert()

    loc3 = SampleLocation(
        description='Tempelhofer Feld',
        geom=SampleLocation.point_representation(
            latitude=52.473580, 
            longitude=13.405252
        ),
        learner_or_mentor='Learner'
    )
    loc3.user = admin_user
    loc3.insert()

    loc4 = SampleLocation(
        description='Alexanderplatz',
        geom=SampleLocation.point_representation(
            latitude=52.5220, 
            longitude=13.4133
        ),
        learner_or_mentor='Mentor'
    )
    loc4.user = admin_user
    loc4.insert()

# クラスの定義とデータベースの作成。ここで作成したクラスの構成がそのままデータベースにテーブルとして反映されます。
class SpatialConstants:
    SRID = 4326
class SampleLocation(db.Model): #first defined model class to store sample locations in the DB
    __tablename__ = 'sample_locations' #table is created and data is stored in a table   

    id = Column(Integer, primary_key=True) #column in a table, primary key is an attribute that identifies the row of the respective table
    description = Column(String(80)) #second column
    geom = Column(Geometry(geometry_type='POINT', srid=SpatialConstants.SRID))  
    learner_or_mentor = Column(String)
    username = Column(String)
    language_learn = Column(String)
    language_speak = Column(String)
    how_long_experienced = Column(String)
    how_long_learning = Column(String)
    online_inperson = Column(String)
    user_id = Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # many to one side of the relationship of SampleLocation with User
    user = db.relationship("User", back_populates="created_locations")

    @staticmethod
    def point_representation(latitude, longitude):
        point = 'POINT(%s %s)' % (longitude, latitude)
        wkb_element = WKTElement(point, srid=SpatialConstants.SRID)
        return wkb_element

    @staticmethod
    def get_items_within_radius(lat, lng, radius):
        """Return all sample locations within a given radius (in meters)"""

        #TODO: The arbitrary limit = 100 is just a quick way to make sure 
        # we won't return tons of entries at once, 
        # paging needs to be in place for real usecase
        results = SampleLocation.query.filter(
            ST_DWithin(
                cast(SampleLocation.geom, Geography),
                cast(from_shape(Point(lng, lat)), Geography),
                radius)
            ).limit(100).all() 

        return [l.to_dict() for l in results]    

    def get_location_latitude(self):
        point = to_shape(self.geom)
        return point.y

    def get_location_longitude(self):
        point = to_shape(self.geom)
        return point.x  

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'location': {
                'lng': self.get_location_longitude(),
                'lat': self.get_location_latitude()
            },
            'learner_or_mentor' : self.learner_or_mentor
        }    

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()         

# User login page
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False) # i.e Hanna Barbera
    display_name = db.Column(db.String(20), unique=True, nullable=False) # i.e hanna_25
    email = db.Column(db.String(120), unique=True, nullable=False) # i.e hanna@hanna-barbera.com
    password = db.Column(db.String(32), nullable=False) 
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_locations = db.relationship('SampleLocation', back_populates='user', order_by="SampleLocation.description", lazy=True) 
    
    @classmethod
    def get_by_id(cls, user_id):
        return cls.query.filter_by(id=user_id).first()
        
    def __repr__(self):
        return f"User({self.id}, '{self.display_name}', '{self.email}')"      

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()  