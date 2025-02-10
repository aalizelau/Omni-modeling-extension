import omni.usd
from pxr import UsdGeom, Gf

class SofaCreator:
    @staticmethod
    def create_sofa_part(root_path, name, position, scale):
        stage = omni.usd.get_context().get_stage()
        path = f"{root_path}/{name}"
        cube = UsdGeom.Cube.Define(stage, path)
        cube.CreateSizeAttr(1.0)
        # Clear existing ops to avoid conflicts (optional precaution)
        xformable = UsdGeom.Xformable(cube)
        xformable.ClearXformOpOrder()
        # Add fresh transform ops
        cube.AddTranslateOp().Set(Gf.Vec3f(*position))
        cube.AddScaleOp().Set(Gf.Vec3f(*scale))
        return cube

    @classmethod
    def create_default_sofa(cls, 
                    length=2.0, 
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


        # Create base
        base_scale = [length, base_height, depth]
        cls.create_sofa_part(sofa_root_path, "Base", (0, base_height/2, 0), base_scale)

        # Create legs (fixed size)
        leg_scale = [0.15, 0.15, 0.15]
        directions = {
            (-1, -1): "Left_Front",
            (-1, 1): "Left_Back",
            (1, -1): "Right_Front",
            (1, 1): "Right_Back"
        }
        for (x_dir, z_dir), dir_name in directions.items():
            x_pos = x_dir * (length/2 - leg_scale[0]/2)
            z_pos = z_dir * (depth/2 - leg_scale[2]/2)
            cls.create_sofa_part(sofa_root_path, f"Leg_{dir_name}", (x_pos, -leg_scale[1]/2, z_pos), leg_scale)

        # Create cushions (3 by default)
        num_cushions = 3
        cushion_x_scale = length / num_cushions
        cushion_z_scale = depth * depth
        for i in range(num_cushions):
            x = -length/2 + cushion_x_scale/2 + i * cushion_x_scale
            y_pos = base_height + cushion_height/2
            cls.create_sofa_part(sofa_root_path, f"Cushion_{i}", (x, y_pos, 0), 
                               [cushion_x_scale, cushion_height, cushion_z_scale])

        # Create arms if enabled
        if arms:
            arm_depth = depth + (backrest_depth if backrest else 0)
            arm_z_pos = backrest_depth/2 if backrest else 0
            for side in [-1, 1]:
                x_pos = side * (length/2 + arm_width/2)
                cls.create_sofa_part(sofa_root_path, f"Arm_{'Left' if side == -1 else 'Right'}", 
                                   (x_pos, arm_height/2, arm_z_pos), 
                                   [arm_width, arm_height, arm_depth])

        # Create backrest if enabled
        if backrest:
            backrest_z = depth/2 + backrest_depth/2
            backrest_y = base_height + backrest_height/2
            cls.create_sofa_part(sofa_root_path, "Backrest", (0, backrest_y, backrest_z),
                               [length, backrest_height, backrest_depth])
        
        return sofa_root