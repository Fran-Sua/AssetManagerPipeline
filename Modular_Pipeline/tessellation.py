"""
Pixyz SDK -- Tessellate
=======================================================

Usage parameters example:
Tesellate the entire scene: --maxSag=0.2 --maxLength=-1 --maxAngle=-1 --createNormals=True --uvMode=0 --uvChannel=1 --uvPadding=0.0 --createTangents=False --createFreeEdges=False --keepBRepShape=True --overrideExistingTessellation=False
All the values are defaulted in the scrip, so it is also possible to call the script without parameters and it will tessellate the full scene

Tessellate by name: This will perform a search in the scene by name, and only tessallate the occurrances that matches
--selectBy=name --selectValue=NameOfOccurance --maxSag=0.2 --maxLength=-1 --maxAngle=-1 --createNormals=True --uvMode=0 --uvChannel=1 --uvPadding=0.0 --createTangents=False --createFreeEdges=False --keepBRepShape=True --overrideExistingTessellation=False

Tessellate by Metadata: This will perform a search in the scene by metadata, and only tessallate the occurrances that matches
--selectBy=metadata --selectValue=metadataValue --selectKey=keyName --maxSag=0.2 --maxLength=-1 --maxAngle=-1 --createNormals=True --uvMode=0 --uvChannel=1 --uvPadding=0.0 --createTangents=False --createFreeEdges=False --keepBRepShape=True --overrideExistingTessellation=False

Verified against Pixyz SDK v2026.3.x (rebranded "Unity Asset Transformer SDK").
The `pxz` Python module and the function names below are unchanged from the
Pixyz-branded SDK, so this runs fine under the 2026.3.1.1 build.

Docs referenced:
  https://docs.unity.com/en-us/asset-transformer-sdk/2026.1/api/python/
"""

import argparse
import os
import sys

import pxz
from pxz import core, scene, io, algo

#Temporal directory to hold the Pixyz Scene so the following node in the pipeline can continue.
TEMP_PIXYZ_FILE_DIR = "/workspace/temp"
TEMP_FILE_NAME= "resume.pxz"
TEMP_FILE = os.path.join(TEMP_PIXYZ_FILE_DIR, TEMP_FILE_NAME)

def initPixyz():
    # init Pixyz
    if pxz.get_current_session() == None:
        pxz.initialize()

    # print Pixyz version
    print(f'Pixyz version: {pxz.core.getVersion()}')

    # set log level to INFO so you can see the logs in the console
    pxz.core.configureInterfaceLogger(True, True, True)
    pxz.core.addConsoleVerbose(core.Verbose.INFO)

def importTemporalPixyzScene():
    output_file = os.path.join(TEMP_PIXYZ_FILE_DIR, TEMP_FILE_NAME)
    print (f"File:{TEMP_FILE}")
    if not os.path.isfile(TEMP_FILE):
        sys.exit(f"Input file not found: {TEMP_FILE}")

    #Import model
    print(f"Importing: {TEMP_FILE}")
    io.importScene(TEMP_FILE)

def saveTempPixyzFile():
    #Save model to a temp Pixyz File so it can be resumed in the next step
    os.makedirs(TEMP_PIXYZ_FILE_DIR, exist_ok=True)
    output_file = os.path.join(TEMP_PIXYZ_FILE_DIR, TEMP_FILE_NAME)
    print(f"Exporting: {TEMP_FILE}")
    io.exportScene(TEMP_FILE, scene.getRoot())


def str2bool(value):
    """argparse type= helper: bool("False") is True in plain Python, so
    boolean flags need explicit string parsing instead."""
    if isinstance(value, bool):
        return value
    if value.lower() in ("true", "1", "yes"):
        return True
    if value.lower() in ("false", "0", "no"):
        return False
    raise argparse.ArgumentTypeError(f"Expected a boolean value, got: {value}")


def parse_tessellation_args(argv):
    """
    Parse the tessellation parameters as optional --name=value flags,
    falling back to their default when omitted.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--selectBy", default="") #possible values: name, metadata
    parser.add_argument("--selectValue", default="") 
    parser.add_argument("--selectKey", default="") #only necesary for Metadata selection
    parser.add_argument("--maxSag", type=float, default=0.2)
    parser.add_argument("--maxLength", type=float, default=-1)
    parser.add_argument("--maxAngle", type=float, default=-1)
    parser.add_argument("--createNormals", type=str2bool, default=True)
    parser.add_argument("--uvMode", type=int, default=0)
    parser.add_argument("--uvChannel", type=int, default=1)
    parser.add_argument("--uvPadding", type=float, default=0.0)
    parser.add_argument("--createTangents", type=str2bool, default=False)
    parser.add_argument("--createFreeEdges", type=str2bool, default=False)
    parser.add_argument("--keepBRepShape", type=str2bool, default=True)
    parser.add_argument("--overrideExistingTessellation", type=str2bool, default=False)

    return parser.parse_args(argv)


def selectOccurrences(selectBy, selectValue, selectKey=""):
    """
    Resolve which occurrences the tessellation should run on.

    selectBy="Name": occurrences whose built-in "Name" property matches
        the selectValue regex (see scene.findOccurrencesByProperty).
    selectBy="Metadata": occurrences whose selectKey metadata property
        matches the selectValue regex (see scene.findOccurrencesByMetadata).
    """
    selectBy = selectBy.strip().lower()

    if selectBy == "name":
        occurrences = list(scene.findOccurrencesByProperty("Name", selectValue))
    elif selectBy == "metadata":
        if not selectKey:
            sys.exit("selectKey is required when selectBy=Metadata")
        occurrences = list(scene.findOccurrencesByMetadata(selectKey, selectValue))
    elif selectBy == "":
        #if no value is provided, select the scene root
        occurrences = [scene.getRoot()]
        
    else:
        sys.exit(f"Unsupported selectBy value: {selectBy}")

    if not occurrences:
        print(f"No occurrences matched selectBy={selectBy}, selectValue={selectValue}, selectKey={selectKey}")

    return occurrences


def main():
    tess_args = parse_tessellation_args(sys.argv[1:])
    print (f"Tessellation args: {tess_args}")

    initPixyz()
    importTemporalPixyzScene()

    print ("Arguments received:")
    for name, value in vars(tess_args).items():
        print(f"  {name} = {value}")

    # select the target occurrences and apply tessellation using the parsed (or default) parameters
    occurrences = selectOccurrences(tess_args.selectBy, tess_args.selectValue, tess_args.selectKey)
    algo.tessellate(
        occurrences,
        maxSag=tess_args.maxSag,
        maxLength=tess_args.maxLength,
        maxAngle=tess_args.maxAngle,
        createNormals=tess_args.createNormals,
        uvMode=tess_args.uvMode,
        uvChannel=tess_args.uvChannel,
        uvPadding=tess_args.uvPadding,
        createTangents=tess_args.createTangents,
        createFreeEdges=tess_args.createFreeEdges,
        keepBRepShape=tess_args.keepBRepShape,
        overrideExistingTessellation=tess_args.overrideExistingTessellation,
    )


    saveTempPixyzFile()
    print("Tessallation finished successfully.")
    pxz.release()
    


if __name__ == "__main__":
    main()

