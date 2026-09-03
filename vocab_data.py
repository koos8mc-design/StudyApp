# -*- coding: utf-8 -*-
"""
Woordenlijsten Grieks - Nederlands
Elke lijst is een lijst van tuples: (Grieks, Nederlands)
"""

TEKST_8A = [
    ("πάρειμι", "aanwezig zijn"),
    ("εἶπον (imperf. van λέγω)", "ik zei"),
    ("οἱ Ἀχαιοί", "Grieken"),
    ("βοηθέω (+ dat.)", "te hulp komen, helpen"),
    ("ὁ ζευγηλάτης", "legeraanvoerder"),
    ("ὁ ναύτης", "zeeman, matroos"),
    ("ὁ ὁπλίτης", "soldaat"),
    ("παύω", "(doen/laten) stoppen, ophouden"),
    ("κωλύω (+ inf.)", "verhinderen, beletten (om)"),
    ("ἅμα", "tegelijk, tegelijkertijd"),
    ("τόδε (onz. mv. τάδε)", "dit / het volgende"),
    ("οὐδέ", "en niet, maar niet / ook niet, zelfs niet"),
    ("ἐχθρός (+ dat.)", "gehaat (bij), vijandig (aan)"),
]

TEKST_8B = [
    ("ἡ τύχη", "lot"),
    ("τοι", "toch"),
    ("ὁ ἄγγελος", "bode"),
    ("ἡ ἀλήθεια", "waarheid"),
    ("ἀγγέλλω", "berichten, melden"),
    ("τὸ στράτευμα", "leger"),
    ("πιστεύω (+ dat.)", "vertrouwen"),
    ("τοιοῦτος, τοιαύτη, τοιοῦτο(ν)", "zodanig, dergelijk, zo'n"),
    ("φίλτατος, φιλτάτη", "liefst, dierbaarst / zeer geliefd, zeer dierbaar"),
    ("ὁμολογέω (+ dat.)", "instemmen met, akkoord gaan met"),
    ("ἱκετεύω", "smeken"),
]

TEKST_8C = [
    ("ὁ βωμός", "altaar"),
    ("οὐδέν", "niets"),
    ("οὐδαμῶς", "helemaal niet"),
    ("ἤδη", "al, reeds"),
    ("δυστυχής", "ongelukkig"),
    ("οὐκέτι", "niet meer"),
    ("ἀντί (+ gen.)", "in plaats van"),
    ("ἀρέσκω (+ dat.)", "bevallen aan, in de smaak vallen bij"),
    ("εὔνους (+ dat.)", "goedgezind (aan)"),
    ("τὸ Ἴλιον", "Troje"),
]

ALL_LESSONS = {
    "Tekst 8A - Het vertrek": TEKST_8A,
    "Tekst 8B - Ifigeneia naar Aulis": TEKST_8B,
    "Tekst 8C - Het offer": TEKST_8C,
}

# Grammatica-oefening: imperfectum van λύω, ποιέω en εἰμί ('zijn')
# Format: (Grieks, Nederlandse prompt) - net als de woordenlijsten hierboven,
# zodat dezelfde quiz-logica (richting Nederlands -> Grieks) hergebruikt kan worden.
GRAMMAR_EXERCISES = [
    ("ἔλυον", "ik (λύω, imperfectum)"),
    ("ἔλυες", "jij (λύω, imperfectum)"),
    ("ἔλυε(ν)", "hij/zij/het (λύω, imperfectum)"),
    ("ἐλύομεν", "wij (λύω, imperfectum)"),
    ("ἐλύετε", "jullie (λύω, imperfectum)"),
    ("ἔλυον", "zij (mv.) (λύω, imperfectum)"),
    ("ἐποίουν", "ik (ποιέω, imperfectum)"),
    ("ἐποίεις", "jij (ποιέω, imperfectum)"),
    ("ἐποίει", "hij/zij/het (ποιέω, imperfectum)"),
    ("ἐποιοῦμεν", "wij (ποιέω, imperfectum)"),
    ("ἐποιεῖτε", "jullie (ποιέω, imperfectum)"),
    ("ἐποίουν", "zij (mv.) (ποιέω, imperfectum)"),
    ("ἦν", "ik (εἰμί = zijn, imperfectum)"),
    ("ἦσθα", "jij (εἰμί = zijn, imperfectum)"),
    ("ἦν", "hij/zij/het (εἰμί = zijn, imperfectum)"),
    ("ἦμεν", "wij (εἰμί = zijn, imperfectum)"),
    ("ἦτε", "jullie (εἰμί = zijn, imperfectum)"),
    ("ἦσαν", "zij (mv.) (εἰμί = zijn, imperfectum)"),
]
# Let op: controleer deze vormen tegen je eigen boek/aantekeningen (Grammatica-
# katern) - dit zijn de standaardvormen, maar jouw methode kan net iets andere
# spelling/afkortingen gebruiken. Pas gerust aan in deze lijst.

# Korte studietips, worden willekeurig getoond op het startscherm
TIPS = [
    "Het imperfectum krijgt een augment (ἐ-) vooraan als signaal voor verleden tijd.",
    "Werkwoorden die met een klinker beginnen krijgen géén ἐ-, maar een lange klinker (ᾱ, η, ω, ι, υ).",
    "Werkwoorden die met ρ beginnen verdubbelen die ρ na het augment: ἔρριψα.",
    "τόδε / τάδε betekent 'dit' of 'het volgende' - let op de context.",
    "Woorden met (+ dat.) hebben een meewerkend voorwerp nodig, geen lijdend voorwerp.",
    "οὐδέ kan zowel 'en niet' als 'zelfs niet' betekenen, afhankelijk van de zin.",
    "Herhaling is de sleutel: oefen kleine setjes vaker, in plaats van alles in één keer.",
    "Lees hardop - de klank helpt vaak om een woord te onthouden.",
    "Verzin een ezelsbruggetje: bijv. 'ἱκετεύω' klinkt als 'ik ga smeken'.",
    "Woorden met een sterretje (afwijkende vormen) vaker herhalen dan de rest.",
]
