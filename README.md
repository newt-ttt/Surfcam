# 🏄 Surfcam

Open-source, autonomous pan-tilt camera rig that detects and tracks a surfer in the water, so you can film a surfing session hands-free.

<!-- Hero image/GIF/demo link goes here once there's a clip worth leading with - a media/detection_videos clip is a good candidate. -->

## Overview

<!-- What problem this solves, who it's for, and why it exists. 2-4 sentences. -->
STATUS: Proof-of-concept

Surfcam is a project with the goal of creating an open-source, autonomous activity tracking setup for surfers to leave alone on the beach while they go about catching waves. It aims to address certain customer-reported issues with existing surf tracking solutions, such as the [SoloShot3](https://soloshot.com/collections/soloshot3), as well as provide users with the documentation to recreate this project on their own. Existing products on the market have had issues with GPS location drifting and annoying calibration, which should to be remedied in the final build.

The proof-of-concept goal is to ensure all components of this project broadly work together before committing to more expensive components time-wise and finance-wise. The current setup effectively tracks a human visually at ~25m range in low resolution and no physical zoom, and follows them adequately given the avaiilable servos. The next step will be integrating a GPS tag on the target & Low power radio communication (LoRa) between the tag and base station (camera), to allow for a more precise system for aiming at a target at range, supplementing pure computer-vision.
## Features

- Real-time person/surfer detection with CV
- Automatic target selection
- Pan/tilt servo control for aiming
- Split-machine architecture over UDP: Raspberry Pi handles capture & servo drive, desktop/laptop handles detection/tracking/control
- Debug overlay window for visualizing detection and live tracking

<!-- Screenshots, GIFs, or embedded/linked video of detection + tracking in action. -->

## How It Works

The current prototype loop is split across two machines: a Raspberry Pi 3B on the tripod, and a desktop/laptop doing the CV computation and calculating servo movements
```mermaid
graph LR;
  Capture(Video Capture) --> Detect(Detect & Track) --> Pick(Pick Target) --> Aim --> Move(Execute Movement) --> Capture;
```
1. **Video Capture.** The Pi grabs frames from a Logitech C270 webcam, JPEG-encodes them, and pushes them over WiFi via raw UDP. Capture and send run on separate threads on the Pi so a slow encode never blocks the next frame grab. On the laptop version of the script, the webcam is connected directly to the laptop, eliminating the streaming over wifi aspect and reducing latency by about 150-200ms.
2. **Detect.** The desktop decodes the stream and runs a YOLO26 model over each frame, currently only using the generic COCO-pretrained (`person` class). However, a surf-specific fine-tuned (`surfai_v9`, `doube2`, trained on harvested surf footage) are WIP but aren't finished or tested in real surf conditions yet.
3. **Track.** Detections are fed through BoT-SORT (Bag of Tricks),  (`model.track(persist=True)`) so the same surfer keeps the same track ID frame to frame instead of being re-detected from scratch. On the laptop version of the script, persistence is toggled off to save compute power and increase FPS. This may change in the future. A confidence floor plus an N-frame hold streak determines which detected objects are eligible to be locked onto, filtering out one-off flicker false positives (birds, spray, glare).
4. **Pick a target.** Among eligible tracked objects, the largest bounding box is chosen, a temporary alternative to "closest/most prominent surfer in frame" or determining a specific surfer with GPS.
5. **Aim.** The target's pixel offset from the center of the frame converts to a pan/tilt angle delta, then runs through a spring-follow controller instead of direct proportional control, which damps overshoot and reduuces jitter by not snapping straight to the target. Max angular speed per axis is capped by a tunable sigmoid speed curve, so the servo eases in near center and hits full speed toward the frame edge.
6. **Execute Movement.** Pan/tilt angle commands go back to the Pi as a fixed 8-byte UDP payload (two floats, no header), where the Pi drives the SG90 pan-tilt servos, clamped to a safe angle range.

This is the prototype/proof-of-concept loop, built to validate detection/tracking/control on cheaper hardware and is available on-hand before committing to the target build.

## Hardware

**Proof-of-concept prototype**
- Raspberry Pi 3B; streams video and drives servos directly
- Logitech C270 webcam - 720p/30fps with 60 degree FOV (low resolution)
- SG90 micro servo (tilt) + MG90 micro servo (pan)
- ThtRht nylon anti-vibration pan-tilt bracket, webcam mounted via hot glue. Product page link [here](https://www.amazon.com/dp/B0CL9CDKQV?ref=ppx_yo2ov_dt_b_fed_asin_title)
- Servos wired to Pi GPIO with hardware PWM
- Field power comes from the laptop running the main script.
- Windows desktop/laptop with a CUDA GPU does all inference for the system wirelessly

**Target build**
- Compute: Jetson Orin Nano, or a Raspberry Pi 5 + Hailo-8L, currently the cost/power favorite, see [research.md](research.md#prototype-findings--full-scale-deployment-considerations-july-2026)
- Camera: Sony a6700 (26MP APS-C, 759-point phase-detect AF, 4K/60p) controlled over USB via Sony's Camera Remote SDK, paired with a Sony E 70-350mm f/4.5-6.3 G OSS lens 
- Pan-tilt: brushless gimbal motors with encoder feedback and closed-loop position control [DigitalBird3 4 Axis pan-tilt kit](https://digital-bird-motion-control.myshopify.com/products/db3-wifi-visca-pan-tilt-head)
- Power: ~100Wh LiFePO4 battery, targeting 4-5hr of unattended runtime

## Model & Training

All fine-tunes start from Ultralytics' pretrained YOLO26 checkpoints (`n`/`s`/`m`) and are trained 50 epochs at `imgsz=640` via `ultralytics`'s training API, with Roboflow-hosted datasets. `doube2_yolo26s.pt` is the current production weight that was fine-tuned off of 7,800 labeled surfer images.

The latest model does well with detecting and tracking surfers on a wave, but most noticebly struggles when too many objects are in frame, i.e. 100 surfers waiting for a wave, all in frame at once. This shouldn't be an issue when GPS is implemented, allowing for a rough reduction in FOV when the camera zooms in to the approximate location of the tagged surfer.

| Model | Classes | Dataset (train / val images) | Precision | Recall | mAP50 | mAP50-95 |
|---|---|---|---|---|---|---|
| `surfai_v9_yolo26n` | 2 (`surfer`, `Surfer_Riding`) | Surfer-Detection-9 (317 / 90) | 80.9% | 72.6% | 81.9% | 37.0% |
| `surfai_v9_yolo26s` | 2 (`surfer`, `Surfer_Riding`) | Surfer-Detection-9 (317 / 90) | 75.1% | 93.3% | 91.3% | 41.9% |
| `surfai_v9_yolo26m` | 2 (`surfer`, `Surfer_Riding`) | Surfer-Detection-9 (317 / 90) | 80.3% | 79.9% | 83.6% | 41.4% |
| `doube2_yolo26n` | 7 (surfer, surfer_ride, wave + 4 wave-state classes) | surfer_doube2_full (5672 / 1412) | 91.5% | 87.5% | 93.4% | 69.0% |
| `doube2_yolo26s` (production, post-hardneg) | 7 (surfer, surfer_ride, wave + 4 wave-state classes) | surfer_doube2_full (5672 / 1412) | 90.1% | 88.9% | 94.1% | 70.1% |

## Project Status & Roadmap

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'sectionBkgColor': '#faf6ec',
    'sectionBkgColor2': '#f0e6d2',
    'altSectionBkgColor': '#f0e6d2',
    'taskBkgColor': '#cfe0f3',
    'taskBorderColor': '#93b3dd',
    'activeTaskBkgColor': '#ffe0b2',
    'activeTaskBorderColor': '#e0a868',
    'doneTaskBkgColor': '#c3e6cb',
    'doneTaskBorderColor': '#7fb28c',
    'critBkgColor': '#f5c6cb',
    'critBorderColor': '#d98a94',
    'taskTextColor': '#4a4a4a',
    'taskTextOutsideColor': '#ffffff',
    'taskTextLightColor': '#4a4a4a',
    'gridColor': '#e3dcc9',
    'todayLineColor': '#d98a94'
  },
  'gantt': {
    'leftPadding': 150,
    'barHeight': 22,
    'barGap': 6,
    'topPadding': 50
  },
  'themeCSS': '.activeText0, .activeText1, .activeText2, .activeText3 { fill: #ffffff !important; }'
}}%%
gantt
    title Surfcam Roadmap
    dateFormat YYYY-MM-DD
    axisFormat %b %d

    section Research & Planning
    Commercial landscape + hardware architecture research   :done, research, 2026-07-01, 18d

    section Prototype Build
    Pi 3B + C270 + servo bring-up                            :done, bringup, after research, 3d
    Video-over-WiFi UDP streaming                             :done, streaming, 2026-07-22, 1d
    Live detection/tracking + spring-follow control loop       :done, controlloop, after streaming, 17d

    section Surf-Specific Models
    surfai_v9 fine-tune (n/s/m)                               :done, surfai, 2026-08-09, 2d
    doube2 fine-tune + hard-negative retrain                  :done, doube2, 2026-08-11, 1d
    Tracker bug fix (GMC) + replay validation                 :done, gmcfix, 2026-08-15, 2d
    Repo cleanup + docs                                        :active, cleanup, 2026-08-17, 1d

    section Next Up
    GPS tag + low-power radio telemetry                       :gps, after cleanup, 21d
    Target hardware migration (Jetson/Hailo, a6700, gimbal)    :target, after gps, 28d
```

Dates for completed work are real; the "Next Up" durations are rough placeholders, not committed timelines. Current focus: Getting GPS integrated with the system to test aiming accuracy at range with pure GPS aiming, without CV for now.

<!--## Results-->

<!-- Quantitative results (accuracy, FPS, latency) and/or qualitative before/after comparisons. -->

<!--## Getting Started -->

<!-- Prerequisites, installation, and how to run it. -->

<!--## Lessons Learned -->

<!-- Notable challenges, dead ends, and what you'd do differently. -->

<!--## Acknowledgments & Sources -->

<!-- Research references, datasets, libraries, and inspirations. -->

<!--## Contact -->

<!-- How to reach you / links to portfolio, LinkedIn, etc. -->
