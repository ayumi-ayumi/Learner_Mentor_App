from audioop import add
from email.headerregistry import Address
import os
import sys
from unicodedata import name
from flask import Flask, request, abort, jsonify, render_template, url_for, flash, redirect
from flask_cors import CORS
import traceback
from flask_login import LoginManager, login_required, login_user, logout_user, login_manager, current_user
from forms import AddCafeForm, NewLocationForm, RegistrationForm, LoginForm
from models import AddCafe, setup_db, SampleLocation, db_drop_and_create_all, User
from sqlalchemy.exc import IntegrityError
import hashlib
from dotenv import load_dotenv

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)
    load_dotenv()

    SECRET_KEY = os.urandom(32)
    app.config['SECRET_KEY'] = SECRET_KEY

    login_manager = LoginManager(app)
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'

    """ uncomment at the first time running the app. Then comment back so you do not erase db content over and over """
    db_drop_and_create_all() 

    @app.route('/', methods=['GET'])
    # @login_required
    def home():
        return render_template(
            'map.html', 
            map_key=os.getenv('GOOGLE_MAPS_API_KEY', 'GOOGLE_MAPS_API_KEY_WAS_NOT_SET?!')
        )

    @app.route('/detail', methods=['GET'])
    def detail():
        location_id = float(request.args.get('id'))
        item = SampleLocation.query.get(location_id)
        return render_template(
            'detail.html', 
            item=item,
            map_key=os.getenv('GOOGLE_MAPS_API_KEY', 'GOOGLE_MAPS_API_KEY_WAS_NOT_SET?!')
        )            

    @app.route("/new-location", methods=['GET', 'POST'])
    @login_required
    def new_location():
        form = NewLocationForm()

        if form.validate_on_submit():            
            latitude = float(form.coord_latitude.data)
            longitude = float(form.coord_longitude.data)
            address = form.address.data
            # description = form.description.data
            learner_or_mentor = form.learner_or_mentor.data
            user_name = User.display_name
            job_title = form.job_title.data
            language_learn = list(form.language_learn.data)
            language_skilled = list(form.language_skilled.data)
            # language_learn = form.getlist('language_learn').data
            # language_learn = request.form.getlist('language_learn')
            language_speak = list(form.language_speak.data)
            how_long_experienced = form.how_long_experienced.data
            how_long_learning = form.how_long_learning.data
            online_inperson = list(form.online_inperson.data)
            
            location = SampleLocation(
                # description=description,
                geom=SampleLocation.point_representation(latitude=latitude, longitude=longitude),
                address=address,
                learner_or_mentor=learner_or_mentor,
                user_name=user_name,
                job_title=job_title,
                language_learn=language_learn,
                language_skilled=language_skilled,
                language_speak=language_speak,
                how_long_experienced=how_long_experienced,
                how_long_learning=how_long_learning,
                online_inperson=online_inperson
            )   
            location.user_id = current_user.id
            location.user_name = current_user.display_name
            # location.fill_in_blanks()
            location.insert()
            
            flash(f'New location created!' , 'success')
            return redirect(url_for('home'))
    
        return render_template(
            'new-location.html',
            form=form,
            map_key=os.getenv('GOOGLE_MAPS_API_KEY', 'GOOGLE_MAPS_API_KEY_WAS_NOT_SET?!')
        ) 

    @app.route("/api/store_item")
    def store_item():
        try:
            latitude = float(request.args.get('lat'))
            longitude = float(request.args.get('lng'))
            # description = request.args.get('description')
            learner_or_mentor = request.args.get('learner_or_mentor')
            user_id = int(request.args.get('user_id'))
            user_name = request.args.get('user_name')
            job_title =request.args.get('job_title')
            address = request.args.get('address')
            language_learn = request.args.get('language_learn')
            language_skilled = request.args.get('language_skilled')
            language_speak = request.args.get('language_speak')
            how_long_experienced = request.args.get('how_long_experienced')
            how_long_learning = request.args.get('how_long_learning')
            online_inperson = request.args.get('online_inperson')

            location = SampleLocation(
                # description=description,
                geom=SampleLocation.point_representation(latitude=latitude, longitude=longitude),
                learner_or_mentor=learner_or_mentor,
                user_id=user_id,
                user_name=User.display_name,
                address=address,
                job_title=job_title,
                language_learn=language_learn,
                language_skilled=language_skilled,
                language_speak=language_speak,
                how_long_experienced=how_long_experienced,
                how_long_learning=how_long_learning,
                online_inperson=online_inperson

            )   
            location.insert()

            return jsonify(
                {
                    "success": True,
                    "location": location.to_dict()
                }
            ), 200
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            app.logger.error(traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2))
            abort(500)

    @app.route("/api/get_items_in_radius")
    def get_items_in_radius():
        try:
            latitude = float(request.args.get('lat'))
            longitude = float(request.args.get('lng'))
            radius = int(request.args.get('radius'))
            
            locations = SampleLocation.get_items_within_radius(latitude, longitude, radius)
            locations_cafe = AddCafe.get_items_within_radius(latitude, longitude, radius)

            return jsonify(
                {
                    "success": True,
                    "results": locations + locations_cafe
                    # "results_cafe": locations_cafe
                }
            ), 200
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            app.logger.error(traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2))
            abort(500)

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "server error"
        }), 500
    
    # register
    @app.route("/register", methods=['GET', 'POST'])
    def register():
    # Sanity check: if the user is already authenticated then go back to home page
    # if current_user.is_authenticated:
    #     return redirect(url_for('home'))

    # Otherwise process the RegistrationForm from request (if it came)
        form = RegistrationForm()
        if form.validate_on_submit():
            # hash user password, create user and store it in database
            hashed_password = hashlib.md5(form.password.data.encode()).hexdigest()
            user = User(
                full_name=form.fullname.data,
                display_name=form.username.data, 
                email=form.email.data, 
                password=hashed_password)

            try:
                user.insert()
                flash(f'Account created for: {form.username.data}!', 'success')
                return redirect(url_for('home'))
            except IntegrityError as e:
                flash(f'Could not sign up! The entered username or email might be already taken', 'danger')
                print('IntegrityError when trying to store new user')
                # db.session.rollback()
            
        return render_template('registration.html', form=form)   

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)           

    # user login
    @app.route("/login", methods=['GET', 'POST'])
    def login():
        # Sanity check: if the user is already authenticated then go back to home page
        # if current_user.is_authenticated:
        #    return redirect(url_for('home'))

        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(display_name=form.username.data).first()
            hashed_input_password = hashlib.md5(form.password.data.encode()).hexdigest()
            if user and user.password == hashed_input_password:
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                flash('Login Unsuccessful. Please check user name and password', 'danger')
        return render_template('login.html', title='Login', form=form) 

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash(f'You have logged out!', 'success')
        return redirect(url_for('home'))   

    @app.route("/add-cafe", methods=['GET', 'POST'])
    @login_required
    def add_cafe():
        form = AddCafeForm()
        pass

        if form.validate_on_submit():            
            # description = form.description.data
            address_cafe = form.address_cafe.data
            # cafe_name = form.address_cafe.data
            latitude = float(form.coord_latitude.data)
            longitude = float(form.coord_longitude.data)
            user_name = User.display_name
            cafe_datail = list(form.cafe_datail.data)


            location = AddCafe(
                # description=description,
                address_cafe=address_cafe,
                geom=SampleLocation.point_representation(latitude=latitude, longitude=longitude),
                cafe_datail=cafe_datail,
                user_name=user_name,
            )   
            location.user_id = current_user.id
            location.user_name = current_user.display_name
            # location.cafe_name()
            location.insert()

            flash(f'New cafe added!' , 'success')
            return redirect(url_for('home'))
    
        return render_template(
            'add-cafe.html',
            form=form,
            map_key=os.getenv('GOOGLE_MAPS_API_KEY', 'GOOGLE_MAPS_API_KEY_WAS_NOT_SET?!')
        ) 

    # これここでだいじょうぶ？ line135の可能性あり
    return app

app = create_app()
if __name__ == '__main__':
    port = int(os.environ.get("PORT",8000))
    app.run(host='127.0.0.1',port=port,debug=True)