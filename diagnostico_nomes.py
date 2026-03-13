import pandas as pd
import re

excel_path = 'Scouts Pós R5 2026.xlsx'
rounds_path = 'RODADAS_BRASILEIRAO_2026.txt'

df = pd.read_excel(excel_path, sheet_name='Por jogo')
times_planilha = sorted(df['Time'].unique())
print("--- Times na Planilha (Scouts) ---")
print(times_planilha)

print("\n--- Times no Arquivo de Rodadas ---")
times_rodadas = set()
with open(rounds_path, 'r', encoding='utf-8') as f:
    content = f.read()
    confrontos_raw = re.split(r'Rodada \d+.*', content)[1:]
    for bloco in confrontos_raw:
        linhas = bloco.strip().split('\n')
        for line in linhas:
            if ' x ' in line:
                teams = line.split(' x ')
                times_rodadas.add(teams[0].strip())
                times_rodadas.add(teams[1].split('(')[0].strip())
print(sorted(list(times_rodadas)))

print("\n--- Diferenças ---")
print("Times nas rodadas que NÃO estão na planilha:")
print(set(times_rodadas) - set(times_planilha))
print("Times na planilha que NÃO estão nas rodadas:")
print(set(times_planilha) - set(times_rodadas))
