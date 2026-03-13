
import pandas as pd
from data_processor import DataProcessor

excel = 'Scouts Pós R5 2026.xlsx'
rounds = 'RODADAS_BRASILEIRAO_2026.txt'
proc = DataProcessor(excel, rounds)

N_JOGOS = 5
MODO = 'sequential' 
POS_REAL = 5.0 # Atacantes

print("=== PROVA REAL ATACANTES (Sem Peneira CSV): 1 JOGO DA RODADA 6 ===")

matches = proc.get_round_matches(6)
match = None
for m in matches:
    if m['Mandante'] == 'Botafogo': 
        match = m
        break

if not match:
    print("Jogo não encontrado!")
    exit()

mandante = match['Mandante']
visitante = match['Visitante']
    
print(f"\nCONFRONTO: {mandante} (CASA) x {visitante} (FORA)\n")

c_casa = proc.filter_scouts(mandante, n_games=N_JOGOS, mode=MODO, mando=None, pos_real=POS_REAL)

print(f"[ATACANTES DO {mandante} - CONQUISTADOS]")
print(f"  Gols: {c_casa['G']} | Assts: {c_casa['A']} | Chutes: {c_casa['Chutes']}")

c_fora = proc.filter_scouts(visitante, n_games=N_JOGOS, mode=MODO, mando=None, pos_real=POS_REAL)

print(f"\n[ATACANTES DO {visitante} - CONQUISTADOS]")
print(f"  Gols: {c_fora['G']} | Assts: {c_fora['A']} | Chutes: {c_fora['Chutes']}")

ced_casa = proc.filter_cedidos(mandante, n_games=N_JOGOS, mode=MODO, mando=None, pos_real=POS_REAL)

print(f"\n[{mandante} CEDIDOS AOS ATACANTES ADVERSÁRIOS]")
print(f"  Gols: {ced_casa['G']} | Assts: {ced_casa['A']} | Chutes: {ced_casa['Chutes']}")
