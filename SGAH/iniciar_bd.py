from app.db import DatabaseConnection
from app.models.usuario import Usuario


def criar_tabelas():
    with DatabaseConnection() as db:
        db.cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL
            )
        """)

        db.cursor.execute("""
            CREATE TABLE IF NOT EXISTS abrigos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                endereco TEXT NOT NULL,
                capacidade INTEGER NOT NULL CHECK (capacidade > 0),
                responsavel TEXT NOT NULL,
                criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                usuario_id INTEGER NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
            )
        """)

        # se o abrigo for apagado o suprimento continua existindo, so perde o vinculo
        db.cursor.execute("""
            CREATE TABLE IF NOT EXISTS suprimentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                categoria TEXT NOT NULL,
                quantidade INTEGER NOT NULL CHECK (quantidade >= 0),
                abrigo_id INTEGER,
                usuario_id INTEGER NOT NULL,
                FOREIGN KEY (abrigo_id) REFERENCES abrigos (id) ON DELETE SET NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
            )
        """)

        db.cursor.execute("""
            CREATE TABLE IF NOT EXISTS operacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                local TEXT NOT NULL,
                prioridade TEXT NOT NULL,
                descricao TEXT NOT NULL,
                criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                usuario_id INTEGER NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
            )
        """)


def criar_usuario_teste():
    if Usuario.buscar_por_username('admin') is None:
        admin = Usuario('Administrador', 'admin', '1234')
        admin.salvar()
        print("Usuário de teste criado: admin / 1234")
    else:
        print("Usuário admin já existe, nada a fazer.")


if __name__ == '__main__':
    criar_tabelas()
    criar_usuario_teste()
    print("Banco de dados pronto!")
