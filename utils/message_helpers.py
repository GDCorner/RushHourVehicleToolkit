# Copyright © 2024-2026 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bpy


def show_warning_message(message="", title="Scene Scale", icon='ERROR'):
    print(f"{title} (warning): {message}")

    # popup_menu requires a window, which doesn't exist in background mode
    if bpy.app.background:
        return

    def draw(self, context):
        lines = message.split('\n')
        for line in lines:
            self.layout.label(text=line)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


def show_info_message(message="", title="Scene Scale", icon='INFO'):
    print(f"{title} (info): {message}")

    # popup_menu requires a window, which doesn't exist in background mode
    if bpy.app.background:
        return

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)
