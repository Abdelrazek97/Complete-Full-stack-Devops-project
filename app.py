from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
import os
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import date

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this in production!
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST'),
    'port': int(os.getenv('MYSQL_PORT')),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'charset': 'utf8mb4',
}
current_year= date.today().year


class CompatRow(dict):
    def __getitem__(self, key):
        if isinstance(key, int):
            return tuple(self.values())[key]
        return super().__getitem__(key)


def adapt_sql_query(query):
    adapted = query.replace('==', '=')
    adapted = adapted.replace('?', '__PARAM__')
    adapted = adapted.replace('%', '%%')
    adapted = adapted.replace('__PARAM__', '%s')
    return adapted


def wrap_row(row):
    if isinstance(row, dict):
        return CompatRow(row)
    return row


class MySQLCursor:
    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, query, params=None):
        if params is None:
            params = ()
        self._cursor.execute(adapt_sql_query(query), params)
        return self

    def fetchone(self):
        return wrap_row(self._cursor.fetchone())

    def fetchall(self):
        return [wrap_row(row) for row in self._cursor.fetchall()]

    def __getattr__(self, name):
        return getattr(self._cursor, name)


class MySQLConnection:
    def __init__(self):
        self._conn = pymysql.connect(
            **MYSQL_CONFIG,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )

    def execute(self, query, params=None):
        cursor = self.cursor()
        cursor.execute(query, params)
        return cursor

    def cursor(self):
        return MySQLCursor(self._conn.cursor())

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()


def get_db_connection():
    return MySQLConnection()

# Initialize database
def init_db():
    conn = get_db_connection()

    # Create admin user if not exists
    admin_exists = conn.execute('SELECT 1 FROM users WHERE username = ?', ('admin',)).fetchone()
    if not admin_exists:
        conn.execute(
            'INSERT INTO users (username, password, role, full_name,department) VALUES (?, ?, ?, ?, ?)',
            ('admin', generate_password_hash('admin123'), 'admin', 'Administrator','Medical Education')
        )
    
    conn.commit()
    conn.close()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login'))
        role = session.get('role')
        if (role == 'admin' or role == 'head' )  :
            return f(*args, **kwargs)
        return redirect(url_for('index'))
    return decorated_function



@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'head' or session.get('role') == 'admin':
            return redirect(url_for('view_users'))
        else:
            return redirect(url_for('view_person',id=session.get('user_id')))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['department'] = user['department']
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        department = request.form['department']
        
        if not username or not password:
            flash('Username and password are required', 'danger')
        else:
            conn = get_db_connection()
            try:
                conn.execute(
                    'INSERT INTO users (username, password, full_name, department) VALUES (?, ?, ?, ?)',
                    (username, generate_password_hash(password), full_name, department)
                )
                conn.commit()
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
            except pymysql.err.IntegrityError:
                flash('Username already exists', 'danger')
            finally:
                conn.close()
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/semester_add', methods=['GET', 'POST'])
@login_required
def semester_data():
    if request.method == 'POST':
        # Get form data
        data = {
            'user_id': session['user_id'],
            'semester': request.form['semester'],
            'course_code': request.form['course_code'],
            'num_students': int(request.form['num_students']) if request.form['num_students'] else None,
            'teaching_load': request.form['teaching_load'],
            'course_name': request.form['course_name'],
            'semester_type': request.form['semester_type'] ,
            'credit_hours': int(request.form['credit_hours']) if request.form['credit_hours'] else None,
            
        }

        # Insert into database
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO academic_data (
                user_id, semester, course_code, num_students, teaching_load,
                course_name, semester_type, credit_hours
                
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ? )
        ''', tuple(data.values()))
        conn.commit()
        conn.close()

        flash('Data added successfully!', 'success')
        return redirect(url_for('view_person',id=session['user_id']))

    return render_template('add_semester.html')



@app.route('/Scientific_production', methods=['GET', 'POST'])
@login_required
def Scientific_production_data():
    if request.method == 'POST':
        # Get form data
        data = {
            'user_id': session['user_id'],
            'Scientific_research': request.form['Scientific_research'],
            'supervision_Graduation': request.form['supervision_Graduation'],
        }
        try:
            # Insert into database
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO Scientific_production (
                    user_id, Scientific_research, supervision_Graduation
                ) VALUES (?, ?, ?)
            ''', tuple(data.values()))
            conn.commit()
            flash('Data added successfully!', 'success')
            return redirect(url_for('view_person',id=session['user_id']))
        except:
            return render_template('page-404.html', error_msg=' لقد قمت بالتقييم بالفعل هذا العام ❌')
        finally:
            conn.close() 

    return render_template('Scientific_production.html')

@app.route('/cirteria_add', methods=['GET', 'POST'])
@login_required
def cirteria_data():
    if request.method == 'POST':
        # Get form data
        data = {
            'user_id': session['user_id'],
            'Develop_courses': request.form['Develop_courses'],
            'Prepare_file': request.form['Prepare_file'],
            'Electronic_tests': request.form['Electronic_tests'],
            'Prepare_material_content': request.form['Prepare_material_content'],
            'Use_learning_effectively': request.form['Use_learning_effectively'],
            'teaching_methods': request.form['teaching_methods'],
            'Methods_student': request.form['Methods_student'],
            'preparing_test_questions': request.form['preparing_test_questions'],
            'Provide_academic_guidance': request.form['Provide_academic_guidance']
        }
        numeric_fields = [
         'Develop_courses', 'Prepare_file', 'Electronic_tests', 
        'Prepare_material_content', 'Use_learning_effectively',
        'teaching_methods', 'Methods_student', 'preparing_test_questions',
        'Provide_academic_guidance'
           ]

        data['aspests_sum'] = sum(int(data[field]) for field in numeric_fields)
        # Insert into database
        try:
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO Evaluation_aspects (
                    user_id, Develop_courses, Prepare_file, Electronic_tests,
                    Prepare_material_content, Use_learning_effectively,teaching_methods,
                    Methods_student,preparing_test_questions,Provide_academic_guidance,aspects_sum
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', tuple(data.values()))
            conn.commit() 
        except:
            return render_template('page-404.html', error_msg=' لقد قمت بالتقييم بالفعل هذا العام ❌')        
        finally:
            conn.close() 
        return redirect(url_for('view_person',id=session['user_id']))

    return render_template('criteria_of_evaluation.html')

@app.route('/ethical_add', methods=['GET', 'POST'])
@login_required
def ethical_data():
    if request.method == 'POST':
        # Get form data
        data = {
            'user_id': session['user_id'],
            'professional_values': request.form['professional_values'],
            'offer_encouragement': request.form['offer_encouragement'],
            'respect_leaders': request.form['respect_leaders'],
            'take_responsibility': request.form['take_responsibility'],
            'decent_appearance': request.form['decent_appearance'],
            'punctuality': request.form['punctuality'],
            'office_hours': request.form['office_hours'],
            
        }
        numeric_fields = [
         'professional_values', 'offer_encouragement', 'respect_leaders', 
        'take_responsibility', 'decent_appearance',
        'punctuality', 'office_hours'
           ]

        data['aspects_sum'] = sum(int(data[field]) for field in numeric_fields)
        try:
        # Insert into database
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO ethics_responsibility (
                    user_id, professional_values, offer_encouragement, respect_leaders, 
            take_responsibility, decent_appearance,
            punctuality, office_hours,aspects_sum
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', tuple(data.values()))
            conn.commit()
        except:
            return render_template('page-404.html', error_msg=' لقد قمت بالتقييم بالفعل هذا العام ❌')
        finally:
            conn.close()

        return redirect(url_for('view_person',id=session['user_id']))

    return render_template('EthicsResponsibility_add.html')

@app.route('/update/ethical/<int:id>', methods=['GET', 'POST'])
@login_required
def update_ethical(id):
    if session.get('role') == 'head':
        if request.method == 'POST':
            # Get form data 
          
            professional_values_evaluation= request.form['professional_values_evaluation']
            offer_encouragement_evaluation= request.form['offer_encouragement_evaluation']
            respect_leaders_evaluation= request.form['respect_leaders_evaluation']
            take_responsibility_evaluation= request.form['take_responsibility_evaluation']
            decent_appearance_evaluation= request.form['decent_appearance_evaluation']
            punctuality_evaluation= request.form['punctuality_evaluation']
            office_hours_evaluation= request.form['office_hours_evaluation']
           
            evaluation_fields = [
            'professional_values_evaluation',
            'offer_encouragement_evaluation',
            'respect_leaders_evaluation',
            'take_responsibility_evaluation',
            'decent_appearance_evaluation',
            'punctuality_evaluation',
            'office_hours_evaluation',
             ]

            # Calculate sum with error handling
            try:
                evaluation_sum = sum(int(request.form[field]) for field in evaluation_fields)
            except ValueError as e:
                # Handle case where a value can't be converted to int
                evaluation_sum = 0  # or raise an exception
                print(f"Error converting form values: {e}")

            # Insert into database
            conn = get_db_connection()
            cursor = conn.cursor()

            update_query = ''' UPDATE ethics_responsibility SET professional_values_evaluation == ?,
            offer_encouragement_evaluation == ?, respect_leaders_evaluation == ? ,
            take_responsibility_evaluation == ?, decent_appearance_evaluation == ?,
            punctuality_evaluation == ?, office_hours_evaluation == ?,
            evaluation_sum == ? 
            WHERE ethics_responsibility.user_id == ? '''

            cursor.execute(update_query, (professional_values_evaluation,offer_encouragement_evaluation,
            respect_leaders_evaluation,take_responsibility_evaluation,
            decent_appearance_evaluation,punctuality_evaluation,
            office_hours_evaluation,evaluation_sum,id))
            conn.commit()
            conn.close()
            flash('Data added successfully!', 'success')
            return redirect(url_for('view_person',id=id))

        conn = get_db_connection()

        # Admin can see all data
        ethics_responsibility = conn.execute('''
            SELECT ethics_responsibility.*, users.username, users.full_name 
            FROM ethics_responsibility 
            JOIN users ON ethics_responsibility.user_id = users.id
            WHERE ethics_responsibility.user_id = ?
            
        ''',(id,)).fetchone()
        conn.close()

        return render_template('admin/ethic_responsibility_evaluation.html',id=id, ethics_responsibility=ethics_responsibility)
    else:
        return render_template('page-404.html', error_msg='Page Not Found')


@app.route('/university_evaluation', methods=['GET', 'POST'])
@login_required
def university_evaluation():
    if request.method == 'POST':
        # Get form data
        data = {
            'user_id': session['user_id'],
            'department_load': request.form['department_load'],
            'workshop_develop': request.form['workshop_develop'],
            'program_bank': request.form['program_bank'],
            'medical_services': request.form['medical_services']
        }
        numeric_fields = [
         'department_load', 'workshop_develop', 'program_bank', 
        'medical_services'
           ]

        data['aspects_sum'] = sum(int(data[field]) for field in numeric_fields)
        try:
            # Insert into database
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO university_evaluation (
                    user_id, department_load, workshop_develop, program_bank,
                    medical_services,aspects_sum
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', tuple(data.values()))
            conn.commit()
        except:
            return render_template('page-404.html', error_msg=' لقد قمت بالتقييم بالفعل هذا العام ❌')
        finally:
            conn.close()

        return redirect(url_for('view_person',id=session['user_id']))

    return render_template('university_evaluation.html')



@app.route('/prticipation_add', methods=['GET', 'POST'])
@login_required
def prticipation_data():
    if request.method == 'POST':
        # Get form data
        data = {
            'user_id': session['user_id'],
            'location': request.form['location'],
            'type_part': request.form['type_part'],
            'place': request.form['place'],
            'year': request.form['year'],
        }

        # Insert into database
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO participate_conference (
                user_id, location, type_part, place, year
            ) VALUES (?, ?, ?, ?, ? )
        ''', tuple(data.values()))
        conn.commit()
        conn.close()

        flash('Data added successfully!', 'success')
        return redirect(url_for('view_person',id=session['user_id']))

    return render_template('Participation_in_conferences.html')

@app.route('/university', methods=['GET', 'POST'])
@login_required
def University_Service():
    if request.method == 'POST':
        # Get form data
        data = {
            'user_id': session['user_id'],
            'task_level': request.form['task_level'],
            'task_type': request.form['task_type'],
            'notes': request.form['notes'],
        }

        # Insert into database
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO University_Service (
                user_id, task_level, task_type, notes
            ) VALUES (?, ?, ?, ? )
        ''', tuple(data.values()))
        conn.commit()
        conn.close()

        flash('Data added successfully!', 'success')
        return redirect(url_for('view_person',id=session['user_id']))

    return render_template('University_Service.html')


@app.route('/activity_add', methods=['GET', 'POST'])
@login_required
def activity_data():
    if request.method == 'POST':
        # Get form data
        data = {
            'user_id': session['user_id'],
            'activity_title': request.form['activity_title'],
            'activity_date': request.form['date'],
            'duration': request.form['duration'],
            'participation_type': request.form['participation_type'],
            'place': request.form['place']
        }

        # Insert into database
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO activity_data (
                user_id, activity_title, activity_date, duration, participation_type, place
            ) VALUES (?, ?, ?, ?, ?, ? )
        ''', tuple(data.values()))
        conn.commit()
        conn.close()

        flash('Data added successfully!', 'success')
        return redirect(url_for('view_person',id=session['user_id']))

    return render_template('add_activity.html')



@app.route('/program_add', methods=['GET', 'POST'])
@login_required
def program_data():
    if request.method == 'POST':
        # Get form data
        data = {
            'user_id': session['user_id'],
            'scientific_output': request.form['scientific_output'],
            'Authors_names': request.form['Authors_names'],
            'Publisher': request.form['Publisher'],
            'Agency': request.form['Agency'],
            'year': request.form['year'],
            'research_type': request.form['research_type'],
            'DOI': request.form['DOI']
        }

        # Insert into database
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO Scientific_research (
                user_id, scientific_output, Authors_names, Publisher, Agency,
                year, research_type, DOI
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', tuple(data.values()))
        conn.commit()
        conn.close()

        flash('Data added successfully!', 'success')
        return redirect(url_for('view_person',id=session['user_id']))

    return render_template('add_program.html')

@app.route('/view')
@login_required
def view_data():
    conn = get_db_connection()
    
    if session.get('role') == 'admin':
        # Admin can see all data
        semseters = conn.execute('''
            SELECT academic_data.*, users.username, users.full_name 
            FROM academic_data 
            JOIN users ON academic_data.user_id = users.id
            ORDER BY academic_data.created_at DESC
        ''').fetchall()
        activity = conn.execute('''
            SELECT activity_data.*, users.username, users.full_name 
            FROM activity_data 
            JOIN users ON activity_data.user_id = users.id
            ORDER BY activity_data.created_at DESC
        ''').fetchall()
        
    else:
        # Regular users can only see their own data
        semseters = conn.execute('''
            SELECT academic_data.*, users.username, users.full_name 
            FROM academic_data 
            JOIN users ON academic_data.user_id = users.id
            WHERE academic_data.user_id = ?
            ORDER BY academic_data.created_at DESC
        ''', (session['user_id'],)).fetchall()

        activity = conn.execute('''
            SELECT activity_data.*, users.username, users.full_name 
            FROM activity_data 
            JOIN users ON activity_data.user_id = users.id
            WHERE activity_data.user_id = ?
            ORDER BY activity_data.created_at DESC
        ''', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('view_data.html', semseters=semseters,activity=activity)


@app.route('/view/Scientific_production')
@login_required
@admin_required
def view_Scientific_production():
    conn = get_db_connection()
    
    # Admin can see all data
    Scientific_production = conn.execute('''
        SELECT Scientific_production.*, users.username, users.full_name 
        FROM Scientific_production 
        JOIN users ON Scientific_production.user_id = users.id
        WHERE users.department = ?
        ORDER BY Scientific_production.created_at DESC
    ''', (session['department'],)).fetchall()

    conn.close()
    return render_template('view_data/view_Scientific_production.html', Scientific_production=Scientific_production)
 
@app.route('/view/criteria_of_evaluation')
@login_required
@admin_required
def view_criteria_of_evaluation():
    conn = get_db_connection()
    
    # Admin can see all data0
    Evaluation_aspects = conn.execute('''
        SELECT aspects_sum,evaluation_sum,user_id, users.username, users.full_name 
        FROM Evaluation_aspects 
        JOIN users ON Evaluation_aspects.user_id = users.id
        WHERE users.department = ?
        ORDER BY Evaluation_aspects.created_at DESC
    ''', (session['department'],)).fetchall()

    activity = conn.execute('''
        SELECT activity_data.*, users.username, users.full_name 
        FROM activity_data 
        JOIN users ON activity_data.user_id = users.id
        WHERE users.department = ?
        ORDER BY activity_data.created_at DESC
    ''' , (session['department'],)).fetchall()
        
    conn.close()
    return render_template('view_data/view_criteria.html', Evaluation_aspects=Evaluation_aspects,activity=activity)


@app.route('/view/university_evaluation')
@login_required
@admin_required
def view_university_evaluation():
    conn = get_db_connection()
    
    # Admin can see all data0
    
    university_evaluation = conn.execute('''
        SELECT aspects_sum,evaluation_sum,evaluation_year,user_id, users.username, users.full_name 
        FROM university_evaluation 
        JOIN users ON university_evaluation.user_id = users.id
        WHERE users.department = ?
        ORDER BY university_evaluation.created_at DESC
        
    ''', (session['department'],)).fetchall()
    conn.close()
    return render_template('view_data/view_university.html', university_evaluation=university_evaluation)

@app.route('/view/all_users')
@login_required
@admin_required
def view_all_users():
    conn = get_db_connection()
    department = request.args.get('department', 'All')
    if department == "All":
        # Admin can see all data0
        users = conn.execute('''
            SELECT id, username, department, full_name ,role
            FROM users 
            WHERE users.role = 'user' 
            ORDER BY users.department
        ''', ).fetchall()

        conn.close()
        
        return render_template('view_all_users.html', users=users)
    else:
            print(department)  
            try:
            # Admin can see all data0
                users = conn.execute('''
                    SELECT id, username, department, full_name ,role
                    FROM users 
                    WHERE users.department = ? AND users.role = 'user' 
                    ORDER BY users.id
                ''', (department,)).fetchall()

                conn.close()
                
                return render_template('view_all_users.html', users=users)
            except:
                return render_template('page-404.html', error_msg='لا يوجد هذا القسم ')


@app.route('/view/users')
@login_required
@admin_required
def view_users():
    conn = get_db_connection()
    # Admin can see all data0
    users = conn.execute('''
        SELECT id, username, department, full_name ,role
        FROM users 
        WHERE users.department = ? AND users.role = 'user' 
        ORDER BY users.id
        
    ''', (session['department'],)).fetchall()

    headusers = conn.execute('''
        SELECT id, username, department, full_name ,role
        FROM users 
        WHERE users.role = 'head' 
        ORDER BY users.id
        
    ''').fetchall()
    conn.close()
    print(users)
    return render_template('view_data/view_users.html', users=users,headusers=headusers)

@app.route('/view/persons13w4z6e7e5a4r76n<int:id>w46das5s4a6', methods=['GET', 'POST'])
@login_required
# @admin_required
def view_person(id):
    conn = get_db_connection()
    
    # Admin can see all data0

    user = conn.execute('''
        SELECT  department, full_name ,id
        FROM users 
        WHERE users.id = ? 
        
    ''', (id,)).fetchone()

    university_evaluation = conn.execute('''
            SELECT university_evaluation.*, users.username, users.full_name 
            FROM university_evaluation 
            JOIN users ON university_evaluation.user_id = users.id
            WHERE university_evaluation.user_id = ?
            
        ''',(id,)).fetchone()
    
    Evaluation_aspects = conn.execute('''
            SELECT Evaluation_aspects.*, users.username, users.full_name 
            FROM Evaluation_aspects 
            JOIN users ON Evaluation_aspects.user_id = users.id
            WHERE Evaluation_aspects.user_id = ?
            
        ''',(id,)).fetchone()
    
    Scientific_production = conn.execute('''
            SELECT Scientific_production.*, users.username, users.full_name 
            FROM Scientific_production 
            JOIN users ON Scientific_production.user_id = users.id
            WHERE Scientific_production.user_id = ?
            
        ''',(id,)).fetchone()
    
    semseters = conn.execute('''
            SELECT academic_data.*, users.username, users.full_name 
            FROM academic_data 
            JOIN users ON academic_data.user_id = users.id
            WHERE academic_data.user_id = ?
        ''', (id,)).fetchall()

    activity = conn.execute('''
        SELECT activity_data.*, users.username, users.full_name 
        FROM activity_data 
        JOIN users ON activity_data.user_id = users.id
        WHERE activity_data.user_id = ?
    ''', (id,)).fetchall()

    Scientific_research = conn.execute('''
        SELECT Scientific_research.*, users.username, users.full_name 
        FROM Scientific_research 
        JOIN users ON Scientific_research.user_id = users.id
        WHERE Scientific_research.user_id = ?
    ''', (id,)).fetchall()

   

    participate_conference = conn.execute('''
        SELECT participate_conference.*, users.username, users.full_name 
        FROM participate_conference 
        JOIN users ON participate_conference.user_id = users.id
        WHERE participate_conference.user_id = ?
    ''', (id,)).fetchall()
   

    conn.close()
    return render_template('view_data/profile.html', id=id,user=user, university_evaluation=university_evaluation,Scientific_production=Scientific_production,Evaluation_aspects=Evaluation_aspects
                          ,semseters=semseters, activity=activity,current_year=current_year,participate_conference=participate_conference,Scientific_research=Scientific_research )

@app.route('/update/university/<int:id>', methods=['GET', 'POST'])
@login_required
def update_university(id):
    if session.get('role') == 'admin' or session.get('role') == 'head':
        if request.method == 'POST':
            # Get form data 
            department_load_Evaluation = request.form['department_load_Evaluation']
            workshop_develop_Evaluation = request.form['workshop_develop_Evaluation']
            medical_services_Evaluation = request.form['medical_services_Evaluation']
            program_bank_Evaluation = request.form['program_bank_Evaluation']

            evaluation_fields = [
            'department_load_Evaluation',
            'workshop_develop_Evaluation',
            'medical_services_Evaluation',
            'program_bank_Evaluation'
             ]

            # Calculate sum with error handling
            try:
                evaluation_sum = sum(int(request.form[field]) for field in evaluation_fields)
            except ValueError as e:
                # Handle case where a value can't be converted to int
                evaluation_sum = 0  # or raise an exception
                print(f"Error converting form values: {e}")

            check_query = '''SELECT evaluation_sum FROM university_evaluation 
             WHERE user_id == ? and evaluation_year == ? '''
            # Insert into database
            conn = get_db_connection()
            cursor = conn.cursor()
            check = cursor.execute(check_query, (id,current_year)).fetchone()[0]
            if(check == None):
                update_query = ''' UPDATE university_evaluation SET department_load_Evaluation == ?,
                workshop_develop_Evaluation == ?, medical_services_Evaluation == ? ,
                program_bank_Evaluation == ?, evaluation_sum == ?
                WHERE university_evaluation.user_id == ? '''

                cursor.execute(update_query, (department_load_Evaluation,workshop_develop_Evaluation,
                medical_services_Evaluation,program_bank_Evaluation,evaluation_sum,id))
                conn.commit()
                conn.close()
            else:
                conn.close()
                return render_template('page-404.html', error_msg=' لقد قمت بالتقييم بالفعل هذا العام ❌')
            flash('Data added successfully!', 'success')
            return redirect(url_for('view_person',id=id))

        conn = get_db_connection()

        # Admin can see all data
        university_evaluation = conn.execute('''
            SELECT university_evaluation.*, users.username, users.full_name 
            FROM university_evaluation 
            JOIN users ON university_evaluation.user_id = users.id
            WHERE university_evaluation.user_id = ?
            ORDER BY university_evaluation.created_at DESC
        ''',(id,)).fetchone()
        conn.close()

        return render_template('admin/update_university.html',id=id, university_evaluation=university_evaluation)
    else:
         return render_template('page-404.html', error_msg='Page Not Found')




@app.route('/kpis')
@login_required
def view_kpis():
    conn = get_db_connection()
    department = request.args.get('department', 'All')
    try:
        if session.get('role') == 'admin' and department=="All" :
            # Admin can see all data
            academic_kpi = conn.execute(''' 
            SELECT COUNT(*)
            FROM academic_data
            ''').fetchone()
            activity_kpi = conn.execute(''' 
            SELECT COUNT(DISTINCT user_id)
            FROM  activity_data
            ''').fetchone()
            users = conn.execute(''' 
            SELECT COUNT(*)
            FROM  users
            WHERE role != 'admin'
            ''').fetchone()
            University_Service = conn.execute(''' 
            SELECT COUNT(*)
            FROM  University_Service
            ''').fetchone()
            # Admin can see all data

            activity = conn.execute('''
            SELECT activity_data.*, users.username, users.full_name 
            FROM activity_data 
            JOIN users ON activity_data.user_id = users.id
            ORDER BY activity_data.created_at DESC
            ''').fetchall()
            Scientific_research1 = conn.execute('''
            SELECT COUNT(*)
            FROM  Scientific_research
            WHERE research_type LIKE "%بحث%" AND Publisher LIKE "%مؤتمر%" ;
            ''').fetchone()

            Scientific_research2 = conn.execute('''
            SELECT COUNT(*)
            FROM  Scientific_research
            WHERE research_type LIKE "%بحث%" AND Publisher LIKE "%مجلة%" ;
            ''').fetchone()

            part_in_conf = conn.execute(''' 
            SELECT COUNT(DISTINCT user_id )
            FROM  participate_conference
            ''').fetchone()

            Evaluation_aspects = conn.execute(''' 
            SELECT SUM(evaluation_sum)
            FROM Evaluation_aspects
            ''').fetchone()

            university_evaluation = conn.execute(''' 
            SELECT SUM(evaluation_sum)
            FROM university_evaluation
            ''').fetchone()

            activity_percent = (activity_kpi[0]/(users[0]))*100
            research2_percent = (Scientific_research2[0]/(users[0]))*100
            research1_percent = (Scientific_research1[0]/(users[0]))*100
            conf_percent = (part_in_conf[0]/(users[0]))*100
            print(Evaluation_aspects[0])
            Evaluation_aspects_percent = (Evaluation_aspects[0]/(users[0]))
            university_evaluation_percent = (university_evaluation[0]/(users[0]))

            return render_template('view_kpis.html', academic_kpi=academic_kpi[0],activity_kpi=activity_kpi[0],
            activity_percent=int(activity_percent), University_Service=University_Service[0],
            Scientific_research1=Scientific_research1[0],Scientific_research2=Scientific_research2[0],
            research1_percent=int(research1_percent),research2_percent=int(research2_percent), conf_percent=int(conf_percent),
            Evaluation_aspects_percent=int(Evaluation_aspects_percent),university_evaluation_percent=int(university_evaluation_percent), department=department)
    
        elif session.get('role') == 'admin' and department != "All":
                # Admin can see all data
                academic_kpi = conn.execute(''' 
                SELECT COUNT(*)
                FROM academic_data
                JOIN users ON academic_data.user_id = users.id
                WHERE users.department = ?
                ''', (department,)).fetchone()
                activity_kpi = conn.execute(''' 
                SELECT COUNT(DISTINCT user_id)
                FROM  activity_data
                JOIN users ON activity_data.user_id = users.id
                WHERE users.department = ?                            
                ''', (department,)).fetchone()
                users = conn.execute(''' 
                SELECT COUNT(*)
                FROM  users
                WHERE role != 'admin' AND users.department = ?                            
                ''',(department,)).fetchone()
                University_Service = conn.execute(''' 
                SELECT COUNT(*)
                FROM  University_Service
                JOIN users ON University_Service.user_id = users.id
                WHERE users.department = ?                            
                ''', (department,)).fetchone()
                # Admin can see all data

                activity = conn.execute('''
                SELECT activity_data.*, users.username, users.full_name 
                FROM activity_data 
                JOIN users ON activity_data.user_id = users.id
                WHERE users.department = ?                               
                ORDER BY activity_data.created_at DESC
                ''', (department,)).fetchall()
                Scientific_research1 = conn.execute('''
                SELECT COUNT(*)
                FROM  Scientific_research
                JOIN users ON Scientific_research.user_id = users.id
                WHERE users.department = ? AND research_type LIKE "%بحث%" AND Publisher LIKE "%مؤتمر%" ;
                ''', (department,)).fetchone()

                Scientific_research2 = conn.execute('''
                SELECT COUNT(*)
                FROM  Scientific_research
                JOIN users ON Scientific_research.user_id = users.id
                WHERE users.department = ? AND research_type LIKE "%بحث%" AND Publisher LIKE "%مجلة%" ;
                ''', (department,)).fetchone()

                part_in_conf = conn.execute(''' 
                SELECT COUNT(DISTINCT user_id )
                FROM  participate_conference
                JOIN users ON participate_conference.user_id = users.id
                WHERE users.department = ? 
                ''', (department,)).fetchone()

                Evaluation_aspects = conn.execute(''' 
                SELECT SUM(evaluation_sum)
                FROM Evaluation_aspects
                JOIN users ON Evaluation_aspects.user_id = users.id
                WHERE users.department = ? 
                ''',(department,)).fetchone()

                university_evaluation = conn.execute(''' 
                SELECT SUM(evaluation_sum)
                FROM university_evaluation
                JOIN users ON university_evaluation.user_id = users.id
                WHERE users.department = ? 
                ''',(department,)).fetchone()

                print(activity_kpi[0])

                activity_percent = (activity_kpi[0]/(users[0]))*100
                research2_percent = (Scientific_research2[0]/(users[0]))*100
                research1_percent = (Scientific_research1[0]/(users[0]))*100
                conf_percent = (part_in_conf[0]/(users[0]))*100
                Evaluation_aspects_percent = (Evaluation_aspects[0]/(users[0]))
                university_evaluation_percent = (university_evaluation[0]/(users[0]))

                return render_template('view_kpis.html', academic_kpi=academic_kpi[0],activity_kpi=activity_kpi[0],
                activity_percent=int(activity_percent), University_Service=University_Service[0],
                Scientific_research1=Scientific_research1[0],Scientific_research2=Scientific_research2[0],
                research1_percent=int(research1_percent),research2_percent=int(research2_percent), conf_percent=int(conf_percent),
                Evaluation_aspects_percent=int(Evaluation_aspects_percent),university_evaluation_percent=int(university_evaluation_percent),department=department)

        
        elif session.get('role') == 'head'  :
                # Admin can see all data
                academic_kpi = conn.execute(''' 
                SELECT COUNT(*)
                FROM academic_data
                JOIN users ON academic_data.user_id = users.id
                WHERE users.department = ?
                ''', (session['department'],)).fetchone()
                activity_kpi = conn.execute(''' 
                SELECT COUNT(DISTINCT user_id)
                FROM  activity_data
                JOIN users ON activity_data.user_id = users.id
                WHERE users.department = ?                            
                ''', (session['department'],)).fetchone()
                users = conn.execute(''' 
                SELECT COUNT(*)
                FROM  users
                WHERE role != 'admin' AND users.department = ?                            
                ''', (session['department'],)).fetchone()
                University_Service = conn.execute(''' 
                SELECT COUNT(*)
                FROM  University_Service
                JOIN users ON University_Service.user_id = users.id
                WHERE users.department = ?                            
                ''', (session['department'],)).fetchone()
                # Admin can see all data

                activity = conn.execute('''
                SELECT activity_data.*, users.username, users.full_name 
                FROM activity_data 
                JOIN users ON activity_data.user_id = users.id
                WHERE users.department = ?                               
                ORDER BY activity_data.created_at DESC
                ''', (session['department'],)).fetchall()
                Scientific_research1 = conn.execute('''
                SELECT COUNT(*)
                FROM  Scientific_research
                JOIN users ON Scientific_research.user_id = users.id
                WHERE users.department = ? AND research_type LIKE "%بحث%" AND Publisher LIKE "%مؤتمر%" ;
                ''', (session['department'],)).fetchone()

                Scientific_research2 = conn.execute('''
                SELECT COUNT(*)
                FROM  Scientific_research
                JOIN users ON Scientific_research.user_id = users.id
                WHERE users.department = ? AND research_type LIKE "%بحث%" AND Publisher LIKE "%مجلة%" ;
                ''', (session['department'],)).fetchone()

                part_in_conf = conn.execute(''' 
                SELECT COUNT(DISTINCT user_id )
                FROM  participate_conference
                JOIN users ON participate_conference.user_id = users.id
                WHERE users.department = ? 
                ''', (session['department'],)).fetchone()

                Evaluation_aspects = conn.execute(''' 
                SELECT SUM(evaluation_sum)
                FROM Evaluation_aspects
                JOIN users ON Evaluation_aspects.user_id = users.id
                WHERE users.department = ? 
                ''', (session['department'],)).fetchone()

                university_evaluation = conn.execute(''' 
                SELECT SUM(evaluation_sum)
                FROM university_evaluation
                JOIN users ON university_evaluation.user_id = users.id
                WHERE users.department = ? 
                ''', (session['department'],)).fetchone()

                activity_percent = (activity_kpi[0]/(users[0]))*100
                research2_percent = (Scientific_research2[0]/(users[0]))*100
                research1_percent = (Scientific_research1[0]/(users[0]))*100
                conf_percent = (part_in_conf[0]/(users[0]))*100
                print(Evaluation_aspects[0])
                Evaluation_aspects_percent = (Evaluation_aspects[0]/(users[0]))
                university_evaluation_percent = (university_evaluation[0]/(users[0]))

                return render_template('view_kpis.html', academic_kpi=academic_kpi[0],activity_kpi=activity_kpi[0],
                activity_percent=int(activity_percent), University_Service=University_Service[0],
                Scientific_research1=Scientific_research1[0],Scientific_research2=Scientific_research2[0],
                research1_percent=int(research1_percent),research2_percent=int(research2_percent), conf_percent=int(conf_percent),
                Evaluation_aspects_percent=int(Evaluation_aspects_percent),university_evaluation_percent=int(university_evaluation_percent),department=session.get("department"))
    except:
        return render_template('view_kpis.html', activity=0)
    finally:
        conn.close()

@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    if session.get('role') == 'admin' or session.get('role') == 'head':
        if request.method == 'POST':
            # Get form data
            Scientific_research_Evaluation = request.form['Scientific_research_Evaluation']
            supervision_Graduation_Evaluation = request.form['supervision_Graduation_Evaluation']
            data = {
                'supervision_Graduation_Evaluation' : request.form['supervision_Graduation_Evaluation'],
                'user_id' : id
            }
            check_query = '''SELECT supervision_Graduation_Evaluation FROM Scientific_production 
             WHERE user_id == ? and evaluation_year == ? '''
            # Insert into database
            conn = get_db_connection()
            cursor = conn.cursor()
            check = cursor.execute(check_query, (id,current_year)).fetchone()[0]
            print(check)
            if (check == None):
                update_query = " UPDATE Scientific_production SET Scientific_research_Evaluation == ?, supervision_Graduation_Evaluation == ? WHERE Scientific_production.user_id == ? "
                cursor.execute(update_query, (Scientific_research_Evaluation,supervision_Graduation_Evaluation,id))
                conn.commit()
                conn.close()
            else:
                conn.close()
                return render_template('page-404.html', error_msg=' لقد قمت بالتقييم بالفعل هذا العام ❌')
            return redirect(url_for('view_person',id=id))

        conn = get_db_connection()

        # Admin can see all data
        Scientific_production = conn.execute('''
            SELECT Scientific_production.*, users.username, users.full_name 
            FROM Scientific_production 
            JOIN users ON Scientific_production.user_id = users.id
            WHERE Scientific_production.user_id = ?
            ORDER BY Scientific_production.created_at DESC
        ''',(id,)).fetchone()
        conn.close()

        return render_template('admin/update.html',id=id, Scientific_production=Scientific_production)
    else:
         return render_template('page-404.html', error_msg='Page Not Found')


@app.route('/update/criteria/<int:id>', methods=['GET', 'POST'])
@login_required
def update_criteria(id):
    if session.get('role') == 'head':
        if request.method == 'POST':
            # Get form data 
            Develop_courses_Evaluation = request.form['Develop_courses_Evaluation']
            Prepare_file_Evaluation = request.form['Prepare_file_Evaluation']
            Electronic_tests_Evaluation = request.form['Electronic_tests_Evaluation']
            Prepare_material_Evaluation = request.form['Prepare_material_Evaluation']
            Use_learning_Evaluation = request.form['Use_learning_Evaluation']
            teaching_methods_Evaluation = request.form['teaching_methods_Evaluation']
            Methods_student_Evaluation = request.form['Methods_student_Evaluation']
            preparing_test_Evaluation = request.form['preparing_test_Evaluation']
            Provide_academic_Evaluation = request.form['Provide_academic_Evaluation']

            evaluation_fields = [
            'Develop_courses_Evaluation',
            'Prepare_file_Evaluation',
            'Electronic_tests_Evaluation',
            'Prepare_material_Evaluation',
            'Use_learning_Evaluation',
            'teaching_methods_Evaluation',
            'Methods_student_Evaluation',
            'preparing_test_Evaluation',
            'Provide_academic_Evaluation'
             ]

            # Calculate sum with error handling
            try:
                evaluation_sum = sum(int(request.form[field]) for field in evaluation_fields)
            except ValueError as e:
                # Handle case where a value can't be converted to int
                evaluation_sum = 0  # or raise an exception
                print(f"Error converting form values: {e}")

            check_query = '''SELECT evaluation_sum FROM Evaluation_aspects 
             WHERE user_id == ? and evaluation_year == ? '''
            # Insert into database
            conn = get_db_connection()
            cursor = conn.cursor()
            check = cursor.execute(check_query, (id,current_year)).fetchone()[0]

            if(check == None):

                update_query = ''' UPDATE Evaluation_aspects SET Develop_courses_Evaluation == ?,
                Prepare_file_Evaluation == ?, Electronic_tests_Evaluation == ? ,
                Prepare_material_Evaluation == ?, Use_learning_Evaluation == ?,
                teaching_methods_Evaluation == ?, Methods_student_Evaluation == ?,
                preparing_test_Evaluation == ?, Provide_academic_Evaluation == ? , evaluation_sum == ?
                WHERE Evaluation_aspects.user_id == ? '''

                cursor.execute(update_query, (Develop_courses_Evaluation,Prepare_file_Evaluation,
                Electronic_tests_Evaluation,Prepare_material_Evaluation,
                Use_learning_Evaluation,teaching_methods_Evaluation,
                Methods_student_Evaluation,preparing_test_Evaluation,Provide_academic_Evaluation,evaluation_sum,id))
                conn.commit()
                conn.close()
            else:
                conn.close()
                return render_template('page-404.html', error_msg=' لقد قمت بالتقييم بالفعل هذا العام ❌')
            return redirect(url_for('view_person',id=id))

        conn = get_db_connection()

        # Admin can see all data
        Evaluation_aspects = conn.execute('''
            SELECT Evaluation_aspects.*, users.username, users.full_name 
            FROM Evaluation_aspects 
            JOIN users ON Evaluation_aspects.user_id = users.id
            WHERE Evaluation_aspects.user_id = ?
            ORDER BY Evaluation_aspects.created_at DESC
        ''',(id,)).fetchone()
        conn.close()

        return render_template('admin/criteria_of_evaluation.html',id=id, Evaluation_aspects=Evaluation_aspects)
    else:
         return render_template('page-404.html', error_msg='Page Not Found')



if __name__ == '__main__':
    app.run(debug=True)
