import os
import re
import shutil
import struct
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from subprocess import run


MELON_BIN = R"C:\Program Files (x86)\Melonbooks\melonbooksviewer\melonbooksviewer.exe"


def main(sourcefile, output, melon):
    if not Path(melon).exists():
        print('melonbooksviewer.exe not found. Please install it first or specify the path to it with -m option.')
        sys.exit(1)

    sourcefile = Path(sourcefile)
    if not sourcefile.exists():
        print('Source file not found.')
        sys.exit(1)
    print('Source file:', sourcefile)
    print('Total filesize: ', sourcefile.stat().st_size)

    temp_file = Path('temp.melon')

    with sourcefile.open('rb') as fi:
        # RIFF
        file_format = fi.read(4)
        assert file_format == b"RIFF"

        file_size_b = fi.read(4)
        (file_size,) = struct.unpack("<i", file_size_b)
        print('Actual file size:', file_size)

        # フォームタイプ
        form_type = fi.read(4)
        print('Form type:', form_type.decode(encoding='utf8', errors='ignore'))

        # META header
        header_meta = fi.read(4)
        assert header_meta == b"META"

        # META size
        meta_size_b = fi.read(4)  # 4
        (meta_size,) = struct.unpack("<i", meta_size_b)
        print('Meta size:', meta_size)

        # META data
        meta = fi.read(meta_size)
        print('Raw metadata:', meta.decode(encoding='utf8', errors='ignore'))

        # extract file type and title
        root = ET.fromstring(meta)
        file_type = root.find("file_type").text
        title = root.find("title").text or '(No title)'
        print('Title:', title)
        print('File type:', file_type)

        if meta_size % 2 != 0:
            padding = fi.read(1)
            assert padding == b"0"

        rest_of_file = fi.read()

        print('Modify file and save to temp.melon...')

        meta_new = re.sub(b"(?<=\<file_type\>)[^\<]+(?=\</file_type\>)", b"pdf", meta)
        meta_size_new = len(meta_new)
        assert meta_size_new == meta_size - len(file_type) + 3
        meta_size_new_b = struct.pack("<i", meta_size_new)

        # padding
        if meta_size_new % 2 != 0:
            meta_new += b"0"

        file_size_new = file_size - len(file_type) + 3
        file_size_new_b = struct.pack("<i", file_size_new)

        meta_size_new = meta_size - len(file_type) + 3
        meta_size_new_b = struct.pack("<i", meta_size_new)

        # generate the new file
        with temp_file.open('wb') as fo:
            fo.write(file_format)  # RIFF
            fo.write(file_size_new_b)
            fo.write(form_type)
            fo.write(header_meta)  # META
            fo.write(meta_size_new_b)
            fo.write(meta_new)
            fo.write(rest_of_file)

    if output:
        output_file = Path(output)
    else:
        output_file = sourcefile.with_name(sourcefile.stem + '_decoded' + '.' + file_type)
    run([melon, temp_file])
    print('Wait for 5 seconds...')
    time.sleep(5)
    print('Copy file...')
    shutil.copy2(Path(os.environ['TEMP']) / 'Melonbooks' / 'temporary.pdf', output_file)
    temp_file.unlink()

    print('Done! You can close the Melonbooks Viewer and/or PDF viewer now.')

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Decode melon file.')
    parser.add_argument('sourcefile', help='source file')
    parser.add_argument('--output', '-o', help='output file (default: {sourcefilename}_decoded.{ext})')
    parser.add_argument('--melon', '-m', default=MELON_BIN, help='path to melonbooksviewer.exe (default: {})'.format(MELON_BIN))

    args = parser.parse_args()

    main(args.sourcefile, args.output, args.melon)
