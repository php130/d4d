# From SLAM to Situational Awareness: Challenges and Survey

## Metadata

- Year: 2023
- URL: https://doi.org/10.3390/s23104849
- DOI: 10.3390/s23104849
- Read status: abstract_only

## One-line Takeaway

Robotic situational awareness needs to move beyond isolated sensing, SLAM, and fusion modules toward semantic situation graphs that connect perception, reasoning, and action.

## D4D Relevance

The paper supports a T3 semantic COP architecture by framing COP as more than a map: it should integrate observations, state estimates, semantic entities, relationships, uncertainty, and mission context into a machine-reasonable situational graph. For resilient maritime COP over denied networks, this points to compact graph updates rather than raw sensor feeds, enabling degraded but meaningful shared awareness when bandwidth or connectivity is limited.

## Key Concepts

- situational awareness
- SLAM
- sensor fusion
- state estimation
- spatial perception
- semantic mapping
- scene graph
- situational graph
- robotic autonomy
- AI and deep learning for perception

## Input Data

- mobile robot sensor observations
- spatial perception outputs
- state estimates
- SLAM maps
- semantic detections
- environmental context inferred from perception modules

## Methods Or Architecture

- survey of robotics algorithms relevant to situational awareness
- conceptual decomposition of robotic situational awareness components
- integration of fragmented perception and comprehension algorithms
- situational graph as a generalized scene graph
- linkage between sensing, reasoning, decision-making, and execution

## Outputs / Metrics

- taxonomy of situational awareness components
- identified limitations of current robotics algorithms
- conceptual S-Graph representation for connected situational understanding
- research directions for real-world autonomous situational awareness

## Prototype Hooks

- represent maritime COP entities as nodes: vessels, sensors, ports, hazards, tracks, zones, missions
- encode relationships as graph edges: proximity, intent, threat, custody, communication availability, confidence
- send graph deltas over denied or intermittent networks instead of raw data streams
- attach provenance, timestamp, confidence, and degradation state to each COP fact
- use S-Graph-style abstraction to fuse AIS, radar, EO/IR, acoustic, HUMINT, and operator reports into a semantic COP layer

## Pitch Evidence

- Situational awareness has established value in military and aerospace domains, matching the COP problem space.
- The paper argues that autonomy requires integrated environmental understanding, not isolated sensing or mapping modules.
- S-Graphs provide a plausible structure for connecting fragmented perception outputs into a shared semantic operating picture.
- The survey notes that AI and deep learning are helping bridge perception-to-understanding gaps relevant to automated maritime COP enrichment.

## Limitations / Risks

- Only abstract text was available, so detailed methods, evidence, and evaluation metrics could not be verified.
- The paper is robotics-focused, not maritime-specific.
- It appears to be a survey and vision paper rather than a deployable architecture.
- Current algorithms are described as immature and environment-specific, which is a risk for contested maritime settings.
- Deep learning approaches may be brittle under sensor denial, spoofing, domain shift, or limited onboard compute.

## Confidence

medium
