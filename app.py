import os
from flask import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aviation_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

aircrafts = [
    {
        'model': 'F-22 Raptor',
        'image': 'uploads/f22.jpg',
        'specs': ['Top Speed: Mach 2.25', 'Role: Air Superiority'],
        'branch': 'US Air Force'
    }
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add', methods=['GET', 'POST'])
def add_plane_page():
    session.setdefault('errors', {})
    session.setdefault('form_data', {})

    if request.method == 'POST':
        errors = {}
        form_data = request.form.to_dict()
        uploaded_file = request.files.get('image')

        if not form_data.get('model'):
            errors['model'] = "Model designation is required."
        if not form_data.get('specs'):
            errors['specs'] = "Specifications are required."
        
        if not uploaded_file or uploaded_file.filename == '':
            errors['image'] = 'No image selected.'
        elif not allowed_file(uploaded_file.filename):
            errors['image'] = 'Invalid file type.'

        if errors:
            session['errors'] = errors
            session['form_data'] = form_data
            return redirect(url_for('add_plane_page'))
        
        filename = uploaded_file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        uploaded_file.save(filepath)

        new_entry = {
            'model': form_data['model'].strip(),
            'image': f'uploads/{filename}',
            'specs': [s.strip() for s in form_data['specs'].splitlines() if s.strip()],
            'branch': form_data.get('branch', '').strip()
        }
        aircrafts.append(new_entry)
        
        session.pop('errors', None)
        session.pop('form_data', None)
        return redirect(url_for('add_plane_page'))

    context_errors = session.pop('errors', {})
    context_data = session.pop('form_data', {})
    return render_template('add_plane.html', aircrafts=aircrafts, errors=context_errors, form_data=context_data)

@app.route('/delete', methods=['GET', 'POST'])
def delete_plane_page():
    global aircrafts
    if request.method == 'POST':
        indices = request.form.getlist('aircraft_to_delete')
        for index in sorted([int(i) for i in indices], reverse=True):
            if 0 <= index < len(aircrafts):
                del aircrafts[index]
        return redirect(url_for('delete_plane_page'))

    return render_template('delete_plane.html', aircrafts=aircrafts)

if __name__ == '__main__':
    app.run(debug=True)