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

class Profile():
    def __init__(self,
                 name,
                 vert_suffix, index_suffix,
                 array_begin, array_delim, array_end,
                 object_begin, object_delim, object_end):
        self.name = name
        self.vert_suffix = vert_suffix
        self.index_suffix = index_suffix
        self.array_begin = array_begin
        self.array_delim = array_delim
        self.array_end = array_end
        self.object_begin = object_begin
        self.object_delim = object_delim
        self.object_end = object_end

profiles = {
    "profile_empty":Profile("Empty", "", "", "", "", "", "", "", ""),
    "profile_c": Profile("C", "f", "", "{", ",", "};", "{", ",", "}"),
    "profile_py": Profile("Python", "", "", "[", ",", "]", "[", ",", "]")
}

def generate_profile_items(self, context):
    result = []
    for key, value in profiles.items():
        result.append((key, value.name, ""))
    return result

def change_profile(self, context):
    changed_to = self.profiles_enum
    storage = bpy.context.scene.export_as_array_properties

    storage.vert_suffix = profiles[changed_to].vert_suffix
    storage.index_suffix = profiles[changed_to].index_suffix
    storage.array_begin = profiles[changed_to].array_begin
    storage.array_delim = profiles[changed_to].array_delim
    storage.array_end = profiles[changed_to].array_end
    storage.object_begin = profiles[changed_to].object_begin
    storage.object_delim = profiles[changed_to].object_delim
    storage.object_end = profiles[changed_to].object_end

class ExportAsArrayProperties(bpy.types.PropertyGroup):
    vert_suffix: StringProperty()
    index_suffix: StringProperty()
    array_begin: StringProperty()
    array_delim: StringProperty()
    array_end: StringProperty()
    object_begin: StringProperty()
    object_delim: StringProperty()
    object_end: StringProperty()
    include_faces: BoolProperty(default=True)

def get_array_string_for(mesh):
    storage = bpy.context.scene.export_as_array_properties

    vert_suffix = storage.vert_suffix
    index_suffix = storage.index_suffix
    array_begin = storage.array_begin
    array_delim = storage.array_delim
    array_end = storage.array_end
    object_begin = storage.object_begin
    object_delim = storage.object_delim
    object_end = storage.object_end
    include_faces = storage.include_faces

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

            v_last = len(f.verts) - 1
            for i, v in enumerate(f.verts):
                result += " "
                result += str(v.index)
                result += index_suffix

                if i != v_last:
                    result += object_delim
                else:
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
        self.report({"ERROR"}, "UNIMPLEMENTED!")
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
                self.report({"INFO"}, "Successfuly copied")
            else:
                self.report({"ERROR"}, "Invalid object selected!")
        else:
            self.report({"ERROR"}, "Select precisely one object!")
        return {"FINISHED"}

class OBJECT_OT_export_as_array(bpy.types.Operator):
    bl_label = "Export as array"
    bl_idname = "object.export_as_array"

    profiles_enum: EnumProperty(
        name="Profile",
        update=change_profile,
        items=generate_profile_items,
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=250)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Export settings")
        row.prop(self, "profiles_enum")
        layout.separator(type="LINE")

        split = layout.split(factor=0.5)
        left_col = split.column()
        right_col = split.column()

        storage = bpy.context.scene.export_as_array_properties

        left_col.label(text="Vertex suffix")
        right_col.prop(storage, "vert_suffix", text="")

        left_col.label(text="Index suffix")
        right_col.prop(storage, "index_suffix", text="")

        left_col.label(text="Array begin")
        right_col.prop(storage, "array_begin", text="")

        left_col.label(text="Array delimiter")
        right_col.prop(storage, "array_delim", text="")

        left_col.label(text="Array end")
        right_col.prop(storage, "array_end", text="")

        left_col.label(text="Object begin")
        right_col.prop(storage, "object_begin", text="")

        left_col.label(text="Object delimiter")
        right_col.prop(storage, "object_delim", text="")

        left_col.label(text="Object end")
        right_col.prop(storage, "object_end", text="")

        left_col.label(text="Include faces")
        right_col.prop(storage, "include_faces", text="")

        layout.operator(OBJECT_OT_export_as_array_clipboard.bl_idname)
        layout.operator(OBJECT_OT_export_as_array_disk.bl_idname)

    def execute(self, context):
        return {"FINISHED"}

def menu_func(self, context):
    layout = self.layout
    layout.separator(type="LINE")
    layout.operator(OBJECT_OT_export_as_array.bl_idname)

def register():
    bpy.utils.register_class(ExportAsArrayProperties)
    bpy.types.Scene.export_as_array_properties = PointerProperty(type=ExportAsArrayProperties)
    bpy.utils.register_class(OBJECT_OT_export_as_array)
    bpy.utils.register_class(OBJECT_OT_export_as_array_clipboard)
    bpy.utils.register_class(OBJECT_OT_export_as_array_disk)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    del bpy.types.Scene.export_as_array_properties
    bpy.utils.unregister_class(ExportAsArrayProperties)
    bpy.utils.unregister_class(OBJECT_OT_export_as_array)
    bpy.utils.unregister_class(OBJECT_OT_export_as_array_clipboard)
    bpy.utils.unregister_class(OBJECT_OT_export_as_array_disk)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
    register()
