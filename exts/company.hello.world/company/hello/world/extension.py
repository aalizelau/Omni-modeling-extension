import omni.ext
import omni.ui as ui
import sys
sys.path.append("C:/Users/85291/Downloads/kit-exts-project/exts/company.hello.world/company/hello/world")
from sofa_generator import SofaCreator

sofa_creator = SofaCreator()

class CompanyHelloWorldExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        self._window = ui.Window("Sofa Customizer", width=300, height=500)
        self.sofas = []  # List to store created sofas' paths and parameters
        self.current_index = -1  # Index of the currently selected sofa
        self.current_sofa = None  # Reference to the currently selected sofa's data
        
        # Set up rebuildable UI frame
        self._window.frame.set_build_fn(self._build_ui)

    def _build_ui(self):
        """Rebuild the UI components dynamically"""
        with self._window.frame:
            with ui.VStack(spacing=10, height=0):
                self._build_sofa_list_section()

                # Create default sofa button
                ui.Button("Create Default Sofa", 
                    clicked_fn=self.create_default_sofa, 
                    height=40,
                    tooltip="Create default sofa configuration")
                
                self._build_parameter_section()
                
                # Customize button
                ui.Button("Customize Sofa", 
                         clicked_fn=self.customize_sofa, 
                         height=40,)

    def _build_sofa_list_section(self):
        with ui.VStack(spacing=5):
            if self.sofas:
                sofa_paths = [sofa["path"] for sofa in self.sofas]
                self.sofa_combobox = ui.ComboBox(
                    self.current_index, 
                    *sofa_paths, 
                    name="Sofa List"
                )
                self._combo_changed_sub = self.sofa_combobox.model.subscribe_item_changed_fn(
                    self._on_sofa_selected
                )
            else:
                ui.Label("No sofas available. Create a new sofa to begin.",
                    alignment=ui.Alignment.CENTER)

    def _build_parameter_section(self):
        with ui.VStack(spacing=5):
            self.width_field = self._create_parameter_field("Width", 2.0)
            self.depth_field = self._create_parameter_field("Depth", 1.0)
            self.cushion_height_field = self._create_parameter_field("Cushion Height", 0.15)
            self.base_height_field = self._create_parameter_field("Base Height", 0.2)
            self.arms_checkbox = self._create_checkbox("Include Arms", True)
            self.arm_height_field = self._create_parameter_field("Arm Height", 0.6)
            self.arm_width_field = self._create_parameter_field("Arm Width", 0.2)
            self.backrest_checkbox = self._create_checkbox("Include Backrest", True)
            self.backrest_depth_field = self._create_parameter_field("Backrest Depth", 0.1)
            self.backrest_height_field = self._create_parameter_field("Backrest Height", 0.8)

    def _create_parameter_field(self, label, default):  
        with ui.HStack():
            ui.Label(label, width=100)
            field = ui.FloatField().model
            field.set_value(default)
        return field

    def _create_checkbox(self, label, default):
        with ui.HStack():
            ui.Label(label, width=100)
            checkbox = ui.CheckBox().model
            checkbox.set_value(default)
        return checkbox

    def create_default_sofa(self):
        # Create and store new sofa
        sofa_root = sofa_creator.create_default_sofa()
        sofa_path = sofa_root.GetPath().pathString
        self._add_sofa(sofa_path, {
            "length": 2.0,
            "depth": 1.0,
            "cushion_height": 0.15,
            "base_height": 0.2,
            "arms": True,
            "arm_height": 0.6,
            "arm_width": 0.2,
            "backrest": True,
            "backrest_depth": 0.1,
            "backrest_height": 0.8
        })

    def _add_sofa(self, path, params):
        """Helper to add a new sofa and refresh UI"""
        self.sofas.append({"path": path, "params": params})
        self.current_index = len(self.sofas) - 1
        self.current_sofa = self.sofas[self.current_index]
        self._rebuild_ui()

    def _rebuild_ui(self):
        """Trigger UI refresh"""
        self._window.frame.rebuild()

    def _on_sofa_selected(self, item_model, item):
        """Handle sofa selection changes"""
        value_model = item_model.get_item_value_model(item)
        self.current_index = value_model.as_int
        if 0 <= self.current_index < len(self.sofas):
            self.current_sofa = self.sofas[value_model.as_int]
            self._load_sofa_parameters()


    def _load_sofa_parameters(self):
        """Load the parameters of the selected sofa into the UI fields."""
        if self.current_sofa is None:
            return
        params = self.current_sofa["params"]
        self.width_field.set_value(params["length"])
        self.depth_field.set_value(params["depth"])
        self.cushion_height_field.set_value(params["cushion_height"])
        self.base_height_field.set_value(params["base_height"])
        self.arms_checkbox.set_value(params["arms"])
        self.arm_height_field.set_value(params["arm_height"])
        self.arm_width_field.set_value(params["arm_width"])
        self.backrest_checkbox.set_value(params["backrest"])
        self.backrest_depth_field.set_value(params["backrest_depth"])
        self.backrest_height_field.set_value(params["backrest_height"])

    def customize_sofa(self):
        """Replace sofas with new parameters."""
        width = self.width_field.get_value_as_float()
        depth = self.depth_field.get_value_as_float()
        cushion_height = self.cushion_height_field.get_value_as_float()
        base_height = self.base_height_field.get_value_as_float()
        arms = self.arms_checkbox.get_value_as_bool()
        arm_height = self.arm_height_field.get_value_as_float()
        arm_width = self.arm_width_field.get_value_as_float()
        backrest = self.backrest_checkbox.get_value_as_bool()
        backrest_depth = self.backrest_depth_field.get_value_as_float()
        backrest_height = self.backrest_height_field.get_value_as_float()

        # Create the custom sofa
        sofa_root = SofaCreator.customize_sofa(
            length=width, 
            depth=depth, 
            cushion_height=cushion_height, 
            base_height=base_height, 
            arms=arms, 
            arm_height=arm_height, 
            arm_width=arm_width, 
            backrest=backrest, 
            backrest_depth=backrest_depth, 
            backrest_height=backrest_height
        )
        sofa_path = sofa_root.GetPath().pathString
        params = {
            "length": width,
            "depth": depth,
            "cushion_height": cushion_height,
            "base_height": base_height,
            "arms": arms,
            "arm_height": arm_height,
            "arm_width": arm_width,
            "backrest": backrest,
            "backrest_depth": backrest_depth,
            "backrest_height": backrest_height
        }
        # self.sofas.append({"path": sofa_path, "params": params})
        # self.current_index = len(self.sofas) - 1
        # self.current_sofa = self.sofas[self.current_index]
        self._load_sofa_parameters()

    def on_shutdown(self):
        print("[company.sofa.creator] extension shutdown")