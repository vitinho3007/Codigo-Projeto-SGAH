from app.db import DatabaseConnection


class Abrigo:
    def __init__(self, nome, endereco, capacidade, responsavel, usuario_id,
                 id=None, criado_em=None, itens_estoque=0):
        self.id = id
        self.nome = nome
        self.endereco = endereco
        self.capacidade = capacidade
        self.responsavel = responsavel
        self.usuario_id = usuario_id
        self.criado_em = criado_em
        self.itens_estoque = itens_estoque  # soma dos suprimentos ligados ao abrigo

    def salvar(self):
        sql = """INSERT INTO abrigos (nome, endereco, capacidade, responsavel, usuario_id)
                 VALUES (?, ?, ?, ?, ?)"""
        with DatabaseConnection() as db:
            db.cursor.execute(sql, (self.nome, self.endereco, self.capacidade,
                                    self.responsavel, self.usuario_id))
            self.id = db.cursor.lastrowid

    def atualizar(self):
        sql = """UPDATE abrigos SET nome = ?, endereco = ?, capacidade = ?, responsavel = ?
                 WHERE id = ? AND usuario_id = ?"""
        with DatabaseConnection() as db:
            db.cursor.execute(sql, (self.nome, self.endereco, self.capacidade,
                                    self.responsavel, self.id, self.usuario_id))

    def excluir(self):
        with DatabaseConnection() as db:
            db.cursor.execute("DELETE FROM abrigos WHERE id = ? AND usuario_id = ?",
                              (self.id, self.usuario_id))
            return db.cursor.rowcount > 0

    @classmethod
    def montar(cls, linha):
        return cls(linha['nome'], linha['endereco'], linha['capacidade'],
                   linha['responsavel'], linha['usuario_id'], linha['id'],
                   linha['criado_em'], linha['itens_estoque'])

    @classmethod
    def listar_por_usuario(cls, usuario_id, busca=''):
        termo = '%' + busca + '%'
        # a subconsulta soma o estoque dos suprimentos ligados a cada abrigo
        sql = """SELECT a.*,
                   (SELECT COALESCE(SUM(s.quantidade), 0) FROM suprimentos s
                    WHERE s.abrigo_id = a.id) AS itens_estoque
                 FROM abrigos a
                 WHERE a.usuario_id = ?
                 AND (a.nome LIKE ? OR a.endereco LIKE ? OR a.responsavel LIKE ?)
                 ORDER BY a.id DESC"""
        with DatabaseConnection() as db:
            db.cursor.execute(sql, (usuario_id, termo, termo, termo))
            linhas = db.cursor.fetchall()
        return [cls.montar(l) for l in linhas]

    @classmethod
    def buscar_por_id(cls, id, usuario_id):
        sql = """SELECT a.*,
                   (SELECT COALESCE(SUM(s.quantidade), 0) FROM suprimentos s
                    WHERE s.abrigo_id = a.id) AS itens_estoque
                 FROM abrigos a
                 WHERE a.id = ? AND a.usuario_id = ?"""
        with DatabaseConnection() as db:
            db.cursor.execute(sql, (id, usuario_id))
            linha = db.cursor.fetchone()
        if linha is None:
            return None
        return cls.montar(linha)

    @classmethod
    def totais(cls, usuario_id):
        sql = """SELECT COUNT(*) AS qtd, COALESCE(SUM(capacidade), 0) AS capacidade
                 FROM abrigos WHERE usuario_id = ?"""
        with DatabaseConnection() as db:
            db.cursor.execute(sql, (usuario_id,))
            linha = db.cursor.fetchone()
        return linha['qtd'], linha['capacidade']
