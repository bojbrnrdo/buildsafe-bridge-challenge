# BuildSafe: Bridge Engineering Game

BuildSafe is a **Python + Tkinter Civil Engineering game** for designing and load-testing simplified bridge girder systems.

## Main Academic Version — Python + Tkinter

The required application is:

`bridge_load_challenge.py`

It uses Python's built-in **Tkinter** GUI toolkit and includes:

- Game-style local player profiles: Create Player / Choose Player
- Multiple player slots with separate saved progress
- Player badge, score, XP, unlocked missions, and best scores
- Main menu before gameplay
- Minimalist game HUD
- Mission brief popups
- Material, girder width, depth, and girder-count controls
- Economy / Balanced / Heavy presets
- Animated bridge scene using `tkinter.Canvas`
- Moving truck load test
- Visible bridge deflection
- Warning state near structural limits
- Cracking, partial failure, and collapse animation
- Strength, deflection, and budget checks
- Success / failure modals
- Engineering-details modal
- Campaign / project-selection modal
- Score, XP, engineer rank, and saved campaign progress

## Run the Tkinter Game

```bash
python bridge_load_challenge.py
```

Tkinter is included with most standard Python desktop installations.

## Simplified Engineering Model

The game includes:

- Concrete deck dead load
- Girder self-weight
- 15% vehicle impact allowance
- Load sharing across parallel girders
- Simplified strength combination: `1.2D + 1.6L`
- Service deflection check using `L / 800`
- Steel, timber, and aluminum material properties
- Simplified conceptual project costing

The structural mechanics use simplified simply supported beam relationships for bending stress and deflection.

> **Educational use only.** BuildSafe is not structural-analysis or code-compliant design software and must not be used for real construction or engineering decisions.

## Optional Web Demo

The HTML/CSS/JavaScript version remains in the repository as an optional Vercel showcase. It is **not** the Tkinter submission version.
