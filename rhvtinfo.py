# Copyright © 2024 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bpy
import logging

log = logging.getLogger(__name__)

if 'addon_bl_info' in globals():
    pass
    # addon_bl_info exists as it's been set by the main module
else:
    # Only set this to none if it doesn't already exist
    addon_bl_info = {"version": (0, 0, 0)}

_b_is_supported_blender_version = False
_b_has_checked_blender_version = False


def _check_blender_version(current_blender_version):
    global _b_has_checked_blender_version
    global _b_is_supported_blender_version
    log.info(f"Checking Blender Version Compatibility with Rush Hour Vehicle Toolkit")
    log.info(f"Blender version: {current_blender_version}")
    log.info(f"Rush Hour Addon version: {addon_bl_info['version']}")
    # maximum supported blender version
    supported_blender_versions = addon_bl_info.get("supported_blender_versions", [(3, 6, 0), (4, 2, 0), (4, 5, 0)])
    if "blender" in addon_bl_info:
        _b_has_checked_blender_version = True
    else:
        # Not the real version, just a placeholder, so don't mark as checked
        log.warning("No Blender version specified in addon_bl_info for Rush Hour Vehicle Toolkit")
        log.warning(addon_bl_info)
        _b_has_checked_blender_version = False

    log.info(f"Checking Blender version: {current_blender_version}")
    log.info(f"Supported Blender versions: {supported_blender_versions}")

    current_blender_version_major_minor = current_blender_version[:2]
    for compatible_version in supported_blender_versions:
        comp_blender_version_major_minor = compatible_version[:2]
        if current_blender_version_major_minor == comp_blender_version_major_minor:
            log.info(f"Blender version is supported, current: {current_blender_version_major_minor} compatible version: {comp_blender_version_major_minor}")
            _b_is_supported_blender_version = True
            return _b_is_supported_blender_version

    # If we got here, the version is not supported
    _b_is_supported_blender_version = False
    return _b_is_supported_blender_version


def is_supported_blender_version():
    if not _b_has_checked_blender_version:
        _check_blender_version(bpy.app.version)
    return _b_is_supported_blender_version


def test_blender_versions_check():
    logging.basicConfig(level=logging.DEBUG)
    log.info("Testing Blender version check")
    versions = {
        (3, 3, 200): False,
        (3, 3, 0): False,
        (3, 4, 0): False,
        (3, 5, 0): False,
        (3, 6, 0): True,
        (3, 6, 12): True,
        (4, 0, 0): False,
        (4, 1, 0): False,
        (4, 2, 0): True,
        (4, 2, 19): True,
        (4, 3, 0): False,
        (4, 4, 0): False,
    }

    b_any_failed = False

    log.info(f"Running tests on {len(versions)} versions")

    for version, expected_result in versions.items():
        log.info(f"Testing version: {version}, expected result: {expected_result}")
        actual_result = _check_blender_version(version)
        if actual_result != expected_result:
            log.error(f"Test failed for version: {version}, expcted: {expected_result}, actual: {actual_result}")
            b_any_failed = True
        else:
            log.info(f"Test passed for version: {version}")

    if b_any_failed:
        log.error("Some tests failed")
    else:
        log.info("All tests passed")


if __name__ == "__main__":
    print("This is the main module")
    test_blender_versions_check()
