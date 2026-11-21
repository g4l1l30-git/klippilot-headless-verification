import sys
def main():
    import os,base64,hashlib,pathlib,zipfile
    data=base64.b64decode(''.join(os.environ['KLP_ZIP_'+str(i)] for i in range(5)),validate=True)
    assert hashlib.sha256(data).hexdigest()=='458fc69686c690fc880f8e6718bf7bf32f35c3be9e29d1ddfe87fba0238c0bf5'
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
