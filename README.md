# Rush Hour Unreal Vehicle Toolkit

This Blender addon makes it a breeze to prepare vehicles for use in Unreal Engine. It's been designed with the [Rush Hour - Vehicle Animator](https://www.gdcorner.com/products/RushHour.html) plugin in mind, however it should be very useful for anyone who wants to get a car into Unreal, even without Rush Hour.

[Rush Hour is available for purchase on the Unreal Engine Marketplace here.](https://www.unrealengine.com/marketplace/en-US/product/rush-hour-vehicle-animator)

[You can find out more about Rush Hour and documentation at the website here.](https://www.gdcorner.com/products/RushHour.html)

[Addon Documentation](https://www.gdcorner.com/documentation/rushhour/10-preparingavehicle.html)

### Blender Versions

This addon is only tested against the active LTS versions of Blender. Other versions may work, but are unsupported. 

- 4.2 LTS
- 4.5 LTS
- 5.2 LTS

## Validating & Packaging

This addon follows the [Blender Extensions](https://docs.blender.org/manual/en/latest/advanced/extensions/getting_started.html) format. The manifest (`blender_manifest.toml`) contains all required metadata and build configuration.

### Validate

To validate the manifest without building the package:

```bash
blender --command extension validate
```

To validate a built `.zip` package:

```bash
blender --command extension validate gdcorner_rush_hour_vehicle_toolkit-1.6.2.zip
```

### Build

To build the extension `.zip` package from the addon directory:

```bash
blender --command extension build
```

This produces `gdcorner_rush_hour_vehicle_toolkit-1.6.2.zip` (version may vary), ready for installation or publishing to the [Blender Extensions Platform](https://extensions.blender.org).

## License

The Rush Hour Unreal Vehicle Toolkit Blender addon is licensed under the MIT license. For full details please read the LICENSE file.

Any files output by this plugin (including Blend, FBX and JSON files) are fully owned by you.

[Rush Hour - Vehicle Animator](https://www.unrealengine.com/marketplace/en-US/product/rush-hour-vehicle-animator) available from the Unreal Engine Marketplace is licensed separately under the [Epic Content License Agreement](https://www.unrealengine.com/en-US/eula/content) as a Code Plugin.
