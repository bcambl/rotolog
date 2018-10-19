#!/usr/bin/env python

import os
import sys
import datetime
import gzip
import shutil

DEBUG = False

# full path to log directory
LOG_PATH = "/tmp/testdata"
# max days before file is compressed
COMPRESSION_AGE = 15
# max days to keep compressed archives
ARCHIVE_AGE = 31
# file extensions to skip compression
SKIP_EXTENSIONS = ['.gz']


def remove_empty_logs(path):
    """ remove empty log files """
    print("remove empty log files...")
    file_count = 0
    for root, _, files in os.walk(path):
        for fname in files:
            filename = os.path.join(root, fname)
            if os.stat(filename).st_size == 0:
                if DEBUG:
                    print("removing: %s" % filename)
                else:
                    try:
                        os.remove(filename)
                        file_count += 1
                    except OSError as err:
                        sys.exit(err)
    print("%d empty logs removed" % file_count)


def compress_old_logs(path):
    """ compress logs based on COMPRESSION_AGE """
    print("compressing logs older than %d days..." % COMPRESSION_AGE)
    current_date = datetime.datetime.now()
    file_count = 0
    for root, _, files in os.walk(path):
        for fname in files:
            filename = os.path.join(root, fname)
            _, file_extension = os.path.splitext(filename)
            if file_extension in SKIP_EXTENSIONS:
                continue
            file_mtime = os.stat(filename).st_mtime
            file_mtime_date = datetime.datetime.fromtimestamp(file_mtime)
            file_age = current_date - file_mtime_date
            if file_age.days >= COMPRESSION_AGE:
                if DEBUG:
                    print("compressing: %s" % filename)
                else:
                    try:
                        with open(filename, 'rb') as fin:
                            with gzip.open('%s.gz' % filename, 'wb') as fout:
                                shutil.copyfileobj(fin, fout)
                        os.remove(filename)
                        file_count += 1
                    except IOError as err:
                        sys.exit(err)
    print("%d logs compressed" % file_count)


def expire_archived_logs(path):
    """ expire archived logs based on ARCHIVE_AGE """
    print("expiring archives older than %d days..." % ARCHIVE_AGE)
    current_date = datetime.datetime.now()
    file_count = 0
    for root, _, files in os.walk(path):
        for fname in files:
            filename = os.path.join(root, fname)
            _, file_extension = os.path.splitext(filename)
            if file_extension != '.gz':
                continue
            file_mtime = os.stat(filename).st_mtime
            file_mtime_date = datetime.datetime.fromtimestamp(file_mtime)
            file_age = current_date - file_mtime_date
            if file_age.days >= ARCHIVE_AGE:
                if DEBUG:
                    print("expiring archive: %s" % filename)
                else:
                    try:
                        os.remove(filename)
                        file_count += 1
                    except OSError as err:
                        sys.exit(err)
    print("%d archived logs expired" % file_count)


def main():
    """ main script """
    remove_empty_logs(LOG_PATH)
    compress_old_logs(LOG_PATH)
    expire_archived_logs(LOG_PATH)


if __name__ == '__main__':
    main()
