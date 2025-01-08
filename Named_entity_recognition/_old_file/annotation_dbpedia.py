import spacy

def get_NER_from_dbpedia(element,lg="en"):

    nlp = spacy.load("en_core_web_lg")
    nlp.add_pipe('dbpedia_spotlight', config={'confidence': 0.6})

    en_text = nlp(element)

    return en_text.ents

if __name__ == "__main__":
    dbpedia = "Barack Hussein Obama II[a] (born August 4, 1961) is an American politician who served as the 44th president of the United States from 2009 to 2017. As a member of the Democratic Party, he was the first African-American president in U.S. history. Obama previously served as a U.S. senator representing Illinois from 2005 to 2008 and as an Illinois state senator from 1997 to 2004. "
    wikidata = "Victor Hugo and Honoré de Balzac are French writers who lived in Paris."
    en_text_test = get_NER_from_dbpedia(wikidata)
    print('Entities dbpedia', [(ent.text, ent.label_, ent.kb_id_) for ent in en_text_test.ents])
