from flask import Flask, request, escape
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt (app)

pw_hash = bcrypt.generate_password_hash('abc123')
bcrypt.check_password_hash(pw_hash, 'abc123')
print(pw_hash)

@app.route('/')
def hello():
    return 'Hello, World!'


@app.route('/greet')
def greet():
    name = request.args['name']
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title></title>
    </head>
    <body>
        <h1>Hi {}</h1>
    </body>
    </html>'''.format(escape(name))
