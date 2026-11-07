import numpy as np
from scipy.integrate import cumulative_trapezoid
import matplotlib.pyplot as plt

lWing = 117.84 #length of wing in ft
halfSpan = 95.8 #length of half span in ft
wTakeoff = 550000.0 #takeoff weight in lbf
liftWing = wTakeoff/2 #lift for one wing assuming n = 1
wFuel = 67013.4 #total weight of fuel in wing in lbf
wLg = 4320.0 #weight of one landing gear in lbf
wEngine = 10000.0 #weight of one engine in lbf
dLg = 0.105*lWing #distance from fuselage to landing gear in ft
cTip = 9.74 #length of chord at wing tip in ft
maxRudderTorque = 5390000.0 #max rudder torque in lbf*ft
maxEngineThrust = 90000.0 #max engine thrust in lbf\
fuselageWidth = 20.04 #fuselage width in ft
maxEngineDistance = 95.0 #max given engine distance
minEngineDistance = 20.0 #min given engine distance
dCGNoseGear = 67.0 #distance from nosegear to CG in ft
dNoseGearMainGear = 93.18-17.58 #distance from noseGear to MainGear in ft
fMainGear = (dCGNoseGear*wTakeoff)/(2*(dNoseGearMainGear)) #reaction force of main gear in lbf
cRoot = 38.94 #root chord in ft
cInt = 24.9 #chord at piecewise split in ft
yInt = 27.5 #projected distance from root to piecewise split in ft


sWing = 2062.4 #planform area in ft^2 
rhoCruise = 7.38e-4 #air density at cruising altitude in slug/ft^3
vCruise = 490*1.68781 #490 knots converted to ft/s
qCruise = 0.5*rhoCruise*vCruise**2 #dynamic pressure under cruising conditions
cd0 = 0.008755 #zero-lift drag coefficient
eOswald = 0.862 #oswald efficiency factor
AR = (2*halfSpan)**2/(2*sWing) #aspect ratio

def mac(x,a,k): #define macauly function for usage later
  return np.where(x>= a,(x- a)**k,0.0) #return (x -a)^k if x>= a, 0 otherwise. compatible with vector operations.

def chord(x): #chord length in ft at distance x along the spar
  y = x*halfSpan/lWing#convert spar distance to projected span distance
  inboard  = cRoot + (cInt- cRoot)*y/yInt #root until piecewise split
  outboard = cInt + (cTip -cInt)*(y- yInt)/(halfSpan- yInt) #piecewise split to tip
  return np.where(y <= yInt, inboard, outboard) #return inboard if before split location, outboard if after


x = np.linspace(0, lWing, 5000)   #5000 evenly spaced points from root to tip @ lWing 
leArray = np.linspace(minEngineDistance,maxEngineDistance,300) #candidate engine locations;

#design parameters to change!
#=====================================================================
import sys #design parameters are read from a separate file: python evaluation_from_file.py <design_file.py> [output.png]
designFile = sys.argv[1] #file containing only the design parameter block
outputFile = sys.argv[2] if len(sys.argv) > 2 else "spar_summary.png" #where to save the report sheet
with open(designFile) as f:
  exec(f.read()) #defines rhoSpar, E, stressYield, pricePerPound, strDistances, nStringers, strA, strI, strIt, ribLocations, ribsWeight, I, It, h, ht, area
#====================================================================

#distributed weights along the spar

pFuel = wFuel*chord(x)/np.trapezoid(chord(x),x) #fuel weight per length along wing proportional to chord 

pSpar = rhoSpar*area(x) #spar weight per length along wing

volume = np.trapezoid(area(x),x) # total spar volume in ft^3

wRib = ribsWeight(ribLocations) #array of weights corresponding to each rib
wSpar = rhoSpar*volume +np.sum(ribsWeight(ribLocations))#total spar weight in lbf

vRibDist = -np.sum(wRib[:, None]*mac(x, ribLocations[:, None], 0), axis=0) #shear from rib point loads up to x
mRibDist = -np.sum(wRib[:, None]*mac(x, ribLocations[:, None], 1), axis=0) #moment from rib point loads up to x
mRibRoot = np.sum(wRib*ribLocations) #moment of all ribs about the root


cost = wSpar*pricePerPound #total cost of design

vFuelDist = cumulative_trapezoid(-pFuel,x,initial = 0) #shear from fuel up to x
mFuelDist = cumulative_trapezoid(vFuelDist,x,initial = 0) #moment from fuel up to x
mFuelRoot = np.trapezoid(x*pFuel,x) #moment of all fuel about the root

vSparDist = cumulative_trapezoid(-pSpar,x,initial = 0) #shear from spar weight up to x
mSparDist = cumulative_trapezoid(vSparDist,x,initial = 0) #moment from spar weight up to x
mSparRoot = np.trapezoid(x*pSpar,x) #moment of all spar weight about the root


def lift(x,n): #define lift distribution based on load factor for p(x) = ax^2 +bx +c (note that b is always 0)
  a = -(3/2)*liftWing/(lWing**3) 
  c = (3/2)*liftWing/lWing
  
  return n*(a*x**2+c) 

def drag(x,n): #define drag distribution based on lift
  py = lift(x, n)
  return qCruise*sWing*cd0/lWing + py**2/(qCruise*sWing*np.pi*eOswald*AR/lWing) #return drag at a point x

def shearBendingLift(x,n,le): #shear and bending moment in the lift direction as a function of load factor, engine placement
  a = -(3/2)*liftWing/(lWing**3)
  c = (3/2)*liftWing/lWing #lift parameters redefined for usage
  vLift = (1/3)*a*x**3 + c*x #shear contribution from lift up to x
  mLift = (1/12)*a*x**4 + (1/2)*c*x**2 #moment contribution from lift up to x

  vFuel = vFuelDist #shear contribution from fuel up to x 
  mFuel = mFuelDist #moment contribution from fuel up to x
  
  vWeight = vSparDist #shear contribution from spar weight up to x 
  mWeight = mSparDist #moment contribution from spar weight up to x
  
  vF = liftWing - wFuel - wLg - wEngine - wSpar #shear reaction at fuselage, assuming to be going downward
  
  mVF = vF*x #moment contribution from fuselage shear reaction force up to x
  
  mF = (lWing*3/8)*liftWing -dLg*wLg -le*wEngine - mFuelRoot - mSparRoot - mRibRoot #moment reaction at fuselage, assuming to be going clockwise
  
  return n*(-vF + vLift +vFuel + vWeight + vRibDist -wLg*mac(x,dLg,0) -wEngine*mac(x,le,0)),n*(mLift +mF + mWeight +mFuel + mRibDist -mVF  -wLg*mac(x,dLg,1) -wEngine*mac(x,le,1)) #return shear, moment at point x
  
  
def staticShearBendingLift(x,le): #shear and bending moment in lift direction for static case
  vF = fMainGear - wLg -wEngine -wFuel - wSpar # fuselage shear reaction
  
  mVF = vF*x # moment contribution from fuselage shear reaction force up to x
  
  mF = dLg*(fMainGear-wLg) -le*wEngine - mFuelRoot - mSparRoot - mRibRoot #fuselage moment reaction
  
  vFuel = vFuelDist #shear contribution from fuel up to x
  mFuel = mFuelDist #moment  contribution from fuel up to x
  
  vWeight = vSparDist #shear contribution from spar weight up to x
  mWeight = mSparDist #moment contribution from spar weight up to x
  
  return (-vF +vFuel+ vWeight + vRibDist +(fMainGear -wLg)*mac(x,dLg,0) - wEngine*mac(x,le,0)),( mF-mVF + mFuel + mWeight + mRibDist + (fMainGear- wLg)*mac(x,dLg,1) - wEngine*mac(x,le,1)) #return shear, moment of taxxing conditions

def shearBendingDrag(x,n,le, thrust): #shear and bending in drag/thrust direction for flight cases
  D = drag(x,n)
  
  vF = thrust - np.trapezoid(D,x) #fuselage shear reaction
  mF = le*thrust - np.trapezoid(D*x,x) #fuselage moment reaction
  
  vDrag = cumulative_trapezoid(-D,x,initial = 0) #shear due to drag
  mDrag = cumulative_trapezoid(vDrag,x,initial = 0)#moment due to drag
  
  return (-vF + vDrag + thrust*mac(x,le,0)),(mF - vF*x + mDrag + thrust*mac(x,le,1)) #return shear, moment
  
def curvature(m,I): #curvature at a given point, pass in arrays of values for moment and second moment of area
  return m/ (E*I)

def deflectionCurve(M): #integrate curvature twice with initla conditions rotation(0)=0 and deflection(0)=0
  slope = cumulative_trapezoid(curvature(M,I(x)),x,initial =0)
  return cumulative_trapezoid(slope,x,initial = 0)


def engineChecks(leArray): #takes in array of engine lenghts and removes all invalid positions
  maxYawDistance = maxRudderTorque/maxEngineThrust -fuselageWidth/2
  
  valid = np.zeros_like(leArray,dtype=bool)#create corresponding array of true/false, which will say true if position is valid
  yTip = np.full_like(leArray, np.nan, dtype=float) #initialize array that will store deflection at tip for each engine placement (if deflection is no calcualted, then returns NAN)
  yEng = np.full_like(leArray, np.nan, dtype=float) #store deflection at engine location for each engine placement, see above
  yTipFlight =np.full_like(leArray, np.nan, dtype=float) #store deflection at wingtip for the flying case, see above x2
  
  leMax = min(maxEngineDistance,maxYawDistance) #determine maximum engine distance based on safety concerns and yawing
  
  for j, le in enumerate(leArray):
    if le < minEngineDistance or le > leMax: #check that value stays within allowable range (minimum defined distance and max distance as defined above)
      continue #loop repeats, engine length j stays false at this index
    
    V,M = staticShearBendingLift(x,le)
    deflection = deflectionCurve(M) #find deflection for each point along wing
    
    yTip[j] = deflection[-1] #obtain deflection at tip
    yEng[j] = np.interp(le,x,deflection) #interpolate to obtain deflection value at exactly engine location
    
    V,Mflight = shearBendingLift(x, 2.5, le) #worst positive lifting case
    yTipFlight[j] = deflectionCurve(Mflight)[-1] #tip deflection in flight
    
    valid[j] = (yTip[j] > -7) and (yEng[j]) > -4 and (yTipFlight[j] < 15) #check to make sure deflections are within limits for static condition and flying condition
  return leArray[valid],yTip,yEng, yTipFlight

def maxStress(Mz,My,x): #determine max bending stress along the wing by checking "corners" of the beams, where both maximum thrust/drag bending and lift/weight bending will occur
  hTop, hBottom = h(x) #top and bottom of beam in lift/weight direction relative to cnetroidal axis
  zTop, zBottom = ht(x) #top and bottom (front and bacK) of beam in drag/thrust direction relative to centroidal axis
  corners = [(hTop, zTop),(hTop, zBottom),(hBottom, zTop), (hBottom,zBottom)] #take every combination to test; some will work against each other others will conribute together
  sigma = np.array([-Mz*y/I(x)-My*z/It(x) for y, z in corners]) #array of combined stress at all corners
  i, k = np.unravel_index(np.argmax(np.abs(sigma)), sigma.shape) #identify index where max stress occurs, as well as which corner it occurs in
  return sigma[i,k],x[k],i #return max stress and its corresponding location along the wing and which corners


cornerNames = ["top-front", "top-back", "bottom-front", "bottom-back"] #provide names to aforementioned corners!

#each load case defined as function that takes an engine position le and returns ((shear, moment) in the lift direction, (shear, moment) in the drag/thrust direction)

def caseFlightPos25(le): #n = +2.5 
  liftDir  = shearBendingLift(x, 2.5, le)
  dragDir = shearBendingDrag(x, 2.5, le, maxEngineThrust)
  return liftDir, dragDir

def caseFlightPos1(le): #n = +1 (also covers engine out, working wing)
  liftDir = shearBendingLift(x, 1.0, le)
  dragDir = shearBendingDrag(x,  1.0, le, maxEngineThrust)
  return liftDir, dragDir

def caseFlightNeg1(le): # n = -1 
  liftDir = shearBendingLift(x, -1.0, le)
  dragDir = shearBendingDrag(x, -1.0, le, maxEngineThrust)
  return liftDir, dragDir

def caseDeadWing(le): #wing with the dead engine: drag but no thrust
  liftDir = shearBendingLift(x, 1.0, le)
  dragDir = shearBendingDrag(x, 1.0, le, 0.0)
  return liftDir, dragDir

def caseStatic(le): #on the ground: no lift, no drag, no thrust
  liftDir = staticShearBendingLift(x, le)
  noShear = np.zeros_like(x)
  noMoment = np.zeros_like(x)
  dragDir = (noShear, noMoment)
  return liftDir, dragDir

#dictionary linking name of each case (used for plot labels) to its function
loads = {}
loads["n = +2.5"] = caseFlightPos25
loads["n = +1"] = caseFlightPos1
loads["n = -1"] = caseFlightNeg1
loads["Engine out, dead wing"] = caseDeadWing
loads["Static"] = caseStatic

#empty result arrays: one array per load case, one slot per engine position
fs = {} #factor of safety vs le
critX = {} #where along the span the max stress occurs
corner = {} #which corner governs (0 top-front, 1 top-back, 2 bottom-front, 3 bottom-back)
sigSign = {} #sign of the max stress: -1 compression, +1 tension

for name in loads: #create blank arrays of quantities for eaching loading case, corresponding to number of tested engine positions
  fs[name] = np.zeros(len(leArray))
  critX[name] = np.zeros(len(leArray))
  corner[name] = np.zeros(len(leArray), dtype=int)
  sigSign[name] = np.zeros(len(leArray))
  

for j, le in enumerate(leArray):
  for name, loadCase in loads.items():
    (Vz, Mz), (Vy, My) = loadCase(le) #compute arrays of shear and moments along the wing for each loadcase, for a given engine positoin
    sigMax, xMax, c = maxStress(Mz, My, x) #compute max stress, max stress location, and return corner of wing it occurs at
    fs[name][j] = stressYield / np.abs(sigMax) #store factor of safety for each load case in position j (position j is position of engine location in engine array)
    critX[name][j] = xMax #see above, for critical positoin
    corner[name][j] = c #see above, for which corner
    sigSign[name][j] = np.sign(sigMax) #see above, storing whether max stress is in tension or compression

fsMin = np.min(np.array(list(fs.values())), axis=0) #create matrix of factor of safety values (each row is a loading case, each column represents an engine position), then take the minimum value in each column, and compare them all to determine the minimum factor of safety across all loading cases for a given engine position

validLe, yTip, yEng, yTipFlight = engineChecks(leArray) #returns engine positions that pass the all the engine checks
feasible = np.isin(leArray, validLe) & (fsMin >= 1.5) #return T/F array representing feasible engine positions that pass all checks and have a minimum facotr of safety greater than 1.5

if feasible.any():
  best = np.argmax(np.where(feasible, fsMin, -np.inf)) #replace all not feasible indices with negative infitnity so they can't win, then return location of maximum minimum factor of safety for all engine positions
  print(f"Best engine position: {leArray[best]:.2f} ft, min FS = {fsMin[best]:.3f}")
else:
  best = np.argmax(fsMin) #if no feasible engine position is found, simply return engine location of maximum minimum factor of safety
  print("No feasible engine position.")
  print(f"Highest min FS (ignoring other checks): {fsMin[best]:.3f} at le = {leArray[best]:.2f} ft")
leBest = leArray[best] #store best engine location

enginePlaceholder = 20*lWing/halfSpan #engine rib position assumed before the sweep
k = np.argmin(np.abs(ribLocations - enginePlaceholder)) #index of the placeholder rib
ribLocations[k] = leBest #move it to the actual engine location
ribLocations = np.sort(ribLocations) #put ribs in order from root to tip 
maxRibGap = np.max(np.diff(ribLocations)) #largest distance between two neighboring ribs

#max compressive stress at every point along the wing, assuming the engine at the best location
hTop, hBottom = h(x) #distances from centroid to top and bottom faces
zFront, zBack = ht(x) #distances from centroid to front and back faces
corners = [(hTop, zFront), (hTop, zBack), (hBottom, zFront), (hBottom, zBack)]

sigCompAlong = np.zeros_like(x) #largest compressive stress at each x, over all load cases and corners
for name in loads:
  (Vz, Mz), (Vy, My) = loads[name](leBest) # moments for this load case with the engine at leBest
  for yC, zC in corners:
    sig = -Mz*yC/I(x) - My*zC/It(x) #stress at this corner along the span (negative = compression)
    sigCompAlong = np.maximum(sigCompAlong, -sig) #keep the highest compressive stress value 

pAlong = sigCompAlong*strA(x)*np.ones_like(x) #compressive load in one stringer at each x (lbf)
kP = np.argmax(pAlong) #index of the largest stringer load
P = pAlong[kP] #largest stringer load anywhere on the wing (lbf)

cleverSol = np.array([[0],[0]]) #zero distances, so strI and strIt return only the stringers' own second moments of area!

if nStringers > 0:
  Pcr = min(np.pi**2*E*strI(lWing,cleverSol)/nStringers/maxRibGap**2,np.pi**2*E*strIt(lWing,cleverSol)/nStringers/maxRibGap**2) #compute critical load for Euler Buckling formula
  fsBuckling = Pcr/P #factor of safety with respect to buckling


#================= below graphs all quantities in a digestible report sheet!

#assign each loading case a color and style to be able to differentiate them (even if they overlap!)
lineColor = {}
lineStyle = {}
lineColor["n = +2.5"] = "blue"
lineStyle["n = +2.5"] = "-"
lineColor["n = +1"] = "orange"
lineStyle["n = +1"] = "--"
lineColor["n = -1"] = "green"
lineStyle["n = -1"] = "-."
lineColor["Engine out, dead wing"] = "goldenrod"
lineStyle["Engine out, dead wing"] = ":"
lineColor["Static"] = "pink"
lineStyle["Static"] = (0, (5, 1, 1, 1)) #additional pattern 

fig = plt.figure(figsize=(17,14)) #write one figure for the whole sheet
grid = fig.add_gridspec(3, 3, height_ratios=[1, 1, 0.75], hspace=0.38, wspace=0.25) #3x3 layout, bottom row is shorter since it will hold a table

axVz = fig.add_subplot(grid[0,0]) #shear in lift direction
axVy = fig.add_subplot(grid[0,1]) #shear in drag/thrust direction
axFS = fig.add_subplot(grid[0,2]) #factor of safety vs engine position
axMz = fig.add_subplot(grid[1,0]) #moment in lift direction
axMy = fig.add_subplot(grid[1,1]) #moment in drag/thrust direction
axDef = fig.add_subplot(grid[1,2]) #wing deflection
axTab = fig.add_subplot(grid[2,:]) #table takes up the whole bottom row

#shear and moment diagrams at the best engine position
for name in loads:
  (Vz, Mz), (Vy, My) = loads[name](leBest) #get shear and moment arrays for each loading case at best engine location
  axVz.plot(x, Vz/10**3, color=lineColor[name], linestyle=lineStyle[name], linewidth=2) #plot in thousands of lb
  axMz.plot(x, Mz/10**6, color=lineColor[name], linestyle=lineStyle[name], linewidth=2) #plot in millions of lb*ft
  if name != "Static": #no drag or thrust on the ground, so skipped
    axVy.plot(x, Vy/10**3, color=lineColor[name], linestyle=lineStyle[name], linewidth=2) #plot in kips
    axMy.plot(x, My/10**6, color=lineColor[name], linestyle=lineStyle[name], linewidth=2) #plot in millions of lb*ft

def formatDiagram(ax, title, ylabel): #same formatting for all four shear and moment plots
  ax.axhline(0, color="0.6", linewidth=0.8) #zero line
  ax.axvline(leBest, color="0.6", linewidth=0.8, linestyle=":") #mark the engine location
  ax.set_title(f"{title} (l_e = {leBest:.1f} ft)")
  ax.set_xlabel("Wing Position x (ft)")
  ax.set_ylabel(ylabel)
  ax.grid(True, alpha=0.3)

#axis titles
formatDiagram(axVz, "Shear, lift direction", "V ($10^3$ lb)")
formatDiagram(axMz, "Bending moment, lift direction", "M ($10^6$ lb$\\cdot$ft)")
formatDiagram(axVy, "Shear, drag/thrust direction", "V ($10^3$ lb)")
formatDiagram(axMy, "Bending moment, drag/thrust direction", "M ($10^6$ lb$\\cdot$ft)")

#deflection at the best engine position
vStatic, mStatic = staticShearBendingLift(x, leBest)
uStatic = deflectionCurve(mStatic) #deflection on the ground
vFlight, mFlight = shearBendingLift(x, 2.5, leBest)
uFlight = deflectionCurve(mFlight) #deflection at n = +2.5
uEngine = np.interp(leBest, x, uStatic) #deflection exactly at the engine on the ground

axDef.plot(x, uFlight, color=lineColor["n = +2.5"], linestyle=lineStyle["n = +2.5"], linewidth=2, label="n = +2.5")
axDef.plot(x, uStatic, color=lineColor["Static"], linestyle=lineStyle["Static"], linewidth=2, label="Static")
axDef.axhline(15, color="red", linestyle=":", linewidth=1.2, label="Flight tip limit") #draw helpful line to bound tip deflection during flight
axDef.axhline(-7, color="gray", linestyle=":", linewidth=1.2, label="Static tip limit") #draw helpful line to represent ground during taxiing
axDef.plot(leBest, -4, marker="v", color="gray", markersize=9, linestyle="none", label="Static engine limit") #insert marker at engine location to represent bound for engine deflection
axDef.plot(leBest, uEngine, marker="o", color="k", markersize=6, linestyle="none", label="Engine") #insert marker on engine to represent engine
axDef.axhline(0, color="0.6", linewidth=0.8) #zero line
axDef.set_title(f"Wing deflection (l_e = {leBest:.1f} ft)") 
axDef.set_xlabel("Wing Position x (ft)")
axDef.set_ylabel("u_y (ft)")
axDef.grid(True, alpha=0.3) #turn on gridlines
axDef.legend(fontsize=8, loc="best") #draws the legend 

#factor of safety vs engine position
maxYawDistance = maxRudderTorque/maxEngineThrust - fuselageWidth/2 #same yaw limit as in engineChecks
leMax = min(maxEngineDistance, maxYawDistance) #determine max engine distance from fusealge same as in engineChekcs

for name in loads:
  axFS.plot(leArray, fs[name], color=lineColor[name], linestyle=lineStyle[name], linewidth=2) 
axFS.plot(leArray, fsMin, color="k", linewidth=2.5, linestyle=":", label="Governing (min)") #plot doitted line to mark governing factor of safety
axFS.axvline(leMax, color="0.4", linestyle="-.", linewidth=1, label="Yaw limit") #show max engine position according to yawing concern
axFS.plot(leBest, fsMin[best], marker="o", color="k", markersize=7, linestyle="none") #mark the chosen engine position
axFS.set_title("Factor of safety vs. engine placement")
axFS.set_xlabel("Engine position l_e (ft)")
axFS.set_ylabel("FS = $\\sigma_Y / \\sigma_{max}$")
axFS.grid(True, alpha=0.3)
axFS.legend(fontsize=8, loc="best")

#table of key numbers
govName = "" #load case with the lowest FS at the best engine position
govFS = np.inf
for name in loads:
  if fs[name][best] < govFS: 
    govName = name
    govFS = fs[name][best]

if feasible.any():
  bestText = f"{leBest:.2f} ft"
else:
  bestText = f"{leBest:.2f} ft  (no feasible position)"

if sigSign[govName][best] < 0:
  stressType = "compression"
else:
  stressType = "tension"

critText = f"x = {critX[govName][best]:.1f} ft, {cornerNames[corner[govName][best]]} corner, {stressType}"

rows = []
rows.append(["Best engine position", bestText])
rows.append(["Governing load case", govName])
rows.append(["Minimum factor of safety", f"{fsMin[best]:.3f}"])
rows.append(["Critical location", critText])
rows.append(["Spar weight / cost per wing", f"{wSpar:,.0f} lb  /  ${cost:,.0f}"])
rows.append(["Static tip / engine deflection", f"{uStatic[-1]:.2f} ft  /  {uEngine:.2f} ft"])
rows.append(["Flight tip deflection (n = +2.5)", f"{uFlight[-1]:.2f} ft"])
if nStringers >0:
  bucklingText = f"{fsBuckling:.3g}  ({nStringers} stringers, {len(ribLocations)} ribs, largest rib gap {maxRibGap:.2f} ft)"
  rows.append(["Stringer buckling FS", bucklingText])



axTab.axis("off") #hide the axes, only show the table
table = axTab.table(cellText=rows, colLabels=["Quantity", "Value"], colWidths=[0.32, 0.68], cellLoc="left", loc="center")
table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1, 1.8) #make rows taller

cells = table.get_celld() #dictionary of (row, column) cell
for (row, col) in cells:
  cells[(row, col)].set_edgecolor("0.8")
  if row == 0: #header row
    cells[(row, col)].set_text_props(weight="bold")
    cells[(row, col)].set_facecolor("0.93")

#one shared legend at the top for all the load cases
handles = []
for name in loads:
  handles.append(plt.Line2D([], [], color=lineColor[name], linestyle=lineStyle[name], linewidth=2))
fig.legend(handles, list(loads), loc="upper center", ncol=len(loads), fontsize=11, frameon=False, bbox_to_anchor=(0.5, 0.965))

fig.suptitle("Design Report Sheet", fontsize=16, y=0.985)
fig.subplots_adjust(top=0.90)
plt.savefig(outputFile, dpi=150, bbox_inches="tight")
plt.show()
