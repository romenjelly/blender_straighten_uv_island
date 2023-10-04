bl_info = {
    "name": "Straighten UV Island",
    "description": "Straightens a UV island based on a selected edge",
    "author": "romenjelly",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "category": "UV"
}

import bpy
import bmesh
import math

class StraightenUvIsland(bpy.types.Operator):
    bl_idname = "uv.straigthen_island"
    bl_label = "Straigten Island"
    bl_description = "Straighten a UV island based on two selected vertices"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bm = bmesh.from_edit_mesh(context.active_object.data)
        uv_layer = bm.loops.layers.uv.verify()
        selected_uvs = {(loop[uv_layer].uv.x, loop[uv_layer].uv.y) for face in bm.faces for loop in face.loops if loop[uv_layer].select}

        selected_count = len(selected_uvs)
        if selected_count != 2:
            self.report({'ERROR'}, "Exactly two vertices need to be selected to straighten an island, " + str(selected_count) + " found")
            return {'CANCELLED'}

        (x1, y1), (x2, y2) = selected_uvs
        angle_rad = math.atan2(y2 - y1, x2 - x1)
        angle_deg = math.degrees(angle_rad)
        angle_deg_rounded = round(angle_deg / 90) * 90
        angle_deg_delta = angle_deg_rounded - angle_deg
        angle_rad_delta = math.radians(angle_deg_delta)

        bpy.ops.uv.select_linked()

        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        # Code copied from https://github.com/SavMartin/TexTools-Blender/blob/master/utilities_uv.py
        # See LICENSE and LICENSE_TexTools
        selected_faces = {face for face in bm.faces if all([loop[uv_layer].select for loop in face.loops])}
        for face in selected_faces:
            for loop in face.loops:
                x, y = loop[uv_layer].uv
                xt = x - center_x
                yt = y - center_y
                xr = (xt * math.cos(angle_rad_delta)) - (yt * math.sin(angle_rad_delta))
                yr = (xt * math.sin(angle_rad_delta)) + (yt * math.cos(angle_rad_delta))

                loop[uv_layer].uv.x = xr + center_x
                loop[uv_layer].uv.y = yr + center_y

        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(StraightenUvIsland.bl_idname, text="Straighten Island")

def register():
    bpy.utils.register_class(StraightenUvIsland)
    bpy.types.IMAGE_MT_uvs_context_menu.append(menu_func)

def unregister():
    bpy.utils.unregister_class(StraightenUvIsland)
    bpy.types.IMAGE_MT_uvs_context_menu.remove(menu_func)

if __name__ == "__main__":
    register()
