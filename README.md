# BuildSafe: Bridge Load Challenge

A Civil Engineering educational game focused on simplified beam design, structural safety, deflection, and cost efficiency.

## Included versions

- `bridge_load_challenge.py` — required **Python + Tkinter** desktop application.
- `index.html` — lightweight browser demo for Vercel deployment.
- `PROJECT_PROPOSAL.md` — project proposal, GUI layout, user flow, and engineering model.

## Engineering model

The game models a simply supported rectangular beam with a point load at midspan using:

- `M = PL / 4`
- `I = bh^3 / 12`
- `σ = Mc / I`
- `δ = PL^3 / (48EI)`
- Deflection limit: `L / 360`

> Educational use only. These simplified values and cost factors must not be used for real structural design or construction.

## Run the Tkinter version

```bash
python bridge_load_challenge.py
```

Python 3 with Tkinter is required.

## Web demo

The repository root contains `index.html`, so Vercel can deploy it as a static site with no build command.
