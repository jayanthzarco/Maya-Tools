import maya.cmds as cmds


class SceneOptimizer:
    def __init__(self):
        self.create_ui()

    def create_ui(self):
        if cmds.window("optimizeWindow", exists=True):
            cmds.deleteUI("optimizeWindow")

        cmds.window("optimizeWindow", title="Scene Optimizer", widthHeight=(400, 300))
        cmds.columnLayout(adjustableColumn=True)

        cmds.text(label="Choose optimization options:")

        cmds.checkBox("removeUnusedNodes", label="Remove Unused Nodes", value=True)
        cmds.checkBox("removeUnusedShadingNetworks", label="Remove Unused Shading Networks", value=True)
        cmds.checkBox("removeUnusedTextures", label="Remove Unused Textures", value=True)
        cmds.checkBox("simplifyMeshes", label="Simplify Meshes", value=True)
        cmds.checkBox("checkNonManifold", label="Check Non-Manifold Geometry", value=True)
        cmds.checkBox("mergeSimilarMaterials", label="Merge Similar Materials", value=True)
        cmds.checkBox("checkDuplicateMeshes", label="Check for Duplicate Meshes", value=True)
        cmds.checkBox("deleteHistory", label="Delete History of Selected Objects", value=False)
        cmds.checkBox("optimizeHierarchy", label="Optimize Scene Hierarchy", value=True)
        cmds.checkBox("optimizeLights", label="Optimize Lights", value=True)
        cmds.checkBox("purgeUnusedNodes", label="Purge Unused Nodes", value=True)
        cmds.checkBox("saveBeforeOptimization", label="Save Scene Before Optimization", value=True)

        cmds.button(label="Optimize Scene", command=self.optimize_scene)

        cmds.showWindow("optimizeWindow")

    def optimize_scene(self, *args):
        if cmds.checkBox("saveBeforeOptimization", query=True, value=True):
            cmds.file(save=True)

        if cmds.checkBox("removeUnusedNodes", query=True, value=True):
            self.remove_unused_nodes()

        if cmds.checkBox("removeUnusedShadingNetworks", query=True, value=True):
            self.remove_unused_shading_networks()

        if cmds.checkBox("removeUnusedTextures", query=True, value=True):
            self.remove_unused_textures()

        if cmds.checkBox("simplifyMeshes", query=True, value=True):
            self.simplify_meshes()

        if cmds.checkBox("checkNonManifold", query=True, value=True):
            self.check_non_manifold()

        if cmds.checkBox("mergeSimilarMaterials", query=True, value=True):
            self.merge_similar_materials()

        if cmds.checkBox("checkDuplicateMeshes", query=True, value=True):
            self.check_duplicate_meshes()

        if cmds.checkBox("deleteHistory", query=True, value=True):
            self.delete_history()

        if cmds.checkBox("optimizeHierarchy", query=True, value=True):
            self.optimize_hierarchy()

        if cmds.checkBox("optimizeLights", query=True, value=True):
            self.optimize_lights()

        if cmds.checkBox("purgeUnusedNodes", query=True, value=True):
            self.purge_unused_nodes()

        cmds.confirmDialog(title="Optimization Complete", message="Scene optimization is complete!", button="OK")

    def remove_unused_nodes(self):
        unused_nodes = cmds.ls(type='lambert', long=True)
        for node in unused_nodes:
            if cmds.listConnections(node + '.outColor') is None:
                cmds.delete(node)

    def remove_unused_shading_networks(self):
        shading_groups = cmds.ls(type='shadingEngine', long=True)
        for shading_group in shading_groups:
            connections = cmds.listConnections(shading_group + '.surfaceShader', d=False)
            if not connections:
                cmds.delete(shading_group)

    def remove_unused_textures(self):
        textures = cmds.ls(type='file', long=True)
        for texture in textures:
            if not cmds.listConnections(texture + '.outColor'):
                cmds.delete(texture)

    def simplify_meshes(self):
        meshes = cmds.ls(type='mesh', long=True)
        for mesh in meshes:
            cmds.polyReduce(mesh, percentage=50)

    def check_non_manifold(self):
        meshes = cmds.ls(type='mesh', long=True)
        non_manifold = cmds.polyInfo(meshes, nonManifold=True)
        if non_manifold:
            cmds.polyCleanup(meshes, nonManifold=True)

    def merge_similar_materials(self):
        materials = cmds.ls(materials=True)
        unique_materials = {}
        for mat in materials:
            shader_attrs = cmds.listAttr(mat, string="*")  # List all attributes
            attr_values = tuple(cmds.getAttr(mat + "." + attr) for attr in shader_attrs if
                                cmds.attributeQuery(attr, node=mat, exists=True))
            unique_materials.setdefault(attr_values, []).append(mat)

        for mats in unique_materials.values():
            if len(mats) > 1:
                # Merge materials (implement merging logic as needed)
                cmds.hyperShade(objects=mats)

    def check_duplicate_meshes(self):
        meshes = cmds.ls(type='mesh', long=True)
        unique_meshes = set()
        for mesh in meshes:
            mesh_shape = cmds.listRelatives(mesh, shapes=True)[0]
            unique_meshes.add(mesh_shape)

        # Logic to merge duplicates would go here
        # This is a placeholder; implement merging logic as needed.

    def delete_history(self):
        selected_objects = cmds.ls(selection=True)
        if selected_objects:
            cmds.delete(selected_objects, constructionHistory=True)
        else:
            cmds.warning("No objects selected to delete history.")

    def optimize_hierarchy(self):
        # Flatten hierarchy logic
        selection = cmds.ls(selection=True, long=True)
        for obj in selection:
            children = cmds.listRelatives(obj, children=True, fullPath=True) or []
            for child in children:
                cmds.parent(child, world=True)

    def optimize_lights(self):
        lights = cmds.ls(type='light', long=True)
        for light in lights:
            if not cmds.listConnections(light + '.message'):
                cmds.delete(light)

    def purge_unused_nodes(self):
        cmds.evalDeferred("cmds.purge()")

if __name__ == '__main__':
    SceneOptimizer()

"""
created by Jayanth
15-07-2024
"""
