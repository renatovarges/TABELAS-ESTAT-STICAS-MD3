
import pandas as pd

file_path = r'c:\Users\User\.gemini\antigravity\scratch\TABELAS ESTATÍSTICAS MD3\Scouts Pós R5 2026.xlsx'

try:
    xl = pd.ExcelFile(file_path)
    print(f"Abas encontradas: {xl.sheet_names}")
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet, nrows=5)
        print(f"\n--- Estrutura da aba: {sheet} ---")
        print(df.columns.tolist())
        print(df.head(2))
except Exception as e:
    print(f"Erro ao ler o arquivo: {e}")
