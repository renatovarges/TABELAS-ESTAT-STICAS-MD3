
import pandas as pd
from data_processor import DataProcessor

excel = 'Scouts Pós R5 2026.xlsx'
rounds = 'RODADAS_BRASILEIRAO_2026.txt'
proc = DataProcessor(excel, rounds)

print("--- DEBUG: BUSCANDO GOLEIROS ADVERSÁRIOS ---")
# Vamos ver alguns jogos do Flamengo como mandante e tentar achar o goleiro do adversário
flamengo_games = proc.df_jogo[proc.df_jogo['Time'] == 'Flamengo'].head(5)

for idx, row in flamengo_games.iterrows():
    adv = row['Adversário']
    data = row['Data']
    mand = row['Mand']
    print(f"Jogo: Flamengo vs {adv} | Data: {data} | Mando: {mand}")
    
    # Busca qualquer jogador do adversário nesse jogo/data
    adv_players = proc.df_jogo[(proc.df_jogo['Time'] == adv) & (proc.df_jogo['Data'] == data)]
    print(f"  Jogadores do adversário encontrados: {len(adv_players)}")
    
    # Busca especificamente goleiros
    adv_gks = adv_players[adv_players['PosReal'] == 4.0]
    print(f"  Goleiros do adversário encontrados (PosReal 4.0): {len(adv_gks)}")
    if not adv_gks.empty:
        print(f"  DE do Goleiro: {adv_gks['DE'].tolist()}")
    else:
        # Se não achou 4.0, vamos ver quais PosReal existem para o adversário
        print(f"  PosReal existentes para {adv}: {adv_players['PosReal'].unique()}")
        print(f"  Exemplo de jogador do adversário: {adv_players[['Jogador', 'PosReal', 'DE']].head(2)}")
