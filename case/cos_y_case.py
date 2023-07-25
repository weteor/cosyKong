import cadquery as cq
import cadquery.selectors as cqs
from cadquery import NearestToPointSelector, exporters as exp

# CONFIGURATION OPTIONS
useAngle = True     # if True, thifts highst col to ringfinger
showKeys = False    # if True, adds keycap models (takes longer)
showPcb = False    # if True, adds keycap models (takes longer)

# CONSTANTS
spacing = 19.05     # MX-Spacing
holeSize = 14       # Platehole size
pcbThickness = 1.6  # PCB Thickness
hsThickness = 2.8   # HS Socket Thickness below PCB
hsSafety = 0.5      # extra space to hide HS Sockets

# CASE PARAMETERS
keySafety = 0.5      # extra space between keycap and case
spaceAbovePCB = 0.25 # space between PCB and Plate.
plateHeight = 5 - spaceAbovePCB # heigth of plate
colStagger = 0.25 * spacing # stagger between cols


heightAbovePlate = 8.5 # height of case rim measured from plate
heightBelowPlate = pcbThickness+hsThickness+hsSafety # height of rim hiding pcb and Sockets

overallHeight = heightAbovePlate+heightBelowPlate+plateHeight

outerRad = 3        # radius of outer edge fillets
outerRadSmall = 1   # radius of other outline fillets

wallWidth  = 7.5    # Wall Width (in effect only left and right)
lWallWidth = 2.5    # min Wallthickness for keys outside of case body

rectOffset = 0.125*19.05-colStagger/2 # rectangular case body y offset
rectHeight = 3*spacing+2*lWallWidth+colStagger # rectangular case y height


caseWidth  = 10 *spacing + 2*wallWidth  # absolute case width
caseHeight =  3*spacing + 2*wallWidth + 3*colStagger # absolute case height


def getRowPos(rowOffset=0):
    """ returns x y coordinate tuple for each right hand switch of the selected row

    :param rowOffset: row number counted from the top
    :return list of coordinate tuples
    """

    topSwitchY = caseHeight/2-wallWidth-spacing/2-rowOffset*spacing

    if useAngle:
        colStaggerOffset = 1;
    else:
        colStaggerOffset = 0;

    points =  [ 
         ( 0.5 * spacing, topSwitchY - (2+colStaggerOffset) * colStagger ),
         ( 1.5 * spacing, topSwitchY - (1+colStaggerOffset) * colStagger ),
         ( 2.5 * spacing, topSwitchY - (0+colStaggerOffset) * colStagger ),
         ( 3.5 * spacing, topSwitchY - (1-colStaggerOffset) * colStagger ),
         ( 4.5 * spacing, topSwitchY - (2-colStaggerOffset) * colStagger ) 
    ]

    return points

def getSwitchPositions():
    """ collects all positions for the first three rows
    """
    return getRowPos(0) + getRowPos(1) + getRowPos(2)

## ------------------------------------------------------------------------------

insetTop = 1
insetTopOffset = -0.5
insetBottom = 0
insetBottomOffset = 1

# SKETCH FOR OUTLINE WITHOUT FILLETS
so = (
    cq.Sketch()
    .push(getSwitchPositions())
    .rect(spacing+2*lWallWidth, spacing+2*lWallWidth)
    .reset()
    .push([(-spacing/2,0)])
    .rect(spacing, caseHeight, mode='s')
    .reset()
    .push([(caseWidth/4,rectOffset/2)])
    .rect(caseWidth/2,rectHeight)
    .reset()
    .polygon([
        (0                                             ,caseHeight/2), 
        (0                                             ,caseHeight/2-(2+insetTop)*colStagger),
        (spacing-colStagger+insetTopOffset             ,caseHeight/2-(2+insetTop)*colStagger),
        (spacing-colStagger*(1-insetTop)+insetTopOffset,caseHeight/2-2*colStagger)], mode='s')
    .reset()
    .polygon([
        (0          ,-caseHeight/2+colStagger+2*lWallWidth), 
        (spacing*1.5,-caseHeight/2+colStagger+2*lWallWidth),
        (spacing*1.5,-caseHeight/2),
        (0          ,-caseHeight/2)], mode='s')
    .reset()
    .polygon([
        (0                                                    ,-caseHeight/2+colStagger+2*lWallWidth), 
        (spacing+(1+insetBottom)*colStagger+insetBottomOffset ,-caseHeight/2+colStagger+2*lWallWidth), 
        (spacing+insetBottomOffset      ,-caseHeight/2+colStagger+  lWallWidth-insetBottom*colStagger-lWallWidth), 
        (0                                                    ,-caseHeight/2+colStagger+  lWallWidth-insetBottom*colStagger-lWallWidth)])
    .clean()
)


# SKETCH FOR SWITCH CUTOUTS
si = (
    cq.Sketch()
    .push(getSwitchPositions())
    .rect(spacing+keySafety, spacing+keySafety)
    .clean()
    .reset()
    .vertices(cqs.BoxSelector( (2, caseHeight/2, 10), (caseWidth/2+2, -caseHeight/2, -10) ))
    .fillet(1)
)

# SKETCH FOR USB Cutout
su = (cq.Sketch()
    .rect(10,5)
    .reset()
    .vertices()
    .fillet(1.5)
)
# SKETCH FOR USB Cutout
suo = (cq.Sketch()
    .rect(13,7)
    .reset()
    .vertices()
    .fillet(2.5)
)

#  BOTTOM RIM
bottom = (
    cq.Workplane("XY")
    .placeSketch(so)
    .extrude(heightBelowPlate)
    .faces("<Z or > Z or <X")
    .shell(-lWallWidth,'intersection')
    .edges("|Z")
    .edges(cqs.BoxSelector( (2, caseHeight/2, 10), (2*spacing, -caseHeight/2, -10) ))
    .fillet(outerRad)
    .edges("|Z")
    .edges(cqs.BoxSelector( (2*spacing, caseHeight/2, 10), (caseWidth/2-wallWidth+2, -caseHeight/2, -10) ))
    .fillet(outerRadSmall)
    .edges(">X and |Z")
    .fillet(outerRad)
)

# PLATE 
plate = (
    cq.Workplane("XY", origin=(0,0,heightBelowPlate))
    .placeSketch(so)
    .extrude(plateHeight)
    .edges("|Z")
    .edges(cqs.BoxSelector( (2, caseHeight/2, heightBelowPlate), (2*spacing, -caseHeight/2, overallHeight) ))
    .fillet(outerRad)
    .edges("|Z")
    .edges(cqs.BoxSelector( (2, caseHeight/2, heightBelowPlate), (caseWidth/2-wallWidth+2, -caseHeight/2, overallHeight) ))
    .fillet(outerRadSmall)
    .edges(">X and |Z")
    .fillet(outerRad)
    .faces(">Z").workplane()
    .pushPoints(getSwitchPositions())
    .rect(holeSize,holeSize)
    .cutBlind(-plateHeight)
    .faces(">Z").workplane(offset=-1.5)
    .pushPoints(getSwitchPositions())
    .rect(5,16)
    .cutBlind(-plateHeight)
)

# TOP
top = (
    cq.Workplane("XY", origin=(0,0,heightBelowPlate+plateHeight))
    .placeSketch(so)
    .extrude(heightAbovePlate)
    .edges("|Z")
    .edges(cqs.BoxSelector( (2, caseHeight/2, heightBelowPlate+plateHeight), (2*spacing, -caseHeight/2, overallHeight) ))
    .fillet(outerRad)
    .edges("|Z")
    .edges(cqs.BoxSelector( (2, caseHeight/2, heightBelowPlate+plateHeight), (caseWidth/2-wallWidth+2, -caseHeight/2, overallHeight) ))
    .fillet(outerRadSmall)
    .edges(">X and |Z")
    .fillet(outerRad)
    .faces(">Z").workplane()
    .placeSketch(si)
    .cutBlind(-heightAbovePlate)
)


# COMBINE
half = (
    bottom.union(plate.union(top))
# USB
    .faces(cqs.NearestToPointSelector((0,caseHeight/2-3*colStagger, heightBelowPlate+plateHeight/2)))
    .workplane().tag("usbPlane")
    .move(0, 6.5)
    .placeSketch(su)
    .cutBlind(-5)
    .workplaneFromTagged("usbPlane")
    .move(0, 6.5)
    .placeSketch(suo)
    .cutBlind(-1)
)

full = (
    half.mirror(half.faces("<X"),union=True)
    .faces(">Z")
    .wires(cqs.NearestToPointSelector((0,1.5*spacing,overallHeight)))
    .chamfer(0.5)
    .faces(">Z")
    .wires(cqs.NearestToPointSelector((0,-caseHeight/2,overallHeight)))
    .chamfer(0.99)
    .faces(cqs.NearestToPointSelector((0,caseHeight/2-3*colStagger, heightBelowPlate+plateHeight/2)))
    .wires().item(1)
    .chamfer(0.5)
    .faces(cqs.NearestToPointSelector((0,caseHeight/2-3*colStagger, overallHeight/2)))
    .wires().item(1)
    .chamfer(0.75)
)

# exp.export(plate.mirror(plate.faces("<X"), union=True).faces("<Z"), "/home/matthias/Data/Keyboards/CoSiNe/case/plate.dxf", exp.ExportTypes.DXF)
# exp.export(bottom.mirror(bottom.faces("<X"), union=True).faces("<Z"), "/home/matthias/Data/Keyboards/CoSiNe/case/bottom.dxf", exp.ExportTypes.DXF)

# kb = cq.Assembly()
# kb = kb.add(full, name="kb", color=cq.Color(60/255,120/255,180/255,0.5))
# kb = kb.constrain("kb", "FixedRotation", (0, 0, 0))

if showPcb:
    pcb = cq.importers.importStep("../pcb/cos_y_kong/cos_y_kong.step")
    kb = kb.add(pcb, loc=cq.Location((0,0,heightBelowPlate-pcbThickness)), name="pcb")

# KEYCAPS
if showKeys:
    dsa = cq.importers.importStep("./parts/dsa.step")

    point = getSwitchPositions();

    for i,point in enumerate(getSwitchPositions()):
        nr = "kr"+str(i)
        nl = "kl"+str(i)
        kb = kb.add(dsa, name=nr)
        kb = kb.constrain(nr, "FixedPoint", (point[0], point[1], overallHeight+2))
        kb = kb.constrain(nr, "FixedRotation", (90, 0, 0))
        kb = kb.add(dsa, name=nl)
        kb = kb.constrain(nl, "FixedPoint", (-point[0], point[1], overallHeight+2))
        kb = kb.constrain(nl, "FixedRotation", (90, 0, 0))
    kb = kb.solve()
    # show_object(body, options=({"color": (60,120,180)}))

# show_object(kb, name="Keyboard")

