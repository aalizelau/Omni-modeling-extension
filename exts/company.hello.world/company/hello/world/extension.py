import omni.ext
import omni.ui as ui
import omni.usd
from pxr import UsdGeom, UsdPhysics, Gf, PhysxSchema

class SofaCreator:
    @staticmethod
    def create_sofa_part(name, position, scale, color=None):
        stage = omni.usd.get_context().get_stage()

         # Ensure valid prim name
        valid_name = name.replace(" ", "_").replace("-", "_")
        path = f"/World/Sofa/{valid_name}"

         # Create parent Xform if it doesn't exist
        UsdGeom.Xform.Define(stage, "/World")
        UsdGeom.Xform.Define(stage, "/World/Sofa")

        cube = UsdGeom.Cube.Define(stage, path)

        cube.CreateSizeAttr(1.0)
        cube.AddTranslateOp().Set(Gf.Vec3f(*position))
        cube.AddScaleOp().Set(Gf.Vec3f(*scale))
        
        # Add physics
        rigid_body = UsdPhysics.RigidBodyAPI.Apply(stage.GetPrimAtPath(path))
        rigid_body.CreateRigidBodyEnabledAttr(True)
        collision_api = PhysxSchema.PhysxCollisionAPI.Apply(stage.GetPrimAtPath(path))
        collision_api.CreateRestOffsetAttr(0.0)
        collision_api.CreateContactOffsetAttr(0.02)
        
        
        return cube

    @classmethod
    def create_default_sofa(cls):
        # Create root sofa transform
        stage = omni.usd.get_context().get_stage()
        sofa_root = UsdGeom.Xform.Define(stage, "/World/Sofa")
        sofa_root.AddTranslateOp().Set(Gf.Vec3f(0, 0, 0))

         # Fixed leg naming with valid prim names
        directions = {
            (-1, -1): "Left_Front",
            (-1, 1): "Left_Back",
            (1, -1): "Right_Front",
            (1, 1): "Right_Back"
        }
        

        # Sofa base
        base_scale = [2.0, 0.2, 1.0]
        cls.create_sofa_part("Base", 
                           position=(0, base_scale[1]/2, 0), 
                           scale=base_scale,
                           color=(0.3, 0.2, 0.1))
        
        for (x, z), dir_name in directions.items():
            leg_scale = [0.15, 0.15, 0.15]
            cls.create_sofa_part(f"Leg_{dir_name}", 
                               position=(x * (base_scale[0]/2 - leg_scale[0]), 
                                        leg_scale[1]/2, 
                                        z * (base_scale[2]/2 - leg_scale[2])),
                               scale=leg_scale,
                               color=(0.1, 0.1, 0.1))
        
        
        # Cushions
        cushion_scale = [0.9, 0.15, 0.9]
        for i in range(3):
            cls.create_sofa_part(f"Cushion_{i}", 
                               position=(-0.8 + i*0.8, base_scale[1] + cushion_scale[1]/2, 0), 
                               scale=cushion_scale,
                               color=(0.8, 0.6, 0.4))
        
        # Arms
        arm_scale = [0.2, 0.6, 1.2]
        for side in [-1, 1]:
            cls.create_sofa_part(f"Arm_{'Left' if side == -1 else 'Right'}", 
                               position=(side * (base_scale[0]/2 + arm_scale[0]/2), 
                                        arm_scale[1]/2, 
                                        0),
                               scale=arm_scale,
                               color=(0.3, 0.2, 0.1))
        
     
        # Backrest
        backrest_scale = [2.0, 0.8, 0.1]
        cls.create_sofa_part("Backrest", 
                           position=(0, 
                                    base_scale[1] + backrest_scale[1]/2, 
                                    base_scale[2]/2 + backrest_scale[2]/2),
                           scale=backrest_scale,
                           color=(0.3, 0.2, 0.1))

class CompanyHelloWorldExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        self.presets = {
            "Small Sofa": {"width": 1.8, "depth": 0.8, "height": 0.7},
            "Standard Sofa": {"width": 2.0, "depth": 1.0, "height": 0.8},
            "Sectional": {"width": 3.0, "depth": 1.2, "height": 0.9}
        }
        
        self._window = ui.Window("Sofa Customizer", width=300, height=350)
        with self._window.frame:
            with ui.VStack(spacing=10, height=0):
                # Preset Selection
                with ui.HStack(spacing=5):
                    self.preset_combobox = ui.ComboBox(
                        *list(self.presets.keys()), 
                        name="Select Preset",
                        width=180
                    ).model
                    ui.Button("Create Default", 
                            clicked_fn=self.create_default_sofa, 
                            width=100,
                            tooltip="Create default sofa configuration")
                
                # Parameters
                with ui.VStack(spacing=5):
                    self.width_field = self._create_parameter_field("Width", 2.0)
                    self.depth_field = self._create_parameter_field("Depth", 1.0)
                    self.height_field = self._create_parameter_field("Height", 0.8)
                
                # Customize Button
                ui.Button("Generate Sofa", 
                         clicked_fn=self.generate_custom_sofa, 
                         height=40,
                         style={"Button": {"background_color": 0xFF00FF00}})

    def _create_parameter_field(self, label, default):
        with ui.HStack():
            ui.Label(label, width=60)
            field = ui.FloatField().model
            field.set_value(default)
        return field

    def create_default_sofa(self):
        SofaCreator.create_default_sofa()
        print("Created default sofa with basic components")

    def generate_custom_sofa(self):
        # Implement parametric sofa generation based on field values
        width = self.width_field.get_value_as_float()
        depth = self.depth_field.get_value_as_float()
        height = self.height_field.get_value_as_float()
        print(f"Generating custom sofa - W: {width}, D: {depth}, H: {height}")
        # Add parametric generation logic here

    def on_shutdown(self):
        print("[company.sofa.creator] extension shutdown")