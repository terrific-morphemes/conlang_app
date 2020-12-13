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


def load_adpositions(adposition_fname):
    all_adpositions = list()
    with adposition_fname.open() as source:
        reader = csv.DictReader(source)
        rows = [row for row in reader]
        for row in rows:
            adposition = {
                'meaning':row['morpheme'],
                'lemma':'',
                'category':row['category'],
            }
            all_adpositions.append(adposition)
    return all_adpositions


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
        if self.phon_syl_cons > 0:
            syllabic_consonants = [
                c for c in consonants
                if 'nasal' in c['description']
                or 'fricative' in c['description']
                or 'approximant' in c['description']
            ]
            self.medials.extend(syllabic_consonants)
        self.finals = consonants

        # TODO: consonant clusters
        # TODO: tone
        # TODO: customize initials, medials, and finals

    def create_lemma(self, morpheme, min_syl, max_syl):
        n_syls = random.randint(
            min_syl,
            max_syl + 1
        )
        lemma = ""
        while not lemma:
            if n_syls == 0:
                phonemes = self.initials + self.medials + self.finals
                lemma = random.choice(phonemes)['ipa']
            else:
                for syl_idx in range(n_syls):
                    has_initial = random.random() >= .5
                    has_final = random.random() >= .5
                    has_geminate_initial = False
                    has_geminate_final = False
                    has_long_vowel = False
                    if self.phon_gemination:
                        has_geminate_initial = random.random() >= .5
                    if self.phon_vowel_length:
                        has_long_vowel = random.random() >= .5
                    if has_initial:
                        initial = random.choice(self.initials)['ipa']
                    else: initial = ""
                    medial = random.choice(self.medials)['ipa']
                    if has_final:
                        final = random.choice(self.finals)['ipa']
                    else:
                        final = ""
                    if initial and has_geminate_initial:
                        initial *= 2
                    if final and has_geminate_final:
                        final *= 2
                    if has_long_vowel:
                        medial *= 2
                    syl = f"{initial}{medial}{final}"
                    lemma += syl
            if lemma in self.all_lemmata:
                matching_morphemes = [
                    m for m in self.morphemes
                    if m['lemma'] == lemma
                ]
                matching_words = [
                    l for l in self.lexicon
                    if l['lemma'] == lemma
                ]
                matching = matching_morphemes + matching_words
                lemma = ""
        morpheme['lemma'] = lemma
        self.all_lemmata.add(lemma)
        return morpheme

    def add_morphemes(self, category, min_syl, max_syl):
        morphemes = [
            m for m in self.all_morphemes 
            if category in m['category']
        ]
        for morpheme in morphemes:
            morpheme = self.create_lemma(
                morpheme,
                self.min_syl_per_morpheme,
                self.max_syl_per_morpheme
            )
            self.morphemes.append(morpheme)


    def create_morphology(self):
        # TODO: copula

        if self.verb_person > 0:
            self.add_morphemes(
                'verb_person',
                self.min_syl_per_morpheme,
                self.max_syl_per_morpheme,
            )

        if self.verb_number > 0:
            self.add_morphemes(
                'verb_number',
                self.min_syl_per_morpheme,
                self.max_syl_per_morpheme,
            )

        if self.verb_gender > 0:
            self.add_morphemes(
                'verb_gender',
                self.min_syl_per_morpheme,
                self.max_syl_per_morpheme,
            )

        if self.verb_tense > 0:
            self.add_morphemes(
                'verb_tense',
                self.min_syl_per_morpheme,
                self.max_syl_per_morpheme,
            )

        if self.verb_aspect > 0:
            self.add_morphemes(
                'verb_aspect',
                self.min_syl_per_morpheme,
                self.max_syl_per_morpheme,
            )

        if self.verb_mood > 0:
            self.add_morphemes(
                'verb_mood',
                self.min_syl_per_morpheme,
                self.max_syl_per_morpheme,
            )

        if self.verb_attitudinal > 0:
            self.add_morphemes(
                'verb_attitudinal',
                self.min_syl_per_morpheme,
                self.max_syl_per_morpheme,
            )

        if self.verb_evidential > 0:
            self.add_morphemes(
                'verb_evidential',
                self.min_syl_per_morpheme,
                self.max_syl_per_morpheme,
            )

        if self.derivational > 0:
            self.add_morphemes(
                'derivational',
                self.min_syl_per_morpheme,
                self.max_syl_per_morpheme,
            )

        if self.verb_valence > 0:
            self.add_morphemes(
                'verb_valence',
                self.min_syl_per_morpheme,
                self.max_syl_per_morpheme,
            )

        if self.noun_class > 0:
            self.add_morphemes(
                'noun_class',
                self.min_syl_per_morpheme,
                self.max_syl_per_morpheme,
            )

        if self.noun_case > 0:
            self.add_morphemes(
                'noun_case',
                self.min_syl_per_morpheme,
                self.max_syl_per_morpheme,
            )


    def generate_sentence(self):
        nouns = [
            l for l in self.lexicon
            if 'noun' in l['category']
            or 'object' in l['category']
        ]

        verbs = [
            l for l in self.lexicon
            if 'verb' in l['category']
        ]

        places = [
            l for l in self.lexicon
            if 'place' in l['category']
            or 'location' in l['category']
        ]

        tenses = [
            m for m in self.morphemes
            if 'tense' in m['category']
        ]

        aspects = [
            m for m in self.morphemes
            if 'aspect' in m['category']
        ]

        moods = [
            m for m in self.morphemes
            if 'mood' in m['category']
        ]

        evidentials = [
            m for m in self.morphemes
            if 'evidentiality' in m['category']
        ]


        if places:
            place = random.choice(places)
        if self.adpositions:
            locative = random.choice(self.adpositions)

        # TODO: identify nouns that can be agents and patients
        # TODO: PNG agreement
        n_subject = random.choice(nouns)
        n_object = random.choice(nouns)
        verb = random.choice(verbs)
        tense = dict()
        aspect = dict()
        mood = dict()
        evidential = dict()
        place = dict()
        locative = dict()

        if tenses:
            tense = random.choice(tenses)
        if aspects:
            aspect = random.choice(aspects)
        if moods:
            mood = random.choice(moods)
        if evidentials:
            evidential = random.choice(evidentials)

        sentence_components = {
            'subject':n_subject,
            'object':n_object,
            'verb':verb,
            'tense':tense,
            'aspect':aspect,
            'mood':mood,
            'place':place,
            'locative':locative,
            'evidential':evidential,
        }

        return sentence_components

    def create_adpositions(self):
        for adposition in self.all_adpositions:
            if self.adpositions == 'morpheme':
                adposition = self.create_lemma(
                    adposition,
                    self.min_syl_per_morpheme,
                    self.max_syl_per_morpheme
                )
                self.morphemes.append(adposition)
            else:
                adposition = self.create_lemma(
                    adposition,
                    self.min_syl_per_word,
                    self.max_syl_per_word
                )
                self.lexicon.append(adposition)

    def build_lexicon(self):
        for lexeme in self.all_lexemes:
            n_syls = random.randint(
                self.min_syl_per_word,
                self.max_syl_per_word + 1
            )
            lexeme = self.create_lemma(
                lexeme,
                self.min_syl_per_word,
                self.max_syl_per_word
            )
            self.lexicon.append(lexeme)


    def __init__(self, cfg_fname):
        cfg = load_config(cfg_fname)
        data_cfg = cfg['data']
        params_cfg = cfg['params']
        lexicon_fname = Path(data_cfg['lexicon_fname'])
        adposition_fname = Path(data_cfg['adposition_fname'])
        phoneme_fname = Path(data_cfg['phoneme_fname'])
        morpheme_fname = Path(data_cfg['morpheme_fname'])
        sentence_fname = Path(data_cfg['sentences_fname'])

        self.all_phonemes = load_phonemes(phoneme_fname)
        self.all_morphemes = load_morphemes(morpheme_fname)
        self.all_adpositions = load_adpositions(adposition_fname)
        self.all_lexemes = load_lexicon(lexicon_fname)
        self.all_sentences = load_sentences(sentence_fname)

        # for preventing homophones
        self.all_lemmata = set()

        self.lexicon = list()
        self.morphemes = list()
        self.adpositions = list()
        self.initials = list()
        self.medials = list()
        self.finals = list()
        self.tones = list()

        self.min_syl_per_word = int(params_cfg['min_syl_per_word'])
        self.max_syl_per_word = int(params_cfg['min_syl_per_word'])

        self.min_syl_per_morpheme = int(params_cfg['min_syl_per_morpheme'])
        self.max_syl_per_morpheme = int(params_cfg['max_syl_per_morpheme'])

        self.onomatopoeia = params_cfg['onomatopoeia']
        self.phon_cons_difficulty = to_ord(params_cfg['phon_cons_difficulty'])
        self.phon_cons_number = to_ord(params_cfg['phon_cons_number'])
        self.phon_vowel_difficulty = to_ord(params_cfg['phon_vowel_difficulty'])
        self.phon_vowel_number = to_ord(params_cfg['phon_vowel_number'])

        self.phon_syl_cons = to_ord(params_cfg['phon_syl_cons'])
        self.phon_tone = to_ord(params_cfg['phon_tone'])
        self.phon_gemination = to_bool(params_cfg['phon_gemination'])
        self.phon_vowel_length =to_bool( params_cfg['phon_vowel_length'])
        self.phon_non_egressive = to_bool(params_cfg['phon_non_egressive'])
        self.phon_initial_clusters = to_ord(params_cfg['phon_initial_clusters'])
        self.phon_final_clusters = to_ord(params_cfg['phon_final_clusters'])
        self.phon_diphthongs = to_ord(params_cfg['phon_diphthongs'])

        self.create_phonology()

        self.word_order = params_cfg['word_order']
        self.noun_class = to_ord(params_cfg['noun_class'])
        self.noun_case = to_ord(params_cfg['noun_case'])
        self.pronouns = to_ord(params_cfg['pronouns'])
        self.adpositions = params_cfg['adpositions']

        self.verb_copula = to_bool(params_cfg['verb_copula'])
        self.verb_person = to_ord(params_cfg['verb_person'])
        self.verb_number = to_ord(params_cfg['verb_number'])
        self.verb_gender = to_ord(params_cfg['verb_gender'])
        self.verb_tense = to_ord(params_cfg['verb_tense'])
        self.verb_aspect = to_ord(params_cfg['verb_aspect'])
        self.verb_mood = to_ord(params_cfg['verb_mood'])
        self.verb_attitudinal = to_ord(params_cfg['verb_attitudinal'])
        self.verb_evidential = to_ord(params_cfg['verb_evidential'])
        self.derivational = to_ord(params_cfg['derivational'])
        self.verb_valence = to_ord(params_cfg['verb_valence'])

        self.create_morphology()
        self.create_adpositions()

        self.build_lexicon()

if __name__ == "__main__":
    conlang = Conlang(CFG_FNAME)
    for lexeme in conlang.lexicon:
        meaning = lexeme['meaning']
        lemma = lexeme['lemma']
        print(f"{lemma}: {meaning}")
    for i in range(20):
        sent = conlang.generate_sentence()
        for role, component in sent.items():
            lemma = component.get('lemma', '')
            meaning = component.get('meaning', '')
            print(f"{role}: {lemma} ({meaning})")
        print()
