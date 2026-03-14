
import streamlit as st
import pandas as pd
from data_processor import DataProcessor
import os
import io

st.set_page_config(page_title="MD3 - Plataforma de Scouts", layout="wide")

st.title("🏆 MD3 - Análise de Scouts Conquistados e Cedidos")
st.markdown("---")

st.sidebar.header("Configurações do Filtro")

default_excel = 'Scouts Pós R5 2026.xlsx'
default_rounds = 'RODADAS_BRASILEIRAO_2026.txt'

st.sidebar.markdown("### Base de Dados")
uploaded_file = st.sidebar.file_uploader("Upload da Planilha de Scouts (.xlsx)", type=['xlsx'])

# Usa o arquivo upado (em RAM) se existir, senão usa o padrão do disco
excel_data = uploaded_file if uploaded_file else default_excel

if (uploaded_file or os.path.exists(default_excel)) and os.path.exists(default_rounds):
    processor = DataProcessor(excel_data, default_rounds)
    
    selected_round = st.sidebar.selectbox("Rodada de Referência", 
                                         options=[r['Rodada'] for r in processor.rounds_data],
                                         index=5) 
    
    n_games = st.sidebar.number_input("Últimos N jogos", min_value=1, max_value=20, value=5)
    
    filter_mode = st.sidebar.radio("Modo de Filtro", ["Sequencial (Todos)", "Por Mando (Casa/Fora)"])
    mode_key = 'mando' if filter_mode == "Por Mando (Casa/Fora)" else 'sequential'

    # Seletor de Tabela / Posição
    view_type = st.sidebar.selectbox("Tabela para Extração", ["Goleiros", "Zagueiros", "Laterais", "Meias", "Atacantes", "Volantes"])
    
    pos_real_map = {
        "Goleiros": 1.0,
        "Zagueiros": 3.0,
        "Laterais": {"LD": 2.2, "LE": 2.6},
        "Meias": 4.0,
        "Atacantes": 5.0,
        "Volantes": 4.0
    }
    
    st.header(f"Análise {view_type} - Rodada {selected_round}")

    matches = processor.get_round_matches(selected_round)
    
    if matches:
        results = []
        for match in matches:
            mandante = match['Mandante']
            visitante = match['Visitante']
            
            # Montagem estrutural baseada na Tabela Selecionada
            if view_type == "Goleiros":
                pos_real = pos_real_map[view_type]
                c_fora = processor.filter_scouts(visitante, n_games, mode=mode_key, mando='Fora', pos_real=pos_real)
                ced_casa = processor.filter_cedidos(mandante, n_games, mode=mode_key, mando='Casa', pos_real=pos_real)
                ced_fora = processor.filter_cedidos(visitante, n_games, mode=mode_key, mando='Fora', pos_real=pos_real)
                c_casa = processor.filter_scouts(mandante, n_games, mode=mode_key, mando='Casa', pos_real=pos_real)
                
                row = {
                    "Pts Conq Fora": f"{c_fora['Pts']:.1f}",
                    "DE Conq Fora": c_fora['DE'],
                    "SG Conq Fora": c_fora['SG'],
                    "Pts Ced Casa": f"{ced_casa['Pts']:.1f}",
                    "DE Ced Casa": ced_casa['DE'],
                    "SG Ced Casa": ced_casa['SG'],
                    "MANDANTE": mandante,
                    "VISITANTE": visitante,
                    "Pts Ced Fora": f"{ced_fora['Pts']:.1f}",
                    "DE Ced Fora": ced_fora['DE'],
                    "SG Ced Fora": ced_fora['SG'],
                    "Pts Conq Casa": f"{c_casa['Pts']:.1f}",
                    "DE Conq Casa": c_casa['DE'],
                    "SG Conq Casa": c_casa['SG']
                }
            elif view_type == "Zagueiros":
                pos_real = pos_real_map[view_type]
                c_fora = processor.filter_scouts(visitante, n_games, mode=mode_key, mando='Fora', pos_real=pos_real)
                ced_casa = processor.filter_cedidos(mandante, n_games, mode=mode_key, mando='Casa', pos_real=pos_real)
                ced_fora = processor.filter_cedidos(visitante, n_games, mode=mode_key, mando='Fora', pos_real=pos_real)
                c_casa = processor.filter_scouts(mandante, n_games, mode=mode_key, mando='Casa', pos_real=pos_real)
                
                row = {
                    "Pts Conq Fora": f"{c_fora['Pts']:.1f}",
                    "Pts Ced Casa": f"{ced_casa['Pts']:.1f}",
                    "Chutes Ced Casa": ced_casa['Chutes'],
                    "PG Ced Casa": ced_casa['PG'],
                    "DS Ced Casa": ced_casa['DS'],
                    "SG Ced Casa": ced_casa['SG'],
                    "MANDANTE": mandante,
                    "VISITANTE": visitante,
                    "SG Ced Fora": ced_fora['SG'],
                    "DS Ced Fora": ced_fora['DS'],
                    "PG Ced Fora": ced_fora['PG'],
                    "Chutes Ced Fora": ced_fora['Chutes'],
                    "Pts Ced Fora": f"{ced_fora['Pts']:.1f}",
                    "Pts Conq Casa": f"{c_casa['Pts']:.1f}"
                }
            elif view_type == "Laterais":
                # Laterais separa direita (LD=2.2) e esquerda (LE=2.6) e TUDO é CEDIDO.
                pos_ld = pos_real_map["Laterais"]["LD"]
                pos_le = pos_real_map["Laterais"]["LE"]
                
                # O que o Mandante cede para os LD e LE
                ced_ld_casa = processor.filter_cedidos(mandante, n_games, mode=mode_key, mando='Casa', pos_real=pos_ld)
                ced_le_casa = processor.filter_cedidos(mandante, n_games, mode=mode_key, mando='Casa', pos_real=pos_le)
                
                # O que o Visitante cede para os LD e LE
                ced_ld_fora = processor.filter_cedidos(visitante, n_games, mode=mode_key, mando='Fora', pos_real=pos_ld)
                ced_le_fora = processor.filter_cedidos(visitante, n_games, mode=mode_key, mando='Fora', pos_real=pos_le)
                
                # SG Coletivo da defesa adversária (basta pegar de um dos lados, pois é relativo ao time)
                # (Se o LD adversário teve SG, então o time inteiro também teve o bônus)
                sg_casa = ced_le_casa['SG'] if ced_le_casa['SG'] >= ced_ld_casa['SG'] else ced_ld_casa['SG']
                sg_fora = ced_le_fora['SG'] if ced_le_fora['SG'] >= ced_ld_fora['SG'] else ced_ld_fora['SG']
                
                row = {
                    "Pts Ced LE Casa": f"{ced_le_casa['Pts']:.1f}",
                    "DS Ced LE Casa": ced_le_casa['DS'],
                    "PG Ced LE Casa": ced_le_casa['PG'],
                    
                    "Pts Ced LD Casa": f"{ced_ld_casa['Pts']:.1f}",
                    "DS Ced LD Casa": ced_ld_casa['DS'],
                    "PG Ced LD Casa": ced_ld_casa['PG'],
                    
                    "SG Ced Casa": sg_casa,
                    "MANDANTE": mandante,
                    "VISITANTE": visitante,
                    "SG Ced Fora": sg_fora,
                    
                    "PG Ced LD Fora": ced_ld_fora['PG'],
                    "DS Ced LD Fora": ced_ld_fora['DS'],
                    "Pts Ced LD Fora": f"{ced_ld_fora['Pts']:.1f}",
                    
                    "PG Ced LE Fora": ced_le_fora['PG'],
                    "DS Ced LE Fora": ced_le_fora['DS'],
                    "Pts Ced LE Fora": f"{ced_le_fora['Pts']:.1f}"
                }
            elif view_type == "Meias":
                pos_real = pos_real_map[view_type]
                role = "MEIA"
                
                c_fora = processor.filter_scouts(visitante, n_games, mode=mode_key, mando='Fora', pos_real=pos_real, role_filter=role)
                ced_casa = processor.filter_cedidos(mandante, n_games, mode=mode_key, mando='Casa', pos_real=pos_real, role_filter=role)
                ced_fora = processor.filter_cedidos(visitante, n_games, mode=mode_key, mando='Fora', pos_real=pos_real, role_filter=role)
                c_casa = processor.filter_scouts(mandante, n_games, mode=mode_key, mando='Casa', pos_real=pos_real, role_filter=role)
                
                # Matriz com 14 colunas rigorosas para Meias (Foco em Gols, Assistencias e Chutes)
                row = {
                    "Chutes Conq Fora": c_fora['Chutes'],
                    "Assistências Conq Fora": c_fora['A'],
                    "Gols Conq Fora": c_fora['G'],
                    
                    "Chutes Ced Casa": ced_casa['Chutes'],
                    "Assistências Ced Casa": ced_casa['A'],
                    "Gols Ced Casa": ced_casa['G'],
                    
                    "MANDANTE": mandante,
                    "VISITANTE": visitante,
                    
                    "Gols Ced Fora": ced_fora['G'],
                    "Assistências Ced Fora": ced_fora['A'],
                    "Chutes Ced Fora": ced_fora['Chutes'],
                    
                    "Gols Conq Casa": c_casa['G'],
                    "Assistências Conq Casa": c_casa['A'],
                    "Chutes Conq Casa": c_casa['Chutes']
                }
            elif view_type == "Atacantes":
                pos_real = pos_real_map[view_type]
                
                c_fora = processor.filter_scouts(visitante, n_games, mode=mode_key, mando='Fora', pos_real=pos_real)
                ced_casa = processor.filter_cedidos(mandante, n_games, mode=mode_key, mando='Casa', pos_real=pos_real)
                ced_fora = processor.filter_cedidos(visitante, n_games, mode=mode_key, mando='Fora', pos_real=pos_real)
                c_casa = processor.filter_scouts(mandante, n_games, mode=mode_key, mando='Casa', pos_real=pos_real)
                
                # Matriz com 14 colunas rigorosas para Atacantes (Idêntico a Meias)
                row = {
                    "Chutes Conq Fora": c_fora['Chutes'],
                    "Assistências Conq Fora": c_fora['A'],
                    "Gols Conq Fora": c_fora['G'],
                    
                    "Chutes Ced Casa": ced_casa['Chutes'],
                    "Assistências Ced Casa": ced_casa['A'],
                    "Gols Ced Casa": ced_casa['G'],
                    
                    "MANDANTE": mandante,
                    "VISITANTE": visitante,
                    
                    "Gols Conq Casa": c_casa['G'],
                    "Assistências Conq Casa": c_casa['A'],
                    "Chutes Conq Casa": c_casa['Chutes']
                }
            elif view_type == "Volantes":
                pos_real = pos_real_map[view_type]
                role = "VOLANTE"
                
                c_fora = processor.filter_scouts(visitante, n_games, mode=mode_key, mando='Fora', pos_real=pos_real, role_filter=role)
                ced_casa = processor.filter_cedidos(mandante, n_games, mode=mode_key, mando='Casa', pos_real=pos_real, role_filter=role)
                ced_fora = processor.filter_cedidos(visitante, n_games, mode=mode_key, mando='Fora', pos_real=pos_real, role_filter=role)
                c_casa = processor.filter_scouts(mandante, n_games, mode=mode_key, mando='Casa', pos_real=pos_real, role_filter=role)
                
                # Matriz minimalista de 10 colunas para Volantes (Pontos e Desarmes)
                row = {
                    "Pontos Conq Fora": f"{c_fora['Pts']:.1f}",
                    "Desarmes Conq Fora": c_fora['DS'],
                    "Pontos Ced Casa": f"{ced_casa['Pts']:.1f}",
                    "Desarmes Ced Casa": ced_casa['DS'],
                    "MANDANTE": mandante,
                    "VISITANTE": visitante,
                    "Desarmes Ced Fora": ced_fora['DS'],
                    "Pontos Ced Fora": f"{ced_fora['Pts']:.1f}",
                    "Desarmes Conq Casa": c_casa['DS'],
                    "Pontos Conq Casa": f"{c_casa['Pts']:.1f}"
                }
                
            results.append(row)

            
        df_res = pd.DataFrame(results)
        
        st.subheader(f"Visualização da Tabela de {view_type}")
        st.dataframe(df_res, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            csv = df_res.to_csv(index=False).encode('utf-8-sig')
            st.download_button(label="Baixar em CSV", data=csv, file_name=f"{view_type.lower()}_rodada_{selected_round}.csv", mime="text/csv", use_container_width=True)
            
        with col2:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_res.to_excel(writer, index=False, sheet_name=view_type)
            
            st.download_button(label="Baixar em EXCEL (.xlsx)", data=buffer.getvalue(), file_name=f"{view_type.lower()}_rodada_{selected_round}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    else:
        st.warning("Nenhum confronto encontrado.")

else:
    st.error("Por favor, faça o upload de uma Planilha de Scouts ou certifique-se de que o arquivo padrão existe na pasta.")
