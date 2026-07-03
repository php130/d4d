# Semantic Edge Computing and Semantic Communications in 6G Networks: A Unifying Survey and Research Challenges

## Metadata

- Year: 2024
- URL: http://arxiv.org/abs/2411.18199v3
- DOI: 10.1016/j.comnet.2025.111531
- Read status: partial_text

## One-line Takeaway

The survey frames semantic communications and split edge AI as one design space: send task-relevant meanings or latent features, not raw bits, while adapting computation and transmission to device and channel constraints.

## D4D Relevance

Highly relevant to a Resilient Maritime COP over Denied Networks because it gives the architectural vocabulary for a T3 semantic COP: vessels, UAVs, buoys, and command nodes can exchange compressed mission semantics, latent detections, tracks, alerts, and task outputs instead of raw ISR streams, with adaptive partitioning and channel-aware coding for low-bandwidth, intermittent, or degraded links.

## Key Concepts

- Semantic communications
- Semantic edge computing
- Task-level semantic communication
- Split computing
- Collaborative inference
- DNN partitioning
- Latent representation transmission
- Semantic compression
- Joint source-channel coding
- Knowledge-base mismatch
- Resource-aware inference
- Channel-adaptive transmission

## Input Data

- Raw sensor streams such as imagery, video, RF, CSI, or beamforming feedback
- Intermediate DNN latent representations
- Channel state and wireless impairment models
- Device compute, memory, battery, and bandwidth constraints
- Shared or local knowledge bases at transmitter and receiver
- Task requirements such as detection, classification, tracking, or decision support

## Methods Or Architecture

- DNN encoder-decoder systems trained end-to-end across a channel model
- Split DNN inference with head models on edge devices and tail models on servers or peer nodes
- Sequential and DAG-based model partitioning
- Static and dynamic resource-aware partitioning using optimization, heuristic search, linear programming, or DRL
- Semantic compression through bottleneck layers, dimensionality reduction, pruning, quantization, entropy coding, NAS, and rate-distortion training
- Physical-layer semantic communication that incorporates channel distortion during model training
- Application-level task optimization using task accuracy, semantic similarity, latency, energy, and rate objectives

## Outputs / Metrics

- End-to-end inference latency
- Communication rate or transmitted feature size
- Energy consumption
- Task accuracy or inference performance
- Semantic similarity or reconstruction quality
- Throughput for multi-user or multi-task systems
- Age of information and value of information
- Resource utilization under changing compute and network conditions

## Prototype Hooks

- Build a COP data plane that transmits semantic objects such as tracks, anomalies, intent cues, confidence, and compressed latent features rather than raw feeds by default
- Prototype split inference where shipboard or unmanned platforms run early perception layers and forward compact features to a T3 fusion node when links permit
- Add channel-aware semantic compression that reduces payload detail under denied or congested links while preserving mission-critical detections
- Use value-of-information and age-of-information scoring to prioritize maritime COP updates
- Create a shared operational knowledge base to reduce semantic mismatch across units
- Implement dynamic model partitioning so workloads move between sensor node, vessel edge server, and command node based on bandwidth, latency, and power
- Evaluate against baselines that send raw video, full-resolution imagery, or conventional feature messages

## Pitch Evidence

- The paper argues that semantic communication improves efficiency by transmitting meaning or task-relevant content rather than full bit-level representations
- It explains that semantic edge computing can lower latency versus raw-data offload by sending compressed intermediate features
- It identifies task-level semantic communication as directly evaluated by mission-style effectiveness metrics, not just bit accuracy
- It connects SEC and SemCom across system, application, and physical layers, which maps well to a contested maritime network stack
- It highlights dynamic partitioning and adaptive compression as responses to changing bandwidth, compute, and channel conditions

## Limitations / Risks

- Survey paper, not a deployable maritime system or benchmark
- Most examples are 6G, image classification, sensing, or generic edge AI rather than naval COP workflows
- Deep semantic encoders may be expensive for small maritime edge devices unless carefully partitioned
- Semantic systems depend on shared knowledge bases, so semantic mismatch between coalition or legacy nodes is a real risk
- Model robustness under jamming, deception, adversarial inputs, and cyber compromise is not fully solved in the provided text
- Interoperability with existing tactical data links and COP schemas would require an additional translation layer

## Confidence

high
