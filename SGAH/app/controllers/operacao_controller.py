from flask import (Blueprint, render_template, request, redirect, url_for,
                   flash, g, abort, current_app)

from app.models.operacao import Operacao, PRIORIDADES
from app.utils.auth_middleware import login_required

operacao_bp = Blueprint('operacoes', __name__, url_prefix='/operacoes')


def validar_operacao(form):
    titulo = form.get('titulo', '').strip()
    local = form.get('local', '').strip()
    prioridade = form.get('prioridade', '').strip()
    descricao = form.get('descricao', '').strip()
    erros = []

    if not titulo:
        erros.append("Digite o título da ocorrência.")
    elif len(titulo) > 120:
        erros.append("O título pode ter no máximo 120 caracteres.")

    if not local:
        erros.append("Digite o local da ocorrência.")
    elif len(local) > 150:
        erros.append("A localização pode ter no máximo 150 caracteres.")

    if prioridade not in PRIORIDADES:
        erros.append("Selecione uma prioridade válida.")

    if len(descricao) < 10:
        erros.append("A descrição precisa ter pelo menos 10 caracteres.")
    elif len(descricao) > 500:
        erros.append("A descrição pode ter no máximo 500 caracteres.")

    return (titulo, local, prioridade, descricao), erros


def montar_pagina(**extra):
    busca = request.args.get('busca', '').strip()
    prioridade = request.args.get('prioridade', '').strip()
    operacoes = Operacao.listar_por_usuario(g.usuario.id, busca, prioridade)
    return render_template('operacoes.html', operacoes=operacoes,
                           prioridades=PRIORIDADES, busca=busca,
                           prioridade_filtro=prioridade, **extra)


@operacao_bp.route('/')
@login_required
def listar():
    return montar_pagina()


@operacao_bp.route('/cadastrar', methods=['POST'])
@login_required
def cadastrar():
    dados, erros = validar_operacao(request.form)

    if erros:
        return montar_pagina(erros=erros, item=request.form, abrir_modal=True)

    titulo, local, prioridade, descricao = dados
    operacao = Operacao(titulo, local, prioridade, descricao, g.usuario.id)
    operacao.salvar()
    current_app.logger.info("Ocorrência '%s' criada por %s", titulo, g.usuario.username)
    flash("Ocorrência registrada!", "sucesso")
    return redirect(url_for('operacoes.listar'))


@operacao_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    operacao = Operacao.buscar_por_id(id, g.usuario.id)
    if operacao is None:
        abort(404)

    if request.method == 'POST':
        dados, erros = validar_operacao(request.form)

        if erros:
            for erro in erros:
                flash(erro, "erro")
            return redirect(url_for('operacoes.editar', id=id))

        operacao.titulo, operacao.local, operacao.prioridade, operacao.descricao = dados
        operacao.atualizar()
        current_app.logger.info("Ocorrência %s atualizada por %s", id, g.usuario.username)
        flash("Ocorrência atualizada!", "sucesso")
        return redirect(url_for('operacoes.listar'))

    return render_template('operacao_editar.html', operacao=operacao,
                           prioridades=PRIORIDADES)


@operacao_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    operacao = Operacao.buscar_por_id(id, g.usuario.id)
    if operacao is None:
        abort(404)

    operacao.excluir()
    current_app.logger.info("Ocorrência %s excluída por %s", id, g.usuario.username)
    flash("Ocorrência removida.", "sucesso")
    return redirect(url_for('operacoes.listar'))
