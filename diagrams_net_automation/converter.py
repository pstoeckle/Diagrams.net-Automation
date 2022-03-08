"""
Converter module.
"""
from json import dumps, loads
from logging import getLogger
from pathlib import Path
from subprocess import call
from typing import MutableMapping, Sequence

from diagrams_net_automation.utils import hash_file
from typer import echo

_LOGGER = getLogger(__name__)


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

    def clear_cache(self) -> None:
        """
        Clears the current cache.
        """
        self._cache = {}

    def update_cache_file(self) -> None:
        """
        Store the current cache in the cache file.
        """
        self.cache_file.write_text(dumps(self._cache))
