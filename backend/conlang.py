import yaml
import datetime
import csv
import random
import json
from pathlib import Path

import spacy
nlp = spacy.load('en')
now = datetime.datetime.now().strftime('%Y%m%d-%H%M')

# CFG_FNAME = Path("./backend/configs/tiefling_config.yaml")
# CFG_FNAME = Path("./backend/configs/city_config.yaml")
CFG_FNAME = Path("./backend/configs/spell_config.yaml")
# CFG_FNAME = Path("./backend/configs/monosyllabic_config.yaml")

# DEST_FNAME = Path("./backend/data/tiefling_conlang.json")
DEST_FNAME = Path(f"./backend/data/spell_conlang_{now}.json")
# DEST_FNAME = Path("./backend/data/monosyllabic_conlang.json")
# TODO: save to json

PARAM_CONVERSION = {
    'none':0,
    'low':1,
    'med':2,
    'high':3,
    '1':1,
    '2':2,
    '3':3,
    '4':4,
    'yes':True,
    'no':False,
}


def load_config(cfg_fname):
    with cfg_fname.open() as source:
        cfg = yaml.safe_load(source)
        return cfg


def load_lexicon(lexicon_fnames):
    seen_words = set()
    all_lexemes = list()
    for lexicon_fname in lexicon_fnames:
        with lexicon_fname.open() as source:
            reader = csv.DictReader(source)
            rows = [row for row in reader]
            for row in rows:
                if row['word'] not in seen_words:
                    seen_words.add(row['word'])
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
                'level':PARAM_CONVERSION.get(row['level'], row['level']),
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


def convert_param(params, param):
    setting = params[param]
    if type(setting) == list:
        return setting
    else:
        return PARAM_CONVERSION.get(setting, setting)


class Conlang:
    def save_conlang(self, dest_fname):
        data = {
            'all_phonemes':self.all_phonemes,
            'all_morphemes':self.all_morphemes,
            'all_adpositions':self.all_adpositions,
            'all_lexemes':self.all_lexemes,
            'all_sentences':self.all_sentences,
            'lexicon':self.lexicon,
            'morphemes':self.morphemes,
            'adpositions':self.adpositions,
            'initials':self.initials,
            'medials':self.medials,
            'finals':self.finals,
            'tones':self.tones,
            'morphology_rules':self.morphology_rules,
            'phonology_rules':self.phonology_rules,
            'syntax_rules':self.syntax_rules,
            'lexicon_rules':self.lexicon_rules,
        }

        with dest_fname.open('w') as dest:
            json.dump(data, dest, indent=1)

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
            if v['level'] <= self.phonology_rules['phon_vowel_difficulty']
        ]

        consonants_matching_level = [
            c for c in all_consonants
            if c['level'] <= self.phonology_rules['phon_cons_difficulty']
        ]

        vowel_number = self.phonology_rules['phon_vowel_number']
        if vowel_number == 0:
            n_vowels = 0
        elif vowel_number == 1:
            n_vowels = random.randint(5,8)
        elif vowel_number == 2:
            n_vowels = random.randint(8,12)
        else:
            n_vowels = random.randint(12, 20)

        cons_number = self.phonology_rules['phon_cons_number']
        if cons_number == 0:
            n_consonants = 0
        elif cons_number == 1:
            n_consonants = random.randint(5,10)
        elif cons_number == 2:
            n_consonants = random.randint(10,15)
        else:
            n_consonants= random.randint(15, 30)

        n_vowels = min(n_vowels, len(vowels_matching_level))
        n_consonants = min(n_consonants, len(consonants_matching_level))

        consonants = random.sample(consonants_matching_level, n_consonants)
        vowels = random.sample(vowels_matching_level, n_vowels)

        self.initials = consonants
        self.medials = vowels
        if self.phonology_rules['phon_syl_cons'] > 0:
            syllabic_consonants = [
                c for c in consonants
                if 'nasal' in c['description']
                or 'fricative' in c['description']
                or 'approximant' in c['description']
            ]
            self.medials.extend(syllabic_consonants)
        self.finals = consonants
        tone = self.phonology_rules['phon_tone']
        if tone >= 1:
            self.tones.extend(['55', '11'])
        if tone >= 2:
            self.tones.extend(['51', '15'])
        if tone >= 3:
            self.tones.extend(['33', '13', '31', '314', '53', '35'])

        # TODO: consonant clusters
        # TODO: customize initials, medials, and finals

    def create_lemma(self, morpheme, min_syl, max_syl):
        n_syls = random.randint(
            min_syl,
            max_syl
        )
        lemma = list()
        attempt_count = 0
        while not lemma:
            if n_syls == 0:
                phonemes = self.initials + self.medials + self.finals
                lemma = [random.choice(phonemes)['ipa']]
            else:
                for syl_idx in range(n_syls):
                    has_initial = random.random() >= .5
                    has_final = random.random() >= .5
                    has_geminate_initial = False
                    has_geminate_final = False
                    has_long_vowel = False
                    if self.phonology_rules['phon_cons_length']:
                        has_geminate_initial = random.random() >= .5
                    if self.phonology_rules['phon_vowel_length']:
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
                    if self.tones:
                        tone = random.choice(self.tones)
                    else:
                        tone = ""
                    syl = f"{initial}{medial}{final}{tone}"
                    lemma.append(syl)
            n_phonemes = len(
                self.initials
                + self.finals
                + self.medials 
                + self.tones
            )
            n_morphemes = len(self.morphemes)
            n_lexemes = len(self.lexicon)
            if (
                '-'.join(lemma) in self.all_lemmata
                and (
                    n_phonemes > n_morphemes
                    or n_phonemes > n_lexemes
                )
                and attempt_count < 100
            ):
                matching_morphemes = [
                    m for m in self.morphemes
                    if m['lemma'] == '-'.join(lemma)
                ]
                matching_words = [
                    l for l in self.lexicon
                    if l['lemma'] == '-'.join(lemma)
                ]
                matching = matching_morphemes + matching_words
                lemma = list()
                attempt_count += 1
                # print(f"Attempt {attempt_count} for {morpheme}")
        morpheme['lemma'] = '-'.join(lemma)
        self.all_lemmata.add('-'.join(lemma))
        return morpheme

    def add_morphemes(self, category):
        morphemes = [
            m for m in self.all_morphemes 
            if category in m['category']
        ]
        for morpheme in morphemes:
            morpheme = self.create_lemma(
                morpheme,
                self.phonology_rules['min_syl_per_morpheme'],
                self.phonology_rules['max_syl_per_morpheme']
            )
            """
            print(
                f"Adding morpheme {morpheme['lemma']}"
                f"{self.min_syl_per_morpheme} {self.max_syl_per_morpheme}"
            )
            """
            self.morphemes.append(morpheme)


    def create_morphology(self):

        for param, setting in self.morphology_rules.items():
            if setting is True:
                self.add_morphemes(param)
            elif type(setting) == int and setting > 0:
                self.add_morphemes(param)
        verb_agreement = self.morphology_rules['verb_agreement']
        verb_agree_with = self.morphology_rules['verb_agree_with']
        if verb_agree_with != 'none' and verb_agree_with != 0:
            verb_morphemes = set()
            person = list()
            number = list()
            noun_class = list()
            case = list()
            if 'person' in verb_agreement:
                person = [
                    m['morpheme'] for category in self.morphemes 
                    if 'noun_person' in m['category']
                ]
            if 'number' in verb_agreement:
                number = [
                    m['morpheme'] for category in self.morphemes 
                    if 'noun_number' in m['category']
                ]
            if 'class' in verb_agreement:
                noun_class = [
                    m['morpheme'] for category in self.morphemes 
                    if 'noun_class' in m['category']
                ]
            if 'case' in verb_agreement:
                case = [
                    m['morpheme'] for category in self.morphemes 
                    if 'noun_case' in m['category']
                ]
            if not person:
                person = [""]
            if not number:
                number = [""]
            if not noun_class:
                noun_class = [""]
            if not case:
                case = [""]
            for p in person:
                for n in number:
                    for g in noun_class:
                        for c in case:
                            verb_morpheme = f"{p}{n}{g}{c}"
                            verb_morphemes.add(verb_morpheme)
            for verb_morpheme in verb_morphemes:
                lexeme = {
                    'category':'verb_agreement',
                    'lemma':'',
                    'meaning':f'verb_{verb_morpheme}'
                }
                lexeme = self.create_lemma(
                    lexeme,
                    self.phonology_rules['min_syl_per_morpheme'],
                    self.phonology_rules['max_syl_per_morpheme']
                )
                self.morphemes.append(lexeme)
        
        if self.morphology_rules['pronouns'] is True:
            pronoun_agreement = self.morphology_rules['pronoun_agreement']
            pronouns = set()
            person = list()
            number = list()
            noun_class = list()
            case = list()

            if 'person' in pronoun_agreement:
                person = [
                    m['meaning'] for m in self.morphemes 
                    if 'noun_person' in m['category']
                ]
            if 'number' in pronoun_agreement:
                number = [
                    m['meaning'] for m in self.morphemes 
                    if 'noun_number' in m['category']
                ]
            if 'class' in pronoun_agreement:
                noun_class = [
                    m['meaning'] for m in self.morphemes 
                    if 'noun_class' in m['category']
                ]
            if not person:
                person = [""]
            if not number:
                number = [""]
            if not noun_class:
                noun_class = [""]
            for p in person:
                for n in number:
                    for c in noun_class:
                        pronoun = f"{p}{n}{c}"
                        pronouns.add(pronoun)
            for pronoun in pronouns:
                lexeme = {
                    'category':'pronouns',
                    'lemma':'',
                    'meaning':f'pronoun_{pronoun}'
                }
                lexeme = self.create_lemma(
                    lexeme,
                    self.phonology_rules['min_syl_per_morpheme'],
                    self.phonology_rules['max_syl_per_morpheme']
                )
                self.morphemes.append(lexeme)
         # TODO: inflection classes

    def generate_sentence(self, text=None):
        if text:
            doc = nlp(text)
            print([(t.text, t.dep_) for t in doc])
            doc_subjs = [
                t.lemma_.lower() for t in doc if 'subj' in t.dep_
            ]
            doc_objs = [
                t.lemma_.lower() for t in doc if 'obj' in t.dep_
            ]
            doc_mods = [
                t.lemma_.lower() for t in doc if 'mod' in t.dep_
            ]

            sent_tokens = list()
            for t in doc:
                lemma = t.lemma_.lower()
                match = dict()
                matches = [
                    l for l in self.lexicon
                    if l['meaning'] == lemma
                ]
                if matches:
                    match = matches[0]
                    sent_tokens.append(match)
            subjects = [
                t for t in sent_tokens
                if t['meaning'] in doc_subjs
            ]

            descriptions = [
                t for t in sent_tokens
                if t['meaning'] in doc_mods

            ]

            objects = [
                t for t in sent_tokens
                if t['meaning'] in doc_objs
            ]

            verbs = [
                t for t in sent_tokens
                if 'verb' in t['category']

            ]

            if subjects:
                n_subject = subjects[0]
            else:
                n_subject = dict()
            if objects:
                n_object = objects[0]
            else:
                n_object = dict()
            if verbs:
                verb = verbs[0]
            else:
                verb = dict()
            if descriptions:
                description = descriptions[0]
            else:
                description = dict()

            sentence_components = {
                'subject':n_subject,
                'object':n_object,
                'verb':verb,
                'description':description,
                # 'tense':tense,
                # 'aspect':aspect,
                # 'modality':modality,
                #'place':place,
                # 'locative':locative,
                # 'evidential':evidential,
            }
            return sentence_components


        n_subject = dict()
        n_object = dict()
        verb = dict()
        tense = dict()
        aspect = dict()
        modality = dict()
        evidential = dict()
        place = dict()
        locative = dict()
        subj_description = dict()
        obj_description = dict()

        subjects = [
            l for l in self.lexicon
            if 'noun' in l['category']
            and 'subject' in l['category']
        ]

        objects = [
            l for l in self.lexicon
            if 'noun' in l['category']
            or 'object' in l['category']
        ]

        verbs = [
            l for l in self.lexicon
            if 'verb' in l['category']
        ]

        descriptions = [
            t for t in self.lexicon
            if 'description' in t['category']

        ]

        places = [
            l for l in self.lexicon
            if 'place' in l['category']
            and 'locative' not in l['category']
        ]

        tenses = [
            m for m in self.morphemes
            if 'tense' in m['category']
        ]

        aspects = [
            m for m in self.morphemes
            if 'aspect' in m['category']
        ]

        modalities = [
            m for m in self.morphemes
            if 'modality' in m['category']
        ]

        evidentials = [
            m for m in self.morphemes
            if 'evidentiality' in m['category']
        ]

        if self.adpositions == 'morpheme':
            locatives = [
                m for m in self.morphemes
                if 'locative' in m['category']
            ]
        else:
            locatives = [
                l for l in self.lexicon
                if 'locative' in l['category']
            ]

        if places:
            place = random.choice(places)
        if locatives:
            locative = random.choice(locatives)

        # TODO: identify nouns that can be agents and patients
        # TODO: PNG agreement
        n_subject = random.choice(subjects)
        n_object = random.choice(objects)
        verb = random.choice(verbs)

        if tenses:
            tense = random.choice(tenses)
        if aspects:
            aspect = random.choice(aspects)
        if modalities:
            modality = random.choice(modalities)
        if evidentials:
            evidential = random.choice(evidentials)
        if descriptions:
            subj_description = random.choice(descriptions)
            obj_description = random.choice(descriptions)

        sentence_components = {
            'subject':n_subject,
            'subj_description':subj_description,
            'object':n_object,
            'obj_description':obj_description,
            'verb':verb,
            'tense':tense,
            'aspect':aspect,
            'modality':modality,
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
                    self.phonology_rules['min_syl_per_morpheme'],
                    self.phonology_rules['max_syl_per_morpheme']
                )
                self.morphemes.append(adposition)
            else:
                adposition = self.create_lemma(
                    adposition,
                    self.phonology_rules['min_syl_per_word'],
                    self.phonology_rules['max_syl_per_word']
                )
                self.lexicon.append(adposition)

    def build_lexicon(self):
        for lexeme in self.all_lexemes:
            lexeme = self.create_lemma(
                lexeme,
                self.phonology_rules['min_syl_per_word'],
                self.phonology_rules['max_syl_per_word']
            )
            self.lexicon.append(lexeme)


    def __init__(self, cfg_fname):
        cfg = load_config(cfg_fname)
        data_cfg = cfg['data']
        phonology_cfg = cfg['phonology']
        morphology_cfg = cfg['morphology']
        lexicon_cfg = cfg['lexicon']
        syntax_cfg = cfg['syntax']

        lexicon_fnames = [Path(f) for f in data_cfg['lexicon_fnames']]
        adposition_fname = Path(data_cfg['adposition_fname'])
        phoneme_fname = Path(data_cfg['phoneme_fname'])
        morpheme_fname = Path(data_cfg['morpheme_fname'])
        sentence_fname = Path(data_cfg['sentences_fname'])

        self.all_phonemes = load_phonemes(phoneme_fname)
        self.all_morphemes = load_morphemes(morpheme_fname)
        self.all_adpositions = load_adpositions(adposition_fname)
        self.all_lexemes = load_lexicon(lexicon_fnames)
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
        self.morphology_rules = dict()
        self.phonology_rules = dict()
        self.syntax_rules = dict()
        self.lexicon_rules = dict()

        for param in phonology_cfg:
            self.phonology_rules[param] = convert_param(phonology_cfg, param)
        for param in syntax_cfg:
            self.syntax_rules[param] = convert_param(syntax_cfg, param)
        for param in morphology_cfg:
            self.morphology_rules[param] = convert_param(morphology_cfg, param)
        for param in lexicon_cfg:
            self.lexicon_rules[param] = convert_param(lexicon_cfg, param)

        self.create_phonology()
        self.create_morphology()
        self.create_adpositions()
        self.build_lexicon()


def sentence_demo():
    """
    for lexeme in conlang.lexicon:
        meaning = lexeme['meaning']
        lemma = lexeme['lemma']
        print(f"{lemma}: {meaning}")
    """
    for i in range(20):
        sent = conlang.generate_sentence()
        for constituent in conlang.syntax_rules['word_order']:
            if constituent == 's':
                lemma = sent['subject']['lemma']
                meaning = sent['subject']['meaning']
                print(f"subject: {lemma} ({meaning})")
            if constituent == 'v':
                lemma = sent['verb']['lemma']
                meaning = sent['verb']['meaning']
                print(f"verb: {lemma} ({meaning})")
            if constituent == 'o':
                lemma = sent['object']['lemma']
                meaning = sent['object']['meaning']
                print(f"object: {lemma} ({meaning})")
        for role, component in sent.items():
            if role not in ['subject', 'verb', 'object']:
                lemma = component.get('lemma', '')
                meaning = component.get('meaning', '')
                print(f"{role}: {lemma} ({meaning})")
        print()
    custom_sents = [
        "The cat sees dark water",
        "The elf likes cats",
    ]
    for custom_sent in custom_sents:
        print(custom_sent)
        sent = conlang.generate_sentence(custom_sent)
        for constituent in conlang.syntax_rules['word_order']:
            if constituent == 's':
                lemma = sent['subject'].get('lemma','')
                meaning = sent['subject'].get('meaning', '')
                print(f"subject: {lemma} ({meaning})")
            if constituent == 'v':
                lemma = sent['verb'].get('lemma','')
                meaning = sent['verb'].get('meaning', '')
                print(f"verb: {lemma} ({meaning})")
            if constituent == 'o':
                lemma = sent['object'].get('lemma','')
                meaning = sent['object'].get('meaning','')
                print(f"object: {lemma} ({meaning})")
        for role, component in sent.items():
            if role not in ['subject', 'verb', 'object']:
                lemma = component.get('lemma', '')
                meaning = component.get('meaning', '')
                print(f"{role}: {lemma} ({meaning})")
        print()


def get_morpheme_by_meaning(conlang, meaning):
    matches = [
        m for m in conlang.morphemes
        if m['meaning'].lower() == meaning.lower()
    ]
    if matches:
        return matches[0]
    else:
        return dict()


def get_lexeme_by_meaning(conlang, meaning):
    matches = [
        l for l in conlang.lexicon
        if l['meaning'].lower() == meaning.lower()
    ]
    if matches:
        return matches[0]
    else:
        return dict()


if __name__ == "__main__":
    conlang = Conlang(CFG_FNAME)
    conlang.save_conlang(DEST_FNAME)
    with Path(f"spells_{now}.txt").open('w') as dest:
        dest.write(f'Sentences for {DEST_FNAME.stem}\n')
        dest.write("\n")
        dest.write("Eldritch blast: Fear my dark power\n")
        eldritch = get_lexeme_by_meaning(conlang, 'eldritch').get('lemma', '')
        blast = get_lexeme_by_meaning(conlang, 'blast').get('lemma', '')
        fear = get_lexeme_by_meaning(conlang, 'fear').get('lemma', '')
        imperative = get_morpheme_by_meaning(conlang, 'imperative').get('lemma', '')
        me = get_morpheme_by_meaning(conlang, 'pronoun_1stsingular').get('lemma', '')
        gen = get_morpheme_by_meaning(conlang, 'gen').get('lemma', '')
        dark = get_lexeme_by_meaning(conlang, 'dark (malicious)').get('lemma', '')
        power = get_lexeme_by_meaning(conlang, 'power').get('lemma', '')
        dest.write(f"{eldritch} {blast}: {fear}-{imperative} {me}-{gen} {dark} {power}\n")
        for word, lemma in [
                ("eldritch", eldritch),
                ("blast", blast),
                ("fear", fear),
                ("imperative", imperative),
                ("me", me),
                ("genitive case", gen),
                ("dark", dark),
                ("power", power),
            ]:
            dest.write(f"\t{word}: {lemma}\n")
        dest.write("\n\n")


        dest.write("Minor illusion: I'm going to lie (deceive) in magic now\n")
        minor = get_lexeme_by_meaning(conlang, 'minor').get('lemma', '')
        illusion = get_lexeme_by_meaning(conlang, 'illusion').get('lemma', '')
        me = get_morpheme_by_meaning(conlang, 'pronoun_1stsingular').get('lemma', '')
        near_fut = get_morpheme_by_meaning(conlang, 'near_future').get('lemma', '')
        deceive = get_lexeme_by_meaning(conlang, 'deceive').get('lemma', '')
        in_the = get_lexeme_by_meaning(conlang, 'in the kitchen').get('lemma', '')
        magic = get_lexeme_by_meaning(conlang, 'magic').get('lemma', '')
        now = get_lexeme_by_meaning(conlang, 'now').get('lemma', '')
        dest.write(f"{minor} {illusion}: {me} {near_fut} {deceive} {in_the} {magic} {now}\n")
        for word, lemma in [
                ("minor", minor),
                ("illusion", illusion),
                ("me", me),
                ("near future tense", near_fut),
                ("deceive", deceive),
                ("in/at/on", in_the),
                ("magic", magic),
                ("now", now),
            ]:
            dest.write(f"\t{word}: {lemma}\n")
        dest.write("\n\n")

        dest.write("Hellish rebuke: oh no you did not\n")
        hellish = get_lexeme_by_meaning(conlang, 'hellish').get('lemma', '')
        rebuke = get_lexeme_by_meaning(conlang, 'rebuke').get('lemma', '')
        oh_no = get_lexeme_by_meaning(conlang, 'interjection of indignation').get('lemma', '')
        you = get_morpheme_by_meaning(conlang, 'pronoun_2ndsingular').get('lemma', '')
        neg = get_morpheme_by_meaning(conlang, 'negative').get('lemma', '')
        do_thus = get_lexeme_by_meaning(conlang, 'to do thusly').get('lemma', '')
        past = get_morpheme_by_meaning(conlang, 'past').get('lemma', '')
        dest.write(f"{hellish} {rebuke}: {oh_no} {you} {neg} {do_thus}-{past}\n")
        for word, lemma in [
                ("hellish", hellish),
                ("rebuke", rebuke),
                ("oh_no", oh_no),
                ("you", you),
                ("negation", neg),
                ("to do (thusly)", do_thus),
                ("past tense", past),
            ]:
            dest.write(f"\t{word}: {lemma}\n")
        dest.write("\n\n")

        dest.write("Unseen servant: let them marvel at my mysterious powers\n")
        unseen = get_lexeme_by_meaning(conlang, 'unseen').get('lemma', '')
        servant = get_lexeme_by_meaning(conlang, 'servant').get('lemma', '')
        marvel = get_lexeme_by_meaning(conlang, 'marvel').get('lemma', '')
        them = get_morpheme_by_meaning(conlang, 'pronoun_3rdmany').get('lemma', '')
        hort = get_morpheme_by_meaning(conlang, 'hortative').get('lemma', '')
        in_the = get_lexeme_by_meaning(conlang, 'in the kitchen').get('lemma', '')
        me = get_morpheme_by_meaning(conlang, 'pronoun_1stsingular').get('lemma', '')
        gen = get_morpheme_by_meaning(conlang, 'gen').get('lemma', '')
        mysterious = get_lexeme_by_meaning(conlang, 'mysterious').get('lemma', '')
        power = get_lexeme_by_meaning(conlang, 'power').get('lemma', '')
        pl = get_morpheme_by_meaning(conlang, 'plural').get('lemma', '')
        dest.write(f"{unseen} {servant}: {marvel}-{them}-{hort} {in_the} {me}-{gen} {mysterious} {power}-{pl}\n")
        for word, lemma in [
                ("unseen", unseen),
                ("servant", servant),
                ("marvel", marvel),
                ("they", them),
                ("hortative mood", hort),
                ("in/at/on", in_the),
                ("me", me),
                ("genitive case", gen),
                ("mysterious", mysterious),
                ("power", power),
                ("plural", pl),
            ]:
            dest.write(f"\t{word}: {lemma}\n")


