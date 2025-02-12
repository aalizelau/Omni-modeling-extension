import omni.usd
from pxr import UsdGeom, UsdShade, Gf, Usd, Sdf
from pathlib import Path
import omni.kit.commands

# Path to your referenced USD file
usd_file_path = Path(__file__).parent.parent.parent.parent / "data" / "clean5.usdc"

class SofaCreator:
    def __init__(self):
        # This will hold the material prim’s path once created
        self.material_path = None

    def create_sofa_part(self, root_path, name, position, scale, usd_file_path):
        """
        Create a sofa part by referencing an external USD file, applying transforms,
        and binding the material if available.
        """
        stage = omni.usd.get_context().get_stage()
        # The part will be placed under the passed-in scope (i.e. the Geometry folder)
        part_path = f"{root_path}/{name}"
        prim = stage.DefinePrim(part_path)
        references = prim.GetReferences()
        references.AddReference(str(usd_file_path))
        
        # Apply translation and scale
        xformable = UsdGeom.Xformable(prim)
        xformable.ClearXformOpOrder()
        xformable.AddTranslateOp().Set(Gf.Vec3f(*position))
        xformable.AddScaleOp().Set(Gf.Vec3f(*scale))
        
        # Bind the material if it has been created
        if self.material_path:
            mat_prim = stage.GetPrimAtPath(self.material_path)
            if mat_prim:
                material = UsdShade.Material(mat_prim)
                UsdShade.MaterialBindingAPI(prim).Bind(material)
        
        return prim

    def create_sofa_material(self, looks_scope_path):
        """
        Create a material prim in the Looks folder using the provided MDL URL.
        """
        stage = omni.usd.get_context().get_stage()
        # Generate a unique path for the material prim under the Looks scope.
        material_path = omni.usd.get_stage_next_free_path(
            stage, f"{looks_scope_path}/Cotton_Fine_Woven", False
        )
        # Create the material prim using an Omni Kit command.
        omni.kit.commands.execute(
            'CreateMdlMaterialPrimCommand',
            mtl_url='https://omniverse-content-production.s3.us-west-2.amazonaws.com/Materials/vMaterials_2/Fabric/Fabric_Cotton_Fine_Woven.mdl',
            mtl_name='Fabric_Cotton_Fine_Woven',
            mtl_path=str(material_path)
        )
        # (Optional) Select the newly created material in the stage
        omni.kit.commands.execute(
            'SelectPrims',
            old_selected_paths=[],
            new_selected_paths=[str(material_path)],
            expand_in_stage=True
        )
        return str(material_path)

    def create_default_sofa(
            self,
            length=200,
            num_cushions = 2, 
            depth=100,
            cushion_height=15,
            base_height=25,
            arms=True,
            arm_height=60,
            arm_width=20,
            backrest=True,
            backrest_depth=15,
            backrest_height=80,
            leg_base =7.5, 
            leg_height =7.5,
            leg_offset =5.0
        ):
        stage = omni.usd.get_context().get_stage()
        # Create a unique sofa root under /World
        sofa_root_path = omni.usd.get_stage_next_free_path(stage, "/World/Sofa", True)
        sofa_root = UsdGeom.Xform.Define(stage, sofa_root_path)
        sofa_root.AddTranslateOp().Set(Gf.Vec3f(0, 0, 0))
        
        # Create Geometry and Looks scopes under the sofa root
        geom_scope_path = omni.usd.get_stage_next_free_path(
            stage, f"{sofa_root_path}/Geometry", False
        )
        looks_scope_path = omni.usd.get_stage_next_free_path(
            stage, f"{sofa_root_path}/Looks", False
        )
        omni.kit.commands.execute('CreatePrim', prim_type='Scope', prim_path=str(geom_scope_path))
        omni.kit.commands.execute('CreatePrim', prim_type='Scope', prim_path=str(looks_scope_path))
        
        # Create the material in the Looks folder and store its path for later binding.
        self.material_path = self.create_sofa_material(looks_scope_path)
        
        # Create each sofa component under the Geometry folder.
        self.create_base(geom_scope_path, length, base_height, depth, usd_file_path)
        self.create_legs(geom_scope_path, length, depth, leg_base, leg_height, leg_offset, usd_file_path)
        self.create_cushions(geom_scope_path, length, num_cushions, base_height, cushion_height, depth, usd_file_path)
        if arms:
            self.create_arms(geom_scope_path, length, arm_width, arm_height, depth, backrest, backrest_depth, usd_file_path)
        if backrest:
            self.create_backrest(geom_scope_path, length, base_height, backrest_height, depth, backrest_depth, usd_file_path)
        
        return sofa_root

    def customize_sofa(self, sofa_root_path, length, depth, cushion_height, base_height,
                       arms, arm_height, arm_width, backrest, backrest_depth, backrest_height):
        stage = omni.usd.get_context().get_stage()
        selection = omni.usd.get_context().get_selection()
        selection.clear_selected_prim_paths()
        
        # Get or create the sofa root.
        sofa_root = stage.GetPrimAtPath(sofa_root_path)
        if not sofa_root:
            sofa_root = UsdGeom.Xform.Define(stage, sofa_root_path)
            sofa_root.AddTranslateOp().Set(Gf.Vec3f(0, 0, 0))
        else:
            # Instead of removing the entire sofa root, we clear out the Geometry folder.
            geom_scope_path = f"{sofa_root_path}/Geometry"
            geom_scope = stage.GetPrimAtPath(geom_scope_path)
            if geom_scope:
                for child in list(geom_scope.GetChildren()):
                    stage.RemovePrim(child.GetPath())
            else:
                geom_scope_path = omni.usd.get_stage_next_free_path(
                    stage, f"{sofa_root_path}/Geometry", False
                )
                omni.kit.commands.execute('CreatePrim', prim_type='Scope', prim_path=str(geom_scope_path))
        
        # Recreate sofa components in the Geometry folder.
        self.create_base(geom_scope_path, length, base_height, depth, usd_file_path)
        self.create_legs(geom_scope_path, length, depth, base_height, usd_file_path)
        self.create_cushions(geom_scope_path, length, base_height, cushion_height, depth, usd_file_path)
        if arms:
            self.create_arms(geom_scope_path, length, arm_width, arm_height, depth, backrest, backrest_depth, usd_file_path)
        if backrest:
            self.create_backrest(geom_scope_path, length, base_height, backrest_height, depth, backrest_depth, usd_file_path)
        
        return sofa_root

    def create_base(self, parent_path, length, base_height, depth, usd_file_path):
        base_scale = [length, base_height, depth]
        self.create_sofa_part(parent_path, "Base", (0, base_height / 2, 0), base_scale, usd_file_path)

    def create_legs(self, parent_path, length, depth, leg_base, leg_height, leg_offset, usd_file_path):
        leg_scale = [leg_base, leg_height, leg_base]
        directions = {
            (-1, -1): "Left_Front",
            (-1,  1): "Left_Back",
            ( 1, -1): "Right_Front",
            ( 1,  1): "Right_Back"
        }
        for (x_dir, z_dir), dir_name in directions.items():
            x_pos = x_dir * (length / 2 - leg_scale[0] / 2 -leg_offset)
            z_pos = z_dir * (depth / 2 - leg_scale[2] / 2 -leg_offset)
            self.create_sofa_part(parent_path, f"Leg_{dir_name}", (x_pos, 0, z_pos), leg_scale, usd_file_path)

    def create_cushions(self, parent_path, length, num_cushions, base_height, cushion_height, depth, usd_file_path):
        cushion_x_scale = length / num_cushions
        cushion_z_scale = depth
        for i in range(num_cushions):
            x = -length / 2 + cushion_x_scale / 2 + i * cushion_x_scale
            y_pos = base_height + cushion_height / 2
            self.create_sofa_part(parent_path, f"Cushion_{i}", (x, y_pos, 0), [cushion_x_scale, cushion_height, cushion_z_scale], usd_file_path)

    def create_arms(self, parent_path, length, arm_width, arm_height, depth, backrest, backrest_depth, usd_file_path):
        arm_depth = depth + (backrest_depth if backrest else 0)
        arm_z_pos = backrest_depth / 2 if backrest else 0
        for side in [-1, 1]:
            x_pos = side * (length / 2 + arm_width / 2)
            side_name = 'Left' if side == -1 else 'Right'
            self.create_sofa_part(parent_path, f"Arm_{side_name}", (x_pos, arm_height / 2, arm_z_pos), [arm_width, arm_height, arm_depth], usd_file_path)

    def create_backrest(self, parent_path, length, base_height, backrest_height, depth, backrest_depth, usd_file_path):
        backrest_z = depth / 2 + backrest_depth / 2
        backrest_y = backrest_height / 2 + base_height/2
        self.create_sofa_part(parent_path, "Backrest", (0, backrest_y, backrest_z), [length, base_height + backrest_height, backrest_depth], usd_file_path)