# This file is part of linuxfd (Python wrapper eventfd/signalfd/timerfd)
# Copyright (C) 2016 Frank Abelbeck <frank.abelbeck@googlemail.com>
#
#    linuxfd is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    linuxfd is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with linuxfd.  If not, see <http://www.gnu.org/licenses/>.

EAPI=7
PYTHON_COMPAT=( python3_{3..10} )

inherit distutils-r1 linux-info git-r3

DESCRIPTION="Python bindings for the Linux eventfd/signalfd/timerfd/inotify syscalls"
HOMEPAGE="https://www.github.com/abelbeck/linuxfd/ https://pypi.python.org/pypi/linuxfd/"
EGIT_REPO_URI="git://github.com/FrankAbelbeck/linuxfd.git"

LICENSE="LGPL-3"
SLOT="0"
KEYWORDS="amd64"
DOCS=( COPYING README.md )

CONFIG_CHECK="EVENTFD SIGNALFD TIMERFD INOTIFY_USER"
ERROR_EVENTFD="${PN} requires support for timerfd system calls (CONFIG_EVENTFD), being enabled in 'General setup -> Configure standard kernel features (expert users)'."
ERROR_SIGNALFD="${PN} requires support for signalfd system calls (CONFIG_SIGNALFD), being enabled in 'General setup -> Configure standard kernel features (expert users)'."
ERROR_TIMERFD="${PN} requires support for eventfd system calls (CONFIG_TIMERFD), being enabled in 'General setup -> Configure standard kernel features (expert users)'."
ERROR_INOTIFY_USER="${PN} requires support for inotify system calls (CONFIG_INOTIFY_USER), being enabled in 'File systems'."

pkg_setup() {
	linux-info_pkg_setup
}
