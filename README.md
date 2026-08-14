# Surfcam

<!-- One-line tagline: what it is and who it's for. -->

<!-- Optional: badges (build status, license, python version, etc.) -->

<!-- Optional: hero image, GIF, or link to a demo video/reel. -->
 (this part got deleted when I forgot to save)
## Overview

<!-- What problem this solves, who it's for, and why it exists. 2-4 sentences. -->
(this part also got deleted but this is the best i can recall of what i wrote)
Surfcam is my project with the goal of creating an open-source, autonomous activity tracking setup for surfers to leave alone on the beach while they go about catching waves. I aim to address certain reported issues with existing surf tracking solutions, such as the SoloShot3 (link needed), as well as provide people the means to recreate the project on their own with their own cameras. Existing products on the market, such as the SoloShot3, have had issues with GPS location drifting and annoying calibration, which I believe can be avoided in this case.
## Features
(this part also got deleted and i will revisit it later)
<!-- Bullet list of what it actually does today. -->

## Demo

<!-- Screenshots, GIFs, or embedded/linked video of detection + tracking in action. -->

## How It Works

The current prototype loop is split across two machines: a Raspberry Pi 3B on the tripod, and a desktop/laptop doing the CV computation and calculating servo movements

1. **Capture.** The Pi grabs frames from a Logitech C270 webcam, JPEG-encodes them, and pushes them over WiFi via raw UDP. Capture and send run on separate threads on the Pi so a slow encode never blocks the next frame grab. On the laptop version of the script, the webcam is connected directly to the laptop, eliminating the streaming over wifi aspect and reducing latency by about 150-200ms.
2. **Detect.** The desktop decodes the stream and runs a YOLO26 model over each frame, currently only using the generic COCO-pretrained (`person` class). However, a surf-specific fine-tuned (`surfai_v9`, `doube2`, trained on harvested surf footage) arer WIP but aren't finished or tested in real surf conditions yet.
3. **Track.** Detections are fed through BoT-SORT (Bag of Tricks),  (`model.track(persist=True)`) so the same surfer keeps the same track ID frame to frame instead of being re-detected from scratch. On the laptop version of the script, persistence is toggled off to save compute power and increase FPS. This may change in the future. A confidence floor plus an N-frame hold streak determines which detected objects are eligible to be locked onto, filtering out one-off flicker false positives (birds, spray, glare).
4. **Pick a target.** Among eligible tracks, the largest bounding box wins, a temporary alternative to "closest/most prominent surfer in frame" or determining a specific surfer with GPS.
5. **Aim.** The target's pixel offset from frame center converts to a pan/tilt angle delta (deg-per-pixel, tuned to the C270's FOV), then runs through a spring-follow controller instead of direct proportional control, which damps overshoot and reduuces jitter by not snapping straight to the target. Max angular speed per axis is capped by a tunable sigmoid speed curve, so the servo eases in near center and hits full speed toward the frame edge.
6. **Move.** Pan/tilt angle commands go back to the Pi as a fixed 8-byte UDP payload (two floats, no header), where the Pi drives the SG90 pan-tilt servos, clamped to a safe angle range.

This is the prototype loop, built to validate detection/tracking/control on cheaper hardware and what I have on-hand before committing to the target build.

## Tech Stack

**Detection & tracking**
- Using [Ultralytics](https://github.com/ultralytics) YOLO26 for detection, `yolo26n.pt` is the current default, with older YOLOv8 checkpoints and `yolo26s.pt`, `yolo26m.pt`, the small and medium versions kept alongside for A/B comparison
- BoT-SORT for multi-frame tracking (`model.track(persist=True)`), run with global motion compensation disabled (improved performance from ~10 to ~16 fps)
- OpenCV (`cv2`) for capture, JPEG encode/decode, and the debug overlay window

**Control**
- A spring-follow controller (critically-damped step) instead of a PID loop, converting pixel offset into pan/tilt angle
- (Phased out) A closed-form logistic-sigmoid speed-cap curve (`speed_curve.py`), live-tunable via an OpenCV trackbar UI, saved to `tracking_tuning.json`
- Pi-side command interpolation — a fixed 50Hz slew-rate loop smooths the servo's discrete, lower-rate UDP updates into continuous motion instead of visibly stepping

**Networking**
- Raw UDP sockets (Python `socket`/`struct`) for both the video stream and servo commands
- Servo commands are a fixed 8-byte payload (two big-endian float32s) with no headers
- Threaded producer/consumer split on both ends (capture vs. encode+send on the Pi; receive vs. detect+track on the desktop/laptop)

**Dataset & training tooling**
- Roboflow for dataset hosting/annotation;
- `ultralytics`'s training API for fine-tuning the surf-specific model lineages (`surfai_v9`, `doube2`)

**Platform**
- Python end-to-end — Windows desktop (CUDA GPU for inference) and Raspberry Pi OS
- `pygrabber` for DirectShow webcam enumeration on the Windows side

## Hardware

**Prototype (current)**
- Raspberry Pi 3B with full-size USB, built-in WiFi; streams video and drives servos directly
- Logitech C270 webcam — 720p/30fps, USB, 60 degree FOV
- SG90 micro servo (tilt) + MG90 micro servo (pan) (MG90 has metal gears)
- ThtRht nylon anti-vibration pan-tilt bracket, webcam mounted via hot glue (amazon link needed)
- Servos wired to Pi GPIO with hardware PWM (`rpi_hardware_pwm`): pan on GPIO 17, tilt on GPIO 27 for later reference
- Wired servos into an extension cord for field power (need to check if they can draw power directly from thhe pi)
- Windows desktop/laptop with a CUDA GPU does all inference for the system wirelessly

**Target build**
- Compute: Jetson Orin Nano, or a Raspberry Pi 5 + Hailo-8L, currently the cost/power favorite, see [research.md](research.md#prototype-findings--full-scale-deployment-considerations-july-2026)
- Camera: Sony a6700 (26MP APS-C, 759-point phase-detect AF, 4K/60p) controlled over USB via Sony's Camera Remote SDK, paired with a Sony E 70-350mm f/4.5-6.3 G OSS lens (This is what Nathan owns)
- Pan-tilt: brushless gimbal motors with encoder feedback and closed-loop position control [DigitalBird3 4 Axis pan-tilt kit](https://digital-bird-motion-control.myshopify.com/products/db3-wifi-visca-pan-tilt-head)
- Power: ~100Wh LiFePO4 battery, targeting 4-5hr of unattended runtime

## Model & Training

<!-- Dataset(s), model lineage/versions, training approach, evaluation metrics. -->

## Results

<!-- Quantitative results (accuracy, FPS, latency) and/or qualitative before/after comparisons. -->

## Project Status & Roadmap

<!-- What's done, what's in progress, what's next. -->

## Repository Structure

<!-- Brief map of top-level folders/files and what lives where. -->

## Getting Started

<!-- Prerequisites, installation, and how to run it. -->

## Lessons Learned

<!-- Notable challenges, dead ends, and what you'd do differently. -->

## Acknowledgments & Sources

<!-- Research references, datasets, libraries, and inspirations. -->

## Contact

<!-- How to reach you / links to portfolio, LinkedIn, etc. -->
