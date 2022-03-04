"""
Convert.
"""
from hashlib import sha3_256
from itertools import chain
from json import dumps, loads
from logging import INFO, basicConfig, getLogger
from pathlib import Path
from subprocess import call
from typing import List, MutableMapping, Sequence

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


class Converter(object):
    """
    Converts Draw.io files.
    """

    draw_io: Path
    cache_file: Path
    output_directory: Path
    widths: Sequence[int]
    create_png: bool
    create_jpg: bool
    skip_pdf: bool

    _cache: MutableMapping[str, str]

    def __init__(
        self,
        draw_io: Path,
        cache_file: Path,
        output_directory: Path,
        widths: Sequence[int],
        create_png: bool,
        create_jpg: bool,
        skip_pdf: bool,
    ) -> None:
        self.draw_io = draw_io
        self.cache_file = cache_file
        self.output_directory = output_directory
        self.widths = widths
        self.create_jpg = create_jpg
        self.create_png = create_png
        self.skip_pdf = skip_pdf
        if self.cache_file.is_file():
            self._cache = loads(cache_file.read_text())
        else:
            self._cache = {}

    def convert_file(
        self,
        file: Path,
    ) -> None:
        """
        Convert a file.
        """
        file_hash = hash_file(file)
        if str(file) in self._cache.keys() and self._cache[str(file)] == file_hash:
            _LOGGER.info(f"The file {file} has not changed since the last conversion.")
            return
        echo(f"Converting {file}")
        output_subdir = self.output_directory.joinpath(file.parent)
        if not output_subdir.is_dir():
            output_subdir.mkdir(parents=True)
        new_pdf_file = output_subdir.joinpath(file.stem + ".pdf")
        new_png_file = output_subdir.joinpath(file.stem + ".png")
        new_jpg_file = output_subdir.joinpath(file.stem + ".jpg")
        if self.skip_pdf:
            _LOGGER.info(f"PDF conversion skipped!")
        else:
            _LOGGER.info(f"Convert {file} to PDF")
            call(
                [
                    str(self.draw_io),
                    file,
                    "--export",
                    "--output",
                    new_pdf_file,
                    "--crop",
                ]
            )
        if self.create_png:
            _LOGGER.info(f"Convert {file} to PNG")
            call(
                [
                    str(self.draw_io),
                    file,
                    "--export",
                    "--output",
                    new_png_file,
                    "--transparent",
                ]
            )
        else:
            _LOGGER.info(f"PNG conversion skipped!")
        if self.create_jpg:
            _LOGGER.info(f"Convert {file} to JPEG")
            call(
                [
                    str(self.draw_io),
                    file,
                    "--export",
                    "--output",
                    new_jpg_file,
                    "--transparent",
                ]
            )
        else:
            _LOGGER.info(f"JPG conversion skipped!")
        for width in self.widths:
            if self.create_png:
                _LOGGER.info(f"Convert {file} to PNG with width {width}")
                new_width_png_file = self.output_directory.joinpath(
                    f"{file.stem}_{width}.png"
                )
                call(
                    [
                        str(self.draw_io),
                        file,
                        "--export",
                        "--output",
                        new_width_png_file,
                        "--width",
                        str(width),
                        "--transparent",
                    ]
                )
            if self.create_jpg:
                _LOGGER.info(f"Convert {file} to JPEG with width {width}")
                new_width_jpg_file = self.output_directory.joinpath(
                    f"{file.stem}_{width}.jpg"
                )
                call(
                    [
                        str(self.draw_io),
                        file,
                        "--export",
                        "--output",
                        new_width_jpg_file,
                    ]
                )
        if self.create_jpg or self.create_png or not self.skip_pdf:
            self._cache[str(file)] = file_hash
        echo(f"Converting {file}: done!")

    def update_cache(self) -> None:
        """
        Store the current cache in the cache file.
        """
        self.cache_file.write_text(dumps(self._cache))


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
