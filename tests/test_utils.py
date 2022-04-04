import os

from bidsNighres.bidsutils import get_dataset_layout
from bidsNighres.utils import return_path_rel_dataset

from bidsNighres.utils import expected_nighres_output


def test_get_dataset_layout_smoke_test():
    get_dataset_layout("data")


def test_return_path_rel_dataset():

    file_path = (
        "/home/data/sub-03/func/sub-03_task-rest_space-T1w_desc-preproc_bold.nii.gz"
    )
    dataset_path = "/home/data"
    rel_file_path = return_path_rel_dataset(file_path, dataset_path)

    assert (
        rel_file_path
        == "sub-03/func/sub-03_task-rest_space-T1w_desc-preproc_bold.nii.gz"
    )


def test_expected_nighres_output():

    sub_entity = "sub-01"
    ses_entity = "ses-01"
    output_dir = os.path.join(os.getcwd(), sub_entity, ses_entity, "anat")
    file_name = f"{sub_entity}_{ses_entity}"

    output_file = expected_nighres_output(
        file_name,
        suffix="cruise-gwb",
        file_name=file_name,
        output_dir=output_dir,
    )

    expected = os.path.join(output_dir, f"{file_name}_cruise-gwb.nii.gz")

    assert output_file == expected
