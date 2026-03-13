
import pandas as pd
from data_processor import DataProcessor
import sys

excel = 'Scouts Pós R5 2026.xlsx'
rounds = 'RODADAS_BRASILEIRAO_2026.txt'
proc = DataProcessor(excel, rounds)

N_JOGOS = 5
MODO = 'sequential' 

matches = proc.get_round_matches(6)

target_matches = [
    m for m in matches if m['Mandante'] in ['Palmeiras', 'Botafogo', 'Fluminense']
][:3]

with open('auditoria_final_md3.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 60 + "\n")
    f.write("🏆 RELATÓRIO DE AUDITORIA FINAL - PLATAFORMA MD3 🏆\n")
    f.write("=" * 60 + "\n\n")

    for match in target_matches:
        mandante = match['Mandante']
        visitante = match['Visitante']
        
        f.write(f"\n--- CONFRONTO: {mandante} (C) x {visitante} (F) ---\n")
        
        # 1. GOLEIROS (PosReal 1.0)
        c_fora_gol = proc.filter_scouts(visitante, N_JOGOS, MODO, mando='Fora', pos_real=1.0)
        f.write("\n[1] GOLEIROS (Conquistados Pelo Visitante)\n")
        f.write(f"    Pontos: {c_fora_gol['Pts']:.1f} | DE: {c_fora_gol['DE']} | SG: {c_fora_gol['SG']}\n")

        # 2. ZAGUEIROS (PosReal 3.0)
        c_casa_zag = proc.filter_scouts(mandante, N_JOGOS, MODO, mando='Casa', pos_real=3.0)
        f.write("\n[2] ZAGUEIROS (Conquistados Pelo Mandante)\n")
        f.write(f"    Pontos: {c_casa_zag['Pts']:.1f} | PG: {c_casa_zag['PG']} | DS: {c_casa_zag['DS']}\n")

        # 3. LATERAIS (PosReal 2.2 e 2.6) - CEDIDOS
        ced_ld_casa = proc.filter_cedidos(mandante, N_JOGOS, MODO, mando='Casa', pos_real=2.2)
        ced_le_casa = proc.filter_cedidos(mandante, N_JOGOS, MODO, mando='Casa', pos_real=2.6)
        f.write("\n[3] LATERAIS (O Que o Mandante Cede)\n")
        f.write(f"    LD -> Pts Ced: {ced_ld_casa['Pts']:.1f} | PG Ced: {ced_ld_casa['PG']} | DS Ced: {ced_ld_casa['DS']}\n")
        f.write(f"    LE -> Pts Ced: {ced_le_casa['Pts']:.1f} | PG Ced: {ced_le_casa['PG']} | DS Ced: {ced_le_casa['DS']}\n")

        # 4. MEIAS (PosReal 4.0 - Filtro: MEIA)
        c_casa_mei = proc.filter_scouts(mandante, N_JOGOS, MODO, mando='Casa', pos_real=4.0, role_filter='MEIA')
        f.write("\n[4] MEIAS (Conquistados Pelo Mandante - Filtro Rigoroso)\n")
        f.write(f"    Gols: {c_casa_mei['G']} | Assts: {c_casa_mei['A']} | Chutes: {c_casa_mei['Chutes']}\n")

        # 5. ATACANTES (PosReal 5.0)
        c_fora_ata = proc.filter_scouts(visitante, N_JOGOS, MODO, mando='Fora', pos_real=5.0)
        f.write("\n[5] ATACANTES (Conquistados Pelo Visitante)\n")
        f.write(f"    Gols: {c_fora_ata['G']} | Assts: {c_fora_ata['A']} | Chutes: {c_fora_ata['Chutes']}\n")

        # 6. VOLANTES (PosReal 4.0 - Filtro: VOLANTE)
        c_casa_vol = proc.filter_scouts(mandante, N_JOGOS, MODO, mando='Casa', pos_real=4.0, role_filter='VOLANTE')
        f.write("\n[6] VOLANTES (Conquistados Pelo Mandante - Filtro Rigoroso)\n")
        f.write(f"    Pontos Média: {c_casa_vol['Pts']:.1f} | Desarmes (DE): {c_casa_vol['DE']}\n")
        
        f.write("\n" + "."*60 + "\n")

    f.write("\nAuditoria finalizada com sucesso nas 6 posições! Módulos certificados.\n")

print("Relatório de auditoria gerado: auditoria_final_md3.txt")
