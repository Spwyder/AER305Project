# DESIGN: D2-T (single I-beam + 4 T-stringers at z = +/-0.125c, 84 ribs)
rhoSpar = 0.1*12**3 #density of spar material in lb/ft^3 (aluminum)
E = 10.2*144*10**6 #young's modulus in lbf/ft^2
stressYield = 144*40*10**3#yield strength of material in lbf/ft^2
pricePerPound = 10 #price per pound of material

#T-stringer geometry as fractions of chord: flange lies flat on the skin, stem points inward
bF = 0.020 #flange width
tF = 0.003 #flange thickness
hS = 0.012 #stem height (below the flange)
tS = 0.003 #stem thickness
aT = bF*tF + hS*tS #area of one T per c^2
yBarT = (bF*tF*(tF/2) + hS*tS*(tF + hS/2))/aT #T centroid depth measured from the skin, per c
IxT = (bF*tF**3/12 + bF*tF*(yBarT - tF/2)**2
       + tS*hS**3/12 + hS*tS*(tF + hS/2 - yBarT)**2) #own I of one T about its horizontal centroidal axis, per c^4
IyT = tF*bF**3/12 + hS*tS**3/12 #own I of one T about its vertical centroidal axis, per c^4
yStr = 0.05 - yBarT #vertical offset of T centroid from box centroid, per c
zStr = 0.125 #chordwise offset of T centerline from box centroid, per c

#return 2xn matrix containing the relevant distances for I and It
def strDistances(x): #row 0: vertical offsets (for I), row 1: chordwise offsets (for It)
  c = chord(x)
  return np.array([[ yStr*c,  yStr*c, -yStr*c, -yStr*c],
                   [ zStr*c, -zStr*c,  zStr*c, -zStr*c]])
nStringers = np.shape(strDistances(0)[0])[0]
def strA(x): #area of one stringer
  return aT*chord(x)**2
def strI(x,arr): #own-axis term + parallel-axis term
  return nStringers*IxT*chord(x)**4 + strA(x)*np.sum(arr[0]**2, axis=0)
def strIt(x,arr):
  return nStringers*IyT*chord(x)**4 + strA(x)*np.sum(arr[1]**2,axis =0)

ribLocations = np.concatenate((np.array([0,33.83,20*lWing/halfSpan,117.84]), #4 hard-coded ribs (engine placeholder is the 3rd)
                               np.linspace(0, lWing, 82)[1:-1])) #plus 80 evenly spaced ribs between root and tip (lWing/81 = 1.455 ft apart)
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
def h(x): #distance from centroid to top and bottom faces (T flange sits on the skin)
  return 0.05*chord(x),-0.05*chord(x)
def ht(x): #distance from centroid to front and back faces (outer tip of T flange, 0.125c + 0.010c)
  return (zStr + bF/2)*chord(x),-(zStr + bF/2)*chord(x)
def area(x): #cross-sectional area
  c = chord(x)
  return 2*(0.15*c)*(0.025*c) + (0.05*c)*(0.005*c) + nStringers*strA(x)
