import bpy
import mathutils



###
 # Operator that calculates the normal of a perspective plane
 ##
class CalculateNormalOfPerspectivePlane(bpy.types.Operator):
    bl_idname = "wm.calculate_normal_of_perspective_plane"
    bl_label = "Minimal Operator"
    
    def execute(self, context):
        # Get the selected points
        SelectedPoints: list[bpy.types.GPencilStrokePoint] = GetGreasePencilStrokePoints()
        
        # Ensure we are working with 4 vertices
        if (len(SelectedPoints) != 4):
            print("Must be used with exactly 4 points!")
            return {'CANCELLED'}
        
        # The points of this plane
        PointA: mathutils.Vector = SelectedPoints[0]
        PointB: mathutils.Vector = SelectedPoints[1]
        PointC: mathutils.Vector = SelectedPoints[2]
        PointD: mathutils.Vector = SelectedPoints[3]
        
        # Ensure points are coplanar
        if (PointsAreCoplanar([PointA.co, PointB.co, PointC.co, PointD.co]) == False):
            print("The 4 points are not aligned on the same global plane!")
            return {'CANCELLED'}
        
        # Ensure quad is convex
        if (PointLiesOnTriangle(PointA.co, PointB.co, PointC.co, PointD.co)):
            print("The 4 points are not convex!")
            return {'CANCELLED'}
        
        # The vectors between the different points
        AToB: mathutils.Vector = (PointB.co - PointA.co)
        BToC: mathutils.Vector = (PointC.co - PointB.co)
        CToD: mathutils.Vector = (PointD.co - PointC.co)
        DToA: mathutils.Vector = (PointA.co - PointD.co)
        
        # The normal of this plane in global space
        GlobalNormal: mathutils.Vector = AToB.normalized().cross(BToC.normalized())
        
        return {'FINISHED'}
    

# Add it to a menu
def menu_func(self, context):
    self.layout.operator(CalculateNormalOfPerspectivePlane.bl_idname, text="CalculateNormalOfPerspectivePlane")

# Update the register function to show up in a menu
bpy.utils.register_class(CalculateNormalOfPerspectivePlane)
bpy.types.VIEW3D_MT_view.append(menu_func)


###
 # Gets the currently selected grease pencil stroke points - if any
 ##
def GetGreasePencilStrokePoints() -> list[bpy.types.GPencilStrokePoint]:
    # Get active object
    ActiveObject: bpy.types.Object = bpy.context.active_object.data
    
    # Get active layer
    ActiveLayer: bpy.types.GPencilLayer = ActiveObject.layers.active
    
    # Get active frame
    ActiveFrame: bpy.types.GPencilFrame = ActiveLayer.active_frame
    
    # Get selected strokes
    SelectedStrokes: list[bpy.types.GPencilStroke] = [ ]
    for Stroke in ActiveFrame.strokes:
        if (Stroke.select):
            SelectedStrokes.append(Stroke)
        
    
    # Get selected points
    SelectedPoints: list[bpy.types.GPencilStrokePoint] = [ ]
    for Stroke in SelectedStrokes:
        for Point in Stroke.points:
            if (Point.select):
                SelectedPoints.append(Point)
            
        
    # Return out gathered points
    return SelectedPoints

###
 # Given two bounding directions A and B and a test direction, does the direction lie between them?
 # Only can return true if the three directions are coplanar.
 ##
def DirectionIsBetween(InA: mathutils.Vector, InB: mathutils.Vector, bInInclusive: bool, InDirection: mathutils.Vector, InErrorTolerance: float = 1e-4) -> bool:
    # Get the normals
    # 
    # InA ^
    #     |        InDirection
    #     |          ^
    #     | NormalA /
    #     |        /
    #     |       /
    #     |      /
    #     |     /
    #     |    /
    #     |   /  NormalB
    #     |  /
    #     | /
    #     |/_____________>
    #                    InB
    # 
    NormalA: mathutils.Vector = InA.cross(InDirection).normalized()
    NormalB: mathutils.Vector = InDirection.cross(InB).normalized()
    
    # If we are inclusive, check if the direction is on one of the bounding directions
    if (bInInclusive):
        # Cross product of zero means that the direction is on the bound
        if (IsNearlyEqualVector(NormalA, mathutils.Vector((0, 0, 0)), InErrorTolerance)
            or IsNearlyEqualVector(NormalB, mathutils.Vector((0, 0, 0)), InErrorTolerance)):
            return true;
    
    # If the two normals are not opposites, then we are within the bounding directions
    bSameNormals: bool = IsNearlyEqualFloat(NormalA.dot(NormalB), 1, InErrorTolerance)
    return bSameNormals;

###
 # Given a triangle and a point, does that point lie on the triangle?
 ##
def PointLiesOnTriangle(InA: mathutils.Vector, InB: mathutils.Vector, InC: mathutils.Vector, InPoint: mathutils.Vector, InErrorTolerance: float = 1e-4) -> bool:
    # Whether the point is within A's angle
    AToPoint: mathutils.Vector = (InPoint - InA)
    AToB: mathutils.Vector = (InB - InA)
    AToC: mathutils.Vector = (InC - InA)
    bPointIsBetweenBAndC: bool = DirectionIsBetween(AToB, AToC, True, AToPoint, InErrorTolerance)
    
    # Whether the point is within B's angle
    BToPoint: mathutils.Vector = (InPoint - InB)
    BToA: mathutils.Vector = (InA - InB)
    BToC: mathutils.Vector = (InC - InB)
    bPointIsBetweenAAndC: bool = DirectionIsBetween(BToA, BToC, True, BToPoint, InErrorTolerance)
    
    if (bPointIsBetweenBAndC and bPointIsBetweenAAndC):
        # Point is on the triangle
        # 
        #          C
        #         / \
        #        /   \
        #       / o   \
        #      /       \
        #     /         \
        #    A _________ B
        # 
        return True
    
    # Point is not on the triangle
    # 
    #          C
    #         / \
    #      o /   \
    #       /     \
    #      /       \
    #     /         \
    #    A _________ B
    # 
    return False;

###
 # Given four points, do they exist on the same plane?
 ##
def PointsAreCoplanar(InPoints: list[mathutils.Vector], InErrorTolerance: float = 1e-4) -> bool:
    if (len(InPoints) <= 3):
        # Three points are always coplanar
        return True
    
    PlaneNormal: mathutils.Vector = (InPoints[2] - InPoints[0]).cross(InPoints[1] - InPoints[0]).normalized()
    
    for i in range(3, len(InPoints)): # skip the first three points
        DirectionToPoint: mathutils.Vector = (InPoints[i] - InPoints[0]).normalized()
        
        bPerpendicular: bool = IsNearlyEqualFloat(PlaneNormal.dot(DirectionToPoint), 0, InErrorTolerance)
        if (bPerpendicular == False):
            # Not coplanar
            return False
    
    # All points lie on the same plane
    return True

###
 # Are two values nearly equal within a given tolerance
 ##
def IsNearlyEqualFloat(InA: float, InB: float, InErrorTolerance: float = 1e-4) -> bool:
    Difference: float = InB - InA
    return (abs(Difference) <= InErrorTolerance)

###
 # Are two values nearly equal within a given tolerance
 ##
def IsNearlyEqualVector(InA: mathutils.Vector, InB: mathutils.Vector, InErrorTolerance: float = 1e-4) -> bool:
    return (IsNearlyEqualFloat(InA.x, InB.x, InErrorTolerance)
        and IsNearlyEqualFloat(InA.y, InB.y, InErrorTolerance)
        and IsNearlyEqualFloat(InA.z, InB.z, InErrorTolerance))
