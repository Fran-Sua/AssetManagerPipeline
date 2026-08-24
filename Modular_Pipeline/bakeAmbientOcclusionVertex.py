"""
Pixyz SDK -- Bake Ambient Occlusion (to vertices)
=======================================================

Bakes ambient occlusion for the entire scene and stores the result as
per-vertex colors (no textures/UVs involved), using Pixyz's vertex baking
session workflow:
    algo.beginVertexBakingSession -> algo.bakeAOMap -> algo.endBakingSession
followed by an optional algo.filterMeshVertexColors smoothing pass.

Usage parameters example:
--samples=32
--samples=64 --bentNormals=True
--applyFilter=False

samples must be a power of two in [8, 4096].

Verified against Pixyz SDK v2026.3.x (rebranded "Unity Asset Transformer SDK").
The `pxz` Python module and the function names below are unchanged from the
Pixyz-branded SDK, so this runs fine under the 2026.3.1.1 build.

Docs referenced:
  https://docs.unity.com/en-us/asset-transformer-sdk/2026.1/manual/functions/bakeao
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


def parse_bake_ao_args(argv):
    """
    Parse the ambient occlusion baking parameters as optional --name=value
    flags, falling back to their default when omitted.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--samples", type=int, default=32) #power of two in [8, 4096]
    parser.add_argument("--bentNormals", type=str2bool, default=False)
    parser.add_argument("--applyFilter", type=str2bool, default=True) #smooth the resulting vertex colors
    parser.add_argument("--sigmaPos", type=float, default=5.0)
    parser.add_argument("--sigmaValue", type=float, default=0.2)
    parser.add_argument("--sigmaNormal", type=float, default=15.0)

    return parser.parse_args(argv)


def bakeAmbientOcclusionToVertices(samples, bentNormals, applyFilter, sigmaPos, sigmaValue, sigmaNormal):
    """
    Bake ambient occlusion for the whole scene onto vertex colors. The
    scene root is used as both destination and source, so the entire
    scene occludes itself.
    """
    root = scene.getRoot()

    sessionId = algo.beginVertexBakingSession([root], [root])
    algo.bakeAOMap(sessionId, samples=samples, bentNormals=bentNormals)
    algo.endBakingSession(sessionId)

    if applyFilter:
        meshes = scene.getPartOccurrences(root)
        algo.filterMeshVertexColors(meshes, sigmaPos=sigmaPos, sigmaValue=sigmaValue, sigmaNormal=sigmaNormal)


def main():
    bake_args = parse_bake_ao_args(sys.argv[1:])
    print(f"Bake AO args: {bake_args}")

    initPixyz()
    importTemporalPixyzScene()

    print("Arguments received:")
    for name, value in vars(bake_args).items():
        print(f"  {name} = {value}")

    bakeAmbientOcclusionToVertices(
        samples=bake_args.samples,
        bentNormals=bake_args.bentNormals,
        applyFilter=bake_args.applyFilter,
        sigmaPos=bake_args.sigmaPos,
        sigmaValue=bake_args.sigmaValue,
        sigmaNormal=bake_args.sigmaNormal,
    )

    saveTempPixyzFile()
    print("Bake Ambient Occlusion finished successfully.")
    pxz.release()


if __name__ == "__main__":
    main()
