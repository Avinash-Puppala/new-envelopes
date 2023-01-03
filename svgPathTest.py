#px divided by 2.02 equals mm

# create svgpathtools Path objects from an SVG file
from svgpathtools import svg2paths
paths, attributes = svg2paths('Templates/PostCodes/Set1 - 8.svg')

# let's take the first path as an example
mypath = paths[0]

 # Let's find its length
print("length = ", mypath.length())

# Find height, width
xmin, xmax, ymin, ymax = mypath.bbox()
print("width = ", xmax - xmin)
print("height = ", ymax - ymin)

# Let's find the area enclosed by the path (assuming the path is closed)
try:
    print("area = ", mypath.area())
except AssertionError:
    print("This path is not closed!")
    # if you want a notion of area for an open path, 
    # you could use the bounding box area.
    print("height*width = ", (ymax - ymin)*(xmax - xmin))

