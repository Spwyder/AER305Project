# Spar Design Definitions for `evaluation.py`

This file defines every wing-spar design to run through `evaluation.py`. Each design is a drop-in replacement for the **design-parameter block** of the script: everything between the two `#=====` marker lines, which is the line after `#design parameters to change!` through the line before the closing `#=====`. Nothing outside that block changes between designs.

All dimensions are fractions of the local chord `c = chord(x)` (ft) unless noted. The wingbox envelope is **0.65c wide (chordwise, drag/thrust direction) by 0.1c tall (lift direction)** for every design.

---

## How to run all designs

1. Keep the original `evaluation.py` untouched. For each design below, make a copy (e.g. `eval_D1.py`) and replace the lines strictly between the two `#=====...` marker lines with that design's code block.
2. In each copy:
   - add `import matplotlib; matplotlib.use("Agg")` before `import matplotlib.pyplot as plt` (so it runs headless),
   - change `plt.savefig("spar_summary.png", ...)` to `plt.savefig("spar_summary_<ID>.png", ...)` (e.g. `spar_summary_D1.png`).
3. Run each copy and collect the printed result plus the report-sheet values: best engine position, governing load case, minimum FS, critical location, spar weight/cost, static tip/engine deflection, flight tip deflection, and stringer buckling FS (only shown for designs with stringers).
4. Produce a comparison table across all designs (one row per design).

Requirements: numpy ≥ 2.0 (the script uses `np.trapezoid`), scipy, matplotlib.

### Conventions the script expects (already followed below)

| Function | Meaning |
|---|---|
| `I(x)` | Second moment about the horizontal centroidal axis, for lift/weight bending (Iz). |
| `It(x)` | Second moment about the vertical centroidal axis, for drag/thrust bending (Iy). |
| `h(x)` | `(+top, −bottom)` distance from centroid to the extreme fiber in the lift direction. |
| `ht(x)` | `(+front, −back)` distance from centroid to the extreme fiber in the chordwise direction. These include stringers when they stick out farther than the beams. |
| `area(x)` | Total cross-sectional area of spar material, stringers included. |
| `strDistances(x)` | 2×n array. Row 0 holds the vertical (y) offsets of each stringer centroid, which feed `I`. Row 1 holds the chordwise (z) offsets, which feed `It`. `nStringers` = number of columns. |
| `strA(x)` | Area of ONE stringer. |
| `strI(x, arr)`, `strIt(x, arr)` | Stringer contribution to I / It. The first term is `nStringers × (own-axis I of one stringer)`, and the second is the parallel-axis term. Calling them with `cleverSol = [[0],[0]]` returns just the own-axis term, which the buckling check uses. |

Material for all designs: **aluminum**, E = 10.2×10⁶ psi, ρ = 0.100 lb/in³, σ_Y = 40 ksi, $10/lb. Rib layout is the same for all designs: 4 ribs at x = 0, 33.83 ft, the engine (placeholder, moved to the best l_e by the script), and 117.84 ft.

---

## Design summary

| ID | Name | Spar members | Stringers | Source |
|---|---|---|---|---|
| D1 | 1 I-beam | 1 I-beam, centered | none | Designs.zip (wingbox, single I) |
| D2 | 1 I-beam + 4 stringers | 1 I-beam, centered | 4 × (0.01c × 0.01c), at z = ±0.125c (same positions as D4) | Designs.zip (single I + stringers) |
| D3 | 3 I-beams | 3 I-beams, centers at z = −0.25c, 0, +0.25c | none | Chat image and current `evaluation.py`; Group_Project.pdf p.16–18 |
| D4 | 3 I-beams + 4 stringers | Same as D3 | 4 × (0.01c × 0.01c), centered in the 0.1c flange gaps | Designs.zip (three I + stringers) |
| D5 | 2 I-beams | 2 I-beams (thin flange), centers at z = ±0.135c | none | Progress_z.pdf (orange terms dropped) |
| D6 | 2 I-beams + 4 stringers | Same as D5 | 4 × (0.005c × 0.005c), in the 4 box corners | Progress_z.pdf (full) |

### Geometry details

**Standard I-beam (D1–D4):** flanges 0.15c wide × 0.025c thick, web 0.005c thick × 0.05c tall, total height 0.1c (fills the box). One I-beam has area 0.00775c². The flange centroid is 0.0375c from the I-beam centroid.

**Thin-flange I-beam (D5, D6):** flanges 0.12c wide × 0.01c thick, web 0.008c thick × 0.08c tall, total height 0.1c. One I-beam has area 0.00304c². The flange centroid is 0.045c from the centroid. Chordwise layout across the box is 0.13c gap | 0.12c beam | 0.15c gap | 0.12c beam | 0.13c gap = 0.65c, so the beam centers are at ±0.135c. The outer flange tips are at ±0.195c.

**D2 stringer placement:** moved to the D4 stringer positions so the two designs compare directly. The stringers sit against the top and bottom skins with centers at y = ±0.045c and z = ±0.125c. The outer stringer face, at z = ±0.13c, is now the chordwise extreme fiber (the flange tips are at ±0.075c).

**D4 stringer placement:** centered in the two 0.1c gaps between flanges, against the skins. The centers are at y = ±0.045c and z = ±0.125c. These stringers sit inside the outer flange tips (±0.325c), so the extreme fibers don't change.

**D6 stringer placement:** in the four box corners (labelled 7–10 in Progress_z). The centers are at y = ±0.0475c and z = ±0.3225c. The outer faces sit at the box edges (±0.05c, ±0.325c), so `ht` becomes ±0.325c.

### Notes on the source hand calcs (Progress_z.pdf)

- In the Progress_z hand calc, the **own-axis (bh³/12) terms are swapped** between Iy and Ix for both the flanges and the webs. For example, the flange term about the vertical axis is written (0.12c)(0.01c)³/12 where it should be (0.01c)(0.12c)³/12. The code below uses the correct terms. The parallel-axis distances (0.135c, 0.045c, 0.3225c, 0.0475c) and the area match the hand calc.
- Several distances are written without the leading zero (e.g. "0.45" and "0.4475"). They're read as 0.045c and 0.0475c.

### Expected section properties (for a quick sanity check, per c⁴ or c²)

The section properties in the table below are the stringer-inclusive totals that `I(x)`, `It(x)` and `area(x)` should return, divided by c⁴ or c². Check these before trusting any run.

| ID | I / c⁴ | It / c⁴ | A / c² | h / c | ht / c | nStringers |
|---|---|---|---|---|---|---|
| D1 | 1.0990e-5 | 1.4063e-5 | 0.00775 | 0.05 | 0.075 | 0 |
| D2 | 1.1803e-5 | 2.0316e-5 | 0.00815 | 0.05 | 0.130 | 4 |
| D3 | 3.2969e-5 | 1.0109e-3 | 0.02325 | 0.05 | 0.325 | 0 |
| D4 | 3.3782e-5 | 1.0172e-3 | 0.02365 | 0.05 | 0.325 | 4 |
| D5 | 1.0443e-5 | 1.1657e-4 | 0.00608 | 0.05 | 0.195 | 0 |
| D6 | 1.0669e-5 | 1.2698e-4 | 0.00618 | 0.05 | 0.325 | 4 |

All six blocks have been checked to run end-to-end in `evaluation.py` without errors.

---

## Design code blocks

Each block replaces everything between the two `#=====` lines in `evaluation.py`.

### D1 — Single I-beam, no stringers

```python
# DESIGN: D1
rhoSpar = 0.1*12**3 #density of spar material in lb/ft^3 (aluminum)
E = 10.2*144*10**6 #young's modulus in lbf/ft^2
stressYield = 144*40*10**3#yield strength of material in lbf/ft^2
pricePerPound = 10 #price per pound of material

#return 2xn matrix containing the relevant distances for I and It
def strDistances(x):
  return np.array([[],[]])
nStringers = np.shape(strDistances(0)[0])[0]
def strA(x):
  return 0
def strI(x,arr):
  return nStringers*0 + strA(x)*np.sum(arr[0]**2, axis=0)
def strIt(x,arr):
  return nStringers*0 + strA(x)*np.sum(arr[1]**2,axis =0)

ribLocations = np.array([0,33.83,20*lWing/halfSpan,117.84]) #locations of ribs (spanwise)
def ribsWeight(arr):
  return chord(arr)**2*0.65*0.1*0.005/12*rhoSpar-area(arr)*0.005/12*rhoSpar# return array of ribweights

def I(x): #second moment of area for lift and weight direction (Iz), one centered I-beam
  c = chord(x)
  return (2*((0.15*c)*(0.025*c)**3/12
             + (0.15*c*0.025*c)*(0.05*c/2 + 0.025*c/2)**2)
          + (0.005*c)*(0.05*c)**3/12)
def It(x): #second moment of area for thrust and drag direction (Iy), centered so no parallel-axis term
  c = chord(x)
  return 2*(0.025*c)*(0.15*c)**3/12 + (0.05*c)*(0.005*c)**3/12
def h(x): #distance from centroid to top and bottom faces
  return 0.05*chord(x),-0.05*chord(x)
def ht(x): #distance from centroid to front and back faces (flange tips)
  return 0.075*chord(x),-0.075*chord(x)
def area(x): #cross-sectional area
  c = chord(x)
  return 2*(0.15*c)*(0.025*c) + (0.05*c)*(0.005*c)
```

### D2 — Single I-beam + 4 stringers (0.01c square, at z = ±0.125c like D4)

```python
# DESIGN: D2
rhoSpar = 0.1*12**3 #density of spar material in lb/ft^3 (aluminum)
E = 10.2*144*10**6 #young's modulus in lbf/ft^2
stressYield = 144*40*10**3#yield strength of material in lbf/ft^2
pricePerPound = 10 #price per pound of material

sStr = 0.01 #stringer side length as fraction of chord

#return 2xn matrix containing the relevant distances for I and It
def strDistances(x): #row 0: vertical offsets (for I), row 1: chordwise offsets (for It)
  c = chord(x)
  return np.array([[ 0.045*c,  0.045*c, -0.045*c, -0.045*c],
                   [ 0.125*c, -0.125*c,  0.125*c, -0.125*c]])
nStringers = np.shape(strDistances(0)[0])[0]
def strA(x): #area of one stringer
  return (sStr*chord(x))**2
def strI(x,arr):
  return nStringers*(sStr*chord(x))**4/12 + strA(x)*np.sum(arr[0]**2, axis=0)
def strIt(x,arr):
  return nStringers*(sStr*chord(x))**4/12 + strA(x)*np.sum(arr[1]**2,axis =0)

ribLocations = np.array([0,33.83,20*lWing/halfSpan,117.84]) #locations of ribs (spanwise)
def ribsWeight(arr):
  return chord(arr)**2*0.65*0.1*0.005/12*rhoSpar-area(arr)*0.005/12*rhoSpar# return array of ribweights

def I(x): #second moment of area for lift and weight direction (Iz)
  c = chord(x)
  return ((2*((0.15*c)*(0.025*c)**3/12
              + (0.15*c*0.025*c)*(0.05*c/2 + 0.025*c/2)**2)
           + (0.005*c)*(0.05*c)**3/12)
          + strI(x, strDistances(x)))
def It(x): #second moment of area for thrust and drag direction (Iy)
  c = chord(x)
  return (2*(0.025*c)*(0.15*c)**3/12 + (0.05*c)*(0.005*c)**3/12
          + strIt(x, strDistances(x)))
def h(x): #distance from centroid to top and bottom faces
  return 0.05*chord(x),-0.05*chord(x)
def ht(x): #distance from centroid to front and back faces (outer face of stringers, 0.125c + 0.005c)
  return 0.13*chord(x),-0.13*chord(x)
def area(x): #cross-sectional area
  c = chord(x)
  return 2*(0.15*c)*(0.025*c) + (0.05*c)*(0.005*c) + nStringers*strA(x)
```

### D3 — Three I-beams, no stringers (current script)

```python
# DESIGN: D3
rhoSpar = 0.1*12**3 #density of spar material in lb/ft^3 (aluminum)
E = 10.2*144*10**6 #young's modulus in lbf/ft^2
stressYield = 144*40*10**3#yield strength of material in lbf/ft^2
pricePerPound = 10 #price per pound of material

#return 2xn matrix containing the relevant distances for I and It
def strDistances(x):
  return np.array([[],[]])
nStringers = np.shape(strDistances(0)[0])[0]
def strA(x):
  return 0
def strI(x,arr):
  return nStringers*0 + strA(x)*np.sum(arr[0]**2, axis=0)
def strIt(x,arr):
  return nStringers*0 + strA(x)*np.sum(arr[1]**2,axis =0)

ribLocations = np.array([0,33.83,20*lWing/halfSpan,117.84]) #locations of ribs (spanwise)
def ribsWeight(arr):
  return chord(arr)**2*0.65*0.1*0.005/12*rhoSpar-area(arr)*0.005/12*rhoSpar# return array of ribweights

def I(x): #second moment of area for lift and weight direction (Iz)
  c = chord(x)
  return 3*(2*((0.15*c)*(0.025*c)**3/12
               + (0.15*c*0.025*c)*(0.05*c/2 + 0.025*c/2)**2)
            + (0.005*c)*(0.05*c)**3/12)
def It(x): #second moment of area for thrust and drag direction (Iy)
  c = chord(x)
  return (3*(2*(0.025*c)*(0.15*c)**3/12 + (0.05*c)*(0.005*c)**3/12)
          + 2*(2*(0.15*c)*(0.025*c) + (0.05*c)*(0.005*c))*(0.25*c)**2)
def h(x): #distance from centroid to top and bottom faces
  return 0.05*chord(x),-0.05*chord(x)
def ht(x): #distance from centroid to front and back faces
  return 0.25*chord(x) + 0.15*chord(x)/2,-0.25*chord(x) -0.15*chord(x)/2
def area(x): #cross-sectional area
  c = chord(x)
  return 3*(2*(0.15*c)*(0.025*c) + (0.05*c)*(0.005*c))
```

### D4 — Three I-beams + 4 stringers (0.01c square, in flange gaps)

```python
# DESIGN: D4
rhoSpar = 0.1*12**3 #density of spar material in lb/ft^3 (aluminum)
E = 10.2*144*10**6 #young's modulus in lbf/ft^2
stressYield = 144*40*10**3#yield strength of material in lbf/ft^2
pricePerPound = 10 #price per pound of material

sStr = 0.01 #stringer side length as fraction of chord

#return 2xn matrix containing the relevant distances for I and It
def strDistances(x): #row 0: vertical offsets (for I), row 1: chordwise offsets (for It)
  c = chord(x)
  return np.array([[ 0.045*c,  0.045*c, -0.045*c, -0.045*c],
                   [ 0.125*c, -0.125*c,  0.125*c, -0.125*c]])
nStringers = np.shape(strDistances(0)[0])[0]
def strA(x): #area of one stringer
  return (sStr*chord(x))**2
def strI(x,arr):
  return nStringers*(sStr*chord(x))**4/12 + strA(x)*np.sum(arr[0]**2, axis=0)
def strIt(x,arr):
  return nStringers*(sStr*chord(x))**4/12 + strA(x)*np.sum(arr[1]**2,axis =0)

ribLocations = np.array([0,33.83,20*lWing/halfSpan,117.84]) #locations of ribs (spanwise)
def ribsWeight(arr):
  return chord(arr)**2*0.65*0.1*0.005/12*rhoSpar-area(arr)*0.005/12*rhoSpar# return array of ribweights

def I(x): #second moment of area for lift and weight direction (Iz)
  c = chord(x)
  return (3*(2*((0.15*c)*(0.025*c)**3/12
                + (0.15*c*0.025*c)*(0.05*c/2 + 0.025*c/2)**2)
             + (0.005*c)*(0.05*c)**3/12)
          + strI(x, strDistances(x)))
def It(x): #second moment of area for thrust and drag direction (Iy)
  c = chord(x)
  return ((3*(2*(0.025*c)*(0.15*c)**3/12 + (0.05*c)*(0.005*c)**3/12)
           + 2*(2*(0.15*c)*(0.025*c) + (0.05*c)*(0.005*c))*(0.25*c)**2)
          + strIt(x, strDistances(x)))
def h(x): #distance from centroid to top and bottom faces
  return 0.05*chord(x),-0.05*chord(x)
def ht(x): #distance from centroid to front and back faces (outer flange tips; stringers are inboard)
  return 0.325*chord(x),-0.325*chord(x)
def area(x): #cross-sectional area
  c = chord(x)
  return 3*(2*(0.15*c)*(0.025*c) + (0.05*c)*(0.005*c)) + nStringers*strA(x)
```

### D5 — Two thin-flange I-beams, no stringers

```python
# DESIGN: D5
rhoSpar = 0.1*12**3 #density of spar material in lb/ft^3 (aluminum)
E = 10.2*144*10**6 #young's modulus in lbf/ft^2
stressYield = 144*40*10**3#yield strength of material in lbf/ft^2
pricePerPound = 10 #price per pound of material

#return 2xn matrix containing the relevant distances for I and It
def strDistances(x):
  return np.array([[],[]])
nStringers = np.shape(strDistances(0)[0])[0]
def strA(x):
  return 0
def strI(x,arr):
  return nStringers*0 + strA(x)*np.sum(arr[0]**2, axis=0)
def strIt(x,arr):
  return nStringers*0 + strA(x)*np.sum(arr[1]**2,axis =0)

ribLocations = np.array([0,33.83,20*lWing/halfSpan,117.84]) #locations of ribs (spanwise)
def ribsWeight(arr):
  return chord(arr)**2*0.65*0.1*0.005/12*rhoSpar-area(arr)*0.005/12*rhoSpar# return array of ribweights

#I-beam: flanges 0.12c x 0.01c, web 0.008c x 0.08c, beam centers at z = +/-0.135c
def I(x): #second moment of area for lift and weight direction (Iz)
  c = chord(x)
  return 2*(2*((0.12*c)*(0.01*c)**3/12 + (0.12*c*0.01*c)*(0.045*c)**2)
            + (0.008*c)*(0.08*c)**3/12)
def It(x): #second moment of area for thrust and drag direction (Iy)
  c = chord(x)
  return (2*(2*(0.01*c)*(0.12*c)**3/12 + (0.08*c)*(0.008*c)**3/12)
          + 2*(2*(0.12*c)*(0.01*c) + (0.08*c)*(0.008*c))*(0.135*c)**2)
def h(x): #distance from centroid to top and bottom faces
  return 0.05*chord(x),-0.05*chord(x)
def ht(x): #distance from centroid to front and back faces (0.135c + 0.06c)
  return 0.195*chord(x),-0.195*chord(x)
def area(x): #cross-sectional area
  c = chord(x)
  return 2*(2*(0.12*c)*(0.01*c) + (0.08*c)*(0.008*c))
```

### D6 — Two thin-flange I-beams + 4 corner stringers (0.005c square)

```python
# DESIGN: D6
rhoSpar = 0.1*12**3 #density of spar material in lb/ft^3 (aluminum)
E = 10.2*144*10**6 #young's modulus in lbf/ft^2
stressYield = 144*40*10**3#yield strength of material in lbf/ft^2
pricePerPound = 10 #price per pound of material

sStr = 0.005 #stringer side length as fraction of chord

#return 2xn matrix containing the relevant distances for I and It
def strDistances(x): #row 0: vertical offsets (for I), row 1: chordwise offsets (for It); box corners
  c = chord(x)
  return np.array([[ 0.0475*c,  0.0475*c, -0.0475*c, -0.0475*c],
                   [ 0.3225*c, -0.3225*c,  0.3225*c, -0.3225*c]])
nStringers = np.shape(strDistances(0)[0])[0]
def strA(x): #area of one stringer
  return (sStr*chord(x))**2
def strI(x,arr):
  return nStringers*(sStr*chord(x))**4/12 + strA(x)*np.sum(arr[0]**2, axis=0)
def strIt(x,arr):
  return nStringers*(sStr*chord(x))**4/12 + strA(x)*np.sum(arr[1]**2,axis =0)

ribLocations = np.array([0,33.83,20*lWing/halfSpan,117.84]) #locations of ribs (spanwise)
def ribsWeight(arr):
  return chord(arr)**2*0.65*0.1*0.005/12*rhoSpar-area(arr)*0.005/12*rhoSpar# return array of ribweights

#I-beam: flanges 0.12c x 0.01c, web 0.008c x 0.08c, beam centers at z = +/-0.135c
def I(x): #second moment of area for lift and weight direction (Iz)
  c = chord(x)
  return (2*(2*((0.12*c)*(0.01*c)**3/12 + (0.12*c*0.01*c)*(0.045*c)**2)
             + (0.008*c)*(0.08*c)**3/12)
          + strI(x, strDistances(x)))
def It(x): #second moment of area for thrust and drag direction (Iy)
  c = chord(x)
  return ((2*(2*(0.01*c)*(0.12*c)**3/12 + (0.08*c)*(0.008*c)**3/12)
           + 2*(2*(0.12*c)*(0.01*c) + (0.08*c)*(0.008*c))*(0.135*c)**2)
          + strIt(x, strDistances(x)))
def h(x): #distance from centroid to top and bottom faces
  return 0.05*chord(x),-0.05*chord(x)
def ht(x): #distance from centroid to front and back faces (corner stringers reach the box edge)
  return 0.325*chord(x),-0.325*chord(x)
def area(x): #cross-sectional area
  c = chord(x)
  return 2*(2*(0.12*c)*(0.01*c) + (0.08*c)*(0.008*c)) + nStringers*strA(x)
```
