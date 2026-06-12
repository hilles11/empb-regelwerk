# Mischungsprüfung – Regelwerk-Updates

Dieses öffentliche Repository stellt ausschließlich das freigegebene Regelwerk für die Anwendung „Mischungsprüfung“ bereit.

## Veröffentlichung

1. Neue VDA-, IATF-, PPAP-, ISO- oder kundenspezifische Änderungen fachlich bewerten.
2. `latest.mprules` aktualisieren und `rulesVersion`, `reviewedAt`, `summary`, `changes`, `references` und die betroffenen Prüfregeln pflegen.
3. Datei gegen das Schema der Anwendung prüfen.
4. Änderung erst nach interner fachlicher Freigabe in den Branch `main` übernehmen.

Die Anwendung ruft folgende Datei ab:

`https://raw.githubusercontent.com/hilles11/empb-regelwerk/main/latest.mprules`

Dieses Repository enthält keine Berichte, Messwerte, Kunden- oder Unternehmensdaten und keine kopierten Normtexte.

## Automatische Quellenüberwachung

Der GitHub-Workflow `check-official-sources.yml` prüft alle sechs Stunden die öffentlich sichtbaren Änderungsstände von VDA Band 2, IATF Sanctioned Interpretations, IATF Customer Specific Requirements und AIAG PPAP. Das Ergebnis wird mit Prüfzeitpunkt in `source-status.json` gespeichert.

Eine Änderung der öffentlich sichtbaren Ausgabe oder Quelle führt in der Anwendung zur Meldung `Gesamtkonformität nicht bestätigt`. Geschützte oder kostenpflichtige Norminhalte werden nicht kopiert oder automatisch als fachlich freigegebene Prüfregel interpretiert.
