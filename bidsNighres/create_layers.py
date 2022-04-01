import copy
from os.path import join

import nighres

from bidsNighres.utils import print_to_screen
from bidsNighres.utils import return_path_rel_dataset


def create_layers(
    layout_out, this_participant, bids_filter: dict, nb_layers=6, dry_run=False
):

    print_to_screen(f"\n[bold]Processing: sub-{this_participant}[/bold]")

    this_filter = copy.deepcopy(bids_filter["UNIT1"])
    this_filter["subject"] = this_participant
    this_filter["extension"] = "nii.*"

    sessions = layout_out.get_sessions(
        regex_search=True,
        **this_filter,
    )

    for ses in sessions:

        this_filter["session"] = ses
        # this_filter["description"] = ""

        print_to_screen(f"[bold] Processing: ses-{ses}[/bold]")

        this_filter["suffix"] = "dseg"
        segmentation = layout_out.get(
            invalid_filters="allow",
            regex_search=True,
            **this_filter,
        )

        this_filter["suffix"] = "dist"
        levelset_boundary = layout_out.get(
            invalid_filters="allow",
            regex_search=True,
            **this_filter,
        )

        this_filter["suffix"] = "probseg"
        this_filter["description"] = "memberships"
        maximum_membership = layout_out.get(
            invalid_filters="allow",
            regex_search=True,
            **this_filter,
        )

        this_filter["description"] = "labels"
        maximum_label = layout_out.get(
            invalid_filters="allow",
            regex_search=True,
            **this_filter,
        )

        print_to_screen(return_path_rel_dataset(segmentation[0], layout_out.root))
        print_to_screen(return_path_rel_dataset(levelset_boundary[0], layout_out.root))
        print_to_screen(return_path_rel_dataset(maximum_membership[0], layout_out.root))
        print_to_screen(return_path_rel_dataset(maximum_label[0], layout_out.root))

        sub_entity = f"sub-{this_participant}"
        ses_entity = f"ses-{ses}"
        output_dir = join(layout_out.root, sub_entity, ses_entity, "anat")
        output_filename = f"{sub_entity}_{ses_entity}"

        # extract cerebrums
        ROIS = ["right_cerebrum", "left_cerebrum"]
        LABELS = ["R", "L"]

        for label, roi in zip(LABELS, ROIS):

            if not dry_run:

                cortex = nighres.brain.extract_brain_region(
                    segmentation=segmentation[0].path,
                    levelset_boundary=levelset_boundary[0].path,
                    maximum_membership=maximum_membership[0].path,
                    maximum_label=maximum_label[0].path,
                    extracted_region=roi,
                    save_data=True,
                    file_name=f"{output_filename}_hemi-{label}",
                    output_dir=output_dir,
                )

                cruise = nighres.cortex.cruise_cortex_extraction(
                    init_image=cortex["inside_mask"],
                    wm_image=cortex["inside_proba"],
                    gm_image=cortex["region_proba"],
                    csf_image=cortex["background_proba"],
                    normalize_probabilities=True,
                    save_data=True,
                    file_name=f"{output_filename}_hemi-{label}",
                    output_dir=output_dir,
                )

                nighres.laminar.volumetric_layering(
                    inner_levelset=cruise["gwb"],
                    outer_levelset=cruise["cgb"],
                    n_layers=nb_layers,
                    save_data=True,
                    file_name=f"{output_filename}_hemi-{label}",
                    output_dir=output_dir,
                )
