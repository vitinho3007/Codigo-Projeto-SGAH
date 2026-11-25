from werkzeug.security import generate_password_hash, check_password_hash

from app.db import DatabaseConnection


class Usuario:
    def __init__(self, nome, username, senha, id=None):
        self.id = id
        self.nome = nome
        self.username = username
        self.senha = senha  # antes de salvar é a senha digitada, depois vira o hash

    def salvar(self):
        # a senha nunca vai pro banco em texto puro
        senha_hash = generate_password_hash(self.senha)
        sql = "INSERT INTO usuarios (nome, username, senha) VALUES (?, ?, ?)"
        with DatabaseConnection() as db:
            db.cursor.execute(sql, (self.nome, self.username, senha_hash))
            self.id = db.cursor.lastrowid
        self.senha = senha_hash

    def verificar_senha(self, senha_digitada):
        return check_password_hash(self.senha, senha_digitada)

    @classmethod
    def montar(cls, linha):
        return cls(linha['nome'], linha['username'], linha['senha'], linha['id'])

    @classmethod
    def buscar_por_id(cls, id):
        with DatabaseConnection() as db:
            db.cursor.execute("SELECT * FROM usuarios WHERE id = ?", (id,))
            linha = db.cursor.fetchone()
        if linha is None:
            return None
        return cls.montar(linha)

    @classmethod
    def buscar_por_username(cls, username):
        with DatabaseConnection() as db:
            db.cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
            linha = db.cursor.fetchone()
        if linha is None:
            return None
        return cls.montar(linha)

    @classmethod
    def autenticar(cls, username, senha):
        usuario = cls.buscar_por_username(username)
        if usuario and usuario.verificar_senha(senha):
            return usuario
        return None
