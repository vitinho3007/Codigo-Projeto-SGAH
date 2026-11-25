// faz as mensagens flash sumirem sozinhas depois de uns segundos
document.addEventListener('DOMContentLoaded', function () {
    var mensagens = document.querySelectorAll('.flash');

    mensagens.forEach(function (mensagem) {
        setTimeout(function () {
            mensagem.classList.add('some');
            setTimeout(function () {
                mensagem.remove();
            }, 400);
        }, 5000);
    });

    ligarBotoesDeSenha();
    ligarMedidorDeSenha();
    ligarSteppers();
    ligarContador();
    ligarJanelas();
    ligarFiltros();
});


// botão do olhinho: mostra ou esconde a senha
function ligarBotoesDeSenha() {
    document.querySelectorAll('.btn-olho').forEach(function (botao) {
        botao.addEventListener('click', function () {
            var campo = document.getElementById(botao.dataset.alvo);
            var escondida = campo.type === 'password';

            campo.type = escondida ? 'text' : 'password';
            botao.classList.toggle('ativo', escondida);
            botao.setAttribute('aria-label', escondida ? 'Esconder senha' : 'Mostrar senha');
        });
    });
}


// barra de força da senha e aviso se as duas senhas são iguais (tela de cadastro)
function ligarMedidorDeSenha() {
    var senha = document.getElementById('senha');
    var barra = document.getElementById('forca-barra');
    var texto = document.getElementById('forca-texto');
    var confirmar = document.getElementById('confirmar_senha');
    var confere = document.getElementById('confere');

    if (!senha || !barra) {
        return;
    }

    function pontuar(valor) {
        var pontos = 0;
        if (valor.length >= 6) pontos++;
        if (valor.length >= 10) pontos++;
        if (/[0-9]/.test(valor)) pontos++;
        if (/[a-z]/.test(valor) && /[A-Z]/.test(valor)) pontos++;
        if (/[^a-zA-Z0-9]/.test(valor)) pontos++;
        return pontos;
    }

    function verificarIgualdade() {
        if (confirmar.value === '') {
            confere.textContent = '';
            confere.className = 'confere';
        } else if (confirmar.value === senha.value) {
            confere.textContent = 'As senhas coincidem.';
            confere.className = 'confere ok';
        } else {
            confere.textContent = 'As senhas ainda não coincidem.';
            confere.className = 'confere erro';
        }
    }

    senha.addEventListener('input', function () {
        var pontos = pontuar(senha.value);
        var nivel = 'fraca';
        var nome = 'Senha fraca';

        if (senha.value === '') {
            barra.style.width = '0';
            barra.className = 'forca-barra';
            texto.textContent = 'Use letras, números e símbolos para uma senha mais forte.';
            verificarIgualdade();
            return;
        }

        if (pontos >= 4) {
            nivel = 'forte';
            nome = 'Senha forte';
        } else if (pontos >= 2) {
            nivel = 'media';
            nome = 'Senha média';
        }

        barra.style.width = (pontos * 20) + '%';
        barra.className = 'forca-barra ' + nivel;
        texto.textContent = nome;
        verificarIgualdade();
    });

    confirmar.addEventListener('input', verificarIgualdade);
}


// botões de + e - nos campos de quantidade e capacidade
function ligarSteppers() {
    document.querySelectorAll('.stepper').forEach(function (stepper) {
        var campo = stepper.querySelector('input');

        stepper.querySelectorAll('button').forEach(function (botao) {
            botao.addEventListener('click', function () {
                var atual = parseInt(campo.value, 10) || 0;
                var minimo = campo.min !== '' ? parseInt(campo.min, 10) : 0;
                var novo = atual + parseInt(botao.dataset.passo, 10);

                campo.value = Math.max(minimo, novo);
                campo.focus();
            });
        });
    });
}


// contador de caracteres do textarea da descrição
function ligarContador() {
    document.querySelectorAll('textarea[data-contador]').forEach(function (area) {
        var contador = document.getElementById(area.dataset.contador);

        function atualizar() {
            contador.textContent = area.value.length + '/' + area.maxLength;
            contador.classList.toggle('perto', area.value.length > area.maxLength - 50);
        }

        area.addEventListener('input', atualizar);
        atualizar();
    });
}


// janelas de cadastro (<dialog>): abrem pelo botão, fecham no X, em "Cancelar" ou clicando fora
function ligarJanelas() {
    document.querySelectorAll('[data-abrir-modal]').forEach(function (botao) {
        botao.addEventListener('click', function () {
            var janela = document.getElementById(botao.dataset.abrirModal);
            janela.showModal();
            var primeiro = janela.querySelector('input:not([type=hidden]), textarea');
            if (primeiro) primeiro.focus();
        });
    });

    document.querySelectorAll('dialog.modal').forEach(function (janela) {
        janela.querySelectorAll('[data-fechar]').forEach(function (botao) {
            botao.addEventListener('click', function () {
                janela.close();
            });
        });

        janela.addEventListener('click', function (e) {
            if (e.target === janela) janela.close();
        });

        // vem aberta quando o servidor devolveu erros de validação
        if (janela.hasAttribute('data-abrir') || location.search.indexOf('novo=1') !== -1) {
            janela.showModal();
        }
    });
}


// filtros da lista: ao trocar um select já envia o formulário
function ligarFiltros() {
    document.querySelectorAll('form[data-auto] select').forEach(function (select) {
        select.addEventListener('change', function () {
            select.form.submit();
        });
    });
}
