from flask import (Blueprint, render_template, request, redirect, url_for,
                   flash, session, current_app)

from app.models.usuario import Usuario

auth_bp = Blueprint('auth', __name__)

UM_MES = 60 * 60 * 24 * 30


@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    # cookie com o ultimo usuario que entrou, pra ja vir preenchido
    ultimo_usuario = request.cookies.get('ultimo_usuario', '')

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        senha = request.form.get('senha', '')

        if not username or not senha:
            flash("Preencha usuário e senha.", "erro")
            return render_template('login.html', ultimo_usuario=username)

        usuario = Usuario.autenticar(username, senha)
        if usuario is None:
            current_app.logger.warning("Falha de login para o usuário '%s'", username)
            flash("Usuário ou senha inválidos, tenta de novo.", "erro")
            return render_template('login.html', ultimo_usuario=username)

        session.clear()
        session['user_id'] = usuario.id
        session['username'] = usuario.username
        current_app.logger.info("Login realizado: %s", usuario.username)
        flash(f"Olá, {usuario.nome}!", "sucesso")

        resposta = redirect(url_for('main.painel'))
        resposta.set_cookie('ultimo_usuario', usuario.username, max_age=UM_MES)
        return resposta

    return render_template('login.html', ultimo_usuario=ultimo_usuario)


@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        username = request.form.get('username', '').strip()
        senha = request.form.get('senha', '')
        confirmar = request.form.get('confirmar_senha', '')

        erros = []
        if not nome:
            erros.append("Digite seu nome completo.")
        elif len(nome) > 100:
            erros.append("O nome pode ter no máximo 100 caracteres.")

        if len(username) < 3 or len(username) > 40:
            erros.append("O nome de usuário deve ter entre 3 e 40 caracteres.")
        elif ' ' in username:
            erros.append("O nome de usuário não pode ter espaços.")
        elif Usuario.buscar_por_username(username):
            erros.append("Esse nome de usuário já está em uso, escolhe outro.")

        if len(senha) < 6:
            erros.append("A senha deve ter pelo menos 6 caracteres.")
        elif senha != confirmar:
            erros.append("As senhas não coincidem.")

        if erros:
            for erro in erros:
                flash(erro, "erro")
            return render_template('cadastro.html', nome=nome, username=username)

        novo = Usuario(nome, username, senha)
        novo.salvar()
        current_app.logger.info("Novo usuário cadastrado: %s", username)
        flash("Conta criada! Agora é só fazer login.", "sucesso")
        return redirect(url_for('auth.login'))

    return render_template('cadastro.html', nome='', username='')


@auth_bp.route('/logout', methods=['POST'])
def logout():
    username = session.get('username')
    session.clear()
    current_app.logger.info("Logout: %s", username)
    flash("Você saiu da conta.", "sucesso")
    return redirect(url_for('auth.login'))
