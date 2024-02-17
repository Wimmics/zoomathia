import spacy


def get_NER_from_dbpedia(element,lg):
    nlp = spacy.blank(lg)
    #nlp.add_pipe('dbpedia_spotlight')
    #nlp.add_pipe('dbpedia_spotlight', config={'types': 'DBpedia:Place', 'confidence': 0.6})
    #nlp.add_pipe('dbpedia_spotlight', config={'confidence': 0.6})
    if lg == "en":
        nlp.add_pipe('dbpedia_spotlight', config={'dbpedia_rest_endpoint': 'http://localhost:2222/rest','confidence': 0.6})
        origin_text = element.text
        #print(origin_text)
        en_text = nlp(origin_text)
    if lg == "it":
        nlp.add_pipe('dbpedia_spotlight',
                     config={'dbpedia_rest_endpoint': 'http://localhost:2223/rest', 'confidence': 0.6})
        origin_text = element.text
        # print(origin_text)
        en_text = nlp(origin_text)
    return en_text
    # nlp.get_pipe('dbpedia_spotlight').language_code = 'it'
