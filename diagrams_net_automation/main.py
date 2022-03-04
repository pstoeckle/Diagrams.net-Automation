"""
Convert.
"""
from itertools import chain
from logging import INFO, basicConfig, getLogger
from pathlib import Path
from typing import List

from tqdm import tqdm

from diagrams_net_automation import __version__
from diagrams_net_automation.converter import Converter
from typer import Exit, Option, Typer, echo

DRAW_IO = "/Applications/draw.io.app/Contents/MacOS/draw.io"

CACHE_FILE = Path(".diagrams.net.json")

basicConfig(
    format="%(levelname)s: %(asctime)s: %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=INFO,
    filename="diagrams-net-automation.log",
    filemode="w",
)
_LOGGER = getLogger(__name__)


def _version_callback(value: bool) -> None:
    if value:
        echo(f"diagrams-net-automation {__version__}")
        raise Exit()


app = Typer()


@app.callback()
def _call_back(
    _: bool = Option(
        None,
        "--version",
        is_flag=True,
        callback=_version_callback,
        expose_value=False,
        is_eager=True,
        help="Version",
    )
) -> None:
    """

    :return:
    """


@app.command()
def convert_diagrams(
    input_directory_path: Path = Option(
        ".", "--input-directory", "-d", exists=True, file_okay=False
    ),
    output_directory_path: Path = Option(
        "dist", "--output-directory", "-o", file_okay=False, resolve_path=True
    ),
    draw_io: Path = Option(
        DRAW_IO, "--draw-io", "-D", exists=True, resolve_path=True, dir_okay=False
    ),
    width: List[int] = Option([], "--width", "-w"),
    include_xml: bool = Option(False, "--include-xml", "-X", is_flag=True),
    create_png: bool = Option(False, "--generate-png", "-P", is_flag=True),
    create_jpg: bool = Option(False, "--generate-jpg", "-J", is_flag=True),
    skip_pdf: bool = Option(False, "--skip-pdf-generation", "-S", is_flag=True),
) -> None:
    """
    Converts Draw.io files to PDF and PNG.
    """
    _setup_output_directory(output_directory_path)

    converter = Converter(
        cache_file=input_directory_path.joinpath(CACHE_FILE),
        create_jpg=create_jpg,
        create_png=create_png,
        draw_io=draw_io,
        output_directory=output_directory_path,
        skip_pdf=skip_pdf,
        widths=width,
    )
    if not create_jpg:
        echo("We will generate no JPGs.")
    if not create_png:
        echo("We will generate no PNGs.")
    if skip_pdf:
        echo("We will generate no PDFs.")
    files = sorted(
        list(
            chain(
                input_directory_path.glob("**/*.drawio"),
                input_directory_path.glob("**/*.xml"),
            )
            if include_xml
            else input_directory_path.glob("**/*.drawio")
        )
    )
    for file in tqdm(files):
        converter.convert_file(file)


def _setup_output_directory(output_directory_path: Path) -> None:
    if not output_directory_path.is_dir():
        output_directory_path.mkdir(parents=True)


if __name__ == "__main__":
    app()
