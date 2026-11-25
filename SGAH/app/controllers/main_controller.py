from flask import Blueprint, render_template, request, redirect, url_for, g

from app.models.suprimento import Suprimento
from app.models.abrigo import Abrigo
from app.models.operacao import Operacao, PRIORIDADES
from app.utils.auth_middleware import login_required

main_bp = Blueprint('main', __name__)

SEIS_MESES = 60 * 60 * 24 * 180

# cor de cada prioridade no gráfico (mesma ordem de PRIORIDADES)
CORES_PRIORIDADE = {
    'Baixa': '#4aa3df',
    'Média': '#e5b53c',
    'Alta': '#ef8a3d',
    'Crítica': '#d9534f',
}


def montar_grafico_prioridades(contagem):
    """Devolve a legenda e o conic-gradient usado na rosca."""
    total = sum(contagem.values())
    legenda = []
    partes = []
    inicio = 0

    for prioridade in PRIORIDADES:
        qtd = contagem.get(prioridade, 0)
        legenda.append({'nome': prioridade, 'qtd': qtd, 'cor': CORES_PRIORIDADE[prioridade]})
        if qtd > 0:
            fim = inicio + qtd / total * 100
            partes.append(CORES_PRIORIDADE[prioridade] + ' ' + str(round(inicio, 2)) + '% ' + str(round(fim, 2)) + '%')
            inicio = fim

    gradiente = 'conic-gradient(' + ', '.join(partes) + ')' if partes else ''
    return legenda, gradiente, total


@main_bp.route('/painel')
@login_required
def painel():
    uid = g.usuario.id

    tipos, itens = Suprimento.totais(uid)
    qtd_abrigos, capacidade = Abrigo.totais(uid)

    # quantas unidades de estoque existem para cada pessoa que cabe nos abrigos
    cobertura = round(itens / capacidade, 1) if capacidade else 0

    resumo = {
        'tipos_suprimentos': tipos,
        'itens_estoque': itens,
        'estoque_baixo': Suprimento.contar_baixos(uid),
        'abrigos': qtd_abrigos,
        'capacidade_abrigos': capacidade,
        'cobertura': cobertura,
        'operacoes': Operacao.contar(uid),
        'urgentes': Operacao.contar_urgentes(uid),
    }

    legenda, gradiente, total_ocorrencias = montar_grafico_prioridades(
        Operacao.contar_por_prioridade(uid))

    return render_template('painel.html',
                           resumo=resumo,
                           legenda=legenda,
                           gradiente=gradiente,
                           total_ocorrencias=total_ocorrencias,
                           por_categoria=Suprimento.estoque_por_categoria(uid)[:5],
                           baixos=Suprimento.listar_baixos(uid),
                           urgentes=Operacao.listar_urgentes(uid))


@main_bp.route('/tema', methods=['POST'])
def tema():
    escolha = request.form.get('escolha', 'claro')
    if escolha not in ('claro', 'dark'):
        escolha = 'claro'

    # volta pra pagina de onde o usuario veio
    destino = request.referrer
    if not destino or not destino.startswith(request.host_url):
        destino = url_for('auth.login')

    resposta = redirect(destino)
    resposta.set_cookie('tema', escolha, max_age=SEIS_MESES)
    return resposta
