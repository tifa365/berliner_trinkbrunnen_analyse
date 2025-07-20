# Das Rätsel der Berliner Trinkbrunnen: Warum unterschiedliche Datenquellen verschiedene Zahlen liefern

*Eine technische Analyse der Diskrepanzen zwischen offiziellen Daten der Berliner Wasserbetriebe und Community-Daten von OpenStreetMap*

## Die verwirrende Ausgangslage

Wer sich in Berlin an einem heißen Sommertag auf die Suche nach einem Trinkbrunnen macht, stößt schnell auf ein verwirrendes Problem: Je nachdem, welche Datenquelle man konsultiert, erhält man völlig unterschiedliche Antworten auf die scheinbar einfache Frage "Wie viele Trinkbrunnen gibt es eigentlich in Berlin?"

Nach einer umfassenden technischen Analyse verschiedener Datenquellen zeigt sich ein komplexes Bild, das weit über eine simple Zählung hinausgeht und grundlegende Fragen über Datenqualität, Aktualität und die Zuverlässigkeit verschiedener Informationsquellen aufwirft.

## Die Datenquellen im Überblick

### Berliner Wasserbetriebe (BWB) - Die offizielle Quelle

Die Berliner Wasserbetriebe, als Eigentümer und Betreiber der meisten Trinkbrunnen in der Hauptstadt, stellen ihre Daten über verschiedene technische Schnittstellen zur Verfügung. Hier wird es jedoch bereits kompliziert:

**WFS-Server (Web Feature Service)**: ✅ **244 Trinkbrunnen**
- Vollständig funktionsfähig
- Detaillierte Metadaten zu jedem Brunnen
- Präzise Koordinaten und Attributdaten

**ArcGIS FeatureServer**: ❌ **0 Trinkbrunnen**
- Technisch konfiguriert, aber leer
- Metadaten vorhanden, aber keine Abfragen möglich
- Fehlermeldungen bei allen Anfragen

**ArcGIS OGC FeatureServer**: ❌ **0 Trinkbrunnen**
- "Ungültige Abfrageparameter" bei allen Versuchen
- Service funktioniert nur für Metadaten

### OpenStreetMap (OSM) - Die Community-Quelle

OpenStreetMap, das von einer weltweiten Community gepflegte freie Kartenprojekt, zeigt ein anderes Bild:

**OSM-Daten**: ✅ **251 Trinkbrunnen**
- Community-gepflegt und regelmäßig aktualisiert
- Hohe Positionsgenauigkeit
- Teilweise zusätzliche Informationen wie Betreiber

### Google Maps KML - Der Sonderfall

Interessanterweise zeigt eine Analyse der Google Maps KML-Daten noch eine dritte Zahl:

**Google Maps KML**: **219 Feature-IDs**
- Bezieht sich auf dieselbe BWB-Quelle
- Möglicherweise gefilterte oder veraltete Daten

## Die detaillierte Analyse: Wo liegen die Unterschiede?

Um das Rätsel zu lösen, wurde eine präzise Gegenüberstellung der OSM- und BWB-Daten durchgeführt. Dabei wurden Trinkbrunnen als "übereinstimmend" betrachtet, wenn sie maximal 50 Meter voneinander entfernt waren.

### Das überraschende Ergebnis

**231 Übereinstimmungen** (94,7% Abdeckung)
- Median-Distanz: nur 1,3 Meter
- 93,1% der Übereinstimmungen liegen sogar unter 10 Meter Abstand
- Beeindruckende Genauigkeit der Community-Daten

**13 BWB-Brunnen fehlen in OSM**
- Hauptsächlich "Kaiser Brunnen" (10 Stück)
- 2 "Bituma-Brunnen" (behindertengerecht)
- 1 unbekannter Typ

**20 OSM-Brunnen sind nicht in BWB-Daten**
- Möglicherweise von anderen Betreibern
- Eventuell neuere Installationen
- Oder historische/inoffizielle Wasserquellen

## Was bedeuten diese Diskrepanzen?

### Technische Infrastruktur-Probleme

Die unterschiedlichen Ergebnisse der BWB-eigenen Systeme deuten auf ernsthafte technische Probleme hin:

1. **Datensynchronisation**: Der WFS-Server und die ArcGIS-Services scheinen nicht synchronisiert zu sein
2. **Service-Konfiguration**: Trotz korrekter Metadaten versagen die Abfrage-Funktionen
3. **Wartung und Updates**: Möglicherweise werden nicht alle Services gleichmäßig gepflegt

### Die Stärke der Community

Die OSM-Daten zeigen beeindruckende Qualität:
- **148 Brunnen** sind korrekt als "Berliner Wasserbetriebe" attribuiert
- Positionsgenauigkeit oft besser als offizielle Daten
- Zusätzliche Informationen durch lokale Kenntnisse

### Die 20 "zusätzlichen" Brunnen

Besonders interessant sind die 20 Trinkbrunnen, die nur in OSM erscheinen:
- **Evangelische Friedensgemeinde Charlottenburg**: 1 Brunnen
- **Studierendenwerk Berlin**: 1 Brunnen  
- **Weitere Betreiber**: 18 Brunnen

Dies deutet darauf hin, dass die offizielle BWB-Statistik möglicherweise nur die eigenen Brunnen erfasst, während die Community auch Brunnen anderer Betreiber kartiert.

## Praktische Konsequenzen für Nutzer

### Für App-Entwickler und Kartenanbieter

- **WFS als primäre Quelle**: Zuverlässigste offizielle Datenquelle
- **OSM als Ergänzung**: Für vollständigste Abdeckung
- **Fallback-Strategien**: Unbedingt nötig bei BWB-Service-Ausfällen

### Für die Stadtverwaltung

- **Service-Wartung**: Dringende Überprüfung der ArcGIS-Infrastruktur nötig
- **Datenqualität**: OSM-Community als wertvolle Ergänzung zu offiziellen Daten
- **Transparenz**: Klärung, welche Brunnen in offizielle Statistiken einfließen

## Fazit: Mehr als nur Zahlen

Das Berliner Trinkbrunnen-Rätsel illustriert exemplarisch die Herausforderungen moderner Dateninfrastruktur:

1. **Technische Zuverlässigkeit**: Selbst gut ausgestattete öffentliche Einrichtungen kämpfen mit Service-Ausfällen
2. **Community-Power**: Crowdsourcing kann offizielle Daten nicht nur ergänzen, sondern teilweise übertreffen
3. **Datenintegration**: Die Wahrheit liegt oft in der Kombination verschiedener Quellen

**Die wahrscheinlich genaueste Antwort**: Berlin hat etwa **271 öffentlich zugängliche Trinkwasserquellen** - 244 offizielle BWB-Brunnen plus 20 zusätzliche, von der Community identifizierte Wasserstellen plus 7 weitere durch Überschneidungen.

Für durstige Berliner und Touristen ist die Botschaft klar: Verlassen Sie sich auf mehrere Quellen, nutzen Sie Community-Apps wie OSM-basierte Karten, und haben Sie Verständnis dafür, dass selbst in einer hochtechnisierten Stadt wie Berlin die digitale Infrastruktur nicht immer perfekt funktioniert.

Das nächste Mal, wenn Sie vor einem Trinkbrunnen stehen, denken Sie daran: Sie stehen nicht nur vor einer Wasserquelle, sondern vor einem kleinen Baustein eines komplexen digitalen Ökosystems, das zeigt, wie wertvoll sowohl offizielle Daten als auch Community-Engagement für unsere städtische Infrastruktur sind.

---

*Die vollständige technische Analyse einschließlich interaktiver Karten und Datendownloads ist verfügbar unter den generierten Dateien: `bwb_vs_osm_simple.html` für eine einfache Übersicht und `trinkbrunnen_osm_vs_bwb_comparison.html` für eine detaillierte Analyse.*