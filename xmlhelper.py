#cool script for manipulating xml files used for Teardown 
#by malario

import xml.etree.ElementTree as ET
import numpy as np
from scipy.spatial.transform import Rotation as spr
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("filename", help="filename of source xml")
parser.add_argument("-f", "--flip", help="flip xml along chosen axis", choices=["x", "y", "z"])
parser.add_argument("-s", "--scale", help="scale xml by amount", type=float)
parser.add_argument("-m", "--modify", help="modify existing file instead of creating a new one", action="store_true")
parser.add_argument("-d", "--debug", help="replace voxes with debug gizmos", action="store_true")
args = parser.parse_args()

#print(args)
if not args.flip and not args.scale:
    print("need pick at least 1 function (--help for a full list)")
    exit()

filename = args.filename[:-4]

debuggizmos = args.debug

class transform:
    def __init__(self, pos:list = None, rot = None):
        
        if pos is None:
            pos = [0, 0, 0]

        if rot is None:
            rot = [0, 0, 0]

        self.pos = np.array(pos)

        if type(rot) == list:
            self.rot = spr.from_euler("xzy", [rot[0], rot[2], rot[1]], degrees=True)
        elif type(rot) == spr:
            self.rot = rot

    def getEulerStrings(self):
        angles = self.rot.as_euler("xzy", degrees=True)
        return [angles[0], angles[2], angles[1]]
    
    def stringified(self, divideBy10:bool):
        angles = self.rot.as_euler("xzy", degrees=True)
        angles = self.rot.as_euler("xzy", degrees=True)
        r = [str(round(x, 1)) for x in angles]
        
        if divideBy10:
            p = [str(round(x/10, 2)) for x in self.pos]
        else:
            p = [str(round(x, 2)) for x in self.pos]

        return [" ".join(p), " ".join([r[0], r[2], r[1]])]

    def __str__(self) -> str:
        angles = self.rot.as_euler("xzy", degrees=True)
        r = [round(x, 1) for x in angles]
        p = [round(x, 2) for x in self.pos]
        return str(p) + ", " + str([r[0], r[2], r[1]])

def transformToParentTransform(parent:transform, child:transform):
    pos = parent.rot.apply(child.pos) + parent.pos
    rot = parent.rot * child.rot
    return transform(pos, rot)

def transformToLocalTransform(parent:transform, child: transform):
    pos = parent.rot.apply(child.pos - parent.pos, inverse=True) 
    rot = parent.rot.inv() * child.rot
    return transform(pos, rot)

def rotateTransform(trans:transform, rotation: spr):
    newRot = rotation * trans.rot
    return transform(trans.pos, newRot)

def flip_stuff(root: ET.Element, parent_global_trans: transform, parent_new_global_trans: transform):
    for child in root.findall("*"):
        #if child.tag == "body" or child.tag == "group":
        #print()
        #if "name" in child.attrib:
        #    print(child.attrib["name"])
        #if "tags" in child.attrib:
        #    print(child.attrib["tags"])
        pos = None
        if "pos" in child.attrib:
            try:
                pos = child.attrib["pos"].split(" ")
                pos = [float(v) for v in pos]
                if child.tag == "body":
                    pos = [v*10 for v in pos]
            except:
                pos = None
        rot = None
        if "rot" in child.attrib: 
            try:
                rot = child.attrib["rot"].split(" ")
                rot = [float(v) for v in rot]
            except:
                rot = None
        local_trans = transform(pos, rot)
        global_trans = transformToParentTransform(parent_global_trans, local_trans)
        
        p = global_trans.pos
        r = global_trans.rot.as_euler("xzy", degrees=True)
        if axis == "x":
            p = [-p[0], p[1], p[2]]
            r = [r[0], -r[2], -r[1]]
        elif axis == "y":
            p = [p[0], -p[1], p[2]]
            r = [-r[0], r[2], -r[1]]
        elif axis == "z":
            p = [p[0], p[1], -p[2]]
            r = [-r[0], -r[2], r[1]]
        flipped_global_trans = transform(p, r)
        rotated_local_trans = transformToLocalTransform(parent_new_global_trans, flipped_global_trans)
        stringTrans = rotated_local_trans.stringified(child.tag == "body")
        child.set("pos", stringTrans[0])
        child.set("rot", stringTrans[1])
        flip_stuff(child, global_trans, flipped_global_trans)

def scale_children(root: ET.Element, scale: float):
    for child in root.findall("*"):
        if "pos" in child.attrib:
            pos = child.attrib["pos"].split(" ")
            pos = [str(float(v) * scale) for v in pos]

            #print(" ".join(pos))
            child.set("pos", " ".join(pos))

        if child.tag == "vox":
            curr_scale = 1
            if "scale" in child.attrib:
                curr_scale = float(child.attrib["scale"])

            child.set("scale", str(curr_scale * scale))

        scale_children(child, scale)

def change_paths(root: ET.Element, new_path: str):
    for child in root.findall("*"):
        if child.tag == "vox":
            child.set("file", new_path)
            child.set("object", "")
        change_paths(child, new_path)

tree = ET.parse(filename+".xml")

if args.flip:
    axis = args.flip
    flip_stuff(tree.getroot().find("*"), transform(), transform())

if args.scale:
    scale = args.scale
    scale_children(tree.getroot().find("*"), scale)

if args.debug:
    path = "MOD/models/gizmo-flipped-"+axis+".vox"
    change_paths(tree.getroot().find("*"), path)

if args.modify:
    tree.write(filename+".xml")
else:
    tree.write(filename+"-edited.xml")