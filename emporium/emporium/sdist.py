"""
Tools for working with sdists

Likely to be highly crude, and should be replaced with something more appropriate sooner!
"""

import io
import pathlib
import tarfile
import tempfile


def extract_setuppy(sdist_content, package_name, version) -> bytes:
    # Yay tarfile supports autodetected compression!
    # Still assuming it's a tarfile, but I bet most sdists are...

    fakefile = io.BytesIO(sdist_content)

    tf = tarfile.open(fileobj=fakefile)

    with tempfile.TemporaryDirectory() as tempdir_path:
        tf.extractall(tempdir_path)
        p = pathlib.Path("%s/%s-%s/setup.py" % (tempdir_path, package_name, version))
        return p.read_bytes()
