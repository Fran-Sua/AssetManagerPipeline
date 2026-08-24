"""
Pixyz SDK -- Make Materials Metallic
=======================================================

Turns every material in the scene metallic: sets the metallic and
roughness coefficients while leaving the base color (albedo) untouched.
Materials coming from CAD sources are often not PBR yet, so any material
that isn't already PBR is converted first (metallic/roughness only exist
on the PBR pattern).

Usage parameters example:
Fully metallic, 0.5 roughness (the defaults):
--metallic=1.0 --roughness=0.5

Verified against Pixyz SDK v2026.3.x (rebranded "Unity Asset Transformer SDK").
The `pxz` Python module and the function names below are unchanged from the
Pixyz-branded SDK, so this runs fine under the 2026.3.1.1 build.

Docs referenced:
  https://docs.unity.com/en-us/asset-transformer-sdk/2026.1/manual/scene/material
  https://docs.unity.com/en-us/asset-transformer-sdk/2026.1/api/python/
"""

import argparse
import os
import sys

import pxz
from pxz import core, scene, io, material

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


def parse_metallic_args(argv):
    """
    Parse the metallic/roughness parameters as optional --name=value flags.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--metallic", type=float, default=1.0)
    parser.add_argument("--roughness", type=float, default=0.5)

    return parser.parse_args(argv)


def ensurePBRMaterials(root):
    """
    Convert every material used under root to the PBR pattern, skipping
    materials that already are PBR. Returns the full material list (both
    the ones already PBR and the newly converted ones).
    """
    materials = scene.getMaterialsFromSubtree(root)
    nonPbrMaterials = [mat for mat in materials if material.getMaterialPattern(mat) != "PBR"]

    if nonPbrMaterials:
        print(f"Converting {len(nonPbrMaterials)} material(s) to PBR")
        scene.convertMaterialsToPBR(nonPbrMaterials)

    return materials


def makeMaterialsMetallic(metallic, roughness):
    """
    Set metallic and roughness on every material in the scene, leaving
    albedo (base color) untouched.
    """
    materials = ensurePBRMaterials(scene.getRoot())

    for mat in materials:
        core.setProperty(mat, "metallic", f"COEFF({metallic})")
        core.setProperty(mat, "roughness", f"COEFF({roughness})")


def main():
    metallic_args = parse_metallic_args(sys.argv[1:])
    print(f"Metallic args: {metallic_args}")

    initPixyz()
    importTemporalPixyzScene()

    print("Arguments received:")
    for name, value in vars(metallic_args).items():
        print(f"  {name} = {value}")

    makeMaterialsMetallic(metallic_args.metallic, metallic_args.roughness)

    saveTempPixyzFile()
    print("Make Materials Metallic finished successfully.")
    pxz.release()


if __name__ == "__main__":
    main()
