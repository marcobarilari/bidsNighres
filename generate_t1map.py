# This won't work if you do not have the phase images.

from bids import BIDSLayout
from os.path import join
from rich import print
from pymp2rage.pymp2rage import MP2RAGE

input_folder = "../../../outputs/derivatives/cpp_spm-preproc"

layout = BIDSLayout(input_folder)

print(layout)

inv1 = layout.get(
    subject="pilot001",
    extension="nii.*",
    suffix="MP2RAGE",
    inv=1,
    part="mag",
    acquisition="r0p75",
    regex_search=True,
)

inv1ph = layout.get(
    subject="pilot001",
    extension="nii.*",
    suffix="MP2RAGE",
    inv=1,
    part="phase",
    acquisition="r0p75",
    regex_search=True,
)

print(inv1[0].path)

inv2 = layout.get(
    subject="pilot001",
    extension="nii.*",
    suffix="MP2RAGE",
    inv=2,
    part="mag",
    acquisition="r0p75",
    regex_search=True,
)

inv2ph = layout.get(
    subject="pilot001",
    extension="nii.*",
    suffix="MP2RAGE",
    inv=2,
    part="phase",
    acquisition="r0p75",
    regex_search=True,
)

print(inv2[0].path)

B0 = inv1[0].get_metadata()["MagneticFieldStrength"]

invtimesAB = [
    inv1[0].get_metadata()["InversionTime"],
    inv2[0].get_metadata()["InversionTime"],
]
flipangleABdegree = [
    inv1[0].get_metadata()["FlipAngle"],
    inv2[0].get_metadata()["FlipAngle"],
]
MPRAGE_tr = inv1[0].get_metadata()["RepetitionTimePreparation"]
nZslices = inv1[0].get_metadata()["NumberShots"]
FLASH_tr = [
    inv1[0].get_metadata()["RepetitionTimeExcitation"],
    inv2[0].get_metadata()["RepetitionTimeExcitation"],
]

fitter = MP2RAGE(
    MPRAGE_tr=B0,
    invtimesAB=invtimesAB,
    flipangleABdegree=flipangleABdegree,
    nZslices=150,
    FLASH_tr=FLASH_tr,
    inv1=inv1[0].path,
    inv1ph=inv1ph[0].path,
    inv2=inv2[0].path,
    inv2ph=inv2ph[0].path,
)

output_file = join(
    input_folder,
)
fitter.t1map.to_filename(
    "sub-pilot001", "ses-001", "anat", "sub-pilot001_ses-001_T1map.nii"
)
