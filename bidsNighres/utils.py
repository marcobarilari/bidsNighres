import os
from os.path import abspath
from os.path import dirname
from pathlib import Path

from nighres.utils import _output_dir_4saving, _fname_4saving

from rich import print


def print_to_screen(msg):
    print(f"[blue]{msg}[/blue]")


def move_file(input: str, output: str, dry_run=False):

    print(f"[blue]{abspath(input)}[/blue] --> \n[green]{abspath(output)}[/green]\n")
    if not dry_run:
        create_dir_for_file(output)
        os.rename(input, output)


def return_regex(string):
    return f"^{string}$"


def create_dir_if_absent(output_path: str):
    if not Path(output_path).exists():
        print(f"Creating dir: {output_path}")
        os.makedirs(output_path)


def create_dir_for_file(file: str):
    output_path = dirname(abspath(file))
    create_dir_if_absent(output_path)


def return_path_rel_dataset(file_path: str, dataset_path: str) -> str:
    """
    Create file path relative to the root of a dataset
    """
    file_path = abspath(file_path)
    dataset_path = abspath(dataset_path)
    rel_path = file_path.replace(dataset_path, "")
    rel_path = rel_path[1:]
    return rel_path


def expected_nighres_output(
    rootfile,
    suffix,
    file_name=None,
    output_dir=None,
):

    output_dir = _output_dir_4saving(output_dir, file_name)

    output_file = os.path.join(
        output_dir,
        _fname_4saving(
            file_name=file_name,
            rootfile=rootfile,
            suffix=suffix,
        ),
    )

    return output_file
