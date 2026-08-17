# Automated Surf Tracking Camera - Research

> Research compiled April 2026

## Table of Contents

- [Problem Statement](#problem-statement)
- [Existing Commercial Products](#existing-commercial-products)
- [Emerging & Adjacent Products](#emerging--adjacent-products)
- [Tracking Technologies](#tracking-technologies)
- [Computer Vision & AI Approaches](#computer-vision--ai-approaches)
- [Hardware Considerations](#hardware-considerations)
- [Sony a6700 as Camera Platform](#sony-a6700-as-camera-platform)
- [Pain Points in Existing Solutions](#pain-points-in-existing-solutions)
- [Opportunities for Improvement](#opportunities-for-improvement)
- [Recommended Architecture](#recommended-architecture)
- [Prototyping on Desktop Hardware](#prototyping-on-desktop-hardware)
- [Prototype Findings & Full-Scale Deployment Considerations (July 2026)](#prototype-findings--full-scale-deployment-considerations-july-2026)
  - [UWB as a GPS Alternative for Coarse Tracking](#uwb-as-a-gps-alternative-for-coarse-tracking)
- [Sources](#sources)
- [Prototype Implementation & Change Log →](prototype.md)

---

## Problem Statement

A surfer wants to leave an unmanned camera on a tripod on the beach that autonomously tracks and records them during a session. The system must:

- Mount to a standard tripod
- Operate unattended for 2+ hours
- Track a surfer at distances of 100-2000+ feet from shore
- Produce usable, watchable footage (not just surveillance-quality)
- Be minimally intrusive to the surfer's experience (ideally no wearable, or a small unobtrusive one)
- Withstand outdoor beach conditions (wind, sand, salt spray, sun)

---

## Existing Commercial Products

### SOLOSHOT3 (soloshot.com)

The current market leader for personal surf filming. Still in business as of 2026, headquartered in San Antonio, TX.

| Spec | Value |
|------|-------|
| Tracking method | GPS wearable tag (waterproof) |
| Range | Up to 2,000 ft |
| Camera | Optic65 (65x optical zoom, up to 4K) |
| Battery life | 5+ hours |
| Tripod | Proprietary (extends to ~6 ft) |
| Price | ~$500-900 (full bundle) |
| Storage | 128 GB microSD (proprietary verified cards recommended) |

**How it works:** A waterproof GPS tag is worn by the surfer (armband, ankle, or attached to gear). The base station receives GPS coordinates from the tag and mechanically pans/tilts/zooms the camera to keep the tag-wearer centered.

**Strengths:**
- Purpose-built for surf and outdoor action sports
- Long range (2,000 ft) covers most lineups
- Long battery life for full sessions
- 65x optical zoom provides tight framing at distance
- Automatic zoom adjustment to keep subject framed
- Ships fully assembled in a carry case

**Weaknesses (from user reviews):**
- GPS tag loses signal when subfer dives/falls underwater, sometimes doesn't reacquire
- Footage becomes shaky in winds over 20 knots (common at the beach)
- Camera can get stuck in "Calibrating" mode
- Tracking can drift - filming ground or areas 30 yards off-target
- Requires open area for calibration (cliffs/structures cause failures)
- Batteries are internally sealed - unit becomes disposable after ~3 years
- No external power option
- Customer support widely reported as poor/unresponsive
- Requires Soloshot-specific microSD cards
- Proprietary tripod screw may not fit all standard tripods

### PIXIO by Move'N See

Originally designed for equestrian/sports coaching, usable outdoors.

| Spec | Value |
|------|-------|
| Tracking method | RF beacons (3 placed around area) + wearable tag |
| Range | 330 ft (100 m) |
| Camera | Supports external cameras up to 5 lbs (DSLR, action cam) |
| Rotation | 360 degrees |
| Tilt | Manual only (+-10 degrees) |
| Pan speed | Up to 120 degrees/sec |

**Strengths:**
- Bring-your-own-camera (use a quality DSLR or mirrorless)
- Works indoors and outdoors
- High pan speed

**Weaknesses for surfing:**
- 100 m range is far too short for most surf scenarios
- Requires 3 beacon placements around filming area (impractical on a beach)
- No auto-tilt or auto-zoom
- Not purpose-built for surf

### PIXEM 2 by Move'N See

Smartphone/tablet version of Pixio.

| Spec | Value |
|------|-------|
| Tracking method | RF beacons + wearable watch tag |
| Range | 330 ft (100 m) |
| Camera | Uses smartphone/tablet |
| Auto-zoom | Yes (digital, via app) |

**Weaknesses for surfing:** Same range limitation as PIXIO. Smartphone camera lacks the optical zoom needed for distant surfers.

### XbotGo Chameleon

AI-powered sports camera, primarily targeting team sports (soccer, basketball, etc.).

| Spec | Value |
|------|-------|
| Tracking method | AI computer vision (tagless) |
| Resolution | 4K at 60fps |
| Battery life | 8 hours |
| Cloud storage | 20 GB free |
| Streaming | YouTube, Facebook live |
| Price | ~$400-500 |

**Strengths:**
- Tagless - pure AI tracking, no wearable needed
- Excellent battery life
- Built-in camera with 4K/60fps
- Auto-highlight clip generation
- Can track by jersey number or appearance

**Weaknesses for surfing:**
- Designed for field sports with relatively close subjects
- Lacks the extreme zoom needed for distant surfer tracking
- No weatherproofing against salt spray/sand
- Tracks ~80-85% of action accurately (acceptable for field sports, problematic for surf where you need to catch the wave)
- Not tested/optimized for ocean environments

---

## Emerging & Adjacent Products

### RocX by Farseer (Kickstarter, December 2025)

Built by former DJI engineers (Mavic Pro, Osmo Pocket, Ronin).

| Spec | Value |
|------|-------|
| Zoom | 50x optical/digital hybrid (35mm-1,750mm equiv.) |
| Resolution | 4K photo, 4K/30fps or 1080p/60fps video |
| Sensor | 1/2.8" |
| Battery | 6 hours |
| Weight | 2.2 lbs (gimbal), 1.1 lbs (handle) |
| Stabilization | 2-axis |
| Price | $199 (camera only), $699 (camera + gimbal) |

**Relevance:** The 50x zoom and AI auto-tracking make this potentially interesting as the camera component of a surf tracking system, though it's not designed as a standalone tracking solution.

### Flowstate (Wave Pool AI)

AI-powered multi-camera system deployed at wave pools (Revel Surf, Atlantic Park).

| Spec | Value |
|------|-------|
| Tracking method | AI computer vision - tagless, no wearables |
| Camera | Cinema-grade, fixed position |
| Tracking | Digital pan/zoom within 4K frame |
| Identification | Movement pattern recognition (no RFID, no tags) |

**How it works:** Fixed high-resolution cameras capture a wide field of view. AI performs digital pan-and-zoom within the frame, tracking individual surfers by their movement patterns. The system was trained on millions of wave pool rides. It can identify specific maneuvers (snaps, cutbacks, barrels).

**Key insight:** This proves tagless surfer tracking via AI is viable - but Flowstate operates in a controlled wave pool environment with known wave patterns, consistent lighting, and close distances. Open ocean is significantly harder.

### Surfline Coastal Intelligence

Surfline's stationary beach cameras use ML to:
- Track individual surfers in the water
- Monitor crowd density
- Detect wave height, direction, and quality
- Track currents and surfer drift

This is observation/analytics (not personal filming) but demonstrates that AI can reliably detect and track surfers in real ocean conditions from fixed cameras.

### OBSBOT Tiny/Tail Series

AI-powered PTZ webcams with gesture control and auto-tracking.

| Spec | Value |
|------|-------|
| Resolution | Up to 4K |
| Tracking | AI (face/body/gesture recognition) |
| Range | Indoor/short-range outdoor |

**Weaknesses for surfing:** Designed for indoor/close-range use. No optical zoom for distance. Not weatherproof.

---

## Tracking Technologies

### 1. GPS Tag (used by Soloshot)

**How it works:** Surfer wears a GPS receiver that transmits coordinates to the camera base via radio. Base calculates bearing/elevation and drives servos.

| Pro | Con |
|-----|-----|
| Long range (2000+ ft) | Requires wearing a tag |
| Works regardless of visibility | GPS accuracy is ~3-5 meters (causes jitter at zoom) |
| Not affected by waves/spray obscuring camera | Signal loss when tag submerges |
| Simple tracking algorithm | Tag must be charged and maintained |
| | GPS update rate (~1-10 Hz) can lag fast action |
| | No framing intelligence (centers on GPS point, not the surfer visually) |

### 2. RF Beacon Triangulation (used by Pixio/Pixem)

**How it works:** Multiple beacons placed in the area triangulate a wearable tag's position.

| Pro | Con |
|-----|-----|
| More precise than GPS indoors | Very short range (100 m) |
| Fast update rate | Requires placing multiple beacons |
| | Completely impractical for surf |

### 3. AI Computer Vision (used by XbotGo, Flowstate)

**How it works:** Camera feed is processed by an AI model (typically YOLO-family) that detects and tracks the subject visually.

| Pro | Con |
|-----|-----|
| No wearable required - zero intrusion | Challenging at long range (surfer is tiny in frame) |
| Can frame intelligently (center on visual subject) | Affected by glare, spray, fog, backlighting |
| Can detect maneuvers and generate highlights | Computationally expensive for real-time |
| Can distinguish surfer from others | May lose track in whitewater/wipeouts |
| No signal loss when underwater | Requires training data for ocean conditions |
| | Multiple surfers create association challenges |

### 4. Hybrid: GPS + Computer Vision

**How it works:** GPS provides coarse tracking (which direction to point). CV refines framing within the frame.

| Pro | Con |
|-----|-----|
| GPS handles long-range pointing | Still requires a wearable tag |
| CV handles precise framing | More complex system |
| CV can maintain track during brief GPS dropouts | Higher power consumption |
| Best of both worlds for quality footage | More failure modes |

### 5. Ultra-Wideband (UWB) Tracking

A newer alternative to GPS for wearable tracking with centimeter-level accuracy, but limited to ~200m range - insufficient for surf.

> **Update (July 2026):** The ~200m figure is generic-consumer-hardware, not a hard UWB ceiling - purpose-built modules already demonstrate 500m, and the tag side can be more minimal than a GPS tag. See [UWB as a GPS Alternative](#uwb-as-a-gps-alternative-for-coarse-tracking).

### 6. High-Contrast Visual Marker

Instead of a GPS tag, the surfer wears or attaches a high-contrast visual marker (e.g., bright-colored rashguard, patterned sticker on board) that is easier for CV to detect at distance than a generic person.

| Pro | Con |
|-----|-----|
| Minimally intrusive (just wear a specific color/pattern) | Still requires something from the surfer |
| No electronics to charge or waterproof | Can be confused by other surfers wearing similar colors |
| Works at any range the camera can resolve | Effectiveness depends on lighting conditions |
| Enhances CV tracking reliability significantly | |

---

## Computer Vision & AI Approaches

### Surfer Detection Models

**YOLOv8** is the current state-of-the-art for real-time object detection applicable to surf tracking:
- YOLOv8 Medium: 295 layers, 25.8M parameters
- Can be trained on surf-specific data (Surfline camera footage)
- Training on ~857 labeled images with ~1200 instances produced strong results in ~45 minutes on GPU
- Pre-trained COCO weights provide transfer learning foundation (person class already exists)

**Key challenge:** Models trained on one beach/lighting condition may not generalize well. Morning footage won't prepare the model for afternoon glare. North Shore footage won't prepare it for beach breaks.

### Tracking Pipeline for Surf

A practical surf tracking CV pipeline would need:

1. **Wide-angle detection:** Periodically scan wide FOV to locate the target surfer
2. **Zoom tracking:** Once located, zoom in and use tighter detection/tracking
3. **Kalman filtering:** Smooth servo commands using predicted trajectory
4. **Re-acquisition:** When track is lost (wipeout, whitewater), zoom out, re-detect, zoom back in
5. **Identity persistence:** Distinguish "your" surfer from others in the lineup

### Surfline's Approach

Surfline Labs built a production ML system that:
- Runs a deep learning object detection network on live beach camera feeds
- Couples detection with a tracking system
- Monitors all water users and waves in real-time
- Converts pixel coordinates to map coordinates
- Operates continuously across varying conditions

This validates that real-time surfer detection in open ocean is an engineering problem, not a research problem - it's been solved at scale.

### Compute Hardware for Edge AI

| Platform | YOLO Performance | Power | Cost |
|----------|-----------------|-------|------|
| Raspberry Pi 5 | ~5-10 FPS (YOLOv8n) | 5-15W | $80 |
| NVIDIA Jetson Nano | ~15-25 FPS (YOLOv8n) | 10-15W | $150 |
| NVIDIA Jetson Orin Nano | ~30-60 FPS (YOLOv8n) | 7-15W | $250 |
| Google Coral TPU (USB) | ~30+ FPS (compiled models) | 2-4W | $60 |
| Intel NCS2 (Movidius) | ~15-20 FPS | 1-2.5W | $70 |

For a battery-powered system, the Jetson Orin Nano or a Coral TPU accelerator attached to a Pi offers the best power/performance tradeoff.

> **Update (July 2026):** This table and the Jetson-only recommendation below predate real prototyping data and a 2026 pricing/availability check. See [Prototype Findings & Full-Scale Deployment Considerations](#prototype-findings--full-scale-deployment-considerations-july-2026) for the current picture - notably, Coral is now discontinued, NVIDIA raised Jetson pricing significantly, and a Pi 5 + Hailo-8L is now the leading low-power candidate.

---

## Hardware Considerations

### Pan-Tilt Mechanism

**Servo-based (hobby):**
- SG90 / MG996R servos: cheap ($5-15), 180 degrees, adequate torque for small cameras
- Pros: Simple, cheap, well-documented
- Cons: Limited rotation (180 degrees), jitter, insufficient torque for wind resistance with a zoom camera, no position feedback (open loop)

**Stepper motor-based:**
- NEMA 17 with worm/gear drive
- Pros: Precise positioning, high torque, 360-degree continuous rotation, holds position under load (wind)
- Cons: More complex driver electronics, heavier, more expensive

**Brushless gimbal motors:**
- Used in camera gimbals (DJI Ronin, etc.)
- Pros: Smooth, precise, designed for camera payloads, good vibration damping
- Cons: Require specialized controllers (SimpleBGC, Storm32), higher cost

**Recommendation for surf:** Stepper motors or brushless gimbal motors. Hobby servos will not survive beach wind gusts with a zoom camera mounted. A worm-gear drive provides passive wind resistance (won't backdrive).

### Camera Options

For usable footage at 500-2000 ft, significant optical zoom is essential:

| Camera Type | Zoom | Quality | Weight | Integration |
|-------------|------|---------|--------|-------------|
| Soloshot Optic65 | 65x optical | 4K | Proprietary | Soloshot only |
| Canon PowerShot SX70 HS | 65x optical | 20MP, 4K | 610g | HDMI out, USB |
| Sony RX10 IV | 25x optical | 20MP, 4K | 1095g | HDMI, USB |
| PTZ security camera (48x) | 48x optical | 4K | ~2-3 kg | IP/RTSP |
| Block camera module (e.g., Sony FCB-EV9520L) | 30x optical | 1080p | ~100g | LVDS/HDMI |

**Block cameras** (OEM modules used in drones/PTZ cameras) are particularly interesting - they're lightweight, have built-in zoom/autofocus motors, and can be controlled programmatically via VISCA/serial protocol.

### Weatherproofing

Beach environment demands:
- **IP65 minimum** (dust-tight, protected against water jets) for the electronics/mechanism
- **Salt spray resistance** - conformal coating on PCBs, stainless steel or anodized aluminum hardware
- **UV resistance** for any plastic housings
- **Sand ingress prevention** - sealed bearings, gaskets on all openings
- **Wind load** - the system must track smoothly in 15-25 knot onshore winds while supporting a zoom camera

### Power

Target: 3+ hours of continuous operation.

| Component | Est. Power Draw |
|-----------|----------------|
| Compute (Jetson Orin Nano) | 7-15W |
| Camera + zoom motor | 3-8W |
| Pan-tilt motors | 2-10W (peak during moves) |
| GPS receiver (if hybrid) | 0.5-1W |
| Misc (controller, radio) | 1-2W |
| **Total** | **~15-35W** |

At 25W average, a 3-hour session needs ~75 Wh. A 100 Wh LiFePO4 battery pack (safe chemistry, temperature-tolerant) weighing ~1 kg would provide adequate margin.

### Tripod & Mounting

- Standard 3/8"-16 or 1/4"-20 tripod mount threads
- System should be compatible with any sturdy tripod
- Total head weight (camera + mechanism + electronics) should stay under 3-5 kg for stability
- Consider a ground spike or sandbag attachment point for wind stability
- Security: Kensington lock slot or cable loop for theft deterrence

---

## Sony a6700 as Camera Platform

The Sony a6700 is a strong candidate for the camera component of this system. Using a dedicated mirrorless camera rather than a block camera module or action cam offers superior image quality, interchangeable lenses for reach flexibility, and Sony's mature autofocus system.

### Core Specifications

| Spec | Value |
|------|-------|
| Sensor | 26 MP APS-C (1.5x crop factor) |
| Mount | Sony E-mount |
| AF system | 759 phase-detect points, 93% coverage, AI subject recognition |
| Video | 4K/60p (1.04x crop), 4K/120p (1.58x crop), 10-bit 4:2:2 |
| IBIS | 5-axis in-body stabilization |
| Weight (body) | 493 g (1.09 lbs) with battery + card |
| Price (body) | ~$1,400 |

### Programmatic Control via Sony Camera Remote SDK

The a6700 is supported by Sony's Camera Remote SDK (v1.09.00+), which enables full programmatic control from an external compute platform:

- **Connection:** USB-C (direct tether) or wired LAN (via USB-C-to-Ethernet adapter)
- **Capabilities:** Shutter release, zoom control (with power zoom lenses), exposure settings, live view monitoring, image transfer
- **Integration:** The Jetson Orin Nano can control the a6700 over USB while simultaneously processing the live view feed for CV tracking
- **No remote port** for traditional wired triggers — all control goes through USB/network via SDK

This is critical: the SDK means the tracking compute platform can programmatically start/stop recording, adjust exposure for changing light conditions, and potentially use the live view feed as the CV input without needing a separate tracking camera.

### Lens Options for Surf Distance

The 1.5x APS-C crop factor extends the effective reach of any E-mount lens.

| Lens | Effective FL (APS-C) | Weight | Weather Sealed | Price | Notes |
|------|----------------------|--------|----------------|-------|-------|
| **Sony E 70-350mm f/4.5-6.3 G OSS** | 105-525mm | 625 g (1.38 lbs) | Dust/moisture resistant | ~$700 | Best balance of reach, weight, and quality for this use case. Built-in OSS. Native APS-C lens. |
| **Sony FE 200-600mm f/5.6-6.3 G OSS** | 300-900mm | 2,115 g (4.66 lbs) | Extensive weather sealing | ~$1,800 | Maximum reach. Excellent sharpness at 600mm. Internal zoom (no extending barrel). Supports 1.4x TC (to 1260mm equiv). Very heavy for a pan-tilt head. |
| **Tamron 70-300mm f/4.5-6.3 Di III RXD** | 105-450mm | 545 g (1.20 lbs) | Moisture resistant | ~$500 | Lightest and cheapest option. No OSS (relies on IBIS). Slightly less reach than 70-350. |
| **Tamron 50-400mm f/4.5-6.3 Di III VC VXD** | 75-600mm | 1,155 g (2.55 lbs) | Moisture resistant | ~$1,200 | Widest zoom range. Built-in VC. Good compromise between reach and weight. |

**Recommendation: Sony E 70-350mm f/4.5-6.3 G OSS**

At 525mm equivalent, this covers surfers at ~200-800 ft with usable framing. The 625g weight keeps the total system (body + lens) at ~1,118g (2.46 lbs) — manageable for a motorized pan-tilt head. It has built-in optical stabilization that complements the body's IBIS, and dust/moisture resistance for beach conditions.

For lineups beyond 800 ft, the Sony 200-600mm provides 900mm equivalent reach, but at 2.6 kg total system weight (~5.75 lbs) it demands a significantly heavier and more expensive pan-tilt mechanism.

### Overheating — The Critical Constraint

The a6700 has a well-documented overheating problem during continuous 4K recording:

| Mode | Approx. Recording Time Before Overheat |
|------|----------------------------------------|
| 4K/24p (XAVC S) | ~30-60 min (varies by ambient temp) |
| 4K/60p | ~10-20 min |
| 4K/60p + Active SteadyShot | As little as ~1-2 min |
| 4K/120p | ~5-10 min |
| 1080p/30p | Extended (rarely overheats) |

A 2-3 hour surf session in direct sun on a beach makes this worse.

**Mitigation strategies (ranked by effectiveness):**

1. **Record at 1080p/30p for tracking, upscale in post.** The CV system only needs a live view feed — it doesn't need 4K. Record the actual footage at 1080p for continuous operation. This is the most reliable solution.

2. **Dummy battery + external power.** Replace the internal battery with a Sony-compatible dummy battery fed from the system's main battery pack. Eliminates internal battery heat. Users have reported 6+ hours of continuous 4K/24p recording with this setup. **Caution:** Use only Sony-branded or reputable dummy batteries — cheap ones have damaged cameras.

3. **USB-C power bank (battery left in).** A power bank connected via USB-C trickle-charges the battery while recording. Users report 6+ hours at 4K/24p/10-bit without overheat. Simpler than dummy battery.

4. **Flip the screen out + passive airflow.** Opening the rear screen exposes a heat dissipation path. The tripod mount allows airflow under the body. Combined with the external power strategies, this helps.

5. **Active cooling fan.** A small 5V fan directed at the camera body. Adds complexity and sand ingress risk, but effective.

6. **Avoid Active SteadyShot.** Use Standard or Off for SteadyShot in video. The pan-tilt mechanism and IBIS provide stabilization — Active mode's aggressive digital stabilization generates excessive heat and adds a crop.

**Recommended recording configuration for continuous surf sessions:**
- 4K/24p XAVC S, SteadyShot Standard (not Active), USB-C external power
- Or 1080p/60p for maximum thermal headroom and smooth motion

### Burst Recording Strategy — Solving Overheating Entirely

Rather than recording continuously for 2+ hours (which fights the a6700's thermal limits), the system can decouple tracking from recording:

**How it works:**

1. **Live view runs continuously** — The Sony SDK streams a low-resolution MJPEG live view feed over USB to the Jetson. This is the CV tracking input. Live view does not engage the heavy H.264/H.265 encoding pipeline, so thermal load is minimal. The camera can sustain this indefinitely.

2. **CV detects wave riding** — The tracking model already watches the surfer. A secondary classification layer detects the transition from "paddling/sitting" to "riding a wave" based on:
   - Lateral movement speed (riding = fast lateral motion vs. paddling = slow, toward/away from shore)
   - Surfer posture (standing vs. prone/sitting)
   - Wave face visible behind the surfer
   - Sudden acceleration pattern (catching a wave)

3. **SDK triggers 4K recording** — When a ride is detected, the Jetson sends a record-start command via the SDK. Recording begins at full 4K quality.

4. **SDK stops recording when ride ends** — Surfer falls, kicks out, or wave dissipates. The model detects the transition back to paddling/sitting and sends record-stop.

5. **Camera cools between waves** — Paddle-back takes 1-5 minutes, providing ample thermal recovery time.

**Recording math for a typical session:**

| Parameter | Value |
|-----------|-------|
| Session length | 2-3 hours |
| Waves ridden | 20-40 |
| Average ride length | 5-15 seconds (beach break) to 15-30 seconds (point break) |
| Total recording time | ~3-20 minutes |
| Longest continuous burst | ~30 seconds |
| Recovery time between bursts | 1-5 minutes |

Even at 4K/60p, 30-second bursts with minutes of cooling between them will never trigger overheating. This means the system can record at maximum quality settings (4K/60p, 10-bit 4:2:2) without compromise.

**Additional benefits of burst recording:**
- **Storage efficiency** — A 2-hour session produces 3-20 minutes of footage instead of 2+ hours of mostly paddling. A 64GB card is more than enough.
- **No post-session editing** — Every clip is already a wave ride. No scrubbing through hours of footage to find the good parts.
- **Battery savings** — SD card writes and encoding are a significant power draw. Burst recording extends overall system battery life.
- **Pre-roll buffer** — Keep a rolling 5-10 second buffer in RAM. When recording triggers, flush the buffer to capture the paddle-in and takeoff that preceded the detection. This ensures no wave starts are clipped.

**Risk: missed waves due to late detection.** Mitigated by:
- The pre-roll buffer (captures 5-10 seconds before the trigger)
- Tuning the trigger to be aggressive (start recording on "probably catching a wave" rather than "definitely riding")
- Fallback: option to record continuously at 1080p as a safety net alongside burst 4K

### System Weight with a6700

| Configuration | Total Weight | Pan-Tilt Implication |
|---------------|-------------|---------------------|
| a6700 + 70-350mm | ~1.1 kg (2.5 lbs) | Mid-range stepper or gimbal motors, manageable |
| a6700 + 50-400mm | ~1.6 kg (3.6 lbs) | Needs heavier-duty mechanism |
| a6700 + 200-600mm | ~2.6 kg (5.8 lbs) | Requires heavy-duty pan-tilt, significantly impacts wind resistance and cost |

The 70-350mm configuration keeps the payload under the threshold where hobby-grade gimbal motors can work, while the 200-600mm pushes into professional heavy-duty pan-tilt territory.

### Advantages over Block Camera Modules

| Factor | Sony a6700 | Block Camera (e.g., Sony FCB series) |
|--------|-----------|--------------------------------------|
| Image quality | Excellent (26MP APS-C, 10-bit video) | Good (1080p-4K, small sensor) |
| Low light | Strong (large sensor, ISO 100-32000) | Limited (small sensor) |
| Autofocus | Industry-leading AI AF with tracking | Basic contrast/phase detect |
| Lens flexibility | Interchangeable, wide ecosystem | Fixed zoom range |
| Stabilization | 5-axis IBIS + lens OSS | None (relies on mechanism) |
| Recording | Internal to SD card, multiple codecs | Requires external recorder |
| Weight (with lens) | 1.1-2.6 kg depending on lens | ~100-300g |
| Cost | $1,400 body + $500-1,800 lens | $200-400 |
| Programmability | Sony SDK (USB/network) | VISCA serial (simpler) |
| Weatherproofing | Dust/moisture resistant (not sealed) | Can be fully sealed |
| Overheating | Problematic for continuous 4K | Not an issue |

### Updated BOM Estimate (a6700 Configuration)

| Component | Est. Cost |
|-----------|-----------|
| Sony a6700 (body) | $1,400 |
| Sony E 70-350mm f/4.5-6.3 G OSS | $700 |
| Jetson Orin Nano | $250 |
| Brushless gimbal motors + controller (5 lb payload) | $150-300 |
| Battery (150Wh LiFePO4 — camera draws more) | $80-120 |
| Dummy battery / power adapter | $25-40 |
| Enclosure + pan-tilt frame | $80-150 |
| PCB / wiring / connectors | $30-50 |
| GPS module (optional) | $20-40 |
| IMU (stabilization) | $10-20 |
| Misc (fasteners, heatsink, cables) | $20-40 |
| **Total** | **$2,765-3,310** |

Significantly more expensive than the block-camera approach (~$730-1,180), but delivers professional-quality footage with a proven autofocus system. The a6700's AI subject tracking AF can complement the external CV tracking — even if the pan-tilt mechanism is slightly off-center, the camera's own AF will keep the subject sharp.

---

## Pain Points in Existing Solutions

| Pain Point | Products Affected | Severity |
|------------|------------------|----------|
| Must wear/charge a GPS tag | Soloshot, Pixio | Medium - intrusive to surf experience |
| GPS signal loss underwater | Soloshot | High - loses track on every wipeout/duck dive |
| Short range (100m) | Pixio, Pixem, OBSBOT | Critical - unusable for surf |
| Wind-induced shake/vibration | Soloshot | High - ruins footage quality |
| Sealed batteries, disposable unit | Soloshot | High - $500+ device with 3-year lifespan |
| Poor customer support | Soloshot | Medium |
| Proprietary accessories | Soloshot | Low-Medium |
| No intelligence in framing | Soloshot (GPS-only) | Medium - centers on GPS point, not visual subject |
| Can't distinguish your surfer from others | Soloshot (tags solve this, but crudely) | Low |
| Not designed for ocean conditions | XbotGo, OBSBOT, Pixio | High |
| No auto-tilt | Pixio | Medium |
| Tracking accuracy (80-85%) | XbotGo | Medium-High for surf (missing a wave is unacceptable) |

---

## Opportunities for Improvement

### 1. Tagless or Minimally-Intrusive Tracking

The single biggest UX improvement. Options ranked by intrusiveness:

1. **Fully tagless (CV-only):** Surfer does nothing. Camera identifies them by appearance/position. Hardest technically but best UX.
2. **Visual marker:** Surfer wears a specific bright rashguard or puts a sticker on their board. Camera looks for that color/pattern. Very easy, almost zero intrusion.
3. **Bluetooth/BLE beacon:** Surfer carries a tiny waterproof BLE tag for identity confirmation at close range, CV handles tracking. Tag is passive (years of battery, no charging).
4. **GPS tag (current Soloshot approach):** Most reliable for range but most intrusive.

**Recommendation:** Hybrid approach - use a distinctive visual marker (e.g., a specific color rashguard sold with the system) as the primary tracking aid, with CV handling all spatial tracking. No electronics on the surfer.

### 2. Stabilization Against Wind

Beach winds are 10-25+ knots. Current solutions shake badly.

**Solutions:**
- Heavier, lower-center-of-gravity pan-tilt mechanism
- Active stabilization via IMU + counter-correction in servo commands
- Electronic image stabilization (EIS) as a post-processing backup
- Worm-gear drives that resist wind backdrive
- Vibration-dampened camera mount (rubber isolators)

### 3. Intelligent Re-acquisition After Wipeouts

When a surfer wipes out, current GPS systems lose the tag signal. A CV system loses the visual target in whitewater. 

**Solution pipeline:**
1. Predict splash zone from last known position + wave direction
2. Hold camera pointed at predicted area
3. Scan for surfer resurfacing within a search window
4. Re-acquire and resume tracking
5. If re-acquisition fails after N seconds, zoom out to wide shot and re-scan

### 4. Smart Framing & Zoom

GPS-based systems center on coordinates. A CV system can frame intelligently:
- Lead the surfer in the direction of travel (rule of thirds)
- Zoom tighter during maneuvers, wider during paddling
- Frame the wave face, not just the surfer
- Auto-detect "riding a wave" vs "paddling out" and adjust framing accordingly

### 5. Session Highlights & AI Editing

Post-session AI processing to:
- Detect and clip individual wave rides
- Score waves by maneuver detection (turns, airs, barrels)
- Generate a highlight reel automatically
- Provide analytics (wave count, ride time, speed estimates)

Flowstate has proven this is viable at the wave pool level.

### 6. Replaceable/Swappable Battery

Unlike Soloshot's sealed battery:
- Standard battery form factor (e.g., NP-F series, V-mount, or USB-C PD)
- Hot-swappable if possible
- Optional USB-C PD input for power bank operation

### 7. Theft Deterrence

Leaving a $500+ device unattended on a beach is risky.
- Kensington lock slot + cable
- Loud alarm if moved (accelerometer trigger)
- GPS location tracking via cellular (eSIM) when moved
- "Find my device" integration
- Camera starts recording its surroundings if disturbed

### 8. Open Ecosystem

- Standard tripod mount (1/4"-20)
- Allow use with external cameras (HDMI/USB passthrough for BYOC)
- Open API for custom tracking behaviors
- Standard storage (any microSD card)
- Firmware updates via USB/WiFi

---

## Recommended Architecture

Based on the research, the optimal design for a next-generation surf tracking camera balances feasibility, cost, and surfer experience:

### Tracking: Hybrid GPS + Computer Vision

- **Primary:** Computer vision (YOLOv8 or newer) for precise framing and tracking
- **Secondary:** Optional small GPS tag for coarse pointing at extreme range and surfer identification in crowded lineups
- **Enhancement:** Visual marker system (distinctive rashguard color) to boost CV reliability without electronics
- GPS handles the "which direction to point" problem at 1000+ ft; CV handles "where exactly is the surfer in the frame"

**Update (July 2026):** Consider UWB ranging in place of GPS - see [UWB as a GPS Alternative](#uwb-as-a-gps-alternative-for-coarse-tracking) for the range/hardware tradeoffs and a cleaner division of labor (UWB for range/identity, CV for bearing at all ranges).

### Compute: NVIDIA Jetson Orin Nano (see July 2026 update)

- 40 TOPS AI performance
- Runs YOLOv8 at 30+ FPS
- 7-15W power draw
- Compact form factor
- Well-supported by NVIDIA (JetPack SDK, TensorRT optimization)

**Update (July 2026):** With real prototype throughput data in hand and a hardware/pricing recheck, a Raspberry Pi 5 + Hailo-8L is now the leading candidate on cost and power, with the Jetson Orin Nano Super as the headroom option if the deployed model grows beyond nano-class. See [Prototype Findings & Full-Scale Deployment Considerations](#prototype-findings--full-scale-deployment-considerations-july-2026) for the full comparison and reasoning.

### Camera: Sony Block Camera Module (30x) or Similar

- Lightweight (~100g)
- Programmable zoom/focus via VISCA protocol
- 1080p or 4K output
- Designed for integration into custom systems
- Alternative: A quality action cam (GoPro) paired with a separate telephoto lens system

### Pan-Tilt: Brushless Gimbal Motors with Encoder Feedback

- Smooth, precise movement
- Active stabilization against wind
- Controller: SimpleBGC or Storm32
- Closed-loop position control

### Power: 100Wh LiFePO4 Battery

- ~3-4 hours runtime
- Safe chemistry (no thermal runaway)
- Wide temperature tolerance
- USB-C PD input for external power bank extension

### Software Stack

```
Camera Feed (4K/30fps)
    |
    v
YOLOv8 Detection (Jetson Orin Nano, TensorRT)
    |
    v
Kalman Filter Tracker (smooth position estimates)
    |
    v
Framing Engine (zoom level, lead direction, rule of thirds)
    |
    v
PID Controller -> Gimbal Motors (pan/tilt commands)
    |
    v
Recording Pipeline (H.265 to microSD)
    |
    v
Post-Session AI Processing (wave detection, highlight reel)
```

### Estimated BOM Cost (Prototype)

| Component | Est. Cost |
|-----------|-----------|
| Jetson Orin Nano | $250 |
| Block camera module (30x, 4K) | $200-400 |
| Brushless gimbal motors + controller | $100-200 |
| Battery (100Wh LiFePO4) | $50-80 |
| Enclosure (weatherproof, custom) | $50-100 |
| PCB / wiring / connectors | $30-50 |
| GPS module (optional) | $20-40 |
| IMU (stabilization) | $10-20 |
| Misc (microSD, fasteners, heatsink) | $20-40 |
| **Total** | **$730-1,180** |

Consumer product target price: $500-800 (at volume)

---

## Prototyping on Desktop Hardware

The full tracking pipeline can be developed and tested using a desktop PC before investing in embedded hardware or an expensive camera. The goal of this phase is to validate the CV tracking, servo control loop, and detection algorithms on land using cheap components.

### Desktop as Development Platform

The i7-9700K + RTX 3060 Ti is more than capable of running the entire tracking pipeline in real-time:

| Task | Desktop (3060 Ti) | Jetson Orin Nano (deploy target) |
|------|-------------------|----------------------------------|
| YOLOv8 nano inference | ~2-3ms (~300+ FPS) | ~15-30ms (~30-60 FPS) |
| YOLOv8 medium inference | ~5-8ms (~120+ FPS) | ~30-60ms (~15-30 FPS) |
| CUDA cores | 4,864 | 1,024 |
| VRAM | 8 GB GDDR6X | 8 GB shared |
| Framework | PyTorch + CUDA 12.x | PyTorch + TensorRT |

Development is faster on desktop — model training, hyperparameter tuning, and algorithm iteration all benefit from the extra compute headroom. The software stack is identical: Python, PyTorch, Ultralytics YOLOv8, OpenCV. When ready to deploy, the model gets exported to TensorRT/ONNX for the Jetson with no code changes to the tracking logic.

### Alternative Dev Platform: MacBook Pro M4 (24GB)

An M4 MacBook Pro also runs the full pipeline comfortably and adds the advantage of portability — you can take the laptop outside with the prototype rig and run everything locally, no WiFi-back-to-desktop needed.

| Spec | M4 MBP (24GB) | Desktop (3060 Ti) | Jetson Orin Nano |
|------|---------------|-------------------|------------------|
| YOLOv8n inference | ~5-10ms (~100+ FPS) | ~2-3ms (~300+ FPS) | ~15-30ms (~30-60 FPS) |
| YOLOv8m inference | ~15-25ms (~40-65 FPS) | ~5-8ms (~120+ FPS) | ~30-60ms (~15-30 FPS) |
| RAM | 24 GB unified | 8 GB VRAM + system RAM | 8 GB shared |
| ML framework | PyTorch (MPS backend) | PyTorch (CUDA) | PyTorch (TensorRT) |
| Portability | Battery-powered, ~12-16 hr battery | Stationary | Embedded |

PyTorch on Apple Silicon uses the **MPS (Metal Performance Shaders)** backend instead of CUDA. Ultralytics YOLOv8 supports MPS out of the box — same code, automatic backend selection:

```python
model = YOLO("yolov8n.pt")
results = model.track(frame, classes=[0], persist=True)
# automatically uses MPS on Apple Silicon, CUDA on desktop
```

**Key advantage for outdoor prototyping:** With the MacBook, you can connect directly to the Pi Zero 2 W's WiFi stream (or even plug the webcam in directly via USB) and run the AI + servo control loop right from a park bench. This eliminates the WiFi-back-to-home latency entirely and makes the outdoor testing experience much closer to the final deployed system.

Slightly slower than the 3060 Ti but still well above real-time. Use the desktop for heavier work (model training, hyperparameter sweeps) and the MacBook for outdoor field testing.

### Prototype Hardware — Actual Build

The goal is a cheap, functional pan-tilt rig that a webcam sits on, streaming wirelessly to a MacBook or desktop for AI processing. Walk around a yard and the camera follows you.

#### Parts List

| Component | Status | Notes |
|-----------|--------|-------|
| 1x SG90 micro servo (tilt) + 1x MG90 micro servo (pan) | Ordered (MG90 ordered separately after bracket arrived) | Bracket kit turned out to require one SG90 and one MG90, not 2x SG90 as originally assumed. MG90 has metal gears vs SG90's plastic — slightly more torque/durability, same 180-degree rotation and mounting footprint. |
| [SG90 pan-tilt bracket (ThtRht nylon)](https://www.amazon.com/ThtRht-Anti-Vibration-Photography-ESP32-CAM-Raspberry/dp/B0CL9CDKQV/) | Arrived | Anti-vibration nylon bracket. Webcam attaches via velcro strip or zip tie. |
| Logitech C270 webcam | Ordered | 720p/30fps, wide FOV, plug-and-play with OpenCV. Plugs directly into Pi 3B USB. |
| Raspberry Pi 3B | Already owned | Full-size USB ports, built-in WiFi. Streams webcam over WiFi and drives servos via GPIO. Eliminates need for Arduino. |
| Jumper wires | Needed (if not already owned) | Connect servo signal/power/ground to Pi GPIO pins. |
| microSD card (8GB+) with Raspberry Pi OS | Needed (if not already owned) | Boot media for the Pi. |
| USB power bank | Already owned | Powers the Pi + servos outdoors. |
| **Total new cost** | **~$25-35** | |

#### How It Connects

```
[Logitech C270] --USB--> [Raspberry Pi 3B] --WiFi--> [MacBook Pro M4 / Desktop PC]
                              |                              |
                         GPIO pins                      Python + YOLOv8
                              |                              |
                         [SG90 servos]  <---UDP commands---  [PID controller]
```

The Pi 3B serves two roles:
1. **Camera streamer** — Captures webcam via OpenCV or mjpg-streamer, sends MJPEG stream over WiFi
2. **Servo controller** — Listens for UDP packets containing pan/tilt angles, drives servos via GPIO (using `pigpio` or `RPi.GPIO` + software PWM)

The MacBook/desktop does all the AI inference (YOLOv8 detection + tracking) and sends servo angle commands back to the Pi over UDP. Total WiFi loop latency: ~120-250ms, sufficient for tracking a walking person.

#### Servo Wiring to Pi 3B GPIO

| Servo | Signal Pin | Power | Ground |
|-------|-----------|-------|--------|
| Pan (horizontal) | GPIO 17 (pin 11) | 5V (pin 2) | GND (pin 6) |
| Tilt (vertical) | GPIO 27 (pin 13) | 5V (pin 4) | GND (pin 9) |

**Note:** SG90 servos can draw up to 500mA under load. Two servos from the Pi's 5V rail is borderline — if you see jitter or brownouts, power the servos from the USB power bank directly (5V line) with only the signal wire going to GPIO.

### Software Architecture (Prototype)

```
USB Webcam (OpenCV VideoCapture)
    |
    v
PC: Python + YOLOv8 (ultralytics)
    |-- Detect person(s) in frame
    |-- Select target (largest bbox / closest to center / manual click)
    |-- Kalman filter for smooth position tracking
    |-- PID controller: compute pan/tilt error from frame center
    |
    v
Serial (pyserial) --> Arduino Nano
    |
    v
Arduino: parse angle commands, drive SG90/MG996R servos
    |
    v
Camera physically pans/tilts to keep target centered
```

### Key Software Components

**1. Detection & Tracking (Python, runs on GPU)**
```
# Pseudocode
from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")  # nano model, fast
cap = cv2.VideoCapture(0)    # USB webcam

while True:
    frame = cap.read()
    results = model.track(frame, classes=[0], persist=True)  # class 0 = person
    # results contain bounding boxes + track IDs
    # compute error from frame center -> PID -> serial command
```

YOLOv8's built-in `.track()` method handles multi-frame tracking with ByteTrack or BoTSORT — no need to write a custom tracker for the prototype.

**2. PID Controller (Python)**

A PID loop converts the pixel offset (target center vs frame center) into servo angle adjustments:
- **P (proportional):** Move toward the target. Larger offset = faster move.
- **I (integral):** Correct steady-state drift. Prevents the target from hovering slightly off-center.
- **D (derivative):** Dampen oscillation. Prevents the servo from overshooting and jittering back and forth.

Start with P-only control (simple proportional gain), then add D if it oscillates, then I if there's steady offset.

**3. Serial Communication (Python -> Arduino)**

Python sends two angles (pan, tilt) over USB serial. Arduino reads and drives servos.

```
# Python side
import serial
ser = serial.Serial('COM3', 115200)  # Windows COM port
ser.write(f"{pan_angle},{tilt_angle}\n".encode())

// Arduino side
void loop() {
    if (Serial.available()) {
        String data = Serial.readStringUntil('\n');
        int comma = data.indexOf(',');
        int pan = data.substring(0, comma).toInt();
        int tilt = data.substring(comma + 1).toInt();
        panServo.write(pan);
        tiltServo.write(tilt);
    }
}
```

### Prototype Testing Progression

| Phase | Test | What You Validate |
|-------|------|-------------------|
| **1. Screen only** | Run YOLOv8 on recorded surf footage (YouTube). Draw bounding boxes, compute hypothetical servo angles. No hardware needed. | Detection model works on surfer-like subjects. Pipeline runs in real-time. |
| **2. Webcam only** | Plug in webcam, run YOLOv8 live. Walk around a room. Overlay tracking on screen. Still no servos. | Live detection latency, tracking ID persistence when occluded, camera latency. |
| **3. Webcam + servos (indoor)** | Mount webcam on pan-tilt bracket. Walk around a room. Camera should follow you. | PID tuning, servo response speed, tracking smoothness, latency in the full loop. |
| **4. Webcam + servos (outdoor)** | Move to a yard/park. Walk/jog at 50-100 ft distance. Vary lighting (sun, shade, backlit). | Outdoor detection robustness, glare handling, range limits of webcam resolution. |
| **5. Recorded surf footage + servos** | Feed surf video into the pipeline as if it were live. Servos move as if tracking a real surfer. | Surf-specific detection tuning, wave ride detection triggers, re-acquisition after wipeout. |

### Wireless Prototype — Taking It Outside

The wired prototype (USB webcam + Arduino + PC) is tethered to your desk. To test outdoors — someone walking across a yard at 50+ ft — the rig needs to go mobile over WiFi. The PC still does all the AI processing; only the camera and servos go outside.

#### Option A: ESP32 + Phone as Camera (~$5-8 added cost)

The cheapest wireless setup. Replace the Arduino Nano with an ESP32 dev board, which has built-in WiFi and can drive servos directly.

| Component | Role | Cost |
|-----------|------|------|
| ESP32 dev board (e.g., ESP32-WROOM-32) | Receives pan/tilt commands over WiFi, drives servos | $5-8 |
| Your phone (Android or iPhone) | Streams video over WiFi using a free app | $0 |
| Phone mount / clamp for pan-tilt bracket | Holds phone on the servo bracket | $3-5 |
| USB power bank | Powers ESP32 + servos outdoors | Already own one |

**Video stream:** Install [DroidCam](https://www.dev47apps.com/) (Android) or [IP Webcam](https://play.google.com/store/apps/details?id=com.pas.webcam) (Android). These stream MJPEG/RTSP over WiFi. On the PC:

```python
# OpenCV grabs phone stream identically to a local webcam
cap = cv2.VideoCapture("http://192.168.1.XXX:4747/video")
```

**Servo control:** The ESP32 runs a minimal WiFi server that listens for UDP packets containing pan/tilt angles. UDP is faster than TCP for real-time control (~1ms vs ~10-50ms).

```python
# PC sends servo commands over UDP instead of serial
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(f"{pan},{tilt}".encode(), ("192.168.1.YYY", 8888))
```

```cpp
// ESP32 Arduino sketch (simplified)
#include <WiFi.h>
#include <WiFiUdp.h>
#include <ESP32Servo.h>

WiFiUDP udp;
Servo panServo, tiltServo;

void setup() {
    WiFi.begin("your_ssid", "your_password");
    udp.begin(8888);
    panServo.attach(13);
    tiltServo.attach(12);
}

void loop() {
    int packetSize = udp.parsePacket();
    if (packetSize) {
        char buf[32];
        udp.read(buf, 32);
        // parse "pan,tilt" and drive servos
        int pan, tilt;
        sscanf(buf, "%d,%d", &pan, &tilt);
        panServo.write(pan);
        tiltServo.write(tilt);
    }
}
```

**Pros:** Cheapest option. Phone cameras are far better than any webcam (autofocus, stabilization, 1080p-4K).
**Cons:** Phone is heavy for SG90 servos — may need MG996R upgrade. Phone battery drains from streaming.

#### Option B: ESP32-CAM — All-in-One (~$8-12)

A single board with camera, WiFi, and microcontroller. The entire outdoor unit is one $8 module plus two servos.

| Component | Role | Cost |
|-----------|------|------|
| ESP32-CAM (with OV2640 sensor) | Streams video + receives servo commands over WiFi | $8-12 |
| 2x SG90 servos + bracket | Pan/tilt | $6-10 (from existing prototype) |
| USB power bank | Power | Already own one |

**How it works:** The ESP32-CAM streams MJPEG at ~10-15 FPS (640x480) over WiFi. A second task on the same chip listens for UDP servo commands. The PC runs the AI and sends commands back.

**Pros:** Smallest, cheapest, lightest. Entire outdoor unit weighs ~50g. No phone needed.
**Cons:** Camera quality is poor (2MP, fixed focus, no autofocus). Low FPS over WiFi. Image quality will limit detection range to ~15-20 ft. Dual-tasking (streaming + servo control) can cause frame drops.

#### Option C: Raspberry Pi Zero 2 W (~$20-30 added)

The most capable option. Replaces both the Arduino and the webcam streaming problem.

| Component | Role | Cost |
|-----------|------|------|
| Raspberry Pi Zero 2 W | Streams webcam feed over WiFi, drives servos via GPIO | $15-20 |
| Logitech C270 USB webcam | Camera (from existing prototype) | $0 (reuse) |
| USB OTG adapter | Connect webcam to Pi Zero's micro-USB port | $3-5 |
| USB power bank | Power | Already own one |

**How it works:** The Pi runs a lightweight MJPEG streaming server (e.g., `mjpg-streamer` or a few lines of Flask + OpenCV). Servos connect directly to GPIO pins — no Arduino needed. The PC grabs the video stream and sends servo commands back over a TCP/UDP socket.

**Pros:** Best webcam quality of the wireless options (reuses Logitech). GPIO servo control eliminates Arduino. Can run lightweight pre-processing (resize, crop) on the Pi to reduce WiFi bandwidth.
**Cons:** Raspberry Pi Zero 2 W can be hard to find in stock. Slight setup overhead (Raspberry Pi OS, Python, GPIO libraries).

**Continued in [prototype.md](prototype.md)**, which covers the chosen approach (Raspberry Pi 3B), the actual video-over-WiFi implementation log, WiFi latency measurements, what the prototype won't test, Jetson porting notes, and possible future changes.

---

## Prototype Findings & Full-Scale Deployment Considerations (July 2026)

Findings from running `mobile_tracking_servo_control.py` on a desktop (RTX 3060 Ti) and a weak 2020 laptop (MSI Modern 15, MX330), which sharpen or override some of the assumptions in the sections above.

### Edge AI Compute Hardware — 2026 Update

The original [Compute Hardware for Edge AI](#compute-hardware-for-edge-ai) table and Jetson-only recommendation are stale on two fronts: real throughput numbers now exist from the prototype, and the hardware landscape shifted materially since April 2026.

| Platform | Price | Power | Weight/Size | Realistic YOLO-nano FPS | Ultralytics friction | Availability |
|---|---|---|---|---|---|---|
| **Jetson Orin Nano Super** | **$399** (NVIDIA raised Jetson pricing up to 101% in July 2026; was $249) | 7-25W+, configurable | Full SBC + carrier board | ~43-66 FPS (nano-class, INT8/TensorRT); YOLOv8s ~100 FPS FP16 | Best-in-class: official 1-line TensorRT export | Sold direct at the new higher price |
| **Pi 5 + Hailo-8L (13 TOPS) HAT** | ~$150 ($80 Pi5 + $70 HAT) | Pi5 ~5-8W + Hailo-8L ~1.5W | Standard HAT, light | Hailo's own benchmark: 431 FPS (YOLOv8n)/491 FPS (YOLOv8s) at 640px batch1; real-world single-PCIe-lane numbers on Pi5 land lower but still far above what a smoothed servo loop needs. Nano/small models see proportionally less accelerator speedup (~13-14x over CPU) than medium/large (~24-27x) | Official Ultralytics Hailo export path (.pt to ONNX to HEF) | Actively sold; newer AI HAT+ 2 (Hailo-10H, 40 TOPS) also available at $130 |
| **Pi 5 + Hailo-8 (26 TOPS) HAT** | ~$190 | Pi5 + ~2.5W | Same | Same ballpark, more headroom | Same | Same |
| **RK3588 SBC** (Radxa Rock 5B+, Orange Pi 5 Max) | ~$157-220 (Rock 5B+ 8GB) | ~5-8W idle, 9-19W loaded | Full SBC | Inconsistent across sources: YOLOv8 INT8/RKNN ~30 FPS in one benchmark, YOLOv5n 58.8 FPS in another, but a YOLO26n-specific RKNN benchmark on Rock 5B came back at only ~15 FPS - notably weaker, treat with caution until tested on the actual model | Official RKNN export doc as of YOLO26, but still needs an INT8 calibration step | Orange Pi 5 Plus largely vanished from retail in 2026; Radxa Rock 5B+ now the more available option |
| **Qualcomm QCS6490 dev kit** | Quote-only (no public retail price) | Not published | SMARC module + carrier | AI Hub lists YOLOv8/v11/X as supported on its 13-TOPS Hexagon NPU, no independently verified nano-class FPS found | Requires Qualcomm's own AI Hub/QNN toolchain, not integrated into Ultralytics' export | Not hobbyist-friendly - quote-based procurement |
| **Google Coral** | Was $60-75 | ~2-4W | USB stick | N/A | TF-Lite only, not a direct Ultralytics export target | **Discontinued by Google** - remaining stock is reseller leftovers. Drop from consideration. |

Given this project only needs a modest FPS floor (the spring-follow controller already tolerates 5-8fps acceptably in real testing), every option above except the QCS6490/Coral has large throughput headroom - the deciding factors are price, power budget, and Ultralytics integration friction rather than raw speed:

- **Pi 5 + Hailo-8L is the leading candidate**: ~$150 all-in, ~6.5-9.5W total marginal draw, official Ultralytics export path, and enormous FPS headroom over what this project actually consumes. Best fit for the ~15-35W total system power budget in [Power](#power).
- **Jetson Orin Nano Super is the headroom fallback** if the deployed model grows past nano-class (e.g. YOLO26s, see below) or the two-stage detection pipeline runs both stages concurrently rather than on a cadence - but the July 2026 price hike changes the BOM math this doc originally worked out.
- **RK3588 is the budget option** but its one YOLO26-specific benchmark ran slower than expected; would need direct testing before trusting it for a deployment (not just a prototype).

### Model Size: `yolo26n` vs `yolo26s` for Deployment

The prototype uses `yolo26n` (nano). For an actual deployed unit - not just a desk prototype - `yolo26s` (small) is worth the extra compute given the project's core challenge (surfer is tiny in frame at range): `s`-class models have meaningfully better accuracy than `n`-class, and both leading compute picks above absorb it without becoming the bottleneck (Hailo-8L: YOLOv8s 28.6-55.7 FPS single-stream, up to 80-120 FPS at higher batch sizes; Jetson Orin Nano: YOLOv8s ~100 FPS FP16). RK3588 is the one candidate where this upgrade adds real risk, compounding its already-uncertain YOLO26-class numbers above.

### Capture Resolution (1080p) vs. Inference Resolution (`imgsz`) — Not the Same Cost

A future move to 1920x1080 capture does not by itself increase YOLO's compute cost. Ultralytics always letterboxes/resizes whatever frame it receives down to a fixed `imgsz` (640 by default) before the forward pass - the network's cost is governed by `imgsz`, not source resolution. Capturing at 1080p only helps if the extra resolution survives to the network somehow:

- **Raising `imgsz`** to actually pass more of the 1080p frame through the network is the real compute-cost lever - cost scales roughly with `imgsz²` (e.g. `imgsz=1280` costs ~4x `imgsz=640`), independent of capture resolution.
- **The two-stage wide/zoom pipeline** (see [Tracking Pipeline for Surf](#tracking-pipeline-for-surf)) gets the resolution benefit more cheaply: a wide 1080p frame locates the surfer roughly, then a cropped region around them is fed to the detector at full resolution - this preserves pixels-on-target for a distant subject without paying `imgsz`-scale cost on the whole frame every frame.
- Capturing at 1080p while leaving `imgsz=640` and no cropping buys nothing - the extra resolution gets discarded in the resize.

This means hardware sizing for "1080p support" should be scoped to whichever of these two levers actually gets built, not to the capture resolution number itself.

### Two-Stage Wide/Zoom Pipeline: Compute Cost Is a Tunable, Not a Fixed Tax

Revisiting the [Tracking Pipeline for Surf](#tracking-pipeline-for-surf) two-stage design (wide-angle scan to locate, then zoom in and track) with a compute budget in mind:

- **Worst case** - both stages run every frame at full `imgsz` - roughly doubles per-frame compute versus today's single-stage approach.
- **Realistic design** - the wide scan only needs to re-run when the target isn't already being tracked (on a cadence, or on track loss), while the zoomed stage runs every frame on a small crop at a smaller `imgsz` (e.g. 320, since it's refining a known-ish location rather than hunting for a speck). At a 15fps target with 2 wide passes/sec (640) + 15 crop passes/sec (320, ~1/4 cost), total cost is roughly equivalent to 5-6 full 640-px passes/sec - cheaper than running one naive full-frame detector at 15fps today.

The wide-scan cadence and crop `imgsz` are knobs to tune against whatever compute is actually available, the same way `imgsz`, the GMC toggle, and capture threading were tuned during prototyping - the pipeline's viability doesn't depend on a specific hardware pick made in advance.

### GMC (Global Motion Compensation) Not Needed Even While Panning

`botsort_nogmc.yaml` disables BoT-SORT's `sparseOptFlow` GMC step (~2x tracker speedup, ~37ms/frame saved). The theoretical concern was that this only holds while the camera is stationary/decoupled from the servos, and would need revisiting once the camera rides the pan-tilt mechanism it steers. Confirmed on the physical rig: it doesn't need revisiting - tracking holds up fine with GMC off even while actively panning, likely because the spring-follow controller keeps servo motion slow/damped and target selection (largest box wins) doesn't depend on stable track IDs.

Whether it's worth applying elsewhere depends on the bottleneck, not just correctness: it was a big win on the weak laptop (CPU-bound). On the desktop path (`tracking_servo_control.py`), FPS is already capped by the Pi camera's own bandwidth (~19-20fps ceiling, not tracker CPU cost), so trimming GMC there wouldn't raise the achieved FPS - not applied there for that reason.

### UWB as a GPS Alternative for Coarse Tracking

The [Ultra-Wideband](#5-ultra-wideband-uwb-tracking) entry's "~200m, insufficient for surf" verdict reflects generic consumer UWB (phone-tag-class hardware). Revisited with actual chip/product data:

**Range.** UWB's regulated power (FCC: -41.3 dBm/MHz EIRP, uniform across the whole 3.1-10.6GHz allocation - low band gets no extra allowance) means range comes from antenna gain and frequency, not extra transmit power. Purpose-built modules with a power amplifier and directional antenna already claim 500m on standard hardware - [Inpixon's nanoANQ Chirp anchor](https://www.inpixon.com/technology/rtls/anchors) and the [Makerfabs/how2electronics ESP32-DW3000 module](https://github.com/Makerfabs/Makerfabs-ESP32-UWB-DW3000) both cite ~500m outdoor. 500m (~1,640ft) already covers most realistic lineups; a directional antenna pointed at the water fits this project's tripod setup naturally (EIRP is measured post-antenna-gain, so a gain antenna raises effective power in the pointed direction within the legal cap).

**Low band vs. high band.** Separately, lower carrier frequency reduces free-space path loss - roughly 7dB less at ~3.5GHz vs ~8GHz for the same distance (Friis equation), worth ~2.3x more range for the same power budget. This is a real, stackable lever on top of the PA+antenna approach above, not a substitute for it. However: **the DW3000 chip (which underlies the demonstrated 500m module above) doesn't support low band at all** - Qorvo's own description is a "6.5GHz-8GHz IR-UWB transceiver IC," fixed to channels 5 and 9. Low band (channels 1-4, ~3.5-6.5GHz per Decawave's datasheet) requires the previous-generation **DW1000**, which brings real costs: ~3x higher power draw than DW3000, no channel 9/Apple U1 interoperability, and uncertain current sourcing (shown discontinued on DigiKey since 2020, though still listed on Qorvo's own site - needs a direct availability check before designing around it). Recommendation: prototype with DW3000 + PA + gain antenna first (proven 500m, better power/sourcing); only chase DW1000 + low band if 500m proves insufficient in real beach testing.

**Hardware split - land-heavy, tag-minimal.** Whatever range-extension approach is used (PA, gain antenna, low band), the added complexity is entirely anchor-side. The wearable tag stays simple regardless: a DW3000-class chip in sleep mode draws under 1.3µA, and tags built on it are reported running years on a single CR2032 coin cell at modest ranging rates, in a package a few mm across. This is a genuine improvement over a GPS tag - UWB ranging is request/response (the tag replies to anchor polls), while GPS requires the tag to run its own continuous satellite-acquisition receiver, which is inherently more power-hungry.

**Bearing: single-anchor ranging alone isn't enough - need AoA or trilateration.** Range-only UWB can't replace GPS's original job. CV can't bootstrap itself at long range either - a wide-enough FOV to see the whole lineup reduces the surfer to a handful of pixels, so CV has no way to find that speck without already being pointed roughly at it. Something has to supply the initial "which way to point" bearing; distance alone doesn't.

**Preferred: AoA (Angle of Arrival), single anchor.** Keeps this project's one-tripod-unit pattern (camera, servos, compute, and now the anchor all in one mounted package) instead of trilateration's requirement for two anchors physically separated by a real baseline along the beach. AoA decodes bearing from the phase difference of the same signal arriving at 2+ antenna elements spaced about half a wavelength apart - at UWB's 6.5-8GHz that's only ~2cm, so the whole array fits on one small board. 2 elements gives azimuth only, which should be sufficient here since the surfer stays near water-level relative to the tripod (elevation barely changes; azimuth is the axis that matters for panning). Full 2D (azimuth + elevation) needs a 3rd, non-collinear element.

Hardware requirement: this needs Qorvo's **DW3120/DW3220** chip specifically (dual antenna ports enabling PDoA on a single IC) - not the plain DW3000/DW3110 used in the how2electronics 500m demo, which is single-antenna and not AoA-capable at all (confirmed on Qorvo's own forum: the common DWM3001CDK kit has to be paired with a separate dedicated AoA board to demonstrate AoA). **Confirmed via the two products' own listing pages (Aug 2026):** the 500m demo module is Makerfabs' plain [**ESP32 UWB DW3000**](https://www.makerfabs.com/esp32-uwb-dw3000.html) ($43.80) - its own reference sheet links the **DW3110 datasheet**, matching the non-AoA chip flagged above. This is a materially different board from the AoA kit below: different MCU (ESP32 vs. STM32), single antenna vs. dual, and not cross-compatible - the 500m figure does not transfer to the AoA kit.

Qorvo's own **QM33120WDK1/WDK2** AoA dev kit costs **~$500**; a much cheaper option is [Makerfabs' **MaUWB_STM32 AOA Development Kit**](https://www.makerfabs.com/mauwb-stm32-aoa-development-kit.html) (1 anchor + 1 tag, STM32F103 + DW3000-family chip, PDoA-based AoA, open-source firmware, on-board PA/LNA) - built on what's marketed as a "DW3000 AOA chipset," most likely the DW3220 under looser family branding, worth confirming the exact part number before ordering. Price varies a lot by seller: **$69.80 direct from Makerfabs**, $109.80 via an Alibaba reseller, ~$235 via a Swedish reseller - same product, buy direct if that price holds at checkout. **Its own spec sheet lists coverage radius as 30m@6.8M** - not the ~300m this doc previously estimated by analogy to the plain ranging module. That's a large gap from the 500m the plain module demonstrates, and from the range this project actually needs to cover a realistic lineup; the two-element antenna array PDoA needs (matched phase response, not just gain) is a harder RF problem than the single-antenna ranging module's, which is the likely reason the AoA kit's range is so much shorter despite similar on-board PA/LNA. Treat 30m as the number to validate empirically before relying on this kit at surf distances - see the custom-PCB feasibility note directly below for what closing that gap would take.

**Custom PCB to close the 30m->500m gap: effort/expertise, not money.** (Reasoned analysis, not a sourced benchmark - flagging as such.) The dollar cost of a DIY attempt is genuinely small: DW3120/DW3220 parts, a small-run RF-capable PCB fab job, and antenna components likely total a few hundred dollars, not thousands. The blocker is that PDoA AoA needs two antenna elements with *matched phase response*, not just gain - spaced at ~half-wavelength (~2cm at 6.5-8GHz) with sub-mm placement accuracy, fed by phase-coherent RF traces, with enough isolation between elements that mutual coupling doesn't corrupt the phase measurement. That's a controlled-impedance RF layout problem across a wide UWB bandwidth (matching one frequency isn't enough - the whole 6.5-8GHz channel has to stay phase-coherent), and verifying it worked requires a VNA that actually covers 6.5-8GHz to check S11/S21 and tune the array - sub-$100 hobbyist VNAs (e.g. base NanoVNA) typically top out well below that band, so the real tooling cost is a better VNA, not the board itself. This is the same reason a single-antenna ranging module (this project's 500m demo) is comparatively easy to push for range with a PA and a gain antenna, while the AoA kit - built for a much shorter 30m spec despite similar PA/LNA hardware - implies its designers hit exactly this array-design ceiling. It's also indirectly why Qorvo sells a pre-validated $500 reference kit instead of the market being full of cheap 500m AoA boards: if it were mostly a matter of adding gain, that kit wouldn't need to exist. None of this rules out a custom board - but it reframes the ask from "populate a board with better parts" to "execute a real RF antenna-array design/tune cycle," which is a multi-iteration effort even with the parts in hand.

Accuracy: reported real-world AoA performance is ~2.4° in good conditions, which becomes ~20m of lateral position error at 500m range (`distance x tan(angle error)`). **Correction (see "Reassessment" below):** 20m is too coarse on two separate counts, not one - it's comparable to realistic inter-surfer spacing (a disambiguation problem) *and*, at the real system's telephoto reach, far wider than the zoomed frame itself would be at that range (a framing problem, one that matters more the more the target is actually moving).

**Fallback: two-anchor trilateration**, if the AoA kit's cost/availability doesn't pan out. Same underlying tradeoff either way (bearing must come from the UWB side, not CV), but trilateration needs no special antenna hardware - two ordinary ranging anchors, each doing the same plain time-of-flight measurement, at a known physical separation - at the cost of needing that separation to be a meaningful fraction of the target's range for good accuracy (a short baseline convenient for a backyard test won't validate real surf-distance bearing accuracy) and two mounting points instead of one.

**How coarse would a 10ft-baseline trilateration bearing actually be at 300m?** Worked estimate (derived, not vendor-published). Two anchors separated by baseline `b`, ranging a tag at distance `R >> b`, is geometrically the same problem as a two-element AoA interferometer: for a target at angle θ off broadside, `d2 - d1 ≈ b·sinθ`, so bearing resolves from the anchors' range-*difference* exactly the way AoA resolves it from phase-difference - baseline length plays the role antenna spacing plays in AoA. Differentiating gives `σ_θ (rad) ≈ √2·σ_d / (b·cosθ)`, where `σ_d` is each anchor's individual ranging error and √2 comes from combining two independent range measurements; error is smallest at broadside (θ=0) and grows toward the baseline's own axis as cosθ shrinks.

For a 10ft (3.05m) baseline: DW3000 two-way ranging is commonly cited at **~10cm accuracy** in good conditions ([Symmetry Electronics](https://www.symmetryelectronics.com/blog/dwm3000-uwb-module-delivers-10cm-accuracy-symmetry-blog/), [how2electronics' 500m demo](https://how2electronics.com/esp32-dw3000-uwb-module-achieving-500m-range/)), but real open-space deployments are reported anywhere from **10-50cm** ([Skylab UWB module roundup](https://www.skylabmodule.com/recommend-5-kinds-of-uwb-ranging-and-positioning-modules/)). Plugging both ends of that range in at broadside, R=300m:

- Best case (10cm/anchor): σ_θ ≈ **2.7°** -> **~14m** lateral position error at 300m
- Conservative (50cm/anchor): σ_θ ≈ **13.3°** -> **~70m** lateral position error at 300m - large enough to point the camera at open water, not the surfer

The best case is genuinely comparable to the ~2.4° reported for the dedicated AoA kit (not worse) - the interferometer math doesn't care whether the baseline is spaced antenna elements on one board or two separated anchor units, only the ratio of ranging precision to baseline length. The real risk isn't the concept, it's whether actual outdoor accuracy lands near the 10cm end or the 50cm end - that's the gap between "workable" and "not remotely useful" at this baseline.

**Two levers to improve this, neither requiring RF array design:** (1) **baseline length** - error scales as 1/b, so tripling it (~30ft/9m) divides lateral error by 3 (down to ~4.6m best-case / ~23m conservative at 300m), at the cost of two precisely-surveyed mounting points spread further apart, not just two mounting points. (2) **orientation** - error grows as 1/cosθ moving off broadside toward the baseline's own axis, so anchors should be sited so the expected lineup sits broadside (perpendicular to the baseline), not off to one end.

Caveat: this assumes the two anchors' ranging errors are independent (no shared calibration bias). If both carry a similar systematic antenna-delay/clock offset - plausible with uncalibrated modules - that bias may not cancel in the range-difference and could add on top of this random-noise estimate rather than average out. Field-measure before committing to a baseline length; this formula is a planning estimate, not a guarantee.

**What this fixes vs. doesn't, relative to GPS:** centimeter-level *ranging* (distance) precision (vs. GPS's ~3-5m, the source of the "jitter at zoom" problem in [SOLOSHOT3](#soloshot3-soloshotcom)'s reviews) and much faster update rates (tens-to-hundreds Hz vs. GPS's 1-10Hz) - real UWB advantages, but only for distance. For *bearing*, the actually-limiting problem, see the reassessment directly below: GPS's absolute few-meter accuracy turns out to beat both UWB approaches above at this range, because it doesn't suffer the short-baseline dilution-of-precision problem that caps AoA's and trilateration's angular resolution. Neither approach fixes GPS's worst failure mode - signal loss when the surfer submerges - since that's an RF-through-water problem common to any RF tag, UWB included; the same re-acquisition mitigation in [Intelligent Re-acquisition After Wipeouts](#3-intelligent-re-acquisition-after-wipeouts) still applies.

**Reassessment: person-disambiguation is one of two jobs the position feed does, not the only one - and "already in frame regardless of aim" doesn't hold once real zoom optics are involved.** The original version of this section ran the framing math against the *prototype's* fixed-wide C270 lens (55° diagonal, ~49° horizontal per `tracking_servo_control.py`'s `_split_fov`), where at 300m the frame is `2 x 300 x tan(24.4°) ≈ 270m` wide - genuinely the whole lineup, regardless of aim. But that's a property of that specific test lens, not of the system this project is actually building toward. The planned rig uses real telephoto reach (see [Sony a6700 as Camera Platform](#sony-a6700-as-camera-platform)): at max zoom on, say, the Sony FE 200-600mm (900mm APS-C-equivalent), horizontal FOV narrows to roughly 2.3°, so frame width at 300m shrinks to `2 x 300 x tan(1.1°) ≈ 12m` - the Tamron 50-400mm's ~600mm-equivalent max gives a similar ~18m. At that reach, "already in frame no matter where you aim" is false - the entire point of zooming in is that most of the lineup is *not* in the frame at once.

So the UWB/GPS position feed does two distinct jobs, not one: **(1) disambiguation** - supply an aim point precise enough to zoom in on the *correct* person out of a group (the 14-70m/~20m analysis above stands for this, and is still marginal-to-inadequate), and **(2) framing** - keep re-aiming that narrow, zoomed frame at the person as they move, so they don't drift out of a window that's only ~12-18m wide at 300m. Framing is very much back in play at zoom; it just doesn't matter equally in every situation.

**Motion determines how much job (2) matters.** A surfer sitting still in the lineup barely stresses framing - the frame doesn't need to move once it's centered, closer to the original "coarse aim, let CV/AF hold it" case. Once they start moving (paddling for a wave, popping up, riding), that ~12-18m window at 300m gives very little margin before they drift out of frame entirely, and now *both* position accuracy and update rate matter a lot more than the disambiguation problem alone implied.

GPS sidesteps the *mechanism* that caused this, not just the numbers. AoA and trilateration both derive bearing from a short local baseline (antenna spacing or anchor separation) relative to a long target range - that ratio is what caused the error blowup (`σ_θ ∝ 1/baseline`). GPS has no local baseline: the tag computes its own absolute position via satellites, so its accuracy is a roughly flat few meters *independent of range from the camera rig*. Cheap hobbyist GPS (u-blox NEO-M8N, ~$10-15) specs **2.5m CEP without SBAS, 1.5m with SBAS** ([u-blox NEO-M8 datasheet](https://content.u-blox.com/sites/default/files/NEO-M8_DataSheet_(UBX-13003366).pdf)) - at 300m that's **~0.29-0.48° of angular error**, 5-8x better than either UWB approach's best case, and an open beach sky view works in GPS's favor rather than against it (unlike UWB's antenna-array/baseline problems, which don't get easier as you shrink the hardware).

The problem GPS reintroduces is comms, not positioning. A phone/watch has GPS but no way to relay a fix to the camera rig at 300m except cellular (coverage-dependent) or short-range Bluetooth/WiFi (useless at this distance) - the practical fix is a small companion tag: cheap GPS module + a long-range low-power radio. **LoRa** (SX1276-class, license-free ISM bands) comfortably covers this - field tests show **90%+ packet delivery at 11km line-of-sight at +20dBm/2dBi antenna** ([IC Online field benchmarks](https://www.ic-online.com/blog/post/lora-rf-module-sensitivity-and-range-benchmarks-side-by-side-field-test-data-for-sx1262-vs-sx1276)), 30-50x more range than needed, with a GPS-fix payload (~8-16 bytes) trivial for LoRa's low data rate even at long-range spreading factors. GPS module current draw (~20-50mA continuous while tracking) is the dominant power cost on the tag, not LoRa's duty-cycled transmit bursts - still fine for session-length battery life.

UWB itself can also carry the data, since it's not just a ranging radio - DW3000 supports 802.15.4z data communication at 850kbps/6.81Mbps with payloads up to 4096 bytes (see [DW3000 datasheet](https://www.mouser.com/pdfDocs/DW3000DataSheet5.pdf), source already cited above), trivially enough for a GPS fix. That lets a UWB tag piggyback the GPS payload on its existing ranging exchange, doing both jobs on one radio - but it only reaches UWB's own range ceiling (~300-500m, same EIRP-capped physics as the AoA/trilateration sections above), so it buys no range advantage over LoRa's 10km+ headroom for the comms leg specifically.

Where this leaves the comparison:

| | Bearing accuracy at 300m | Update rate | Comms range | Effort |
|---|---|---|---|---|
| UWB AoA | ~2.4-13° (~20m+ err), and only ~30m confirmed anchor range | tens-hundreds Hz | n/a (same radio) | High - custom RF antenna array design |
| UWB trilateration (10ft baseline) | ~2.7-13.3° (14-70m err) | tens-hundreds Hz | n/a (same radio) | Low - off-the-shelf modules, two mounts |
| GPS + LoRa | ~0.29-0.48° (1.5-2.5m err, range-independent) | 1-10Hz | 10km+ | Low - off-the-shelf modules |

GPS+LoRa wins decisively on accuracy for the **disambiguation** job (identifying the right person in a group) while being no harder to build than the trilateration fallback. It still shares UWB's one unfixed failure mode (RF signal loss when the tag goes underwater during a wipeout). Its slower 1-10Hz update rate is a real tradeoff, not a dismissible one, for the **framing** job once real zoom optics and a moving target are in play (see the reassessment above) - the earlier claim that update rate was "likely inconsequential" only held against the prototype's own slew-limited, spring-damped servo, a mechanical bottleneck specific to that rig, not a property of the position feed itself. Treat GPS+LoRa as the leading candidate for disambiguation specifically; whether it also suffices for framing a moving target at full zoom - or whether UWB's much faster update rate earns it a role there too, alongside rather than instead of GPS - depends on the real zoom FOV and expected target angular velocity during maneuvers, neither pinned down yet. UWB trilateration remains the fallback if GPS accuracy itself underdelivers in real beach testing.

**Concrete hardware: Meshtastic on LILYGO T-Beam, not a custom build.** Meshtastic is a pre-built open-source firmware that already does almost exactly this job - broadcast a node's own GPS position over LoRa to another node - so this can be a flash-and-configure task rather than a custom radio protocol build. [LILYGO T-Beam](https://lilygo.cc/en-us/products/t-beam) (~$50: ESP32 + SX1262 + L76K GPS, ~1-5m accuracy) or the pricier [T-Beam Supreme](https://store.rokland.com/products/lilygo-t-beam-supreme-esp32-s3-lora-development-board-sx1262-915mhz-gps-l76k-or-u-blox) (~$105, ESP32-S3, sold in two GPS-chip SKUs - **H660** ships u-blox's MAX-M10S, 1.5m CEP multi-constellation/<2s TTFF/~12mW continuous; **H663** ships the cheaper L76K, ~1-5m accuracy - H660 is the better match for the accuracy this project needs) - one GPS-equipped unit worn as the tag.

**Only the tag needs GPS.** The anchor at the camera rig doesn't - its position is fixed for the whole session (the tripod doesn't move), so a plain GPS-less LoRa board works there via Meshtastic's **Fixed Position** setting (hardcode the tripod's coordinates once, from a phone reading or a one-time survey - GPS-less nodes with a fixed position are a normal, supported Meshtastic pattern, e.g. base stations/repeaters). A [Heltec WiFi LoRa 32 V3](https://heltec.org/project/wifi-lora-32-v3/) (ESP32-S3 + SX1262, no GPS - same radio chip as the T-Beam Supreme, so no interop concern) is the natural anchor pick, meaningfully cheaper than a second Supreme since it skips the GPS chip entirely. Bill of materials is one GPS-equipped tag + one GPS-less anchor, not two identical boards. Stock-antenna single-hop range is realistically **~400m** ([Meshtastic range guide](https://www.sdrstore.eu/meshtastic-range-guide-how-far-lora-mesh-nodes-reach/)) - comfortably past the 300m target, with a better antenna as headroom; the 100+ km figures seen elsewhere are multi-hop mesh records with specialized antennas, not relevant here.

**Confirmed anchor SKU (Aug 2026):** [Heltec WiFi LoRa 32 V3, US915](https://store.rokland.com/products/heltec-wifi-lora-32v3), **$26.97** (bulk discounts down to $21.85/unit at 25+, not relevant at this quantity) - ships **pre-flashed with Meshtastic** (skips the initial firmware-flash step, just needs configuring: region, Fixed Position, GPS/broadcast intervals), plus LoRa antenna, SH1.25x2 battery connector, pin headers, and a shell case all included in that price - no separate antenna purchase needed. Confirmed specs: 21±1dBm max TX power (slightly above the 20dBm the earlier range benchmarks assumed), -136dBm max RX sensitivity at SF12/125kHz, 3.7V LiPo via the same JST 1.25mm battery interface as covered in the calibration/power notes above, 50.2x25.5x10.2mm.

**Catch, and it's a config issue, not a hardware one:** Meshtastic's defaults are tuned for battery life, not live tracking - GPS position is fetched only once every **2 minutes** by default, and broadcast only every **15 minutes** ([Meshtastic position config docs](https://meshtastic.org/docs/configuration/radio/position/)). Both are configurable down to seconds via the app/CLI, no firmware rebuild needed - but this has to be explicitly changed, or the tag would appear to barely move.

**Integration:** the official `meshtastic` Python package (`pip install meshtastic`) exposes an `iface.nodes` dict with each node's live `position` (lat/lon as `latitudeI`/`longitudeI`, integer degrees x1e7), updated via a pub/sub callback over serial/TCP - a clean drop-in for feeding position data into the tracking pipeline instead of hand-rolling a packet protocol, and no need for the raw-LoRa custom firmware route unless Meshtastic's mesh-protocol overhead proves to be a problem in practice.

**Where the anchor plugs in: the laptop, not the Pi.** The Heltec anchor connects via **USB-C** to whichever machine runs the tracking control loop (`tracking_servo_control.py`/`mobile_tracking_servo_control.py`) - its onboard CP2102 chip exposes a standard serial port that `meshtastic`'s `SerialInterface` reads directly, no custom wiring needed. USB over UART-GPIO because the anchor is co-located with that machine anyway (no reason to add a second wireless hop - Bluetooth or WiFi - on top of the LoRa link this whole system already depends on), and it powers the board for free. This is *not* the Raspberry Pi: in the current architecture, the Pi's role stays exactly what it already is - a dumb servo executor running `servo_udp_receiver.py`, receiving pan/tilt angle commands over UDP and driving the SG90s, with no awareness of GPS, LoRa, or bearing math. The anchor's position data flows into the laptop-side control loop, gets fused with the existing CV pipeline there, and the resulting pan/tilt commands go out over the same UDP path to the Pi as today - nothing about the Pi's role or the servo protocol changes.

**Anchor calibration procedure: two separate steps, position and heading.** GPS-derived bearing needs both nailed down before it means anything to the servos:

1. **Position (where the anchor is).** No second GPS device needed - use the tag itself. At setup, place the tag on the tripod next to the camera and let it dwell there for a few minutes rather than grabbing the first fix (GPS noise is roughly zero-mean, so a multi-minute average lands closer to the true position than one instantaneous sample). Set that averaged reading as the anchor's Fixed Position, then move the tag to the surfer for the session. This reuses hardware you already have instead of a second GPS chip, a phone reading, or a map lookup.
2. **Heading (which way the tripod's pan-zero actually points).** Position alone doesn't give this - a magnetometer does. A cheap breakout (QMC5883L/HMC5883L-class, a few dollars, wires in over I2C - SDA/SCL plus power, four wires total) reads magnetic north directly. One gotcha: it reads *magnetic* north, not *true* north, and the difference (magnetic declination) varies by location - a few degrees to, in parts of Alaska, over 15° across the US, not negligible for pointing accuracy. Look up the declination for the beach's coordinates once (NOAA has a free calculator) and bake that fixed offset into the heading calculation at setup, rather than discovering a consistent pointing bias later without knowing why.

Both are one-time, per-session setup steps, not something the system needs to redo continuously - the tripod doesn't move once planted, so neither its position nor its heading should need re-measuring mid-session.

**Placement:** body-worn (armband/ankle, matching Soloshot's proven form factor) over board-mounted, despite the board being an architecturally easier attach point - during a wipeout the board and surfer often separate, and tracking should follow the person, not an unmanned floating board.

## Sources

- [UWB Frequencies, Channels, Bandwidth, and EIRP Explained - RF Wireless World](https://www.rfwireless-world.com/Terminology/UWB-Frequencies-channels-UWB-bandwidth-UWB-EIRP.html)
- [FCC UWB Emission Limits - Ultra-Wideband Communications Fundamentals](https://www.oreilly.com/library/view/ultra-wideband-communications-fundamentals/0131463268/0131463268_ch01lev1sec10.html)
- [Inpixon nanoANQ Chirp - UWB Anchors for RTLS](https://www.inpixon.com/technology/rtls/anchors)
- [ESP32 DW3000 UWB Module Achieving 500m Range - how2electronics](https://how2electronics.com/esp32-dw3000-uwb-module-achieving-500m-range/)
- [Makerfabs ESP32 UWB DW3000 - GitHub](https://github.com/Makerfabs/Makerfabs-ESP32-UWB-DW3000)
- [DWM3000 UWB Module Delivers 10cm Accuracy - Symmetry Electronics](https://www.symmetryelectronics.com/blog/dwm3000-uwb-module-delivers-10cm-accuracy-symmetry-blog/)
- [Angle of Arrival and Centimeter Distance Estimation on a Smart UWB Sensor Node - arXiv](https://arxiv.org/pdf/2312.13672)
- [DW3000 Datasheet - Qorvo/Mouser](https://www.mouser.com/pdfDocs/DW3000DataSheet5.pdf)
- [All Decawave products show discontinued on DigiKey - Qorvo Tech Forum](https://forum.qorvo.com/t/all-decawave-products-show-to-be-discontinued-on-digikey/8456)
- [DW3120 - Qorvo](https://www.qorvo.com/products/p/DW3120)
- [DWM3001CDK AoA capabilities and MCU integration - Qorvo Tech Forum](https://forum.qorvo.com/t/dwm3001cdk-aoa-capabilities-and-mcu-integration/24465)
- [Low-Profile Triple-Element Antenna for UWB Indoor Localization - triple-element AoA azimuth/elevation](https://www.jees.kr/upload/pdf/jees-2023-1-r-145.pdf)
- [Makerfabs MaUWB_STM32 AOA Development Kit](https://www.makerfabs.com/mauwb-stm32-aoa-development-kit.html)
- [Makerfabs ESP32 UWB DW3000 (plain ranging module)](https://www.makerfabs.com/esp32-uwb-dw3000.html)
- [Skylab - Recommend 5 Kinds of UWB Ranging and Positioning Modules](https://www.skylabmodule.com/recommend-5-kinds-of-uwb-ranging-and-positioning-modules/)
- [u-blox NEO-M8 Datasheet](https://content.u-blox.com/sites/default/files/NEO-M8_DataSheet_(UBX-13003366).pdf)
- [LoRa RF Module Sensitivity and Range Benchmarks (SX1262 vs SX1276) - IC Online](https://www.ic-online.com/blog/post/lora-rf-module-sensitivity-and-range-benchmarks-side-by-side-field-test-data-for-sx1262-vs-sx1276)
- [Soloshot Official](https://soloshot.com/)
- [Soloshot 3 Review & Tips - da Surf Engine](https://www.dasurfengine.com/blog/soloshot-3-review-tips-tricks-surf-training-benefits/)
- [Soloshot Trustpilot Reviews](https://www.trustpilot.com/review/soloshot.com)
- [Soloshot BBB Complaints](https://www.bbb.org/us/ca/san-diego/profile/drone-photography/soloshot-1126-1000063823/complaints)
- [XbotGo Chameleon](https://xbotgo.com/pages/xbotgo-chameleon)
- [XbotGo Chameleon Review - The Gadgeteer](https://the-gadgeteer.com/2025/10/09/xbotgo-chameleon-review-your-personal-ai-sports-cameraman/)
- [Move'N See PIXIO/PIXEM](https://shop.movensee.com/en/)
- [RocX AI Camera - PetaPixel](https://petapixel.com/2025/11/26/this-ai-powered-camera-auto-tracks-subjects-and-has-a-1750mm-zoom-lens/)
- [Flowstate AI Wave Pool Technology](https://www.surfertoday.com/surfing/flowstate-ai-technology-tracks-surfers-in-wave-pools)
- [Flowstate AI - Tracks Magazine](https://tracksmag.com.au/how-ai-is-used-by-flowstate-to-monitor-surfing-performance)
- [Surfline Intelligent Surf Cameras](https://medium.com/surfline-labs/intelligent-surf-cameras-fce6e7e3d03e)
- [Machine Learning Surfing - Oliver Ricken](https://medium.com/@2oliver.ricken/machine-learning-surfing-15b2ad1158c4)
- [ML Surf Cameras - Surfline Labs](https://medium.com/surfline-labs/machine-learning-surf-cameras-c6b4f8bd3340)
- [Pan-Tilt Tracking Camera (YOLOv8) - GitHub](https://github.com/maxboels/TrackingPanTiltCam)
- [AI Vision Tracker - Instructables](https://www.instructables.com/Vision-Tracker-AI-Powered-Smart-Tracking-Camera/)
- [Pan/Tilt Face Tracking with RPi - PyImageSearch](https://pyimagesearch.com/2019/04/01/pan-tilt-face-tracking-with-a-raspberry-pi-and-opencv/)
- [Soloshot Alternatives - Horse Rookie](https://horserookie.com/soloshot-alternatives/)
- [OBSBOT Tiny Series](https://www.obsbot.com/obsbot-tiny-4k-webcam)
- [Best AI Auto-Tracking Cameras 2025 - XbotGo](https://xbotgo.com/blogs/buying-guide/auto-tracking-cameras-for-sports)
- [Sports Camera Tracking Guide - ARwall](https://arwall.co/blogs/arwall-blogs/sports-camera-tracking)
- [Waterproof Pan-Tilt Mechanism - Oz Robotics](https://ozrobotics.com/shop/waterproof-pan-tilt-mechanism-pt-mech-h2o/)
- [Heavy Duty Pan-Tilt - Bit CCTV](https://www.bit-cctv.com/products/heavy-duty-pan-tilt-head-positioner/)
- [Sony a6700 Specifications - DPReview](https://www.dpreview.com/products/sony/slrs/sony_a6700/specifications)
- [Sony a6700 Review - DPReview](https://www.dpreview.com/reviews/sony-a6700-review)
- [Sony Camera Remote SDK](https://support.d-imaging.sony.co.jp/app/sdk/en/index.html)
- [Sony Camera Remote SDK Developer Platform](https://crsdk.app/)
- [Sony a6700 Overheating Fixes - 4K Shooters](https://www.4kshooters.net/2023/11/14/how-to-fix-overheating-on-the-sony-a6700-and-zv-e1/)
- [Sony a6700 Long-Term Recording - DPReview Forums](https://www.dpreview.com/forums/threads/sony-6700-long-term-recordings.4777655/)
- [Sony a6700 Recording Limits](https://www.recordinglimits.com/sony-alpha-6700/)
- [Sony a6700 + 200-600mm Discussion - DPReview Forums](https://www.dpreview.com/forums/threads/anyone-using-a-a6700-with-a-200-600g-lens.4738665/)
- [Best Telephoto Lenses for Sony a6700 - Alpha Shooters](https://www.alphashooters.com/cameras/sony-a6700/best-lenses/)
- [Sony E 70-350mm + a6700 - Camera Decision](https://cameradecision.com/camera-lens/Sony-Alpha-a6700-with-Sony-E-70-350mm-F4.5-6.3-G-OSS-lens)
