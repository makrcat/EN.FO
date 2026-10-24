---
title: "EN.FO"
github: "https://github.com/makrcat/EN.FO"
description: "a BME680 environment-sensing gadget, with games! run on esp32c6"
created_at: "2026-10-24"
total_time: "24h"
---

# October 23, 2026: All the progress so far
<!-- fabricate:entry 1162 -->

## EN.FO

Moving this over from stardance...

The EN.FO is a personal project for tracking the environment when outdoors. It measures altitude (pressure), temperature, humidity, and air quality through the BME680 chip. And it also has games!

It's definitely taken over 24 hours so far in total -- the CAD, the coding, the PCB. (I'm pretty sure it's more. My vscode tracked 58 hours xd but a lot of it was testing from before.) This was my first microcontroller project, and all of the components changed throughout the project lol. The final thing uses an ESP32, a LCD screen, and a BME680 to detect the environment.

It also has limited-UI games!

## Design

As per class inheritance structure, I split each page into its own class. Each page also extends a basic page class. Game pages extend a gamepage class, to detect short/long button presses.

Uses circuitpython for UI.

<img src="https://fabricate.hackclub-assets.com/3e47cdf883c9c3612142ea7e6b835ae8b5619dec0f6acec5d2e21d32a063e8ff/image-jpeg/blarb.jpeg" width="500">

<img src="https://fabricate.hackclub-assets.com/42c26fa19bfcc3c688a191c4d8237a568c1794ad986cdc92af2cf7f4ef3e8bda/image-png/Screenshot%202026-10-23%20at%208.32.37%E2%80%AFPM.png" width="500">

<img src="https://fabricate.hackclub-assets.com/35ce6a031879425171b5ca06a6886b5d0a08e5a30d46a8e0e0e5d2c1ba819031/image-png/kicad_model.png" width="500">

<img src="https://fabricate.hackclub-assets.com/eeed687c8a82d56d2ff104aa2dc7667d4cccc6af12e08caf8425f549191babf9/image-png/CAD.png" width="500">

**Total time spent: 24h**
