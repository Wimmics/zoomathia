import spacy


def get_NER_from_wikidata(element, lg):
    if lg == "en":
        nlp_model = spacy.load("en_core_web_sm")
        nlp_model.add_pipe("entityfishing")
    if lg == "it":
        nlp_model = spacy.load("it_core_news_sm")
        nlp_model.add_pipe("entityfishing", config={"language": lg})
    origin_text = element.text
    #print(origin_text)
    en_text = nlp_model(origin_text)
    return en_text
