"""
Asset Manager Pipeline - Import Model
=======================================================

Docs referenced:
- IO functions:
  https://docs.unity.com/en-us/asset-transformer-sdk/2026.1/api/python/io_functions#importscene
"""

import os
import sys

import pxz
from pxz import core, scene, io

#Temporal directory to hold the Pixyz Scene so the following node in the pipeline can continue.
TEMP_PIXYZ_FILE_DIR = "/workspace/temp"
TEMP_FILE_NAME= "resume.pxz"
TEMP_FILE = os.path.join(TEMP_PIXYZ_FILE_DIR, TEMP_FILE_NAME)

def parse_pipeline_args(argv):
    """
    Parse arguments as invoked by an Asset Manager pipeline step.

    The pipeline runner builds the call as:
        script.py [ "input.ext" ]
    without quoting the brackets, so the shell splits it into argv tokens
    like:
        ['[', 'input.ext', ']']

    Strips any bare bracket/comma noise tokens rather than matching an
    exact argv shape, so it keeps working if the runner adds/drops
    trailing arguments. Falls back to a single plain argument for
    local/manual runs.
    """
    print("Checking arguments")
    cleaned = [arg.rstrip(",") for arg in argv if arg.strip(",") not in ("[", "]", "")]

    if len(cleaned) == 1:
        return cleaned[0]

    sys.exit(f"Unrecognized arguments: {argv}")


def initPixyz():
    # init Pixyz
    if pxz.get_current_session() == None:
        pxz.initialize()

    # print Pixyz version
    print(f'Pixyz version: {pxz.core.getVersion()}')

    # set log level to INFO so you can see the logs in the console
    pxz.core.configureInterfaceLogger(True, True, True)
    pxz.core.addConsoleVerbose(core.Verbose.INFO)

def saveTempPixyzFile():
    #Save model to a temp Pixyz File so it can be resumed in the next step
    os.makedirs(TEMP_PIXYZ_FILE_DIR, exist_ok=True)
    output_file = os.path.join(TEMP_PIXYZ_FILE_DIR, TEMP_FILE_NAME)
    print(f"Exporting: {TEMP_FILE}")
    io.exportScene(TEMP_FILE, scene.getRoot())

def importModel(FilePath):
    print (f"InputFile:{FilePath}")
    if not os.path.isfile(FilePath):
        sys.exit(f"Input file not found: {FilePath}")
       
    #Import model
    print(f"Importing: {FilePath}")
    io.importScene(FilePath)


def main():
    initPixyz()

    input_file = parse_pipeline_args(sys.argv[1:])
    importModel (input_file)
    
    saveTempPixyzFile()

    print("Import Process finished successfully.")
    pxz.release()


if __name__ == "__main__":
    main()

