# Copyright © 2024 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import math


# calculates the area of a triangle with usage of code
# from the below source, obtained under the GPL license
# https://github.com/amb/blender-scripts/blob/master/uv_area.py
def triangle_area(verts):
    # Heron's formula
    a = (verts[1][0] - verts[0][0]) ** 2.0 + (verts[1][1] - verts[0][1]) ** 2.0
    b = (verts[2][0] - verts[1][0]) ** 2.0 + (verts[2][1] - verts[1][1]) ** 2.0
    c = (verts[0][0] - verts[2][0]) ** 2.0 + (verts[0][1] - verts[2][1]) ** 2.0
    cal = (2 * a * b + 2 * b * c + 2 * c * a - a ** 2 - b ** 2 - c ** 2) / 16
    if cal < 0:
        cal = 0
    return math.sqrt(cal)


# calculates area of a quad with usage of code
# from the below source, obtained under the GPL license
# https://github.com/amb/blender-scripts/blob/master/uv_area.py
def quad_area(verts):
    return triangle_area(verts[:3]) + triangle_area(verts[2:] + [verts[0]])


# Calculates the area of an ngon. This will likely produce incorrect results on concave polygons
def ngon_area(verts):
    area = 0
    num_sides = len(verts)
    for i in range(num_sides - 2):
        area += triangle_area([verts[0], verts[i + 1], verts[i + 2]])
    return area


def register():
    pass


def unregister():
    pass
