import os
import nighres

from bids import BIDSLayout
from os.path import join
from rich import print

this_participant = "pilot001"
this_session = "001"

n_layers = 6
input_folder = "../../../outputs/derivatives/cpp_spm-preproc"

layout = BIDSLayout(input_folder)

print(layout)

sub_entity = f"sub-{this_participant}"
ses_entity = f"ses-{this_session}"
output_dir = join(layout.root, sub_entity, ses_entity, "anat")

segmentation = layout.get(
    subject="pilot001",
    extension="nii.*",
    suffix="dseg",
    acquisition="r0p75",
    invalid_filters="allow",
    regex_search=True,
)

levelset_boundary = layout.get(
    subject="pilot001",
    extension="nii.*",
    suffix="dist",
    acquisition="r0p75",
    invalid_filters="allow",
    regex_search=True,
)

maximum_membership = layout.get(
    subject="pilot001",
    extension="nii.*",
    description=["memberships"],
    suffix="probseg",
    acquisition="r0p75",
    invalid_filters="allow",
    regex_search=True,
)

maximum_label = layout.get(
    subject="pilot001",
    extension="nii.*",
    description=["labels"],
    suffix="probseg",
    acquisition="r0p75",
    invalid_filters="allow",
    regex_search=True,
)

output_filename = f"{sub_entity}_{ses_entity}_"

# extract left cerebrum
ROIS = ["right_cerebrum", "left_cerebrum"]
LABELS = ["RightCerebrum", "LeftCerebrum"]

for roi in ROIS:
    cortex = nighres.brain.extract_brain_region(
        segmentation=segmentation,
        levelset_boundary=levelset_boundary,
        maximum_membership=maximum_membership,
        maximum_label=maximum_label,
        extracted_region=roi,
        save_data=True,
        file_name=output_filename,
        output_dir=output_dir,
    )

    cruise = nighres.cortex.cruise_cortex_extraction(
        init_image=cortex["inside_mask"],
        wm_image=cortex["inside_proba"],
        gm_image=cortex["region_proba"],
        csf_image=cortex["background_proba"],
        normalize_probabilities=True,
        save_data=True,
        file_name=output_filename,
        output_dir=output_dir,
    )

    depth = nighres.laminar.volumetric_layering(
        inner_levelset=cruise["gwb"],
        outer_levelset=cruise["cgb"],
        n_layers=n_layers,
        save_data=True,
        file_name=output_filename,
        output_dir=output_dir,
    )
