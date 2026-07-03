# Detecting Intentional AIS Shutdown in Open Sea Maritime Surveillance Using Self-Supervised Deep Learning

## Metadata

- Year: 2023
- URL: https://doi.org/10.1109/tits.2023.3322690
- DOI: 10.1109/tits.2023.3322690
- Read status: abstract_only

## One-line Takeaway

A self-supervised transformer can flag suspicious AIS silence by learning when satellite AIS messages should normally be received and detecting mismatches in real time.

## D4D Relevance

Directly supports a resilient maritime COP by treating missing AIS as an interpretable signal rather than simply a data gap. For a T3 semantic COP, this paper provides a way to infer vessel intent or deception under degraded, denied, or intermittent sensing conditions and convert absence-of-reporting into anomaly events for operators.

## Key Concepts

- intentional AIS shutdown detection
- abnormal missing reception
- self-supervised learning
- transformer models
- satellite AIS surveillance
- real-time maritime anomaly detection
- open-sea vessel behavior inference
- absence as evidence

## Input Data

- historical satellite AIS messages
- vessel trajectories
- one year of real-world AIS data
- AIS receptions from four Norwegian surveillance satellites
- per-minute message reception or non-reception labels inferred from history

## Methods Or Architecture

- train a self-supervised model on historical AIS reception patterns
- use transformer-based sequence modeling
- predict whether an AIS message should be received in the next minute
- compare predicted reception with actual reception
- raise anomaly when expected AIS reception is absent
- scale processing to large monthly AIS volumes

## Outputs / Metrics

- AIS missing-reception anomaly alerts
- predicted probability or decision that a message should be received
- comparison between expected and observed AIS reception
- real-time processing claim above 500 million AIS messages per month
- coverage of more than 60000 ship trajectories
- validation by rediscovering previously identified intentional shutdown cases

## Prototype Hooks

- implement an AIS silence-risk service for the COP event pipeline
- convert predicted-but-missing AIS messages into semantic events such as suspected dark activity
- fuse AIS silence anomalies with satellite imagery, RF detections, weather, and vessel history
- use model output as a confidence-weighted track annotation during denied-network operations
- cache recent trajectory context locally so edge nodes can flag suspicious gaps without continuous reachback
- surface anomaly explanations as expected reception versus actual absence

## Pitch Evidence

- Shows that missing AIS can be operationalized as a detection feature for illicit or deceptive behavior
- Demonstrates relevance to open-sea surveillance where direct observation is sparse
- Uses real operational-scale satellite AIS data rather than only synthetic examples
- Claims throughput suitable for national or regional maritime monitoring
- Validates against known shutdown findings, supporting use as evidence for semantic COP alerts

## Limitations / Risks

- Only abstract-level detail is available here, so exact model design, thresholds, and evaluation metrics are unknown
- Intentional shutdown is difficult to distinguish from satellite geometry, protocol limits, weather, or reception failures
- Validation appears based on rediscovering known cases rather than a fully labeled ground-truth benchmark
- Model may depend heavily on historical reception patterns and satellite constellation characteristics
- False positives could burden operators if anomaly explanations and confidence scoring are weak

## Confidence

medium
