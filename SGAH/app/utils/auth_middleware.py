from functools import wraps

from flask import session, redirect, url_for, flash, g, current_app

from app.models.usuario import Usuario


def login_required(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        user_id = session.get('user_id')

        if not user_id:
            current_app.logger.warning("Acesso sem login bloqueado")
            flash("Faça login para entrar nessa página.", "aviso")
            return redirect(url_for('auth.login'))

        # confere no banco se o usuario da sessao ainda existe
        usuario = Usuario.buscar_por_id(user_id)
        if usuario is None:
            session.clear()
            flash("Sua sessão não é mais válida, entre de novo.", "erro")
            return redirect(url_for('auth.login'))

        g.usuario = usuario
        return f(*args, **kwargs)
    return decorada
