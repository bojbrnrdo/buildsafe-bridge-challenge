# BuildSafe: Bridge Engineering Game

BuildSafe is a production-style **Civil Engineering educational game** where players design, load-test, inspect, and optimize simplified bridge girder systems.

## Version 3 Improvements

- Clear **Design → Load Test → Inspection** workflow
- Simpler controls with presets and a mission-specific suggested starting design
- More realistic bridge scene with abutments, bearings, roadway, multiple girders, truck loading, and failure cracks
- Three-stage test sequence:
  1. Bridge dead load
  2. Dynamic vehicle crossing
  3. Engineering inspection
- Inspector feedback explains exactly why a design passed or failed
- Expandable engineering calculation details for students who want the numbers

## Game Engineering Model

The browser game now includes a more realistic educational load model:

- Concrete deck dead load
- Girder self-weight based on material density
- Vehicle load with a **15% impact allowance**
- Equal load sharing across parallel girders
- Simplified strength combination: **1.2D + 1.6L**
- Service deflection using dead load + dynamic vehicle load
- Game serviceability limit: **L / 800**
- Material-specific section efficiency for:
  - Steel I-girder
  - Glulam timber
  - Aluminum box girder
- Conceptual project estimate for deck, girders, connections, and substructure allowance

The underlying beam relationships still use simplified structural mechanics such as:

- Simply supported beam bending
- `M = wL²/8 + PL/4`
- `σ = Mc/I`
- UDL and point-load deflection equations

## Game Features

- 6-project campaign from Rookie to Expert
- Steel, Glulam Timber, and Aluminum structural systems
- Adjustable girder width, depth, and girder count
- Economy, Balanced, and Heavy Duty presets
- Animated truck load test
- Strength, deflection, and budget inspection cards
- Test attempts, mission scoring, XP, player levels, and engineer rating
- Saved campaign progress in the browser
- Responsive desktop and mobile UI

## Included Versions

- `index.html` + `styles.css` + `game.js` — Vercel web game
- `bridge_load_challenge.py` — required **Python + Tkinter** academic desktop application
- `PROJECT_PROPOSAL.md` — original proposal and program specification

> **Educational use only.** BuildSafe is not a structural analysis package and is not code-compliant design software. Do not use its loads, capacities, costs, or results for real construction, permitting, or engineering decisions.

## Run the Tkinter Version

```bash
python bridge_load_challenge.py
```

## Deployment

The repository is connected to Vercel. Commits to the production branch automatically trigger a new deployment.
