# DESIGN: <your design name>
# Blank design file for the Spar Design Evaluator. Replace every FILL_IN, then upload this file.
# Units are ft and lbf. Dimensions are usually written as fractions of the local chord c = chord(x).
# You can use np, chord(x), lWing, halfSpan, cTip and cRoot.

#material (aluminum shown; titanium is 0.1628 lb/in^3, 16.8e6 psi, v = 0.32, 110 ksi, $50/lb)
rhoSpar = 0.1*12**3 #density of spar material in lb/ft^3 (lb/in^3 times 12^3)
E = 10.2*144*10**6 #young's modulus in lbf/ft^2 (psi times 144)
v = 0.33 #poisson's ratio
G = E/(2*(1+v)) #modulus of rigidity in lbf/ft^2
stressYield = 144*40*10**3 #yield strength of material in lbf/ft^2 (psi times 144)
pricePerPound = 10 #price per pound of material

#stringers: leave this section as is for a design with no stringers
def strDistances(x): #2xn array of stringer centroid offsets from the box centroid. Row 0: vertical (y), row 1: chordwise (z)
  c = chord(x)
  return np.array([[],[]]) #e.g. np.array([[0.045*c, 0.045*c, -0.045*c, -0.045*c], [0.125*c, -0.125*c, 0.125*c, -0.125*c]])
nStringers = np.shape(strDistances(0)[0])[0]
def strA(x): #area of ONE stringer
  return 0 #e.g. (0.01*chord(x))**2
def strI(x,arr): #nStringers*(own I of one stringer, lift direction) + parallel-axis term
  return nStringers*0 + strA(x)*np.sum(arr[0]**2, axis=0) #replace the 0 with one stringer's own I, e.g. (0.01*chord(x))**4/12
def strIt(x,arr): #nStringers*(own I of one stringer, drag direction) + parallel-axis term
  return nStringers*0 + strA(x)*np.sum(arr[1]**2, axis=0) #replace the 0 the same way

#ribs: the 3rd location is the engine placeholder, which the script moves to the best engine position
ribLocations = np.array([0,33.83,20*lWing/halfSpan,117.84]) #add evenly spaced ribs with np.concatenate((..., np.linspace(0, lWing, N+2)[1:-1]))
def ribsWeight(arr): #weight of each rib (0.005 in thick plate filling the 0.65c x 0.1c box, minus the spar cutout)
  return chord(arr)**2*0.65*0.1*0.005/12*rhoSpar-area(arr)*0.005/12*rhoSpar

#I-beam dimensions for the angle of twist (Roark's I-section torsion), in ft
def flangeWidth(x): #flange width
  return FILL_IN #e.g. 0.15*chord(x)
def flangeThick(x): #flange thickness
  return FILL_IN #e.g. 0.025*chord(x)
def webHeight(x): #clear web height between the flanges (total height - 2*flange thickness)
  return FILL_IN #e.g. 0.05*chord(x)
def webThick(x): #web thickness
  return FILL_IN #e.g. 0.005*chord(x)
def filletRadius(x): #fillet radius where the web meets the flanges
  return FILL_IN #e.g. 0.002*chord(x)

#section properties (include the stringers)
def I(x): #second moment of area for lift and weight direction (Iz)
  c = chord(x)
  return FILL_IN + strI(x, strDistances(x))
def It(x): #second moment of area for thrust and drag direction (Iy)
  c = chord(x)
  return FILL_IN + strIt(x, strDistances(x))
def h(x): #distance from centroid to top and bottom faces (+top, -bottom)
  return FILL_IN, -FILL_IN #e.g. 0.05*chord(x), -0.05*chord(x)
def ht(x): #distance from centroid to front and back faces (+front, -back), including stringers that stick out
  return FILL_IN, -FILL_IN
def area(x): #total cross-sectional area, stringers included
  c = chord(x)
  return FILL_IN + nStringers*strA(x)
