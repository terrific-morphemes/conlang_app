"""Create vocab lists from texts"""
from pathlib import Path
import csv

import spacy
nlp = spacy.load('en')

SOURCE_FNAMES = [
    Path("./backend/data/texts/bard.txt"),
    Path("./backend/data/texts/tiefling.txt")
]

DEST_FNAME = Path("./backend/data/vocab_lists/dnd.csv")

def vocab_from_txt(source_fnames, dest_fname):
    seen_lemmata = set()
    new_vocab = list()
    for source_fname in source_fnames:
        with source_fname.open() as source:
            raw = source.read()
            doc = nlp(raw)
            word_types = set(t for t in doc)
            for t in word_types:
                if t.lemma_.isalpha() and t.lemma_ not in seen_lemmata:
                    seen_lemmata.add(t.lemma_)
                    pos = t.pos_.lower()
                    dep = t.dep_.lower()
                    role = ""
                    if 'subj' in role:
                        role = 'subject'
                    elif 'dobj' in role:
                        role = 'object'
                    elif 'pobj' in role:
                        role = 'place'
                    category = f"{pos}_{role}"
                    lexeme = {
                        'word':t.lemma_,
                        'lemma':'',
                        'category':category,
                    }
                    new_vocab.append(lexeme)
    with dest_fname.open('w') as dest:
        writer = csv.DictWriter(
            dest,
            fieldnames=['word', 'lemma','category'],
        )
        writer.writeheader()
        for lexeme in sorted(new_vocab, key=lambda x:x['word']):
            writer.writerow(lexeme)

if __name__ == "__main__":
    vocab_from_txt(SOURCE_FNAMES, DEST_FNAME)
