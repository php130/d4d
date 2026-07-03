# Enhancing Maritime Cybersecurity through Operational Technology Sensor Data Fusion: A Comprehensive Survey and Analysis

## Metadata

- Year: 2024
- URL: https://doi.org/10.3390/s24113458
- DOI: 10.3390/s24113458
- Read status: abstract_only

## One-line Takeaway

Maritime OT sensor fusion can turn navigation, surveillance, RF, and related feeds into near-real-time cyber situational awareness for detecting attacks that affect vessel, port, and logistics operations.

## D4D Relevance

Directly supports a T3 semantic maritime COP by treating cyber anomalies as operational events derived from fused OT sensor evidence, helping maintain trusted maritime awareness when networks, sensors, or reporting channels are degraded or contested.

## Key Concepts

- maritime cybersecurity
- operational technology sensor data fusion
- maritime cyber situational awareness
- RF sensor fusion
- navigation and surveillance systems
- near-real-time cyberincident detection
- maritime attack surface
- event correlation

## Input Data

- OT sensor feeds from ships, ports, surveillance systems, and navigation systems
- RF sensor observations
- other maritime sensors used for situational awareness
- cargo and logistics system signals where available
- maritime operational context from industrial and communication systems

## Methods Or Architecture

- survey and literature analysis of maritime OT data fusion approaches
- fusion of maritime situational-awareness data for cybersecurity purposes
- correlation of sensor observations to detect cyberincidents
- use of RF and non-RF sensors as complementary evidence streams
- real-time or near-real-time detection framing

## Outputs / Metrics

- cyberincident alerts or indicators
- improved maritime cyber situational awareness
- operational continuity risk awareness
- safety and security impact awareness
- no quantitative benchmark metrics available from the provided excerpt

## Prototype Hooks

- Represent each OT/RF observation as a semantic COP event with provenance, confidence, timestamp, and sensor health metadata
- Fuse AIS-like navigation reports, RF detections, and surveillance observations to flag spoofing, jamming, missing reports, or inconsistent vessel behavior
- Add cyber anomaly layers to the maritime COP alongside tracks, zones, and mission events
- Support denied-network operation by enabling local edge fusion from onboard or coastal sensors before synchronization is restored
- Use event correlation rules to distinguish physical maritime anomalies from cyber-induced reporting anomalies

## Pitch Evidence

- The paper frames maritime operations as a large cyberattack surface spanning ships, ports, surveillance, navigation, industrial, cargo, and logistics systems
- It argues that navigation and surveillance OT sensors can improve maritime cyber situational awareness
- It specifically examines whether fused OT data can detect cyberincidents in real time or near-real time
- Its emphasis on RF and other sensors aligns with resilient sensing when conventional communications are denied or unreliable

## Limitations / Risks

- Only the abstract/excerpt was available, so specific algorithms, datasets, validation results, and performance numbers are unknown
- As a survey, it may guide architecture more than provide a directly reusable implementation
- Sensor fusion can amplify errors if compromised or spoofed sensors are not modeled explicitly
- Near-real-time detection depends on sensor coverage, latency, synchronization, and edge compute availability
- Cyber and operational anomalies may be hard to separate without strong context and labeled incidents

## Confidence

medium
