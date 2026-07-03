# Wireless End-to-End Image Transmission System Using Semantic Communications

## Metadata

- Year: 2023
- URL: https://doi.org/10.1109/access.2023.3266656
- DOI: 10.1109/access.2023.3266656
- Read status: abstract_only

## One-line Takeaway

Send compact semantic image representations instead of full pixels, then reconstruct useful visuals at the receiver using a shared knowledge base and generative decoder.

## D4D Relevance

Directly supports a T3 semantic COP concept: maritime platforms could transmit object classes, masks, tracks, and scene state over degraded links rather than raw imagery, preserving operational meaning when bandwidth is denied or unreliable.

## Key Concepts

- semantic communications
- semantic segmentation as source representation
- shared transmitter-receiver knowledge base
- receiver-side GAN reconstruction
- bandwidth-efficient multimedia transmission
- channel distortion effects
- quantization noise

## Input Data

- images
- semantic segmentation maps
- COCO-Stuff dataset
- physical channel impairments
- quantized semantic representations

## Methods Or Architecture

- transmitter performs semantic segmentation
- segmentation map is transmitted through the channel instead of full image data
- receiver uses a pre-trained GAN to reconstruct realistic imagery from semantic labels
- encoder and decoder are trained against a common dataset/knowledge base
- experiments consider physical channel distortion and quantization noise

## Outputs / Metrics

- bandwidth/resource savings versus conventional image transmission
- quality of reconstructed realistic image
- impact of channel distortion on semantic transmission
- impact of quantization noise on reconstruction

## Prototype Hooks

- encode maritime sensor frames as semantic masks, object labels, and geometry before transmission
- use a shared maritime ontology/knowledge base across ships, UAVs, and command nodes
- reconstruct COP visuals at the receiver from compact semantic packets
- prioritize mission-critical classes such as vessels, hazards, routes, and contacts under link degradation
- flag reconstructed imagery as synthesized so operators distinguish observed semantics from generated pixels

## Pitch Evidence

- The paper reports large bandwidth savings when transmitting segmentation maps rather than ground-truth images.
- It demonstrates an end-to-end semantic image transmission pattern that maps well to denied-network COP updates.
- Its common-knowledge-base framing supports coalition nodes interpreting compact semantic messages consistently.
- Its channel and quantization focus is relevant to contested maritime communications.

## Limitations / Risks

- Only abstract-level text was available for this review.
- COCO-Stuff is not maritime-specific, so domain adaptation would be required.
- GAN reconstruction can hallucinate visual details that were not actually transmitted.
- Segmentation errors at the transmitter could become authoritative-looking COP errors.
- The abstract does not provide detailed quantitative results, latency, compute cost, or operational validation.

## Confidence

medium
