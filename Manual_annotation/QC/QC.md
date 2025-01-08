## Patch note

- La récupération des résultats via Corèse n'est possible qu'a travers un graphe (XML). Il serait bien de faire un script Python qui transforme les réponses du graphe en CSV (possible avec Py4J et la Corese-Python-Lib) pour pouvoir faire une vérification minutieuse des résultats.  Je proposerai ça à terme, ce qui donnera une base pour le développement d'un "web application" Django.
- Il est difficile de reformuler avec des concepts du thesaurus certains termes des questions (trop précis, pas assez précis, pas d'équivalent direct).

## Préfixes utilisés

```SPARQL
prefix oa:     <http://www.w3.org/ns/oa#>.
prefix skos: <http://www.w3.org/2004/02/skos/core#>.
prefix schema:  <http://schema.org/> .
```



## Requêtes statistiques et tests

- Nombre d'annotation et nombre de concept distinct présent

```SPARQL
PREFIX oa:     <http://www.w3.org/ns/oa#>.
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>.

select distinct (count(?x) as ?an) (count(distinct ?y) as ?nb) where {
  ?x a oa:Annotation;
	oa:hasBody ?y.
  ?y a skos:Concept
}

```

-> 10601 annotations et 1482 concepts différents

- Top 10 des concepts les plus récurent

```SPARQL
PREFIX oa:     <http://www.w3.org/ns/oa#>.
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>.

select distinct ?label (count(?x) as ?nb) where {
  ?x a oa:Annotation;
	oa:hasBody ?y.
  ?y a skos:Concept; skos:prefLabel ?label.
  filter (lang(?label) = "en")
}
GROUP BY ?label
ORDER BY DESC (?nb)
```

| Concept                           | Occurence |
| --------------------------------- | --------- |
| "historical character"@en         | 253       |
| "size"@en                         | 188       |
| "habitat"@en                      | 182       |
| "intellectual authority"@en       | 178       |
| "nourishment"@en                  | 150       |
| "anecdote"@en                     | 111       |
| "similarity to another animal"@en | 111       |
| "female"@en                       | 107       |
| "male"@en                         | 104       |
| "color"@en                        | 103       |


## Requêtes métiers

### Quels sont les animaux qui construisent un habitat (textes où l’on parle de cette construction)

<u>Reformulation:</u> Les annotations qui mentionnent un animal et une construction d'habitation étant dans le même paragraphe.

<u>Note:</u> généralisation de l'animal faisant parti de la **collection** "Archéotaxon" ("Ancient class" en anglais)

<u>Sortie:</u> Le paragraphe, l'animal (concept), le texte mentionnant l'animal, la construction (concept), le texte mentionnant la construction

```SPARQL
PREFIX oa:     <http://www.w3.org/ns/oa#>.
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>.
PREFIX schema:  <http://schema.org/> .

SELECT DISTINCT ?paragraph ?name_animal ?mention_animal ?name_construction ?mention_construction WHERE {
  ?annotation1 a oa:Annotation;
              oa:hasBody ?animal;
              oa:hasTarget ?target1.
  ?target1 oa:hasSource ?paragraph;
     oa:hasSelector ?selector.
    
  ?selector oa:exact ?mention_animal.

  ?animal a skos:Concept;
       skos:prefLabel ?name_animal.
    
  ?animal_collection a skos:Collection;
       skos:prefLabel "Ancient class"@en;
       skos:member ?animal.

  ?annotation2 oa:hasBody ?construction;
        oa:hasTarget ?target2.
  ?target2 oa:hasSource ?paragraph;
      oa:hasSelector ?selector2.
  ?selector2 oa:exact ?mention_construction.

  ?construction skos:prefLabel ?name_construction;
     	            skos:broader+ ?construction_generique.
  ?construction_generique skos:prefLabel "house building"@en.

  FILTER (lang(?name_animal) = "en").
  FILTER (lang(?name_construction) = "en")
}
ORDER BY ?paragraph
```

<u>Extrait de réponse de la requête:</u>

![qc1](img/qc1.png)

### Quelles anecdotes mettant en relation un homme et un animal (pas toutes les relations hommes/animaux, comme la chasse, etc., mais seulement les situations individuelles, qui seront probablement marquées par un nom propre, ou un nom de lieu, etc.)

Reformulation: Les annotation mentionnant une anecdote, une relation homme/animal faisant parti du même paragraphe.

Note: Je me suis restreint à des relations spéciales (prédation, enmity, friendship)

```SPARQL
PREFIX oa:     <http://www.w3.org/ns/oa#>.
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>.
PREFIX schema:  <http://schema.org/> .
PREFIX paragraph: <http://www.zoomathia.com/>.

SELECT DISTINCT ?paragraph ?name_animal ?name_relation ?name_anthro WHERE {
  ?annotation1 a oa:Annotation;
              oa:hasBody ?animal;
              oa:hasTarget ?target1.
  ?target1 oa:hasSource ?paragraph;
     oa:hasSelector ?selector.
 ?selector oa:exact ?mention_animal.

  ?annotation2 oa:hasBody ?relation;
        oa:hasTarget ?target2.
  ?target2 oa:hasSource ?paragraph;
      oa:hasSelector ?selector2.
  ?selector2 oa:exact ?mention_relation.

   ?annotation3 oa:hasBody ?anthro;
        oa:hasTarget ?target3.
  ?target3 oa:hasSource ?paragraph;
      oa:hasSelector ?selector3.
  ?selector3 oa:exact ?mention_anthro.

  ?animal a skos:Concept;
       skos:prefLabel ?name_animal.
    
  ?animal_collection a skos:Collection;
       skos:prefLabel "Ancient class"@en;
       skos:member ?animal.

  ?relation skos:prefLabel ?name_relation;
     	            skos:broader+ ?relation_generique.
  ?relation_generique skos:prefLabel  "special relationship"@en.

 ?anthro skos:prefLabel ?name_anthro.
 ?anthro_collection skos:prefLabel ?anthro_collection_name;
	skos:member ?anthro.

  FILTER (lang(?name_animal) = "en").
  FILTER (lang(?name_relation) = "en")
  FILTER (lang(?name_anthro) = "en")
  FILTER (?anthro_collection_name in ("Place"@en, "Anthroponym"@en))
}
ORDER BY ?paragraph
```

Extrait résultat:

![qc2](img/qc2.png)

### Quels sont les oiseaux qui sont consommés (gastronomie)

Reformulation: Les annotations mentionnant un oiseau et une gastronomie faisant parti du même paragraphe

Note: L'insertion d'une collection Oiseau serait intéressante.

```SPARQL
PREFIX oa:     <http://www.w3.org/ns/oa#>.
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>.
PREFIX schema:  <http://schema.org/> .

SELECT DISTINCT ?paragraph ?name_animal ?mention_animal ?name_conso ?mention_conso WHERE {
  ?annotation1 a oa:Annotation;
              oa:hasBody ?animal;
              oa:hasTarget ?target1.
  ?target1 oa:hasSource ?paragraph;
     oa:hasSelector ?selector.
    
  ?selector oa:exact ?mention_animal.

  ?animal a skos:Concept;
       skos:prefLabel ?name_animal;
       skos:broader+ ?animal_generique.
    
  ?animal_generique a skos:Concept;
       skos:prefLabel ?name_animal_generique.

  ?annotation2 oa:hasBody ?conso;
        oa:hasTarget ?target2.
  ?target2 oa:hasSource ?paragraph;
      oa:hasSelector ?selector2.
  ?selector2 oa:exact ?mention_conso.

  ?conso skos:prefLabel ?name_conso;
     	            skos:broader+ ?conso_generique.
  ?conso_generique skos:prefLabel ?name_conso_generique.

  FILTER (str(?name_animal_generique) in ("BIRD","BIRD WITH CLAW","BIRD WITH TOES","WATERBIRD","NIGHT BIRD","MIGRATORY BIRD", "PALMIPED BIRD")).
  FILTER (str(?name_conso_generique) = "animal in human nourishing").
  FILTER (lang(?name_animal) = "en").
  FILTER (lang(?name_conso) = "en")
}
ORDER BY ?paragraph
```

Extrait résultat:

![qc3](img/qc3.png)

### Quels sont les remèdes (thérapeutiques) qui incluent une langue animale (ou un morceau de langue)?

Reformulation: Les annotations qui mentionnent un remède , <u>**une langue et un animal**</u> faisant parti du même paragraphe

Note: Difficile de trouver le concept "remède thérapeutique" ou "remède". Dans la hiérarchie, il existe remède vétérinaire (erreur dans l'accent utilisé dans le thésaurus). https://opentheso.huma-num.fr/opentheso/?idc=105552&idt=th310
Tentative d'utilisation "medical use of animal", "medical use of animal parts". Résultat basé sur le concept générique "medical use of animal" et inclue tous les descendant.

Il est possible de trouver les mentions de langue et l'animal en question cependant.

```sparql
PREFIX oa:     <http://www.w3.org/ns/oa#>.
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>.
PREFIX schema:  <http://schema.org/> .

SELECT DISTINCT ?paragraph ?name_animal ?mention1 ?name_use ?mention2 WHERE {
  ?annotation1 a oa:Annotation;
              oa:hasBody ?animal;
              oa:hasTarget ?target1.
  ?target1 oa:hasSource ?paragraph;
     oa:hasSelector ?selector1.

?annotation2 a oa:Annotation;
              oa:hasBody ?use;
              oa:hasTarget ?target2.
  ?target2 oa:hasSource ?paragraph;
     oa:hasSelector ?selector2.
    
  ?selector1 oa:exact ?mention1.
  ?selector2 oa:exact ?mention2.

  ?animal a skos:Concept;
       skos:prefLabel ?name_animal.
    
  ?animal_collection a skos:Collection;
       skos:prefLabel ?name_animal_collection;
       skos:member ?animal.

  ?use skos:prefLabel ?name_use;
	skos:broader+ ?use_generique.
  ?use_generique skos:prefLabel ?name_use_generique.

  FILTER (str(?name_animal_collection) = "Ancient class").
  FILTER (str(?name_use_generique) = "medical use of animal").
  FILTER (lang(?name_animal) = "en").
  FILTER (lang(?name_use) = "en")
}
ORDER BY ?paragraph
```

Extrait résultat:

![qc4](img/qc4.png)

### Quels sont les animaux qui communiquent entre eux (textes où il est question de mode de communication, de langage, etc.)?

Remarque: Pas de concept **spécifique** qui représente ce comportement dans "comportement social". Le Concept le plus proche de communication est "Parole". Possibilité de chercher comportement social général et parole au sein d'un même paragraphe (Pas de résultat).

Solution: On se concentre uniquement sur le concept de parole. Ce qui inclue les mimiques, la compréhension de la parole humaine, etc... 

```sparql
PREFIX oa:     <http://www.w3.org/ns/oa#>.
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>.
PREFIX schema:  <http://schema.org/> .

SELECT DISTINCT ?paragraph ?name_animal ?mention_animal ?name_social ?mention_social WHERE {
  ?annotation1 a oa:Annotation;
              oa:hasBody ?animal;
              oa:hasTarget ?target1.
  ?target1 oa:hasSource ?paragraph;
     oa:hasSelector ?selector.
    
  ?selector oa:exact ?mention_animal.

  ?animal a skos:Concept;
       skos:prefLabel ?name_animal.
    
  ?animal_collection a skos:Collection;
       skos:prefLabel ?name_animal_collection;
       skos:member ?animal.

  ?annotation2 oa:hasBody ?social;
        oa:hasTarget ?target2.
  ?target2 oa:hasSource ?paragraph;
      oa:hasSelector ?selector2.
  ?selector2 oa:exact ?mention_social.

  ?social skos:prefLabel ?name_social.

  FILTER (str(?name_animal_collection) = "Ancient class").
  FILTER (str(?name_social) = "speech").
  FILTER (lang(?name_animal) = "en").
  FILTER (lang(?name_social) = "en")
}
ORDER BY ?paragraph
```

Extrait résultat:

![qc5](img/qc5.png)

### Sur le rythme alimentaire des animaux : quels sont les animaux capables de jeûner, quelles sont les informations sur les rythmes de repas (fréquence)?

Reformulation: une annotation mentionnant un animal et une annotation mentionnant le jeune dans le même paragraphe.

Note: Jeûne en anglais se dit "Fast" ou "Fasting". Peut être renommer le concept en Fasting pour éviter toutes confusion. (se trouve dans vie quotidienne)

 ```sparql
 PREFIX oa:     <http://www.w3.org/ns/oa#>.
 PREFIX skos: <http://www.w3.org/2004/02/skos/core#>.
 PREFIX schema:  <http://schema.org/> .
 
 SELECT DISTINCT ?paragraph ?mention_fasting WHERE {
   ?annotation2 oa:hasBody ?fasting;
         oa:hasTarget ?target2.
   ?target2 oa:hasSource ?paragraph;
       oa:hasSelector ?selector2.
   ?selector2 oa:exact ?mention_fasting.
 
   ?fasting skos:prefLabel ?name_fasting.
 
   FILTER (str(?name_fasting) = "fast").
   FILTER (lang(?name_fasting) = "en")
 }
 ORDER BY ?paragraph
 ```

Aucune mention de jeûne relevée dans les chapitres de Pline. Dans le fichier d'erreur, il y a la mention "special diet" qui pourrait faire référence au jeûne.

### Quelles sont les données transmises sur le temps de gestation des animaux?

Remarque: Il n'existe pas de concept représentant la "**valeur**" du temps de gestion. Voir ce qu'on peut faire (une collection de valeur ?)

```sparql
PREFIX oa:     <http://www.w3.org/ns/oa#>.
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>.
PREFIX schema:  <http://schema.org/> .

SELECT DISTINCT ?paragraph ?mention_pregnancy WHERE {
  ?annotation2 oa:hasBody ?pregnancy;
        oa:hasTarget ?target2.
  ?target2 oa:hasSource ?paragraph;
      oa:hasSelector ?selector2.
  ?selector2 oa:exact ?mention_pregnancy.

  ?pregnancy skos:prefLabel ?name_pregnancy.

  FILTER (str(?name_pregnancy) = "length of pregnancy").
  FILTER (lang(?name_pregnancy) = "en")
}
ORDER BY ?paragraph
###########################################################################################################################
PREFIX oa:     <http://www.w3.org/ns/oa#>.
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>.
PREFIX schema:  <http://schema.org/> .

SELECT DISTINCT ?paragraph ?name_animal ?mention_animal ?mention_pregnancy WHERE {
?annotation1 a oa:Annotation;
              oa:hasBody ?animal;
              oa:hasTarget ?target1.
  ?target1 oa:hasSource ?paragraph;
     oa:hasSelector ?selector.
    
  ?selector oa:exact ?mention_animal.

  ?animal a skos:Concept;
       skos:prefLabel ?name_animal.
    
  ?animal_collection a skos:Collection;
       skos:prefLabel ?name_animal_collection;
       skos:member ?animal.

  ?annotation2 oa:hasBody ?pregnancy;
        oa:hasTarget ?target2.
  ?target2 oa:hasSource ?paragraph;
      oa:hasSelector ?selector2.
  ?selector2 oa:exact ?mention_pregnancy.

  ?pregnancy skos:prefLabel ?name_pregnancy.

  FILTER (str(?name_pregnancy) = "length of pregnancy").
  FILTER (lang(?name_pregnancy) = "en")
  FILTER (str(?name_animal_collection) = "Ancient class").
  FILTER (lang(?name_animal) = "en").
}
ORDER BY ?paragraph
```

Extrait resultat:

![qc7](img/qc7.png)

![qc7_2](img/qc7_2.png)

### Quelles sont les expérimentations faites sur les animaux (contexte, description…)?

Remarque: Pas de concept expérimentations. On peut éventuellement se trouver dans le cadre d'une "utilisation de l'animal", cependant il n'y a pas de concept expriment l'utilisation pour la science ou autre. Peut être que ça rentre dans "l'utilisation médical" ou "technique" ?

```SPARQL
PREFIX oa:     <http://www.w3.org/ns/oa#>.
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>.
PREFIX schema:  <http://schema.org/> .

SELECT DISTINCT ?paragraph ?name_animal ?mention_animal ?mention_use WHERE {
?annotation1 a oa:Annotation;
              oa:hasBody ?animal;
              oa:hasTarget ?target1.
  ?target1 oa:hasSource ?paragraph;
     oa:hasSelector ?selector.
    
  ?selector oa:exact ?mention_animal.

  ?animal a skos:Concept;
       skos:prefLabel ?name_animal.
    
  ?animal_collection a skos:Collection;
       skos:prefLabel ?name_animal_collection;
       skos:member ?animal.

  ?annotation2 oa:hasBody ?use;
        oa:hasTarget ?target2.
  ?target2 oa:hasSource ?paragraph;
      oa:hasSelector ?selector2.
  ?selector2 oa:exact ?mention_use.

  ?use skos:prefLabel ?name_use.

  FILTER (str(?name_use) = "technical use").
  FILTER (lang(?name_use) = "en")
  FILTER (str(?name_animal_collection) = "Ancient class").
  FILTER (lang(?name_animal) = "en").
}
ORDER BY ?paragraph
```

Extrait resultat

![qc8](img/qc8.png)

### Quels sont les animaux typiques de l’Afrique (qui ne sont pas considérés comme des variantes d’animaux connus en Europe, telles les moutons (ici d’Afrique), les lions (ici d’Afrique, mais il y en a aussi en Europe et en Asie)

```SPARQL

```



### Quels sont les caractéristiques comportementaux des rongeurs, ou des souris ?

```SPARQL

```



### quelles sont les paires d’animaux (régulièrement associés) qui sont dans un rapport spécial d’affection (sympathie) ou de haine (antipathie)?

```SPARQL

```



### Quels sont les objets techniques réalisés avec des parties animales (peau, os, cornes…)?

```SPARQL
PREFIX oa:     <http://www.w3.org/ns/oa#>.
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>.
PREFIX schema:  <http://schema.org/> .

SELECT DISTINCT ?paragraph ?name_animal ?mention_animal ?mention_use WHERE {
?annotation1 a oa:Annotation;
              oa:hasBody ?animal;
              oa:hasTarget ?target1.
  ?target1 oa:hasSource ?paragraph;
     oa:hasSelector ?selector.
    
  ?selector oa:exact ?mention_animal.

  ?animal a skos:Concept;
       skos:prefLabel ?name_animal.
    
  ?animal_collection a skos:Collection;
       skos:prefLabel ?name_animal_collection;
       skos:member ?animal.

  ?annotation2 oa:hasBody ?use;
        oa:hasTarget ?target2.
  ?target2 oa:hasSource ?paragraph;
      oa:hasSelector ?selector2.
  ?selector2 oa:exact ?mention_use.

  ?use skos:prefLabel ?name_use.

  FILTER (str(?name_use) = "technical use").
  FILTER (lang(?name_use) = "en")
  FILTER (str(?name_animal_collection) = "Ancient class").
  FILTER (lang(?name_animal) = "en").
}
ORDER BY ?paragraph
```

## Extraire le sous-graphe de connaissance d'un paragraphe 

Exemple pour le paragraphe 195 du chapitre 8 de Pline.

```SPARQL
PREFIX oa:     <http://www.w3.org/ns/oa#>.
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>.
PREFIX schema:  <http://schema.org/> .
PREFIX graphs: <http://exemple.fr/>.
PREFIX para: <http://www.zoomathia.com/PLINE-8-annoteIPL/8/>.

construct { para:195 graphs:hasConcept ?label_concept.}  where {
  ?annotation a oa:Annotation;
              oa:hasBody ?concept;
              oa:hasTarget ?target.
  ?target oa:hasSource para:195.
  ?concept skos:prefLabel ?label_concept.
}

```

![sous_graph](img/sous_graph.png)
