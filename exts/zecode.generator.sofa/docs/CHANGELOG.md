# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).


## [1.0.0] - 2025-02-12

### Added
- **Sofa Geometry Generation:**  
  - Implemented the `SofaCreator` class to generate sofa parts (base, legs, cushions, arms, backrest) by referencing an external USD file.
  - Added support for applying translation and scaling transforms to each sofa component.

- **Material Binding:**  
  - Integrated MDL material binding using OmniKit commands to assign a fabric material (Fabric_Cotton_Fine_Woven) to sofa parts.
  
- **Customization Capabilities:**  
  - Enabled creation of a default sofa with preset parameters.
  - Implemented a method to customize an existing sofa, allowing dynamic updates to dimensions and features.

- **User Interface Extension:**  
  - Developed a UI extension ("Sofa Customizer") using omni.ui for interactive sofa creation and parameter customization.
  - Added UI elements such as parameter fields and checkboxes to control sofa dimensions and options (e.g., width, number of cushions, arms, backrest).

- **Integration with Omniverse:**  
  - Leveraged Omniverse USD APIs and OmniKit commands for seamless integration within the Omniverse environment.
