from flask import (Blueprint, render_template, request, redirect, url_for,
                   flash, g, abort, current_app)

from app.models.suprimento import Suprimento
from app.models.abrigo import Abrigo
from app.utils.auth_middleware import login_required

suprimento_bp = Blueprint('suprimentos', __name__, url_prefix='/suprimentos')


def validar_suprimento(form):
    """Confere os campos e devolve (dados, erros)."""
    nome = form.get('nome', '').strip()
    categoria = form.get('categoria', '').strip()
    quantidade = form.get('quantidade', '').strip()
    abrigo = form.get('abrigo_id', '').strip()
    erros = []

    if not nome:
        erros.append("Digite o nome do suprimento.")
    elif len(nome) > 100:
        erros.append("O nome pode ter no máximo 100 caracteres.")

    if not categoria:
        erros.append("Digite a categoria.")
    elif len(categoria) > 60:
        erros.append("A categoria pode ter no máximo 60 caracteres.")

    try:
        quantidade = int(quantidade)
        if quantidade < 0:
            erros.append("A quantidade não pode ser negativa.")
    except ValueError:
        erros.append("A quantidade deve ser um número inteiro.")

    # abrigo é opcional, mas se vier precisa ser do próprio usuário
    abrigo_id = None
    if abrigo:
        if abrigo.isdigit() and Abrigo.buscar_por_id(int(abrigo), g.usuario.id):
            abrigo_id = int(abrigo)
        else:
            erros.append("Abrigo inválido.")

    return (nome, categoria, quantidade, abrigo_id), erros


def montar_pagina(**extra):
    busca = request.args.get('busca', '').strip()
    categoria = request.args.get('categoria', '').strip()
    abrigo_filtro = request.args.get('abrigo', type=int, default=0)

    suprimentos = Suprimento.listar_por_usuario(g.usuario.id, busca, categoria, abrigo_filtro)
    return render_template('suprimentos.html',
                           suprimentos=suprimentos,
                           abrigos=Abrigo.listar_por_usuario(g.usuario.id),
                           categorias=Suprimento.listar_categorias(g.usuario.id),
                           busca=busca, categoria=categoria, abrigo_filtro=abrigo_filtro,
                           **extra)


@suprimento_bp.route('/')
@login_required
def listar():
    return montar_pagina()


@suprimento_bp.route('/cadastrar', methods=['POST'])
@login_required
def cadastrar():
    dados, erros = validar_suprimento(request.form)

    if erros:
        # volta pra lista com a janela aberta e o que a pessoa já digitou
        return montar_pagina(erros=erros, item=request.form, abrir_modal=True)

    nome, categoria, quantidade, abrigo_id = dados
    suprimento = Suprimento(nome, categoria, quantidade, g.usuario.id, abrigo_id)
    suprimento.salvar()
    current_app.logger.info("Suprimento '%s' criado por %s", nome, g.usuario.username)
    flash("Suprimento cadastrado com sucesso!", "sucesso")
    return redirect(url_for('suprimentos.listar'))


@suprimento_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    suprimento = Suprimento.buscar_por_id(id, g.usuario.id)
    if suprimento is None:
        abort(404)

    if request.method == 'POST':
        dados, erros = validar_suprimento(request.form)

        if erros:
            for erro in erros:
                flash(erro, "erro")
            return redirect(url_for('suprimentos.editar', id=id))

        suprimento.nome, suprimento.categoria, suprimento.quantidade, suprimento.abrigo_id = dados
        suprimento.atualizar()
        current_app.logger.info("Suprimento %s atualizado por %s", id, g.usuario.username)
        flash("Suprimento atualizado!", "sucesso")
        return redirect(url_for('suprimentos.listar'))

    return render_template('suprimento_editar.html', suprimento=suprimento,
                           abrigos=Abrigo.listar_por_usuario(g.usuario.id),
                           categorias=Suprimento.listar_categorias(g.usuario.id))


@suprimento_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    suprimento = Suprimento.buscar_por_id(id, g.usuario.id)
    if suprimento is None:
        abort(404)

    suprimento.excluir()
    current_app.logger.info("Suprimento %s excluído por %s", id, g.usuario.username)
    flash("Suprimento removido.", "sucesso")
    return redirect(url_for('suprimentos.listar'))
