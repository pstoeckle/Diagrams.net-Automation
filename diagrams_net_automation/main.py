"""
Convert.
"""
from hashlib import sha3_256
from json import dump, load
from logging import INFO, basicConfig, getLogger
from pathlib import Path as pathlib_Path
from shutil import rmtree
from subprocess import call
from sys import stdout
from typing import Any, List, MutableMapping

from click import Context, Path, command, echo, group, option

from diagrams_net_automation import __version__

DRAW_IO = "/Applications/draw.io.app/Contents/MacOS/draw.io"

CACHE_FILE = ".diagrams.net.json"

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
@option("--width", "-w", type=int, multiple=True, default=())
@main_group.command()
def convert_diagrams(
    input_directory: str, output_directory: str, draw_io: str, width: List[int]
) -> None:
    """
    Converts Draw.io files to PDF and PNG.
    """
    input_directory_path = pathlib_Path(input_directory)
    output_directory_path = pathlib_Path(output_directory)
    _setup_output_directory(output_directory_path)
    cache_file = input_directory_path.joinpath(CACHE_FILE)
    content = _load_cache(cache_file)
    files = list(input_directory_path.iterdir())
    files = [
        f
        for f in files
        if f.is_file()
        and (f.suffix.casefold() == ".xml" or f.suffix.casefold() == ".drawio")
    ]
    for file in files:
        _convert_file(content, draw_io, file, output_directory_path, width)
    with cache_file.open("w") as f_write:
        dump(content, f_write, indent=4)


def _convert_file(
    cache_content: MutableMapping[str, str],
    draw_io: str,
    file: pathlib_Path,
    output_directory_path: pathlib_Path,
    widths: List[int],
) -> None:
    file_hash = hash_file(file)
    if str(file) in cache_content.keys() and cache_content[str(file)] == file_hash:
        _LOGGER.info(f"The file {file} has not changed since the last conversion.")
        return
    new_pdf_file = output_directory_path.joinpath(file.stem + ".pdf")
    new_png_file = output_directory_path.joinpath(file.stem + ".png")
    new_jpg_file = output_directory_path.joinpath(file.stem + ".jpg")
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


def _load_cache(cache_file: pathlib_Path) -> MutableMapping[str, str]:
    content: MutableMapping[str, str]
    if cache_file.is_file():
        with cache_file.open() as f_read:
            content = load(f_read)
    else:
        content = {}
    return content


def _setup_output_directory(output_directory_path: pathlib_Path) -> None:
    if not output_directory_path.is_dir():
        output_directory_path.mkdir()


def hash_file(file: pathlib_Path) -> str:
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
    main_group()
