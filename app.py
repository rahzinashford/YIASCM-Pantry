import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from models import db, Team, Product, Submission, Setting

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")

# Upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database configuration
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL environment variable is not set")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize database
db.init_app(app)

# Initialize database and sample data
def init_database():
    with app.app_context():
        db.create_all()
        
        # Run database migrations
        migrate_database()
        
        # Check if we need to initialize default settings
        if not Setting.query.filter_by(setting_key='round1_budget').first():
            Setting.set_setting('round1_budget', '200', 'Budget limit for Round 1')
            Setting.set_setting('admin_username', 'admin', 'Administrator username')
            Setting.set_setting('admin_password', generate_password_hash('admin123'), 'Administrator password hash')
        
        # Check if we need to add sample products
        try:
            product_count = Product.query.count()
        except Exception as e:
            # If query fails due to missing columns, assume we need sample data
            product_count = 0
        
        if product_count == 0:
            sample_products = [
                {'name': 'Rice', 'price': 5, 'unit_type': 'grams'},
                {'name': 'Apple', 'price': 15, 'unit_type': 'pieces'},
                {'name': 'Sugar', 'price': 3, 'unit_type': 'grams'},
                {'name': 'Chocolate Bar', 'price': 50, 'unit_type': 'pieces'},
                {'name': 'Flour', 'price': 4, 'unit_type': 'grams'},
                {'name': 'Orange', 'price': 12, 'unit_type': 'pieces'},
                {'name': 'Salt', 'price': 2, 'unit_type': 'grams'},
                {'name': 'Banana', 'price': 8, 'unit_type': 'pieces'}
            ]
            
            for product_data in sample_products:
                product = Product(**product_data)
                db.session.add(product)
            
            db.session.commit()

def migrate_database():
    """Handle database migrations"""
    try:
        with db.engine.connect() as conn:
            # Check if image_filename column exists
            result = conn.execute(db.text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='products' AND column_name='image_filename'
            """))
            
            if not result.fetchone():
                # Add image_filename column if it doesn't exist
                conn.execute(db.text("ALTER TABLE products ADD COLUMN image_filename VARCHAR(255)"))
                conn.commit()
                app.logger.info("Added image_filename column to products table")
            
            # Check if image_data column exists
            result = conn.execute(db.text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='products' AND column_name='image_data'
            """))
            
            if not result.fetchone():
                # Add image_data and image_mimetype columns
                conn.execute(db.text("ALTER TABLE products ADD COLUMN image_data BYTEA"))
                conn.execute(db.text("ALTER TABLE products ADD COLUMN image_mimetype VARCHAR(50)"))
                conn.commit()
                app.logger.info("Added image_data and image_mimetype columns to products table")
    except Exception as e:
        app.logger.error(f"Migration error: {e}")

init_database()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'team_name' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Admin access required.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        team_name = request.form['team_name'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        institution = request.form['institution'].strip()
        members = request.form['members'].strip()
        
        if not all([team_name, password, institution, members]):
            flash('All fields are required.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        # Check if team name already exists
        existing_team = Team.query.filter_by(team_name=team_name).first()
        if existing_team:
            flash('Team name already exists. Please choose a different name.', 'error')
            return render_template('register.html')
        
        # Create new team
        team = Team(
            team_name=team_name,
            institution=institution,
            members=members,
            registered_at=datetime.utcnow()
        )
        team.set_password(password)
        
        db.session.add(team)
        db.session.commit()
        
        flash('Team registered successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        team_name = request.form['team_name'].strip()
        password = request.form['password']
        
        team = Team.query.filter_by(team_name=team_name).first()
        
        if team and team.check_password(password):
            session['team_name'] = team_name
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid team name or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('team_name', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    team_name = session['team_name']
    team = Team.query.filter_by(team_name=team_name).first()
    
    if not team:
        flash('Team not found.', 'error')
        return redirect(url_for('logout'))
    
    team_data = team.to_dict()
    return render_template('dashboard.html', team_name=team_name, team_data=team_data)

@app.route('/round1', methods=['GET', 'POST'])
@login_required
def round1():
    team_name = session['team_name']
    team = Team.query.filter_by(team_name=team_name).first()
    
    if not team:
        flash('Team not found.', 'error')
        return redirect(url_for('logout'))
    
    if team.round1_completed:
        flash('You have already completed Round 1.', 'info')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # Log the POST request for debugging
        app.logger.info(f"Round 1 POST request from team: {team_name}")
        app.logger.info(f"Form data keys: {list(request.form.keys())}")
        app.logger.info(f"User agent: {request.headers.get('User-Agent', 'Unknown')}")
        
        products = Product.query.filter_by(is_active=True).all()
        budget = float(Setting.get_setting('round1_budget', '200'))
        
        selected_items = []
        total_price = 0
        total_grams = 0
        total_pieces = 0
        
        for product in products:
            quantity_key = f'quantity_{product.id}'
            if quantity_key in request.form:
                raw_quantity = request.form[quantity_key]
                quantity = int(raw_quantity or 0)
                app.logger.info(f"Product {product.id} ({product.name}): raw='{raw_quantity}', parsed={quantity}")
                if quantity > 0:
                    item_total = quantity * float(product.price)
                    total_price += item_total
                    
                    if product.unit_type == 'grams':
                        total_grams += quantity
                    else:  # pieces
                        total_pieces += quantity
                    
                    selected_items.append({
                        'product_id': product.id,
                        'name': product.name,
                        'price': float(product.price),
                        'unit_type': product.unit_type,
                        'quantity': quantity,
                        'total': item_total
                    })
        
        app.logger.info(f"Final summary: selected_items={len(selected_items)}, total_price={total_price}, total_grams={total_grams}, total_pieces={total_pieces}")
        
        if total_price > budget:
            app.logger.warning(f"Budget exceeded: {total_price} > {budget}")
            flash(f'Total price (₹{total_price}) exceeds budget (₹{budget}). Please adjust your selection.', 'error')
            products_dict = [p.to_dict() for p in products]
            return render_template('round1.html', products=products_dict, budget=budget)
        
        if not selected_items:
            app.logger.warning("No items selected")
            flash('Please select at least one item.', 'error')
            products_dict = [p.to_dict() for p in products]
            return render_template('round1.html', products=products_dict, budget=budget)
        
        # Calculate score (total quantity)
        score = total_grams + total_pieces
        
        # Save submission
        submission = Submission(
            team_id=team.id,
            round_number=1,
            total_price=total_price,
            total_grams=total_grams,
            total_pieces=total_pieces,
            score=score,
            submitted_at=datetime.utcnow()
        )
        submission.set_items(selected_items)
        
        db.session.add(submission)
        
        # Mark round as completed
        team.round1_completed = True
        db.session.commit()
        
        flash(f'Round 1 completed! Total quantity: {score} units for ₹{total_price}', 'success')
        return redirect(url_for('dashboard'))
    
    products = Product.query.filter_by(is_active=True).all()
    products_dict = [p.to_dict() for p in products]
    budget = float(Setting.get_setting('round1_budget', '200'))
    
    return render_template('round1.html', products=products_dict, budget=budget)

@app.route('/round2', methods=['GET', 'POST'])
@login_required
def round2():
    team_name = session['team_name']
    team = Team.query.filter_by(team_name=team_name).first()
    
    if not team:
        flash('Team not found.', 'error')
        return redirect(url_for('logout'))
    
    if not team.round1_completed:
        flash('You must complete Round 1 first.', 'error')
        return redirect(url_for('round1'))
    
    if team.round2_completed:
        flash('You have already completed Round 2.', 'info')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        products = Product.query.filter_by(is_active=True).all()
        
        selected_items = []
        total_price = 0
        total_grams = 0
        total_pieces = 0
        
        for product in products:
            quantity_key = f'quantity_{product.id}'
            if quantity_key in request.form:
                quantity = int(request.form[quantity_key] or 0)
                if quantity > 0:
                    item_total = quantity * float(product.price)
                    total_price += item_total
                    
                    if product.unit_type == 'grams':
                        total_grams += quantity
                    else:  # pieces
                        total_pieces += quantity
                    
                    selected_items.append({
                        'product_id': product.id,
                        'name': product.name,
                        'price': float(product.price),
                        'unit_type': product.unit_type,
                        'quantity': quantity,
                        'total': item_total
                    })
        
        if not selected_items:
            flash('Please select at least one item.', 'error')
            products_dict = [p.to_dict() for p in products]
            return render_template('round2.html', products=products_dict)
        
        # Calculate score (total price divided by total quantity)
        total_quantity = total_grams + total_pieces
        score = total_price / total_quantity if total_quantity > 0 else 0
        
        # Save submission
        submission = Submission(
            team_id=team.id,
            round_number=2,
            total_price=total_price,
            total_grams=total_grams,
            total_pieces=total_pieces,
            score=score,
            submitted_at=datetime.utcnow()
        )
        submission.set_items(selected_items)
        
        db.session.add(submission)
        
        # Mark round as completed
        team.round2_completed = True
        db.session.commit()
        
        flash(f'Round 2 completed! Score: {score:.2f} (₹{total_price} for {total_quantity} units)', 'success')
        return redirect(url_for('dashboard'))
    
    products = Product.query.filter_by(is_active=True).all()
    products_dict = [p.to_dict() for p in products]
    return render_template('round2.html', products=products_dict)

@app.route('/leaderboard')
def leaderboard():
    # Get Round 1 submissions sorted by score (descending - higher quantity is better)
    round1_submissions = Submission.query.filter_by(round_number=1).order_by(Submission.score.desc()).all()
    round1_leaderboard = [s.to_dict() for s in round1_submissions]
    
    # Get Round 2 submissions sorted by score (descending - higher ratio is better)
    round2_submissions = Submission.query.filter_by(round_number=2).order_by(Submission.score.desc()).all()
    round2_leaderboard = [s.to_dict() for s in round2_submissions]
    
    return render_template('leaderboard.html', 
                         round1_leaderboard=round1_leaderboard,
                         round2_leaderboard=round2_leaderboard)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        admin_username = Setting.get_setting('admin_username', 'admin')
        admin_password_hash = Setting.get_setting('admin_password')
        
        if (username == admin_username and admin_password_hash and
            check_password_hash(admin_password_hash, password)):
            session['admin_logged_in'] = True
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials.', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Admin logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    teams = Team.query.all()
    teams_dict = {team.team_name: team.to_dict() for team in teams}
    
    products = Product.query.filter_by(is_active=True).all()
    products_dict = [p.to_dict() for p in products]
    
    round1_submissions = Submission.query.filter_by(round_number=1).all()
    round2_submissions = Submission.query.filter_by(round_number=2).all()
    submissions = {
        'round1': [s.to_dict() for s in round1_submissions],
        'round2': [s.to_dict() for s in round2_submissions]
    }
    
    settings = {
        'round1_budget': float(Setting.get_setting('round1_budget', '200'))
    }
    
    return render_template('admin_dashboard.html',
                         teams=teams_dict,
                         products=products_dict,
                         submissions=submissions,
                         settings=settings)

@app.route('/admin/delete_team/<team_name>', methods=['POST'])
@admin_required
def delete_team(team_name):
    team = Team.query.filter_by(team_name=team_name).first()
    
    if team:
        # Delete associated submissions (cascade should handle this)
        db.session.delete(team)
        db.session.commit()
        flash(f'Team "{team_name}" deleted successfully.', 'success')
    else:
        flash('Team not found.', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_product', methods=['POST'])
@admin_required
def add_product():
    name = request.form['name'].strip()
    price = float(request.form['price'])
    quantity = int(request.form['quantity'])
    unit_type = request.form['unit_type']
    
    image_filename = None
    image_data = None
    image_mimetype = None
    
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename and allowed_file(file.filename):
            # Store image data in database instead of file system
            image_data = file.read()
            image_mimetype = file.mimetype
            image_filename = secure_filename(file.filename)
    
    if name and price > 0 and quantity > 0 and unit_type in ['grams', 'pieces']:
        product = Product(
            name=name,
            price=price,
            quantity=quantity,
            unit_type=unit_type,
            image_filename=image_filename,
            image_data=image_data,
            image_mimetype=image_mimetype
        )
        
        db.session.add(product)
        db.session.commit()
        flash(f'Product added successfully! ({product.unit_display})', 'success')
    else:
        flash('Invalid product data. Please check all fields.', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update_product/<int:product_id>', methods=['POST'])
@admin_required
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    name = request.form['name'].strip()
    price = float(request.form['price'])
    quantity = int(request.form['quantity'])
    unit_type = request.form['unit_type']
    
    # Handle image update
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename and allowed_file(file.filename):
            # Store new image data in database
            product.image_data = file.read()
            product.image_mimetype = file.mimetype
            product.image_filename = secure_filename(file.filename)
    
    if name and price > 0 and quantity > 0 and unit_type in ['grams', 'pieces']:
        product.name = name
        product.price = price
        product.quantity = quantity
        product.unit_type = unit_type
        product.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash(f'Product "{name}" updated successfully!', 'success')
    else:
        flash('Invalid product data. Please check all fields.', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
@admin_required
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        # No need to delete files since images are stored in database
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully!', 'success')
    else:
        flash('Product not found.', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/product_image/<int:product_id>')
def serve_product_image(product_id):
    """Serve product image from database"""
    product = Product.query.get(product_id)
    if product and product.image_data:
        from flask import Response
        return Response(
            product.image_data,
            mimetype=product.image_mimetype or 'image/jpeg',
            headers={'Cache-Control': 'public, max-age=3600'}
        )
    return '', 404

@app.route('/admin/update_budget', methods=['POST'])
@admin_required
def update_budget():
    budget = float(request.form['budget'])
    
    if budget > 0:
        Setting.set_setting('round1_budget', str(budget), 'Budget limit for Round 1')
        flash(f'Round 1 budget updated to ₹{budget}', 'success')
    else:
        flash('Invalid budget amount.', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reset_rounds', methods=['POST'])
@admin_required
def reset_rounds():
    team_name = request.form.get('team_name')
    reset_round1 = 'reset_round1' in request.form
    reset_round2 = 'reset_round2' in request.form
    
    if not team_name:
        flash('No team selected.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    team = Team.query.filter_by(team_name=team_name).first()
    if not team:
        flash('Team not found.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    reset_actions = []
    
    if reset_round1:
        # Delete Round 1 submission
        round1_submission = Submission.query.filter_by(team_id=team.id, round_number=1).first()
        if round1_submission:
            db.session.delete(round1_submission)
        team.round1_completed = False
        reset_actions.append('Round 1')
        
        # If resetting Round 1, also reset Round 2 since it depends on Round 1
        if team.round2_completed:
            round2_submission = Submission.query.filter_by(team_id=team.id, round_number=2).first()
            if round2_submission:
                db.session.delete(round2_submission)
            team.round2_completed = False
            if 'Round 2' not in reset_actions:
                reset_actions.append('Round 2 (dependent on Round 1)')
    
    if reset_round2 and not reset_round1:
        # Delete Round 2 submission only
        round2_submission = Submission.query.filter_by(team_id=team.id, round_number=2).first()
        if round2_submission:
            db.session.delete(round2_submission)
        team.round2_completed = False
        reset_actions.append('Round 2')
    
    if reset_actions:
        db.session.commit()
        flash(f'Successfully reset {", ".join(reset_actions)} for team "{team_name}".', 'success')
    else:
        flash('No rounds were selected for reset.', 'warning')
    
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



