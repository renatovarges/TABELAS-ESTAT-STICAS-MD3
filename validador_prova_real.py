
import pandas as pd
from data_processor import DataProcessor

excel = 'Scouts Pós R5 2026.xlsx'
rounds = 'RODADAS_BRASILEIRAO_2026.txt'
proc = DataProcessor(excel, rounds)

# Parâmetros do filtro solicitado na imagem
N_JOGOS = 5
MODO = 'sequential' 
MANDO = None # Porque o modo é sequencial (todos)

print("=== PROVA REAL: AUDITORIA PROFUNDA DE 3 JOGOS (Rodada 6) ===")
print(f"Filtro: {N_JOGOS} jogos | Modo: {MODO}")

# Pegar 3 confrontos da Rodada 6
matches = proc.get_round_matches(6)[:3]

for match in matches:
    mandante = match['Mandante']
    visitante = match['Visitante']
    
    print(f"\n=======================================================")
    print(f"CONFRONTO: {mandante} (CASA) x {visitante} (FORA)")
    print(f"=======================================================")
    
    # 1. Pts Conq Fora: Visitante nos últimos 5 jogos gerais (modo sequencial)
    c_fora = proc.filter_scouts(visitante, n_games=N_JOGOS, mode=MODO, mando=MANDO, pos_real=1.0)
    print(f"\n[BLOCO 1] CONQUISTADOS FORA -> Dados do {visitante}")
    print(f"  Pts Conq Fora (Média de Pts do {visitante} em {c_fora['Jogos']} jogos): {c_fora['Pts']:.1f}")
    print(f"  DE Conq Fora (Total de Defesas do GK do {visitante}): {c_fora['DE']}")
    print(f"  SG Conq Fora (Total de SG do {visitante}): {c_fora['SG']}")
    
    # Validando na força bruta para o visitante
    dates_vis = proc._get_recent_game_dates(visitante, N_JOGOS, MODO, MANDO)
    df_v = proc.df_jogo[(proc.df_jogo['Time'] == visitante) & (proc.df_jogo['Data'].isin(dates_vis)) & (proc.df_jogo['PosReal'] == 1.0)]
    print(f"  > Prova Real (Soma direta na planilha): DE={df_v['DE'].sum()} | SG={df_v['SG'].sum()} | Pts Médio={df_v.groupby('Data')['Pts'].sum().mean():.1f}")


    # 2. Cedidos Casa: Mandante cede aos adversários nos últimos 5 jogos gerais
    ced_casa = proc.filter_cedidos(mandante, n_games=N_JOGOS, mode=MODO, mando=MANDO, pos_real=1.0)
    print(f"\n[BLOCO 2] CEDIDOS CASA -> Dados cedidos pelo {mandante}")
    print(f"  Pts Ced Casa (Média de Pts cedidos pelo {mandante} em {ced_casa['Jogos']} jogos): {ced_casa['Pts']:.1f}")
    print(f"  DE Ced Casa (Total de Defesas dos GK adversários do {mandante}): {ced_casa['DE']}")
    print(f"  SG Ced Casa (Total de SG dos adversários do {mandante}): {ced_casa['SG']}")

    
    # 3. Cedidos Fora: Visitante cede aos adversários nos últimos 5 jogos gerais
    ced_fora = proc.filter_cedidos(visitante, n_games=N_JOGOS, mode=MODO, mando=MANDO, pos_real=1.0)
    print(f"\n[BLOCO 3] CEDIDOS FORA -> Dados cedidos pelo {visitante}")
    print(f"  Pts Ced Fora (Média de Pts cedidos pelo {visitante} em {ced_fora['Jogos']} jogos): {ced_fora['Pts']:.1f}")
    print(f"  DE Ced Fora (Total de Defesas dos GK adversários do {visitante}): {ced_fora['DE']}")
    print(f"  SG Ced Fora (Total de SG dos adversários do {visitante}): {ced_fora['SG']}")
    
    
    # 4. Conquistados Casa: Mandante nos últimos 5 jogos gerais
    c_casa = proc.filter_scouts(mandante, n_games=N_JOGOS, mode=MODO, mando=MANDO, pos_real=1.0)
    print(f"\n[BLOCO 4] CONQUISTADOS CASA -> Dados do {mandante}")
    print(f"  Pts Conq Casa (Média de Pts do {mandante} em {c_casa['Jogos']} jogos): {c_casa['Pts']:.1f}")
    print(f"  DE Conq Casa (Total de Defesas do GK do {mandante}): {c_casa['DE']}")
    print(f"  SG Conq Casa (Total de SG do {mandante}): {c_casa['SG']}")
    
    # Validando na força bruta para o mandante
    dates_mand = proc._get_recent_game_dates(mandante, N_JOGOS, MODO, MANDO)
    df_m = proc.df_jogo[(proc.df_jogo['Time'] == mandante) & (proc.df_jogo['Data'].isin(dates_mand)) & (proc.df_jogo['PosReal'] == 1.0)]
    print(f"  > Prova Real (Soma direta na planilha): DE={df_m['DE'].sum()} | SG={df_m['SG'].sum()} | Pts Médio={df_m.groupby('Data')['Pts'].sum().mean():.1f}")
