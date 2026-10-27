# app/shared/database/populate.py
import logging
from datetime import datetime
from app.core.config.settings import Configuration
from app.shared.database.connection import session_scope
from app.shared.utils.password_utils import hash_password
from app.modules.assistente.models.database_models import (
    Master, User, Assistant, Chat, ChatItem, Finance, FinanceItem
)

config = Configuration()

def populate_database():
    """Popula o banco de dados com dados iniciais se a flag estiver ativa"""
    
    # Verifica se deve popular
    if not config.db_populate:
        logging.info("DB_POPULATE está desativado. Banco de dados vazio.")
        return
    
    try:
        with session_scope() as session:
            # Verifica se já existem dados
            existing_master = session.query(Master).count()
            if existing_master > 0:
                logging.info("Banco de dados já populado. Pulando população inicial.")
                return
            
            logging.info("Populando banco de dados com dados iniciais...")
            
            # 1. Criar Master
            master = Master(
                system_name="Assistant System",
                system_version="1.0.0",
                is_active=True,
                maintenance_mode=False,
                default_language="pt-BR",
                default_timezone="America/Sao_Paulo",
                description="Sistema de assistente pessoal com IA",
                system_owner="Leonan"
            )
            session.add(master)
            session.flush()
            
            # 2. Criar usuário admin
            user_admin = User(
                master_id=master.id,
                username="admin",
                email="admin@assistant.com",
                full_name="Administrador do Sistema",
                password_hash=hash_password("admin123"),  # Senha: admin123
                is_active=True,
                is_admin=True,
                bio="Administrador do sistema de assistente"
            )
            session.add(user_admin)
            session.flush()
            
            # 3. Criar assistente para o admin
            assistant = Assistant(
                master_id=master.id,
                user_id=user_admin.id,
                name="Tainá",
                model="llama-3.1-8b-instant",
                temperature=0.7,
                max_tokens=2048,
                greeting_message="Olá! Sou a Tainá, sua assistente pessoal. Como posso ajudar você hoje?",
                system_prompt="You are a helpful and friendly assistant named Tainá. Always respond in Portuguese.",
                personality="friendly",
                communication_style="casual",
                is_active=True,
                is_default=True
            )
            session.add(assistant)
            session.flush()
            
            # 4. Criar um chat inicial
            chat = Chat(
                master_id=master.id,
                user_id=user_admin.id,
                assistant_id=assistant.id,
                title="Primeira Conversa",
                context_type="general",
                status="active",
                total_messages=0
            )
            session.add(chat)
            session.flush()
            
            # 5. Adicionar mensagens iniciais
            messages = [
                ChatItem(
                    chat_id=chat.id,
                    role="assistant",
                    content="Olá! Bem-vindo ao Assistant System. Como posso ajudar você hoje?",
                    tokens_used=15
                ),
                ChatItem(
                    chat_id=chat.id,
                    role="user",
                    content="Olá! Quero começar a organizar minhas finanças.",
                    tokens_used=8
                ),
                ChatItem(
                    chat_id=chat.id,
                    role="assistant",
                    content="Excelente! Posso ajudar você a organizar suas finanças. Que tal começarmos registrando suas receitas e despesas do mês?",
                    tokens_used=22
                )
            ]
            for msg in messages:
                session.add(msg)
                chat.total_messages += 1
            
            session.add(chat)
            
            # 6. Criar um financeiro inicial
            finance = Finance(
                master_id=master.id,
                user_id=user_admin.id,
                reference_month=datetime.now().strftime("%Y-%m"),
                reference_year=datetime.now().year,
                total_income=0.0,
                total_expenses=0.0,
                total_balance=0.0,
                is_closed=False
            )
            session.add(finance)
            session.flush()
            
            # 7. Adicionar transações iniciais
            transactions = [
                FinanceItem(
                    finance_id=finance.id,
                    description="Salário",
                    amount=5000.00,
                    transaction_type="income",
                    category="Salário",
                    transaction_date=datetime.now().replace(day=5),
                    status="paid",
                    tags='["salário", "renda"]'
                ),
                FinanceItem(
                    finance_id=finance.id,
                    description="Aluguel",
                    amount=1200.00,
                    transaction_type="expense",
                    category="Moradia",
                    subcategory="Aluguel",
                    transaction_date=datetime.now().replace(day=10),
                    due_date=datetime.now().replace(day=10),
                    status="paid",
                    is_recurring=True,
                    recurring_period="monthly",
                    tags='["moradia", "fixa"]'
                ),
                FinanceItem(
                    finance_id=finance.id,
                    description="Supermercado",
                    amount=450.00,
                    transaction_type="expense",
                    category="Alimentação",
                    subcategory="Supermercado",
                    transaction_date=datetime.now().replace(day=15),
                    status="pending",
                    tags='["alimentação", "variável"]'
                )
            ]
            for trans in transactions:
                session.add(trans)
                # Atualiza totais
                if trans.transaction_type == "income":
                    finance.total_income += trans.amount
                else:
                    finance.total_expenses += trans.amount
            
            finance.total_balance = finance.total_income - finance.total_expenses
            session.add(finance)
            
            session.commit()
            logging.info("Banco de dados populado com sucesso!")
            logging.info(f"Usuário admin criado com senha: admin123")
            
    except Exception as e:
        logging.error(f"Erro ao popular banco de dados: {e}")
        raise