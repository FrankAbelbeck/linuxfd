# linuxfd: Python interface for the Linux system calls eventfd/signalfd/timerfd

Copyright (C) 2014-2020 Frank Abelbeck <frank.abelbeck@googlemail.com>

License: LGPL-3

## Platform

Linux (kernel version >= 2.6.27); requires activated kernel options
CONFIG_TIMERFD, CONFIG_SIGNALFD, CONFIG_EVENTFD and CONFIG_INOTIFY_USER as well
as a recent version of the GNU C Library.

## Installation

An ebuild for Gentoo Linux is provided with this package. On any
other Linux system this package might be installed using the usual distutils way:
```bash
python setup.py install
```

## Usage

After installation a well documented new python module named "linuxfd"
is available.

## Changelog

 * **2020-12-01:** adapted to current Abelbeck coding standard

 * **2017-03-02:** merged changes proposed by robagar (close file descriptors only once)

 * **2016-09-27:** revised code base; new inotify event string translation method,
    buffer allocation via posix_memalign, fix of inotify_event->name handling,
    compiler now uses -Wall

 * **2016-09-26:** fixed variable init problem, added support for GIT portage version

 * **2016-09-25:** added inotify support; v1.4.1: removed small but important typo
 
 * **2016-07-23:** fixed float <-> timespec conversion issues; v1.2 suffered
   from a type but pypi would not let me replace the source tar ball
 
 * **2016-07-06:** merged changes proposed by palaviv (make linuxfd thread-safe)

 * **2014-01-22:** inital commit
