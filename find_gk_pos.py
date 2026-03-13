
import pandas as pd

excel_path = 'Scouts Pós R5 2026.xlsx'
df = pd.read_excel(excel_path, sheet_name='Por jogo')

# Vamos listar os PosReal únicos e alguns exemplos de cada
print("--- Mapeamento de Posições (PosReal) ---")
for pos in sorted(df['PosReal'].unique()):
    exemplo = df[df['PosReal'] == pos].head(3)
    # Tentar identificar qual posição é Goleiro (quem tem DE > 0 ou SG > 0)
    gks_in_pos = df[(df['PosReal'] == pos) & ((df['DE'] > 0) | (df['SG'] > 0))]
    print(f"PosReal: {pos} | Amostra: {exemplo['Nome2'].tolist()} | Jogadores com scouts de GK: {len(gks_in_pos)}")

# Procurar por nomes conhecidos de goleiros se necessário
known_gks = ['Weverton', 'Everson', 'Rossi', 'Fabio', 'Bento', 'Rochet', 'Cássio', 'João Paulo', 'Marcos Felipe', 'Léo Jardim']
for gk in known_gks:
    found = df[df['Nome2'].str.contains(gk, case=False, na=False)]
    if not found.empty:
        print(f"\nGoleiro Encontrado: {found['Nome2'].iloc[0]} | PosReal: {found['PosReal'].iloc[0]}")
        break
