import copy
from os.path import join

import nighres

from bidsNighres.utils import print_to_screen
from bidsNighres.utils import return_path_rel_dataset
from bidsNighres.bidsutils import bidsify_layering_output

from rich import print


def create_layers(
    layout_out, this_participant, bids_filter: dict, nb_layers=6, dry_run=False
):
    """_summary_

    Args:
        layout_out (_type_): _description_
        this_participant (_type_): _description_
        bids_filter (dict): _description_
        nb_layers (int, optional): _description_. Defaults to 6.
        dry_run (bool, optional): _description_. Defaults to False.

    Raises:
        ValueError: _description_
    """

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

        print_to_screen(f"[bold] Processing: ses-{ses}[/bold]")

        # TODO make sure only the dseg is selected
        # Could be an issue if we get layer files that are renamed to *_dseg.nii

        this_filter["suffix"] = "dseg"
        segmentations = layout_out.get(
            invalid_filters="allow",
            regex_search=True,
            **this_filter,
        )

        for segmentation_img in segmentations:

            entities = segmentation_img.get_entities()

            segmentation_img = layout_out.get(
                invalid_filters="allow",
                regex_search=True,
                return_type="filename",
                **entities,
            )

            if len(segmentation_img) > 1:
                print(f"[red]{segmentation_img}[/red]")
                raise ValueError("Only one image there")

            entities["suffix"] = "dist"
            levelset_boundary_img = layout_out.get(
                invalid_filters="allow",
                regex_search=True,
                return_type="filename",
                **entities,
            )

            entities["suffix"] = "probseg"
            entities["desc"] = "memberships"
            max_membership_img = layout_out.get(
                invalid_filters="allow",
                regex_search=True,
                return_type="filename",
                **entities,
            )

            entities["desc"] = "labels"
            max_label_img = layout_out.get(
                invalid_filters="allow",
                regex_search=True,
                return_type="filename",
                **entities,
            )

            print_to_screen(
                "  " + return_path_rel_dataset(segmentation_img[0], layout_out.root)
            )
            print_to_screen(
                "  "
                + return_path_rel_dataset(levelset_boundary_img[0], layout_out.root)
            )
            print_to_screen(
                "  " + return_path_rel_dataset(max_membership_img[0], layout_out.root)
            )
            print_to_screen(
                "  " + return_path_rel_dataset(max_label_img[0], layout_out.root)
            )

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
                        segmentation=segmentation_img[0],
                        levelset_boundary=levelset_boundary_img[0],
                        maximum_membership=max_membership_img[0],
                        maximum_label=max_label_img[0],
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

                    layering = nighres.laminar.volumetric_layering(
                        inner_levelset=cruise["gwb"],
                        outer_levelset=cruise["cgb"],
                        n_layers=nb_layers,
                        save_data=True,
                        file_name=f"{output_filename}_hemi-{label}",
                        output_dir=output_dir,
                    )

                    outputs = {**cruise, **layering}

                    bidsify_layering_output(
                        outputs,
                        layout_out,
                        segmentation_img[0],
                        hemi_label=label,
                        nb_layers=nb_layers,
                        dry_run=dry_run,
                    )
