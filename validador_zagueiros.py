
import pandas as pd
from data_processor import DataProcessor

excel = 'Scouts Pós R5 2026.xlsx'
rounds = 'RODADAS_BRASILEIRAO_2026.txt'
proc = DataProcessor(excel, rounds)

N_JOGOS = 5
MODO = 'sequential' 
MANDO = None 

print("=== PROVA REAL ZAGUEIROS: 1 JOGO DA RODADA 6 ===")
print(f"Filtro: {N_JOGOS} jogos | Módulo: PosReal 3.0 (Zagueiros)")

# Vamos pegar 1 confronto só para auditoria profunda de todos os 5 parâmetros
match = proc.get_round_matches(6)[0]
mandante = match['Mandante']
visitante = match['Visitante']
    
print(f"\n=======================================================")
print(f"CONFRONTO: {mandante} (CASA) x {visitante} (FORA)")
print(f"=======================================================")

# CONQUISTADOS FORA:
c_fora = proc.filter_scouts(visitante, n_games=N_JOGOS, mode=MODO, mando=MANDO, pos_real=3.0)
print(f"\n[DADOS DO ZAGUEIRO DO {visitante.upper()}] - CONQUISTADOS")
print(f"  Pts: {c_fora['Pts']:.1f}")
print(f"  Chutes Limpos pela Zaga (FF+FD+FT): {c_fora['Chutes']}")
print(f"  Part. Gols da Zaga (G+A): {c_fora['PG']}")
print(f"  Desarmes da Zaga (DS): {c_fora['DS']}")
print(f"  SG Coletivo ({visitante} não tomou gol em X jogos): {c_fora['SG']}")

# FORÇA BRUTA NO EXCEL -> VISITANTE
dates_vis = proc._get_recent_game_dates(visitante, N_JOGOS, MODO, MANDO)
df_v = proc.df_jogo[(proc.df_jogo['Time'] == visitante) & (proc.df_jogo['Data'].isin(dates_vis)) & (proc.df_jogo['PosReal'] == 3.0)]

chutes_bruta = 0
pg_bruta = 0
if 'FF' in df_v.columns: chutes_bruta = df_v['FF'].sum() + df_v['FD'].sum() + df_v['FT'].sum()
if 'G' in df_v.columns: pg_bruta = df_v['G'].sum() + df_v['A'].sum()
ds_bruta = df_v['DS'].sum() if 'DS' in df_v.columns else 0

# SG Coletivo Bruto
sg_coletivo_count = 0
for d in dates_vis:
    if proc.df_jogo[(proc.df_jogo['Time'] == visitante) & (proc.df_jogo['Data'] == d)]['SG'].max() > 0:
        sg_coletivo_count += 1

print(f"  > Prova Real: Pts={df_v.groupby('Data')['Pts'].sum().mean():.1f} | Chutes={chutes_bruta} | PG={pg_bruta} | DS={ds_bruta} | SG_Coletivo={sg_coletivo_count}")


# CEDIDOS MANDANTE:
print(f"\n[DADOS CEDIDOS PELO {mandante.upper()} AOS ZAGUEIROS ADVERSÁRIOS]")
ced_casa = proc.filter_cedidos(mandante, n_games=N_JOGOS, mode=MODO, mando=MANDO, pos_real=3.0)
print(f"  Pts Cedidos: {ced_casa['Pts']:.1f}")
print(f"  Chutes Cedidos: {ced_casa['Chutes']}")
print(f"  PG Cedidos: {ced_casa['PG']}")
print(f"  Desarmes Cedidos: {ced_casa['DS']}")
print(f"  SG Cedido (Adversários do {mandante} não tomaram gol): {ced_casa['SG']}")

# FORÇA BRUTA NO EXCEL -> CEDIDOS PELO MANDANTE
dates_mand = proc._get_recent_game_dates(mandante, N_JOGOS, MODO, MANDO)
chutes_ced = 0
pg_ced = 0
ds_ced = 0
sg_ced_count = 0
pts_ced_total = []

for d in dates_mand:
    adv = proc.df_jogo[(proc.df_jogo['Time'] == mandante) & (proc.df_jogo['Data'] == d)]['Adversário'].iloc[0]
    
    # Se o adversário fez SG
    if proc.df_jogo[(proc.df_jogo['Time'] == adv) & (proc.df_jogo['Data'] == d)]['SG'].max() > 0:
        sg_ced_count += 1
        
    df_adv_zag = proc.df_jogo[(proc.df_jogo['Time'] == adv) & (proc.df_jogo['Data'] == d) & (proc.df_jogo['PosReal'] == 3.0)]
    if not df_adv_zag.empty:
        if 'FF' in df_adv_zag.columns: chutes_ced += df_adv_zag['FF'].sum() + df_adv_zag['FD'].sum() + df_adv_zag['FT'].sum()
        if 'G' in df_adv_zag.columns: pg_ced += df_adv_zag['G'].sum() + df_adv_zag['A'].sum()
        if 'DS' in df_adv_zag.columns: ds_ced += df_adv_zag['DS'].sum()
        pts_ced_total.append(df_adv_zag['Pts'].sum())
    else:
        pts_ced_total.append(0.0)

print(f"  > Prova Real Cedidos: Pts={sum(pts_ced_total)/len(pts_ced_total):.1f} | Chutes={chutes_ced} | PG={pg_ced} | DS={ds_ced} | SG_Coletivo={sg_ced_count}")
