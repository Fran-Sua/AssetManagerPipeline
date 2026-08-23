"""
Asset Manager Pipeline - Export Model
=======================================================

Docs referenced:
  https://docs.unity.com/en-us/asset-transformer-sdk/2026.1/api/python/
"""

import os
import sys

import pxz
from pxz import core, scene, io

#Temporal directory to hold the Pixyz Scene so the following node in the pipeline can continue.
TEMP_PIXYZ_FILE_DIR = "/workspace/temp"
TEMP_FILE_NAME= "resume.pxz"
TEMP_FILE = os.path.join(TEMP_PIXYZ_FILE_DIR, TEMP_FILE_NAME)

def parse_file_formats(raw):
    """
    The pipeline passes file formats as a single argv token that looks
    like a list, e.g. "[glb]" or "[glb, fbx]", but it arrives as a plain
    string. Strip the brackets and split on commas to get a real list.
    """
    cleaned = raw.strip().lstrip("[").rstrip("]")
    return [fmt.strip().strip('"').strip("'") for fmt in cleaned.split(",") if fmt.strip()]


def parse_pipeline_args(argv):

    print(f"Checking arguments: {argv}")
    if len(argv) == 3:
        return argv[0], argv[1], parse_file_formats(argv[2])

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
    print(f"Exporting: {TEMP_FILE}")
    io.exportScene(TEMP_FILE, scene.getRoot())

def importTemporalPixyzScene():
    output_file = os.path.join(TEMP_PIXYZ_FILE_DIR, TEMP_FILE_NAME)
    print (f"File:{TEMP_FILE}")
    if not os.path.isfile(TEMP_FILE):
        sys.exit(f"Input file not found: {TEMP_FILE}")
       
    #Import model
    print(f"Importing: {TEMP_FILE}")
    io.importScene(TEMP_FILE)

def exportFiles(output_dir, fileName, fileFormats):
    for fileFormat in fileFormats:
        output_name = fileName + "." + fileFormat
        output_file = os.path.join(output_dir, output_name)
        print(f"Exporting: {output_file}")
        io.exportScene(output_file, scene.getRoot())

    print("Done.")

    

def main():

    output_dir, fileName, fileFormats = parse_pipeline_args(sys.argv[1:])
    print (f"OutputDir: {output_dir}, fileName: {fileName}, FileFormats: {fileFormats}")
    initPixyz()
    importTemporalPixyzScene()
    exportFiles(output_dir, fileName, fileFormats)
    
    print("Export Process finished successfully.")
    pxz.release()


if __name__ == "__main__":
    main()

