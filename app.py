# Rode com o comando: flask run

import sqlite3
import os
import re
import datetime
from flask import Flask, render_template, request, url_for, flash, redirect, Response, jsonify, send_from_directory
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_ngrok import run_with_ngrok


def get_db_connection():
    database_file = 'database.db'
    sql_file = 'schema.sql'

    # Caso banco de dados não exista
    if not os.path.exists(database_file):
        print(
            f"Base de dados não encontrada. Criando a partir do arquivo {sql_file}..."
        )
        # Conecta ao banco de dados em memória para executar o script SQL
        memconn = sqlite3.connect(':memory:')
        cursor = memconn.cursor()

        # Executa o script SQL do arquivo database.sql
        with open(sql_file, 'r') as file:
            sql_script = file.read()
            cursor.executescript(sql_script)

        # Conecta ao banco de dados em disco e faz o backup
        conn = sqlite3.connect(database_file)
        memconn.backup(conn)

        # Fecha a conexão com o banco de dados em memória
        memconn.close()

    # Caso o arquivo exista, conecta-se ao banco de dados
    else:
        conn = sqlite3.connect(database_file)

    conn.row_factory = sqlite3.Row
    return conn


def get_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM usuarios WHERE id = ?',
                        (user_id, )).fetchone()
    conn.close()
    if user is None:
        abort(404)
    return user


def get_noticia(noticia_id):
    conn = get_db_connection()
    noticia = conn.execute('SELECT * FROM noticias WHERE id = ?',
                           (noticia_id, )).fetchone()
    conn.close()
    if noticia is None:
        abort(404)
    return noticia


def get_cronograma(cronograma_id):
    conn = get_db_connection()
    cronograma = conn.execute('SELECT * FROM cronogramas WHERE id = ?',
                              (cronograma_id, )).fetchone()
    horarios = conn.execute('SELECT * FROM horarios WHERE id_cronograma = ?',
                            (cronograma_id, )).fetchall()
    retorno = {}

    for horario in horarios:
        retorno[f"{horario['dia']}_professor_{horario['horario']}"] = horario[
            'professor']
        retorno[f"{horario['dia']}_disciplina_{horario['horario']}"] = horario[
            'disciplina']

    retorno.update(cronograma)

    conn.close()
    if cronograma is None:
        abort(404)
    return retorno


def get_mapa(mapa_id):
    conn = get_db_connection()
    mapa = conn.execute('SELECT * FROM mapas WHERE id = ?',
                        (mapa_id, )).fetchone()
    conn.close()
    if mapa is None:
        abort(404)
    return mapa


def get_setor(setor_id):
    conn = get_db_connection()
    setor = conn.execute('SELECT * FROM setores WHERE id = ?',
                         (setor_id, )).fetchone()
    conn.close()
    if setor is None:
        abort(404)
    return setor


def get_evento(evento_id):
    conn = get_db_connection()
    evento = conn.execute('SELECT * FROM eventos WHERE id = ?',
                          (evento_id, )).fetchone()
    conn.close()
    if evento is None:
        abort(404)
    return evento


UPLOAD_FOLDER = 'C:\\Users\\ciros\\Downloads\\flask totem\\flask totem\\static\\imagens\\'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

#app.config['JSON_AS_ASCII'] = False

run_with_ngrok(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"


class User(UserMixin):

    def __init__(self, id, email, senha):
        self.id = id
        self.email = email
        self.senha = senha
        self.authenticated = False

    def is_active(self):
        return self.is_active()

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return True

    def get_id(self):
        return self.id


@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    curs = conn.cursor()
    curs.execute("SELECT * from usuarios where id = ?", (user_id, ))
    lu = curs.fetchone()
    if lu is None:
        return None
    else:
        return User(int(lu[0]), lu[1], lu[2])


# rotas para save cordenates


@app.route('/load-data', methods=['GET'])
def laod_data():
    conn = get_db_connection()
    coordenadas = conn.execute('SELECT x, y FROM coordenadas').fetchall()
    coordenadas = [dict(row) for row in coordenadas]
    conn.close()

    return jsonify(coordenadas)


@app.route('/save-data/<int:id_setor>', methods=['POST'])
@login_required
def save_data(id_setor):
    dados = request.get_json()
    x = dados['x']
    y = dados['y']

    conn = get_db_connection()
    conn.execute('UPDATE setores SET x = ?, y = ? WHERE id = ?',
                 (x, y, id_setor))
    conn.commit()
    conn.close()

    return jsonify(x, y)


@app.route('/delete-data', methods=['POST'])
@login_required
def delete_data():
    conn = get_db_connection()
    conn.execute('DELETE FROM coordenadas')
    conn.commit()
    conn.close()

    return 'Deletado'


# Rotas para Admin


@app.route('/login', methods=('GET', 'POST'))
def login():

    if current_user.is_authenticated:
        return redirect(url_for('index_noticias_admin'))

    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['password']

        conn = get_db_connection()
        user_email = conn.execute('SELECT email FROM usuarios WHERE email = ?',
                                  (email, )).fetchone()
        conn.commit()
        conn.close()

        if user_email:
            conn = get_db_connection()
            user_id = conn.execute('SELECT id FROM usuarios WHERE email = ?',
                                   (email, )).fetchone()[0]
            user_senha = conn.execute(
                'SELECT senha FROM usuarios WHERE email = ?',
                (email, )).fetchone()[0]
            conn.commit()
            conn.close()

            if bcrypt.check_password_hash(user_senha, senha):
                us = load_user(user_id)
                user = User(user_id, email, senha)
                login_user(us, remember=True)
                print('Logged in successfully ')
                return redirect(url_for('index_noticias_admin'))
            else:
                return redirect(url_for('login'))

        else:
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index_noticias'))


@app.route('/admin/register', methods=('GET', 'POST'))
@login_required
def register():

    if request.method == 'POST':
        email = request.form['email']
        nome = request.form['nome']
        senha = request.form['password']
        hashed_password = bcrypt.generate_password_hash(senha)

        conn = get_db_connection()
        users = conn.execute('SELECT email FROM usuarios WHERE email = ?',
                             (email, )).fetchall()
        conn.commit()
        conn.close()

        if not senha:
            flash('O campo senha é necessário!')
            return redirect(url_for('login'))
        else:
            if not users:
                conn = get_db_connection()
                conn.execute(
                    'INSERT INTO usuarios (email, nome, senha) VALUES (?, ?, ?)',
                    (email, nome, hashed_password))
                conn.commit()
                conn.close()
                return redirect(url_for('index_noticias_admin'))
            else:
                flash('Esse usuário já existe')
                return redirect(url_for('register'))

    return render_template('admin-create.html')


@app.route('/admin')
@login_required
def index_user():
    if current_user.is_authenticated:
        conn = get_db_connection()
        users = conn.execute(
            'SELECT * FROM usuarios ORDER BY nome ASC').fetchall()
        conn.close()
        return render_template('admin-profile.html', users=users)
    else:
        return redirect(url_for('login'))


@app.route('/admin/<int:user_id>')
@login_required
def user(user_id):
    user = get_user(user_id)
    return render_template('admin-profile.html', user=user)


@app.route('/admin/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit_user(id):
    user = get_user(id)

    if request.method == 'POST':
        email = request.form['email']
        nome = request.form['nome']
        senha = request.form['senha']

        if not email:
            flash('O email é necessário!')
        else:
            conn = get_db_connection()
            conn.execute(
                'UPDATE usuarios SET email = ?, nome = ?, senha = ?'
                ' WHERE id = ?', (email, nome, senha, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index_user'))

    return render_template('admin-edit.html', user=user)


@app.route('/admin/<int:id>/delete', methods=('POST', ))
@login_required
def delete_user(id):
    user = get_user(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM usuarios WHERE id = ?', (id, ))
    conn.commit()
    conn.close()
    flash('"{}" foi deletado com sucesso!'.format(user['nome']))
    return redirect(url_for('login'))


# Rotas para Noticias Admin


@app.route('/admin/noticias')
@login_required
def index_noticias_admin():
    if current_user.is_authenticated:
        conn = get_db_connection()
        noticias = conn.execute(
            'SELECT * FROM noticias ORDER BY created DESC').fetchall()
        conn.close()
        return render_template('noticia-preview-admin.html', noticias=noticias)
    else:
        return redirect(url_for('login'))


@app.route('/admin/noticias/<int:noticia_id>')
@login_required
def noticia_admin(noticia_id):
    noticia = get_noticia(noticia_id)
    return render_template('noticia-full-admin.html', noticia=noticia)


@app.route('/admin/noticias/create', methods=('GET', 'POST'))
@login_required
def create_noticia():
    if request.method == 'POST':
        title = request.form['title']
        autor = request.form['autor']
        content = request.form['content']
        url = request.form['url']
        fonte = request.form['fonte']

        if not title:
            flash('O Titulo é necessário!')
        else:
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO noticias (title, autor, content, url, fonte) VALUES (?, ?, ?, ?, ?)',
                (title, autor, content, url, fonte))
            conn.commit()
            conn.close()
            return redirect(url_for('index_noticias_admin'))

    return render_template('noticia-create.html')


@app.route('/admin/noticias/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit_noticia(id):
    noticia = get_noticia(id)

    if request.method == 'POST':
        title = request.form['title']
        autor = request.form['autor']
        content = request.form['content']
        url = request.form['url']
        fonte = request.form['fonte']

        if not title:
            flash('O Titulo é necessário!')
        else:
            conn = get_db_connection()
            conn.execute(
                'UPDATE noticias SET title = ?, autor = ?, content = ?, url = ?, fonte = ?'
                ' WHERE id = ?', (title, autor, content, url, fonte, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index_noticias_admin'))

    return render_template('noticia-edit.html', noticia=noticia)


@app.route('/admin/noticias/<int:id>/delete', methods=('POST', ))
@login_required
def delete_noticia(id):
    noticia = get_noticia(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM noticias WHERE id = ?', (id, ))
    conn.commit()
    conn.close()
    flash('"{}" foi deletado com sucesso!'.format(noticia['title']))
    return redirect(url_for('index_noticias_admin'))


# Rotas para Mapas Admin


@app.route('/admin/mapas')
@login_required
def index_mapas_admin():
    conn = get_db_connection()
    mapas = conn.execute('SELECT * FROM mapas').fetchall()
    conn.close()
    return render_template('mapa-preview-admin.html', mapas=mapas)


@app.route('/admin/mapas/<int:mapa_id>', methods=['GET', 'POST'])
@login_required
def mapa_admin(mapa_id):

    mapa = get_mapa(mapa_id)
    conn = get_db_connection()
    setores = conn.execute('SELECT * FROM setores WHERE id_mapa = ?',
                           (mapa_id, )).fetchall()
    conn.close()

    # Adicionar as rotas possíveis a partir dessa rota é uma das tarefas do controller
    links = {
        "noticias": "index_noticias_admin",
        "cronogramas": "index_cronogramas_admin",
        "mapas": "index_mapas_admin",
        "eventos": "index_eventos_admin",
        "setor": "setor_admin",
    }

    return render_template('setor-preview-admin.html',
                           mapa=mapa,
                           setores=setores,
                           links=links)


@app.route('/admin/mapas/create', methods=['GET', 'POST'])
@login_required
def create_mapa():
    if request.method == 'POST':
        title = request.form['title']
        url = request.form['url']
        if not title:
            flash('O Titulo é necessário!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO mapas (title, url) VALUES (?, ?)',
                         (title, url))
            conn.commit()
            conn.close()
            return redirect(url_for('index_mapas_admin'))

    return render_template("mapa-create.html")


@app.route('/admin/mapas/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit_mapa(id):
    mapa = get_mapa(id)

    if request.method == 'POST':
        title = request.form['title']
        url = request.form['url']

        if not title:
            flash('O Titulo é necessário!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE mapas SET title = ?, url = ?'
                         ' WHERE id = ?', (title, url, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index_mapas_admin'))

    return render_template('mapa-edit.html', mapa=mapa)


@app.route('/admin/mapas/<int:id>/delete', methods=('POST', ))
@login_required
def delete_mapa(id):
    mapa = get_mapa(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM mapas WHERE id = ?', (id, ))
    conn.commit()
    conn.close()
    flash('"{}" foi deletado com sucesso!'.format(mapa['title']))
    return redirect(url_for('index_mapas_admin'))


# Rotas para Setores Admin


@app.route('/admin/setores/<int:setor_id>')
@login_required
def setor_admin(setor_id):
    setor = get_setor(setor_id)
    return render_template('setor-full-admin.html', setor=setor)


@app.route('/admin/setores/create', methods=['GET', 'POST'])
@login_required
def create_setor():
    if request.method == 'POST':
        title = request.form['title']
        id_mapa = request.form['id_mapa']
        descricao = request.form['descricao']
        url = request.form['url']

        if not title:
            flash('O Titulo é necessário!')
        else:
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO setores (title, id_mapa, descricao, url) VALUES (?, ?, ?, ?)',
                (title, id_mapa, descricao, url))
            conn.commit()
            conn.close()
            return redirect(url_for('mapa_admin', mapa_id=id_mapa))

    return render_template("setor-create.html")


@app.route('/admin/setores/create/<int:id>', methods=['GET', 'POST'])
@login_required
def create_setor_id(id):
    if request.method == 'POST':
        title = request.form['title']
        id_mapa = id
        descricao = request.form['descricao']
        url = request.form['url']

        if not title:
            flash('O Titulo é necessário!')
        else:
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO setores (title, id_mapa, descricao, url) VALUES (?, ?, ?, ?)',
                (title, id_mapa, descricao, url))
            conn.commit()
            conn.close()
            return redirect(url_for('create_setor_id', id=id))

    return render_template("setor-create.html")


@app.route('/admin/setores/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit_setor(id):
    setor = get_setor(id)

    if request.method == 'POST':
        title = request.form['title']
        id_mapa = request.form['id_mapa']
        descricao = request.form['descricao']
        url = request.form['url']

        if not title:
            flash('O Titulo é necessário!')
        else:
            conn = get_db_connection()
            conn.execute(
                'UPDATE setores SET title = ?, id_mapa = ?, descricao = ?, url = ?'
                ' WHERE id = ?', (title, id_mapa, descricao, url, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index_mapas_admin'))

    return render_template('setor-edit.html', setor=setor)


@app.route('/admin/setores/<int:id>/delete', methods=('POST', ))
@login_required
def delete_setor(id):
    setor = get_setor(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM setores WHERE id = ?', (id, ))
    conn.commit()
    conn.close()
    flash('"{}" foi deletado com sucesso!'.format(setor['title']))
    return redirect(url_for('index_mapas_admin'))


# Rotas para Cronogramas Admin


@app.route('/admin/cronogramas')
@login_required
def index_cronogramas_admin():
    conn = get_db_connection()
    cronogramas = conn.execute(
        'SELECT * FROM cronogramas ORDER BY turma ASC').fetchall()

    dia = datetime.datetime.today().weekday()
    dias = ['seg', 'ter', 'qua', 'qui', 'sex', 'sab', 'dom']
    horarios = {}

    for cronograma in cronogramas:
        horarios[cronograma['id']] = get_cronograma(cronograma['id'])

    conn.close()
    return render_template('cronograma-preview-admin.html',
                           cronogramas=cronogramas,
                           horarios=horarios,
                           dia=dias[dia])


@app.route('/admin/cronogramas/<int:cronograma_id>')
@login_required
def cronograma_admin(cronograma_id):
    cronograma = get_cronograma(cronograma_id)
    print(cronograma)
    return render_template('cronograma-full-admin.html', cronograma=cronograma)


@app.route('/admin/cronogramas/create', methods=('GET', 'POST'))
@login_required
def create_cronograma():
    if request.method == 'POST':
        dados = request.get_json()
        section = dados['section']
        turma = dados.get('turma')

        if not turma:
            flash('A Turma é necessário!')
        else:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                'INSERT INTO cronogramas (section, turma) VALUES (?, ?)',
                (section, turma))
            id_cronograma = cur.lastrowid

            for dado in dados:
                match = re.search("([^_]+)_([^_]+)_(\d+)", dado)

                if (match):
                    if (match.group(2) == 'professor'):
                        cur.execute(
                            'INSERT INTO horarios (id_cronograma, horario, dia, professor) VALUES (?, ?, ?, ?) ON CONFLICT DO UPDATE SET professor = excluded.professor',
                            (id_cronograma, match.group(3), match.group(1),
                             dados[dado]))
                    else:
                        cur.execute(
                            'INSERT INTO horarios (id_cronograma, horario, dia, disciplina) VALUES (?, ?, ?, ?) ON CONFLICT DO UPDATE SET disciplina = excluded.disciplina',
                            (id_cronograma, match.group(3), match.group(1),
                             dados[dado]))

            conn.commit()
            conn.close()
            return redirect(url_for('index_cronogramas_admin'))

    dias = {
        'seg': "Segunda",
        'ter': "Terça",
        'qua': "Quarta",
        'qui': "Quinta",
        'sex': "Sexta",
        'sab': "Sábado"
    }
    horarios = range(1, 11)
    return render_template('cronograma-create.html',
                           dias=dias,
                           horarios=horarios)


@app.route('/admin/cronogramas/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit_cronograma(id):
    cronograma = get_cronograma(id)

    if request.method == 'POST':
        print(request)
        dados = request.get_json()
        section = dados['section']
        turma = dados.get('turma')

        if not turma:
            flash('A Turma é necessária!')
        else:
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute('DELETE FROM horarios WHERE id_cronograma = ?', (id, ))

            for dado in dados:
                match = re.search("([^_]+)_([^_]+)_(\d+)", dado)

                if (match):
                    if (match.group(2) == 'professor'):
                        cur.execute(
                            'INSERT INTO horarios (id_cronograma, horario, dia, professor) VALUES (?, ?, ?, ?) ON CONFLICT DO UPDATE SET professor = excluded.professor',
                            (id, match.group(3), match.group(1), dados[dado]))
                    else:
                        cur.execute(
                            'INSERT INTO horarios (id_cronograma, horario, dia, disciplina) VALUES (?, ?, ?, ?) ON CONFLICT DO UPDATE SET disciplina = excluded.disciplina',
                            (id, match.group(3), match.group(1), dados[dado]))

            conn.commit()
            conn.close()
            return redirect(url_for('index_cronogramas_admin'))

    dias = {
        'seg': "Segunda",
        'ter': "Terça",
        'qua': "Quarta",
        'qui': "Quinta",
        'sex': "Sexta",
        'sab': "Sábado"
    }
    print(cronograma)
    horarios = range(1, 11)
    return render_template('cronograma-edit.html',
                           cronograma=cronograma,
                           dias=dias,
                           horarios=horarios)


@app.route('/admin/cronogramas/<int:id>/delete', methods=('POST', ))
@login_required
def delete_cronograma(id):
    cronograma = get_cronograma(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM cronogramas WHERE id = ?', (id, ))
    conn.execute('DELETE FROM horarios WHERE id_cronograma = ?', (id, ))
    conn.commit()
    conn.close()
    flash('"{}" foi deletado com sucesso!'.format(cronograma['turma']))
    return redirect(url_for('index_cronogramas_admin'))


# Rotas para Eventos Admin


@app.route('/admin/eventos')
@login_required
def index_eventos_admin():
    conn = get_db_connection()
    eventos = conn.execute(
        'SELECT * FROM eventos ORDER BY data DESC').fetchall()
    conn.close()
    return render_template('evento-preview-admin.html', eventos=eventos)


@app.route('/admin/eventos/<int:evento_id>')
@login_required
def evento_admin(evento_id):
    evento = get_setor(evento_id)
    return render_template('evento-full.html', evento=evento)


@app.route('/admin/eventos/create', methods=['GET', 'POST'])
@login_required
def create_evento():
    if request.method == 'POST':
        title = request.form['title']
        autor = request.form['autor']
        data = request.form['data']
        descricao = request.form['descricao']
        local = request.form['local']

        if not title:
            flash('O Titulo é necessário!')
        else:
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO eventos (title, autor, data, descricao, local) VALUES (?, ?, ?, ?, ?)',
                (title, autor, data, descricao, local))
            conn.commit()
            conn.close()
            return redirect(url_for('index_eventos_admin'))

    return render_template("evento-create.html")


@app.route('/admin/eventos/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit_evento(id):
    evento = get_evento(id)

    if request.method == 'POST':
        title = request.form['title']
        autor = request.form['autor']
        data = request.form['data']
        descricao = request.form['descricao']
        local = request.form['local']

        if not title:
            flash('O Titulo é necessário!')
        else:
            conn = get_db_connection()
            conn.execute(
                'UPDATE eventos SET title = ?, autor = ?, data = ?, descricao = ?, local = ?'
                ' WHERE id = ?', (title, autor, data, descricao, local, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index_eventos_admin'))

    return render_template('evento-edit.html', evento=evento)


@app.route('/admin/eventos/<int:id>/delete', methods=('POST', ))
@login_required
def delete_evento(id):
    evento = get_evento(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM eventos WHERE id = ?', (id, ))
    conn.commit()
    conn.close()
    flash('"{}" foi deletado com sucesso!'.format(evento['title']))
    return redirect(url_for('index_eventos_admin'))


# Rotas para Uploads Admin


@app.route('/admin/uploads', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print('sucesso no upload')
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    return render_template('upload.html')


@app.route('/admin/uploads/arquivos', methods=["GET"])
@login_required
def index_arquivos():
    arquivos = []

    for nome_arquivo in os.listdir(UPLOAD_FOLDER):
        endereco_arquivo = os.path.join(UPLOAD_FOLDER, nome_arquivo)

        if (os.path.isfile(endereco_arquivo)):
            arquivos.append(nome_arquivo)

    return render_template('uploaded-files.html', arquivos=arquivos)


@app.route('/admin/uploads/<name>', methods=["GET"])
@login_required
def get_arquivo(name):
    return send_from_directory(UPLOAD_FOLDER, name, as_attachment=True)


@app.route('/admin/uploads/<name>/delete', methods=["GET"])
@login_required
def delete_arquivo(name):
    os.remove(UPLOAD_FOLDER + name)
    print('arquivo deletado com sucesso')
    return redirect(url_for('index_arquivos'))


# Rotas para Noticias Public


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/noticias')
def index_noticias():
    conn = get_db_connection()
    noticias = conn.execute(
        'SELECT * FROM noticias ORDER BY created DESC').fetchall()
    conn.close()
    return render_template('noticia-preview.html', noticias=noticias)


@app.route('/noticias/<int:noticia_id>')
def noticia(noticia_id):
    noticia = get_noticia(noticia_id)
    return render_template('noticia-full.html', noticia=noticia)


# Rotas para Cronogramas Public


@app.route('/cronogramas')
def index_cronogramas():
    conn = get_db_connection()
    cronogramas = conn.execute(
        'SELECT * FROM cronogramas ORDER BY turma ASC').fetchall()

    dia = datetime.datetime.today().weekday()
    dias = ['seg', 'ter', 'qua', 'qui', 'sex', 'sab', 'dom']
    horarios = {}

    for cronograma in cronogramas:
        horarios[cronograma['id']] = get_cronograma(cronograma['id'])

    # horarios = conn.execute('SELECT * FROM horarios WHERE dia = ?', (dias[dia],)).fetchall()

    # def keys(horario):
    #     return [f"{horario['id_cronograma']}_professor_{horario['horario']}", f"{horario['id_cronograma']}_disciplina_{horario['horario']}"]

    # def values(horario):
    #     return [horario['professor'], horario['disciplina']]

    # chaves = [item for sublist in map(keys, horarios) for item in sublist]
    # valores = [item for sublist in map(values, horarios) for item in sublist]

    # print(dict(zip(chaves, valores)))

    conn.close()
    return render_template('cronograma-preview.html',
                           cronogramas=cronogramas,
                           horarios=horarios,
                           dia=dias[dia])


@app.route('/cronogramas/<int:cronograma_id>')
def cronograma(cronograma_id):
    cronograma = get_cronograma(cronograma_id)
    dias = {
        'seg': "Segunda",
        'ter': "Terça",
        'qua': "Quarta",
        'qui': "Quinta",
        'sex': "Sexta",
        'sab': "Sábado"
    }
    horarios = range(1, 11)

    return render_template('cronograma-full.html',
                           cronograma=cronograma,
                           dias=dias,
                           horarios=horarios)


# Rotas para Mapas Public


@app.route('/mapas')
def index_mapas():
    conn = get_db_connection()
    mapas = conn.execute('SELECT * FROM mapas').fetchall()
    conn.close()
    return render_template('mapa-preview.html', mapas=mapas)


@app.route('/mapas/<int:mapa_id>')
def mapa(mapa_id):
    mapa = get_mapa(mapa_id)
    conn = get_db_connection()
    setores = conn.execute('SELECT * FROM setores WHERE id_mapa = ?',
                           (mapa_id, )).fetchall()

    # Adicionar as rotas possíveis a partir dessa rota é uma das tarefas do controller
    links = {
        "noticias": "index_noticias",
        "cronogramas": "index_cronogramas",
        "mapas": "index_mapas",
        "eventos": "index_eventos",
        "setor": "setor",
    }

    conn.close()
    return render_template('setor-preview-admin.html',
                           mapa=mapa,
                           setores=setores,
                           links=links)


@app.route('/setores/<int:setor_id>')
def setor(setor_id):
    setor = get_setor(setor_id)
    return render_template('setor-full.html', setor=setor)


# Rotas para Eventos Public


@app.route('/eventos')
def index_eventos():
    conn = get_db_connection()
    eventos = conn.execute(
        'SELECT * FROM eventos ORDER BY data DESC').fetchall()
    conn.close()
    return render_template('evento-preview.html', eventos=eventos)


@app.route('/eventos/<int:evento_id>')
def evento(evento_id):
    evento = get_setor(evento_id)
    return render_template('evento-full.html', evento=evento)
