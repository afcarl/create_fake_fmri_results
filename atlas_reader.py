import sys
import numpy as np
import nibabel as nb


def getVoxCoord(affine, coord):
    """computes voxel ID from MNI coordinate"""
    inverse = np.linalg.inv(affine)
    voxCoord = np.dot(inverse, np.hstack((coord, 1)))[:3]
    return voxCoord.round().astype('int').tolist()


def getLabel(atlastype, labelID):
    """reads out the name of a specific label"""
    if 'freesurfer' in atlastype:
        atlastype = 'freesurfer'
    labels = np.recfromcsv('atlases/labels_%s.csv' % atlastype)
    labelIdx = labels.index == labelID
    if labelIdx.sum() == 0:
        label = 'No_label'
    else:
        label = labels[labelIdx][0][1]
    return label


def readAtlas(atlastype, coordinate, probThresh=5):
    """
    Reads specific atlas and returns segment/probability information.
    It is possible to threshold a given probability atlas [in percentage].
    """

    atlas = nb.load('atlases/atlas_%s.nii.gz' % atlastype)

    # Get atlas data and affine matrix
    data = atlas.get_data()
    affine = atlas.affine

    # Get voxel index
    voxID = getVoxCoord(affine, coordinate)

    # Get Label information
    probs = data[voxID[0], voxID[1], voxID[2]]
    probs[probs < probThresh] = 0
    idx = np.where(probs)[0]

    # sort list by probability
    idx = idx[np.argsort(probs[idx])][::-1]

    # get probability and label names
    probLabel = []
    for i in idx:
        label = getLabel(atlastype, i)
        probLabel.append([probs[i], label])

    # If no labels found
    if probLabel == []:
        probLabel = [[0, 'No_label']]

    return probLabel


def writeOutputToScreen(atlasinfo, coord):
    """Writes output to the sceen"""
    print("Peak Information at {0}:".format(coord))

    for ainfo in atlasinfo:
        for s in ainfo[1]:
            print("{0:<30}{1:>4}% {2}".format(ainfo[0], s[0], s[1]))
    print("\n")


def getAtlasinfo(coord, atlastype='all', probThresh=5, writeToScreen=True):

    atlasinfo = []
    if atlastype != 'all':
        segment = readAtlas(atlastype, coord, probThresh)
        atlasinfo.append([atlastype, segment])
    else:
        for atypes in ['HarvardOxford',
                       'Juelich']:
            segment = readAtlas(atypes, coord, probThresh)
            atlasinfo.append([atypes, segment])

    # Write output to screen
    if writeToScreen:
        writeOutputToScreen(atlasinfo, coord)

    return atlasinfo


if __name__ == "__main__":

    atlastype = str(sys.argv[1])
    coord = [float(x) for x in str(sys.argv[2]).split(',')]
    probThresh = int(sys.argv[3])
    writeToScreen = bool(sys.argv[4])

    getAtlasinfo(coord, atlastype, probThresh, writeToScreen)
