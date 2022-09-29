# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import os
import bpy.ops
from bpy.utils import (register_class,
                       unregister_class
                       )
from bpy.props import (BoolProperty,
                       StringProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import PropertyGroup 

bl_info = {
    "name": "Material Asset Creator",
    "description": "Quickly create material asset with textures",
    "author": "Anindya Jana",
    "version": (1,0,1),
    "blender": (3,3,0),
    "location": "View3D > Slidebar > Quick Asset",
    "doc_url": "https://github.com/anindya-jana/Material_asset_creator",
    "category": "Material"}


class ASSET_PT_main(bpy.types.Panel):
    bl_label = "material asset creator"
    bl_idname = "A1_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Asset"
    
    def draw(self, context):
        
        assettool=context.scene.asset_tool
        layout = self.layout
        box = layout.box()       
        row = box.row()
        wm = context.window_manager  
        row = box.row()
        row.label(text="Textures folder:") 
        row = box.row()                             
        row.prop(wm, "asset_dir")
        if  wm.asset_dir  != "":
            if wm.asset_dir[0] =='/':
                row = box.box()
                row.label(icon='ERROR')
                row.label(text="Uncheck relative path path")
                row.label(text="Please provide an absolute path")
                
        box = layout.box()
        row = box.row()        
        row.label(text="Select texture maps:")         
        row = box.row()
        row.prop(assettool, "use_base_color")      
        if not assettool.use_base_color:
            row = box.box()
            row.label(icon='GHOST_DISABLED')
            row.label(text="Basecolor is  most important ")              
            row.label(text="map that defines a material!")  
        row = box.row()                
        row.prop(assettool, "use_AO")
        row = box.row()
        row.prop(assettool, "use_roughness")
        row = box.row()
        row.prop(assettool, "use_metallic")
        row = box.row()
        row.prop(assettool, "use_specular")
        row = box.row()
        row.prop(assettool, "use_normal")
        row = box.row()
        row.prop(assettool, "use_displacement")
        row = box.row()
        row.prop(assettool, "use_alpha")
        box = layout.box()
        row = box.row()
        
        row.scale_y=1.7
        row.operator('shader.material',icon='MATERIAL')
        row = box.row()
        row.scale_y=1.7
        row.operator('shader.asset',icon='ASSET_MANAGER')
        
class SHADER_OT_material(bpy.types.Operator):     
    bl_label = "Create Materials"
    bl_idname = "shader.material"   
    bl_description="Automatically create material based on the maps available ."    
    def execute(self, context):    
        
        assettool=context.scene.asset_tool
        wm = context.window_manager                      
        path = wm.asset_dir    
        scene = context.scene
        for root, subdirectories, files in os.walk(path):
#            for subdirectory in subdirectories:
#                print(os.path.join(root, subdirectory))
            has_map=False
            has_ao=False
            for file_name in files:
                file_name=file_name.lower()
                if file_name.find("albedo")!=-1 or file_name.find("col")!=-1 or  file_name.find("diff")!=-1:
                    has_map=True
                    if file_name.find("albedo")!=-1: 
                        material_name=file_name.replace('albedo', '') 
                    if file_name.find("color")!=-1:     
                        material_name=file_name.replace('color', '')
                    else:
                        if file_name.find("col")!=-1 :    
                            material_name=file_name.replace('col', '')     
                    if file_name.find("diffuse")!=-1 :    
                        material_name=file_name.replace('diffuse', '')  
                    else:
                        if file_name.find("diff")!=-1:     
                            material_name=file_name.replace('diff', '')                                                          
                    material_name=material_name.split(".", 1)[0]
                    if material_name in bpy.data.materials:
                        print(material_name+" has already used")        
                        has_map=False
                    
                if file_name.find("ao")!=-1 or file_name.find("ambientocclusion")!=-1: 
                    has_ao=True   
       
            if has_map:                                
                material_new = bpy.data.materials.new(name= material_name)
                print("material "+material_name+" created")
                material_new.use_nodes =True        
                principalshader = material_new.node_tree.nodes.get('Principled BSDF')  
                tex_cor=material_new.node_tree.nodes.new('ShaderNodeTexCoord')
                tex_cor.location=(-1250,-70)
                mapping=material_new.node_tree.nodes.new('ShaderNodeMapping')
                mapping.location=(-1000,0)                  
                material_new.node_tree.links.new(tex_cor.outputs[2],mapping.inputs[0])         
                if has_ao and  assettool.use_AO:
                    mix=material_new.node_tree.nodes.new('ShaderNodeMixRGB')
                    mix.location=(-300,300)
                    mix.blend_type='MULTIPLY'
                    material_new.node_tree.links.new(mix.outputs[0],principalshader.inputs[0])                    
                for file_name in files:
                    file_path =os.path.join(root, file_name) 
                    file_name=file_name.lower()                                            
                    if has_ao and  assettool.use_AO:
                        if (file_name.find("albedo")!=-1 or file_name.find("col")!=-1  or  file_name.find("diff")!=-1) and  assettool.use_base_color:
                            base_color=material_new.node_tree.nodes.new('ShaderNodeTexImage')
                            base_color.location=(-700,600)
                            base_color.image = bpy.data.images.load(file_path)
                            mix= principalshader.inputs[0].links[0].from_node
                            material_new.node_tree.links.new(base_color.outputs[0],mix.inputs[1]) 
                            material_new.node_tree.links.new(mapping.outputs[0],base_color.inputs[0])
                                                         
                        if  file_name.find("ao")!=-1 or file_name.find("ambientocclusion")!=-1:
                            ambient=material_new.node_tree.nodes.new('ShaderNodeTexImage')
                            ambient.location=(-700,300)
                            ambient.image = bpy.data.images.load(file_path)
                            ambient.image.colorspace_settings.name = 'Non-Color'
                            mix= principalshader.inputs[0].links[0].from_node
                            material_new.node_tree.links.new(ambient.outputs[0],mix.inputs[2])
                            material_new.node_tree.links.new(mapping.outputs[0],ambient.inputs[0])
                    else:                                                                                                             
                        if (file_name.find("albedo")!=-1 or file_name.find("col")!=-1  or  file_name.find("diff")!=-1) and  assettool.use_base_color:
                            base_color=material_new.node_tree.nodes.new('ShaderNodeTexImage')
                            base_color.location=(-700,300)
                            base_color.image = bpy.data.images.load(file_path)
                            material_new.node_tree.links.new(base_color.outputs[0],principalshader.inputs[0])   
                            material_new.node_tree.links.new(mapping.outputs[0],base_color.inputs[0])
                                          
                    if (file_name.find("metallic")!=-1) and  assettool.use_metallic:    
                        metallic=material_new.node_tree.nodes.new('ShaderNodeTexImage')
                        metallic.location=(-350,150)
                        metallic.image = bpy.data.images.load(file_path)
                        metallic.image.colorspace_settings.name = 'Non-Color'
                        material_new.node_tree.links.new(metallic.outputs[0],principalshader.inputs[6])
                        material_new.node_tree.links.new(mapping.outputs[0],metallic.inputs[0])
                         
                    if (file_name.find("specular")!=-1 or file_name.find("spec")!=-1 or file_name.find("refl")!=-1) and  assettool.use_specular:    
                        specular=material_new.node_tree.nodes.new('ShaderNodeTexImage')
                        specular.location=(-900,0)
                        specular.image = bpy.data.images.load(file_path)
                        specular.image.colorspace_settings.name = 'Non-Color'
                        material_new.node_tree.links.new(specular.outputs[0],principalshader.inputs[7])
                        material_new.node_tree.links.new(mapping.outputs[0],specular.inputs[0])
                         
                    if (file_name.find("gloss")!=-1 or file_name.find("smoothness")!=-1 ) and  assettool.use_roughness:    
                        gloss=material_new.node_tree.nodes.new('ShaderNodeTexImage')
                        gloss.location=(-630,-100)
                        gloss.image = bpy.data.images.load(file_path)
                        gloss.image.colorspace_settings.name = 'Non-Color'
               
                        invert=material_new.node_tree.nodes.new('ShaderNodeInvert')
                        invert.location=(-250,-100)
                        material_new.node_tree.links.new(gloss.outputs[0],invert.inputs[1])
                        material_new.node_tree.links.new(invert.outputs[0],principalshader.inputs[9])
                        material_new.node_tree.links.new(mapping.outputs[0],gloss.inputs[0])
                                       
                    if (file_name.find("roughness")!=-1  or file_name.find("rough")!=-1) and   assettool.use_roughness:    
                        roughness=material_new.node_tree.nodes.new('ShaderNodeTexImage')
                        roughness.location=(-350,-100)
                        roughness.image = bpy.data.images.load(file_path)
                        roughness.image.colorspace_settings.name = 'Non-Color'
                        material_new.node_tree.links.new(roughness.outputs[0],principalshader.inputs[9])
                        material_new.node_tree.links.new(mapping.outputs[0],roughness.inputs[0])
                                                                                                                   
                    if (file_name.find("normal")!=-1 or file_name.find("nrm")!=-1 or file_name.find("nor")!=-1) and  assettool.use_normal:  
                        normal=material_new.node_tree.nodes.new('ShaderNodeTexImage')
                        normal.location=(-600,-400)
                        normal.image = bpy.data.images.load(file_path)
                        normal.image.colorspace_settings.name = 'Non-Color'

                        normal_map=material_new.node_tree.nodes.new('ShaderNodeNormalMap')
                        normal_map.location=(-250,-400)
                        
                        material_new.node_tree.links.new(normal.outputs[0],normal_map.inputs[1])
                        material_new.node_tree.links.new(normal_map.outputs[0],principalshader.inputs[22])
                        material_new.node_tree.links.new(mapping.outputs[0],normal.inputs[0])
                         
                    if (file_name.find("disp")!=-1 or file_name.find("height")!=-1) and  assettool.use_displacement:   
                        displacement=material_new.node_tree.nodes.new('ShaderNodeTexImage')
                        displacement.location=(-300,-600)
                        displacement.image = bpy.data.images.load(file_path)
                        displacement.image.colorspace_settings.name = 'Non-Color'
                        
                        disp=material_new.node_tree.nodes.new('ShaderNodeDisplacement')
                        disp.location=(50,-500)
                        disp.inputs[2].default_value=0.1
                        
                        mat_out= material_new.node_tree.nodes.get('Material Output')
                        material_new.node_tree.links.new(displacement.outputs[0],disp.inputs[0])
                        material_new.node_tree.links.new(disp.outputs[0],mat_out.inputs[2])
                        material_new.cycles.displacement_method = 'BOTH'
                        material_new.node_tree.links.new(mapping.outputs[0],displacement.inputs[0])
                         
                    if file_name.find("alpha")!=-1 and assettool.use_alpha:   
                        alpha=material_new.node_tree.nodes.new('ShaderNodeTexImage')
                        alpha.location=(-350,-100)
                        alpha.image = bpy.data.images.load(file_path)
                        material_new.blend_method = 'CLIP'

                        material_new.node_tree.links.new(alpha.outputs[0],principalshader.inputs[21])
                        material_new.node_tree.links.new(mapping.outputs[0],alpha.inputs[0])                                                                                            
                           
                                                                                                                                            
        return {'FINISHED'} 
class SHADER_OT_asset(bpy.types.Operator):     
    bl_label = "Mark material assets"
    bl_idname = "shader.asset"   
    bl_description="Automatically marks the material created as assets."    
    def execute(self, context):  
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'

        for material in bpy.data.materials:
            if material.asset_data is  None: 
                material.asset_mark()
                material.asset_generate_preview()
            
          
        return {'FINISHED'}
  
class AssetSceneProperties(PropertyGroup):
         
    use_base_color : BoolProperty(
       name = "Diffuse/Albedo",
       default = True,
       description=''
       )  
    use_AO : BoolProperty(
       name = "Ambient Occlusion(AO)",
       default = True,
       description=''
       )
    use_roughness : BoolProperty(
       name = "Roughness/Gloss",
       default = True,
       description=''
       )
    use_metallic : BoolProperty(
       name = "Metallic",
       default = True,
       description=''
       )
    use_specular : BoolProperty(
       name = "Specular",
       default = True,
       description=''
       )   
    use_normal : BoolProperty(
       name = "Normal",
       default = True,
       description=''
       )
    use_displacement : BoolProperty(
       name = "Displacement",
       default = True,
       description=''
       )       
    use_alpha : BoolProperty(
       name = "Alpha",
       default = True,
       description=''
       )            
    
classes = (
    ASSET_PT_main,
    SHADER_OT_asset,
    SHADER_OT_material,
    AssetSceneProperties,
    )
def register():
    from bpy.types import WindowManager
    from bpy.props import (
        StringProperty,
    )

    WindowManager.asset_dir = StringProperty(
        name="",
        subtype='DIR_PATH',
        default="",
        
    )
  
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.asset_tool = PointerProperty(type= AssetSceneProperties)
        
def unregister():  
    
    del bpy.types.Scene.asset_tool
    for cls in reversed(classes):
        unregister_class(cls)
if __name__ == "__main__":
    register()
        
