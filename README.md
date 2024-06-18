cool script for manipulating xml files used for Teardown

features: scaling and flipping, but more will come

you will have to move the "models" folder into the same folder as the xml if you want them to show up sorry
```
usage: xmlhelper.py [-h] [-f {x,y,z}] [-s SCALE] [-m] [-d] filename

positional arguments:
  filename              filename of source xml

options:
  -h, --help            show this help message and exit
  -f {x,y,z}, --flip {x,y,z}
                        flip xml along chosen axis
  -s SCALE, --scale SCALE
                        scale xml by amount
  -m, --modify          modify existing file instead of creating a new one
  -d, --debug           replace voxes with debug gizmos
```
