"""Tests de annotation_filters.py (aucun acces reseau).
Lancer : python3 -m unittest test_annotation_filters -v
Les cas viennent de la releve de 200 annotations (documentation, section 26.7)."""
import unittest
import annotation_filters as f

DBP = 'http://dbpedia.org/resource/'
WD = 'https://www.wikidata.org/wiki/'
TH = 'https://opentheso.huma-num.fr/?idc=%s&idt=th310'


class NombresEtChiffresRomains(unittest.TestCase):
    def test_refuses(self):
        for mention in ('42', '51', 'XIX', 'XVII', ' 70 '):
            for origin, uri in (('DBpedia', DBP + 'Super_Bowl_XIX'), ('wikidata', WD + 'Q3599091'), ('zoomathia_match', TH % '105124')):
                self.assertFalse(f.keep_annotation(uri, mention, origin), (mention, origin))

    def test_mention_vide(self):
        self.assertFalse(f.keep_annotation(DBP + 'Dog', '', 'DBpedia'))


class DBpedia(unittest.TestCase):
    def test_accepte_quand_le_titre_correspond(self):
        for mention, page in (('lips', 'Lip'), ('animals', 'Animal'), ('men', 'Man'), ('homes', 'Home'),
                              ('Minyas', 'Minyas_(mythology)'), ('water', 'Water')):
            self.assertTrue(f.keep_annotation(DBP + page, mention, 'DBpedia'), mention)

    def test_accepte_un_nom_propre_contenu_dans_le_titre(self):
        self.assertTrue(f.keep_annotation(DBP + 'Alexander_the_Great', 'Alexander', 'DBpedia'))

    def test_refuse_un_mot_courant_sans_rapport(self):
        for mention, page in (('revolving', 'Revolver'), ('victory', 'Second_Battle_of_El_Alamein'),
                              ('case', 'Grammatical_case'), ('power', 'Electric_power'), ('ground', 'Earth')):
            self.assertFalse(f.keep_annotation(DBP + page, mention, 'DBpedia'), mention)

    def test_refuse_un_titre_avec_chiffre(self):
        self.assertFalse(f.keep_annotation(DBP + '3_Juno', 'Juno', 'DBpedia'))

    def test_alias_connu(self):
        f._ALIASES.add('tarentum|' + DBP + 'Taranto')
        try:
            self.assertTrue(f.keep_annotation(DBP + 'Taranto', 'Tarentum', 'DBpedia'))
        finally:
            f._ALIASES.discard('tarentum|' + DBP + 'Taranto')


class Thesaurus(unittest.TestCase):
    def test_concept_exclu(self):
        self.assertFalse(f.keep_annotation(TH % 'pcrtEpGlZykUTy', 'led', 'zoomathia_match'))   # Lead (metal)
        self.assertFalse(f.keep_annotation(TH % 'pcrtLnUS9cADfI', 'saw', 'zoomathia_match'))   # saw (outil)

    def test_forme_exclue_d_un_concept_conserve(self):
        self.assertFalse(f.keep_annotation(TH % 'pcrtGm7ZMfoQrc', 'born', 'zoomathia_match'))  # Bear
        self.assertTrue(f.keep_annotation(TH % 'pcrtGm7ZMfoQrc', 'bears', 'zoomathia_match'))

    def test_concept_ordinaire_conserve(self):
        self.assertTrue(f.keep_annotation(TH % '105124', 'head', 'zoomathia_match'))


class Wikidata(unittest.TestCase):
    def setUp(self):
        self.saved = dict(f._WIKIDATA)
        f._WIKIDATA.update({'Q1': {'description': 'British ska band'}, 'Q2x': {'description': 'ancient Greek physician'},
                            'Q3': {'description': 'town in Queensland, Australia'}})

    def tearDown(self):
        f._WIKIDATA.clear(); f._WIKIDATA.update(self.saved)

    def test_ecarte_les_entites_modernes(self):
        self.assertFalse(f.keep_annotation(WD + 'Q1', 'Madness', 'wikidata'))
        self.assertFalse(f.keep_annotation(WD + 'Q3', 'Thallon', 'wikidata'))

    def test_garde_une_entite_ancienne(self):
        self.assertTrue(f.keep_annotation(WD + 'Q2x', 'Praxagoras', 'wikidata'))

    def test_description_inconnue_conservee(self):
        self.assertTrue(f.keep_annotation(WD + 'Q999999999', 'Anytus', 'wikidata'))


if __name__ == '__main__':
    unittest.main()
