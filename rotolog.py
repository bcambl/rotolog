#!/usr/bin/env python

import os
import sys
import datetime
import gzip
import shutil
import argparse

DEBUG = False

# default log directory path
DEFAULT_LOG_PATH = "/tmp/testdata"
# default max days before file is compressed
DEFAULT_COMPRESSION_AGE = 15
# default max days to keep compressed archives
DEFAULT_ARCHIVE_AGE = 31

# file extensions to skip compression
SKIP_EXTENSIONS = ['.gz']


class RotoLog:

    def __init__(self):
        self.debug = DEBUG
        self.log_path = DEFAULT_LOG_PATH
        self.compression_age = DEFAULT_COMPRESSION_AGE
        self.archive_age = DEFAULT_ARCHIVE_AGE
        self.skip_extentions = SKIP_EXTENSIONS

    def remove_empty_logs(self):
        """ remove empty log files """
        print("remove empty log files...")
        file_count = 0
        for root, _, files in os.walk(self.log_path):
            for fname in files:
                filename = os.path.join(root, fname)
                if os.stat(filename).st_size == 0:
                    if self.debug:
                        print("removing: %s" % filename)
                    else:
                        try:
                            os.remove(filename)
                            file_count += 1
                        except OSError as err:
                            sys.exit(err)
        print("%d empty logs removed" % file_count)

    def compress_old_logs(self):
        """ compress logs based on COMPRESSION_AGE """
        print("compressing logs older than %d days..." % self.compression_age)
        current_date = datetime.datetime.now()
        file_count = 0
        for root, _, files in os.walk(self.log_path):
            for fname in files:
                filename = os.path.join(root, fname)
                _, file_extension = os.path.splitext(filename)
                if file_extension in self.skip_extentions:
                    continue
                file_mtime = os.stat(filename).st_mtime
                file_mtime_date = datetime.datetime.fromtimestamp(file_mtime)
                file_age = current_date - file_mtime_date
                if file_age.days >= self.compression_age:
                    if self.debug:
                        print("compressing: %s" % filename)
                    else:
                        try:
                            with open(filename, 'rb') as fin:
                                gz_file = '%s.gz' % filename
                                with gzip.open(gz_file, 'wb') as fout:
                                    shutil.copyfileobj(fin, fout)
                            os.remove(filename)
                            file_count += 1
                        except IOError as err:
                            sys.exit(err)
        print("%d logs compressed" % file_count)

    def expire_archived_logs(self):
        """ expire archived logs based on ARCHIVE_AGE """
        print("expiring archives older than %d days..." % self.archive_age)
        current_date = datetime.datetime.now()
        file_count = 0
        for root, _, files in os.walk(self.log_path):
            for fname in files:
                filename = os.path.join(root, fname)
                _, file_extension = os.path.splitext(filename)
                if file_extension != '.gz':
                    continue
                file_mtime = os.stat(filename).st_mtime
                file_mtime_date = datetime.datetime.fromtimestamp(file_mtime)
                file_age = current_date - file_mtime_date
                if file_age.days >= self.archive_age:
                    if self.debug:
                        print("expiring archive: %s" % filename)
                    else:
                        try:
                            os.remove(filename)
                            file_count += 1
                        except OSError as err:
                            sys.exit(err)
        print("%d archived logs expired" % file_count)

    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--debug", action="store_true",
                            help="enable debug/noop")
        parser.add_argument("-p", "--path", type=str,
                            help="path to log directory")
        parser.add_argument("-c", "--compression", type=int,
                            help="log age in days to compress/archive")
        parser.add_argument("-a", "--archive", type=int,
                            help="archive age when archives should be deleted")
        args = parser.parse_args()
        if args.path:
            self.log_path = args.path
        if not os.path.isdir(self.log_path):
            print("directory %s does not exists" % self.log_path)
            sys.exit(1)
        if not os.listdir(self.log_path):
            print("log directory %s is empty" % self.log_path)
            sys.exit(0)
        if args.compression:
            self.compression_age = args.compression
        if args.archive:
            self.archive_age = args.archive
        if args.debug:
            self.debug = args.debug
        if self.debug:
            print("** DEBUG/NOOP ENABLED **")
            print("log_path: %s" % self.log_path)
            print("compression_age: %d" % self.compression_age)
            print("archive_age: %d" % self.archive_age)


def main():
    """ main script """
    L = RotoLog()
    L.parse_args()
    L.remove_empty_logs()
    L.compress_old_logs()
    L.expire_archived_logs()


if __name__ == '__main__':
    main()
