from os.path import join

import nighres

from bidsNighres.bidsutils import bidsify_segment_output
from bidsNighres.bidsutils import bidsify_skullstrip_output
from bidsNighres.utils import print_to_screen
from bidsNighres.utils import return_path_rel_dataset


def skullstrip(
    layout_in, layout_out, this_participant, bids_filter: dict, dry_run=False
):

    print_to_screen(f"\n[bold]Processing: sub-{this_participant}[/bold]")

    sessions = layout_in.get_sessions(
        subject=this_participant,
        extension="nii",
        regex_search=True,
        **bids_filter["UNIT1"],
    )

    for ses in sessions:

        print_to_screen(f"[bold] Processing: ses-{ses}[/bold]")

        unit1_files = layout_in.get(
            subject=this_participant,
            session=ses,
            extension="nii",
            regex_search=True,
            **bids_filter["UNIT1"],
        )

        for bf in unit1_files:

            # entities = bf.get_entities()

            # TODO make output path generation more flexible
            sub_entity = f"sub-{this_participant}"
            ses_entity = f"ses-{ses}"
            output_dir = join(layout_out.root, sub_entity, ses_entity, "anat")

            # TODO find a way to match the entities between files
            # use filter file to select only lores
            # entities["acquisition"] = "lores"

            UNIT1 = layout_in.get(
                return_type="filename",
                subject=this_participant,
                session=ses,
                extension="nii",
                regex_search=True,
                **bids_filter["UNIT1"],
            )
            print_to_screen(
                f"t1 weighted image: {return_path_rel_dataset(UNIT1[0], layout_in.root)}"
            )

            inv2 = layout_in.get(
                return_type="filename",
                subject=this_participant,
                session=ses,
                extension="nii",
                regex_search=True,
                **bids_filter["inv2"],
            )
            print_to_screen(
                f"second inversion image: {return_path_rel_dataset(inv2[0], layout_in.root)}"
            )

            T1map = layout_in.get(
                return_type="filename",
                subject=this_participant,
                session=ses,
                extension="nii",
                regex_search=True,
                **bids_filter["T1map"],
            )
            print_to_screen(
                f"t1 map image: {return_path_rel_dataset(T1map[0], layout_in.root)}"
            )

            if not dry_run:

                skullstrip_output = nighres.brain.mp2rage_skullstripping(
                    second_inversion=inv2[0],
                    t1_weighted=UNIT1[0],
                    t1_map=T1map[0],
                    save_data=True,
                    file_name=f"{sub_entity}_{ses_entity}",
                    output_dir=output_dir,
                )

                bidsify_skullstrip_output(
                    skullstrip_output,
                    layout_in=layout_in,
                    layout_out=layout_out,
                    UNIT1=UNIT1[0],
                    inv2=inv2[0],
                    T1map=T1map[0],
                    dry_run=False,
                )

                # TODO generate JSON for derivatives
                # import json
                # data = {'field1': 'value1', 'field2': 3, 'field3': 'field3'}
                # with open('my_output_file.json', 'w') as ff:
                #     json.dump(data, ff)


def segment(layout_out, this_participant, bids_filter: dict, dry_run=False):

    print_to_screen(f"\n[bold]Processing: sub-{this_participant}[/bold]")

    sessions = layout_out.get_sessions(
        subject=this_participant,
        extension="nii",
        regex_search=True,
        **bids_filter["UNIT1"],
    )

    for ses in sessions:

        print_to_screen(f"[bold] Processing: ses-{ses}[/bold]")

        # TODO make output path generation more flexible
        sub_entity = f"sub-{this_participant}"
        ses_entity = f"ses-{ses}"
        output_dir = join(layout_out.root, sub_entity, ses_entity, "anat")

        skullstripped_UNIT1 = layout_out.get(
            return_type="filename",
            subject=this_participant,
            session=ses,
            extension="nii",
            description=["skullstripped"],
            regex_search=True,
            invalid_filters="allow",
            **bids_filter["UNIT1"],
        )
        print_to_screen(
            f"t1 weigthed image: {return_path_rel_dataset(skullstripped_UNIT1[0], layout_out.root)}"
        )

        skullstripped_T1map = layout_out.get(
            return_type="filename",
            subject=this_participant,
            session=ses,
            extension="nii",
            description=["skullstripped"],
            regex_search=True,
            invalid_filters="allow",
            **bids_filter["T1map"],
        )
        print_to_screen(
            f"t1 map image: {return_path_rel_dataset(skullstripped_T1map[0], layout_out.root)}"
        )

        if not dry_run:

            segment_output = nighres.brain.mgdm_segmentation(
                contrast_image1=skullstripped_UNIT1[0],
                contrast_type1="Mp2rage7T",
                contrast_image2=skullstripped_T1map[0],
                contrast_type2="T1map7T",
                save_data=True,
                file_name=f"{sub_entity}_{ses_entity}",
                output_dir=output_dir,
            )

            bidsify_segment_output(
                segment_output, layout_out, skullstripped_UNIT1[0], dry_run=False
            )

            # TODO generate JSON for derivatives
            # import json
            # data = {'field1': 'value1', 'field2': 3, 'field3': 'field3'}
            # with open('my_output_file.json', 'w') as ff:
            #     json.dump(data, ff)
