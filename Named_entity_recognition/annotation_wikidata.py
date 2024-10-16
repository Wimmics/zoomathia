import spacy

API_ENDPOINT_URL = "http://nerd.huma-num.fr/nerd/service"
def get_NER_from_wikidata(element, lg="en"):

    if lg == "it":
        nlp_model = spacy.load("it_core_news_lg")
        nlp_model.add_pipe("entityfishing", config={"language": lg, "api_ef_base": API_ENDPOINT_URL})
    else:
        nlp_model = spacy.load("en_core_web_sm")
        nlp_model.add_pipe("entityfishing", config={'language': lg, "api_ef_base": API_ENDPOINT_URL})

    en_text = nlp_model(element)

    return en_text.ents

if __name__ == "__main__":
    dbpedia = "Barack Hussein Obama II[a] (born August 4, 1961) is an American politician who served as the 44th president of the United States from 2009 to 2017. As a member of the Democratic Party, he was the first African-American president in U.S. history. Obama previously served as a U.S. senator representing Illinois from 2005 to 2008 and as an Illinois state senator from 1997 to 2004. "
    wikidata = "Victor Hugo and Honoré de Balzac are French writers who lived in Paris."
    en_text_test = get_NER_from_wikidata(wikidata)
    print('Entities wikidata',
          [(ent.text, ent.label_, ent._.kb_qid, ent._.url_wikidata, ent._.nerd_score) for ent in en_text_test.ents])
