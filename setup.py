#!/usr/bin/env python
r"""This file is part of linuxfd (Python wrapper for eventfd/signalfd/timerfd)
Copyright (C) 2014-2016 Frank Abelbeck <frank.abelbeck@googlemail.com>

    linuxfd is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    linuxfd is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with linuxfd.  If not, see <http://www.gnu.org/licenses/>."""

from distutils.core import setup, Extension

eventfd_c  = Extension("eventfd_c",  sources = ["source/eventfd_c.c"])
signalfd_c = Extension("signalfd_c", sources = ["source/signalfd_c.c"])
timerfd_c  = Extension("timerfd_c",  sources = ["source/timerfd_c.c"])

longdescription = """linuxfd provides a Python interface for the Linux system calls 'eventfd',
'signalfd' and 'timerfd'."""

setup(
	name = "linuxfd",
	version = "1.1",
	description = "Python bindings for the Linux eventfd/signalfd/timerfd syscalls",
	long_description = longdescription,
	author = "Frank Abelbeck",
	author_email = "frank.abelbeck@googlemail.com",
	url = "https://abelbeck.wordpress.com",
	license = "LGPL",
	platforms = "Linux",
	package_dir = {"linuxfd":"source"},
	packages = ["linuxfd"],
	ext_package = "linuxfd",
	ext_modules = [eventfd_c,signalfd_c,timerfd_c]
)
