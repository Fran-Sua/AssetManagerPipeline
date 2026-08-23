"""
Pixyz SDK -- Bake Ambient Occlusion (to textures)
=======================================================

Bakes ambient occlusion for the entire scene into texture maps (as opposed
to per-vertex colors -- see Bake_Ambient_Occlusion_Vertex.py) and assigns
the resulting maps to each part's material "ao" channel. Materials that
aren't PBR yet are converted first, since PBR is the material pattern that
exposes an ao channel to write into.

Pipeline used:
    scene.convertMaterialsToPBR (only on non-PBR materials)
    algo.beginBakingSession -> algo.bakeAOMap -> algo.endBakingSession
    optional material.filterAO smoothing pass
    material.getPBRMaterialInfos / setPBRMaterialInfos to wire the baked
        image into each part's active material as its ao texture

This step requires the geometry to already have UV coordinates on
uvChannel (e.g. produced by a prior Tessellation.py step) -- texture
baking, unlike vertex baking, projects onto UV space.

Usage parameters example:
--resolution=1024 --uvChannel=1 --samples=32
--resolution=2048 --samples=64 --bentNormals=True
--applyFilter=False

samples must be a power of two in [8, 4096].

Verified against Pixyz SDK v2026.3.x (rebranded "Unity Asset Transformer SDK").
The `pxz` Python module and the function names below are unchanged from the
Pixyz-branded SDK, so this runs fine under the 2026.3.1.1 build.

Docs referenced:
  https://docs.unity.com/en-us/asset-transformer-sdk/2026.1/manual/functions/bakeao
  https://docs.unity.com/en-us/asset-transformer-sdk/2026.1/manual/scene/material
  https://docs.unity.com/en-us/asset-transformer-sdk/2026.1/api/python/
"""

import argparse
import os
import sys

import pxz
from pxz import core, scene, io, algo, material

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
    parser.add_argument("--resolution", type=int, default=512)
    parser.add_argument("--uvChannel", type=int, default=0)
    parser.add_argument("--samples", type=int, default=32) #power of two in [8, 4096]
    parser.add_argument("--bentNormals", type=str2bool, default=False)
    parser.add_argument("--applyFilter", type=str2bool, default=True) #smooth the resulting AO maps
    parser.add_argument("--sigmaPos", type=float, default=5.0)
    parser.add_argument("--sigmaValue", type=float, default=0.2)
    parser.add_argument("--sigmaNormal", type=float, default=15.0)

    return parser.parse_args(argv)


def ensurePBRMaterials(root):
    """
    Convert every material used under root to the PBR pattern, skipping
    materials that already are PBR.
    """
    materials = scene.getMaterialsFromSubtree(root)
    nonPbrMaterials = [mat for mat in materials if material.getMaterialPattern(mat) != "PBR"]

    if nonPbrMaterials:
        print(f"Converting {len(nonPbrMaterials)} material(s) to PBR")
        scene.convertMaterialsToPBR(nonPbrMaterials)


def bakeAmbientOcclusionToTextures(resolution, uvChannel, samples, bentNormals, applyFilter, sigmaPos, sigmaValue, sigmaNormal):
    """
    Bake ambient occlusion for the whole scene into texture maps, one per
    part occurrence (shareMaps=False keeps the returned image list aligned
    1:1 with the destinations list), then assign each image to its part's
    active material as the ao channel.
    """
    root = scene.getRoot()
    ensurePBRMaterials(root)

    destinations = scene.getPartOccurrences(root)
    if not destinations:
        sys.exit("No part occurrences found to bake ambient occlusion on.")

    sessionId = algo.beginBakingSession(destinations, destinations, uvChannel, resolution, shareMaps=False)
    aoMaps = algo.bakeAOMap(sessionId, samples=samples, bentNormals=bentNormals)
    algo.endBakingSession(sessionId)

    if applyFilter:
        aoMaps = material.filterAO(aoMaps, sigmaPos=sigmaPos, sigmaValue=sigmaValue, sigmaNormal=sigmaNormal)

    for occurrence, aoImage in zip(destinations, aoMaps):
        mat = scene.getActiveMaterial(occurrence)
        if mat is None:
            print(f"Occurrence {occurrence} has no active material, skipping AO assignment")
            continue

        texture = material.Texture(image=aoImage, channel=uvChannel)
        materialInfo = material.getPBRMaterialInfos(mat)
        materialInfo.ao = ["texture", texture]
        material.setPBRMaterialInfos(mat, materialInfo)


def main():
    bake_args = parse_bake_ao_args(sys.argv[1:])
    print(f"Bake AO args: {bake_args}")

    initPixyz()
    importTemporalPixyzScene()

    print("Arguments received:")
    for name, value in vars(bake_args).items():
        print(f"  {name} = {value}")

    bakeAmbientOcclusionToTextures(
        resolution=bake_args.resolution,
        uvChannel=bake_args.uvChannel,
        samples=bake_args.samples,
        bentNormals=bake_args.bentNormals,
        applyFilter=bake_args.applyFilter,
        sigmaPos=bake_args.sigmaPos,
        sigmaValue=bake_args.sigmaValue,
        sigmaNormal=bake_args.sigmaNormal,
    )

    saveTempPixyzFile()
    print("Bake Ambient Occlusion (texture) finished successfully.")
    pxz.release()


if __name__ == "__main__":
    main()
