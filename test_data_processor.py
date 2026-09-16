import unittest
from pathlib import Path

import pandas as pd

from data_processor import DataProcessor


class DataProcessorSafetyTests(unittest.TestCase):
    def make_processor(self):
        processor = DataProcessor.__new__(DataProcessor)
        processor.reference_cutoff = pd.Timestamp("2026-09-12")
        processor.team_aliases = {
            "Inter": "Internacional",
            "RB Bragantino": "Red Bull Bragantino",
        }
        processor.roles_df = pd.DataFrame(
            [["INTERNACIONAL", "ALAN PATRICK", "MEIA"]],
            columns=["TIME", "JOGADOR", "CLASSIFICACAO"],
        )
        processor.df_jogo = pd.DataFrame(
            [
                ["Internacional", "Fora", "Alan Patrick", 4.0, "2026-09-08"],
                ["Internacional", "Fora", "Sem Cadastro", 4.0, "2026-09-01"],
                ["Internacional", "Fora", "Alan Patrick", 4.0, "2026-09-15"],
            ],
            columns=["Time", "Mand", "Nome2", "PosReal", "Data"],
        )
        processor.df_jogo["Data"] = pd.to_datetime(processor.df_jogo["Data"])
        processor.df_jogo = processor.df_jogo.sort_values("Data", ascending=False)
        return processor

    def test_reference_round_excludes_future_matches(self):
        processor = self.make_processor()
        dates = processor._get_recent_game_dates("Internacional", 3, "mando", "Fora")
        self.assertEqual(list(pd.to_datetime(dates)), [
            pd.Timestamp("2026-09-08"), pd.Timestamp("2026-09-01")
        ])

    def test_missing_role_is_not_silently_discarded(self):
        processor = self.make_processor()
        sample = processor.df_jogo[processor.df_jogo["Data"] < processor.reference_cutoff]
        with self.assertRaisesRegex(ValueError, "SEM CADASTRO"):
            processor._apply_role_filter(sample, "Inter", "MEIA")

    def test_team_alias_uses_canonical_name(self):
        processor = self.make_processor()
        self.assertEqual(processor._normalize_team_name("Inter"), "Internacional")
        self.assertEqual(
            processor._normalize_team_name("RB Bragantino"),
            "Red Bull Bragantino",
        )

    def test_lescano_is_classified_as_vasco_meia(self):
        roles = pd.read_csv(Path(__file__).resolve().parent / "classificacao_meias_volantes.csv")
        entry = roles[
            roles["TIME"].str.upper().eq("VASCO")
            & roles["JOGADOR"].str.upper().eq("LESCANO")
        ]
        self.assertEqual(entry["CLASSIFICACAO"].tolist(), ["MEIA"])

    def test_kayke_is_not_classified_as_midfielder(self):
        roles = pd.read_csv(Path(__file__).resolve().parent / "classificacao_meias_volantes.csv")
        entry = roles[
            roles["TIME"].str.upper().eq("CORINTHIANS")
            & roles["JOGADOR"].str.upper().eq("KAYKE")
        ]
        self.assertTrue(entry.empty)

    def test_philippe_coutinho_is_classified_for_both_clubs(self):
        roles = pd.read_csv(Path(__file__).resolve().parent / "classificacao_meias_volantes.csv")
        entries = roles[roles["JOGADOR"].str.upper().eq("PHILIPPE COUTINHO")]
        self.assertEqual(
            dict(zip(entries["TIME"], entries["CLASSIFICACAO"])),
            {"Vasco": "MEIA", "Santos": "MEIA"},
        )

    def test_reviewed_midfielder_roles(self):
        roles = pd.read_csv(Path(__file__).resolve().parent / "classificacao_meias_volantes.csv")
        actual = {(row.TIME.upper(), row.JOGADOR.upper()): row.CLASSIFICACAO for row in roles.itertuples()}
        expected = {
            ("BAHIA", "DAVID MARTINS"): "MEIA",
            ("BOTAFOGO", "DOMINGOS ANDRADE"): "VOLANTE",
            ("BOTAFOGO", "EDENÍLSON"): "VOLANTE",
            ("BOTAFOGO", "HUGUINHO"): "VOLANTE",
            ("CHAPECOENSE", "BRUNO MATIAS"): "VOLANTE",
            ("CHAPECOENSE", "YAGO FELIPE"): "VOLANTE",
            ("CORITIBA", "VITOR TISSI"): "VOLANTE",
            ("INTER", "VILLAGRA"): "VOLANTE",
            ("GRÊMIO", "JEFINHO"): "MEIA",
            ("REMO", "DAVID BRAGA"): "MEIA",
            ("SÃO PAULO", "MARCOS ANTÔNIO"): "MEIA",
            ("VITÓRIA", "ZÉ VITOR"): "VOLANTE",
        }
        for key, role in expected.items():
            self.assertEqual(actual.get(key), role, key)


if __name__ == "__main__":
    unittest.main()
