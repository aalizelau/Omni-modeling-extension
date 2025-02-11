import omni.usd
from pxr import UsdGeom, Gf, Usd
from pathlib import Path

usd_file_path = Path(__file__).parent.parent.parent.parent / "data" / "clean2.usdc"

class SofaCreator:
    def create_sofa_part(self, root_path, name, position, scale, usd_file_path):
        # Get the current stage
        stage = omni.usd.get_context().get_stage()
        
        # Define the path where the USD component will be placed
        path = f"{root_path}/{name}"

        # cube = UsdGeom.Cube.Define(stage, path)
        # cube.CreateSizeAttr(1.0)
        # cube.AddTranslateOp().Set(Gf.Vec3f(*position))
        # cube.AddScaleOp().Set(Gf.Vec3f(*scale))

        # Open the USD file that contains the component
        sofa_stage = Usd.Stage.Open(str(usd_file_path))

        # Copy the content from the external stage to the current stage
        prim = stage.DefinePrim(path)
        references= prim.GetReferences()
        references.AddReference(str(usd_file_path))

        # Apply transformations to the copied component
        xformable = UsdGeom.Xformable(prim)
        xformable.ClearXformOpOrder()  # Clear existing ops to avoid conflicts
        xformable.AddTranslateOp().Set(Gf.Vec3f(*position))
        xformable.AddScaleOp().Set(Gf.Vec3f(*scale))

        return prim

    def create_default_sofa(self, length=2.0, 
                            depth=1.0, 
                            cushion_height=0.15, 
                            base_height=0.2, 
                            arms=True, 
                            arm_height=0.6, 
                            arm_width=0.2, 
                            backrest=True, 
                            backrest_depth=0.1, 
                            backrest_height=0.8):
        stage = omni.usd.get_context().get_stage()
        
        # Generate unique sofa root path
        sofa_root_path = omni.usd.get_stage_next_free_path(stage, "/World/Sofa", True)
        sofa_root = UsdGeom.Xform.Define(stage, sofa_root_path)
        sofa_root.AddTranslateOp().Set(Gf.Vec3f(0, 0, 0))
        
        # Create each part of the sofa
        self.create_base(sofa_root_path, length, base_height, depth, usd_file_path)
        self.create_legs(sofa_root_path, length, depth, base_height, usd_file_path)
        self.create_cushions(sofa_root_path, length, base_height, cushion_height, depth, usd_file_path)
        if arms:
            self.create_arms(sofa_root_path, length, arm_width, arm_height, depth, backrest, backrest_depth, usd_file_path)
        if backrest:
            self.create_backrest(sofa_root_path, length, base_height, backrest_height, depth, backrest_depth, usd_file_path)
        
        return sofa_root

    def customize_sofa(self, sofa_root_path, length, 
                    depth, 
                    cushion_height, 
                    base_height, 
                    arms, 
                    arm_height, 
                    arm_width, 
                    backrest, 
                    backrest_depth, 
                    backrest_height):
        stage = omni.usd.get_context().get_stage()
        selection = omni.usd.get_context().get_selection()
        
        # Clear any selected prims
        selection.clear_selected_prim_paths()
        
       # Get the sofa prim if it exists; otherwise, create it.
        sofa_root = stage.GetPrimAtPath(sofa_root_path)
        if not sofa_root:
            # Sofa prim does not exist; define it and set a default translation.
            sofa_root = UsdGeom.Xform.Define(stage, sofa_root_path)
            sofa_root.AddTranslateOp().Set(Gf.Vec3f(0, 0, 0))
        else:
            # Instead of removing the prim, remove its children (which hold the geometry).
            for child in list(sofa_root.GetChildren()):
                stage.RemovePrim(child.GetPath())
        
        # Create the sofa parts with the new parameters
        self.create_base(sofa_root_path, length, base_height, depth)
        self.create_legs(sofa_root_path, length, depth, base_height)
        self.create_cushions(sofa_root_path, length, base_height, cushion_height, depth)
        if arms:
            self.create_arms(sofa_root_path, length, arm_width, arm_height, depth, backrest, backrest_depth)
        if backrest:
            self.create_backrest(sofa_root_path, length, base_height, backrest_height, depth, backrest_depth)
        
        return sofa_root

    def create_base(self, sofa_root_path, length, base_height, depth, usd_file_path):
        base_scale = [length, base_height, depth]
        self.create_sofa_part(sofa_root_path, "Base", (0, base_height / 2, 0), base_scale, usd_file_path)

    def create_legs(self, sofa_root_path, length, depth, base_height, usd_file_path):
        # Fixed-size legs
        leg_scale = [0.15, 0.15, 0.15]
        directions = {
            (-1, -1): "Left_Front",
            (-1, 1): "Left_Back",
            (1, -1): "Right_Front",
            (1, 1): "Right_Back"
        }
        for (x_dir, z_dir), dir_name in directions.items():
            x_pos = x_dir * (length / 2 - leg_scale[0] / 2)
            z_pos = z_dir * (depth / 2 - leg_scale[2] / 2)
            self.create_sofa_part(sofa_root_path, f"Leg_{dir_name}", (x_pos, -leg_scale[1] / 2, z_pos), leg_scale, usd_file_path)

    def create_cushions(self, sofa_root_path, length, base_height, cushion_height, depth, usd_file_path):
        # Create cushions (3 by default)
        num_cushions = 3
        cushion_x_scale = length / num_cushions
        cushion_z_scale = depth
        for i in range(num_cushions):
            x = -length / 2 + cushion_x_scale / 2 + i * cushion_x_scale
            y_pos = base_height + cushion_height / 2
            self.create_sofa_part(sofa_root_path, f"Cushion_{i}", (x, y_pos, 0), [cushion_x_scale, cushion_height, cushion_z_scale], usd_file_path)

    def create_arms(self, sofa_root_path, length, arm_width, arm_height, depth, backrest, backrest_depth, usd_file_path):
        # Create arms on both sides
        arm_depth = depth + (backrest_depth if backrest else 0)
        arm_z_pos = backrest_depth / 2 if backrest else 0
        for side in [-1, 1]:
            x_pos = side * (length / 2 + arm_width / 2)
            side_name = 'Left' if side == -1 else 'Right'
            self.create_sofa_part(sofa_root_path, f"Arm_{side_name}", (x_pos, arm_height / 2, arm_z_pos), [arm_width, arm_height, arm_depth], usd_file_path)

    def create_backrest(self, sofa_root_path, length, base_height, backrest_height, depth, backrest_depth, usd_file_path):
        backrest_z = depth / 2 + backrest_depth / 2
        backrest_y = base_height + backrest_height / 2
        self.create_sofa_part(sofa_root_path, "Backrest", (0, backrest_y, backrest_z), [length, backrest_height, backrest_depth], usd_file_path)