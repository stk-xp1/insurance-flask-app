# flaskapp.py
from flask import Flask, render_template, request, redirect, url_for, abort
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime
from sqlalchemy import text
import logging
from models import db, InsurancePolicy, User
from forms import PolicyForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///insurance.db'
app.config['SECRET_KEY'] = '#############'  # Change this

login_manager = LoginManager(app)
login_manager.login_view = 'login'

db.init_app(app)
csrf = CSRFProtect(app)

# Create tables when the app is initialized
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/test_db')
def test_db():
    try:
        db.session.execute(text('SELECT 1'))
        return "Databe connection is active."
    except Exception as e:
        return f"Database connection failed: {str(e)}"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']

            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for('index'))
            else:
                return "Invalid username or password"
            
        except Exception as e:
            app.logger.error(f"Error during login: {str(e)}")
            return "An error occurred during login. Please try again. "    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']

            if User.query.filter_by(username=username).first():
                return "Username already exists"

            new_user = User(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        
        except Exception as e:  
            app.logger.error(f"Error during registration: {str(e)}")
            return "An erro occurred registration . Please try again.   "
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('logout'))

@app.route('/')
@login_required
def index():
    policies = InsurancePolicy.query.all()
    return render_template('index.html', policies=policies)

@app.route('/delete/<int:policy_id>', methods=['POST'])
@login_required
def delete_policy(policy_id):
    policy = InsurancePolicy.query.get_or_404(policy_id)
    db.session.delete(policy)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/search')
@login_required
def search_policies():
    policies = InsurancePolicy.query.filter(
        (InsurancePolicy.insurance_type == 'Auto') &
        (InsurancePolicy.premium < 1000)
    ).all()
    return render_template('search_results.html', policies=policies)

@app.route('/policy/<int:policy_id>', methods=['GET'])
@login_required
def get_policy_by_id():
    policy = InsurancePolicy.query.get_or_404(policy)
    return render_template('policy_detail.html', policy=policy)

@app.route('/policy/raw/<string:policy_number>')
@login_required
def get_policy_by_number(policy_number):
    query = text("""
        SELECT id, policy_number, insurance_type, premium,
               DATE(start_date) as start_date,
               DATE(end_date) as end_date,
               status
        FROM insurance_policy
        WHERE policy_number = :policy_number
    """)

    result = db.session.execute(query, {'policy_number': policy_number})
    policy = result.mappings().first()

    if not policy:
        abort(404)
    return render_template('policy_detail.html', policy=policy)

@app.route('/stats')
@login_required
def policy_stats():
    query = text("""
        SELECT insurance_type,
               COUNT(*) as total_policies,
               AVG(premium) as avg_premium
        FROM insurance_policy
        GROUP BY insurance_type
    """)

    stats = db.session.execute(query).mappings().all()
    return render_template('stats.html', stats=stats)

@app.route('/add_policy', methods=['POST'])
def add_policy():
    start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
    end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date() if request.form['end_date'] else None

    new_policy = InsurancePolicy(
        policy_number=request.form['policy_number'],
        customer_id=request.form['customer_id'],
        insurance_type=request.form['insurance_type'],
        premium=float(request.form['premium']),
        start_date=start_date,
        end_date=end_date,
        status='Active'
    )

    db.session.add(new_policy)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

