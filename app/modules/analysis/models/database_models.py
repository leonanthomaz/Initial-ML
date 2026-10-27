# app/modules/assistente/models/database_models.py
from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func, Integer, ForeignKey, String, Text, Float, Boolean
import uuid


class BaseModel(SQLModel):
    """Modelo base com campos comuns"""
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        max_length=36,
        unique=True,
        index=True
    )


class Master(BaseModel, table=True):
    """
    Tabela principal do sistema (Core)
    """
    __tablename__ = "tb_master"
    
    # Campos principais
    system_name: str = Field(max_length=100, default="Assistant System")
    system_version: str = Field(max_length=20, default="1.0.0")
    is_active: bool = Field(default=True)
    maintenance_mode: bool = Field(default=False)
    
    # Configurações
    default_language: str = Field(max_length=10, default="pt-BR")
    default_timezone: str = Field(max_length=50, default="America/Sao_Paulo")
    
    # Metadata
    description: Optional[str] = Field(default=None, max_length=500)
    system_owner: Optional[str] = Field(default=None, max_length=100)
    
    # Timestamps - definidos diretamente
    created_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, onupdate=func.now())
    )
    
    # Relacionamentos
    users: List["User"] = Relationship(back_populates="master")
    assistants: List["Assistant"] = Relationship(back_populates="master")
    chats: List["Chat"] = Relationship(back_populates="master")
    finances: List["Finance"] = Relationship(back_populates="master")


class User(BaseModel, table=True):
    """
    Tabela de usuários do sistema
    """
    __tablename__ = "tb_users"
    
    # FK para Master
    master_id: int = Field(
        sa_column=Column(Integer, ForeignKey("tb_master.id"), nullable=False)
    )
    
    # Dados pessoais
    username: str = Field(max_length=50, unique=True, index=True)
    email: str = Field(max_length=100, unique=True, index=True)
    full_name: str = Field(max_length=200)
    
    # Autenticação
    password_hash: str = Field(max_length=255)
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)
    last_login: Optional[datetime] = Field(default=None)
    
    # Preferências
    preferred_language: str = Field(max_length=10, default="pt-BR")
    timezone: str = Field(max_length=50, default="America/Sao_Paulo")
    
    # Metadata
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    bio: Optional[str] = Field(default=None, max_length=500)
    
    # Timestamps
    created_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, onupdate=func.now())
    )
    
    # Relacionamentos
    master: Master = Relationship(back_populates="users")
    assistants: List["Assistant"] = Relationship(back_populates="user")
    chats: List["Chat"] = Relationship(back_populates="user")
    finances: List["Finance"] = Relationship(back_populates="user")


class Assistant(BaseModel, table=True):
    """
    Tabela de configurações da assistente
    """
    __tablename__ = "tb_assistants"
    
    # FKs
    master_id: int = Field(
        sa_column=Column(Integer, ForeignKey("tb_master.id"), nullable=False)
    )
    user_id: int = Field(
        sa_column=Column(Integer, ForeignKey("tb_users.id"), nullable=False)
    )
    
    # Identificação
    name: str = Field(max_length=100, default="Assistant")
    
    # Configurações da IA
    model: str = Field(max_length=100, default="llama-3.1-8b-instant")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048)
    
    # Comportamento
    greeting_message: Optional[str] = Field(
        default="Olá! Sou sua assistente pessoal. Como posso ajudar você hoje?",
        max_length=500
    )
    system_prompt: Optional[str] = Field(
        default="You are a helpful assistant.",
        max_length=2000
    )
    
    # Preferências
    personality: Optional[str] = Field(default=None, max_length=50)
    communication_style: Optional[str] = Field(default=None, max_length=50)
    
    # Status
    is_active: bool = Field(default=True)
    is_default: bool = Field(default=False)
    
    # Timestamps
    created_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, onupdate=func.now())
    )
    
    # Relacionamentos
    master: Master = Relationship(back_populates="assistants")
    user: User = Relationship(back_populates="assistants")


class Chat(BaseModel, table=True):
    """
    Tabela de conversas/chats
    """
    __tablename__ = "tb_chats"
    
    # FKs
    master_id: int = Field(
        sa_column=Column(Integer, ForeignKey("tb_master.id"), nullable=False)
    )
    user_id: int = Field(
        sa_column=Column(Integer, ForeignKey("tb_users.id"), nullable=False)
    )
    assistant_id: Optional[int] = Field(
        sa_column=Column(Integer, ForeignKey("tb_assistants.id"), nullable=True)
    )
    
    # Dados do chat
    title: str = Field(max_length=200, default="Nova Conversa")
    context_type: str = Field(max_length=50, default="general")
    status: str = Field(max_length=20, default="active")
    
    # Métricas
    total_messages: int = Field(default=0)
    total_tokens: int = Field(default=0)
    
    # Timestamps
    created_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, onupdate=func.now())
    )
    
    # Relacionamentos
    master: Master = Relationship(back_populates="chats")
    user: User = Relationship(back_populates="chats")
    assistant: Optional[Assistant] = Relationship()
    items: List["ChatItem"] = Relationship(back_populates="chat")


class ChatItem(BaseModel, table=True):
    """
    Tabela de mensagens/items de um chat
    """
    __tablename__ = "tb_chat_items"
    
    # FK
    chat_id: int = Field(
        sa_column=Column(Integer, ForeignKey("tb_chats.id"), nullable=False)
    )
    
    # Conteúdo
    role: str = Field(max_length=20)
    content: str = Field(sa_column=Column(Text))
    
    # Métricas
    tokens_used: Optional[int] = Field(default=0)
    response_time: Optional[float] = Field(default=None)
    
    # Metadata
    metadata_json: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    # Timestamps
    created_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, onupdate=func.now())
    )
    
    # Relacionamentos
    chat: Chat = Relationship(back_populates="items")


class Finance(BaseModel, table=True):
    """
    Tabela mestre de finanças
    """
    __tablename__ = "tb_finances"
    
    # FKs
    master_id: int = Field(
        sa_column=Column(Integer, ForeignKey("tb_master.id"), nullable=False)
    )
    user_id: int = Field(
        sa_column=Column(Integer, ForeignKey("tb_users.id"), nullable=False)
    )
    
    # Dados do período
    reference_month: str = Field(max_length=7)
    reference_year: int = Field()
    
    # Totais calculados
    total_income: float = Field(default=0.0)
    total_expenses: float = Field(default=0.0)
    total_balance: float = Field(default=0.0)
    savings_rate: Optional[float] = Field(default=None)
    
    # Resumos (JSON)
    categories_summary: Optional[str] = Field(default=None, sa_column=Column(Text))
    insights: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    # Status
    is_closed: bool = Field(default=False)
    closed_at: Optional[datetime] = Field(default=None)
    
    # Timestamps
    created_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, onupdate=func.now())
    )
    
    # Relacionamentos
    master: Master = Relationship(back_populates="finances")
    user: User = Relationship(back_populates="finances")
    items: List["FinanceItem"] = Relationship(back_populates="finance")


class FinanceItem(BaseModel, table=True):
    """
    Tabela de items/transações financeiras
    """
    __tablename__ = "tb_finance_items"
    
    # FK
    finance_id: int = Field(
        sa_column=Column(Integer, ForeignKey("tb_finances.id"), nullable=False)
    )
    
    # Dados da transação
    description: str = Field(max_length=500)
    amount: float = Field()
    transaction_type: str = Field(max_length=20)
    category: str = Field(max_length=100)
    subcategory: Optional[str] = Field(default=None, max_length=100)
    
    # Data
    transaction_date: datetime = Field(default_factory=datetime.now)
    due_date: Optional[datetime] = Field(default=None)
    payment_date: Optional[datetime] = Field(default=None)
    
    # Pagamento
    payment_method: Optional[str] = Field(default=None, max_length=50)
    status: str = Field(default="pending", max_length=20)
    
    # Recorrência
    is_recurring: bool = Field(default=False)
    recurring_period: Optional[str] = Field(default=None, max_length=20)
    recurring_end_date: Optional[datetime] = Field(default=None)
    
    # Metadata
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))
    tags: Optional[str] = Field(default=None, max_length=500)
    attachments: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    # Timestamps
    created_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, onupdate=func.now())
    )
    
    # Relacionamentos
    finance: Finance = Relationship(back_populates="items")