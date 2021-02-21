//xsampa, ipa, description, level
#[derive(Debug)]
struct Phoneme(String, String, String, i32);

//meaning, lemma, category
#[derive(Debug)]
struct Morpheme(String, String, String);

#[derive(Debug)]
struct Lexeme(String, String, String);

fn make_phoneme(xsampa: &str, ipa: &str, description: &str, level: i32) -> Phoneme {
    let xsampa_str = String::from(xsampa);
    let ipa_str = String::from(ipa);
    let description_str = String::from(description);
    return Phoneme(xsampa_str, ipa_str, description_str, level);
}

fn make_morpheme(meaning: &str, lemma: &str, category: &str) -> Morpheme {
    let meaning_str = String::from(meaning);
    let lemma_str = String::from(lemma);
    let category_str = String::from(category);
    return Morpheme(meaning_str, lemma_str, category_str);
}

fn make_lexeme(meaning: &str, lemma: &str, category: &str) -> Lexeme {
    let meaning_str = String::from(meaning);
    let lemma_str = String::from(lemma);
    let category_str = String::from(category);
    return Lexeme(meaning_str, lemma_str, category_str);
}

#[derive(Debug)]
struct Conlang {
    name: String,
    initials: Phoneme,
    medials: Phoneme,
    finals: Phoneme,
    tones: String,
    morphemes: Morpheme,
    lexemes: Lexeme,
    adpositions: Morpheme,
    // morphology_rules: String,
    // syntax_rules: String,
    // phonology_rules: String,
    // lexicon_rules: String,
}

impl Conlang {
    fn get_phonology(&self) {
        println!("The phonology is {:?} {:?} {:?} {:?}", self.initials, self.medials, self.finals, self.tones)
    }
}

fn make_conlang() -> Conlang {
    let conlang = Conlang {
        name: String::from("Eedh"),
        initials: make_phoneme("a", "b", "c", 1),
        medials: make_phoneme("a", "b", "c", 1),
        finals: make_phoneme("a", "b", "c", 1),
        tones: String::from("no tones"),
        morphemes: make_morpheme("go", "yay", "yes"),
        lexemes: make_lexeme("stop", "boo", "no"),
        adpositions: make_morpheme("wait", "hmm", "maybe"),
    };
    return conlang;
}


fn main() {
    let conlang = make_conlang();
    println!("Created a conlang named {}", conlang.name);
    conlang.get_phonology();
}
