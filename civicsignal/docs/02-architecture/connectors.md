# Connector Registry (Phase 1)

## City-to-Platform Map
| City | Platform | Discovery URL |
|---|---|---|
| Irvine | Granicus | https://irvine.granicus.com/ViewPublisher.php |
| Anaheim | Granicus | https://anaheim.granicus.com/ViewPublisher.php |
| Santa Ana | Laserfiche WebLink | https://publicdocs.santa-ana.org/WebLink |
| Huntington Beach | Legistar | https://huntingtonbeach.legistar.com/Calendar.aspx |
| Newport Beach | Legistar | https://newportbeach.legistar.com/Calendar.aspx |
| Costa Mesa | Legistar | https://costamesa.legistar.com/Calendar.aspx |
| Fullerton | Legistar | https://fullerton.legistar.com/Calendar.aspx |
| Garden Grove | NovusAGENDA | https://gardengrove.novusagenda.com/AgendaPublic |
| Mission Viejo | Hyland OnBase | https://dms.cityofmissionviejo.org/OnBaseAgendaOnline |
| Laguna Niguel | CivicPlus Agenda Center | https://www.cityoflagunaniguel.org/AgendaCenter |

## Bodies to Track per City
- City Council
- Planning Commission

## Connector Notes
- Granicus: parse meeting table, extract meeting links, download agenda packets
- Legistar: parse calendar, extract meeting IDs, fetch agenda items + attachments
- Laserfiche: traverse meeting folders and agenda packet directories
- NovusAGENDA: fetch list, parse meeting ID, open detail, download attachments
- Hyland OnBase: query meeting search, parse meeting page, download attachments
- CivicPlus: parse agenda center list, follow links, download PDFs
