#!/usr/bin/env python
r"""This file is part of linuxfd (Python wrapper for eventfd/signalfd/timerfd)
Copyright (C) 2017 Roy O'Young <roy2220@outlook.com>

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

import platform


def get():
    a, b, c = (int(x) for x in platform.release().split("-")[0].split("."))
    return a << 16 | b << 8 | c


def make(a, b, c):
    return a << 16 | b << 8 | c
