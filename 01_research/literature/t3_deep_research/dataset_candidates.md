# Dataset Candidates

Last updated: 2026-07-03

## Goal

Find data that supports a 24-hour demo for:

> Semantic maritime events -> degraded-network prioritization -> COP update -> grounded brief.

## Highest Priority

| Dataset/source | URL | Use | Access risk |
| --- | --- | --- | --- |
| D4D synthetic scenario data | local generation | Guaranteed demo path: AIS tracks, weather, OSINT events, SAR-only detection | Low |
| NOAA AIS / MarineCadastre | https://hub.marinecadastre.gov/pages/vesseltraffic | AIS behavior examples and maritime traffic baseline | Medium; U.S. waters |
| Global Fishing Watch | https://globalfishingwatch.org/ | vessel activity / fishing behavior context | Medium; API/policy check |
| MarineTraffic | https://marinetraffic.com/ | AIS and vessel tracking if account/API available | High; likely paid/limited |
| KMA weather data | https://data.kma.go.kr/ and https://apihub.kma.go.kr/ | weather masking and operational condition | Medium; API key may be needed |
| GDELT | https://www.gdeltproject.org/ | OSINT/news event stream | Low-medium |
| OpenStreetMap / Overpass | https://www.openstreetmap.org/ and https://wiki.openstreetmap.org/wiki/Overpass_API | ports, coastline, facilities, geography | Low |

## Maritime / Satellite Sources

| Dataset/source | URL | Use | Note |
| --- | --- | --- | --- |
| Copernicus Sentinel | https://dataspace.copernicus.eu/ | SAR/EO reference layer | Full SAR processing may be too heavy |
| LS-SSDD-v1.0 | https://doi.org/10.3390/rs12182997 | Sentinel-1 small ship detection dataset reference | Good research evidence; actual data access needs check |
| NASA FIRMS | https://firms.modaps.eosdis.nasa.gov/ | thermal anomaly / fire context | More useful for disaster than MDA |
| KHOA / OceanGrid | http://www.khoa.go.kr/oceangrid/ | tide/ocean conditions | Korean ocean data; API status check |

## Practical Demo Dataset Plan

Use a hybrid approach:

1. **Synthetic AIS tracks**
   - 8-12 vessels
   - 2 normal cargo routes
   - 1 AIS gap
   - 1 loitering behavior
   - 1 rendezvous candidate
   - 1 route deviation

2. **Synthetic network degradation**
   - normal bandwidth
   - 30% bandwidth
   - 10% bandwidth
   - intermittent link drop

3. **Public context**
   - OpenStreetMap coastline/ports
   - weather sample
   - GDELT/news sample or static OSINT event snippets

4. **Synthetic SAR-only event**
   - "unmatched radar/satellite detection near AIS gap"
   - clearly labeled as synthetic

## Data Safety

- Do not show real personal information.
- Do not label real vessels as hostile.
- Use synthetic vessel IDs in demo.
- Use public event/news only as context, not as accusation.
- Mark generated dark-vessel cases as synthetic.

