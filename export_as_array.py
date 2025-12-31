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
    "profile_empty": Profile("Empty", "", "", "", "", "", "", "", ""),
    "profile_c": Profile("C", "f", "", "{", ",", "};", "{", ",", "}"),
    "profile_py": Profile("Python", "", "", "[", ",", "]", "[", ",", "]")
}

def generate_profile_items(self, context):
    result = []
    for key, value in profiles.items():
        result.append((key, value.name, ""))
    return result

def get_selected_mesh(self, context):
    selected_objects = bpy.context.selected_objects
    selected_objects_count = len(selected_objects)
    if selected_objects_count == 1:
        active_object = selected_objects[0]
        if active_object is not None and active_object.type == "MESH":
            return active_object.to_mesh()
        else:
            self.report({"ERROR"}, "Invalid object selected!")
            return None
    else:
        self.report({"ERROR"}, "Select precisely one object!")
        return None

last_profile = "profile_empty"
def change_profile(self, context):
    global last_profile
    changed_to = self.profiles_enum

    if last_profile == changed_to:
        return

    storage = bpy.context.scene.export_as_array_properties

    profiles[last_profile].vert_suffix = storage.vert_suffix
    profiles[last_profile].index_suffix = storage.index_suffix
    profiles[last_profile].array_begin = storage.array_begin
    profiles[last_profile].array_delim = storage.array_delim
    profiles[last_profile].array_end = storage.array_end
    profiles[last_profile].object_begin = storage.object_begin
    profiles[last_profile].object_delim = storage.object_delim
    profiles[last_profile].object_end = storage.object_end
    last_profile = changed_to

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
    profiles_enum: EnumProperty(
        name="Profile",
        update=change_profile,
        items=generate_profile_items,
    )
    export_mode_enum: EnumProperty(
        name="Export mode",
        items=[
            ("export_mode_verts_plus_faces", "Vertices + faces", ""),
            ("export_mode_verts_only", "Vertices only", ""),
            ("export_mode_faces_only", "Faces only", ""),
            ("export_mode_verts_per_face", "Vertices (per face)", ""),
        ]
    )

def format_vertices(vertices):
    storage = bpy.context.scene.export_as_array_properties
    vert_suffix = storage.vert_suffix
    object_begin = storage.object_begin
    object_delim = storage.object_delim
    object_end = storage.object_end
    array_begin = storage.array_begin
    array_delim = storage.array_delim
    array_end = storage.array_end

    vertex_lines = [
        (
            f"\t{object_begin} {v.co.x}{vert_suffix}{object_delim} "
            f"{v.co.y}{vert_suffix}{object_delim} "
            f"{v.co.z}{vert_suffix} "
            f"{object_end}"
        )
        for v in vertices
    ]
    return (
        f"verts = {array_begin}\n" +
        f"{array_delim}\n".join(vertex_lines) +
        f"\n{array_end}"
    )

def format_faces(faces):
    storage = bpy.context.scene.export_as_array_properties
    index_suffix = storage.index_suffix
    object_begin = storage.object_begin
    object_delim = storage.object_delim
    object_end = storage.object_end
    array_begin = storage.array_begin
    array_delim = storage.array_delim
    array_end = storage.array_end

    face_lines = [
        (
            f"\t{object_begin} " +
            f"{object_delim} ".join([f"{v.index}{index_suffix}" for v in f.verts]) +
            f" {object_end}"
        )
        for f in faces
    ]

    return (
        f"faces = {array_begin}\n" +
        f"{array_delim}\n".join(face_lines) +
        f"\n{array_end}"
    )

def format_vertices_per_face(faces):
    storage = bpy.context.scene.export_as_array_properties
    vert_suffix = storage.vert_suffix
    object_begin = storage.object_begin
    object_delim = storage.object_delim
    object_end = storage.object_end
    array_begin = storage.array_begin
    array_delim = storage.array_delim
    array_end = storage.array_end

    face_lines = [
        (
            f"\t{object_begin} {v.co.x}{vert_suffix}{object_delim} "
            f"{v.co.y}{vert_suffix}{object_delim} "
            f"{v.co.z}{vert_suffix} "
            f"{object_end}"
        )
        for f in faces
        for v in f.verts
    ]

    return (
        f"verts_per_face = {array_begin}\n" +
        f"{array_delim}\n".join(face_lines) +
        f"\n{array_end}"
    )

def get_array_string_for(mesh):
    storage = bpy.context.scene.export_as_array_properties
    export_mode = storage.export_mode_enum

    export_vertices = False
    export_faces = False
    export_vertices_per_face = False
    if export_mode == "export_mode_verts_plus_faces":
        export_vertices = True
        export_faces = True
    elif export_mode == "export_mode_verts_only":
        export_vertices = True
    elif export_mode == "export_mode_faces_only":
        export_faces = True
    elif export_mode == "export_mode_verts_per_face":
        export_vertices_per_face = True

    bm = bmesh.new()
    bm.from_mesh(mesh)
    sep = "\n\n"
    result = (
        f"{format_vertices(bm.verts) if export_vertices else ''}"
        f"{sep if export_vertices else ''}{format_faces(bm.faces) if export_faces else ''}"
        f"{format_vertices_per_face(bm.faces) if export_vertices_per_face else ''}"
    )
    bm.free()
    return result

class OBJECT_OT_export_as_array_disk(bpy.types.Operator):
    bl_label = "Export to disk"
    bl_idname = "object.export_as_array_disk"

    filepath: StringProperty(subtype="FILE_PATH", options={"HIDDEN"})
    check_existing: BoolProperty(default=True, options={"HIDDEN"})

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"};

    def execute(self, context):
        selected_mesh = get_selected_mesh(self, context)

        if selected_mesh != None:
            string = get_array_string_for(selected_mesh)
            try:
                with open(self.filepath, "w") as f:
                    f.write(string)
                self.report({"INFO"}, "Successfuly saved!")
            except Exception as e:
                self.report({"ERROR"}, str(e))

        return {"FINISHED"}

class OBJECT_OT_export_as_array_clipboard(bpy.types.Operator):
    bl_label = "Copy to clipboard"
    bl_idname = "object.export_as_array_clipboard"

    def execute(self, context):
        selected_mesh = get_selected_mesh(self, context)

        if selected_mesh != None:
            string = get_array_string_for(selected_mesh)
            context.window_manager.clipboard = string
            self.report({"INFO"}, "Successfuly copied")

        return {"FINISHED"}

class OBJECT_OT_export_as_array(bpy.types.Operator):
    bl_label = "Export as array"
    bl_idname = "object.export_as_array"

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=250)

    def draw(self, context):
        layout = self.layout
        storage = bpy.context.scene.export_as_array_properties

        row = layout.row()
        row.label(text="Export settings")
        row.prop(storage, "profiles_enum")
        layout.separator(type="LINE")

        split = layout.split(factor=0.5)
        left_col = split.column()
        right_col = split.column()

        props = [
            ("Vertex suffix", "vert_suffix"),
            ("Index suffix", "index_suffix"),
            ("Array begin", "array_begin"),
            ("Array delimiter", "array_delim"),
            ("Array end", "array_end"),
            ("Object begin", "object_begin"),
            ("Object delimiter", "object_delim"),
            ("Object end", "object_end")
        ]
        for prop in props:
            left_col.label(text=prop[0])
            right_col.prop(storage, prop[1], text="")

        layout.prop(storage, "export_mode_enum", text="")

        layout.operator(OBJECT_OT_export_as_array_clipboard.bl_idname)
        layout.operator(OBJECT_OT_export_as_array_disk.bl_idname)

    def execute(self, context):
        return {"FINISHED"}

def menu_func(self, context):
    layout = self.layout
    layout.separator(type="LINE")
    layout.operator(OBJECT_OT_export_as_array.bl_idname)

classes = [
    ExportAsArrayProperties,
    OBJECT_OT_export_as_array,
    OBJECT_OT_export_as_array_clipboard,
    OBJECT_OT_export_as_array_disk
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.export_as_array_properties = PointerProperty(type=ExportAsArrayProperties)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    del bpy.types.Scene.export_as_array_properties
    for c in classes:
        bpy.utils.unregister_class(c)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
    register()
