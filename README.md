# Grieks Woordjes Oefenen

Klein oefenprogramma voor Grieks-Nederlandse woordenschat (Tekst 8A, 8B, 8C).

## Hoe krijg ik de .exe?

1. Maak een nieuwe (privé of publieke) repository aan op GitHub.
2. Upload alle bestanden uit deze map naar die repository (inclusief de map `.github`!).
   - Makkelijkste manier: pak de hele map uit en sleep alles naar de GitHub-website
     via "Add file" -> "Upload files", of gebruik `git`:
     ```
     git init
     git add .
     git commit -m "Eerste versie"
     git branch -M main
     git remote add origin <jouw-repo-url>
     git push -u origin main
     ```
3. Zodra je pusht naar de branch `main`, start GitHub Actions automatisch.
   Ga naar het tabblad **Actions** in je repository, klik op de laatst gestarte run
   ("Build Windows exe"), wacht tot hij groen is (duurt ~1-2 minuten).
4. Onderaan die run-pagina vind je bij **Artifacts** een bestand
   `GrieksWoordjesOefenen-windows`. Download en pak het uit — daar zit je `.exe` in.

Je kunt de build ook handmatig opnieuw starten via Actions -> "Build Windows exe" ->
"Run workflow" (rechtsboven), zonder dat je iets hoeft te wijzigen.

## Lokaal uitproberen (zonder .exe)

Als je Python geïnstalleerd hebt, kun je de app ook direct starten:

```
python main.py
```

## Woordjes bijwerken

Alle woorden staan in `vocab_data.py`. Voeg gewoon nieuwe regels toe in het format
`("Grieks", "Nederlands")` en push opnieuw — de volgende build neemt ze automatisch mee.

## Functies

- Kies zelf welke lessen (8A/8B/8C) je oefent, of oefen werkwoordsvormen (imperfectum)
- Richting: Grieks -> Nederlands, Nederlands -> Grieks, of gemengd
- Drie oefenvormen: meerkeuze, zelf typen, of flashcards
- Score en langste reeks bijhouden
- **Voortgang tussen sessies**: de app onthoudt welke woorden je vaak fout hebt
  (opgeslagen in `voortgang.json`, naast de .exe). Vink "Focus op moeilijke
  woorden" aan om die vaker te zien.
- **Optionele timer** per vraag (zelf instelbaar aantal seconden)
- **Hints** bij zelf typen (eerste letter van het antwoord)
- **"Oefen je foute woorden opnieuw"** na elke ronde
- **Experimentele uitspraak** (🔊-knop): leest het Griekse woord voor met een
  offline stem. Dit is *geen* native Oudgrieks - het is een best-effort
  voorlezing, vooral bedoeld als extra geheugensteuntje. Kun je uitzetten
  in de opties.

## Grammatica-oefening bijwerken

De imperfectum-vormen staan in `vocab_data.py` onder `GRAMMAR_EXERCISES`.
Dit zijn standaardvormen uit de klassieke grammatica - controleer ze even
tegen je eigen boek, want jouw methode gebruikt soms net iets andere
afkortingen of spelling.
