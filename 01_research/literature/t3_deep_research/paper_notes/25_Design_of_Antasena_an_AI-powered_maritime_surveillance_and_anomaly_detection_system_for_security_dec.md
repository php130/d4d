# Design of Antasena: an AI-powered maritime surveillance and anomaly detection system for security decision support

## Metadata

- Year: 2026
- URL: https://doi.org/10.11591/ijai.v15.i1.pp269-288
- DOI: 10.11591/ijai.v15.i1.pp269-288
- Read status: partial_text

## One-line Takeaway

Antasena offers a concrete maritime COP pattern: fuse AIS-derived vessel behavior features with contextual layers, run interpretable anomaly detection, and surface prioritized alerts through an operator dashboard.

## D4D Relevance

Highly relevant as a reference architecture for a T3 semantic COP: instead of moving heavy raw feeds over denied or degraded networks, edge nodes can convert AIS/radar/satellite observations into compact semantic events such as vessel identity, kinematic anomaly, restricted-zone violation, confidence, explanation, and recommended priority.

## Key Concepts

- Maritime domain awareness
- AIS-based anomaly detection
- Random forest operational model
- XGBoost and decision tree benchmarking
- Lagged trajectory feature engineering
- Human-in-the-loop validation
- Explainable AI using feature importance and SHAP
- Multi-source maritime data fusion
- Conservation impact scoring
- Real-time alerting dashboard

## Input Data

- AIS records with MMSI, latitude, longitude, speed, course over ground, draught, and timestamp
- Approximately 24,565 AIS records from Indonesian waters collected June 22 to September 22, 2023
- Cargo and tanker vessel tracks
- Planned or conceptual SAR satellite imagery
- Planned coastal radar inputs
- Environmental and conservation layers such as marine protected areas, pollution risk, and biodiversity sensitivity

## Methods Or Architecture

- ADDIE framework for system design and evaluation
- AIS cleaning, interpolation, outlier filtering, normalization, and duplicate removal
- Lag features over five time steps for latitude, longitude, course, speed, and draught
- Supervised anomaly detection using decision tree, random forest, and XGBoost
- Grid-search hyperparameter tuning with cross-validation
- Streaming-style workflow: ingest, preprocess, infer, alert, visualize, operator feedback
- Model comparison across detection performance, robustness, interpretability, latency, scalability, and adaptability
- Explainability through feature importance and planned SHAP summaries

## Outputs / Metrics

- Anomaly alerts for suspicious vessel behavior
- Dashboard visualization of vessel tracks and flagged events
- Reported random forest accuracy of 95.3 percent
- Reported precision of 94.7 percent and recall of 94.2 percent
- Reported ROC-AUC of 96.8 percent
- Cross-domain robustness claims for unseen maritime regions
- Ablation claim that contextual and environmental features materially improve F1-score
- Conservation impact score for anomalies near sensitive ecological areas

## Prototype Hooks

- Represent each contact as a compact semantic object: vessel_id, position, speed, course, behavior_label, anomaly_score, explanation, timestamp, and priority
- Use RF-style feature importance or SHAP-like reason codes to make alerts transmissible and auditable over low-bandwidth links
- Create edge inference nodes that emit only anomaly deltas and summarized tracks when the network is denied
- Add a human validation field so watchstanders can confirm, downgrade, or correct alerts for model retraining
- Fuse AIS with radar or satellite detections to label possible dark vessels when AIS disappears
- Use conservation or restricted-zone layers as mission-context overlays for prioritization
- Benchmark model choices not only by accuracy but by latency, compute footprint, interpretability, and bandwidth cost

## Pitch Evidence

- The paper reports strong anomaly detection performance, with RF slightly outperforming XGBoost and decision trees across accuracy, precision, recall, and ROC-AUC
- It validates a dashboard-centered workflow that maps directly to maritime security decision support
- It argues that interpretable ensemble models are operationally attractive when compute and accountability matter
- It includes a feedback loop where operators can validate predictions, supporting trusted human-machine teaming
- It frames multi-source fusion as necessary for detecting dark vessels and improving maritime situational awareness
- It explicitly connects anomaly detection to prioritization, conservation zones, and operational field use by maritime authorities

## Limitations / Risks

- The provided text emphasizes AIS-based pilots while SAR, radar, and automated multi-source ingestion appear partly future or under development
- The dataset is regional and relatively small, so generalization to other theaters or adversarial behavior may be limited
- Denied-network operation is not the paper's focus; resilience, store-and-forward behavior, compression, and tactical message formats must be designed separately
- Reported performance may depend on labeling quality and class balance handling
- Deep spatio-temporal models may outperform ensembles for complex trajectories but require more compute and data
- False positives could trigger unnecessary enforcement unless human review and audit trails are maintained
- AIS spoofing, silence, jamming, and deceptive tracks require additional trust scoring beyond the described model

## Confidence

medium
