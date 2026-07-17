--
-- PostgreSQL database dump
--

\restrict ZDEGGY2I7E7vJAhTGpdzWCN0etqJhZsb0tGMg0HA8j35D9JSydRmDc0gh4kuuvN

-- Dumped from database version 17.6
-- Dumped by pg_dump version 18.4 (Ubuntu 18.4-1.pgdg25.10+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA public;


--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- Name: rls_auto_enable(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.rls_auto_enable() RETURNS event_trigger
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'pg_catalog'
    AS $$
DECLARE
  cmd record;
BEGIN
  FOR cmd IN
    SELECT *
    FROM pg_event_trigger_ddl_commands()
    WHERE command_tag IN ('CREATE TABLE', 'CREATE TABLE AS', 'SELECT INTO')
      AND object_type IN ('table','partitioned table')
  LOOP
     IF cmd.schema_name IS NOT NULL AND cmd.schema_name IN ('public') AND cmd.schema_name NOT IN ('pg_catalog','information_schema') AND cmd.schema_name NOT LIKE 'pg_toast%' AND cmd.schema_name NOT LIKE 'pg_temp%' THEN
      BEGIN
        EXECUTE format('alter table if exists %s enable row level security', cmd.object_identity);
        RAISE LOG 'rls_auto_enable: enabled RLS on %', cmd.object_identity;
      EXCEPTION
        WHEN OTHERS THEN
          RAISE LOG 'rls_auto_enable: failed to enable RLS on %', cmd.object_identity;
      END;
     ELSE
        RAISE LOG 'rls_auto_enable: skip % (either system schema or not in enforced list: %.)', cmd.object_identity, cmd.schema_name;
     END IF;
  END LOOP;
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: auteurs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auteurs (
    id integer NOT NULL,
    nom_canonique text NOT NULL,
    identifiant text NOT NULL,
    periode text
);


--
-- Name: auteurs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.auteurs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: auteurs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.auteurs_id_seq OWNED BY public.auteurs.id;


--
-- Name: fichiers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fichiers (
    id integer NOT NULL,
    oeuvre_id integer NOT NULL,
    nom_fichier text NOT NULL,
    format text,
    langue text,
    statut text,
    source text
);


--
-- Name: fichiers_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.fichiers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: fichiers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.fichiers_id_seq OWNED BY public.fichiers.id;


--
-- Name: oeuvres; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.oeuvres (
    id integer NOT NULL,
    auteur_id integer NOT NULL,
    titre_original text,
    titre_francais text,
    titre_anglais text,
    langue_originale text,
    dans_classeur_lea text DEFAULT 'Non'::text,
    original_sur_git text DEFAULT 'Non'::text,
    traduction_anglaise_sur_git text DEFAULT 'Non'::text,
    traduction_francaise_sur_git text DEFAULT 'Non'::text,
    traduction_italienne_sur_git text DEFAULT 'Non'::text,
    note text
);


--
-- Name: oeuvres_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.oeuvres_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: oeuvres_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.oeuvres_id_seq OWNED BY public.oeuvres.id;


--
-- Name: auteurs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auteurs ALTER COLUMN id SET DEFAULT nextval('public.auteurs_id_seq'::regclass);


--
-- Name: fichiers id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fichiers ALTER COLUMN id SET DEFAULT nextval('public.fichiers_id_seq'::regclass);


--
-- Name: oeuvres id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.oeuvres ALTER COLUMN id SET DEFAULT nextval('public.oeuvres_id_seq'::regclass);


--
-- Data for Name: auteurs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auteurs (id, nom_canonique, identifiant, periode) FROM stdin;
1	AELIANUS SOPHISTES	tlg0545	antique (800 av. J.-C. - 300 ap. J.-C.)
2	ALBERTUS MAGNUS	viaf88125532	medieval (apres 700 ap. J.-C.)
3	AMBROSIUS	stoa0022	tardo-antique (300 - 700 ap. J.-C.)
4	ANTIGONUS	tlg0568	antique (800 av. J.-C. - 300 ap. J.-C.)
5	APOLLONIUS	tlg0569	antique (800 av. J.-C. - 300 ap. J.-C.)
6	APSYRTOS	wikidataQ456578	tardo-antique (300 - 700 ap. J.-C.)
7	ARISTOTELES	tlg0086	antique (800 av. J.-C. - 300 ap. J.-C.)
8	ARRIANUS	tlg0074	antique (800 av. J.-C. - 300 ap. J.-C.)
9	ARTEMIDORUS	tlg0553	antique (800 av. J.-C. - 300 ap. J.-C.)
10	ATHENAEUS	tlg0008	antique (800 av. J.-C. - 300 ap. J.-C.)
11	AVIANUS	stoa004	tardo-antique (300 - 700 ap. J.-C.)
12	BABRIUS	tlg0614	antique (800 av. J.-C. - 300 ap. J.-C.)
13	BASILIUS	tlg2040	tardo-antique (300 - 700 ap. J.-C.)
14	CASSIANUS BASSUS	tlg4080	tardo-antique (300 - 700 ap. J.-C.)
15	COLUMELLA	phi0845	antique (800 av. J.-C. - 300 ap. J.-C.)
16	DIODORE	tlg0060	antique (800 av. J.-C. - 300 ap. J.-C.)
17	ESOPUS	tlg0096	antique (800 av. J.-C. - 300 ap. J.-C.)
18	EUCHERIUS	stoa0117	tardo-antique (300 - 700 ap. J.-C.)
19	GALENUS	tlg0057	antique (800 av. J.-C. - 300 ap. J.-C.)
20	GRATTIUS	phi0887	antique (800 av. J.-C. - 300 ap. J.-C.)
21	HERODOTUS	tlg0016	antique (800 av. J.-C. - 300 ap. J.-C.)
22	HESIODUS	tlg0020	antique (800 av. J.-C. - 300 ap. J.-C.)
23	HIEROCLES	mirabile222866	tardo-antique (300 - 700 ap. J.-C.)
24	HIPPOCRATES	tlg0627	antique (800 av. J.-C. - 300 ap. J.-C.)
25	ISIDORUS HISPALENSIS	stoa0159	tardo-antique (300 - 700 ap. J.-C.)
26	LUCIANUS SAMOSATENSIS	tlg0062	antique (800 av. J.-C. - 300 ap. J.-C.)
27	NEMESIANUS, MARCUS AURELIUS OLYMPUS	stoa0209	antique (800 av. J.-C. - 300 ap. J.-C.)
28	NICANDER COLOPHONIUS	tlg0022	antique (800 av. J.-C. - 300 ap. J.-C.)
29	OPPIANUS-1	tlg0023	antique (800 av. J.-C. - 300 ap. J.-C.)
30	OPPIANUS-2	tlg0024	antique (800 av. J.-C. - 300 ap. J.-C.)
31	OVIDIUS	stoa0216	antique (800 av. J.-C. - 300 ap. J.-C.)
32	PHAEDRUS	phi0975	antique (800 av. J.-C. - 300 ap. J.-C.)
42	PLATO	tlg0059	antique (800 av. J.-C. - 300 ap. J.-C.)
43	PLINIUS MAJOR	phi0978	antique (800 av. J.-C. - 300 ap. J.-C.)
44	PLUTARCHUS	tlg0007	antique (800 av. J.-C. - 300 ap. J.-C.)
45	PORPHYRIUS	tlg2034	antique (800 av. J.-C. - 300 ap. J.-C.)
46	PS-DIOSCORIDE	tlg1118	antique (800 av. J.-C. - 300 ap. J.-C.)
47	DENYS (pseudo)	tlg0084	tardo-antique (300 - 700 ap. J.-C.)
48	SEMONIDES AMORGINUS	tlg0260	antique (800 av. J.-C. - 300 ap. J.-C.)
49	STRABO	tlg0099	antique (800 av. J.-C. - 300 ap. J.-C.)
50	STRATO LAMPSACENUS	tlg1696	antique (800 av. J.-C. - 300 ap. J.-C.)
51	THEOMNESTOS	wikidataQ679536	tardo-antique (300 - 700 ap. J.-C.)
52	THEOPHRASTUS	tlg0093	antique (800 av. J.-C. - 300 ap. J.-C.)
54	TIMOTHEUS GAZAEUS	tlg2449	tardo-antique (300 - 700 ap. J.-C.)
55	VARRO	phi0684	antique (800 av. J.-C. - 300 ap. J.-C.)
57	XENOPHON	tlg0032	antique (800 av. J.-C. - 300 ap. J.-C.)
58	PETRUS GALLECUS	viaf79204298	medieval (apres 700 ap. J.-C.)
60	CONRAD DE HALBERSTADT	viaf67263708	medieval (apres 700 ap. J.-C.)
61	ENGELBERTUS ADMONTENSIS	viaf36891982	medieval (apres 700 ap. J.-C.)
62	IOHANNES DE CUBA	viaf49269039	medieval (apres 700 ap. J.-C.)
63	IOHANNES EGIDIUS ZAMORENSIS	viaf18034405	medieval (apres 700 ap. J.-C.)
64	IOHANNES DE SANCTO GEMINIANO	mirabile20323	medieval (apres 700 ap. J.-C.)
65	MARCUS DE URBE VETERI	pas didentifiant auteur trouve	medieval (apres 700 ap. J.-C.)
66	THOMAS CANTIMPRATENSIS	viaf100174374	medieval (apres 700 ap. J.-C.)
68	VINCENTIUS BELVACENSIS	viaf105133420	medieval (apres 700 ap. J.-C.)
69	PHILO ALEXANDRINUS	tlg0018	antique (800 av. J.-C. - 300 ap. J.-C.)
70	PHILOUMENOS	tlg0671	antique (800 av. J.-C. - 300 ap. J.-C.)
71	PHYSIOLOGUS	tlg2654	tardo-antique (300 - 700 ap. J.-C.)
75	PHYSIOLOGUS LATINUS B	digiliblt.DLT000410	tardo-antique (300 - 700 ap. J.-C.)
77	PHYSIOLOGUS LATINUS Y	digiliblt.DLT000533	tardo-antique (300 - 700 ap. J.-C.)
79	HILDEBERTUS CENOMANENSIS	viaf282035032	medieval (apres 700 ap. J.-C.)
80	HIPPIATRICA	tlg0738	tardo-antique (300 - 700 ap. J.-C.)
81	EUTECNIUS	tlg0752	tardo-antique (Ve siecle ap. J.-C.)
82	ANONYME	anon_halieutica_oppien	tardo-antique (paraphraste des Halieutiques d'Oppien)
83	PHYSIOLOGUS LATINUS D	pas didentifiant auteur trouve D	\N
84	PHYSIOLOGUS LATINUS X	pas didentifiant auteur trouve X	\N
\.


--
-- Data for Name: fichiers; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.fichiers (id, oeuvre_id, nom_fichier, format, langue, statut, source) FROM stdin;
1	25	tlg0614.tlg001.1st1K-grc1.xml	TEI P5	grec	Disponible	First1KGreek
2	70	2_eng_p5.xml	TEI P5	anglais	Disponible	CLTK greek_text_perseus
3	70	2_gk_p5.xml	TEI P5	grec	Disponible	CLTK greek_text_perseus
4	47	phi0975.phi001.perseus-eng1_p5.xml	TEI P5	anglais	Obsolete - remplacee par phaedrus_fables_eng_tei.xml	Perseus Digital Library
5	47	phi0975.phi001.perseus-lat1-p5.xml	TEI P5	latin	Disponible	Perseus Digital Library
6	77	varro.rr1.txt	TEI P5	latin	Disponible	The Latin Library
7	77	varro.rr2.txt	TEI P5	latin	Disponible	The Latin Library
8	77	varro.rr3.txt	TEI P5	latin	Disponible	The Latin Library
9	34	tlg0016.tlg001.perseus-grc2.xml	TEI P5	grec	Disponible	Perseus Digital Library
10	35	tlg0020.tlg002.perseus-grc2.xml	TEI P5	grec	Disponible	Perseus Digital Library
11	83	tlg0022.tlg002.1st1K-grc1.xml	TEI P5	grec	Disponible	First1KGreek
12	43	tlg0022.tlg001.1st1K-grc1.xml	TEI P5	grec	Disponible	First1KGreek
13	71	tlg0099.tlg001.perseus-grc1_p5.xml	TEI P5	grec	Disponible	Perseus Digital Library
20	130	ovid.fasti1.txt	TEI P5	latin	Disponible	The Latin Library
21	130	ovid.fasti2.txt	TEI P5	latin	Disponible	The Latin Library
22	130	ovid.fasti3.txt	TEI P5	latin	Disponible	The Latin Library
23	130	ovid.fasti4.txt	TEI P5	latin	Disponible	The Latin Library
24	130	ovid.fasti5.txt	TEI P5	latin	Disponible	The Latin Library
25	130	ovid.fasti6.txt	TEI P5	latin	Disponible	The Latin Library
48	129	ovid.met1.txt	TEI P5	latin	Disponible	The Latin Library
49	129	ovid.met10.txt	TEI P5	latin	Disponible	The Latin Library
50	129	ovid.met11.txt	TEI P5	latin	Disponible	The Latin Library
51	129	ovid.met12.txt	TEI P5	latin	Disponible	The Latin Library
52	129	ovid.met13.txt	TEI P5	latin	Disponible	The Latin Library
53	129	ovid.met14.txt	TEI P5	latin	Disponible	The Latin Library
54	129	ovid.met15.txt	TEI P5	latin	Disponible	The Latin Library
55	129	ovid.met2.txt	TEI P5	latin	Disponible	The Latin Library
56	129	ovid.met3.txt	TEI P5	latin	Disponible	The Latin Library
57	129	ovid.met4.txt	TEI P5	latin	Disponible	The Latin Library
58	129	ovid.met5.txt	TEI P5	latin	Disponible	The Latin Library
59	129	ovid.met6.txt	TEI P5	latin	Disponible	The Latin Library
60	129	ovid.met7.txt	TEI P5	latin	Disponible	The Latin Library
61	129	ovid.met8.txt	TEI P5	latin	Disponible	The Latin Library
62	129	ovid.met9.txt	TEI P5	latin	Disponible	The Latin Library
73	61	Perseus_text_1999.02.0138_p5.xml	TEI P5	latin	Disponible	Perseus Digital Library
74	31	eucherius.txt	TEI P5	latin	Disponible	The Latin Library
75	1	tlg0545.tlg001.perseus-grc1_p5.xml	TEI P5	grec	Disponible	Perseus Digital Library
76	33	grattius.txt	TEI P5	latin	Disponible	The Latin Library
77	67	tlg2034.tlg003.1st1K-grc1.xml	TEI P5	grec	Disponible	First1KGreek
78	44	tlg0023.tlg001.perseus-grc1_p5.xml	TEI P5	grec	Disponible	Perseus Digital Library
79	24	avianus.txt	TEI P5	latin	Disponible	The Latin Library
80	41	nemesianus1.txt	TEI P5	latin	Disponible	The Latin Library
81	41	nemesianus2.txt	TEI P5	latin	Disponible	The Latin Library
82	41	nemesianus3.txt	TEI P5	latin	Disponible	The Latin Library
83	41	nemesianus4.txt	TEI P5	latin	Disponible	The Latin Library
84	79	tlg0032.tlg014.perseus-grc1.xml	TEI P5	grec	Disponible	Perseus Digital Library
85	79	tlg0032.tlg003.perseus-grc1.xml	TEI P5	grec	Disponible	Perseus Digital Library
86	79	tlg0032.tlg013.perseus-grc1.xml	TEI P5	grec	Disponible	Perseus Digital Library
87	79	tlg0032.tlg012.perseus-grc1.xml	TEI P5	grec	Disponible	Perseus Digital Library
88	22	tlg0553.tlg001.1st1K-grc1.xml	TEI P5	grec	Disponible	First1KGreek
89	37	tlg0627.tlg005.perseus-grc1.xml	TEI P5	grec	Disponible	Perseus Digital Library
90	60	tlg0059.tlg031.perseus-eng2.xml	TEI P5	anglais	Disponible	Perseus Digital Library
91	60	tlg0059.tlg031.perseus-grc2.xml	TEI P5	grec	Disponible	Perseus Digital Library
92	32	tlg0057.tlg010.perseus-grc1_p5.xml	TEI P5	grec	Disponible	Perseus Digital Library
96	38	12.txt	TEI P5	latin	Disponible	The Latin Library
117	72	STRATO_LAMPSACENUS_tei.xml	TEI P5	grec	Disponible	DFHG Project
122	74	tlg0093.tlg010x03.1st1K-grc1.xml	TEI P5	grec	Disponible	First1KGreek
123	29	tlg0060.tlg001.perseus-grc1_p5.xml	TEI P5	grec	Disponible	Perseus Digital Library
124	29	tlg0060.tlg001.perseus-grc2_p5.xml	TEI P5	grec	Disponible	Perseus Digital Library
125	29	tlg0060.tlg001.perseus-grc3_p5.xml	TEI P5	grec	Disponible	Perseus Digital Library
126	30	tlg0096.tlg002.First1K-grc1.xml	TEI P5	grec	Disponible	First1KGreek
131	39	tlg0062.tlg027.perseus-grc1_p5.xml	TEI P5	grec	Disponible	Perseus Digital Library
132	39	tlg0062.tlg027.perseus-grc2.xml	TEI P5	grec	Disponible	Perseus Digital Library
133	39	tlg0062.tlg054.perseus-grc1_p5.xml	TEI P5	grec	Disponible	Perseus Digital Library
134	45	tlg0024.tlg001.perseus-grc1_p5.xml	TEI P5	grec	Disponible	Perseus Digital Library
135	23	tlg0008.tlg001.perseus-grc4_annotated.xml	TEI P5	grec	Disponible	Perseus Digital Library
136	28	phi0845.phi002.perseus-lat1_p5.xml	TEI P5	latin	Disponible	Perseus Digital Library
137	28	phi0845.phi002.perseus-lat2_p5.xml	TEI P5	latin	Disponible	Perseus Digital Library
141	62	tlg0007.tlg098.perseus-grc1_p5.xml	TEI P5	grec	Disponible	Perseus Digital Library
143	7	tlg0086.tlg018.1st1K-grc1.xml	TEI P5	grec	Disponible	First1KGreek
144	7	tlg0086.tlg014.1st1K-grc1.xml	TEI P5	grec	Disponible	First1KGreek
145	7	tlg0086.tlg029.perseus-grc1_p5.xml	TEI P5	grec	Disponible	Perseus Digital Library
146	7	tlg0086.tlg037.1st1K-grc1.xml	TEI P5	grec	Disponible	First1KGreek
147	7	tlg0086.tlg030.1st1K-grc1.xml	TEI P5	grec	Disponible	First1KGreek
148	7	tlg0086.tlg041.1st1K-grc1.xml	TEI P5	grec	Disponible	First1KGreek
149	21	tlg0074.tlg003.perseus-grc2.xml	TEI P5	grec	Disponible	Perseus Digital Library
150	69			grec	Introuvable	Introuvable
151	4			grec	Introuvable	Introuvable
152	26			grec	Introuvable	Introuvable
153	47	phaedrus_fables_eng_tei.xml	TEI P5	anglais	Disponible	Gutenberg #25512 (Riley + Smart), via LacusCurtius/zoomathia_encoder.py
154	22	artemidorus_dreams_eng_tei.xml	TEI P5	anglais	Disponible	Internet Archive 1755 (Robert Wood), via zoomathia_encoder.py
155	80	tlg0032.tlg012.perseus-grc1.xml	TEI P5	grec	Disponible	Perseus
156	80	xenophon_cavalry_commander_eng.xml	TEI P5	anglais	Disponible	Perseus (Marchant), via Xenophon Minor Works
157	82	tlg0032.tlg014.perseus-grc1.xml	TEI P5	grec	Disponible	Perseus
158	82	xenophon_hunting_eng.xml	TEI P5	anglais	Disponible	Perseus (Marchant), via Xenophon Minor Works
159	122	xenophon_agesilaus_eng.xml	TEI P5	anglais	Disponible	Perseus (Marchant), via Xenophon Minor Works
160	123	xenophon_constitution_lacedaemonians_eng.xml	TEI P5	anglais	Disponible	Perseus (Marchant), via Xenophon Minor Works
161	124	xenophon_hiero_eng.xml	TEI P5	anglais	Disponible	Perseus (Marchant), via Xenophon Minor Works
162	125	xenophon_ways_and_means_eng.xml	TEI P5	anglais	Disponible	Perseus (Marchant), via Xenophon Minor Works
163	66	plutarch_de_esu_carnium_eng_tei.xml	TEI P5	anglais	Disponible	LacusCurtius (Goodwin, Loeb vol. XII, 1957)
164	122	tlg0032.tlg009.perseus-grc2.xml	TEI P5	grec	Disponible	PerseusDL/canonical-greekLit
165	123	tlg0032.tlg010.perseus-grc2.xml	TEI P5	grec	Disponible	PerseusDL/canonical-greekLit
166	124	tlg0032.tlg008.perseus-grc2.xml	TEI P5	grec	Disponible	PerseusDL/canonical-greekLit
167	125	tlg0032.tlg011.perseus-grc2.xml	TEI P5	grec	Disponible	PerseusDL/canonical-greekLit
168	62	plutarch_de_amore_prolis_eng.xml	TEI P5	anglais	Disponible	Perseus (Goodwin)
169	64	tlg0007.tlg129.perseus-grc1_p5.xml	TEI P5	grec	Disponible	Perseus
170	64	plutarch_de_sollertia_animalium_eng.xml	TEI P5	anglais	Disponible	Perseus (Goodwin)
171	65	tlg0007.tlg130.perseus-grc2.xml	TEI P5	grec	Disponible	Perseus
172	65	plutarch_bruta_animalia_eng.xml	TEI P5	anglais	Disponible	Perseus (Goodwin)
173	63	tlg0007.tlg125.perseus-grc1_p5.xml	TEI P5	grec	Disponible	Perseus
174	66	tlg0007.tlg131.perseus-grc2.xml	TEI P5	grec	Disponible	Perseus
175	66	tlg0007.tlg132.perseus-grc1_p5.xml	TEI P5	grec	Disponible	Perseus
176	19	tlg0086.tlg014.1st1K-grc1.xml	TEI P5	grec	Disponible	First1KGreek/Perseus
177	20	tlg0086.tlg029.perseus-grc1_p5.xml	TEI P5	grec	Disponible	First1KGreek/Perseus
178	16	tlg0086.tlg030.1st1K-grc1.xml	TEI P5	grec	Disponible	First1KGreek/Perseus
179	18	tlg0086.tlg037.1st1K-grc1.xml	TEI P5	grec	Disponible	First1KGreek/Perseus
180	14	tlg0086.tlg041.1st1K-grc1.xml	TEI P5	grec	Disponible	First1KGreek/Perseus
181	15	tlg0086.tlg018.1st1K-grc1.xml	TEI P5	grec	Disponible	First1KGreek/Perseus
182	81	tlg0032.tlg013.perseus-grc1.xml	TEI P5	grec	Disponible	Perseus
183	81	xenophon_horsemanship_eng_p5.xml	TEI P5	anglais	Disponible	Perseus
184	4	Antigonus_Mirabilia_tlg568.001.xml	TEI P5	grec	Disponible	Corpus Zoomathia
185	69	Dionysius_Ixeutica_tlg0084.003.xml	TEI P5	grec	Disponible	Corpus Zoomathia
186	115	Basilius_Hexaemeron_tlg2040.001.xml	TEI P5	grec	Disponible	Corpus Zoomathia
187	26	Basilius Homiliae in hexaemeron VII-VIII-IX_tei.xml	TEI P5	grec	Disponible	Corpus Zoomathia
188	121	TLG0738-Additamenta Londinensia ad hippiatrica Cantabrigiensia_tei.xml	TEI P5	grec	Disponible	Corpus Zoomathia
189	118	TLG0738-Hippiatrica Cantabrigiensia_tei.xml	TEI P5	grec	Disponible	Corpus Zoomathia
190	40	tlg0062.tlg054.perseus-grc1.xml	TEI P5	grec	Disponible	Perseus
191	48	tlg0018.tlg029.opp-grc1.xml	TEI P5	grec	Disponible	Perseus
192	49	tlg0018.tlg009.opp-grc1.xml	TEI P5	grec	Disponible	Perseus
193	50	tlg0018.tlg010.opp-grc1.xml	TEI P5	grec	Disponible	Perseus
194	51	tlg0018.tlg019.opp-grc1.xml	TEI P5	grec	Disponible	Perseus
195	9	tlg0086.tlg021.1st1K-grc1.xml	TEI P5	grec	Disponible	First1KGreek/Perseus
196	8	tlg0086.tlg015.1st1K-grc1.xml	TEI P5	grec	Disponible	First1KGreek/Perseus
197	10	tlg0086.tlg020.1st1K-grc1.xml	TEI P5	grec	Disponible	First1KGreek/Perseus
198	12	tlg0086.tlg032.1st1K-grc1.xml	TEI P5	grec	Disponible	First1KGreek/Perseus
199	13	tlg0086.tlg027.1st1K-grc1.xml	TEI P5	grec	Disponible	First1KGreek/Perseus
200	11	tlg0086.tlg036.1st1K-grc1.xml	TEI P5	grec	Disponible	First1KGreek/Perseus
201	76	Timotheus De animalibus_tei.xml	TEI P5	grec	Disponible	Encodage manuel Zoomathia (Mistral)
202	119	TLG0738-Hippiatrica Berolinensia_tei.xml	TEI P5	grec	Disponible	Encodage manuel Zoomathia (Mistral) - repare (recover lxml)
203	127	TLG0752-Eutecnius Paraphrasis in Oppiani cynegetica (fort. auctore Eutecnio)_tei.xml	TEI P5	grec	Disponible	Encodage complet (structure + balisage semantique) - Mistral
204	128	TLG0752-Paraphrasis in Oppiani halieutica (fort. auctore Eutecnio)_tei.xml	TEI P5	grec	Disponible	Encodage complet (structure + balisage semantique) - Mistral
205	120	TLG0738-Hippiatrica Parisina_tei.xml	TEI P5	grec	Disponible	Encodage complet (structure + balisage semantique) - Mistral
206	69	dionysius_ixeuticon_tei.xml	TEI P5	grec	Disponible	Encodage complet (structure + balisage semantique) - Mistral, source TLG fournie par A. Zucker
207	76	fragmenta_timothee_tei.xml	TEI P5	grec	Disponible	Encodage complet (structure + balisage semantique) - Mistral, fragments Teubner 1927
208	76	timothee_extraits_sylloge_tei.xml	TEI P5	grec	Disponible	Encodage complet (structure + balisage semantique) - Mistral, extraits Sylloge byzantine
209	28	columella_1745_eng_tei.xml	TEI P5	anglais	Disponible	Traduction anglaise 1745 (domaine public), encodage complet Mistral, repare via lxml recover
210	76	bodenheimer_1949_traduction_eng_tei.xml	TEI P5	anglais	EN ATTENTE - droits auteur a clarifier avec Zucker (Bodenheimer mort 1959, domaine public 2029-2030)	Bodenheimer and Rabinowitz 1949 - OCR ameliore, PAS PUBLIER sans autorisation
211	85	171_Hildebertus-Cenomanensis_Physiologus_tei.xml	TEI P5	latin	Disponible	Edition Migne 1854 (Patrologia Latina vol. 171) via Corpus Corporum - encodage complet Mistral
212	84	Liber_de_animalibus_tei.xml	TEI P5	latin	EN ATTENTE - droits auteur a clarifier (edition critique SISMEL 2000, Martinez Gazquez)	Corpus Corporum - PAS PUBLIER sans autorisation SISMEL
213	89	hortus_animalibus_tei.xml	TEI P5	latin	Disponible	Incunable Mainz 1497, section De Animalibus - domaine public, encodage complet, XML repare via lxml recover
214	52	philumenus_tei.xml	TEI P5	grec	Disponible	Edition Wellmann 1908 (Corpus Medicorum Graecorum XI,1) - domaine public, encodage complet, XML repare via lxml recover
215	19	aristote_ha_eng_tei.xml	TEI P5	anglais	Disponible	Traduction D'Arcy Wentworth Thompson (Oxford 1910), domaine public, via topostext.org - encodage complet Mistral
216	34	herodotus_eng_tei.xml	TEI P5	anglais	Disponible	Traduction G.C. Macaulay 1904, domaine public, via Project Gutenberg - encodage complet Mistral
217	74	theophrastus_eng_tei.xml	TEI P5	anglais	Disponible	Traduction Arthur Hort 1926 (Loeb), domaine public, via topostext.org - encodage complet Mistral
218	32	galen_eng_complet_tei.xml	TEI P5	anglais	Disponible	Traduction A.J. Brock 1916, domaine public CC BY-SA, via Perseus Digital Library - encodage complet Mistral
219	61	pline_animaux_eng_tei.xml	TEI P5	anglais	Disponible	Traduction Bostock/Riley 1855, domaine public, Livres VIII-XI (animaux), via Project Gutenberg - encodage complet Mistral
220	21	arrian_cynegetique_tei.xml	TEI P5	anglais	Disponible	Traduction William Dansey 1831, domaine public, via Project Gutenberg (ebook 78013) - encodage complet Mistral
221	25	babrius_complet_tei.xml	TEI P5	anglais	Disponible	Traduction James Davies 1860, domaine public, via elfinspell.com - encodage complet Mistral
222	26	basil_complet_tei.xml	TEI P5	anglais	Disponible	Traduction Blomfield Jackson 1895 (NPNF), domaine public, via New Advent - encodage complet Mistral
223	30	esopus_eng_tei.xml	TEI P5	anglais	Disponible	Traduction V.S. Vernon Jones 1912, domaine public, via Project Gutenberg - encodage complet Mistral
224	44	oppian_hal_eng_complet_tei.xml	TEI P5	anglais	Disponible	Traduction A.W. Mair 1928 (Loeb), domaine public, via LacusCurtius - encodage complet Mistral
225	45	oppian_cyn_eng_complet_tei.xml	TEI P5	anglais	Disponible	Traduction A.W. Mair 1928 (Loeb), domaine public, via LacusCurtius - encodage complet Mistral
226	48	philo_complet_v2_tei.xml	TEI P5	anglais	Disponible	Traduction C.D. Yonge (XIXe siecle), domaine public, via earlychristianwritings.com - encodage complet Mistral, fichier partage entre les 4 traites
227	49	philo_complet_v2_tei.xml	TEI P5	anglais	Disponible	Traduction C.D. Yonge (XIXe siecle), domaine public, via earlychristianwritings.com - encodage complet Mistral, fichier partage entre les 4 traites
228	50	philo_complet_v2_tei.xml	TEI P5	anglais	Disponible	Traduction C.D. Yonge (XIXe siecle), domaine public, via earlychristianwritings.com - encodage complet Mistral, fichier partage entre les 4 traites
229	51	philo_complet_v2_tei.xml	TEI P5	anglais	Disponible	Traduction C.D. Yonge (XIXe siecle), domaine public, via earlychristianwritings.com - encodage complet Mistral, fichier partage entre les 4 traites
230	43	nicander_complet_eng_tei.xml	TEI P5	anglais	EN ATTENTE - droits auteur a clarifier (Gow and Scholfield 1953, Cambridge University Press)	attalus.org - PAS PUBLIER sans autorisation
231	83	nicander_complet_eng_tei.xml	TEI P5	anglais	EN ATTENTE - droits auteur a clarifier (Gow and Scholfield 1953, Cambridge University Press)	attalus.org - PAS PUBLIER sans autorisation
232	71	strabo_complet_eng_tei.xml	TEI P5	anglais	Disponible	Traduction Hamilton/Falconer 1854, domaine public, via Project Gutenberg - encodage complet Mistral
233	23	athenaeus_complet_eng_tei.xml	TEI P5	anglais	Disponible	Traduction C.D. Yonge 1854, domaine public, via Project Gutenberg - encodage complet Mistral
234	3	ambrose_hexaemeron_tei.xml	TEI P5	latin	Disponible	Migne Patrologia Latina vol. 14 (1844), domaine public, via Internet Archive - encodage complet Mistral, XML repare via lxml recover
235	77	varro_complet_eng_tei.xml	TEI P5	anglais	Disponible	Traduction Hooper/Ash 1934, domaine public confirme par LacusCurtius, via penelope.uchicago.edu - encodage complet Mistral
236	67	porphyry_abstinence_tei.xml	TEI P5	anglais	Disponible	Traduction Thomas Taylor 1823, domaine public, via Project Gutenberg - encodage complet Mistral
237	89	noble_lyfe_oxford_tei.xml	TEI P5	anglais	Disponible	Traduction Laurence Andrew 1521/1527, domaine public CC0, via Oxford Text Archive/Text Creation Partnership - encodage complet Mistral
238	29	diodore_livre3_tei.xml	TEI P5	anglais	Disponible	Traduction C.H. Oldfather 1933-1967 (domaine public, traducteur mort 1954), Livre III chap. 35-48 sur les animaux sauvages, via LacusCurtius - encodage complet Mistral
239	40	lucian_of_sacrifice_tei.xml	TEI P5	anglais	Disponible	Traduction Fowler and Fowler 1905, domaine public (avant 1923), via Internet Archive/sacred-texts.com - encodage complet Mistral
240	29	diodore_supplement_tei.xml	TEI P5	anglais	Disponible	Traduction C.H. Oldfather (domaine public), Livre I ch. 30-41 (hippopotame) et Livre III ch. 1-34 (serpents, chasse aux elephants), via LacusCurtius - encodage complet Mistral
241	116	Pseudo-Dioscorides Alexipharmaca (De venenis eorumque praecautione et medicatione)_tei.xml	TEI P5	grec	Disponible	Texte fourni par A. Zucker (source TLG) - encodage complet Mistral
242	117	pseudo_dioscorides_theriaca_tei.xml	TEI P5	grec	Disponible	Texte fourni par A. Zucker (source TLG) - encodage complet Mistral, XML repare via lxml recover
243	46	Publius_Ovidius_Halieutica_tei.xml	TEI P5	latin	Disponible	Texte fourni par A. Zucker (IntraText Library) - encodage complet Mistral
244	27	geoponica_arnaud_tei.xml	TEI P5	grec	Disponible	Texte fourni par A. Zucker - encodage complet Mistral, XML repare via lxml recover
245	33	grattius_haupt_tei.xml	TEI P5	latin	Disponible	Edition Haupt 1838 (domaine public), via Google Books - encodage complet Mistral
246	41	nemesianus_haupt_tei.xml	TEI P5	latin	Disponible	Edition Haupt 1838 (domaine public), via Google Books - encodage complet Mistral
247	33	grattius_eng_tei.xml	TEI P5	anglais	Disponible	Traduction Loeb 1935, domaine public, via LacusCurtius - encodage complet Mistral
248	41	nemesianus_eng_tei.xml	TEI P5	anglais	Disponible	Traduction Loeb 1935, domaine public, via LacusCurtius - encodage complet Mistral
249	42	nemesianus_aucupio_eng_tei.xml	TEI P5	anglais	Disponible	Traduction Loeb 1934/1935 (Minor Latin Poets), domaine public (droits expires 1962-63, non renouveles), via LacusCurtius - encodage complet Mistral
250	42	nemesianus_aucupio_lat_tei.xml	TEI P5	latin	Disponible	Loeb 1934/35 (Minor Latin Poets), domaine public, via LacusCurtius - encodage complet Mistral
251	2	albertus_borgnet_texte_tei.xml	TEI P5	latin	Disponible - Livres XIII-XXVI	Edition Auguste Borgnet 1891 (domaine public), via document fourni par A. Zucker - encodage complet Mistral
252	2	albertus_stadler_texte_tei.xml	TEI P5	latin	Disponible - Livres I-XII	Edition Hermann Stadler 1916 (domaine public, Biodiversity Heritage Library confirme), via Internet Archive - encodage complet Mistral
253	87	Conrad de Halberstadt - Liber similitudinum naturalium - 4.xml	TEI P5	latin	Disponible	Edition I. Ventura 2003, transformation XML-TEI E. Kuhry (IRHT-CNRS) pour Zoomathia - balisage semantique complete Mistral
254	90	Iohannes Egidius Zamorensis - Historia naturalis.xml	TEI P5	latin	Disponible	Transformation XML-TEI IRHT-CNRS pour Zoomathia - balisage semantique complete Mistral
255	89	Iohannes de Cuba - Hortus sanitatis, Liber de piscibus.xml	TEI P5	latin	Disponible - Liber de piscibus (section poissons)	Transformation XML-TEI IRHT-CNRS pour Zoomathia - balisage semantique complete Mistral
256	91	Iohannes de Sancto Geminiano - Summa de exemplis ac similitudinibus rerum.xml	TEI P5	latin	Disponible	Transformation XML-TEI IRHT-CNRS pour Zoomathia - balisage semantique complete Mistral
257	94	Thomas Cantimpratensis - Liber de natura rerum, version Thomas III.xml	TEI P5	latin	Disponible	Transformation XML-TEI IRHT-CNRS pour Zoomathia - balisage semantique complete Mistral
258	88	Engelbertus Admontensis - Tractatus de naturis animalium.xml	TEI P5	latin	Disponible	Transformation XML-TEI IRHT-CNRS pour Zoomathia - balisage semantique complete Mistral
259	75	Thomas Cantimpratensis - Liber de natura rerum, version Thomas I II.xml	TEI P5	latin	Disponible	Transformation XML-TEI IRHT-CNRS pour Zoomathia - balisage semantique complete Mistral
260	92	Marcus de Urbe Veteri - Tractatus septiformis de moralitatibus rerum.xml	TEI P5	latin	Disponible	Transformation XML-TEI IRHT-CNRS pour Zoomathia - balisage semantique complete Mistral
261	78	Vincentius Belvacensis - Speculum naturale.xml	TEI P5	latin	Disponible	Transformation XML-TEI IRHT-CNRS pour Zoomathia - balisage semantique complete Mistral
262	57	physiologus_latin_b_complet.xml	TEI P5	latin	Disponible	Version B (Carmody 1939), transformation IRHT-CNRS (E. Kuhry) pour Zoomathia - balisage semantique complete Mistral
263	59	physiologus_latin_y_complet.xml	TEI P5	latin	Disponible	Version Y (Carmody), transformation IRHT-CNRS (E. Kuhry) pour Zoomathia - balisage semantique complete Mistral
264	131	physiologus_latin_d_complet.xml	TEI P5	latin	Disponible	Version D (Wilhelm), transformation IRHT-CNRS (E. Kuhry) pour Zoomathia - balisage semantique complete Mistral
265	132	physiologus_latin_x_complet.xml	TEI P5	latin	Disponible	Version X (Gebert), transformation IRHT-CNRS (E. Kuhry) pour Zoomathia - balisage semantique complete Mistral
\.


--
-- Data for Name: oeuvres; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.oeuvres (id, auteur_id, titre_original, titre_francais, titre_anglais, langue_originale, dans_classeur_lea, original_sur_git, traduction_anglaise_sur_git, traduction_francaise_sur_git, traduction_italienne_sur_git, note) FROM stdin;
1	1	Περὶ ζῴων ἠδιότητος	De la nature des animaux	On the characteristics of Animals	grec	Oui	Oui	Oui	Non	Non	\N
2	2	De animalibus	De animalibus	De animalibus	latin	Oui	Non	Non	Non	Non	\N
3	3	Hexaemeron	Hexaméron	Hexaemeron	latin	Oui	Non	Non	Non	Non	\N
4	4	Ἱστοριῶν παραδόξων συναγωγή	Recueil d'histoires extraordinaires	Collection of Marvellous Tales	grec	Oui	Oui	Non	Non	Non	\N
5	5	à renseigner	à renseigner	à renseigner	latin	Oui	Non	Non	Non	Non	\N
6	6	Hippiatrica	Hippiatrique	Hippiatrica	latin	Oui	Non	Non	Non	Non	Texte non publié séparément. Extraits conservés dans les Hippiatrica (tlg0738)
7	7	Περὶ ζᾥων γενέσεως	De la génération des animaux	Generation of animals	grec	Oui	Oui	Oui	Non	Non	\N
8	7	Περὶ πορείας ζῴων	Marche des animaux	On the progression of animals	grec	Oui	Oui	Oui	Non	Non	\N
9	7	Περὶ ζῴων κινήσεως	Mouvement des animaux	On the movement of animals	grec	Oui	Oui	Oui	Non	Non	\N
10	7	Περὶ μακροβιότητος καὶ βραχυβιότητος	De la longévité et de la brièveté de la vie	On Length and Shortness of Life	grec	Oui	Oui	Oui	Non	Non	\N
11	7	Προβλήματα	Problèmes	Problems	grec	Oui	Oui	Non	Non	Non	\N
12	7	Φυσιογνωμονικά	Physiognomonica	Physiognomonica	grec	Oui	Oui	Non	Non	Non	\N
13	7	Περὶ θαυμασίων ἀκουσμάτων	De mirabilibus auscultationibus	On marvellous things heard	grec	Oui	Oui	Non	Non	Non	\N
14	7	Περὶ αἰσθήσεως καὶ αἰσθητῶν	De sensu et sensibilibus	Sense and Sensibilia	grec	Oui	Oui	Oui	Non	Non	\N
15	7	Περὶ Ζωῆς καὶ Θανάτου	De la vie et de la mort	De vita et morte	grec	Oui	Oui	Oui	Non	Non	\N
16	7	Περὶ ζῴων μορίων	Les parties des animaux	On the parts of animals	grec	Oui	Oui	Oui	Non	Non	\N
17	7	Περὶ νεότητος καὶ γήρως, καὶ ζωῆς καὶ θανάτου, καὶ ἀναπνοῆς	De juventute et senectute	On Youth, Old Age, Life and Death, and Respiration	grec	Oui	Oui	Oui	Non	Non	\N
18	7	Περὶ ἀναπνοῆς	De la respiration	On respiration	grec	Oui	Oui	Oui	Non	Non	\N
19	7	περὶ ζῴων ἱστορίας	Histoire des animaux	Historia Animalium	grec	Oui	Oui	Oui	Oui	Non	\N
20	7	Οἰκονομικά	Economics	Economics	grec	Oui	Oui	Oui	Non	Non	\N
21	8	Κυνηγετικά	On Dogs	On Dogs	grec	Oui	Oui	Oui	Non	Non	\N
22	9	Ὀνειροκριτικά	L'interprétation des songes	The Interpretation of Dreams	grec	Oui	Oui	Oui	Non	Non	VERIFICATION STRUCTURELLE (07/2026) : traduction anglaise ajoutee (Robert Wood, 1755, Internet Archive, domaine public). Texte source nettoye (index alphabetique de fin retire, caracteres 's long' corriges). Encodage TEI valide sans erreur XML (corrige suite a l'amelioration de zoomathia_encoder.py -- validation et nouvelle tentative automatique par morceau -- puis 2 corrections manuelles ciblees sur fragments OCR illisibles). Verification de contenu manuelle standard recommandee, comme pour tout encodage automatique. VERIFICATION DE CONFORMITE (07/2026, apres structuration complete du corpus) : ecart structurel avec l'original confirme (402 div/19 l/1412 lb cote grec vs 185 div/0 l cote traduction). Contrairement a Semonide/Phedre, l'oeuvre est majoritairement en PROSE (traite d'interpretation des reves), pas un poeme. L'ecart vient de 19 vers de citations poetiques (Homere, Iliade, citees par Artemidore pour illustrer une interpretation) que l'original balise en <l> mais que la traduction de 1755 rend en prose continue, fondue dans le texte -- ecart mineur et localise (19 vers sur un texte de 402 divisions), pas une non-conformite generale.
23	10	Δειπνοσοφισταί	Les déipnosophistes	The deipnosophists	grec	Oui	Oui	Oui	Non	Non	\N
24	11	Fabulae	Fables	Fables	latin	Oui	Non	Non	Non	Non	\N
25	12	Μυθίαμβοι Αἰσώπειοι	Fables	Fables	grec	Oui	Oui	Oui	Non	Non	\N
26	13	Ὁμιλίαι εἰς τὴν Ἑξαήμερον	Homélies sur l'Hexaéméron	Homilies on the Hexaemeron	grec	Oui	Oui	Oui	Non	Non	\N
27	14	Γεωπονικά	Géoponiques	Geoponica	latin	Oui	Non	Non	Non	Non	\N
28	15	De re rustica	On agriculture	On agriculture	latin	Oui	Non	Non	Non	Non	\N
29	16	Βιβλιοθήκη ἱστορική	Bibliothèque historique	Historical library	grec	Oui	Oui	Oui	Non	Non	\N
30	17	Μῦθοι	Fables	Fables	grec	Oui	Oui	Oui	Non	Non	\N
31	18	Formulae spiritalis intellegentiae	Formulae spiritalis intellegentiae	Formulae spiritalis intellegentiae	latin	Oui	Non	Non	Non	Non	\N
32	19	Περὶ φυσικῶν δυνάμεων	Sur les facultés naturelles	On the naturals faculties	grec	Oui	Oui	Oui	Non	Non	\N
33	20	Cynegetica	Cynegetica	Cynegetica	latin	Oui	Non	Non	Non	Non	\N
34	21	Ἱστορία	Histoires	History	grec	Oui	Oui	Oui	Oui	Oui	\N
35	22	Ἔργα καὶ ἡμέραι	Les travaux et les jours	Works and Days	grec	Oui	Oui	Oui	Non	Non	\N
36	23	Hippiatrica	Hippiatrique	Hippiatrica	latin	Oui	Non	Non	Non	Non	\N
37	24	Περὶ διαίτης ὀξέω	Du régime des maladies aiguës	On Regim	grec	Oui	Oui	Oui	Oui	Non	\N
38	25	Etymologiae	Étymologies	Etymologies	latin	Oui	Non	Non	Non	Non	\N
39	26	Dipsades	Sur les dipsades	Dipsads	grec	Oui	Oui	Oui	Oui	Non	\N
40	26	De sacrificiis	Sur les sacrifices	On sacrifices	grec	Oui	Oui	Oui	Oui	Non	\N
41	27	Cynegetica	Les cynégétiques	Cynegetica	latin	Oui	Non	Non	Non	Non	\N
42	27	De aucupio	Sur la capture des oiseaux	On Bird-catching	latin	Oui	Non	Non	Non	Non	\N
43	28	Θηριακά	Les thériaques	On Venomous Animals	grec	Oui	Oui	Oui	Non	Non	\N
44	29	῾Αλιευτικά	Halieutiques	Halieutica	grec	Oui	Oui	Oui	Non	Non	\N
45	30	Κυνηγετικά	Cynégétique	Cynegetica	grec	Oui	Oui	Oui	Non	Non	\N
46	31	Halieutica	Halieutiques	Halieutica	latin	Oui	Non	Non	Non	Non	\N
92	65	Tractatus septiformis	Tractatus septiformis	Tractatus septiformis	latin	Non	Oui	Non	Non	Non	\N
94	66	Liber de natura rerum (version III)	Liber de natura rerum (version III)	Liber de natura rerum (version III)	latin	Non	Oui	Non	Non	Non	\N
108	46	à renseigner	à renseigner	à renseigner	grec	Non	Non	Non	Non	Non	\N
47	32	Fabulae	Fables	Fables	latin	Oui	Non	Oui	Non	Non	VERIFICATION STRUCTURELLE (07/2026, mise a jour) : l'ancienne traduction (Smart, Perseus perseus-eng1) etait incomplete (32/132 fables). Remplacee par phaedrus_fables_eng_tei.xml (Riley + Smart combines, Gutenberg #25512), couverture complete. Traduction en PROSE litterale, non alignee vers-a-vers avec l'original latin (1943 <l> cote latin, quasi aucun cote traduction) -- meme situation que Semonide (oeuvre id=70), alignement automatique impossible.
48	69	Περὶ ἀφθαρσίας κόσμου	Sur l'éternité du monde	On the eternity of the world	grec	Oui	Oui	Oui	Non	Non	\N
49	69	περί γεωργίας	Sur l’agriculture	On husbandry	grec	Oui	Oui	Oui	Non	Non	\N
50	69	Περι Φυτουργιας Νωε Το Δευτερον	Sur l’oeuvre de Noé comme planteur	Concerning Noah's Work as a Planter	grec	Oui	Oui	Oui	Non	Non	\N
51	69	Περὶ τοῦ θεοπέμπτους εἴναι τοὺς ὀνείρους	Des songes	On dreams	grec	Oui	Oui	Oui	Non	Non	\N
52	70	De venenatis animalibus eorumque remediis	Sur les animaux venimeux et leurs remèdes	On Venomous Animals and their Remedies	grec	Oui	Oui	Non	Non	Non	\N
53	71	Physiologus	Physiologus (redaction I)	Physiologus	grec	Oui	Oui	Non	Non	Non	\N
54	71	Physiologus	Physiologus (redaction II, byzantine)	Physiologus	grec	Oui	Oui	Non	Non	Non	\N
55	71	Physiologus	Physiologus (redaction III, pseudo-basilienne)	Physiologus	grec	Oui	Oui	Non	Non	Non	\N
57	75	Physiologus	Physiologus	Physiologus	latin	Oui	Oui	Non	Non	Non	\N
59	77	Physiologus	Physiologus	Physiologus	latin	Oui	Oui	Non	Non	Non	\N
60	42	Τίμαιος	Timée	Timaeus	grec	Oui	Oui	Oui	Oui	Oui	\N
61	43	Naturalis Historia	Histoire naturelle	Natural history	latin	Oui	Non	Non	Non	Non	\N
62	44	Περί της εις τα έγγονα φιλοστοργίας	De l’amour de la progéniture	On affection for offsprings	grec	Oui	Oui	Oui	Non	Non	\N
63	44	Αίτια φυσικά	Questions naturelles	Causes of natural phenomena	grec	Oui	Oui	Oui	Oui	Non	\N
64	44	Πότερα τῶν ζῴων φρονιμώτερα τὰ χερσαῖα ἢ τὰ ἔνυδρα	L'intelligence des animaux	Whether Land or Sea Animals Are Cleverer	grec	Oui	Oui	Oui	Non	Non	\N
65	44	Περὶ τοῦ τὰ ἄλογα λόγῳ χρῆσθαι	Que les bêtes ont l'usage de la raison	Beasts are rationals	grec	Oui	Oui	Oui	Oui	Non	\N
66	44	Περὶ σαρκροφαγίας	Sur la consommation de viande	The eating of flesh	grec	Oui	Oui	Oui	Oui	Non	 | DOUBLON FUSIONNE (07/2026) : AJOUT 07/2026 : traduction anglaise 'De Esu Carnium I et II' (Goodwin, Loeb Classical Library vol. XII, 1957, domaine public, via LacusCurtius). AUCUN TEXTE GREC ORIGINAL retrouve dans le corpus actuel (code Perseus attendu : tlg0007.tlg131, absent). A rechercher (Perseus/First1KGreek) pour permettre la verification structurelle. CORRECTION (07/2026) : originaux grecs retrouves et rattaches (tlg131=Livre I, tlg132=Livre II, precedemment mal attache a l'oeuvre 62 par erreur d'import anterieure). VERIFICATION DETAILLEE (07/2026) : originaux grecs tlg131+tlg132 combines = 15 div / 21 p au total ; traduction anglaise (encodage automatique) = 37 div / 211 p -- facteur ~10x sur les paragraphes. Pas une erreur de contenu, mais un ecart de granularite structurelle (l'IA a fragmente le texte en beaucoup plus de paragraphes que l'edition critique grecque). Non resolu -- necessiterait un reencodage avec des instructions de granularite plus larges, ou une restructuration manuelle du fichier traduit pour aligner le decoupage sur l'original.
67	45	Περὶ ἀποχῆς τῶν ἐμψύχων	Sur l'abstinence de la chair des animaux	On Abstinence from Animal Food	grec	Oui	Oui	Oui	Non	Non	\N
68	46	à renseigner	à renseigner	à renseigner	latin	Oui	Non	Non	Non	Non	\N
69	47	Ἰξευτικά	Ixeuticon	Paraphrases on Bird-catching	grec	Oui	Oui	Non	Non	Non	\N
70	48	Iamboi	Iambes	Iambs	grec	Oui	Non	Non	Non	Non	VERIFICATION STRUCTURELLE (07/2026) : traduction anglaise (Edmonds, Loeb 1931) en prose continue, non alignee vers-a-vers avec l'original grec (1174 <l> cote grec, 0 cote traduction). Alignement automatique impossible sans nouvelle traduction versifiee. Traductions versifiees partielles identifiees : Diotima (fr. 7, 'sur les femmes', 118 vers) et A.Z. Foreman (fr. 1, 'sur le destin') -- non integrees, verifier droits de reutilisation avant integration.
71	49	Γεωγραφικά	Géographie	Geography	grec	Oui	Oui	Oui	Oui	Non	\N
72	50	Περὶ εὑρημάτων	Sur les inventions	On Inventions	grec	Oui	Non	Non	Non	Non	\N
73	51	Hippiatrica	Hippiatrica	Hippiatrica	latin	Oui	Non	Non	Non	Non	Texte non publié séparément. Extraits conservés dans les Hippiatrica (tlg0738)
74	52	De Signis Tempestatum	On wheather signs	On wheather signs	grec	Oui	Non	Non	Non	Non	\N
75	66	Liber de natura rerum	Livre de la nature des choses	Book on the Nature of Things	latin	Oui	Non	Non	Non	Non	\N
76	54	Περὶ ζώων	Sur les animaux	On animals	grec	Oui	Non	Non	Non	Non	\N
77	55	De re rustica	L’économie rurale	On agriculture	latin	Oui	Non	Non	Non	Non	\N
78	68	Speculum naturale	Speculum naturale	Speculum naturale	latin	Oui	Oui	Non	Non	Non	\N
79	57	Οἰκονομικός	Économique	Economics	grec	Oui	Oui	Oui	Oui	Non	\N
80	57	Ἱππαρχικός	Le commandant de la cavalerie	The Cavalry commander	grec	Oui	Oui	Oui	Oui	Non	\N
81	57	περὶ Ἱππικῆς	De l’art équestre	On the Art of Horsemanship	grec	Oui	Oui	Oui	Non	Non	\N
82	57	Κυνηγετικά	L’art de la chasse	On Hunting	grec	Oui	Oui	Oui	Oui	Non	\N
83	28	Αλεξιφάρμακα	Les Alexipharmaques	Alexipharmaca	grec	Oui	Oui	Oui	Non	Non	\N
84	58	Liber de animalibus	Livre des animaux	Book of Animals	latin	Oui	Oui	Non	Non	Non	\N
85	79	Physiologus Theobaldi	Physiologus métrique	Metrical Physiologus	latin	Oui	Oui	Non	Non	Non	\N
86	24	—	Du régime des maladies aiguës (spuria)	On Regim (spurious)	grec	Oui	Oui	Oui	Oui	Non	\N
87	60	Liber similitudinum naturalium	Liber similitudinum naturalium	Liber similitudinum naturalium	latin	Non	Oui	Non	Non	Non	\N
88	61	Tractatus de naturis animalium	Tractatus de naturis animalium	Tractatus de naturis animalium	latin	Non	Oui	Non	Non	Non	\N
89	62	Hortus sanitatis	Hortus sanitatis	Hortus sanitatis	latin	Non	Oui	Non	Non	Non	\N
90	63	Historia naturalis	Historia naturalis	Historia naturalis	latin	Non	Oui	Non	Non	Non	\N
91	64	Summa de exemplis	Summa de exemplis	Summa de exemplis	latin	Non	Oui	Non	Non	Non	\N
109	51	Hippiatrica	Hippiatrica	Hippiatrica	grec	Non	Non	Non	Non	Non	Texte non publié séparément. Extraits conservés dans les Hippiatrica (tlg0738)
115	13	Homiliae in Hexaemeron	Homelies sur l'Hexaemeron	Homilies on the Hexaemeron	grec	Non	Oui	Oui	Non	Non	\N
116	46	Alexipharmaca	Alexipharmaques	Alexipharmaca	grec	Non	Oui	Non	Non	Non	\N
117	46	Theriaca	Thériaques	Theriaca	grec	Non	Oui	Non	Non	Non	\N
118	80	Hippiatrica Cantabrigiensia	Hippiatrica Cantabrigiensia	Hippiatrica Cantabrigiensia	grec	Non	Oui	Non	Non	Non	\N
119	80	Hippiatrica Berolinensia	Hippiatrica Berolinensia	Hippiatrica Berolinensia	grec	Non	Oui	Non	Non	Non	\N
120	80	Hippiatrica Parisina	Hippiatrica Parisina	Hippiatrica Parisina	grec	Non	Oui	Non	Non	Non	\N
121	80	Additamenta Londinensia	Additamenta Londinensia	Additamenta Londinensia	grec	Non	Oui	Non	Non	Non	\N
122	57	Ἀγησίλαος	Agésilas	Agesilaus	grec	Non	Non	Oui	Non	Non	AJOUT 07/2026 : traduction anglaise extraite du fichier groupe 'Xenophon English Minor Works.xml' (Perseus, trad. Marchant), convertie de milestones a plat vers une structure div/section/p. AUCUN TEXTE GREC ORIGINAL retrouve dans le corpus actuel -- verification structurelle impossible tant que l'original n'est pas ajoute. A rechercher (Perseus/First1KGreek). MISE A JOUR (07/2026) : original grec retrouve sur PerseusDL/canonical-greekLit (code tlg009) et rattache. Verification de conformite structurelle a faire.
123	57	Λακεδαιμονίων Πολιτεία	Constitution des Lacédémoniens	Constitution of the Lacedaemonians	grec	Non	Non	Oui	Non	Non	AJOUT 07/2026 : traduction anglaise extraite du fichier groupe 'Xenophon English Minor Works.xml' (Perseus, trad. Marchant), convertie de milestones a plat vers une structure div/section/p. AUCUN TEXTE GREC ORIGINAL retrouve dans le corpus actuel -- verification structurelle impossible tant que l'original n'est pas ajoute. A rechercher (Perseus/First1KGreek). MISE A JOUR (07/2026) : original grec retrouve sur PerseusDL/canonical-greekLit (code tlg010) et rattache. Verification de conformite structurelle a faire.
124	57	Ἱέρων	Hiéron	Hiero	grec	Non	Non	Oui	Non	Non	AJOUT 07/2026 : traduction anglaise extraite du fichier groupe 'Xenophon English Minor Works.xml' (Perseus, trad. Marchant), convertie de milestones a plat vers une structure div/section/p. AUCUN TEXTE GREC ORIGINAL retrouve dans le corpus actuel -- verification structurelle impossible tant que l'original n'est pas ajoute. A rechercher (Perseus/First1KGreek). MISE A JOUR (07/2026) : original grec retrouve sur PerseusDL/canonical-greekLit (code tlg008) et rattache. Verification de conformite structurelle a faire.
125	57	Πόροι	Revenus	Ways and Means	grec	Non	Non	Oui	Non	Non	AJOUT 07/2026 : traduction anglaise extraite du fichier groupe 'Xenophon English Minor Works.xml' (Perseus, trad. Marchant), convertie de milestones a plat vers une structure div/section/p. AUCUN TEXTE GREC ORIGINAL retrouve dans le corpus actuel -- verification structurelle impossible tant que l'original n'est pas ajoute. A rechercher (Perseus/First1KGreek). MISE A JOUR (07/2026) : original grec retrouve sur PerseusDL/canonical-greekLit (code tlg011) et rattache. Verification de conformite structurelle a faire.
127	81	Paraphrasis in Oppiani Cynegetica	Paraphrase des Cynegetiques d'Oppien	Paraphrase of Oppian's Cynegetica	grec	Non	Non	Non	Non	Non	\N
128	82	Paraphrasis in Oppiani Halieutica	Paraphrase des Halieutiques d'Oppien	Paraphrase of Oppian's Halieutica	grec	Non	Non	Non	Non	Non	\N
129	31	Metamorphoses	Metamorphoses	Metamorphoses	latin	Non	Non	Non	Non	Non	\N
130	31	Fasti	Fastes	Fasti	latin	Non	Non	Non	Non	Non	\N
131	83	Physiologus	\N	\N	\N	Non	Non	Non	Non	Non	\N
132	84	Physiologus	\N	\N	\N	Non	Non	Non	Non	Non	\N
\.


--
-- Name: auteurs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auteurs_id_seq', 84, true);


--
-- Name: fichiers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.fichiers_id_seq', 265, true);


--
-- Name: oeuvres_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.oeuvres_id_seq', 132, true);


--
-- Name: auteurs auteurs_identifiant_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auteurs
    ADD CONSTRAINT auteurs_identifiant_key UNIQUE (identifiant);


--
-- Name: auteurs auteurs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auteurs
    ADD CONSTRAINT auteurs_pkey PRIMARY KEY (id);


--
-- Name: fichiers fichiers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fichiers
    ADD CONSTRAINT fichiers_pkey PRIMARY KEY (id);


--
-- Name: oeuvres oeuvres_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.oeuvres
    ADD CONSTRAINT oeuvres_pkey PRIMARY KEY (id);


--
-- Name: fichiers fichiers_oeuvre_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fichiers
    ADD CONSTRAINT fichiers_oeuvre_id_fkey FOREIGN KEY (oeuvre_id) REFERENCES public.oeuvres(id);


--
-- Name: oeuvres oeuvres_auteur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.oeuvres
    ADD CONSTRAINT oeuvres_auteur_id_fkey FOREIGN KEY (auteur_id) REFERENCES public.auteurs(id);


--
-- Name: auteurs; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.auteurs ENABLE ROW LEVEL SECURITY;

--
-- Name: fichiers; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.fichiers ENABLE ROW LEVEL SECURITY;

--
-- Name: oeuvres; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.oeuvres ENABLE ROW LEVEL SECURITY;

--
-- PostgreSQL database dump complete
--

\unrestrict ZDEGGY2I7E7vJAhTGpdzWCN0etqJhZsb0tGMg0HA8j35D9JSydRmDc0gh4kuuvN

