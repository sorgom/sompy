from os import walk, remove
from os.path import relpath, join, isdir, isfile, getmtime
from shutil import rmtree, copytree, copyfile, copystat

def rpath(dir:str, base:str):
    "relative path without ."
    rp = relpath(dir, base)
    return '' if rp == '.' else rp

def cpfile(src:str, dst:str):
    "copy file with attributes"
    copyfile(src, dst)
    copystat(src, dst)


def wlist(dir:str):
    "list relative non empty directories with files and subdirs"
    return [ [rpath(root, dir), files] for root, dirs, files in walk(dir) if files or dirs]

def back(src:str, dst:str):
    if not (isdir(src) and isdir(dst)):
        print('skip:', src, dst)
        return
    ls = wlist(src)
    lt = wlist(dst)
    ds = { rdir:files for rdir, files in ls }
    dt = { rdir:files for rdir, files in lt }

    print('src:', len(ds))
    print('dst:', len(dt))

    # removal in target
    ndt = list(range(0, len(len(lt))))
    ndt.reverse

    print(ndt)
    exit()

    for dir, tfiles in lt:
        tdir = join(dst, dir)
        # already removed?
        if not isdir(tdir): continue
        sfiles = ds.get(dir, None)
        # non source folder
        if sfiles is None:
            print('rmtree:', tdir)
            rmtree(tdir)
            continue
        for file in tfiles:
            tfile = join(tdir, file)
            # non source file
            if not file in sfiles:
                print('remove (nx):', tfile)
                remove(tfile)
                continue
            # source is newer
            mtt = getmtime(tfile)
            mts = getmtime(join(src, dir, file))
            if mts > mtt:
                print('remove (mt):', tfile)
                remove(tfile)

    # copy from source to target
    for dir, sfiles in ls:
        tdir = join(dst, dir)
        sdir = join(src, dir)
        if isfile(tdir):
            print('remove (if):', tdir)
            remove(tdir)

        if not isdir(tdir):
            print('copytree', sdir, tdir)
            copytree(sdir, tdir)
            continue
        for file in sfiles:
            sfile = join(sdir, file)
            tfile = join(tdir, file)
            if isdir(tfile):
                print('rmtree (id):', tfile)
                rmtree(tfile)
            if not isfile(tfile):
                print('copyfile:', sfile, tfile)
                cpfile(sfile, tfile)


if __name__ == '__main__':
    back('C:/users/MS/data', 'M:/tmp_backup_test')
