# Copyright © 2023 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import textwrap
import bpy


def label_multiline(context: bpy.types.Context, text: str, parent: bpy.types.UILayout):
    """ Automatically wrap text to fit in the panel """
    # https://b3d.interplanety.org/en/multiline-text-in-blender-interface-panels/
    chars = int(context.region.width / 7)  # 7 pix on 1 character
    wrapper = textwrap.TextWrapper(width=chars)
    text_lines = wrapper.wrap(text=text)
    for text_line in text_lines:
        parent.label(text=text_line)


def register():
    pass


def unregister():
    pass
