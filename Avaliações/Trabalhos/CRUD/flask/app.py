from flask import *
from flask_session import Session
import sqlite3
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)
app.secret_key = 'chave_secreta'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

s = URLSafeTimedSerializer(app.secret_key)

def init_db():
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# Funções CRUD

def salvar_usuario(login, senha):
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    
    cursor.execute('INSERT INTO usuarios (login, senha) VALUES (?, ?)', (login, senha))
    
    conn.commit()
    conn.close()

def carregar_usuarios():
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT login, senha FROM usuarios')
    usuarios = {row[0]: row[1] for row in cursor.fetchall()}
    
    conn.close()
    return usuarios

def usuario_existe(login, senha):
    login = login.strip()
    senha = senha.strip()
    
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, login, senha FROM usuarios WHERE login = ? AND senha = ?', (login, senha))
    usuario = cursor.fetchone()
    
    conn.close()
    
    if usuario:
        print("Usuário encontrado:", usuario)
        return {"id": usuario[0], "login": usuario[1], "senha": usuario[2]}
    else:
        print(f"Nenhum usuário encontrado com o login: '{login}' e senha: '{senha}'")
        return None

def debug_usuarios():
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, login, senha FROM usuarios')
    usuarios = cursor.fetchall()
    
    conn.close()
    return usuarios

def salvar_chamada(nome, usuario_id):
    pass

def carregar_chamada():
    return {}

def deletar_chamada(chamada_id):
    pass

chamada = carregar_chamada()

# Rotas
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('login')
        senha = request.form.get('senha')
        usuario = usuario_existe(login, senha)
        if not usuario:
            return render_template("login.html", error="Usuário ou senha incorretos!")
        else:
            token = s.dumps(login, salt='login-token')
            return redirect(f"/?token={token}")
    return render_template("login.html")

@app.route("/logout")
def logout():
    if 'username' not in session:
        print('Usuário não mais logado')
    else:
        session.pop('username', None)
    return redirect("/about")

@app.route("/delete", methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
        print("Conteúdo do request.form:", request.form)
        
        login = request.form.get('login')
        senha = request.form.get('senha')
        
        if login is None or senha is None:
            print(f"Login ou senha não foram fornecidos: Login='{login}', Senha='{senha}'")
            return render_template("delete.html", error="Login ou senha não fornecidos!")
        
        login = login.strip()
        senha = senha.strip()
        
        print(f"Dados recebidos - Login: '{login}', Senha: '{senha}'")
        
        usuario = usuario_existe(login, senha)
        
        if not usuario:
            print('USER', usuario)
            print('Usuário ou senha incorretos!')
            return render_template("delete.html", error="Usuário ou senha incorretos!")
        
        if 'username' in session and session['username'] == usuario['login']:
            user_id = usuario['id']
            
            conn = sqlite3.connect('banco.db')
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM usuarios WHERE id = ? AND login = ? AND senha = ?', (user_id, login, senha))
            
            cursor.execute('UPDATE sqlite_sequence SET seq = seq - 1 WHERE name = "usuarios"')
            
            conn.commit()
            conn.close()
            
            session.pop('username', None)
            print('Usuário deletado com sucesso!')
            return redirect("/login")
        else:
            print('Você não está logado ou não tem permissão para deletar este usuário!')
            return render_template("delete.html", error="Você não está logado ou não tem permissão para deletar este usuário!")
    
    return render_template("delete.html")

@app.route("/cadastro", methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        login = request.form.get('login')
        senha = request.form.get('senha')
        if not usuario_existe(login, senha):
            salvar_usuario(login, senha)
            return redirect("/")
        else:
            return "Usuário já existe!", 400
    return render_template("cadastro.html")

@app.route("/", methods=['GET', 'POST'])
def index():
    token = request.args.get('token')
    if token:
        try:
            login = s.loads(token, salt='login-token', max_age=3600)
            session['username'] = login
        except:
            return redirect("/login")
    if not 'username' in session:
        return redirect("/login")
        print('Usuário não logado')
    Planeta = 'Saturno'
    username = session.get('username', '')
    users = ['Bob', 'Alice', 'John']
    return render_template("index.html", Planeta=Planeta, username=username, users=users)

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)
