let fs = require('fs');

const executeDescribeRequest = async (endpoint, query) => {
    /**
     * TODO:  Catch unexpected error during fetch (fetchControler)
     */
    try {
        // POST plutot que GET+query en parametre d'URL : certaines requetes
        // (ex. /getSummary sur une oeuvre au titre long/non-ASCII, repete
        // plusieurs fois dans les branches UNION) depassent, une fois
        // URL-encodees, la limite de taille de ligne de requete de Jetty
        // (~8 Ko), qui repond alors une page d'erreur HTML au lieu du JSON
        // attendu - echec silencieux cote client (resultat vide). Le corps
        // POST n'a pas cette limite.
        let result_data = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': `text/turtle`
            },
            body: new URLSearchParams({ query, format: 'turtle' })
        })
        return await result_data.text()
    }
    catch (e) {
        console.log(`Request fail...`)
        console.log(e)
        if (e.cause?.code === 'ECONNREFUSED') {
            console.log("SPARQL Endpoint unreachable, server is not launch or doesn't accept connection")
        } else {
            console.log(e.cause)
        }
        return "Doesn't work..."
    }
}

const executeSPARQLRequest = async (endpoint, query) => {
    /**
     * TODO:  Catch unexpected error during fetch (fetchControler)
     */
    try {
        // POST plutot que GET+query en parametre d'URL : voir le commentaire
        // equivalent dans executeDescribeRequest ci-dessus (meme limite
        // Jetty ~8 Ko sur la ligne de requete GET).
        let result_data = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': `application/sparql-results+json`
            },
            body: new URLSearchParams({ query, format: 'json' })
        })
        return await result_data.json()
    }
    catch (e) {
        console.log(`Request fail...`)
        console.log(e)
        if (e.cause?.code === 'ECONNREFUSED') {
            console.log("SPARQL Endpoint unreachable, server is not launch or doesn't accept connection")
        } else {
            console.log(e.cause)
        }
        return {
            head: {
                vars: []
            },
            results: {
                bindings: []
            }
        }
    }
}

/**
 * Read a SPARQL query template and replace the {id} placeholder
 * @param {string} template - the template file name
 * @param {number} id - value to replace "{id}" with
 * @returns {string} SPARQL query string
 */
const readTemplate = (template, id) => {
    let queryTpl = fs.readFileSync('queries/' + template, 'utf8');
    return queryTpl.replaceAll("{id}", id);
}

/**
 * Read a SPARQL query template and replace the {id} placeholder
 * @param {string} template - the template file name
 * @param {number} id - value to replace "{id}" with
 * @returns {string} SPARQL query string
 */
const getCompetenciesQuestion = (file) => {
    let queryTpl = fs.readFileSync(`queries/qc${file}.rq`, 'utf8');
    return queryTpl;
}

const checkParagraph = (node, paragraph) => {
    for(const p of node.children){
        if(p.id === paragraph.id){
            return true
        }
    }
    return false
}

const getTypeFromURI = (uri) => {
    const uri_split = uri.split('#')
    return uri_split[uri_split.length - 1]
}

const jsonToCsv = (jsonObject) => {
    const header = jsonObject.head.vars
    let fileWriter = []

    fileWriter.push(header.join(";"))

    for(const line of jsonObject.results.bindings){
        const temp = []
        for(const title of header){
            temp.push(line[title].value)
        }
        fileWriter.push(temp.join(";"))
    }

    return fileWriter.join("\n")
}

// Les questions de competence "getQC" combinent en general plusieurs blocs
// d'annotation independants (ex. "quel animal" + "quel lieu") joints sur le
// meme ?paragraph. Executee telle quelle, cette jointure est tres lente sur
// Corese des que les deux blocs sont volumineux (des dizaines de milliers de
// lignes chacun) : le moteur semble comparer chaque paire au lieu d'indexer
// sur ?paragraph, ce qui explose meme quand le resultat final ne compte que
// quelques centaines de milliers de lignes. On execute donc chaque bloc
// separement (rapide seul) et on fait la jointure ici, cote serveur.

const extractPrefixes = (queryText) => {
    const matches = queryText.match(/^\s*prefix\s+\w*:\s*<[^>]+>\s*$/gim) || []
    return matches.join('\n')
}

const extractSelectVars = (queryText) => {
    const match = queryText.match(/select\s+distinct\s+([\s\S]*?)\s+where/i)
    if (!match) return []
    return [...match[1].matchAll(/\?(\w+)/g)].map(m => m[1])
}

// Extrait le contenu de la clause WHERE (entre les accolades correspondantes).
const extractWhereBody = (queryText) => {
    const whereIndex = queryText.search(/where\s*\{/i)
    if (whereIndex === -1) return null
    const braceStart = queryText.indexOf('{', whereIndex)
    let depth = 0
    for (let i = braceStart; i < queryText.length; i++) {
        if (queryText[i] === '{') depth++
        else if (queryText[i] === '}') {
            depth--
            if (depth === 0) return queryText.slice(braceStart + 1, i)
        }
    }
    return null
}

const ANNOTATION_BLOCK_START = /\?annotation\d+\s+(?:a\s+oa:Annotation\s*;\s*)?oa:hasBody\s+\?(\w+)/g

// Extrait chaque clause FILTER(...) (parentheses equilibrees, ex.
// "FILTER (lang(?x) = "en")" en contient une paire imbriquee), avec son
// eventuel "." final, et renvoie le texte nettoye (sans ces FILTER) plus
// la liste des clauses trouvees.
const extractFilters = (text) => {
    const filters = []
    let cleaned = ''
    const filterStart = /filter\s*\(/gi
    let lastIndex = 0
    let match
    while ((match = filterStart.exec(text))) {
        if (match.index < lastIndex) continue
        const parenStart = match.index + match[0].length - 1
        let depth = 0
        let end = parenStart
        for (; end < text.length; end++) {
            if (text[end] === '(') depth++
            else if (text[end] === ')') {
                depth--
                if (depth === 0) break
            }
        }
        end += 1
        const trailingDot = text.slice(end).match(/^\s*\./)
        if (trailingDot) end += trailingDot[0].length
        cleaned += text.slice(lastIndex, match.index)
        filters.push(text.slice(match.index, end))
        lastIndex = end
        filterStart.lastIndex = lastIndex
    }
    cleaned += text.slice(lastIndex)
    return { cleaned, filters }
}

// Decoupe le corps de la clause WHERE en blocs, un par annotation
// (?annotationN oa:hasBody ...), chaque bloc restant autonome (seul
// ?paragraph est partage entre blocs). Retourne null si la requete ne suit
// pas ce schema (moins de 2 blocs), auquel cas on l'execute telle quelle.
const splitAnnotationBlocks = (whereBody) => {
    // Retire la liaison redondante zoo:hasAnnotation : deja couverte par
    // oa:hasTarget/oa:hasSource dans chaque bloc, elle n'appartient a aucun
    // bloc en particulier.
    const withoutConnector = whereBody.replace(/\?paragraph\s+zoo:hasAnnotation\s+[^.]*\.\s*/i, '')

    // Les FILTER sont souvent regroupees en fin de requete (une par
    // variable), pas forcement juste apres le bloc auquel elles
    // appartiennent : on les extrait d'abord pour les rattacher ensuite au
    // bon bloc selon la variable qu'elles filtrent, plutot que de risquer
    // qu'un FILTER finisse dans un bloc ou sa variable n'est pas liee (ce
    // qui invaliderait la sous-requete entiere).
    const { cleaned, filters } = extractFilters(withoutConnector)

    const starts = [...cleaned.matchAll(ANNOTATION_BLOCK_START)]
    if (starts.length < 2) return null

    const blocks = []
    for (let i = 0; i < starts.length; i++) {
        const start = starts[i].index
        const end = i + 1 < starts.length ? starts[i + 1].index : cleaned.length
        blocks.push(cleaned.slice(start, end))
    }

    for (const filter of filters) {
        const vars = [...filter.matchAll(/\?(\w+)/g)].map(m => m[1])
        const targetIndex = blocks.findIndex(b => vars.every(v => new RegExp(`\\?${v}\\b`).test(b)))
        if (targetIndex !== -1) {
            blocks[targetIndex] += `\n${filter}`
        }
        // Si aucun bloc ne contient toutes les variables du filtre (cas non
        // rencontre dans les questions actuelles), le filtre est ignore
        // plutot que de risquer de casser une sous-requete.
    }

    return blocks
}

const groupByParagraph = (bindings) => {
    const map = new Map()
    for (const row of bindings) {
        const key = row.paragraph.value
        if (!map.has(key)) map.set(key, [])
        map.get(key).push(row)
    }
    return map
}

const executeAnnotationJoinQuery = async (endpoint, queryText) => {
    const whereBody = extractWhereBody(queryText)
    const blocks = whereBody && splitAnnotationBlocks(whereBody)

    if (!blocks) {
        return executeSPARQLRequest(endpoint, queryText)
    }

    const prefixes = extractPrefixes(queryText)
    const selectVars = extractSelectVars(queryText)

    const blockResults = await Promise.all(blocks.map(async (block) => {
        const varsInBlock = selectVars.filter(v => v !== 'paragraph' && new RegExp(`\\?${v}\\b`).test(block))
        const subQuery = `${prefixes}\nSELECT DISTINCT ?paragraph ${varsInBlock.map(v => '?' + v).join(' ')} WHERE {\n${block}\n}`
        const result = await executeSPARQLRequest(endpoint, subQuery)
        return result.results.bindings
    }))

    let joined = blockResults[0].map(row => ({ ...row }))
    for (let i = 1; i < blockResults.length; i++) {
        const grouped = groupByParagraph(blockResults[i])
        const next = []
        for (const row of joined) {
            for (const match of grouped.get(row.paragraph.value) || []) {
                next.push({ ...row, ...match })
            }
        }
        joined = next
    }

    joined.sort((a, b) => a.paragraph.value < b.paragraph.value ? -1 : a.paragraph.value > b.paragraph.value ? 1 : 0)

    return {
        head: { vars: selectVars },
        results: { bindings: joined }
    }
}

// Vue graphe de la question de competence 2 (relation speciale entre un
// animal et un anthroponyme dans un meme passage). La requete SPARQL d'origine
// (qc2_spo.rq) reevalue, pour chaque combinaison possible, un FILTER NOT EXISTS
// qui garde le libelle le plus court d'un concept : trop lourde pour Corese
// (plus de 5 min, donc timeout du backend et graphe vide, pendant que Corese
// continue de saturer le processeur). On reutilise ici la jointure rapide du
// tableau (qc2.rq, ~10 s) en recuperant aussi l'URI de chaque concept, puis on
// choisit le libelle une seule fois par concept, avec la meme regle de
// depart que qc2_spo.rq : longueur croissante, puis ordre alphabetique
// (casse ignoree), puis a egalite la chaine la plus grande.
const QC2_GRAPH_VARS = ['p', 's', 'o', 'date', 'type', 'url', 'style1', 'style2']

const isPreferredLabel = (a, b) => {
    const la = [...a].length, lb = [...b].length
    if (la !== lb) return la < lb
    const a2 = a.toLowerCase(), b2 = b.toLowerCase()
    if (a2 !== b2) return a2 < b2
    return a > b
}

const preferredLabelByConcept = (rows, uriVar, nameVar) => {
    const best = new Map()
    for (const row of rows) {
        const uri = row[uriVar].value, name = row[nameVar].value
        const current = best.get(uri)
        if (current === undefined || isPreferredLabel(name, current)) best.set(uri, name)
    }
    return best
}

const getQC2Graph = async (endpoint) => {
    const template = fs.readFileSync('queries/qc2.rq', 'utf8')
    const query = template.replace(
        /select\s+distinct[\s\S]*?\s+where/i,
        'SELECT DISTINCT ?paragraph ?relation ?animal ?anthro ?name_relation ?name_animal ?name_anthroponym WHERE'
    )
    const joined = await executeAnnotationJoinQuery(endpoint, query)
    const rows = joined.results.bindings

    const relationLabel = preferredLabelByConcept(rows, 'relation', 'name_relation')
    const animalLabel = preferredLabelByConcept(rows, 'animal', 'name_animal')
    const anthroLabel = preferredLabelByConcept(rows, 'anthro', 'name_anthroponym')

    const literal = (value) => ({ type: 'literal', 'xml:lang': 'en', value })
    const text = (value) => ({ type: 'typed-literal', datatype: 'http://www.w3.org/2001/XMLSchema#string', value })

    const seen = new Set()
    const bindings = []
    const add = (paragraph, relation, target, style2, withDate) => {
        const key = `${paragraph}\u0000${relation}\u0000${target}\u0000${style2}`
        if (seen.has(key)) return
        seen.add(key)
        const binding = {
            p: { type: 'uri', value: paragraph },
            s: literal(relation),
            o: literal(target),
            type: literal(relation),
            style1: text('snd'),
            style2: text(style2)
        }
        if (withDate) binding.date = literal(target)
        bindings.push(binding)
    }

    for (const row of rows) {
        const paragraph = row.paragraph.value
        const relation = relationLabel.get(row.relation.value)
        add(paragraph, relation, animalLabel.get(row.animal.value), 'fst', true)
        add(paragraph, relation, anthroLabel.get(row.anthro.value), 'rst', false)
    }

    bindings.sort((a, b) => a.p.value < b.p.value ? -1 : a.p.value > b.p.value ? 1 : 0)
    return { head: { vars: QC2_GRAPH_VARS }, results: { bindings } }
}

exports.getQC2Graph = getQC2Graph;
exports.executeSPARQLRequest = executeSPARQLRequest;
exports.executeAnnotationJoinQuery = executeAnnotationJoinQuery;
exports.readTemplate = readTemplate;
exports.getCompetenciesQuestion = getCompetenciesQuestion;
exports.checkParagraph = checkParagraph;
exports.executeDescribeRequest = executeDescribeRequest;
exports.getTypeFromURI = getTypeFromURI;
exports.jsonToCsv = jsonToCsv;