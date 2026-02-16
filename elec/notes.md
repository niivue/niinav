python elc2json.py standard_1005.tsv standard_1005.jcon --xmin -100 --xmax 0  --ymin -100 --ymax 100  --zmin -100 --zmax 100


Original source for electrode positions:
https://github.com/mne-tools/mne-python/blob/main/mne/channels/data/montages/standard_1005.elc

https://github.com/sccn/dipfit/blob/b0b660e7efca0a9b68a4afb4e1749042e327b90c/standard_BEM/elec/standard_1005.elc#L4


The file standard_1005.elc contains electrode positions defined for the 10-05 system, a very high-density extension of the original standard with many sites.

Prompt: Help me write a Python script to convert my tsv file to json. The basic structure should be
 elc2json.py <input.tsv> <output.json> [options]
For example:
 python elc2json.py standard_1005.tsv elc.json --xmin -100 --xmax 0  --ymin -100 --ymax 100  --zmin -100 --zmax 100

  

The options should allow me to filter output to only include electrodes within a range of coordinates. The input file contains the eletrode name in the first column, followed by the X,Y,Z positions:

Labels	X	Y	Z
LPA	-86.0761	-19.9897	-47.986
RPA	85.7939	-20.0093	-48.031
Nz	0.0083	86.811	-39.983
Fp1	-29.4367	83.9171	-6.99

The ouput should provide each filtered electrode location as a node (ideally, copy the boilerplate, you can put the input filename as the `name`), and set the color and size to 1 for all nodes:

{
	"name": "standard_1005",
	"nodeColormap": "nih",
	"nodeMinColor": 1,
	"nodeMaxColor": 2,
	"nodeScale": 1,
	"legendLineThickness": 0,
	"nodes": [
  {
    "name": "TP7",
    "x": -84.8302,
    "y": -46.0217,
    "z": -7.056,
    "colorValue": 1,
    "sizeValue": 1
  },
  {
    "name": "CP5",
    "x": -79.5922,
    "y": -46.5507,
    "z": 30.949,
    "colorValue": 1,
    "sizeValue": 1
  },
...
}
