import pandas as pd
from data_processor import DataProcessor

excel = 'Scouts Pós R5 2026.xlsx'
rounds = 'RODADAS_BRASILEIRAO_2026.txt'
proc = DataProcessor(excel, rounds)

N_JOGOS = 5
MODO = 'sequential' 

print("=== PROVA REAL LATERAIS: 4 JOGOS DA RODADA 6 ===")

matches = proc.get_round_matches(6)[:4]

for match in matches:
    mandante = match['Mandante']
    visitante = match['Visitante']
        
    print(f"\n=======================================================")
    print(f"CONFRONTO: {mandante} (CASA) x {visitante} (FORA)")
    print(f"=======================================================")

    ced_ld_casa = proc.filter_cedidos(mandante, n_games=N_JOGOS, mode=MODO, mando=None, pos_real=2.2)
    ced_le_casa = proc.filter_cedidos(mandante, n_games=N_JOGOS, mode=MODO, mando=None, pos_real=2.6)

    print(f"[BLOCO 1 & 2] MANDANTE ({mandante}) CEDE PARA LATERAIS ADVERSÁRIOS:")
    print(f"  LE <- Pts: {ced_le_casa['Pts']:.1f} | DS: {ced_le_casa['DS']} | PG: {ced_le_casa['PG']}")
    print(f"  LD <- Pts: {ced_ld_casa['Pts']:.1f} | DS: {ced_ld_casa['DS']} | PG: {ced_ld_casa['PG']}")

    # Verificar FORÇA BRUTA (Cedidos LE do MANDANTE)
    dates_mand = proc._get_recent_game_dates(mandante, N_JOGOS, MODO, None)
    ds_le_bruta = 0
    ds_ld_bruta = 0
    for d in dates_mand:
        adv = proc.df_jogo[(proc.df_jogo['Time'] == mandante) & (proc.df_jogo['Data'] == d)]['Adversário'].iloc[0]
        df_adv_le = proc.df_jogo[(proc.df_jogo['Time'] == adv) & (proc.df_jogo['Data'] == d) & (proc.df_jogo['PosReal'] == 2.6)]
        df_adv_ld = proc.df_jogo[(proc.df_jogo['Time'] == adv) & (proc.df_jogo['Data'] == d) & (proc.df_jogo['PosReal'] == 2.2)]
        if not df_adv_le.empty and 'DS' in df_adv_le.columns: ds_le_bruta += df_adv_le['DS'].sum()
        if not df_adv_ld.empty and 'DS' in df_adv_ld.columns: ds_ld_bruta += df_adv_ld['DS'].sum()

    print(f"  >> PROVA REAL DS CEDIDO: LE={ds_le_bruta} (Platforma: {ced_le_casa['DS']}) | LD={ds_ld_bruta} (Plataforma: {ced_ld_casa['DS']})")
    if ds_le_bruta == ced_le_casa['DS'] and ds_ld_bruta == ced_ld_casa['DS']:
        print("     [OK] Os Desarmes Cedidos pelo Mandante batem 100%!")
    else:
        print("     [ERRO] Divergência encontrada!")

    ced_ld_fora = proc.filter_cedidos(visitante, n_games=N_JOGOS, mode=MODO, mando=None, pos_real=2.2)
    ced_le_fora = proc.filter_cedidos(visitante, n_games=N_JOGOS, mode=MODO, mando=None, pos_real=2.6)

    print(f"\n[BLOCO 3 & 4] VISITANTE ({visitante}) CEDE PARA LATERAIS ADVERSÁRIOS:")
    print(f"  LD <- Pts: {ced_ld_fora['Pts']:.1f} | DS: {ced_ld_fora['DS']} | PG: {ced_ld_fora['PG']}")
    print(f"  LE <- Pts: {ced_le_fora['Pts']:.1f} | DS: {ced_le_fora['DS']} | PG: {ced_le_fora['PG']}")

    sg_coletivo_fora_engine = ced_le_fora['SG'] if ced_le_fora['SG'] >= ced_ld_fora['SG'] else ced_ld_fora['SG']
    sg_count = 0
    dates_vis = proc._get_recent_game_dates(visitante, N_JOGOS, MODO, None)
    for d in dates_vis:
        adv = proc.df_jogo[(proc.df_jogo['Time'] == visitante) & (proc.df_jogo['Data'] == d)]['Adversário'].iloc[0]
        df_adv_def = proc.df_jogo[(proc.df_jogo['Time'] == adv) & (proc.df_jogo['Data'] == d)]
        if df_adv_def['SG'].max() > 0:
            sg_count += 1
            
    print(f"  >> PROVA REAL SG CEDIDO pelo {visitante} (Adversários que não tomaram gol):")
    print(f"     Engine={sg_coletivo_fora_engine} | Manual={sg_count}")
    if sg_coletivo_fora_engine == sg_count:
        print("     [OK] O Saldo de Gols Coletivo (Bônus) bate 100%!")
    else:
         print("     [ERRO] Divergência encontrada no SG!")
