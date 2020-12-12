import yaml
import csv
import random
import json
from pathlib import Path

CFG_FNAME = Path("./configs/tiefling_config.yaml")

# TODO: save to json


ORD_SCALE = {
    'none':0,
    'low':1,
    'med':2,
    'high':3,
}


def load_config(cfg_fname):
    with cfg_fname.open() as source:
        cfg = yaml.safe_load(source)
        return cfg


def load_lexicon(lexicon_fname):
    all_lexemes = list()
    with lexicon_fname.open() as source:
        reader = csv.DictReader(source)
        rows = [row for row in reader]
        for row in rows:
            lexeme = {
                'meaning':row['word'],
                'lemma':'',
                'category':row['category'],
            }
            all_lexemes.append(lexeme)
    return all_lexemes


def load_phonemes(phoneme_fname):
    all_phonemes = list()
    with phoneme_fname.open() as source:
        reader = csv.DictReader(source)
        rows = [row for row in reader]
        for row in rows:
            phoneme = {
                'xsampa':row['xsampa'],
                'ipa':row['ipa'],
                'description':row['description'],
                'level':to_ord(row['level']),
            }
            all_phonemes.append(phoneme)
    return all_phonemes


def load_morphemes(morpheme_fname):
    all_morphemes = list()
    with morpheme_fname.open() as source:
        reader = csv.DictReader(source)
        rows = [row for row in reader]
        for row in rows:
            morpheme = {
                'meaning':row['morpheme'],
                'lemma':'',
                'category':row['category'],
            }
            all_morphemes.append(morpheme)
    return all_morphemes


def load_sentences(sentence_fname):
    all_sentences = list()
    with sentence_fname.open() as source:
        reader = csv.DictReader(source)
        rows = [row for row in reader]
        for row in rows:
            sentence = {
                'meaning':row['meaning'],
                'lemma':'',
                'category':row['category'],
            }
            all_sentences.append(sentence)
    return all_sentences


def to_bool(string):
    return True if string == 'yes' else False


def to_ord(string):
    return ORD_SCALE[string]


class Conlang:
    def create_phonology(self):
        all_vowels = [
            p for p in self.all_phonemes
            if 'vowel' in p['description']
        ]

        all_consonants = [
            p for p in self.all_phonemes
            if 'vowel' not in p['description']
        ]

        vowels_matching_level = [
            v for v in all_vowels
            if v['level'] <= self.phon_vowel_difficulty
        ]

        consonants_matching_level = [
            c for c in all_consonants
            if c['level'] <= self.phon_cons_difficulty
        ]

        if self.phon_vowel_number == 0:
            n_vowels = 0
        elif self.phon_vowel_number == 1:
            n_vowels = random.randint(5,8)
        elif self.phon_vowel_number == 2:
            n_vowels = random.randint(8,12)
        else:
            n_vowels = random.randint(12, 20)


        if self.phon_cons_number == 0:
            n_consonants = 0
        elif self.phon_cons_number == 1:
            n_consonants = random.randint(5,10)
        elif self.phon_cons_number == 2:
            n_consonants = random.randint(10,15)
        else:
            n_consonants= random.randint(15, 30)

        n_vowels = min(n_vowels, len(vowels_matching_level))
        n_consonants = min(n_consonants, len(consonants_matching_level))

        consonants = random.sample(consonants_matching_level, n_consonants)
        vowels = random.sample(vowels_matching_level, n_vowels)

        self.initials = consonants
        self.medials = vowels
        self.finals = consonants


        # TODO: consonant clusters
        # TODO: tone
        # TODO: customize initials, medials, and finals


    def create_noun_morphology(self):
        pass

    def create_verb_morphology(self):
        pass

    def create_locative_morphology(self):
        pass

    def build_lexicon(self):
        for lexeme in self.all_lexemes:
            n_syls = random.randint(
                self.min_syl_per_word,
                self.max_syl_per_word + 1
            )
            lemma = ""
            while not lemma:
                for syl_idx in range(n_syls):
                    has_initial = random.random() >= .5
                    has_final = random.random() >= .5
                    if has_initial:
                        initial = random.choice(self.initials)['ipa']
                    else: initial = ""
                    medial = random.choice(self.medials)['ipa']
                    if has_final:
                        final = random.choice(self.finals)['ipa']
                    else:
                        final = ""
                    syl = f"{initial}{medial}{final}"
                    lemma += syl
            if lemma in self.all_lemmata:
                lemma = ""
            lexeme['lemma'] = lemma
            self.lexicon.append(lexeme)


    def __init__(self, cfg_fname):
        cfg = load_config(cfg_fname)
        data_cfg = cfg['data']
        params_cfg = cfg['params']
        lexicon_fname = Path(data_cfg['lexicon_fname'])
        phoneme_fname = Path(data_cfg['phoneme_fname'])
        morpheme_fname = Path(data_cfg['morpheme_fname'])
        sentence_fname = Path(data_cfg['sentences_fname'])

        self.all_phonemes = load_phonemes(phoneme_fname)
        self.all_morphemes = load_morphemes(morpheme_fname)
        self.all_lexemes = load_lexicon(lexicon_fname)
        self.all_sentences = load_sentences(sentence_fname)

        self.all_lemmata = set()
        self.lexicon = list()
        self.morphemes = list()
        self.initials = list()
        self.medials = list()
        self.finals = list()
        self.tones = list()

        self.min_syl_per_word = int(params_cfg['min_syl_per_word'])
        self.max_syl_per_word = int(params_cfg['min_syl_per_word'])

        self.min_syl_per_morpheme = int(params_cfg['min_syl_per_morpheme'])
        self.max_syl_per_morpheme = int(params_cfg['min_syl_per_morpheme'])

        self.onomatopoeia = params_cfg['onomatopoeia']
        self.phon_cons_difficulty = to_ord(params_cfg['phon_cons_difficulty'])
        self.phon_cons_number = to_ord(params_cfg['phon_cons_number'])
        self.phon_vowel_difficulty = to_ord(params_cfg['phon_vowel_difficulty'])
        self.phon_vowel_number = to_ord(params_cfg['phon_vowel_number'])

        self.syl_cons = to_ord(params_cfg['phon_syl_cons'])
        self.phon_tone = to_ord(params_cfg['phon_tone'])
        self.phon_gemination = to_bool(params_cfg['phon_gemination'])
        self.phon_vowel_length =to_bool( params_cfg['phon_vowel_length'])
        self.phon_non_egressive = to_bool(params_cfg['phon_non_egressive'])
        self.phon_initial_clusters = to_ord(params_cfg['phon_initial_clusters'])
        self.phon_final_clusters = to_ord(params_cfg['phon_final_clusters'])
        self.phon_diphthongs = to_ord(params_cfg['phon_diphthongs'])

        self.create_phonology()

        self.word_order = params_cfg['word_order']
        self.locatives = params_cfg['locatives']
        self.noun_class = to_ord(params_cfg['noun_class'])
        self.pronouns = to_ord(params_cfg['pronouns'])

        self.create_noun_morphology()

        self.verb_copula = to_bool(params_cfg['verb_copula'])
        self.verb_person = to_ord(params_cfg['verb_person'])
        self.verb_number = to_ord(params_cfg['verb_number'])
        self.verb_gender = to_ord(params_cfg['verb_gender'])
        self.verb_tense = to_ord(params_cfg['verb_tense'])
        self.verb_aspect = to_ord(params_cfg['verb_aspect'])
        self.verb_mood = to_ord(params_cfg['verb_mood'])
        self.verb_attitudinal = to_ord(params_cfg['verb_attitudinal'])

        self.create_verb_morphology()

        self.build_lexicon()

if __name__ == "__main__":
    conlang = Conlang(CFG_FNAME)
    for lexeme in conlang.lexicon:
        meaning = lexeme['meaning']
        lemma = lexeme['lemma']
        print(f"{lemma}: {meaning}")
