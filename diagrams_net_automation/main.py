"""
Convert.
"""
from logging import INFO, basicConfig, getLogger
from pathlib import Path as pathlib_Path
from shutil import rmtree
from subprocess import call
from sys import stdout
from typing import Any

from click import Context, Path, command, echo, option, group

from diagrams_net_automation import __version__

DRAW_IO = "/Applications/draw.io.app/Contents/MacOS/draw.io"


_LOGGER = getLogger(__name__)
basicConfig(
    format="%(levelname)s: %(asctime)s: %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=INFO,
    stream=stdout,
)


def _print_version(ctx: Context, _: Any, value: Any) -> None:
    """

    :param ctx:
    :param _:
    :param value:
    :return:
    """
    if not value or ctx.resilient_parsing:
        return
    echo(__version__)
    ctx.exit()


@group()
@option(
    "--version",
    is_flag=True,
    callback=_print_version,
    expose_value=False,
    is_eager=True,
    help="Version",
)
def main_group() -> None:
    """

    :return:
    """


@option(
    "--input-directory",
    "-d",
    type=Path(exists=True, file_okay=False, resolve_path=True),
    default=".",
)
@option(
    "--output-directory",
    "-o",
    type=Path(file_okay=False, resolve_path=True),
    default="dist",
)
@option(
    "--draw-io",
    "-D",
    type=Path(exists=True, resolve_path=True, dir_okay=False),
    default=DRAW_IO,
)
@main_group.command()
def convert_diagrams(input_directory: str, output_directory: str, draw_io: str) -> None:
    """
    Converts Draw.io files to PDF and PNG.
    """
    input_directory_path = pathlib_Path(input_directory)
    output_directory_path = pathlib_Path(output_directory)
    if output_directory_path.is_dir():
        rmtree(output_directory)
    output_directory_path.mkdir()
    files = input_directory_path.iterdir()
    files = [
        f
        for f in files
        if f.is_file()
        and (f.suffix.casefold() == ".xml" or f.suffix.casefold() == ".drawio")
    ]
    for file in files:
        _LOGGER.info(file)
        new_pdf_file = output_directory_path.joinpath(file.stem + ".pdf")
        new_png_file = output_directory_path.joinpath(file.stem + ".png")
        call(
            [
                draw_io,
                file,
                "--export",
                "--output",
                new_pdf_file,
                "--crop",
            ]
        )
        call(
            [
                draw_io,
                file,
                "--export",
                "--output",
                new_png_file,
                "--transparent",
            ]
        )


if __name__ == "__main__":
    main_group()
