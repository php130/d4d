# S-DOT Drone Public Dataset / Simulator Catalog

- Date: 2026-07-04 KST
- Purpose: candidate public datasets and simulators for S-DOT drone semantic transmission demo validation.

## Use Criteria

Prioritize resources that provide one or more of:

- drone/MAV trajectories
- visual-inertial data
- IMU/GNSS data
- ground truth poses
- adverse weather / lighting
- simulation environments
- aggressive flight dynamics
- sensor modalities usable for edge semantic event demos

Do not use resources to infer real military routes or operational EW behavior.

## Candidate Resources

| Resource | Type | Why Relevant | Candidate Use |
|---|---|---|---|
| EuRoC MAV Dataset | Visual-inertial MAV dataset | Stereo images, synchronized IMU, motion/structure ground truth | VIO/SLAM baseline, prediction-vs-ground-truth demo |
| UZH-FPV Drone Racing Dataset | Aggressive visual-inertial drone dataset | High-speed FPV trajectories, challenging rotations/accelerations | stress-test state estimation and uncertainty growth |
| TartanAir | Synthetic visual SLAM dataset | Photo-realistic simulated environments, weather, moving objects, multimodal labels | simulation-based raw observation source and weather/context cases |
| Mid-Air | Synthetic low-altitude drone dataset | drone flight records, climate variants, large frame count | adverse weather/visual odometry scenario data |
| Blackbird UAV Dataset | Aggressive UAV perception dataset | visual-inertial navigation, 3D reconstruction, depth estimation | aggressive maneuver and high-speed state-estimation cases |
| Zurich Urban MAV Dataset | Urban low-altitude MAV dataset | high-resolution aerial images, GPS/IMU, street-view, ground truth | urban canyon / low-altitude context demo |
| MUN-FRL VIL Dataset | Visual-inertial-LiDAR aerial dataset | camera, LiDAR, IMU, RTK GNSS on drone/helicopter platforms | multimodal sensor fusion and ground-truth comparisons |
| AirSim | Open-source drone/vehicle simulator | realistic Unreal-based drone simulation, SITL/HITL support | generate synthetic raw feeds and 3D sim scenarios |
| PX4 SITL + Gazebo | Flight controller simulation | PX4 software-in-the-loop with Gazebo, vehicle simulation | future control-loop / telemetry simulation |

## Recommended v0.6 Use

For the immediate hackathon demo, do not ingest large datasets yet. Use them as validation references and visual/algorithm inspiration.

Recommended sequence:

1. Use the current synthetic v0.6 dataset for the first 3D demo.
2. Use EuRoC or UZH-FPV as a later validation dataset for VIO/IMU trajectory logic.
3. Use TartanAir or Mid-Air for weather/visual-condition variation.
4. Use AirSim or PX4/Gazebo only if there is enough time to generate controlled synthetic telemetry.

## Source Links

- EuRoC MAV Dataset: https://projects.asl.ethz.ch/datasets/euroc-mav/
- UZH-FPV Dataset: https://fpv.ifi.uzh.ch/
- TartanAir Dataset: https://theairlab.org/tartanair-dataset/
- TartanAir docs: https://tartanair.org/
- AirSim: https://github.com/microsoft/AirSim
- AirSim docs: https://microsoft.github.io/AirSim/
- Zurich Urban MAV Dataset: https://rpg.ifi.uzh.ch/zurichmavdataset.html
- Mid-Air Dataset: https://midair.ulg.ac.be/
- Blackbird Dataset GitHub: https://github.com/mit-aera/Blackbird-Dataset
- PX4 Gazebo Simulation: https://docs.px4.io/main/en/sim_gazebo_gz/index
- PX4 Gazebo Classic: https://docs.px4.io/main/en/sim_gazebo_classic/
- MUN-FRL VIL Dataset: https://mun-frl-vil-dataset.readthedocs.io/

