from bids import BIDSLayout

from pymp2rage.pymp2rage import MP2RAGE

input_folder = "../../../inputs/raw/"

layout = BIDSLayout(input_folder)

inv1 = layout.get(
    subject="pilot001",
    extension="nii.*",
    suffix="MP2RAGE",
    inv=1,
    part="mag",
    acquisition="r0p75",
    regex_search=True,
)

inv1[0].get_metadata()["FieldStrength"]
inv1[0].get_metadata()["InversionTime"]
inv1[0].get_metadata()["FlipAngle"]

inv2 = layout.get(
    subject="pilot001",
    extension="nii.*",
    suffix="MP2RAGE",
    inv=2,
    part="mag",
    acquisition="r0p75",
    regex_search=True,
)

# MP2RAGE inv1 0.75mm ;
# echo spacing = 7.2 ms
# SlicesPerSlab = 192
# SlicePartialFourier = 6/8
# nbShotsBefore = SlicesPerSlab*(SlicePartialFourier - 0.5) = 48
# nbShotsAfter = SlicesPerSlab / 2

inversion_efficiency = 0.96
B0 = inv1[0].get_metadata()["MagneticFieldStrength"]
inv1[0].get_metadata()["MagneticFieldStrength"]
invtimesAB = [
    inv1[0].get_metadata()["InversionTime"],
    inv2[0].get_metadata()["InversionTime"],
]
flipangleABdegree = [
    inv1[0].get_metadata()["FlipAngle"],
    inv2[0].get_metadata()["FlipAngle"],
]

# MPRAGE_tr = df.loc[('MP2RAGE', 1, 'mag'), 'RepetitionTimePreparation']
# nZslices = df.loc[('MP2RAGE', 1, 'mag'), 'NumberShots']
# FLASH_tr = df.loc[('MP2RAGE', 1, 'mag'), 'RepetitionTimeExcitation'], df.loc[('MP2RAGE', 2, 'mag'), 'RepetitionTimeExcitation']


"""
If NumberShots is an array of numbers such that "NumberShots": [before, after], the values of before and after are calculated as follows:

SlicesPerSlab * [PartialFourierInSlice-0.5 0.5]

before = SlicesPerSlab*(SlicePartialFourier - 0.5)
after  = SlicesPerSlab/2

"""

"""
The value of the RepetitionTimeExcitation field is not commonly found in the DICOM files.
When accessible, the value of EchoSpacing corresponds to this metadata.
When not accessible, 2 X EchoTime can be used as a surrogate.
"""

# fitter = pymp2rage.MP2RAGE(MPRAGE_tr=6.723,
#                            invtimesAB=[0.67, 3.855],
#                            flipangleABdegree=[7, 6],
#                            nZslices=150,
#                            FLASH_tr=[0.0062, 0.0320],
#                            inv1='/data/sourcedata/sub-012/anat/sub-012_acq-highres0p64ME_INV1.nii',
#                            inv1ph='/data/sourcedata/sub-012/anat/sub-012_acq-highres0p64ME_INV1ph.nii',
#                            inv2='/data/sourcedata/sub-012/anat/sub-012_acq-highres0p64ME_INV2.nii',
#                            inv2ph='/data/sourcedata/sub-012/anat/sub-012_acq-highres0p64ME_INV2ph.nii')
