import sys
def main():
    import os,base64,hashlib,pathlib,zipfile
    data=base64.b64decode(''.join(os.environ['KLP_ZIP_'+str(i)] for i in range(5)),validate=True)
    assert hashlib.sha256(data).hexdigest()=='6f9e39e0b9ba4c0f6bb9f760211bc50c042edc356d71a0101e5b1ed8165764c0'
    pathlib.Path('buyer.zip').write_bytes(data)
    with zipfile.ZipFile('buyer.zip') as archive:
        assert all(not pathlib.PurePosixPath(n).is_absolute() and '..' not in pathlib.PurePosixPath(n).parts for n in archive.namelist())
        archive.extractall('buyer')
    print('PACKAGE_INTEGRITY_PASS')
try:
    main()
except Exception as error:
    print('HARNESS_FAILED='+type(error).__name__)
    sys.exit(1)
