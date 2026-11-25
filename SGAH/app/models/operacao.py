from app.db import DatabaseConnection

PRIORIDADES = ('Baixa', 'Média', 'Alta', 'Crítica')


class Operacao:
    def __init__(self, titulo, local, prioridade, descricao, usuario_id,
                 id=None, criado_em=None):
        self.id = id
        self.titulo = titulo
        self.local = local
        self.prioridade = prioridade
        self.descricao = descricao
        self.usuario_id = usuario_id
        self.criado_em = criado_em

    def salvar(self):
        sql = """INSERT INTO operacoes (titulo, local, prioridade, descricao, usuario_id)
                 VALUES (?, ?, ?, ?, ?)"""
        with DatabaseConnection() as db:
            db.cursor.execute(sql, (self.titulo, self.local, self.prioridade,
                                    self.descricao, self.usuario_id))
            self.id = db.cursor.lastrowid

    def atualizar(self):
        sql = """UPDATE operacoes SET titulo = ?, local = ?, prioridade = ?, descricao = ?
                 WHERE id = ? AND usuario_id = ?"""
        with DatabaseConnection() as db:
            db.cursor.execute(sql, (self.titulo, self.local, self.prioridade,
                                    self.descricao, self.id, self.usuario_id))

    def excluir(self):
        with DatabaseConnection() as db:
            db.cursor.execute("DELETE FROM operacoes WHERE id = ? AND usuario_id = ?",
                              (self.id, self.usuario_id))
            return db.cursor.rowcount > 0

    @classmethod
    def montar(cls, linha):
        return cls(linha['titulo'], linha['local'], linha['prioridade'],
                   linha['descricao'], linha['usuario_id'], linha['id'],
                   linha['criado_em'])

    @classmethod
    def listar_por_usuario(cls, usuario_id, busca='', prioridade=''):
        termo = '%' + busca + '%'
        sql = """SELECT * FROM operacoes
                 WHERE usuario_id = ?
                 AND (titulo LIKE ? OR local LIKE ? OR descricao LIKE ?)
                 ORDER BY id DESC"""
        with DatabaseConnection() as db:
            db.cursor.execute(sql, (usuario_id, termo, termo, termo))
            linhas = db.cursor.fetchall()
        lista = [cls.montar(l) for l in linhas]

        if prioridade:
            lista = [o for o in lista if o.prioridade == prioridade]
        return lista

    @classmethod
    def buscar_por_id(cls, id, usuario_id):
        with DatabaseConnection() as db:
            db.cursor.execute("SELECT * FROM operacoes WHERE id = ? AND usuario_id = ?",
                              (id, usuario_id))
            linha = db.cursor.fetchone()
        if linha is None:
            return None
        return cls.montar(linha)

    @classmethod
    def contar_por_prioridade(cls, usuario_id):
        sql = """SELECT prioridade, COUNT(*) AS total FROM operacoes
                 WHERE usuario_id = ? GROUP BY prioridade"""
        with DatabaseConnection() as db:
            db.cursor.execute(sql, (usuario_id,))
            linhas = db.cursor.fetchall()
        return {l['prioridade']: l['total'] for l in linhas}

    @classmethod
    def contar_urgentes(cls, usuario_id):
        sql = """SELECT COUNT(*) AS total FROM operacoes
                 WHERE usuario_id = ? AND prioridade IN ('Alta', 'Crítica')"""
        with DatabaseConnection() as db:
            db.cursor.execute(sql, (usuario_id,))
            return db.cursor.fetchone()['total']

    @classmethod
    def contar(cls, usuario_id):
        with DatabaseConnection() as db:
            db.cursor.execute("SELECT COUNT(*) AS total FROM operacoes WHERE usuario_id = ?",
                              (usuario_id,))
            return db.cursor.fetchone()['total']

    @classmethod
    def listar_urgentes(cls, usuario_id, limite=4):
        sql = """SELECT * FROM operacoes
                 WHERE usuario_id = ? AND prioridade IN ('Alta', 'Crítica')
                 ORDER BY CASE prioridade WHEN 'Crítica' THEN 0 ELSE 1 END, id DESC
                 LIMIT ?"""
        with DatabaseConnection() as db:
            db.cursor.execute(sql, (usuario_id, limite))
            linhas = db.cursor.fetchall()
        return [cls.montar(l) for l in linhas]
