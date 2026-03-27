
import pandas as pd
import numpy as np
import re

class DataProcessor:
    def __init__(self, excel_path, rounds_path):
        self.excel_path = excel_path
        self.rounds_path = rounds_path
        self.df_jogo = None
        self.rounds_data = []
        self.roles_df = pd.DataFrame()
        # Tradutor de nomes de times (Rodadas -> Planilha)
        self.team_aliases = {
            'Atlético': 'Atlético-MG',
            'Athletico': 'Athletico-PR'
        }
        self._load_data()

    def _normalize_team_name(self, name):
        return self.team_aliases.get(name, name)

    def _load_data(self):
        import os
        self.df_jogo = pd.read_excel(self.excel_path, sheet_name='Por jogo')
        
        roles_file = 'classificacao_meias_volantes.csv'
        if os.path.exists(roles_file):
            self.roles_df = pd.read_csv(roles_file)
            self.roles_df['TIME'] = self.roles_df['TIME'].astype(str).str.strip().str.upper()
            self.roles_df['JOGADOR'] = self.roles_df['JOGADOR'].astype(str).str.strip().str.upper()
            self.roles_df['CLASSIFICACAO'] = self.roles_df['CLASSIFICACAO'].astype(str).str.strip().str.upper()
            
        self.df_jogo['Data'] = pd.to_datetime(self.df_jogo['Data'])
        
        # Garantir limpeza de NaNs e tipos numéricos
        cols_calc = ['DE', 'SG', 'Pts']
        for col in cols_calc:
            if col in self.df_jogo.columns:
                self.df_jogo[col] = pd.to_numeric(self.df_jogo[col], errors='coerce').fillna(0)
        
        # Ordenar CRONOLOGICAMENTE (do mais recente para o mais antigo para facilitar head(N))
        self.df_jogo = self.df_jogo.sort_values(by='Data', ascending=False)
        
        # Parse das rodadas
        with open(self.rounds_path, 'r', encoding='utf-8') as f:
            content = f.read()
            rodadas = re.split(r'Rodada (\d+)', content)
            for i in range(1, len(rodadas), 2):
                rodada_num = int(rodadas[i])
                confrontos_raw = rodadas[i+1].strip().split('\n')
                confrontos = []
                for line in confrontos_raw:
                    if ' x ' in line:
                        teams = line.split(' x ')
                        mandante = self._normalize_team_name(teams[0].strip())
                        visitante = self._normalize_team_name(teams[1].split('(')[0].strip())
                        confrontos.append({'Mandante': mandante, 'Visitante': visitante})
                self.rounds_data.append({'Rodada': rodada_num, 'Confrontos': confrontos})

    def get_round_matches(self, round_num):
        for rd in self.rounds_data:
            if rd['Rodada'] == round_num:
                return rd['Confrontos']
        return []

    def _get_recent_game_dates(self, team_name, n_games, mode='sequential', mando=None):
        """Retorna as N datas únicas de jogos do time, respeitando filtros."""
        df_team_full = self.df_jogo[self.df_jogo['Time'] == team_name]
        
        if mode == 'mando' and mando:
            df_team_full = df_team_full[df_team_full['Mand'] == mando]
        
        # Datas únicas ordenadas (já está ordenado descendente)
        recent_dates = df_team_full['Data'].unique()[:n_games]
        return recent_dates

    def filter_scouts(self, team_name, n_games, mode='sequential', mando=None, pos_real=1.0, role_filter=None):
        """Calcula scouts CONQUISTADOS pelo time na posição especificada. Aceita filtro cruzado de role."""
        recent_dates = self._get_recent_game_dates(team_name, n_games, mode, mando)
        
        if len(recent_dates) == 0:
            return {'DE': 0, 'SG': 0, 'Pts': 0.0, 'DS': 0, 'Chutes': 0, 'PG': 0, 'G': 0, 'A': 0, 'Jogos': 0}

        game_stats = []
        for date in recent_dates:
            team_defenders = self.df_jogo[(self.df_jogo['Time'] == team_name) & (self.df_jogo['Data'] == date)]
            sg_coletivo = 1 if team_defenders['SG'].max() > 0 else 0

            pos_data = self.df_jogo[
                (self.df_jogo['Time'] == team_name) & 
                (self.df_jogo['Data'] == date) & 
                (self.df_jogo['PosReal'] == pos_real)
            ]
            if role_filter and not pos_data.empty and not self.roles_df.empty:
                valid_players = self.roles_df[
                    (self.roles_df['TIME'] == team_name.upper()) & 
                    (self.roles_df['CLASSIFICACAO'] == role_filter.upper())
                ]['JOGADOR'].tolist()
                pos_data = pos_data[pos_data['Nome2'].astype(str).str.strip().str.upper().isin(valid_players)]
            
            if not pos_data.empty:
                chutes = 0
                gols = 0
                assists = 0
                pg = 0
                if 'FF' in pos_data.columns and 'FD' in pos_data.columns and 'FT' in pos_data.columns:
                    chutes = pos_data['FF'].sum() + pos_data['FD'].sum() + pos_data['FT'].sum()
                if 'G' in pos_data.columns: 
                    gols = pos_data['G'].sum() 
                if 'A' in pos_data.columns:
                    assists = pos_data['A'].sum()
                
                pg = gols + assists
                ds = pos_data['DS'].sum() if 'DS' in pos_data.columns else 0
                
                game_stats.append({
                    'DE': pos_data['DE'].sum(),
                    'SG': sg_coletivo, 
                    'Pts': pos_data['Pts'].sum(),
                    'DS': ds,
                    'Chutes': chutes,
                    'PG': pg,
                    'G': gols,
                    'A': assists,
                    'NumJogadores': len(pos_data)
                })
            else:
                game_stats.append({'DE': 0, 'SG': sg_coletivo, 'Pts': 0.0, 'DS': 0, 'Chutes': 0, 'PG': 0, 'G': 0, 'A': 0, 'NumJogadores': 0})
        
        if not game_stats:
            return {'DE': 0, 'SG': 0, 'Pts': 0.0, 'DS': 0, 'Chutes': 0, 'PG': 0, 'G': 0, 'A': 0, 'Jogos': len(recent_dates)}

        df_stats = pd.DataFrame(game_stats)
        total_jogadores = df_stats['NumJogadores'].sum()
        media_pts = df_stats['Pts'].sum() / total_jogadores if total_jogadores > 0 else 0.0
        return {
            'DE': df_stats['DE'].sum(),
            'SG': df_stats['SG'].sum(), 
            'Pts': media_pts,
            'DS': df_stats['DS'].sum(),
            'Chutes': df_stats['Chutes'].sum(),
            'PG': df_stats['PG'].sum(),
            'G': df_stats['G'].sum(),
            'A': df_stats['A'].sum(),
            'Jogos': len(recent_dates)
        }

    def filter_cedidos(self, team_name, n_games, mode='sequential', mando=None, pos_real=1.0, role_filter=None):
        """Calcula scouts CEDIDOS pelo time para a posição adversária especificada. Suporta Filtro CSV."""
        recent_dates = self._get_recent_game_dates(team_name, n_games, mode, mando)
        
        if len(recent_dates) == 0:
            return {'DE': 0, 'SG': 0, 'Pts': 0.0, 'DS': 0, 'Chutes': 0, 'PG': 0, 'G': 0, 'A': 0, 'Jogos': 0}

        game_stats = []
        for date in recent_dates:
            match_sample = self.df_jogo[
                (self.df_jogo['Time'] == team_name) & 
                (self.df_jogo['Data'] == date)
            ]
            if match_sample.empty: continue
            
            adversario = match_sample['Adversário'].iloc[0]
            
            adv_defenders = self.df_jogo[(self.df_jogo['Time'] == adversario) & (self.df_jogo['Data'] == date)]
            sg_coletivo = 1 if adv_defenders['SG'].max() > 0 else 0
            
            adv_pos_data = self.df_jogo[
                (self.df_jogo['Time'] == adversario) & 
                (self.df_jogo['Data'] == date) & 
                (self.df_jogo['PosReal'] == pos_real)
            ]
            
            if role_filter and not adv_pos_data.empty and not self.roles_df.empty:
                valid_players = self.roles_df[
                    (self.roles_df['TIME'] == adversario.upper()) & 
                    (self.roles_df['CLASSIFICACAO'] == role_filter.upper())
                ]['JOGADOR'].tolist()
                adv_pos_data = adv_pos_data[adv_pos_data['Nome2'].astype(str).str.strip().str.upper().isin(valid_players)]

            if not adv_pos_data.empty:
                chutes = 0
                gols = 0
                assists = 0
                pg = 0
                if 'FF' in adv_pos_data.columns and 'FD' in adv_pos_data.columns and 'FT' in adv_pos_data.columns:
                    chutes = adv_pos_data['FF'].sum() + adv_pos_data['FD'].sum() + adv_pos_data['FT'].sum()
                if 'G' in adv_pos_data.columns: 
                    gols = adv_pos_data['G'].sum() 
                if 'A' in adv_pos_data.columns:
                    assists = adv_pos_data['A'].sum()
                pg = gols + assists
                ds = adv_pos_data['DS'].sum() if 'DS' in adv_pos_data.columns else 0

                game_stats.append({
                    'DE': adv_pos_data['DE'].sum(),
                    'SG': sg_coletivo,
                    'Pts': adv_pos_data['Pts'].sum(),
                    'DS': ds,
                    'Chutes': chutes,
                    'PG': pg,
                    'G': gols,
                    'A': assists,
                    'NumJogadores': len(adv_pos_data)
                })
            else:
                game_stats.append({'DE': 0, 'SG': sg_coletivo, 'Pts': 0.0, 'DS': 0, 'Chutes': 0, 'PG': 0, 'G': 0, 'A': 0, 'NumJogadores': 0})

        df_stats = pd.DataFrame(game_stats)
        total_jogadores = df_stats['NumJogadores'].sum()
        media_pts = df_stats['Pts'].sum() / total_jogadores if total_jogadores > 0 else 0.0
        return {
            'DE': df_stats['DE'].sum(),
            'SG': df_stats['SG'].sum(),
            'Pts': media_pts,
            'DS': df_stats['DS'].sum(),
            'Chutes': df_stats['Chutes'].sum(),
            'PG': df_stats['PG'].sum(),
            'G': df_stats['G'].sum(),
            'A': df_stats['A'].sum(),
            'Jogos': len(recent_dates)
        }
