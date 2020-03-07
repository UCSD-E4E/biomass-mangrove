import os
import sys
import gdal
import ntpath
import argparse


if __name__ == "__main__":
    """
    Entry point from command line.

    Optional Parameters:
        folder  (str): Source folder will be scanned for TIF files.
    """

    # Define arguments and options
    parser = argparse.ArgumentParser(prog="get_centers.py",
                                     description="Roughly calculate the center point of an orthomosaic.")
    parser.add_argument('folder', metavar='FOLDER', type=str, help='Source folder containing orthomosaics.')

    # Process arguments and options
    a = parser.parse_args(sys.argv[1:])
    folder = a.folder

    # Prepare file list
    files = []
    for r, d, f in os.walk(folder):
        for file in f:
            if '.tif' in file.lower():
                files.append(os.path.join(r, file))
    if len(files) == 0:
        print("Please specify a folder that contains TIF files.")
        exit()

    # Process center for each file
    for file in files:

        # Vars
        lat = "Invalid File"
        long = ""

        # Analyze image file
        image_transform = size = []
        if file != "":
            image_info = gdal.Info(file, format="json")
            image_transform = image_info['geoTransform']
            size = image_info["size"]

        # Calculate centers
        width = image_transform[1] * size[0]
        height = image_transform[5] * size[1]
        long = image_transform[0] + 0.5 * width
        lat = image_transform[3] + 0.5 * height

        # Print file info
        name = ntpath.basename(file)
        print("{0:<40}{1:<20}{2:<20}".format(name, lat, long))
