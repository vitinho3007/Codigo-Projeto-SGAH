from app.db import DatabaseConnection


class Suprimento:
    def __init__(self, nome, categoria, quantidade, usuario_id, abrigo_id=None,
                 id=None, abrigo_nome=None):
        self.id = id
        self.nome = nome
        self.categoria = categoria
        self.quantidade = quantidade
        self.usuario_id = usuario_id
        self.abrigo_id = abrigo_id
        self.abrigo_nome = abrigo_nome

    def salvar(self):
        sql = """INSERT INTO suprimentos (nome, categoria, quantidade, abrigo_id, usuario_id)
                 VALUES (?, ?, ?, ?, ?)"""
        with DatabaseConnection() as db:
            db.cursor.execute(sql, (self.nome, self.categoria, self.quantidade,
                                    self.abrigo_id, self.usuario_id))
            self.id = db.cursor.lastrowid

    def atualizar(self):
        sql = """UPDATE suprimentos
                 SET nome = ?, categoria = ?, quantidade = ?, abrigo_id = ?
                 WHERE id = ? AND usuario_id = ?"""
        with DatabaseConnection() as db:
            db.cursor.execute(sql, (self.nome, self.categoria, self.quantidade,
                                    self.abrigo_id, self.id, self.usuario_id))

    def excluir(self):
        with DatabaseConnection() as db:
            db.cursor.execute("DELETE FROM suprimentos WHERE id = ? AND usuario_id = ?",
                              (self.id, self.usuario_id))
            return db.cursor.rowcount > 0

    @classmethod
    def montar(cls, linha):
        return cls(linha['nome'], linha['categoria'], linha['quantidade'],
                   linha['usuario_id'], linha['abrigo_id'], linha['id'],
                   linha['abrigo_nome'])

    @classmethod
    def listar_por_usuario(cls, usuario_id, busca='', categoria='', abrigo_id=0):
        termo = '%' + busca + '%'
        sql = """SELECT s.*, a.nome AS abrigo_nome
                 FROM suprimentos s
                 LEFT JOIN abrigos a ON a.id = s.abrigo_id
                 WHERE s.usuario_id = ?
                 AND (s.nome LIKE ? OR s.categoria LIKE ?)
                 ORDER BY s.id DESC"""
        with DatabaseConnection() as db:
            db.cursor.execute(sql, (usuario_id, termo, termo))
            linhas = db.cursor.fetchall()
        lista = [cls.montar(l) for l in linhas]

        # filtros de categoria e abrigo
        if categoria:
            lista = [s for s in lista if s.categoria == categoria]
        if abrigo_id:
            lista = [s for s in lista if s.abrigo_id == abrigo_id]
        return lista

    @classmethod
    def buscar_por_id(cls, id, usuario_id):
        sql = """SELECT s.*, a.nome AS abrigo_nome
                 FROM suprimentos s
                 LEFT JOIN abrigos a ON a.id = s.abrigo_id
                 WHERE s.id = ? AND s.usuario_id = ?"""
        with DatabaseConnection() as db:
            db.cursor.execute(sql, (id, usuario_id))
            linha = db.cursor.fetchone()
        if linha is None:
            return None
        return cls.montar(linha)

    @classmethod
    def listar_categorias(cls, usuario_id):
        sql = "SELECT DISTINCT categoria FROM suprimentos WHERE usuario_id = ? ORDER BY categoria"
        with DatabaseConnection() as db:
            db.cursor.execute(sql, (usuario_id,))
            linhas = db.cursor.fetchall()
        return [l['categoria'] for l in linhas]

    @classmethod
    def estoque_por_categoria(cls, usuario_id):
        sql = """SELECT categoria, SUM(quantidade) AS total
                 FROM suprimentos WHERE usuario_id = ?
                 GROUP BY categoria ORDER BY total DESC"""
        with DatabaseConnection() as db:
            db.cursor.execute(sql, (usuario_id,))
            linhas = db.cursor.fetchall()
        return [(l['categoria'], l['total']) for l in linhas]

    @classmethod
    def listar_baixos(cls, usuario_id, limite=4):
        sql = """SELECT s.*, a.nome AS abrigo_nome
                 FROM suprimentos s
                 LEFT JOIN abrigos a ON a.id = s.abrigo_id
                 WHERE s.usuario_id = ? AND s.quantidade <= 30
                 ORDER BY s.quantidade ASC LIMIT ?"""
        with DatabaseConnection() as db:
            db.cursor.execute(sql, (usuario_id, limite))
            linhas = db.cursor.fetchall()
        return [cls.montar(l) for l in linhas]

    @classmethod
    def contar_baixos(cls, usuario_id):
        sql = "SELECT COUNT(*) AS total FROM suprimentos WHERE usuario_id = ? AND quantidade <= 30"
        with DatabaseConnection() as db:
            db.cursor.execute(sql, (usuario_id,))
            return db.cursor.fetchone()['total']

    @classmethod
    def totais(cls, usuario_id):
        sql = """SELECT COUNT(*) AS tipos, COALESCE(SUM(quantidade), 0) AS itens
                 FROM suprimentos WHERE usuario_id = ?"""
        with DatabaseConnection() as db:
            db.cursor.execute(sql, (usuario_id,))
            linha = db.cursor.fetchone()
        return linha['tipos'], linha['itens']
