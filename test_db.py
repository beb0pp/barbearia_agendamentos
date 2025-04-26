import os
from dotenv import load_dotenv
from app import create_app
from extensions import db
from models import User, Agendamento

# Carregar variáveis de ambiente
load_dotenv()

def test_database_connection():
    app = create_app()
    
    with app.app_context():
        try:
            # Criação das tabelas (se não existirem)
            db.create_all()
            print("✅ Banco de dados conectado e tabelas criadas com sucesso!")
            
            # Teste de consulta nos usuários
            users = User.query.all()
            print(f"👤 Usuários encontrados: {len(users)}")
            
            # Teste de consulta nos agendamentos
            agendamentos = Agendamento.query.all()
            print(f"📅 Agendamentos encontrados: {len(agendamentos)}")
            
        except Exception as e:
            print("\n❌ ERRO na conexão ou criação de tabelas!")
            print(f"Detalhes do erro:\n{str(e)}\n")
            raise  # Opcional: lança o erro novamente se quiser parar o script

if __name__ == "__main__":
    print("🔎 Testando conexão com o banco de dados...")
    test_database_connection()
