
import pandas as pd
from data_processor import DataProcessor

excel = 'Scouts Pós R5 2026.xlsx'
rounds = 'RODADAS_BRASILEIRAO_2026.txt'
proc = DataProcessor(excel, rounds)

N_JOGOS = 5
MODO = 'sequential' 
POS_REAL = 4.0 # Volantes e Meias Misturados Internamente

print("=== PROVA REAL VOLANTES (Com Filtro Reverso CSV): 1 JOGO DA RODADA 6 ===")

matches = proc.get_round_matches(6)
match = None
for m in matches:
    if m['Mandante'] == 'Palmeiras':
        match = m
        break

if not match:
    print("Jogo do Palmeiras não encontrado!")
    exit()

mandante = match['Mandante']
visitante = match['Visitante']
    
print(f"\nCONFRONTO: {mandante} (CASA) x {visitante} (FORA)\n")

# Extração da Plataforma Oficial (FILTRO: APENAS VOLANTES)
c_casa_volantes = proc.filter_scouts(mandante, n_games=N_JOGOS, mode=MODO, mando=None, pos_real=POS_REAL, role_filter="VOLANTE")

print(f"[VOLANTES DE OFÍCIO DO {mandante} - CONQUISTADOS]")
print(f"  Média Pts: {c_casa_volantes['Pts']:.1f} | Desarmes: {c_casa_volantes['DS']}")

# Extração Bruta SEM CSV (Sujo com Meias)
c_casa_tudo = proc.filter_scouts(mandante, n_games=N_JOGOS, mode=MODO, mando=None, pos_real=POS_REAL)

print(f"\n[TODOS DA POS 4.0 DO {mandante} - (Cruza Volantes + Meias!)]")
print(f"  Média Pts: {c_casa_tudo['Pts']:.1f} | Desarmes: {c_casa_tudo['DS']}")

print(f"\n==> NÚMEROS DE 'MEIAS' ISOLADOS PELO SISTEMA:")
print(f"  Desarmes Purificados/Retirados (Feitos pelos Meias): {c_casa_tudo['DS'] - c_casa_volantes['DS']}")
