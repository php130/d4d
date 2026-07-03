# Sensors and AI Techniques for Situational Awareness in Autonomous Ships: A Review

## Metadata

- Year: 2020
- URL: https://doi.org/10.1109/tits.2020.3023957
- DOI: 10.1109/tits.2020.3023957
- Read status: partial_text

## One-line Takeaway

A resilient maritime COP should distrust any single feed and fuse AIS, radar, GNSS/INS, cameras, LiDAR, audio, charts, and external archives into validated objects, tracks, classifications, anomalies, and sensor-integrity scores.

## D4D Relevance

Directly supports a T3 semantic COP by defining the maritime perception stack, operational requirements, sensor tradeoffs, and AI tasks needed to turn degraded or intermittent sensor/network data into a cross-validated shared operational picture. The paper is especially useful for denied-network design because it stresses offline AI operation, local processing, redundancy, integrity monitoring, and output interfaces for downstream autonomy or decision-support modules.

## Key Concepts

- multi-sensor maritime situational awareness
- sensor fusion for autonomous ships
- GNSS/INS positioning and integrity
- AIS augmentation and validation
- radar and LiDAR complementary sensing
- visual and infrared vessel detection
- microphone arrays for maritime context awareness
- target detection, classification, localization, and tracking
- situational abnormality detection
- sensor integrity monitoring
- offline AI/ML inference
- cross-referencing among heterogeneous sensors

## Input Data

- GNSS position, velocity, and time
- INS/IMU attitude and dead-reckoning data
- AIS broadcasts
- X-band and S-band marine radar returns
- LiDAR point clouds
- monocular, stereo, monochrome, RGB, and infrared camera imagery
- microphone or microphone-array audio
- electronic charts and external maritime data archives
- weather and visibility context where available
- own-ship state such as heading, velocity, route, and planned track

## Methods Or Architecture

- advanced sensor system feeding autonomous navigation and situational-awareness modules
- long-range fusion using radar, AIS, and cameras above roughly 1 nautical mile
- close-range fusion using LiDAR, cameras, AIS, and audio below roughly 1 nautical mile
- object detection and classification from images, sound, radar, and LiDAR
- stereo-camera ranging by triangulation
- cross-validation of position, velocity, heading, and identity across redundant sensors
- machine learning including deep learning and Gaussian processes for perception and fusion tasks
- sensor-integrity monitoring to assess source quality and detect degraded inputs
- offline-trained AI models running locally without internet dependency
- output interface from perception layer to collision avoidance, route planning, ship-state definition, or COP services

## Outputs / Metrics

- detected maritime objects
- classified vessels or obstacles
- localized targets with range, bearing, position, velocity, and heading
- validated or contradicted AIS tracks
- sensor health and integrity indicators
- situational abnormality alerts
- true positive, false positive, true negative, and false negative rates
- positioning accuracy, availability, fix interval, integrity, and continuity
- target detection range
- processing latency target under 60 seconds for online situational-awareness results
- comparisons by accuracy, complexity, resource demand, maritime compatibility, and adaptability

## Prototype Hooks

- Build a local edge-fusion node that emits semantic COP objects with confidence and provenance rather than raw-only sensor feeds.
- Represent each track as a T3 entity with source evidence, uncertainty, freshness, and contradiction flags.
- Use AIS as a helpful but untrusted claim source, validated against radar, camera, LiDAR, and audio detections.
- Add degraded-network behavior where the vessel or local node continues inference offline and synchronizes semantic deltas when connectivity returns.
- Implement integrity scoring per sensor family so the COP can explain why an object is trusted, stale, or suspect.
- Create long-range and close-range fusion zones matching the paper's deployment concept.
- Use audio hooks for small craft or event detection when AIS is absent and visual/radar data are weak.
- Expose outputs as a compact semantic event stream: object detected, track updated, classification changed, anomaly detected, sensor degraded.
- Prioritize COTS-compatible sensors and local ML inference for hackathon realism.

## Pitch Evidence

- The paper frames autonomous maritime awareness as a multi-sensor perception problem, which validates a semantic COP architecture built around fusion rather than a single network feed.
- It explicitly argues that autonomous vessels need to cross-reference and verify data from multiple sensors, matching the denied-network requirement for trust under uncertainty.
- It identifies AIS and external archives as auxiliary data, not sufficient truth sources, supporting a COP that treats messages as claims to be corroborated.
- It states that AI/ML functions should work offline after training and compute online situational-awareness results within practical latency, which supports edge-first COP operation.
- It maps sensor families to operational ranges, giving a defensible basis for layered maritime awareness in a prototype demo.
- It links perception outputs to downstream modules such as collision avoidance, route planning, and ship-state definition, which helps position the COP as a decision layer rather than a dashboard only.

## Limitations / Risks

- This is a review paper rather than a deployed COP implementation, so it offers architecture guidance more than validated end-to-end performance.
- The paper is focused on autonomous shipboard perception, while a multi-unit maritime COP also needs inter-node synchronization, data governance, and command workflows.
- Some sensors, especially LiDAR and infrared cameras, face cost, weather, range, eye-safety, and ruggedization constraints in maritime environments.
- AIS can be unavailable, spoofed, stale, or absent on small craft, so it must not be treated as authoritative.
- Camera and LiDAR performance degrade in fog, rain, darkness, sea spray, glare, and harsh weather.
- Ship system interfaces may be proprietary, serial, unidirectional, or isolated for cyber-security reasons, complicating integration.
- The excerpt does not provide complete benchmark tables for all AI techniques, so detailed model selection should be validated against the full paper and newer literature.

## Confidence

high
