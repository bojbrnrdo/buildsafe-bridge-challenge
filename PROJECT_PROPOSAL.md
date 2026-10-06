# BuildSafe: Bridge Load Challenge

## Project Proposal

**Title:** BuildSafe: Bridge Load Challenge

**Description:**  
BuildSafe is a Python Tkinter civil-engineering educational game where users design a simplified simply supported beam. The player chooses the material and beam dimensions, then tests whether the design can carry a target load while satisfying bending stress, deflection, and budget limits.

**Target Audience:**  
Civil engineering students and beginners learning basic structural behavior, material selection, safety checks, and cost-efficiency concepts.

## GUI Layout

### Header
- Program title
- Short description
- Current round, challenge target load, budget, and total score

### Left Panel – Beam Design Inputs
- Material dropdown
- Span Length (m)
- Beam Width (mm)
- Beam Depth (mm)
- Applied Midspan Load (kN)
- **TEST DESIGN** button
- **NEW CHALLENGE** button

### Right Panel – Structural Check & Game Result
- Pass / Revise status banner
- Bending stress result
- Allowable stress
- Beam deflection result
- Deflection limit (L/360)
- Estimated cost
- Budget result
- Score feedback

## User Flow
1. Open the application.
2. Read the randomly generated target load and budget.
3. Select a material.
4. Enter span, width, depth, and applied load.
5. Click **TEST DESIGN**.
6. Review stress, deflection, and cost checks.
7. Revise the design if needed.
8. Pass the challenge and earn points.
9. Start another challenge.

## Program Specifications

### Main Features
- Randomized bridge/beam design challenges
- Material selection
- Bending-stress calculation
- Beam-deflection calculation
- Budget/cost comparison
- Pass/fail status
- Score system
- Input validation and error messages

### Python Libraries
- `tkinter` – graphical user interface
- `tkinter.ttk` – styled GUI components
- `random` – randomized challenge generation

### Data Handling
- Material properties are stored in a Python dictionary.
- User inputs are read from Tkinter variables.
- Calculations are performed in memory.
- No database is required for the basic version.

### Error Handling
- Rejects non-numeric values.
- Restricts span, beam size, and load to reasonable classroom ranges.
- Displays an error dialog when inputs are invalid.

## Engineering Model
The program uses a simplified simply supported rectangular beam with a point load at midspan:

- Maximum moment: `M = PL / 4`
- Second moment of area: `I = bh^3 / 12`
- Bending stress: `σ = Mc / I`
- Midspan deflection: `δ = PL^3 / (48EI)`
- Serviceability limit: `L / 360`

**Important:** The values and material cost factors are simplified for educational/game purposes only and must not be used for real structural design or construction decisions.
