""" Additions to python's shutil standard library """


import fnmatch
import glob
import os
import shutil
import subprocess
import time
import zipfile


class SvnError(Exception):
    pass


def svn_checkout(remote, local):
    """ Check out repository 'remote' to 'local' path """
    if subprocess.call(['svn', 'co', '-q', remote, local]) != 0:
        raise SvnError('Error checking out' + remote)


def find_files(path, incl_patterns, excl_patterns=[], search_subdirs=False):
    """ A more flexible way of finding a group of files than glob.glob().
        Return a list of files under the given path that match
        any of the include patterns, and none of the exclude patterns.

        Optionally searches all subdirectories.
    """
    # convert patterns to lists if they are not already
    if type(incl_patterns) is not list:
        incl_patterns = [incl_patterns]
    if type(excl_patterns) is not list:
        excl_patterns = [excl_patterns]

    # find all filenames that match any include patterns
    matches = []
    num_dirs_searched = 0
    for root, dirnames, filenames in os.walk(path):
        if not search_subdirs and num_dirs_searched >= 1:
            break
        else:
            for filename in filenames:
                for pattern in incl_patterns:
                    if fnmatch.fnmatch(filename, pattern):
                        matches.append(os.path.join(root, filename))
                        break
            num_dirs_searched += 1

    # remove all filenames that match any exclude patterns
    def isExcluded(filename):
        for pattern in excl_patterns:
            if fnmatch.fnmatch(filename, pattern):
                return True
        return False

    return [x for x in matches if not isExcluded(os.path.basename(x))]


def unzip(archive_path, dest=None):
    """ Extract the given zip archive, to present dir if no dest is given """
    archive = zipfile.ZipFile(archive_path, 'r')
    if dest is not None:
        archive.extractall(dest)
    else:
        archive.extractall()


def zipdir(path, dest):
    """ Zip all contents of path to dest """
    zipf = zipfile.ZipFile(dest, 'w', compression=zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(path):
        for file in files:
            zipf.write(os.path.join(root, file))
    zipf.close()


def mkdirs(path):
    """ Create the given directory if it doesn't already exist """
    if not os.path.exists(path):
        os.makedirs(path)


def copy_glob(pattern, dest):
    """ Copy files by unix path pattern to the destination dir.
        dest must be an existing directory, also if the pattern
        returns directories, you're in trouble
    """
    assert(os.path.isdir(dest))
    items = glob.glob(pattern)
    if len(items) == 0:
        print 'warning: no files found in copy_glob. pattern: ' + pattern
    else:
        for item in items:
            shutil.copy(item, dest)


def rmtree(path):
    """ A wrapper for shutil.rmtree() since it sometimes fails
        due to OS file handling delays (?). At least on windows it does.
    """
    max_attempts = 3
    attempts = 0
    try:
        shutil.rmtree(path)
        attempts += 1
    except:
        if attempts < max_attempts:
            time.sleep(0.5)
        else:
            raise Exception('rmtree failed after' + str(max_attempts) + 'attempts')

    # sleep after removing tree as OS delays can cause errors
    # shortly after this function
    time.sleep(0.5)


if __name__ == '__main__':
    print find_files('..', ['*.py'], search_subdirs=True)
