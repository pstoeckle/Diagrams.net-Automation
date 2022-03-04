# Diagrams.net Automation

[[_TOC_]]

## Usage

```bash
Usage: diagrams-net-automation [OPTIONS] COMMAND [ARGS]...

  :return:

Options:
  --version                       Version
  --help                          Show this message and exit.

Commands:
  convert-diagrams  Converts Draw.io files to PDF and PNG.
```

### Convert Diagrams

```bash
Usage: diagrams-net-automation convert-diagrams [OPTIONS]

  Converts Draw.io files to PDF and PNG.

Options:
  -d, --input-directory DIRECTORY
                                  Input directory with the diagrams.net files.
                                  [default: .]
  -o, --output-directory DIRECTORY
                                  The output directory where the PDF, JPG, or
                                  PNG files should be stored.  [default: dist]
  -D, --draw-io FILE              The diagrams.net executable.  [default: /App
                                  lications/draw.io.app/Contents/MacOS/draw.io
                                  ]
  -w, --width INTEGER             If a width is passed, we will generate a PNG
                                  and/or JPG with this width.
  -X, --include-xml               Convert also .xml files, not only .drawio
                                  files.
  -P, --generate-png              Generate PNG files.
  -J, --generate-jpg              Generate JPG files.
  -S, --skip-pdf-generation       If this flag is set, we will not generate
                                  PDF files.
  -I, --ignore-cache              If this flag is passed, we will ignore
                                  anything in the current cache file. In the
                                  end, we will overwrite the current cache
                                  file.
```
