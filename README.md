# CTS SML Parser API

REST API zur Analyse von Tasmota SML Dump Ausgaben und Dekodierung der enthaltenen Daten.

Erleichtert die Erstellung eines Tasmota SML Scripts erheblich durch programmatischen Zugriff über eine REST API.

## Über dieses Projekt

Diese Software ist eine modifizierte Version des ursprünglichen [tasmota-sml-parser](https://github.com/ixs/tasmota-sml-parser) Projekts.

**Betrieben und weiterentwickelt von:** Christians Technikshop GmbH

## Lizenz

Dieses Programm ist freie Software: Sie können es unter den Bedingungen der GNU Affero General Public License, wie von der Free Software Foundation veröffentlicht, weitergeben und/oder modifizieren, entweder gemäß Version 3 der Lizenz oder (nach Ihrer Option) jeder späteren Version.

Dieses Programm wird in der Hoffnung verteilt, dass es nützlich sein wird, aber OHNE JEDE GEWÄHRLEISTUNG; sogar ohne die implizite Gewährleistung der MARKTFÄHIGKEIT oder EIGNUNG FÜR EINEN BESTIMMTEN ZWECK. Siehe die GNU Affero General Public License für weitere Details.

Sie sollten eine Kopie der GNU Affero General Public License zusammen mit diesem Programm erhalten haben. Falls nicht, siehe <https://www.gnu.org/licenses/>.

## Quellcode

Der Quellcode dieser modifizierten Version ist verfügbar unter:
**https://github.com/Christians-Shop/CTS_sml_parser**

Gemäß den Anforderungen der GNU Affero General Public License (AGPL v3) stellen wir den vollständigen Quellcode dieser modifizierten Version zur Verfügung.

## API Verwendung

### Endpunkt: `/api/decode`

**Methode:** `POST`  
**Content-Type:** `application/json`

**Request Body:**
```json
{
  "smldump": "14:10:15.988 : 77 07 01 00 10 07 00 ff 01 01 62 1b 52 00 53 01 c6 01\n14:10:16.009 : 77 07 01 00 20 07 00 ff 01 01 62 23 52 ff 63 08 f2 01"
}
```

Oder als Array:
```json
{
  "smldump": [
    "14:10:15.988 : 77 07 01 00 10 07 00 ff 01 01 62 1b 52 00 53 01 c6 01",
    "14:10:16.009 : 77 07 01 00 20 07 00 ff 01 01 62 23 52 ff 63 08 f2 01"
  ]
}
```

**Response:**
```json
{
  "messages": [...],
  "tasmota_meter_def": "M 1\n+1,3,s,0,9600,\n...",
  "parse_errors": [],
  "obis_errors": []
}
```

### Weitere Endpunkte

- `GET /` - API-Informationen und Quellcode-Link
- `GET /license` - Vollständiger Lizenztext (AGPL v3)

## Modifikationen

Diese Version wurde von Christians Technikshop GmbH modifiziert und erweitert, insbesondere:
- Umstellung von Webapp auf reine REST API
- Entfernung der Web-UI Komponenten
- Verbesserte Fehlerbehandlung und JSON-Serialisierung
- API-Endpunkt für programmatischen Zugriff

## Original

Ursprüngliches Projekt: https://github.com/ixs/tasmota-sml-parser
