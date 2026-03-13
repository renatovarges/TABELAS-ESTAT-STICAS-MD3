
import pandas as pd
from data_processor import DataProcessor

excel = 'Scouts Pós R5 2026.xlsx'
rounds = 'RODADAS_BRASILEIRAO_2026.txt'
proc = DataProcessor(excel, rounds)

N_JOGOS = 5
MODO = 'sequential' 
POS_REAL = 4.0

print("=== PROVA REAL MEIAS (Com Filtro CSV): 1 JOGO DA RODADA 6 ===")

# Jogo Palmeiras x Mirassol (Palmeiras tem Zé Rafael, Richard Ríos, Veiga... ideal para teste de bloco)
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

# Extração da Plataforma (Filtrando VOLANTES via CSV)
c_casa_meias = proc.filter_scouts(mandante, n_games=N_JOGOS, mode=MODO, mando=None, pos_real=POS_REAL, role_filter="MEIA")

print(f"[MEIAS DO {mandante} - CONQUISTADOS]")
print(f"  Gols: {c_casa_meias['G']} | Assts: {c_casa_meias['A']} | Chutes: {c_casa_meias['Chutes']}")

# Extração da Plataforma (SEM FILTRO CSV -> "Puxando todo mundo da PosReal 4.0")
c_casa_tudo = proc.filter_scouts(mandante, n_games=N_JOGOS, mode=MODO, mando=None, pos_real=POS_REAL)

print(f"\n[TODOS DA POS 4.0 DO {mandante} - (Inclui Volantes!)]")
print(f"  Gols: {c_casa_tudo['G']} | Assts: {c_casa_tudo['A']} | Chutes: {c_casa_tudo['Chutes']}")

print(f"\n==> DADOS EXCLUÍDOS PELA PENEIRA (Diferença que seriam os volantes):")
print(f"  Gols Bloqueados: {c_casa_tudo['G'] - c_casa_meias['G']}")
print(f"  Assts Bloqueadas: {c_casa_tudo['A'] - c_casa_meias['A']}")
print(f"  Chutes Bloqueados: {c_casa_tudo['Chutes'] - c_casa_meias['Chutes']}")

if c_casa_tudo['Chutes'] > c_casa_meias['Chutes']:
    print("\n[OK] O Filtro funcionou perfeitamente. Volantes foram ignorados na contagem final da Plataforma de Meias.")
else:
    print("\n[INFO] Nenhuma diferença encontrada (talvez os volantes não tenham chutado ou o filtro falhou). Verificando os times na base de CSV...")
