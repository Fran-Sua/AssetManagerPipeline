"""
Pixyz SDK -- Remove Parts By Name
=======================================================

Selects occurrences by name and deletes them from the scene.

Usage parameters example:
--names=["PartA", "PartB", "PartC"]

Each entry in --names is matched against the built-in "Name" property of
occurrences in the scene. Every matching occurrence across all names is
collected and deleted together in one call to scene.deleteOccurrences.

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


def parse_remove_args(argv):
    """
    Parse the removal parameters as optional --name=value flags.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--names", type=parse_names, default=[])

    return parser.parse_args(argv)


def selectOccurrencesByNames(names):
    """
    Resolve which occurrences to delete by looking up each requested name
    against the built-in "Name" property.
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
    remove_args = parse_remove_args(sys.argv[1:])
    print(f"Remove args: {remove_args}")

    initPixyz()
    importTemporalPixyzScene()

    print("Arguments received:")
    for name, value in vars(remove_args).items():
        print(f"  {name} = {value}")

    if not remove_args.names:
        sys.exit("No names provided to remove. Use --names=[Name1, Name2, ...]")

    occurrences = selectOccurrencesByNames(remove_args.names)
    if not occurrences:
        sys.exit(f"No occurrences matched any of the requested names: {remove_args.names}")

    print(f"Removing {len(occurrences)} occurrence(s): {[o for o in occurrences]}")
    scene.deleteOccurrences(occurrences)

    saveTempPixyzFile()
    print("Remove Parts By Name finished successfully.")
    pxz.release()


if __name__ == "__main__":
    main()
