import bpy



# Operator that calculates the normal of a perspective plane
class CalculateNormalOfPerspectivePlane(bpy.types.Operator):
    bl_idname = "wm.calculate_normal_of_perspective_plane"
    bl_label = "Minimal Operator"
    
    def execute(self, context):
        # Get the selected points
        SelectedPoints = GetGreasePencilStrokePoints()
        
        # Ensure we are working with 4 vertices
        if len(SelectedPoints) != 4:
            print("Must be used with exactly 4 points")
            return {'CANCELLED'}
        
        # The points of this plane
        PointA = SelectedPoints[0]
        PointB = SelectedPoints[1]
        PointC = SelectedPoints[2]
        PointD = SelectedPoints[3]
        
        # The vectors between the different points
        AToB = PointB.co - PointA.co
        BToC = PointC.co - PointB.co
        CToD = PointD.co - PointC.co
        DToA = PointA.co - PointD.co
        
        # The normal of this plane in global space
        GlobalNormal = AToB.normalized().cross(BToC.normalized())
        
        return {'FINISHED'}
    

# Add it to a menu
def menu_func(self, context):
    self.layout.operator(CalculateNormalOfPerspectivePlane.bl_idname, text="CalculateNormalOfPerspectivePlane")

# Update the register function to show up in a menu
bpy.utils.register_class(CalculateNormalOfPerspectivePlane)
bpy.types.VIEW3D_MT_view.append(menu_func)


# Gets the currently selected grease pencil stroke points if any
def GetGreasePencilStrokePoints():
    # Get active object
    ActiveObject =  bpy.context.active_object.data
    
    # Get active layer
    ActiveLayer = ActiveObject.layers.active
    
    # Get active frame
    ActiveFrame = ActiveLayer.active_frame
    
    # Get selected strokes
    SelectedStrokes = [ ]
    for Stroke in ActiveFrame.strokes:
        if Stroke.select:
            SelectedStrokes.append(Stroke)
        
    
    # Get selected points
    SelectedPoints = [ ]
    for Stroke in SelectedStrokes:
        for Point in Stroke.points:
            if Point.select:
                SelectedPoints.append(Point)
            
        
    
    return SelectedPoints
