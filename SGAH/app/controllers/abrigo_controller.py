from flask import (Blueprint, render_template, request, redirect, url_for,
                   flash, g, abort, current_app)

from app.models.abrigo import Abrigo
from app.utils.auth_middleware import login_required

abrigo_bp = Blueprint('abrigos', __name__, url_prefix='/abrigos')


def validar_abrigo(form):
    nome = form.get('nome', '').strip()
    endereco = form.get('endereco', '').strip()
    responsavel = form.get('responsavel', '').strip()
    capacidade = form.get('capacidade', '').strip()
    erros = []

    if not nome:
        erros.append("Digite o nome do abrigo.")
    elif len(nome) > 100:
        erros.append("O nome pode ter no máximo 100 caracteres.")

    if not endereco:
        erros.append("Digite o endereço.")
    elif len(endereco) > 200:
        erros.append("O endereço pode ter no máximo 200 caracteres.")

    if not responsavel:
        erros.append("Digite quem é o responsável.")
    elif len(responsavel) > 100:
        erros.append("O nome do responsável pode ter no máximo 100 caracteres.")

    try:
        capacidade = int(capacidade)
        if capacidade < 1:
            erros.append("A capacidade deve ser maior que zero.")
    except ValueError:
        erros.append("A capacidade deve ser um número inteiro.")

    return (nome, endereco, capacidade, responsavel), erros


def montar_pagina(**extra):
    busca = request.args.get('busca', '').strip()
    abrigos = Abrigo.listar_por_usuario(g.usuario.id, busca)
    return render_template('abrigos.html', abrigos=abrigos, busca=busca, **extra)


@abrigo_bp.route('/')
@login_required
def listar():
    return montar_pagina()


@abrigo_bp.route('/cadastrar', methods=['POST'])
@login_required
def cadastrar():
    dados, erros = validar_abrigo(request.form)

    if erros:
        return montar_pagina(erros=erros, item=request.form, abrir_modal=True)

    nome, endereco, capacidade, responsavel = dados
    abrigo = Abrigo(nome, endereco, capacidade, responsavel, g.usuario.id)
    abrigo.salvar()
    current_app.logger.info("Abrigo '%s' criado por %s", nome, g.usuario.username)
    flash("Abrigo cadastrado com sucesso!", "sucesso")
    return redirect(url_for('abrigos.listar'))


@abrigo_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    abrigo = Abrigo.buscar_por_id(id, g.usuario.id)
    if abrigo is None:
        abort(404)

    if request.method == 'POST':
        dados, erros = validar_abrigo(request.form)

        if erros:
            for erro in erros:
                flash(erro, "erro")
            return redirect(url_for('abrigos.editar', id=id))

        abrigo.nome, abrigo.endereco, abrigo.capacidade, abrigo.responsavel = dados
        abrigo.atualizar()
        current_app.logger.info("Abrigo %s atualizado por %s", id, g.usuario.username)
        flash("Abrigo atualizado!", "sucesso")
        return redirect(url_for('abrigos.listar'))

    return render_template('abrigo_editar.html', abrigo=abrigo)


@abrigo_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    abrigo = Abrigo.buscar_por_id(id, g.usuario.id)
    if abrigo is None:
        abort(404)

    abrigo.excluir()
    current_app.logger.info("Abrigo %s excluído por %s", id, g.usuario.username)
    flash("Abrigo removido. Os suprimentos dele continuam no sistema, só ficam sem abrigo.", "aviso")
    return redirect(url_for('abrigos.listar'))
