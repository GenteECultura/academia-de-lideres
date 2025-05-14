from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
import requests
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'sua_chave_secreta_aqui')

# Configurações do Xano
XANO_BASE_URL = "https://xidg-u2cu-sa8e.n7c.xano.io/api:sojjGI-P"
XANO_API_KEY = "eyJhbGciOiJBMjU2S1ciLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwiemlwIjoiREVGIn0.vJuNda57rFNXqTjzBH7x2QyvcStL9QKDU6iGL1mApxrgUywVpUbYQycNczDgLS-j7NJCTFf2eKAzr___mXTicm6eAd8hENoE.Y4lNJAKMA_17gPNJmEU9Kw.A_zMNLNF6gbSkHnRY7T1pJR_sKzqNxcwEAtFQhct_xb1XaN67X-42EBRtBm0qXjgkm1l2v7pBpRLGDbSx34o27Zzn9j0xxeb5AzfThXi5Y3MKDfbgdIIKvLDrx8DITgKrh6c97DdTqdwEpl0sWCx0g.SBkgAuEabfJ5DqoVLay-pZszw3k9fAChzX1bosA3rbo"

# Mapeamento de tabelas amigáveis
XANO_TABLES = {
    'users': 'usuarios',
    'forum_post': 'forum_post',
    'projects': 'projetos',
    'student_disciplines': 'aluno_disciplinas',
    'professor_disciplines': 'professor_disciplinas'
}

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_id, username, role, name=None):
        self.id = user_id
        self.username = username
        self.role = role
        self.name = name

# Função genérica para requisição ao Xano
def xano_request(endpoint, method='GET', data=None, params=None, token=None):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token or XANO_API_KEY}"
    }
    url = f"{XANO_BASE_URL}/{endpoint}"
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError("Método HTTP não suportado")

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro Xano: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Falha na requisição ao Xano: {str(e)}")
        return None

@login_manager.user_loader
def load_user(user_id):
    user_data = xano_request(f"{XANO_TABLES['users']}/{user_id}")
    if user_data:
        return User(
            user_id=user_data.get('id'),
            username=user_data.get('username'),
            role=user_data.get('role'),
            name=user_data.get('name')
        )
    return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/notas")
def notas():
    # Simulação de dados vindos de projetos com notas
    projetos_com_notas = []  # Ex: [{'nome': 'Projeto 1', 'nota': 85}, {'nome': 'Projeto 2', 'nota': 92}]

    return render_template("notas.html", projetos_com_notas=projetos_com_notas)



@app.route('/enter')
def enter():
    return redirect(url_for('login'))

def redirect_to_dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('user_dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect_to_dashboard()

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('Preencha todos os campos', 'error')
            return redirect(url_for('login'))

        try:
            # Autenticação com Xano
            auth_response = xano_request('auth/login', method='POST', data={
                "username": username,
                "password": password
            })

            if not auth_response or 'authToken' not in auth_response:
                flash('Usuário ou senha incorretos', 'error')
                return redirect(url_for('login'))

            token = auth_response['authToken']

            # Buscar dados do usuário autenticado
            me_data = xano_request('auth/me', token=token)

            if not me_data or 'id' not in me_data:
                flash('Erro ao buscar dados do usuário autenticado', 'error')
                return redirect(url_for('login'))

            user = User(
                user_id=me_data['id'],
                username=me_data['username'],
                role=me_data.get('role', 'user'),
                name=me_data.get('name')
            )

            login_user(user)
            return redirect_to_dashboard()

        except Exception as e:
            print(f"ERRO no login: {str(e)}")
            flash('Erro durante o login. Tente novamente.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/user/dashboard')
@login_required
def user_dashboard():
    nome_usuario = current_user.name or current_user.username
    foto_usuario = url_for('static', filename='assets/images/foto_padrao.png')

    # Buscar projetos do usuário no Xano
    projetos = xano_request("projetos", params={"aluno_id": current_user.id}) or []

    qtd_projetos = len(projetos)

    # Calcular média das notas, apenas se existirem projetos com nota
    notas = [p.get("nota") for p in projetos if p.get("nota") is not None]
    media_notas = round(sum(notas) / len(notas), 1) if notas else None

    return render_template(
        'user_dashboard.html',
        nome_usuario=nome_usuario,
        foto_usuario=foto_usuario,
        qtd_projetos=qtd_projetos,
        media_notas=media_notas
    )



@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('user_dashboard'))
    all_users = xano_request(XANO_TABLES['users'])
    return render_template('admin_dashboard.html', users=all_users)

@app.route('/forum')
@login_required
def forum():
    posts = xano_request(XANO_TABLES['forum_post'])
    return render_template("forum.html", postagens=posts)

@app.route('/postar', methods=['POST'])
@login_required
def postar():
    texto = request.form.get('texto')
    imagem = request.files.get('imagem')

    imagem_url = None
    if imagem:
        imagem_url = f"https://meu-servidor.com/uploads/{imagem.filename}"

    data = {
        "autor_id": current_user.id,
        "autor_nome": current_user.name,
        "autor_foto": url_for('static', filename='assets/images/foto_padrao.png'),
        "texto": texto,
        "imagem_url": imagem_url,
        "curtidas": 0
    }

    xano_request(XANO_TABLES['forum_post'], method='POST', data=data)
    return redirect(url_for('forum'))

@app.route('/curtir/<int:post_id>', methods=['POST'])
@login_required
def curtir(post_id):
    post = xano_request(f"{XANO_TABLES['forum_post']}/{post_id}")
    if post:
        novas_curtidas = post.get("curtidas", 0) + 1
        xano_request(f"{XANO_TABLES['forum_post']}/{post_id}", method="PUT", data={"curtidas": novas_curtidas})
    return redirect(url_for('forum'))
@app.route('/meus_projetos')
@login_required
def meus_projetos():
    projetos = xano_request("projetos", params={"aluno_id": current_user.id})
    if projetos is None:
        projetos = []  # Garante que seja iterável no Jinja
    return render_template("meus_projetos.html", projetos=projetos)
@app.route('/admin/projetos')
@login_required
def admin_projetos():
    if current_user.role != 'admin':
        return redirect(url_for('user_dashboard'))
    
    todos_projetos = xano_request(XANO_TABLES['projects'])
    return render_template('corrigir_projetos.html', projetos=todos_projetos)

@app.route('/download/<int:projeto_id>')
@login_required
def download_projeto(projeto_id):
    projeto = xano_request(f"projetos/{projeto_id}")
    if not projeto:
        return "Projeto não encontrado", 404

    file_url = projeto.get('arquivo_url')  # campo que armazena o link do arquivo no Xano
    if not file_url:
        return "Arquivo não encontrado", 404

    return redirect(file_url)



@app.route('/admin/projetos/<int:projeto_id>/corrigir', methods=['POST'])
@login_required
def corrigir_projeto(projeto_id):
    if current_user.role != 'admin':
        return redirect(url_for('user_dashboard'))

    novo_status = request.form.get('status')
    comentario = request.form.get('comentario')

    dados = {
        "status": novo_status,
        "comentario_admin": comentario
    }

    xano_request(f"{XANO_TABLES['projects']}/{projeto_id}", method="PUT", data=dados)
    return redirect(url_for('admin_projetos'))
@app.route('/admin/corrigir_projetos')
@login_required
def corrigir_projetos():
    if current_user.role != 'admin':
        return redirect(url_for('user_dashboard'))
    
    projetos = xano_request('projetos') or []  # pega todos os projetos
    return render_template('corrigir_projetos.html', projetos=projetos)

@app.route('/admin/corrigir_projeto/<int:projeto_id>', methods=['POST'])
@login_required
def corrigir_projeto_action(projeto_id):
    if current_user.role != 'admin':
        return redirect(url_for('user_dashboard'))

    novo_status = request.form.get('status')
    status_texto = "Corrigido" if novo_status == "aprovado" else "Reprovado"
    
    # Atualiza o projeto no Xano
    xano_request(f'projetos/{projeto_id}', method='PUT', data={
        "status_correcao": True,
        "comentario_correcao": status_texto
    })

    flash(f"Projeto {status_texto.lower()} com sucesso!", "success")
    return redirect(url_for('corrigir_projetos'))


UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Garante que o diretório exista
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/enviar_projeto', methods=['GET', 'POST'])
@login_required
def enviar_projeto():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        descricao = request.form.get('descricao')
        arquivo = request.files.get('arquivo')

        # Verifica se o arquivo foi enviado
        arquivo_url = None
        if arquivo:
            filename = secure_filename(arquivo.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Garante que o diretório existe
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

            arquivo.save(save_path)

        # Cria o projeto no Xano (sem o arquivo_url inicialmente)
        projeto_data = {
            "aluno_id": current_user.id,
            "titulo": titulo,
            "descricao": descricao,
            "arquivo_url": "",  # Temporário
            "status": "Pendente"
        }

        response = xano_request("projetos", method='POST', data=projeto_data)

        if response and 'id' in response:
            projeto_id = response['id']

            # Gera a URL do arquivo com base no projeto_id
            arquivo_url = url_for('download_projeto', projeto_id=projeto_id, _external=True)

            # Atualiza o projeto com o campo arquivo_url real
            xano_request(f"projetos/{projeto_id}", method='PUT', data={"arquivo_url": arquivo_url})

        flash("Projeto enviado com sucesso!", "success")
        return redirect(url_for('user_dashboard'))

    return render_template("enviar_projeto.html")




@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
