import json
import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import logging
from services.deepseek_service import DeepseekService

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///items.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'growlog-secure-key-32-chars-long-1234')
app.config['DEEPSEEK_API_KEY'] = os.environ.get('DEEPSEEK_API_KEY')
db = SQLAlchemy(app)

def from_json(value):
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return value

app.jinja_env.filters['from_json'] = from_json

# Serve manifest.json from root path
@app.route('/manifest.json')
def serve_manifest():
    return app.send_static_file('manifest.json')

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Plant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='plants')
    facts = db.relationship('PlantFact', backref='plant', lazy=True, order_by='PlantFact.position', cascade="all, delete-orphan")

class PlantFact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plant.id'), nullable=False)
    label = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Text, nullable=False)
    value_type = db.Column(db.String(20), nullable=False)  # 'date', 'short_text', 'long_text', 'integer', 'decimal', 'photo'
    photo_path = db.Column(db.String(200), nullable=True)  # Path to uploaded photo
    position = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

def admin_required(f):
    """Decorator to ensure user is admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Admin access required', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/users')
@login_required
@admin_required
def list_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_admin = 'is_admin' in request.form
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('add_user'))
            
        user = User(username=username, is_admin=is_admin)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('User created successfully', 'success')
        return redirect(url_for('list_users'))
    
    return render_template('admin/edit_user.html', user=None)

@app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.username = request.form['username']
        if request.form['password']:
            user.set_password(request.form['password'])
        user.is_admin = 'is_admin' in request.form
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('list_users'))
    
    return render_template('admin/edit_user.html', user=user)

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash('Cannot delete your own account', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully', 'success')
    return redirect(url_for('list_users'))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = 'remember' in request.form
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/')
@login_required
def index():
    search_query = request.args.get('q', '')
    if search_query:
        plants = Plant.query.filter(
            Plant.name.contains(search_query) |
            (Plant.number == int(search_query) if search_query.isdigit() else False)
        )
    else:
        plants = Plant.query.filter_by(user_id=current_user.id).all()
    # Get first photo fact for each plant
    plants_with_photos = []
    for plant in plants:
        first_photo = next((fact for fact in plant.facts if fact.photo_path), None)
        plants_with_photos.append((plant, first_photo))
    
    return render_template('list.html', plants=plants_with_photos, search_query=search_query)

@app.route('/plant/<int:plant_id>/facts/add')
@login_required
def add_fact_page(plant_id):
    plant = Plant.query.get_or_404(plant_id)
    return render_template('add_fact.html', plant=plant)


@app.route('/api/plant/<int:plant_id>/facts', methods=['POST'])
@login_required
def add_fact(plant_id):
    plant = Plant.query.get_or_404(plant_id)
    
    if request.content_type.startswith('multipart/form-data'):
        data = request.form
    else:
        data = request.get_json()
    
    # Handle plant description special case
    if data.get('value_type') == 'plant_care':
        logging.info(f"Entering plant_care case for plant_id: {plant.id}")
        
        # Get first plant type fact
        plant_type_fact = PlantFact.query.filter_by(
            plant_id=plant.id,
            label='Plant Type'
        ).first()

        if not plant_type_fact:
            logging.error(f"No Plant Type fact found for plant_id: {plant.id}")
            return jsonify({
                'error': 'Cannot generate care guidelines - please first set a Plant Type for this plant'
            }), 400

        # Call Deepseek API
        plant_type = plant_type_fact.value
        logging.info(f"Generating care guidelines for plant_type: {plant_type}")
        
        try:
            deepseek = DeepseekService(app.config['DEEPSEEK_API_KEY'])
            care_guidelines = deepseek.generate_care_guidelines(plant_type)
            logging.debug(f"Generated care guidelines: {care_guidelines}")
        except Exception as e:
            logging.error(f"Failed to generate care guidelines: {str(e)}")
            return jsonify({'error': 'Failed to generate care guidelines'}), 500
        
        fact = PlantFact(
            plant_id=plant.id,
            label=data['label'],
            value=care_guidelines,
            value_type='plant_care',
            position=len(plant.facts)
        )
        
    elif data.get('value_type') == 'photo':
        if 'photo' not in request.files:
            return jsonify({'error': 'No photo uploaded'}), 400
        
        photo = request.files['photo']
        if photo.filename == '':
            return jsonify({'error': 'No selected photo'}), 400
            
        filename = f"plant_{plant.id}_fact_{len(plant.facts)}_{photo.filename}"
        upload_dir = "static/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        photo_path = os.path.join(upload_dir, filename)
        photo.save(photo_path)
        # Store relative path without 'static/' prefix
        photo_url = f"uploads/{filename}"
        
        fact = PlantFact(
            plant_id=plant.id,
            label=data['label'],
            value='Photo',
            value_type='photo',
            photo_path=photo_url,
            position=len(plant.facts)
        )
    else:
        # Convert and validate value before insertion
        value = data['value']
        if isinstance(value, dict):
            value = json.dumps(value)
        elif not isinstance(value, str):
            value = str(value)
        
        # Debug log the value type before insertion
        app.logger.debug(f"Storing fact value (type: {type(value)}): {value[:100]}")
            
        fact = PlantFact(
            plant_id=plant.id,
            label=data['label'],
            value=value,
            value_type=data['value_type'],
            position=len(plant.facts)
        )
    
    db.session.add(fact)
    db.session.commit()
    
    return jsonify({
        'id': fact.id,
        'label': fact.label,
        'value': fact.value,
        'value_type': fact.value_type,
        'position': fact.position,
        'created_at': fact.created_at.strftime('%Y-%m-%d'),
        'updated_at': fact.updated_at.strftime('%Y-%m-%d')
    })

@app.route('/api/fact/<int:fact_id>', methods=['PUT', 'DELETE'])
@login_required
def manage_fact(fact_id):
    fact = PlantFact.query.get_or_404(fact_id)
    
    if request.method == 'PUT':
        data = request.get_json()
        fact.label = data.get('label', fact.label)
        fact.value = data.get('value', fact.value)
        fact.value_type = data.get('value_type', fact.value_type)
        db.session.commit()
        
        return jsonify({
            'id': fact.id,
            'label': fact.label,
            'value': fact.value,
            'value_type': fact.value_type,
            'position': fact.position,
            'updated_at': fact.updated_at.strftime('%Y-%m-%d')
        })
    
    elif request.method == 'DELETE':
        db.session.delete(fact)
        db.session.commit()
        return jsonify({'success': True})

@app.route('/api/fact/<int:fact_id>/move', methods=['POST'])
@login_required
def move_fact(fact_id):
    fact = PlantFact.query.get_or_404(fact_id)
    direction = request.json.get('direction')
    
    if direction == 'up' and fact.position > 0:
        other_fact = PlantFact.query.filter_by(
            plant_id=fact.plant_id,
            position=fact.position - 1
        ).first()
        if other_fact:
            other_fact.position += 1
            fact.position -= 1
    elif direction == 'down':
        other_fact = PlantFact.query.filter_by(
            plant_id=fact.plant_id,
            position=fact.position + 1
        ).first()
        if other_fact:
            other_fact.position -= 1
            fact.position += 1
    
    db.session.commit()
    return jsonify({
        'new_position': fact.position,
        'success': True
    })

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_plant():
    if request.method == 'POST':
        number = request.form['number']
        name = request.form['name']
        new_plant = Plant(number=number, name=name, user_id=current_user.id)
        db.session.add(new_plant)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/view/<int:id>')
@login_required
def view_plant(id):
    plant = Plant.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template('view.html', plant=plant)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_plant(id):
    plant = Plant.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    if request.method == 'POST':
        plant.number = request.form['number']
        plant.name = request.form['name']
        if current_user.is_admin:  # Only admins can change ownership
            plant.user_id = request.form['user_id']
        db.session.commit()
        from_page = request.args.get('from', 'index')
        if from_page == 'view':
            return redirect(url_for('view_plant', id=id))
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template('edit.html', plant=plant, users=users)

@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_plant(id):
    plant = Plant.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(plant)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/plants/<int:plant_id>/facts/<int:fact_id>/reorder', methods=['POST'])
def reorder_fact(plant_id, fact_id):
    fact = PlantFact.query.get_or_404(fact_id)
    direction = request.json.get('direction')
    
    if direction == 'up':
        # Find previous fact and swap positions
        prev_fact = PlantFact.query.filter(
            PlantFact.plant_id == plant_id,
            PlantFact.position < fact.position
        ).order_by(PlantFact.position.desc()).first()
        
        if prev_fact:
            prev_fact.position, fact.position = fact.position, prev_fact.position
            db.session.commit()
            
    elif direction == 'down':
        # Find next fact and swap positions
        next_fact = PlantFact.query.filter(
            PlantFact.plant_id == plant_id,
            PlantFact.position > fact.position
        ).order_by(PlantFact.position.asc()).first()
        
        if next_fact:
            next_fact.position, fact.position = fact.position, next_fact.position
            db.session.commit()
    
    return jsonify({'success': True})

@app.route('/plants/<int:plant_id>/facts/<int:fact_id>', methods=['DELETE'])
def delete_fact(plant_id, fact_id):
    fact = PlantFact.query.get_or_404(fact_id)
    db.session.delete(fact)
    db.session.commit()
    return jsonify({'success': True})

def create_first_user():
    if not User.query.first():
        admin = User(username='admin', is_admin=True)
        password = secrets.token_urlsafe(8)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print(f"Created first admin user. Credentials:")
        print(f"Username: admin")
        print(f"Password: {password}")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_first_user()
    app.run(host='0.0.0.0', port=5000, debug=True)