"""Remplit deux caches consultes par annotation_filters.py :
 - dbpedia_aliases.json : couples (mention, ressource DBpedia) pour lesquels la
   page portant le nom de la mention est une redirection vers la ressource
   (ex. "Tarentum" redirige vers "Taranto") : la mention est alors un nom
   reconnu de la ressource ;
 - wikidata_descriptions.json : description anglaise de chaque entite Wikidata
   annotee, pour ecarter les films, groupes, marques, villes... sans rapport.
Usage : python3 refresh_annotation_caches.py paires_dbpedia.json ids_wikidata.json
(les deux fichiers sont des listes JSON : [[mention, uri], ...] et [uri, ...])."""
import json, os, sys, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))


def _post(url, data, headers=None, tries=6):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(), headers=headers or {})
            return json.load(urllib.request.urlopen(req, timeout=120))
        except Exception as e:
            time.sleep(min(5 * (k + 1), 60))
    return None


def resource_for(mention):
    m = mention.strip()
    if not m or any(c in m for c in '<>"{}|\\^`'):
        return None
    m = m[:1].upper() + m[1:]
    return 'http://dbpedia.org/resource/' + urllib.parse.quote(m.replace(' ', '_'), safe="_,()'-:!*.")


def dbpedia_aliases(pairs, out_path, batch=100):
    found = json.load(open(out_path, encoding='utf-8')) if os.path.exists(out_path) else {}
    done = set(found.get('_checked', []))
    todo = [(m, c) for m, c in pairs if f'{m}|{c}' not in done]
    aliases = set(found.get('aliases', []))
    for i in range(0, len(todo), batch):
        chunk = todo[i:i + batch]
        rows, back = [], {}
        for m, c in chunk:
            r = resource_for(m)
            if r:
                rows.append(f'(<{r}> <{c}>)')
                back[(r, c)] = (m, c)
        if rows:
            q = 'PREFIX dbo: <http://dbpedia.org/ontology/> SELECT ?r ?c WHERE { VALUES (?r ?c) { %s } ?r dbo:wikiPageRedirects ?c }' % ' '.join(rows)
            d = _post('https://dbpedia.org/sparql', {'query': q, 'format': 'application/json'})
            if d is None:
                continue
            for b in d['results']['bindings']:
                key = (b['r']['value'], b['c']['value'])
                if key in back:
                    aliases.add(f'{back[key][0].lower()}|{back[key][1]}')
        done.update(f'{m}|{c}' for m, c in chunk)
        if (i // batch) % 20 == 0:
            json.dump({'aliases': sorted(aliases), '_checked': sorted(done)}, open(out_path, 'w', encoding='utf-8'))
            print('dbpedia', i, '/', len(todo), 'alias trouves', len(aliases), flush=True)
    json.dump({'aliases': sorted(aliases), '_checked': sorted(done)}, open(out_path, 'w', encoding='utf-8'))


def wikidata_descriptions(ids, out_path, batch=50):
    cache = json.load(open(out_path, encoding='utf-8')) if os.path.exists(out_path) else {}
    qids = [u.rstrip('/').split('/')[-1] for u in ids]
    qids = [q for q in qids if q not in cache]
    for i in range(0, len(qids), batch):
        d = _post('https://www.wikidata.org/w/api.php',
                  {'action': 'wbgetentities', 'ids': '|'.join(qids[i:i + batch]), 'props': 'labels|descriptions',
                   'languages': 'en', 'format': 'json'}, headers={'User-Agent': 'zoomathia-annotation-filters/1.0'})
        if d is None:
            continue
        for k, v in d.get('entities', {}).items():
            cache[k] = {'label': v.get('labels', {}).get('en', {}).get('value'),
                        'description': v.get('descriptions', {}).get('en', {}).get('value')}
        if (i // batch) % 20 == 0:
            json.dump(cache, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False)
            print('wikidata', i, '/', len(qids), flush=True)
    json.dump(cache, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False)


if __name__ == '__main__':
    pairs = json.load(open(sys.argv[1], encoding='utf-8'))
    ids = json.load(open(sys.argv[2], encoding='utf-8'))
    wikidata_descriptions(ids, os.path.join(HERE, 'wikidata_descriptions.json'))
    dbpedia_aliases([tuple(p) for p in pairs], os.path.join(HERE, 'dbpedia_aliases.json'))
