import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import pandas as pd
from datetime import datetime

# Configuração do banco de dados SQLite
DATABASE_URL = "sqlite:///finance.db"

Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

# Estrutura das Entidades
class Caixa(Base):
    __tablename__ = "caixas"
    id = Column(Integer, primary_key=True, index=True)
    caixa_aberto = Column(String, unique=True)
    data = Column(Date)
    saldo_inicial = Column(Float)
    valor_cartao_credito = Column(Float, default=0)
    valor_cartao_debito = Column(Float, default=0)
    valor_ifood = Column(Float, default=0)
    valor_dinheiro = Column(Float)
    valor_fiado = Column(Float, default=0)
    saidas_caixa = Column(Float)
    valor_acrescimo = Column(Float, default=0)
    fechamento_do_caixa = Column(Float, default=0)
    movimentos = relationship("Movimentos", back_populates="caixa")
    op_credito = relationship("OpCredito", back_populates="caixa")

class OperadoraCredito(Base):
    __tablename__ = "operadoras_credito"
    id = Column(Integer, primary_key=True, index=True)
    nome_operadora = Column(String, unique=True)
    op_credito = relationship("OpCredito", back_populates="operadora")

class OpCredito(Base):
    __tablename__ = "op_creditos"
    id = Column(Integer, primary_key=True, index=True)
    id_caixa = Column(Integer, ForeignKey('caixas.id'))
    id_operadora = Column(Integer, ForeignKey('operadoras_credito.id'))
    data_extrato = Column(Date)
    total_credito = Column(Float)
    total_debito = Column(Float)
    valor_pix = Column(Float, default=0)
    valor_voucher = Column(Float, default=0)
    caixa = relationship("Caixa", back_populates="op_credito")
    operadora = relationship("OperadoraCredito", back_populates="op_credito")

class Movimentos(Base):
    __tablename__ = "movimentos"
    id = Column(Integer, primary_key=True, index=True)
    id_caixa = Column(Integer, ForeignKey('caixas.id'))
    tipo_movimento = Column(String)
    valor = Column(Float)
    data_hora = Column(Date)
    descricao = Column(String)
    caixa = relationship("Caixa", back_populates="movimentos")

# Drop and create tables
# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Funções de CRUD
def create_caixa(caixa_aberto, data, saldo_inicial, valor_cartao_credito, valor_cartao_debito, valor_ifood, valor_dinheiro, valor_fiado, saidas_caixa, valor_acrescimo):
    fechamento_do_caixa = saldo_inicial + valor_cartao_credito + valor_cartao_debito + valor_ifood + valor_dinheiro + valor_fiado + valor_acrescimo - saidas_caixa
    db_caixa = Caixa(
        caixa_aberto=caixa_aberto,
        data=data,
        saldo_inicial=saldo_inicial,
        valor_cartao_credito=valor_cartao_credito,
        valor_cartao_debito=valor_cartao_debito,
        valor_ifood=valor_ifood,
        valor_dinheiro=valor_dinheiro,
        valor_fiado=valor_fiado,
        saidas_caixa=saidas_caixa,
        valor_acrescimo=valor_acrescimo,
        fechamento_do_caixa=fechamento_do_caixa
    )
    session.add(db_caixa)
    session.commit()
    session.refresh(db_caixa)
    return db_caixa

def get_caixas():
    return session.query(Caixa).all()

def create_operadora_credito(nome_operadora):
    db_operadora = OperadoraCredito(nome_operadora=nome_operadora)
    session.add(db_operadora)
    session.commit()
    session.refresh(db_operadora)
    return db_operadora

def get_operadoras_credito():
    return session.query(OperadoraCredito).all()

def create_op_credito(id_caixa, id_operadora, data_extrato, total_credito, total_debito, valor_pix, valor_voucher):
    db_op_credito = OpCredito(
        id_caixa=id_caixa,
        id_operadora=id_operadora,
        data_extrato=data_extrato,
        total_credito=total_credito,
        total_debito=total_debito,
        valor_pix=valor_pix,
        valor_voucher=valor_voucher
    )
    session.add(db_op_credito)
    session.commit()
    session.refresh(db_op_credito)
    return db_op_credito

def get_op_creditos():
    return session.query(OpCredito).all()

def create_movimento(id_caixa, tipo_movimento, valor, data_hora, descricao):
    db_movimento = Movimentos(
        id_caixa=id_caixa,
        tipo_movimento=tipo_movimento,
        valor=valor,
        data_hora=data_hora,
        descricao=descricao
    )
    session.add(db_movimento)
    session.commit()
    session.refresh(db_movimento)
    return db_movimento

def get_movimentos():
    return session.query(Movimentos).all()

# Funções utilitárias
def format_currency(value):
    return f"{value:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

def parse_currency(value):
    return float(value.replace(".", "").replace(",", "."))

# Interface do Streamlit
st.sidebar.title("Menu")
menu = st.sidebar.selectbox("Selecione a Entidade", ["Caixa", "Operadora_Credito", "Op_Credito", "Movimentos"])
crud_operation = st.sidebar.selectbox("Selecione a Operação", ["Create", "Update", "Delete", "List"])

def clear_inputs_caixa():
    st.session_state["caixa_aberto"] = ""
    st.session_state["data"] = datetime.now()
    st.session_state["saldo_inicial"] = "0,00"
    st.session_state["valor_cartao_credito"] = "0,00"
    st.session_state["valor_cartao_debito"] = "0,00"
    st.session_state["valor_ifood"] = "0,00"
    st.session_state["valor_dinheiro"] = "0,00"
    st.session_state["valor_fiado"] = "0,00"
    st.session_state["saidas_caixa"] = "0,00"
    st.session_state["valor_acrescimo"] = "0,00"

def clear_inputs_movimento():
    st.session_state["tipo_movimento"] = ""
    st.session_state["valor_movimento"] = "0,00"
    st.session_state["data_hora"] = datetime.now()
    st.session_state["descricao"] = ""

if menu == "Caixa":
    if crud_operation == "Create":
        st.subheader("Create Caixa")
        caixa_aberto = st.text_input("Caixa Aberto", key="caixa_aberto")
        data = st.date_input("Data", value=datetime.now(), key="data")
        saldo_inicial = st.text_input("Saldo Inicial", "0,00", key="saldo_inicial")
        valor_cartao_credito = st.text_input("Valor Cartão de Crédito", "0,00", key="valor_cartao_credito")
        valor_cartao_debito = st.text_input("Valor Cartão de Débito", "0,00", key="valor_cartao_debito")
        valor_ifood = st.text_input("Valor de Ifood", "0,00", key="valor_ifood")
        valor_dinheiro = st.text_input("Valor em Dinheiro", "0,00", key="valor_dinheiro")
        valor_fiado = st.text_input("Valor Fiado", "0,00", key="valor_fiado")
        saidas_caixa = st.text_input("Saídas de Caixa", "0,00", key="saidas_caixa")
        valor_acrescimo = st.text_input("Valor de Acréscimo", "0,00", key="valor_acrescimo")
        
        # Calculando Fechamento do Caixa
        try:
            fechamento_do_caixa = parse_currency(saldo_inicial) + parse_currency(valor_cartao_credito) + parse_currency(valor_cartao_debito) + parse_currency(valor_ifood) + parse_currency(valor_dinheiro) + parse_currency(valor_fiado) + parse_currency(valor_acrescimo) - parse_currency(saidas_caixa)
        except ValueError:
            fechamento_do_caixa = 0.0
        
        st.text(f"Fechamento do Caixa: {format_currency(fechamento_do_caixa)}")

        if st.button("Create Caixa"):
            create_caixa(
                st.session_state["caixa_aberto"],
                st.session_state["data"], 
                parse_currency(st.session_state["saldo_inicial"]), 
                parse_currency(st.session_state["valor_cartao_credito"]), 
                parse_currency(st.session_state["valor_cartao_debito"]), 
                parse_currency(st.session_state["valor_ifood"]), 
                parse_currency(st.session_state["valor_dinheiro"]), 
                parse_currency(st.session_state["valor_fiado"]), 
                parse_currency(st.session_state["saidas_caixa"]), 
                parse_currency(st.session_state["valor_acrescimo"])
            )
            st.success("Caixa criado com sucesso!")
            # clear_inputs_caixa()
            # st.experimental_rerun()
    
    elif crud_operation == "Update":
        st.subheader("Update Caixa")
        caixa_id = st.number_input("ID do Caixa", min_value=1, step=1)
        caixa = session.query(Caixa).filter(Caixa.id == caixa_id).first()
        
        if caixa:
            caixa_aberto = st.text_input("Caixa Aberto", value=caixa.caixa_aberto)
            data = st.date_input("Data", value=caixa.data)
            saldo_inicial = st.text_input("Saldo Inicial", value=format_currency(caixa.saldo_inicial))
            valor_cartao_credito = st.text_input("Valor Cartão de Crédito", value=format_currency(caixa.valor_cartao_credito))
            valor_cartao_debito = st.text_input("Valor Cartão de Débito", value=format_currency(caixa.valor_cartao_debito))
            valor_ifood = st.text_input("Valor de Ifood", value=format_currency(caixa.valor_ifood))
            valor_dinheiro = st.text_input("Valor em Dinheiro", value=format_currency(caixa.valor_dinheiro))
            valor_fiado = st.text_input("Valor Fiado", value=format_currency(caixa.valor_fiado))
            saidas_caixa = st.text_input("Saídas de Caixa", value=format_currency(caixa.saidas_caixa))
            valor_acrescimo = st.text_input("Valor de Acréscimo", value=format_currency(caixa.valor_acrescimo))
            
            # Calculando Fechamento do Caixa
            try:
                fechamento_do_caixa = parse_currency(saldo_inicial) + parse_currency(valor_cartao_credito) + parse_currency(valor_cartao_debito) + parse_currency(valor_ifood) + parse_currency(valor_dinheiro) + parse_currency(valor_fiado) + parse_currency(valor_acrescimo) - parse_currency(saidas_caixa)
            except ValueError:
                fechamento_do_caixa = 0.0
            
            st.text(f"Fechamento do Caixa: {format_currency(fechamento_do_caixa)}")
            
            if st.button("Update Caixa"):
                caixa.caixa_aberto = caixa_aberto
                caixa.data = data
                caixa.saldo_inicial = parse_currency(saldo_inicial)
                caixa.valor_cartao_credito = parse_currency(valor_cartao_credito)
                caixa.valor_cartao_debito = parse_currency(valor_cartao_debito)
                caixa.valor_ifood = parse_currency(valor_ifood)
                caixa.valor_dinheiro = parse_currency(valor_dinheiro)
                caixa.valor_fiado = parse_currency(valor_fiado)
                caixa.saidas_caixa = parse_currency(saidas_caixa)
                caixa.valor_acrescimo = parse_currency(valor_acrescimo)
                caixa.fechamento_do_caixa = fechamento_do_caixa
                session.commit()
                st.success("Caixa atualizado com sucesso!")
        else:
            st.error("Caixa não encontrado.")
    
    elif crud_operation == "Delete":
        st.subheader("Delete Caixa")
        caixa_id = st.number_input("ID do Caixa", min_value=1, step=1)
        
        if st.button("Delete Caixa"):
            caixa = session.query(Caixa).filter(Caixa.id == caixa_id).first()
            if caixa:
                session.delete(caixa)
                session.commit()
                st.success("Caixa deletado com sucesso!")
            else:
                st.error("Caixa não encontrado.")
    
    elif crud_operation == "List":
        st.subheader("Lista de Caixas")
        caixas = get_caixas()
        caixa_data = [{"Caixa Aberto": c.caixa_aberto, "Data": c.data.strftime('%d/%m/%Y'), "Saldo Inicial": format_currency(c.saldo_inicial),
                       "Valor Cartão de Crédito": format_currency(c.valor_cartao_credito), "Valor Cartão de Débito": format_currency(c.valor_cartao_debito),
                       "Valor de Ifood": format_currency(c.valor_ifood), "Valor em Dinheiro": format_currency(c.valor_dinheiro),
                       "Valor Fiado": format_currency(c.valor_fiado), "Saídas de Caixa": format_currency(c.saidas_caixa),
                       "Valor de Acréscimo": format_currency(c.valor_acrescimo), "Fechamento do Caixa": format_currency(c.fechamento_do_caixa)} for c in caixas]
        df = pd.DataFrame(caixa_data)
        st.dataframe(df)

elif menu == "Operadora_Credito":
    if crud_operation == "Create":
        st.subheader("Create Operadora_Credito")
        nome_operadora = st.text_input("Nome da Operadora")
        
        if st.button("Create Operadora"):
            create_operadora_credito(nome_operadora)
            st.success("Operadora de Crédito criada com sucesso!")
            st.experimental_rerun()
    
    elif crud_operation == "Update":
        st.subheader("Update Operadora_Credito")
        operadora_id = st.number_input("ID da Operadora", min_value=1, step=1)
        operadora = session.query(OperadoraCredito).filter(OperadoraCredito.id == operadora_id).first()
        
        if operadora:
            nome_operadora = st.text_input("Nome da Operadora", value=operadora.nome_operadora)
            
            if st.button("Update Operadora"):
                operadora.nome_operadora = nome_operadora
                session.commit()
                st.success("Operadora de Crédito atualizada com sucesso!")
        else:
            st.error("Operadora não encontrada.")
    
    elif crud_operation == "Delete":
        st.subheader("Delete Operadora_Credito")
        operadora_id = st.number_input("ID da Operadora", min_value=1, step=1)
        
        if st.button("Delete Operadora"):
            operadora = session.query(OperadoraCredito).filter(OperadoraCredito.id == operadora_id).first()
            if operadora:
                session.delete(operadora)
                session.commit()
                st.success("Operadora de Crédito deletada com sucesso!")
            else:
                st.error("Operadora não encontrada.")
    
    elif crud_operation == "List":
        st.subheader("Lista de Operadoras de Crédito")
        operadoras = get_operadoras_credito()
        operadora_data = [{"Nome da Operadora": o.nome_operadora} for o in operadoras]
        df = pd.DataFrame(operadora_data)
        st.dataframe(df)

elif menu == "Op_Credito":
    if crud_operation == "Create":
        st.subheader("Create Op_Credito")
        caixas = get_caixas()
        operadoras = get_operadoras_credito()
        
        id_caixa = st.selectbox("ID do Caixa", [c.caixa_aberto for c in caixas])
        id_operadora = st.selectbox("Nome da Operadora", [o.nome_operadora for o in operadoras])
        data_extrato = st.date_input("Data do Extrato", value=datetime.now())
        total_credito = st.text_input("Total Crédito", "0,00")
        total_debito = st.text_input("Total Débito", "0,00")
        valor_pix = st.text_input("Valor de Pix", "0,00")
        valor_voucher = st.text_input("Valor de Voucher", "0,00")
        
        if st.button("Create Op_Credito"):
            operadora_id = next((o.id for o in operadoras if o.nome_operadora == id_operadora), None)
            create_op_credito(
                id_caixa, 
                operadora_id, 
                data_extrato, 
                parse_currency(total_credito), 
                parse_currency(total_debito), 
                parse_currency(valor_pix), 
                parse_currency(valor_voucher)
            )
            st.success("Operação de Crédito criada com sucesso!")
            st.experimental_rerun()
    
    elif crud_operation == "Update":
        st.subheader("Update Op_Credito")
        op_credito_id = st.number_input("ID da Operação de Crédito", min_value=1, step=1)
        op_credito = session.query(OpCredito).filter(OpCredito.id == op_credito_id).first()
        
        if op_credito:
            caixas = get_caixas()
            operadoras = get_operadoras_credito()
            
            id_caixa = st.selectbox("ID do Caixa", [c.id for c in caixas], index=[c.id for c in caixas].index(op_credito.id_caixa))
            id_operadora = st.selectbox("Nome da Operadora", [o.nome_operadora for o in operadoras], index=[o.nome_operadora for o in operadoras].index(op_credito.operadora.nome_operadora))
            data_extrato = st.date_input("Data do Extrato", value=op_credito.data_extrato)
            total_credito = st.text_input("Total Crédito", value=format_currency(op_credito.total_credito))
            total_debito = st.text_input("Total Débito", value=format_currency(op_credito.total_debito))
            valor_pix = st.text_input("Valor de Pix", value=format_currency(op_credito.valor_pix))
            valor_voucher = st.text_input("Valor de Voucher", value=format_currency(op_credito.valor_voucher))
            
            if st.button("Update Op_Credito"):
                operadora_id = next((o.id for o in operadoras if o.nome_operadora == id_operadora), None)
                op_credito.id_caixa = id_caixa
                op_credito.id_operadora = operadora_id
                op_credito.data_extrato = data_extrato
                op_credito.total_credito = parse_currency(total_credito)
                op_credito.total_debito = parse_currency(total_debito)
                op_credito.valor_pix = parse_currency(valor_pix)
                op_credito.valor_voucher = parse_currency(valor_voucher)
                session.commit()
                st.success("Operação de Crédito atualizada com sucesso!")
        else:
            st.error("Operação de Crédito não encontrada.")
    
    elif crud_operation == "Delete":
        st.subheader("Delete Op_Credito")
        op_credito_id = st.number_input("ID da Operação de Crédito", min_value=1, step=1)
        
        if st.button("Delete Op_Credito"):
            op_credito = session.query(OpCredito).filter(OpCredito.id == op_credito_id).first()
            if op_credito:
                session.delete(op_credito)
                session.commit()
                st.success("Operação de Crédito deletada com sucesso!")
            else:
                st.error("Operação de Crédito não encontrada.")
    
    elif crud_operation == "List":
        st.subheader("Lista de Operações de Crédito")
        op_creditos = get_op_creditos()
        op_credito_data = [{"ID do Caixa": o.id_caixa, "Nome da Operadora": o.operadora.nome_operadora, "Data do Extrato": o.data_extrato.strftime('%d/%m/%Y'),
                            "Total Crédito": format_currency(o.total_credito), "Total Débito": format_currency(o.total_debito),
                            "Valor de Pix": format_currency(o.valor_pix), "Valor de Voucher": format_currency(o.valor_voucher)} for o in op_creditos]
        df = pd.DataFrame(op_credito_data)
        st.dataframe(df)

elif menu == "Movimentos":
    if crud_operation == "Create":
        st.subheader("Create Movimento")
        caixas = get_caixas()
   
        
        id_caixa = st.selectbox("ID do Caixa", [c.caixa_aberto for c in caixas])
        tipo_movimento = st.text_input("Tipo de Movimento", key="tipo_movimento")
        valor = st.text_input("Valor", "0,00", key="valor_movimento")
        data_hora = st.date_input("Data e Hora", value=datetime.now(), key="data_hora")
        descricao = st.text_input("Descrição", key="descricao")
       
        if st.button("Create Movimento"):
            create_movimento(
                st.session_state["id_caixa"], 
                st.session_state["tipo_movimento"], 
                parse_currency(st.session_state["valor_movimento"]), 
                st.session_state["data_hora"], 
                st.session_state["descricao"]
            )
            st.success("Movimento criado com sucesso!")
            # clear_inputs_movimento()
            # st.experimental_rerun()
    
    elif crud_operation == "Update":
        st.subheader("Update Movimento")
        movimento_id = st.number_input("ID do Movimento", min_value=1, step=1)
        movimento = session.query(Movimentos).filter(Movimentos.id == movimento_id).first()
        
        if movimento:
            id_caixa = st.selectbox("ID do Caixa", [c.id for c in get_caixas()], index=[c.id for c in get_caixas()].index(movimento.id_caixa))
            tipo_movimento = st.text_input("Tipo de Movimento", value=movimento.tipo_movimento)
            valor = st.text_input("Valor", value=format_currency(movimento.valor))
            data_hora = st.date_input("Data e Hora", value=movimento.data_hora)
            descricao = st.text_input("Descrição", value=movimento.descricao)
            
            if st.button("Update Movimento"):
                movimento.id_caixa = id_caixa
                movimento.tipo_movimento = tipo_movimento
                movimento.valor = parse_currency(valor)
                movimento.data_hora = data_hora
                movimento.descricao = descricao
                session.commit()
                st.success("Movimento atualizado com sucesso!")
        else:
            st.error("Movimento não encontrado.")
    
    elif crud_operation == "Delete":
        st.subheader("Delete Movimento")
        movimento_id = st.number_input("ID do Movimento", min_value=1, step=1)
        
        if st.button("Delete Movimento"):
            movimento = session.query(Movimentos).filter(Movimentos.id == movimento_id).first()
            if movimento:
                session.delete(movimento)
                session.commit()
                st.success("Movimento deletado com sucesso!")
            else:
                st.error("Movimento não encontrado.")
    
    elif crud_operation == "List":
        st.subheader("Lista de Movimentos")
        movimentos = get_movimentos()
        movimento_data = [{"ID do Caixa": m.id_caixa, "Tipo de Movimento": m.tipo_movimento, "Valor": format_currency(m.valor),
                           "Data e Hora": m.data_hora.strftime('%d/%m/%Y'), "Descrição": m.descricao} for m in movimentos]
        df = pd.DataFrame(movimento_data)
        st.dataframe(df)



        