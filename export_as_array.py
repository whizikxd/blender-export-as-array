# Copyright (C) 2025  Timotej Milcak
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


bl_info = {
    "name": "Export as array",
    "description": "Exports selected object as an array",
    "author": "Timotej Milcak",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "Object > Export as array",
    "warning": "WIP",
    "wiki_url": "",
    "tracker_url": "",
    "support": "COMMUNITY",
    "category": "Export"
}

import bpy
import bmesh
from bpy.props import *

def get_array_string_for(mesh):
    vert_suffix = bpy.context.scene.option_vert_suffix
    index_suffix = bpy.context.scene.option_index_suffix
    array_begin = bpy.context.scene.option_array_begin
    array_delim = bpy.context.scene.option_array_delim
    array_end = bpy.context.scene.option_array_end
    object_begin = bpy.context.scene.option_object_begin
    object_delim = bpy.context.scene.option_object_delim
    object_end = bpy.context.scene.option_object_end
    include_faces = bpy.context.scene.option_include_faces

    result = "verts = "
    result += array_begin
    result += "\n"

    bm = bmesh.new()
    bm.from_mesh(mesh)
    for v in bm.verts:
        result += "\t"
        result += object_begin
        result += " "
        result += str(v.co.x)
        result += vert_suffix
        result += object_delim
        result += " "

        result += str(v.co.y)
        result += vert_suffix
        result += object_delim
        result += " "

        result += str(v.co.z)
        result += vert_suffix
        result += " "

        result += object_end
        result += array_delim
        result += "\n"

    result += array_end

    if include_faces:
        result += "\n\n"
        result += "faces = "
        result += array_begin
        result += "\n"
        for f in bm.faces:
            result += "\t"
            result += object_begin
            for v in f.verts:
                result += " "
                result += str(v.index)
                result += index_suffix
                result += object_delim
                result += " "

            result += object_end
            result += array_delim
            result += "\n"

        result += array_end

    bm.free()
    return result

class OBJECT_OT_export_as_array_disk(bpy.types.Operator):
    bl_label = "Export to disk"
    bl_idname = "object.export_as_array_disk"

    filepath: StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"};

    def execute(self, context):
        self.report({'ERROR'}, "UNIMPLEMENTED!")
        return {"FINISHED"}

class OBJECT_OT_export_as_array_clipboard(bpy.types.Operator):
    bl_label = "Copy to clipboard"
    bl_idname = "object.export_as_array_clipboard"

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        selected_objects_count = len(selected_objects)
        if selected_objects_count == 1:
            active_object = selected_objects[0]
            if active_object is not None and active_object.type == "MESH":
                string = get_array_string_for(active_object.to_mesh())
                context.window_manager.clipboard = string
            else:
                self.report({'ERROR'}, "Invalid object selected!")
        else:
            self.report({'ERROR'}, "Select precisely one object!")
        return {"FINISHED"}

class OBJECT_OT_export_as_array(bpy.types.Operator):
    bl_label = "Export as array"
    bl_idname = "object.export_as_array"

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=250)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Export settings")
        layout.separator(type="LINE")

        split = layout.split(factor=0.5)
        left_col = split.column()
        right_col = split.column()

        left_col.label(text="Vertex suffix")
        right_col.prop(bpy.context.scene, "option_vert_suffix", text="")

        left_col.label(text="Index suffix")
        right_col.prop(bpy.context.scene, "option_index_suffix", text="")

        left_col.label(text="Array begin")
        right_col.prop(bpy.context.scene, "option_array_begin", text="")

        left_col.label(text="Array delimiter")
        right_col.prop(bpy.context.scene, "option_array_delim", text="")

        left_col.label(text="Array end")
        right_col.prop(bpy.context.scene, "option_array_end", text="")

        left_col.label(text="Object begin")
        right_col.prop(bpy.context.scene, "option_object_begin", text="")

        left_col.label(text="Object delimiter")
        right_col.prop(bpy.context.scene, "option_object_delim", text="")

        left_col.label(text="Object end")
        right_col.prop(bpy.context.scene, "option_object_end", text="")

        left_col.label(text="Include faces")
        right_col.prop(bpy.context.scene, "option_include_faces", text="")

        layout.operator(OBJECT_OT_export_as_array_clipboard.bl_idname)
        layout.operator(OBJECT_OT_export_as_array_disk.bl_idname)

    def execute(self, context):
        return {"FINISHED"}

def menu_func(self, context):
    layout = self.layout
    layout.separator(type="LINE")
    layout.operator(OBJECT_OT_export_as_array.bl_idname)

def register():
    bpy.types.Scene.option_vert_suffix = StringProperty(default="f")
    bpy.types.Scene.option_index_suffix = StringProperty(default="")

    bpy.types.Scene.option_array_begin = StringProperty(default="{")
    bpy.types.Scene.option_array_delim = StringProperty(default=",")
    bpy.types.Scene.option_array_end = StringProperty(default="};")

    bpy.types.Scene.option_object_begin = StringProperty(default="{")
    bpy.types.Scene.option_object_delim = StringProperty(default=",")
    bpy.types.Scene.option_object_end = StringProperty(default="}")

    bpy.types.Scene.option_include_faces = BoolProperty(default=True)

    bpy.utils.register_class(OBJECT_OT_export_as_array)
    bpy.utils.register_class(OBJECT_OT_export_as_array_clipboard)
    bpy.utils.register_class(OBJECT_OT_export_as_array_disk)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    del bpy.types.Scene.option_vert_suffix
    del bpy.types.Scene.option_index_suffix
    del bpy.types.Scene.option_array_begin
    del bpy.types.Scene.option_array_delim
    del bpy.types.Scene.option_array_end
    del bpy.types.Scene.option_object_begin
    del bpy.types.Scene.option_object_delim
    del bpy.types.Scene.option_object_end
    del bpy.types.Scene.option_include_faces

    bpy.utils.unregister_class(OBJECT_OT_export_as_array)
    bpy.utils.unregister_class(OBJECT_OT_export_as_array_clipboard)
    bpy.utils.unregister_class(OBJECT_OT_export_as_array_disk)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
    register()
