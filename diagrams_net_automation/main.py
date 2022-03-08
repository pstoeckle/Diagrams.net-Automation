"""
Convert.
"""
from itertools import chain
from json import dumps, loads
from logging import INFO, basicConfig, getLogger
from pathlib import Path
from subprocess import check_call
from typing import List, MutableMapping

from lxml import etree
from tqdm import tqdm

from diagrams_net_automation import __version__
from diagrams_net_automation.converter import Converter
from diagrams_net_automation.utils import hash_file
from typer import Exit, Option, Typer, echo

DRAW_IO = "/Applications/draw.io.app/Contents/MacOS/draw.io"

_CONVERT_CACHE_FILE = Path(".diagrams.net.json")
_UNCOMPRESS_CACHE_FILE = Path(".diagrams.net.uncompress.json")

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


_DRAW_IO_OPTION = Option(
    DRAW_IO,
    "--draw-io",
    "-D",
    exists=True,
    resolve_path=True,
    dir_okay=False,
    help="The diagrams.net executable.",
)
_INPUT_DIR_OPTION = Option(
    ".",
    "--input-directory",
    "-d",
    exists=True,
    file_okay=False,
    help="Input directory with the diagrams.net files.",
)


@app.command()
def convert_diagrams(
    input_directory_path: Path = _INPUT_DIR_OPTION,
    output_directory_path: Path = Option(
        "dist",
        "--output-directory",
        "-o",
        file_okay=False,
        resolve_path=True,
        help="The output directory where the PDF, JPG, or PNG files should be stored.",
    ),
    draw_io: Path = _DRAW_IO_OPTION,
    width: List[int] = Option(
        [],
        "--width",
        "-w",
        help="If a width is passed, we will generate a PNG and/or JPG with this width.",
    ),
    include_xml: bool = Option(
        False,
        "--include-xml",
        "-X",
        is_flag=True,
        help="Convert also .xml files, not only .drawio files.",
    ),
    create_png: bool = Option(
        False, "--generate-png", "-P", is_flag=True, help="Generate PNG files."
    ),
    create_jpg: bool = Option(
        False, "--generate-jpg", "-J", is_flag=True, help="Generate JPG files."
    ),
    skip_pdf: bool = Option(
        False,
        "--skip-pdf-generation",
        "-S",
        is_flag=True,
        help="If this flag is set, we will not generate PDF files.",
    ),
    ignore_cache: bool = Option(
        False,
        "--ignore-cache",
        "-I",
        is_flag=True,
        help="If this flag is passed, we will ignore anything in the current cache file. In the end, we will overwrite the current cache file.",
    ),
) -> None:
    """
    Converts Draw.io files to PDF and PNG.
    """
    _setup_output_directory(output_directory_path)

    converter = Converter(
        cache_file=input_directory_path.joinpath(_CONVERT_CACHE_FILE),
        create_jpg=create_jpg,
        create_png=create_png,
        draw_io=draw_io,
        output_directory=output_directory_path,
        skip_pdf=skip_pdf,
        widths=width,
    )
    if ignore_cache:
        converter.clear_cache()
        echo("We cleared the cache")
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
    converter.update_cache_file()


@app.command()
def uncompress_all_diagrams(
    input_directory_path: Path = _INPUT_DIR_OPTION,
    draw_io: Path = _DRAW_IO_OPTION,
    inplace: bool = Option(
        False,
        "--inplace",
        "-I",
        is_flag=True,
        help="If this flag is set, all files will be rewritten.",
    ),
) -> None:
    """
    Uncompress all draw.io (diagrams.net) files.
    """
    cache: MutableMapping[str, str] = (
        loads(local_cache_file.read_text())
        if (local_cache_file := input_directory_path.joinpath(_UNCOMPRESS_CACHE_FILE)).is_file()
        else {}
    )

    echo("Start file uncompression...")
    file: Path
    for file in tqdm(list(input_directory_path.glob("**/*.drawio"))):
        _LOGGER.info(f"Convert {file}...")
        new_hash = hash_file(file)
        if (old_hash := cache.get(str(file))) is not None and new_hash == old_hash:
            _LOGGER.info(f"The file {file} has the same hash as last time.")
            continue
        log_file_path = Path("draw-io.log")
        with log_file_path.open("a") as log_file:
            new_file = (
                str(file)
                if inplace
                else str(file.parent.joinpath(file.stem + ".cleaned.drawio"))
            )
            res = check_call(
                [
                    str(draw_io),
                    "--export",
                    "--format",
                    "xml",
                    "--output",
                    new_file,
                    "--uncompressed",
                    str(file),
                ],
                stdout=log_file,
            )
            if res != 0:
                echo(log_file_path.read_text())
                raise Exit(1)
        xml = etree.XML(file.read_text())
        file.write_text(etree.tostring(xml, pretty_print=True).decode())
        cache[str(file)] = hash_file(file) if inplace else new_hash
        _LOGGER.info(f"Converting {file} done!")
    local_cache_file.write_text(dumps(cache))
    echo("Done!")


def _setup_output_directory(output_directory_path: Path) -> None:
    if not output_directory_path.is_dir():
        output_directory_path.mkdir(parents=True)


if __name__ == "__main__":
    app()
