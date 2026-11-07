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
