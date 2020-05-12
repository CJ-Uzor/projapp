from app import app

@app.route('/')
@app.route('/index')
def index():
    return '<p>Hello <strong>Micro-Proj-App</strong></p>'