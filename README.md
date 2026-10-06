# BuildSafe: Bridge Load Challenge

BuildSafe is a production-style **Civil Engineering educational game** where players design and load-test simplified bridge girders while balancing structural safety, serviceability, material use, and project budget.

## Game Features

- 6-mission Civil Engineering campaign
- Progressive difficulty from Rookie to Expert
- Structural Steel, Engineered Timber, and Aluminum
- Adjustable girder width, depth, and girder count
- Animated truck load testing
- Live structural utilization meter
- Bending stress and L/360 deflection checks
- Project budget constraint
- Attempts, mission scores, XP, player levels, and engineer rating
- Saved campaign progress in the browser
- Responsive production-style game interface

## Included Versions

- `index.html` + `styles.css` + `game.js` — web game deployed through Vercel
- `bridge_load_challenge.py` — required **Python + Tkinter** academic desktop application
- `PROJECT_PROPOSAL.md` — project proposal, GUI layout, user flow, and engineering model

## Simplified Engineering Model

The game uses a simply supported rectangular girder with a point load at midspan:

- `M = PL / 4`
- `I = bh³ / 12`
- `σ = Mc / I`
- `δ = PL³ / (48EI)`
- Serviceability limit: `L / 360`

The mission load is shared equally by the selected parallel girders.

> **Educational use only.** The simplified loads, material properties, cost factors, and structural model are for classroom/game use and must not be used for real construction or engineering decisions.

## Run the Tkinter Version

```bash
python bridge_load_challenge.py
```

Python 3 with Tkinter is required.

## Deployment

The repository is connected to Vercel. Pushing changes to the production branch automatically triggers a new deployment.
