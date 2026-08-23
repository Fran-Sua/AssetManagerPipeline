"""
Pixyz SDK -- Tessellate
=======================================================

Verified against Pixyz SDK v2026.3.x (rebranded "Unity Asset Transformer SDK").
The `pxz` Python module and the function names below are unchanged from the
Pixyz-branded SDK, so this runs fine under the 2026.3.1.1 build.

Docs referenced:
- Algo functions:
  https://docs.unity.com/en-us/asset-transformer-sdk/2026.1/api/python/algo_functions
"""

import os
import sys

import pxz
from pxz import core, scene, io, algo


def parse_pipeline_args(argv):
    """
    Parse arguments as invoked by an Asset Manager pipeline step.

    The pipeline runner builds the call as:
        script.py [ "input.ext" ], output_dir
    without quoting the brackets/comma, so the shell splits it into argv
    tokens like:
        ['[', 'input.ext', '],', 'output_dir']

    Falls back to plain "input_file output_file" for local/manual runs.
    """
    print("Checking arguments")
    if len(argv) == 4 and argv[0] == "[" and argv[2] == "],":
        return argv[1], argv[3]

    if len(argv) == 2:
        return argv[0], argv[1]

    sys.exit(f"Unrecognized arguments: {argv}")


def main():
    input_file, output_dir = parse_pipeline_args(sys.argv[1:])
    print (f"InputFile:{input_file}, OutputFile: {output_dir}")

    if not os.path.isfile(input_file):
        sys.exit(f"Input file not found: {input_file}")

    os.makedirs(output_dir, exist_ok=True)

    # init Pixyz
    if pxz.get_current_session() == None:
        pxz.initialize()

    # print Pixyz version
    print(f'Pixyz version: {pxz.core.getVersion()}')

    # set log level to INFO so you can see the logs in the console
    pxz.core.configureInterfaceLogger(True, True, True)
    pxz.core.addConsoleVerbose(core.Verbose.INFO)

    print(f"Importing: {input_file}")
    root = io.importScene(input_file)

    # select root and apply the default tessellation
    #algo.tessellate([root])
    algo.tessellate([root], maxSag=0.2, maxLength=-1, maxAngle=-1, createNormals=True, uvMode=0, uvChannel=1, uvPadding=0.0, createTangents=False, createFreeEdges=False, keepBRepShape=True, overrideExistingTessellation=False)


    output_name = os.path.splitext(os.path.basename(input_file))[0] + ".glb"
    output_file = os.path.join(output_dir, output_name)
    print(f"Exporting: {output_file}")
    io.exportScene(output_file, root)

    print("Done.")
    pxz.release()


if __name__ == "__main__":
    main()

