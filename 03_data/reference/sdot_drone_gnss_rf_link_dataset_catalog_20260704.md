# S-DOT Drone GNSS / RF / Link Dataset Catalog

- Date: 2026-07-04 KST
- Purpose: identify public datasets that can support S-DOT drone semantic transmission under GNSS degradation, spoofing/jamming suspicion, and degraded wireless links.
- Safety boundary: use these datasets for defensive detection, anomaly scoring, simulation calibration, and validation only. Do not use them to infer real military routes, emitter locations, or operational EW tactics.

## Bottom Line

For the hackathon demo, keep the main scenario synthetic.

Use public datasets in three ways:

1. **Candidate validation**: pull small samples later to sanity-check feature ranges such as C/N0, DOP, RSS, packet loss, or RF power.
2. **Reference only**: cite as evidence that datasets and methods exist, but do not ingest during the hackathon.
3. **Synthetic required**: create controlled mock data because the exact public dataset does not exist or is unsafe/too operational.

The strongest public sources for v0.7 are:

- TEXBAT for GPS spoofing benchmark context.
- OAKBAT for reproducible GNSS RF spoofing/interference recordings.
- FGI-JSDR / FGI-SpoofRepo / Jammertest for modern GNSS jamming/spoofing I/Q data.
- Yunnan GNSS interference/spoofing dataset for processed receiver features such as C/N0, DOP, pseudorange, Doppler, and position.
- DroneRF / AERPAW / DeepSense 6G for drone RF/link context.

## Candidate Validation Sources

| Source | Domain | Public Data Type | Best S-DOT Use | Caveat |
|---|---|---|---|---|
| TEXBAT | GNSS spoofing | recorded GPS spoofing scenarios | spoofing benchmark reference; feature sanity check | GPS L1 spoofing benchmark, not drone telemetry |
| OAKBAT | GNSS spoofing/interference | binary RF recordings and metadata | reproducible RF spoofing/interference test battery | large RF files; requires SDR processing |
| FGI-JSDR / FGI-SpoofRepo | GNSS spoofing/jamming | raw GNSS I/Q across GPS/Galileo bands | modern multi-frequency spoofing/jamming reference | processing requires GNSS receiver tooling |
| FGI Jammertest 2023 | GNSS jamming/spoofing | raw I/Q from real jammer test campaign | realistic jamming/spoofing feature reference | controlled test data, not drone-specific |
| Yunnan GNSS Dataset with Interference and Spoofing | GNSS receiver features | raw and processed GNSS data; clean/jamming/spoofing scenarios | best candidate for v0.7 feature ranges: C/N0, DOP, Doppler, pseudorange, position | static receiver location; not drone movement |
| Zenodo GNSS Dataset Under Jamming, Spoofing, and Meaconing | GNSS attack dataset | UBX/RINEX/RF monitoring/navigation solutions | reference for attack condition labels and dynamic/static cases | large external resources; verify file access before ingest |
| AERPAW Dataset-12 | UAV wireless link | UAV I/Q, GPS coordinates, RSS at 3.3 GHz | link-health and RSS/trajectory feature ranges | not jamming; wireless propagation dataset |
| DeepSense 6G Scenario 23 | drone wireless/mmWave | received power, RGB, GPS, height, distance, speed, pitch/roll | sensing-aided link prediction and bearer-state feature inspiration | not DDIL/jamming; dataset access may require project-specific download flow |

## Reference-Only Sources

| Source | Domain | Why Reference Only |
|---|---|---|
| DroneRF Mendeley | drone RF detection | useful for RF fingerprinting/detection but not S-DOT link degradation or GNSS integrity |
| AERPAW Drone RC RF Dataset | drone remote-controller RF | useful for Counter-UAS RF fingerprinting; drones idle during capture |
| KU Leuven Drone RF Dataset | chamber RF drone dataset | useful for RF classification/novelty detection; controlled chamber data, not field link health |
| AERPAW Multi-Modal RF Sensor and Radar Dataset for UAV Tracking | RF/radar UAV tracking | useful for future sensor-fusion case; not a communication outage/jamming dataset |
| Maritime GNSS/Jamming Dataset | maritime GNSS interference | useful for real-world jamming labels and RF waterfall concepts; maritime vessel, not drone |
| UAV LoRa avalanche dataset | UAV communication/RSSI/SNR | useful RSS/SNR example; search-and-rescue LoRa, not tactical drone DDIL |
| UAV A2G path loss Mendeley dataset | channel modeling | useful path-loss reference; simulation-derived, not live outage data |

## Synthetic Required For This Project

The following are not available as safe, directly reusable public data for this hackathon and should remain synthetic:

| Needed Data | Reason Synthetic Is Required |
|---|---|
| Drone mission under active jamming with command-board telemetry | Real data is sensitive, rare, and may disclose operational behavior |
| Combined drone GNSS/link/EO-IR/local-cache/rejoin audit timeline | Public datasets usually cover only one modality or non-drone receivers |
| Tactical network mode transitions: full_sync, semantic_summary, store_forward, local_only | Public datasets rarely include tactical bearer policy states |
| Operator decision labels and S-DOT packet priority decisions | These are product/workflow labels, not raw sensor measurements |
| Jamming/spoofing hypothesis score for drone command UI | Must be a defensive synthetic score, not source/emitter attribution |
| Rejoin audit truth-vs-prediction object | Requires known hidden truth and cached raw evidence timeline |

## v0.7 Data Strategy

Recommended:

1. Keep `mock_dataset.json` synthetic for the public demo.
2. Add fields inspired by public GNSS/RF datasets:
   - `cn0_dbhz_mean`
   - `satellite_count`
   - `hdop`
   - `vdop`
   - `doppler_shift_proxy`
   - `pseudorange_residual_proxy`
   - `rss_dbm`
   - `snr_bucket`
   - `packet_loss_pct`
   - `heartbeat_gap_sec`
3. Use public datasets only for range sanity checks and citations.
4. Do not download multi-GB RF/IQ datasets during the initial demo unless a specific validation task is defined.

## Source Notes

### TEXBAT

The University of Texas Radionavigation Laboratory describes TEXBAT as recorded spoofing scenarios compiled to evaluate civil GPS signal authentication techniques. TEXBAT 1.1 includes original TEXBAT 1.0 data plus ds7/ds8 scenarios.

Use:

- spoofing benchmark context
- anti-spoofing evaluation reference
- optional later raw I/Q processing

Source: https://radionavlab.ae.utexas.edu/texbat/

### OAKBAT

Oak Ridge National Laboratory provides OAKBAT GPS L1C/A RF recordings as binary files, with metadata, equipment documentation, configuration files, and collection procedures referenced via the OAKBAT GitHub organization.

Use:

- reproducible GNSS RF spoofing/interference reference
- candidate for future SDR feature extraction

Source: https://doi.ccs.ornl.gov/dataset/d21dfe58-3af9-5ed8-9c97-693c12045aee

### FGI-JSDR / FGI-SpoofRepo / Jammertest

FGI describes a repository of raw GNSS I/Q data with GPS and Galileo signals, covering spoofing types such as synchronous, asynchronous, and meaconing, plus Jammertest 2023 jamming/spoofing recordings. FGI-GSRx can process these datasets.

Use:

- modern GNSS spoofing/jamming data reference
- future FGI-GSRx based processing

Sources:

- https://www.maanmittauslaitos.fi/en/research/research/gnss-specialists/fgi-gnss-jamming-and-spoofing-dataset-repository-fgi-jsdr
- https://researchportal.tuni.fi/en/datasets/fgis-gnss-spoofing-dataset-repository-fgi-spoofrepo/
- https://github.com/nlsfi/FGI-GSRx

### Yunnan GNSS Dataset With Interference And Spoofing

This Mendeley dataset includes clean, commercial-jammer-affected, and HackRF-spoofed scenarios. It includes receiver observations such as C/N0, spectrum, Doppler, pseudorange, carrier phase, position, and DOP.

Use:

- best near-term candidate for synthetic feature range calibration
- clean/jam/spoof class labels for model prototyping

Source: https://data.mendeley.com/datasets/ccdgjcfvn5/1

### Zenodo GNSS Dataset Under Jamming, Spoofing, And Meaconing

This 2025 Zenodo dataset describes controlled attack scenarios including jamming, spoofing, meaconing, and combined attacks with UBX, RINEX, RF monitoring, and navigation solutions.

Use:

- label taxonomy and attack-condition metadata reference
- possible future validation if files are accessible and scope permits

Source: https://zenodo.org/records/15911359

### DroneRF

DroneRF is a Mendeley RF dataset of drone operating modes such as off, on/connected, hovering, flying, and video recording, plus background RF.

Use:

- RF modality reference
- drone RF fingerprinting and mode classification

Source: https://data.mendeley.com/datasets/f4c2b4n755/1

### AERPAW

AERPAW maintains multiple aerial wireless datasets. Dataset-12 includes UAV I/Q samples, GPS coordinates, and RSS values at 3.3 GHz. Dataset-28 includes RF sensor, radar, and ground-truth trajectory measurements for UAV tracking.

Use:

- link-health and RF propagation feature references
- future sensor-fusion validation

Sources:

- https://aerpaw.org/experiments/datasets/
- https://aerpaw.org/dataset/uav-based-signal-data-collected-at-varying-altitudes-and-sampling-rates-for-wireless-communication-studies/
- https://aerpaw.org/dataset/multi-modal-rf-sensor-and-radar-dataset-for-uav-tracking/

### DeepSense 6G Scenario 23

DeepSense 6G Scenario 23 uses drones as transmitters and includes modalities such as received wireless power, images, GPS position, height, distance, speed, pitch, and roll.

Use:

- sensing-aided bearer/link prediction reference
- future multi-modal drone communications validation

Sources:

- https://www.deepsense6g.net/
- https://arxiv.org/html/2412.04734v1

## Recommendation For Current Demo

Do not ingest these datasets yet.

Instead:

- use them to justify v0.7 feature choices
- add source links and caveats in the demo appendix
- keep all operational timelines synthetic
- later run a targeted smoke test on the Yunnan Mendeley GNSS dataset or AERPAW Dataset-12 if feature calibration is needed
