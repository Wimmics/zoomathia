# Hippiatrica Berolinensia - English translation, batch 33
# global indices 2050-2085 (36 items)
#
# CORPUS-FIX NOTE (2026-09-04): the source zoo80/2g.xml had a single missing
# </p> right after this batch's last recipe (an ancient mid-word page-break
# split, "amor-" / "-ges" = amorges, olive-lees, at the 84/84.1.1 section
# boundary), which caused the *entire remainder of the book* (chapters
# 84-130, ~960 more real paragraphs) to nest inside that one <p> and collapse
# into a single giant unnumbered blob at the tail of the extracted reference
# text - invisible as separate items. Fixed by closing the dangling <p> and
# removing the now-redundant stray </p> that had been closing it at the very
# end of the file; re-ran extract_hippiatrica_berol.py, which now reports
# 3047 real paragraphs (was 2084) with items 1-2083 byte-identical to before.
# This batch's final item, previously item 2084 alone (translated as one
# unsplit sentence), is now correctly split across new items 2084/2085 at
# the "amor-"/"-ges" boundary, matching the corrected reference text.
# Translation continues from item 2086 onward in batch34+.
#
# Section: end of cauterization aftercare (best season for cauterizing) ->
# further cautery-wound salve recipes -> "On fig-warts and ant-warts
# (myrmekiai)" (Apsyrtus to Herodion of Alexandria - not to be cauterized,
# especially at the crown of the hoof; the related "sykē" heel-sore of
# donkeys and mules) -> many further ant-wart remedies (Hierocles) ->
# "On neuritic horses" (a nerve/sinew affliction with no cure once fully
# established; Apsyrtus, Hierocles) -> opening of "On wounds affecting the
# sinews" (Apsyrtus).

BATCH33 = [
"And if, on the seventh day, the scabs have not fallen off from the ointment, there is danger that something internal has ruptured, and that it has fallen into inescapable danger. The best season for cauterizing is spring and summer.",
"Another, for the same.",
"One pound of wax, two ounces of propolis, two ounces of ammoniac gum, one ounce of unwashed wool-grease, two ounces of galbanum, two ounces of frankincense-manna, four ounces of mistletoe-glue, one ounce of soda-froth, two ounces of pepper.",
"Another.",
"One pound of wax, one ounce of propolis, two ounces of ammoniac gum, one ounce of unwashed wool-grease, two ounces of galbanum, four ounces of bitumen, two ounces of opopanax, two ounces of soda, one ounce of split alum, two ounces of pepper, two ounces of mistletoe-glue, one ounce of sulfur.",
"On figs (fig-warts) and ant-warts (myrmekiai).",
"By Apsyrtus.",
"To Herodion of Alexandria, horse-doctor, greetings. As for the fig-warts, or so-called ant-warts, that arise in horses, mules, or donkeys, in whatever part of the body, but especially",
"on the extremities, one must not cauterize them, but cut them off, and scrape close with glass, and, grinding raw chalcitis in a mortar, bandage it on, and do this daily, and do not apply water, and it will become healthy. One must especially avoid cauterizing when it is located at the crown of the hoof; for such places scar over only with difficulty.",
"Apsyrtus advises against cauterizing the so-called fig-warts and ant-warts, wherever in the body they occur, but especially on the extremities; instead, cut them off and scrape close, then grind raw chalcitis and apply it, binding it on, and do this daily, not bringing water to the place, until it becomes healthy. He especially forbids cauterizing when it occurs at the crown of the hoof; for it scars over only with difficulty there.",
"It happens that, at the heel of the hind foot, right by the frog itself, a sore arises, which they call a 'sykē' (fig-sore). The horse is troubled by this, then, and goes lame and is in pain, and does not allow anyone to touch it. One must, then, treat this as quickly as possible with the cautery and other remedies. For, if it becomes chronic, in walking the hoof comes to be strained down onto the toe, and the horse becomes altogether lame. This happens to the donkey and mule, but not readily to the horse.",
"Another, against ant-warts.",
"One ounce of quicklime, one ounce of pounded litharge-scum, one pint of dripping lye, one ounce of frankincense, two ounces of lees, two ounces of",
"salt-lye, two ounces of verdigris, two ounces of vinegar.",
"Another.",
"Grind two ounces each of misy, blue vitriol, quicklime, and verdigris, and, having first cut out the wart and cauterized it, sprinkle this on. And if it is around the eye or eyelid, grind it with honey and anoint, having first removed the wart with a hair-ligature and applied small cauteries.",
"Another.",
"If ant-warts arise on the feet, take two ounces of chalcitis and one ounce of red ochre, two ounces of lees, and boil pomegranate-rind with vinegar, then also pound the pomegranate itself, and mix it in with these, and, straining it, apply it to a rag and pour it on. Use also the wound-remedy.",
"Another.",
"First cut it out, then apply honey and quicklime, and, pounding and sifting willow-bark, mix it in, and, anointing with it, you will cure it.",
"By Hierocles, for the same.",
"Having cut out the ant-warts, pour on sulfur, bitumen. Or burn dry colocynth, grind it, and sprinkle it on. Or burn the fern called 'pteris,' and pound and sift it, and do the same. Or boil goat's-beard root in water, and, grinding it, apply as a poultice. You also have other remedies against ant-warts written down among the compound preparations.",
"Another.",
"Two ounces each of soft alum, clustered cadmia, and misy, four ounces of chalcitis, two ounces of gum, enough gum-resin drippings; soak the gum in the drippings, add the rest, and, making troches, use them.",
"Another.",
"One ounce each of white quicklime, lees, dove-dung, and orpiment,",
"six ounces of chalcitis, enough gum-resin drippings; grind these and dissolve them in wine, and anoint the ant-warts, binding them with a hair or a fine sinew-thread. And when they fall off, sprinkle on this remedy once it has dried.",
"On neuritic horses (afflicted with a nerve/sinew ailment).",
"By Apsyrtus.",
"The neuritic horse suffers pain in the neck, and stretches out its head, and throws its muzzle upward. It is unable to open its mouth, and so it neither eats nor drinks. And, extending its member, it urinates little by little, and does nothing as regards its belly. It happens that, while walking, it staggers and falls onto its neck, because its internal sinews are drawn taut. Such a horse cannot live.",
"By Hierocles.",
"For those already seized by the neuritic affliction, no remedy can help at all. But it is good that the signs be recorded, so that no one, supposing the neuritic horse to have fallen into some other affliction, and being unable to cure it, should be condemned for it. The neuritic horse, then, stretches its neck taut, and extends its head, and is unable to raise its face or open its mouth, and so can neither eat nor drink. And, extending its genitals, it urinates little by little, and its belly does not move. It happens too that, while walking, it staggers and falls onto its neck, because its internal sinews are drawn extremely taut. For this reason, as I have said, a horse already seized by it could not live.",
"On wounds affecting the sinews.",
"By Apsyrtus.",
"Best for horses against wounds affecting the sinews: old olive-",
"lees, boiled down to a third - one cotyla; one cotyla of the pressed juice of boiled elm-root bark; half a cotyla of bull's gall; four staters of fine birthwort (or, if bull's gall is not available, that of a wild goat). Pour these together into a vessel and boil them in the open air. And when it is boiled, take a twig and let a drop fall onto a potsherd, and, if it sets, take it off promptly and use it.",
]
