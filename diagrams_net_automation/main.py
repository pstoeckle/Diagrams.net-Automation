"""
Convert.
"""
from hashlib import sha3_256
from itertools import chain
from json import dumps, loads
from logging import INFO, basicConfig, getLogger
from pathlib import Path
from subprocess import call
from typing import List, MutableMapping

from tqdm import tqdm

from diagrams_net_automation import __version__
from typer import Exit, Option, Typer, echo

DRAW_IO = "/Applications/draw.io.app/Contents/MacOS/draw.io"

CACHE_FILE = Path(".diagrams.net.json")

_LOGGER = getLogger(__name__)
basicConfig(
    format="%(levelname)s: %(asctime)s: %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=INFO,
    filename="diagrams-net-automation.log",
    filemode="w",
)


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
) -> None:
    """
    Converts Draw.io files to PDF and PNG.
    """
    _setup_output_directory(output_directory_path)
    cache_file = input_directory_path.joinpath(CACHE_FILE)
    content = _load_cache(cache_file)
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
        _convert_file(content, draw_io, file, output_directory_path, width)
    cache_file.write_text(dumps(content))


def _convert_file(
    cache_content: MutableMapping[str, str],
    draw_io: Path,
    file: Path,
    output_directory_path: Path,
    widths: List[int],
) -> None:
    file_hash = hash_file(file)
    # if str(file) in cache_content.keys() and cache_content[str(file)] == file_hash:
    #     _LOGGER.info(f"The file {file} has not changed since the last conversion.")
    #     return
    echo(f"Converting {file}")
    output_subdir = output_directory_path.joinpath(file.parent)
    if not output_subdir.is_dir():
        output_subdir.mkdir(parents=True)
    new_pdf_file = output_subdir.joinpath(file.stem + ".pdf")
    new_png_file = output_subdir.joinpath(file.stem + ".png")
    new_jpg_file = output_subdir.joinpath(file.stem + ".jpg")
    _LOGGER.info(f"Convert {file} to PDF")
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
    _LOGGER.info(f"Convert {file} to PNG")
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
    _LOGGER.info(f"Convert {file} to JPEG")
    call(
        [
            draw_io,
            file,
            "--export",
            "--output",
            new_jpg_file,
            "--transparent",
        ]
    )
    for width in widths:
        _LOGGER.info(f"Convert {file} to PNG with width {width}")
        new_width_png_file = output_directory_path.joinpath(f"{file.stem}_{width}.png")
        call(
            [
                draw_io,
                file,
                "--export",
                "--output",
                new_width_png_file,
                "--width",
                str(width),
                "--transparent",
            ]
        )
        _LOGGER.info(f"Convert {file} to JPEG with width {width}")
        new_width_jpg_file = output_directory_path.joinpath(f"{file.stem}_{width}.jpg")
        call(
            [
                draw_io,
                file,
                "--export",
                "--output",
                new_width_jpg_file,
            ]
        )
    cache_content[str(file)] = file_hash
    echo(f"Converting {file}: done!")


def _load_cache(cache_file: Path) -> MutableMapping[str, str]:
    content: MutableMapping[str, str]
    if cache_file.is_file():
        content = loads(cache_file.read_text())
        return content
    else:
        content = {}
    return content


def _setup_output_directory(output_directory_path: Path) -> None:
    if not output_directory_path.is_dir():
        output_directory_path.mkdir()


def hash_file(file: Path) -> str:
    """
    Tp.
    """
    if not file.is_file():
        return ""
    current_sha = sha3_256()
    with file.open("rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            current_sha.update(chunk)
    return current_sha.hexdigest()


if __name__ == "__main__":
    app()
