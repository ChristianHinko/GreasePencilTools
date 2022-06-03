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
            print("Must be used with exactly 4 points")
            return {'CANCELLED'}
        
        # The points of this plane
        PointA: mathutils.Vector = SelectedPoints[0]
        PointB: mathutils.Vector = SelectedPoints[1]
        PointC: mathutils.Vector = SelectedPoints[2]
        PointD: mathutils.Vector = SelectedPoints[3]
        
        # Ensure points are coplanar
        if (PointsAreCoplanar([PointA.co, PointB.co, PointC.co, PointD.co]) == False):
            print("The 4 points are not aligned on the same global normal")
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
 # Given four points, do they exist on the same plane?
 ##
def PointsAreCoplanar(InPoints: list[mathutils.Vector], InErrorTolerance: float = 0.0001) -> bool:
    if (len(InPoints) <= 3):
        # Three points are always coplanar
        return True;
    
    PlaneNormal: mathutils.Vector = (InPoints[2] - InPoints[0]).cross(InPoints[1] - InPoints[0]).normalized();
    
    for i in range(3, len(InPoints)): # skip the first three points
        DirectionToPoint: mathutils.Vector = (InPoints[i] - InPoints[0]).normalized();
        
        bPerpendicular: bool = IsNearlyEqual(PlaneNormal.dot(DirectionToPoint), 0, InErrorTolerance);
        if (bPerpendicular == False):
            # Not coplanar
            return False
    
    # All points lie on the same plane
    return True;

###
 # Are two values nearly equal within a given tolerance
 ##
def IsNearlyEqual(InA: float, InB: float, InErrorTolerance: float = 0.0001) -> bool:
    Difference: float = InB - InA
    return (abs(Difference) <= InErrorTolerance)
