"""
Pixyz SDK -- Merge Parts
=======================================================

Selects occurrences by name and merges them into a single part.

Usage parameters example:
--names=["PartA", "PartB", "PartC"] --mergeHiddenPartsMode=0

Each entry in --names is matched against the built-in "Name" property of
occurrences in the scene (exact match). Every matching occurrence across
all names is collected and merged together in one call to
scene.mergePartOccurrences.

mergeHiddenPartsMode controls how hidden parts among the selection are
handled: 0=Destroy, 1=MakeVisible, 2=MergeSeparately (default).

Verified against Pixyz SDK v2026.3.x (rebranded "Unity Asset Transformer SDK").
The `pxz` Python module and the function names below are unchanged from the
Pixyz-branded SDK, so this runs fine under the 2026.3.1.1 build.

Docs referenced:
  https://docs.unity.com/en-us/asset-transformer-sdk/2026.1/api/python/
"""

import argparse
import os
import re
import sys

import pxz
from pxz import core, scene, io

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
    print(f"Exporting: {TEMP_FILE}")
    io.exportScene(TEMP_FILE, scene.getRoot())


def parse_names(raw):
    """
    The pipeline passes lists as a single argv token that looks like
    "[PartA, PartB, PartC]", but it arrives as a plain string. Strip the
    brackets and split on commas to get the real list of names.
    """
    cleaned = raw.strip().lstrip("[").rstrip("]")
    return [name.strip().strip('"').strip("'") for name in cleaned.split(",") if name.strip()]


def parse_merge_args(argv):
    """
    Parse the merge parameters as optional --name=value flags.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--names", type=parse_names, default=[])
    parser.add_argument("--mergeHiddenPartsMode", type=int, default=2) #0=Destroy, 1=MakeVisible, 2=MergeSeparately

    return parser.parse_args(argv)


def selectOccurrencesByNames(names):
    """
    Resolve which occurrences to merge by looking up each requested name
    against the built-in "Name" property (exact match, so names containing
    regex-special characters are handled correctly).
    """
    occurrences = []
    seen = set()

    for name in names:
        matches = list(scene.findOccurrencesByProperty("Name", name))
        if not matches:
            print(f"No occurrences matched name={name}")
            continue
        for occurrence in matches:
            if occurrence not in seen:
                seen.add(occurrence)
                occurrences.append(occurrence)

    return occurrences


def main():
    merge_args = parse_merge_args(sys.argv[1:])
    print(f"Merge args: {merge_args}")

    initPixyz()
    importTemporalPixyzScene()

    print("Arguments received:")
    for name, value in vars(merge_args).items():
        print(f"  {name} = {value}")

    if not merge_args.names:
        sys.exit("No names provided to merge. Use --names=[Name1, Name2, ...]")

    occurrences = selectOccurrencesByNames(merge_args.names)
    if not occurrences:
        sys.exit(f"No occurrences matched any of the requested names: {merge_args.names}")

    print(f"Merging {len(occurrences)} occurrence(s): {[o for o in occurrences]}")
    scene.mergePartOccurrences(occurrences, mergeHiddenPartsMode=merge_args.mergeHiddenPartsMode)

    saveTempPixyzFile()
    print("Merge Parts finished successfully.")
    pxz.release()


if __name__ == "__main__":
    main()
