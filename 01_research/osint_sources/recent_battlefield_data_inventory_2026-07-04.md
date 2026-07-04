# Recent Battlefield OSINT Data Inventory

- Last checked: 2026-07-04 KST
- Scope: Russia-Ukraine, Israel-Iran / wider Middle East, and reusable global OSINT sources
- D4D fit: T2 OSINT, T3 COP/C2/MDA, T5 training/simulation
- Safety stance: use public, delayed, aggregated, or synthetic data. Do not collect or redistribute PII, faces, account handles, raw Telegram media, live tactical positions, or active targeting cues.

## Best Immediate Sources

| Priority | Source | Theater | Data type | Access | Why it matters for D4D |
|---|---|---:|---|---|---|
| 1 | ACLED | Global, Ukraine, Israel/Iran | conflict events, actors, dates, geocoded locations, fatalities, strategic developments | account/API/export | strongest base event layer for COP and trend analysis |
| 2 | GDELT | Global | news-derived events, entities, themes, tone, geocoding | open API/files | fast broad monitoring and intelligence copilot evidence |
| 3 | NASA FIRMS | Global | thermal anomalies / active fire hotspots | MAP_KEY/API/CSV | proxy for strikes, explosions, fires, infrastructure damage |
| 4 | Copernicus Sentinel-1/2 | Global | SAR/EO satellite imagery | account/API/STAC | damage detection, cloud-independent SAR, maritime/port monitoring |
| 5 | Ukraine missile/drone datasets | Ukraine | daily launched/intercepted missile/UAV counts | Kaggle/GitHub/CSIS/MDAA | air-defense saturation and infrastructure pressure scenario |
| 6 | WarSpotting / Oryx | Ukraine | visually confirmed equipment losses | web/scrape/manual | attrition trends and evidence-backed loss taxonomy |
| 7 | UKMTO/JMIC/MARAD | Strait of Hormuz, Gulf, Arabian Sea | maritime incident advisories, vessel incident summaries, risk levels | web/PDF/manual scrape | direct T3/MDA scenario input |
| 8 | Airwars | Israel/Iran, wider Middle East | civilian harm incident tracking and methodology | web/manual scrape | harm-aware COP and responsible analysis |
| 9 | HDX / ReliefWeb | Global, Ukraine | humanitarian, admin, infrastructure, damage datasets | open download/API | basemaps and humanitarian impact layer |
| 10 | OpenStreetMap / Overpass | Global | roads, rails, ports, power, hospitals, admin boundaries | open API/download | critical infrastructure graph for routing and exposure |

## Global Data Backbone

| Source | URL | Data | Access notes | Use in prototype |
|---|---|---|---|---|
| ACLED | https://acleddata.com/ | political violence, demonstrations, strategic developments | account required; API supports JSON/CSV, filters, pagination | event spine, actor graph, trend alerts |
| UCDP GED | https://ucdp.uu.se/downloads/ | organized violence, georeferenced events, yearly/disaggregated datasets | free downloads, CC BY 4.0 | slower but academically stable validation layer |
| GDELT Event DB / GKG / DOC | https://www.gdeltproject.org/ | global news events, entities, themes, sentiment, source URLs | open, frequent updates | early warning, source triangulation, narrative shifts |
| HDX | https://data.humdata.org/ | humanitarian datasets, admin boundaries, health/education/aid incidents | open account often useful | civilian and infrastructure context |
| ReliefWeb | https://reliefweb.int/ | reports, situation updates, humanitarian documents | open API | report ingestion and summarization |
| ISW / Critical Threats | https://understandingwar.org/ | daily campaign assessments, maps, analytic text | web pages; usually no simple raw API | analyst narrative layer |
| NASA FIRMS | https://firms.modaps.eosdis.nasa.gov/api/ | MODIS/VIIRS active fire / hotspots | MAP_KEY; CSV/KML endpoints | strike/fire proxy, anomaly trigger |
| VIIRS Nighttime Lights | https://www.earthdata.nasa.gov/topics/human-dimensions/nighttime-lights | night lights and outage proxy | NASA Earthdata / EOG products | power outage and recovery proxy |
| Copernicus Data Space | https://dataspace.copernicus.eu/ | Sentinel EO/SAR data | account, STAC/OData/Sentinel Hub APIs | damage mapping, port/maritime monitoring |
| Sentinel-1 | https://dataspace.copernicus.eu/data-collections/copernicus-sentinel-missions/sentinel-1 | C-band SAR, day/night, all-weather | Copernicus API | cloud-independent damage and vessel/port pattern checks |
| OpenStreetMap / Overpass | https://overpass-turbo.eu/ | infrastructure and POI graph | open API, rate-limited | roads/rail/power/ports/hospitals basemap |
| Open-Meteo | https://open-meteo.com/ | weather forecast and historical weather | open API | explain drone/ISR/weather constraints safely |
| ERA5 / Copernicus Climate | https://cds.climate.copernicus.eu/ | reanalysis weather | account/API | backtesting strike/weather correlations |
| MarineTraffic | https://www.marinetraffic.com/ | AIS and ship tracks | commercial/limited free | maritime COP if licensed |
| AISStream | https://aisstream.io/ | live AIS stream | account/API; coverage varies | demo/live maritime feed alternative |
| Global Fishing Watch | https://globalfishingwatch.org/ | fishing activity, AIS-derived products, some public APIs | account/API and license constraints | dark vessel / maritime anomaly proxy |
| OpenSky Network | https://opensky-network.org/ | ADS-B air traffic | account/API, military coverage incomplete | airspace disruption, not tactical tracking |
| FRED / EIA | https://fred.stlouisfed.org/ / https://www.eia.gov/ | oil, fuel, energy price indicators | open APIs | strategic/economic impact layer |

## Russia-Ukraine Specific Sources

| Source | URL | Data | Access notes | Useful scenario |
|---|---|---|---|---|
| ACLED Ukraine Conflict Monitor | https://acleddata.com/monitor/ukraine-conflict-monitor | Ukraine/Black Sea events from 2020-present, infrastructure subsets | restricted download/account | nationwide conflict event layer |
| ISW Russia-Ukraine assessments | https://understandingwar.org/research/russia-ukraine | daily operational assessments and maps | web/manual ingestion | analyst text to event extraction |
| ISW ArcGIS StoryMap | https://storymaps.arcgis.com/stories/36a7f6a6f5a9448496de641cf64bd375 | interactive Ukraine war map | web; raw access unclear | map reference / validation |
| DeepStateMap | https://deepstatemap.live/en | frontline and territorial control map | web/app; raw reuse unclear | front proximity context, use cautiously |
| Liveuamap Ukraine | https://liveuamap.com/ | incident map and updates | web; paid/raw options reported | event cross-check, source links |
| WarSpotting | https://ukr.warspotting.net/ | visually confirmed equipment losses | web; possible scrape/API exploration needed | attrition dashboard and evidence links |
| Oryx Russia losses | https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-equipment.html | visually confirmed vehicle/equipment losses | web; evidence-backed but scrape carefully | loss taxonomy and evidence model |
| Oryx/Kaggle derivative | https://www.kaggle.com/datasets/piterfm/2022-ukraine-russia-war-equipment-losses-oryx | structured Oryx-derived losses | Kaggle | quick analysis without scraping Oryx |
| Massive Missile Attacks on Ukraine | https://www.kaggle.com/datasets/piterfm/massive-missile-attacks-on-ukraine | launched and shot-down missiles/UAVs | Kaggle; Petro Ivaniuk dataset | air-defense saturation scenario |
| Petro Ivaniuk dataset repo | https://github.com/PetroIvaniuk/2022-Ukraine-Russia-War-Dataset | missile/UAV and Oryx-derived datasets | GitHub/Kaggle links | reproducible source path |
| CSIS Russian Firepower Strike Tracker | https://www.csis.org/programs/futures-lab/projects/russian-firepower-strike-tracker-analyzing-missile-attacks-ukraine | missile/UAV attack analysis | dashboard/commentary; cites Petro dataset | policy framing and validation |
| Missile Defense Advocacy Ukrainian War Tracker | https://www.missiledefenseadvocacy.org/missile-threat-and-proliferation/todays-missile-threat/ukrainian-war-updates/ | missile/UAV counts from Ukrainian Air Force reporting | downloadable data link may change | missile defense trend charts |
| alerts.in.ua | https://alerts.in.ua/en | real-time air raid alerts | token/API request for programmatic access | warning/COP layer, delayed demo mode |
| Official alerts.in.ua Python client | https://github.com/alerts-ua/alerts-in-ua-py | API client | token required | connector implementation |
| Open-source air raid API wrapper | https://github.com/and3rson/raid | self-hostable alert API wrapper | MIT repo | local simulation / API pattern |
| Ukraine War Unmanned Systems Tracker | https://unmannedsystemstracker.com/ | USV, UGV, UAV, air defense, loss trends | web; terms and raw access need review | unmanned systems trend layer |
| ISIS Shahed monthly analysis | https://isis-online.org/isis-reports/monthly-analysis-of-russian-shahed-136-deployment-against-ukraine | monthly UAV launch, composition, saturation analysis | web tables/sources | air-defense saturation briefing |
| UNOSAT Ukraine products | https://unosat.org/ | satellite-based damage assessments | web/product downloads vary | damage labels for SAR/EO validation |
| KSE Russia Will Pay | https://kse.ua/russia-will-pay/ | physical infrastructure damage estimates and methodology | web/reports/aggregates | infrastructure impact and reconstruction |
| ACAPS Ukraine Master Dataset | https://www.acaps.org/ | consolidated crisis indicators | PDFs/dataset docs | humanitarian context |
| HDX Ukraine group | https://data.humdata.org/group/ukr | 200+ Ukraine humanitarian datasets | open download | admin/humanitarian basemap |
| OHCHR Ukraine | https://ukraine.ohchr.org/ | human rights reports, energy infrastructure impacts | reports | civilian impact context |
| Texty rail attacks analysis | https://texty.org.ua/ | open-source rail attack analysis and maps | article-derived data | rail logistics resilience scenario |
| Gard Black Sea maritime updates | https://gard.no/en/insights/war-ukraine-impact-on-maritime-situation/ | maritime risk commentary | web | Black Sea shipping risk layer |
| Skuld Black Sea security update | https://www.skuld.com/topics/port/port-news/europe/maritime-security-in-the-northern-black-sea-operational-realities-and-emerging-risks/ | shipping and tanker attack context | web | maritime threat narrative |
| UN Trade and Development AIS Black Sea deck | https://unstats.un.org/bigdata/events/2024/conference/agenda/day2-sessions/qol-demos/presentations/Daniel%20Hopp%2002%20-%202024_06_11_Using%20AIS%20data%20for%20insights%20to%20Black%20Sea%20shipping.pdf | AIS-derived Black Sea shipping insights | PDF, aggregated | maritime data method reference |

## Israel-Iran / Middle East Specific Sources

| Source | URL | Data | Access notes | Useful scenario |
|---|---|---|---|---|
| ACLED Middle East updates | https://acleddata.com/update/middle-east-special-issue-march-2026 | regional conflict trends and Iran crisis analysis | web; eligible users can access daily data hub | event layer and trend framing |
| ACLED Israel profile | https://acleddata.com/country/israel | country-level conflict event profile | account for deeper data | missile/drone impact trends |
| ACLED Iran profile/data | https://data.humdata.org/dataset/iran-acled-conflict-data | ACLED-derived Iran conflict data on HDX | HDX download/account | Iran-side event layer |
| UCDP Israel-Iran conflict info | https://ucdp.uu.se/ | organized violence records | downloads/API | stable conflict metadata |
| GDELT | https://www.gdeltproject.org/ | news events/entities/themes | open | rapid monitoring across languages |
| CTP/ISW Iran updates | https://www.criticalthreats.org/briefs/iran-updates | Iran updates and assessments | web | analyst narrative and chronology |
| Airwars Iran/Israel/US war methodology | https://airwars.org/methodology-note-documenting-civilian-harm-in-the-2026-iran-israel-and-us-war/ | civilian harm tracking methodology | web/manual | harm-aware evidence model |
| Airwars research hub | https://airwars.org/research/ | incident research and updates | web | civilian harm and maritime harm tracking |
| Iran-Israel War OSINT Dataset GitHub | https://github.com/danielrosehill/Iran-Israel-War-2026-OSINT-Data | missile/drone wave records, targets, estimates, reactions | third-party; cross-check required | fast prototype seed dataset |
| Iran-Israel War Hugging Face dataset | https://huggingface.co/datasets/danielrosehill/Iran-Israel-War-2026 | 53 attack waves, many structured fields | third-party; cross-check required | wave-level simulator |
| INSS Campaign Dashboard | https://www.inss.org.il/publication/lions-roar-data/ | selected real-time campaign data and map | web/dashboard | situational dashboard reference |
| JINSA IAMD analysis | https://jinsa.org/jinsa_report/rising-lion-air-defense/ | air/missile defense estimates | article/report | intercept-cost and saturation framing |
| UKMTO | https://www.ukmto.org/ | maritime alerts, incident reporting, advisories | web/PDF | Hormuz maritime COP |
| UKMTO recent incidents | https://www.ukmto.org/recent-incidents | recent maritime security incidents | web | event ingestion candidate |
| JMIC advisories via UKMTO | https://www.ukmto.org/partner-products/jmic-products | maritime threat levels, confirmed incident lists | PDF | structured incident extraction |
| MARAD MSCI alerts | https://www.maritime.dot.gov/msci | U.S. maritime alerts/advisories | web | official maritime risk layer |
| MSCIO | https://www.mscio.eu/ | Indian Ocean maritime security coordination | web/PDF | regional maritime context |
| Windward Daily Intelligence | https://insights.windward.ai/ | maritime risk, dark activity, vessel incidents | vendor/public snippets | commercial MDA reference |
| UANI shipping updates | https://www.unitedagainstnucleariran.com/ | Iran shipping / tanker updates | advocacy source; cross-check | vessel risk narrative |
| MarineTraffic / AISStream | https://www.marinetraffic.com/ / https://aisstream.io/ | AIS and vessel movements | commercial/free tiers | Hormuz traffic disruption |
| NASA FIRMS Middle East AOI | https://firms.modaps.eosdis.nasa.gov/api/ | fire hotspots in Iran/Israel/Gulf | MAP_KEY/API | strike/fire corroboration |
| Copernicus Sentinel Middle East AOI | https://dataspace.copernicus.eu/ | EO/SAR imagery | account/API | port/damage/smoke/floodlight monitoring |
| OpenSky / ADS-B Exchange | https://opensky-network.org/ / https://www.adsbexchange.com/ | aircraft tracks and airspace disruption | incomplete for military | civil aviation disruption only |
| EIA / FRED oil indicators | https://www.eia.gov/ / https://fred.stlouisfed.org/ | oil price, supply, stock indicators | open APIs | Hormuz strategic impact |

## Safety / Legal Red Lines

- Avoid live targeting support: do not output current military unit coordinates, active route recommendations, or strike optimization.
- Use delayed or aggregated time windows for demos when possible.
- Do not store raw social media posts containing faces, usernames, phone numbers, exact home addresses, or distress footage.
- For Telegram/X/YouTube sources, store only citation metadata and derived non-sensitive indicators unless explicit permission and safety review exist.
- Treat third-party AI-assisted datasets as seed data only. Cross-check with ACLED, official advisories, satellite proxies, and multiple news sources.
- Keep all API keys in `.env`; never commit or paste them into reports, demos, or notebooks.

## Recommended First Collection Order

1. Build event spine from ACLED + GDELT.
2. Add theater-specific strike/missile counts:
   - Ukraine: Petro/Kaggle, CSIS, MDAA, alerts.in.ua.
   - Israel-Iran: ACLED crisis data if accessible, Airwars, Iran-Israel OSINT dataset as seed.
3. Add physical evidence proxies:
   - FIRMS fire hotspots.
   - Sentinel-1/2 imagery or precomputed damage products.
   - VIIRS nighttime lights for outage/energy impact.
4. Add infrastructure graph:
   - OSM roads/rails/ports/power/hospitals.
   - HDX admin boundaries and humanitarian layers.
5. Add maritime layer for T3:
   - UKMTO/JMIC/MARAD advisories.
   - AIS from MarineTraffic/AISStream/Global Fishing Watch if license allows.
6. Normalize into a shared schema:
   - `event_id`, `time`, `lat/lon`, `area`, `actor`, `event_type`, `source_refs`, `confidence`, `civilian_risk`, `infrastructure_refs`, `network_priority`, `recommended_action`.
