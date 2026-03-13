
import pandas as pd
import numpy as np

# Configurações
excel_path = 'Scouts Pós R5 2026.xlsx'
df = pd.read_excel(excel_path, sheet_name='Por jogo')

# Auditoria de um time específico: Flamengo
team = 'Flamengo'
print(f"--- Auditoria: {team} ---")

# Colunas disponíveis
cols = df.columns.tolist()
name_col = 'Nome2' if 'Nome2' in cols else ('Jogador' if 'Jogador' in cols else cols[0])
print(f"Usando coluna de nome: {name_col}")

df_team = df[df['Time'] == team].copy()
df_team['Data'] = pd.to_datetime(df_team['Data'])
df_team = df_team.sort_values(by='Data', ascending=False)

# Forma CORRETA: Filtrar as DATAS primeiro para pegar as partidas e não as linhas
recent_dates = df_team['Data'].unique()[:5]

print(f"Datas únicas para {team}: {len(df_team['Data'].unique())}")

for date in recent_dates:
    game_data = df_team[df_team['Data'] == date]
    opponent = game_data['Adversário'].iloc[0]
    mando = game_data['Mand'].iloc[0]
    # Goleiro: PosReal 4.0
    goleiros = game_data[game_data['PosReal'] == 4.0]
    
    print(f"\nData: {date} | Adversário: {opponent} | Mando: {mando}")
    print(f"  Goleiros encontrados: {goleiros[name_col].tolist()}")
    print(f"  DE do(s) Goleiro(s) (Bruto): {goleiros['DE'].tolist()}")
    print(f"  SG do(s) Goleiro(s) (Bruto): {goleiros['SG'].tolist()}")
    
    # Simular o processamento que fiz no motor
    de_sum = pd.to_numeric(goleiros['DE'], errors='coerce').fillna(0).sum()
    sg_sum = pd.to_numeric(goleiros['SG'], errors='coerce').fillna(0).sum()
    print(f"  DE Processado: {de_sum}")
    print(f"  SG Processado: {sg_sum}")

print("\n--- TESTE DE IDENTIFICAÇÃO DE GOLEIRO ---")
# Vamos ver alguns registros de quem tem PosReal 4.0
gks_all = df[df['PosReal'] == 4.0].head(10)
print(gks_all[['Time', name_col, 'PosReal', 'DE', 'SG', 'Pts']])
