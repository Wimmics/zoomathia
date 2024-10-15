import spacy

def get_NER_from_wikidata(element, lg):
    if lg == "en":
        nlp_model = spacy.load("en_core_web_sm")
        nlp_model.add_pipe("entityfishing", config={"api_ef_base": "http://nerd.huma-num.fr/nerd/service"})
    if lg == "it":
        nlp_model = spacy.load("it_core_news_sm")
        nlp_model.add_pipe("entityfishing", config={"language": lg, "api_ef_base": "http://nerd.huma-num.fr/nerd/service"})
    origin_text = element.text
    en_text = nlp_model(origin_text)
    print('Entities wikidata',
      [(ent.text, ent.label_, ent._.kb_qid, ent._.url_wikidata, ent._.nerd_score) for ent in en_text.ents])
    return en_text
