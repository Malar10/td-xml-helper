import xml.etree.ElementTree as ET

filename = "leveraction copy.xml"
scale = 3

def scale_children(root: ET.Element):
    for child in root.findall("*"):
        if "pos" in child.attrib:
            pos = child.attrib["pos"].split(" ")
            pos = [str(float(v) * scale) for v in pos]

            #print(" ".join(pos))
            child.set("pos", " ".join(pos))

        if "scale" in child.attrib:
            child.set("scale", str(float(child.attrib["scale"]) * scale))

        scale_children(child)

tree = ET.parse(filename)
scale_children(tree.getroot())

tree.write(filename)