# Hippiatrica Berolinensia - English translation, batch 4
# global indices 195-259 (65 items)
# Section: end of "Against plague" recipes -> "On the lung" (Hierocles, Tiberius,
# Eumelus, Cassius, Hippocrates) -> "On rupture of the lung" (Apsyrtus to
# Dionysius, Eumelus) -> "On peripneumonia".
#
# NOTE: a handful of source paragraphs (indices 231, 234, 236, 239, 241) are pure
# cross-manuscript apparatus/section-numbering codes (e.g. '6.4."t"'), not actual
# text of the treatise. They were not caught by the extraction script's is_apparatus()
# filter (which only matches pure digit/dot/space strings) because they contain
# stray letters/quote marks. Per the same convention already used for pure-number
# apparatus markers (silently dropped, per zoo80/1e), these are kept here as
# labelled placeholders to preserve 1:1 index alignment with the reference file,
# and must be filtered out (not written as <p>) when the final zoo80/2e.xml is
# assembled from hippiatrica_berol_structure.pkl + the translation batches.

BATCH4 = [
"Bleed the animal from all the joints, then bind them round with wild-vine, and moreover anoint the joints themselves with liquid pitch, and make it walk about more continually, its feed of course being reduced; give, however, four ounces of ground and sifted barley with wild fig. For this too contributes considerably.",
"Another.",
"Having bled the animal, and soaked barley in water or urine, mix vinegar with cow dung and cumin and mustard, and apply to the joints.",
"Another.",
"Toast and pound about an oxybaphon-measure of Alexandrian colocynth seed, sift it and mix it in fragrant white wine, and, straining it and putting it into a horn, drench through the nostrils for five days.",
"Another.",
"Plagues must be forestalled with remedies. So mix roots of all-heal and eryngo, and also fennel seed, with wheat-flour, and leaven it with hot water. In addition, mix an equal quantity of cassia, myrrh, and frankincense with the blood of a sea-turtle, and give three ounces of old wine through the nostrils. Take two ounces of this remedy, make it up to three, and administer for three days.",
"Another.",
"Five ounces of carrot, ten ounces of agaric, three ounces of cassam, three ounces of nard, three ounces of ground-pine herb, six ounces of betony, one ounce of Illyrian iris, three ounces of rush leaf, one ounce of white pepper, ten ounces of southernwood, three ounces of horehound, three ounces of sandonicum - grind all these well, and, straining them into wine, give as a drench.",
"Another, for the same purpose, by Aemilius Spanus.",
"Bleed the animal from the feet, then mix four ounces of trogline myrrh, six ounces of saffron, four grammes of centaury, one ounce of Indian spikenard, three ounces of white pepper, five spoonfuls of celery seed, one ounce of poppy, one ounce of propolis, one pint of honey, and enough soda, and make it into pieces the size of a hazelnut, and, dissolving one in a pint of lukewarm water, give it to the ailing animal.",
"Another, by Litorius of Beneventum.",
"For a horse suffering from plague, one must first draw blood from the chest, then from the legs; and if necessity presses, from the temples too. It is also good to give it varied feed, that is, barley- and wheat-flour, and also bran, and a little fodder; and besides these to prepare a draught and pour it in through the nostrils, boiling centaury and wormwood in equal weight with enough wine.",
"Another.",
"If it begins to go lame in the forelegs, draw blood from the forearms; if in the hind legs, from the thighs; if it drags its flanks and holds its nostrils open, from both temples. Then boil a seven-day-old puppy thoroughly, and, mixing in the urine of an unspoiled child and a cotyla's worth of wine, drench.",
"Another.",
"When an animal begins to go lame in the forefeet, first anoint its whole body all over with wine-and-oil, then drench it beforehand with this remedy: four ounces of bear fat, six ounces of centaury, one ounce of the herb called turnip-wort, six ounces of wild thyme, three ounces of hyssop, one ounce of germander, one ounce of fragrant wormwood, one ounce of sharp trefoil, six ounces of wild rue root, three ounces of vervain, three ounces of betony. Boil all these in honeyed wine, and give through the mouth (adding to these also six ounces of wild thyme, three ounces of hyssop, one ounce of germander).",
"On the lung.",
"By Hierocles.",
"Whenever a horse suffers pain in the lung, the affliction is a very",
"chronic one, and the horse is especially weak in spring. Signs: its body collapses, and it coughs as if it seemed to have swallowed a bone, and it brings up mucus and snores, and drinks much, and seeks more food. Its treatment, then: pound saffron, myrrh, cassia, and cinnamon, grind them together with honey, and, adding wine, drench. One must anticipate it with treatment; for if the lung is allowed to fill with pus, it dies.",
"By Tiberius, for the same.",
"Take honey and pepper and a pine-cone still holding its resin, and boil them with wine, and thus drench through the mouth for three days. Feed it especially with more fodder, and allow it to roll about, observing the signs closely. For it happens also to turn into a different disease.",
"By Eumelus, for the same.",
"The signs of lung-disease are these: the legs and veins swell, and the testicles twitch more frequently. Fever also comes on in the body, which is detected when the hand is brought near the armpit. Draw blood from this one, then, from the tendon, and, mixing it in summer with vinegar and oil, in winter with wine, anoint the whole body with it. Give this same animal a drench too, mixing one ounce each of spikenard, saffron, myrrh, camel-hay, cassia-fistula, and white pepper, then adding an equal amount of ground vetch, and, grinding and sifting all together, bind with honey and store; and from this, when needed, dissolve an obol's weight in water,",
"and pour it in through the left nostril. And before giving the drench, wipe out the mouth with wormwood, soda, honey, and vinegar-water. And if it is not helped, apply the cautery to it as well, until it discharges pus.",
"By Cassius, for the same.",
"If a horse suffers pain in the lung, it emits breath through the mouth and nostrils, and distends its ribs with the breathing, and looks more distressed, and leaves its food half-chewed in the manger, and smells foul. It is drenched with a compound such as this: grind about two beans' weight of dried bay-berries and turpentine-resin, and enough honey, in vinegar, and pour it in through the nostril. For after this it will urinate blood-tinged and purulent matter, and after that give a drench of one ounce of alum and an equal amount of soda and honey-water, then afterward with honey-water alone, and offer it good fodder.",
"By Hippocrates, for the same.",
"A horse afflicted in the lung discharges moisture through the nostrils, breathes heavily through the mouth, and has its flanks drawn in. It is drenched thus: boil the most astringent tree-nuts in one cotyla of wine, and likewise of oil, and give through the mouth, and use smooth feed, mixing vetch into the barley; or boil a pig's brain in one cotyla of wine, and, mixing in half a cotyla of oil, drench with enough of it, and likewise with the aromatic remedy; or boil a cockerel until it falls apart, and, mixing in one pint of sweet wine, drench. Also bleed it, according to",
"the animal's strength. Give also dog's-tooth grass or lucerne, and sprinkle the drinking-water with flour, so as to keep the animal's strength well-nourished - [lacuna] - if the season permits. Or pound Illyrian iris with water, eggs, and oil, and drench.",
"On rupture of the lung.",
"Apsyrtus to Dionysius Tomeus, greetings. Since you keep horses, I want you to know that if rupture of the lung occurs, the neck grows thin, and the chest likewise, and it breathes heavily and coughs and snores and expectorates thick purulent matter, and it goes lame in the forelegs. It is cured slowly, and even once cured it does not endure strenuous exertion.",
"One must treat it thus: crush vetch and soak it in water a night and a day, and, after washing it, cool it and make it into fine flour, and, sifting it with fragrant dark wine and hot water in equal parts of each, give it to drink; and if it is unwilling to drink, hold its tongue and drench it. And let it not walk about much, but stand covered in a warm place. Warm the strained liquid of the crushed vetch and give it to drink, and mix soda into the rest of the drinking-water while it is warm. Suitable for this too is a raw mixture of fine barley-flour sprinkled with soda and given to eat.",
"By the same treatment one whose windpipe is strained is also cured, though it takes longer. Both these must be treated by blowing in oil and wine, and the whole rubbing-down must be done against the grain of the hair. It is also beneficial for one with ruptured lung to drench with",
"warmed sharp vinegar, or human urine mixed with twenty drachms' weight of melted pork fat, but not a woman's urine, when it is in its natural state.",
'[apparatus reference marker "6.4"]',
"By Eumelus, for the same.",
"In some cases it happens that the lungs rupture, either from being forced to run very far, or from continual coughing. Such animals, then, some suppose to have swallowed bones, because they take food and drink more greedily, and discharge pus. Drench it beforehand, then, thus: grind and mix equal weights of saffron, cassia, nard, myrrh, and cinnamon with a cotyla of dark wine, and give it. If these are not to be found, mix ground vetch with wine and hot water, and give enough of it.",
'[apparatus reference marker "6.5.t1"]',
"A preliminary drench for those with rupture of the lung",
'[apparatus reference marker "6.5.t2"]',
"who are enduring it, or who fall into lung-disease also from running.",
"Take one ounce each of spikenard, saffron, myrrh, costus, camel-hay, cassia-fistula, and white pepper, and enough vetch-flour, grind and sift all, bind with honey, and, when needed, dissolve it and pour it in through the left nostril. But before doing this, rinse the horse's mouth with wormwood, soda, honey, and vinegar-water.",
'[apparatus reference marker "7.t.1"]',
"On peripneumonia, that is, broken wind.",
'[apparatus reference marker "7.1.t"]',
"Cure of peripneumonia.",
"Take six ounces of sulfur, grind six ounces of myrrh, and, pouring on about half a cotyla of wine and about a cyathus of oil, pour it into the nostrils, and give the rest of the usual care. But if",
"it is not healed by these, cauterize it beneath the armpits toward the belly, holding the iron shallow so as not to reach the depth. And if pus flows, stop, and treat the burn with pitch, wax, and oil.",
"Slaughter a suckling piglet, with the ailing animal already standing ready close by, and immediately pour the seething blood into its throat.",
"From wheat leaven, from which bread would otherwise be made, make little balls with boiled must, and give to the animal for as many days as needed, until it recovers. And when giving it to drink, remember to mix flour into the water.",
"Peel Gallic garlic and pound it in a mortar, mix it with old lard, and make pastilles; then mix honey, boiled must, and eggs, and, dipping the pastilles in this mixture, give for three days.",
"Soak six ounces of ground bean-meal in three ounces of boiled must, and grind well in a mortar thirty-one peppercorns, and, mixing in one pound of goat's tallow, grind them together again, and drench through a horn for three days.",
"Following the chapter on coughing, I have written also on lung-disease; for it is especially from this strain that the lung ruptures. Rupture often occurs, too, from running or from jumping, when it clears a fence or a ditch. This often happens in the course of hunting-chases; and sometimes also",
"a horse or other beast of burden, having become very thirsty, gulps down its drink all at once with much heaving breath, and ruptures the lung, for this reason: the lung has the thinnest membrane of all the internal organs, and the whole of it is filled with its own proper breath.",
"The fluid within it, being frothy from its continual motion, is exceedingly thin. It has no sinew, flesh, or muscle in it at all, but is the softest of organs. For nature has propped it up against the ever-throbbing heart in such a way that it might never, by coming up against something resistant and being struck, become a cause of death to the animal. Such an organ, then, undergoes rupture under only slight strain. And when the rupture in the lung is at its outset, the affliction follows a course that must be treated. But when it goes unnoticed, it becomes suppurative and is called 'empyic.' One must, then, treat the fresh rupture one way, and the suppurative condition another.",
"We shall, then, set forth the signs and treatments of both, since we shall also point out to you one way in which lung-disease may be man-made, having ourselves witnessed it and treated it and kept it in memory. A soldier, thinking himself a lover of fine things, used to overfill his own horse with salt once a day, in this manner: having a hollow horn, he filled it with salt, and, raising the horse's head and opening its mouth, he poured the salt into its throat all at once, and hung the head up again, so that the salt would settle in. For this is what he told me when I asked him.",
"By doing this he made the horse consumptive, though it was a very well-bred and excellent animal. For the salt, being thinning in nature, all at once",
"poured in through the horn, when the horse's head was tilted back from the hanging, ran down into the lung, and the most acrid discharges, dripping down, ate deep into the membrane of the lung, and, having made an ulcer, wrapped the animal in consumption, and it grew thinner every day. Having recognized and understood, then, what had befallen it, and that it came from nothing other than the salt, I gave the weeping and lamenting man a horse, by no means well-bred, but healthy. And I took his horse, and, having treated it, had it again",
"as a competitor, so that it pleased the king and was kept by him.",
"I shall, then, set forth the diagnosis and the treatment. This is the diagnosis of ruptured lung: it breathes shallowly, and shows the region along the ribs with its mouth, groans in a stifled way, being in pain while breathing, is afraid to cough, and coughs as though it had swallowed a bone. One must, then, leave it in quiet, and bleed it at the projection by the hip-socket. For it grows suddenly thin in the rupture of the lung.",
"One must, then, drench for seven days with goat's milk together with barley-gruel juice, or better still if of oats. And if it is not the season for milk, boil a very fat pig's trotter, with goat-tallow along with it, and drench with the broths for seven days. Let it drink water made milk-like in consistency, in winter from wheat-flour, in summer barley-gruel; for thus the rupture will knit together.",
"But if it comes to be suppurative, these are its signs: it takes much water, it eats more than usual, and",
"the horse, coughing gently, often brings up pus, and sometimes even scabs themselves. You will drench such a horse with a drench such as this: purslane is a wild garden vegetable. Drench its juice with rose-oil for three or seven days, adding tragacanth soaked in sweet Cretan wine and goat's milk - or, if there is no milk, barley-gruel juice or of oats - especially when the suppurative discharge smells very foul through the nostrils. You will finish its treatment over seven days, drenching it with this: pound two ounces of costus and four ounces of cassia, sift through a fine sieve, and, adding raisins, drench with wine. Let it abstain from exercise, and take only a few walks, led by a handler.",
]
