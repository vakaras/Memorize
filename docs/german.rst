======
German
======

Conjugation
===========

`memorize.holders.german.conjugation.Conjugator`:py:class: can be used
to conjugate german words::

    >>> from memorize.holders.german.conjugation import Conjugator
    ... words = [(u'machen', {}),
    ...          (u'antworten', {}),
    ...          (u'biegen', {
    ...              'present': {'es': 'biegt'},
    ...              'past': {'es': 'bog'},
    ...              }),
    ...          (u'rasen', {}),
    ...          (u'ändern', {}),
    ...          (u'bügeln', {}),
    ...          (u'wohnen', {}),
    ...          (u'schicken', {}),
    ...          (u'glauben', {}),
    ...          (u'bauen', {}),
    ...          (u'kosten', {}),
    ...          (u'eröffnen', {}),
    ...          (u'arbeiten', {}),
    ...          (u'sein', {
    ...              'present': {
    ...                  'ich': 'bin',
    ...                  'du': 'bist',
    ...                  'es': 'ist',
    ...                  'wir': 'sind',
    ...                  'ihr': 'seid',
    ...                  },
    ...              'past': {'es': 'war'},
    ...              }),
    ...          (u'fahren', {
    ...              'present': {'es': 'fährt'},
    ...              'past': {'es': 'fuhr'},
    ...              }),
    ...          (u'stehen', {
    ...              'present': {},
    ...              'past': {'es': 'stand'},
    ...              }),
    ...          (u'nennen', {
    ...              'present': {},
    ...              'past': {'es': 'nannte'},
    ...              }),
    ...          (u'können', {
    ...              'present': {'es': 'kann', 'ich': 'kann'},
    ...              'past': {'es': 'konnte'},
    ...              }),
    ...          (u'haben', {
    ...              'present': {'es': 'hat'},
    ...              'past': {'es': 'hatte'},
    ...              }),
    ...          ]
    ... for word, conjugation_data in words:
    ...     conjugator = Conjugator(word, conjugation_data)
    ...     print u'\n{0.infinitive} ({0.stem}, {1}, {0.infinitive_ending}):'.format(
    ...         conjugator, conjugator.is_kranton())
    ...     for pronoun, value in list(conjugator.present) + list(conjugator.past):
    ...         print pronoun, value

    machen (mach, False, en):
    ich mache
    du machst
    es macht
    wir machen
    ihr macht
    sie machen
    ich machte
    du machtest
    es machte
    wir machten
    ihr machtet
    sie machten

    antworten (antwort, True, en):
    ich antworte
    du antwortest
    es antwortet
    wir antworten
    ihr antwortet
    sie antworten
    ich antwortete
    du antwortetest
    es antwortete
    wir antworteten
    ihr antwortetet
    sie antworteten

    biegen (bieg, False, en):
    ich biege
    du biegst
    es biegt
    wir biegen
    ihr biegt
    sie biegen
    ich bog
    du bogst
    es bog
    wir bogen
    ihr bogt
    sie bogen

    rasen (ras, False, en):
    ich rase
    du rast
    es rast
    wir rasen
    ihr rast
    sie rasen
    ich raste
    du rastest
    es raste
    wir rasten
    ihr rastet
    sie rasten

    ändern (änder, False, n):
    ich ändere
    du änderst
    es ändert
    wir ändern
    ihr ändert
    sie ändern
    ich änderte
    du ändertest
    es änderte
    wir änderten
    ihr ändertet
    sie änderten

    bügeln (bügel, False, n):
    ich bügle
    du bügelst
    es bügelt
    wir bügeln
    ihr bügelt
    sie bügeln
    ich bügelte
    du bügeltest
    es bügelte
    wir bügelten
    ihr bügeltet
    sie bügelten

    wohnen (wohn, False, en):
    ich wohne
    du wohnst
    es wohnt
    wir wohnen
    ihr wohnt
    sie wohnen
    ich wohnte
    du wohntest
    es wohnte
    wir wohnten
    ihr wohntet
    sie wohnten

    schicken (schick, False, en):
    ich schicke
    du schickst
    es schickt
    wir schicken
    ihr schickt
    sie schicken
    ich schickte
    du schicktest
    es schickte
    wir schickten
    ihr schicktet
    sie schickten

    glauben (glaub, False, en):
    ich glaube
    du glaubst
    es glaubt
    wir glauben
    ihr glaubt
    sie glauben
    ich glaubte
    du glaubtest
    es glaubte
    wir glaubten
    ihr glaubtet
    sie glaubten

    bauen (bau, False, en):
    ich baue
    du baust
    es baut
    wir bauen
    ihr baut
    sie bauen
    ich baute
    du bautest
    es baute
    wir bauten
    ihr bautet
    sie bauten

    kosten (kost, True, en):
    ich koste
    du kostest
    es kostet
    wir kosten
    ihr kostet
    sie kosten
    ich kostete
    du kostetest
    es kostete
    wir kosteten
    ihr kostetet
    sie kosteten

    eröffnen (eröffn, True, en):
    ich eröffne
    du eröffnest
    es eröffnet
    wir eröffnen
    ihr eröffnet
    sie eröffnen
    ich eröffnete
    du eröffnetest
    es eröffnete
    wir eröffneten
    ihr eröffnetet
    sie eröffneten

    arbeiten (arbeit, True, en):
    ich arbeite
    du arbeitest
    es arbeitet
    wir arbeiten
    ihr arbeitet
    sie arbeiten
    ich arbeitete
    du arbeitetest
    es arbeitete
    wir arbeiteten
    ihr arbeitetet
    sie arbeiteten

    sein (sei, False, n):
    ich bin
    du bist
    es ist
    wir sind
    ihr seid
    sie sind
    ich war
    du warst
    es war
    wir waren
    ihr wart
    sie waren

    fahren (fahr, False, en):
    ich fahre
    du fährst
    es fährt
    wir fahren
    ihr fahrt
    sie fahren
    ich fuhr
    du fuhrst
    es fuhr
    wir fuhren
    ihr fuhrt
    sie fuhren

    stehen (steh, False, en):
    ich stehe
    du stehst
    es steht
    wir stehen
    ihr steht
    sie stehen
    ich stand
    du standest
    es stand
    wir standen
    ihr standet
    sie standen

    nennen (nenn, False, en):
    ich nenne
    du nennst
    es nennt
    wir nennen
    ihr nennt
    sie nennen
    ich nannte
    du nanntest
    es nannte
    wir nannten
    ihr nanntet
    sie nannten

    können (könn, False, en):
    ich kann
    du kanst
    es kann
    wir können
    ihr könnt
    sie können
    ich konnte
    du konntest
    es konnte
    wir konnten
    ihr konntet
    sie konnten

    haben (hab, False, en):
    ich habe
    du hast
    es hat
    wir haben
    ihr habt
    sie haben
    ich hatte
    du hattest
    es hatte
    wir hatten
    ihr hattet
    sie hatten


