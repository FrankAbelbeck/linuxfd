#!/usr/bin/env python
"""This file is part of linuxfd (Python wrapper for eventfd/signalfd/timerfd)
Copyright (C) 2014 Frank Abelbeck <frank.abelbeck@googlemail.com>

linuxfd is free software: you can redistribute it and/or modify it under the
terms of the GNU Lesser General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your option)
any later version.

linuxfd is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with linuxfd.  If not, see <http://www.gnu.org/licenses/>.

Written in Python V3."""

import linuxfd,signal,select,time

# create special file objects
efd = linuxfd.eventfd(initval=0,nonBlocking=True)
sfd = linuxfd.signalfd(signalset={signal.SIGINT},nonBlocking=True)
tfd = linuxfd.timerfd(rtc=True,nonBlocking=True)

# program timer and mask SIGINT
tfd.settime(3,3)
signal.pthread_sigmask(signal.SIG_SETMASK,{signal.SIGINT})

# create epoll instance and register special files
epl = select.epoll()
epl.register(efd.fileno(),select.EPOLLIN)
epl.register(sfd.fileno(),select.EPOLLIN)
epl.register(tfd.fileno(),select.EPOLLIN)

# start main loop
isrunning=True
print("{0:.3f}: Hello!".format(time.time()))
while isrunning:
	# block until epoll detects changes in the registered files
	events = epl.poll(-1)
	t = time.time()
	# iterate over occurred events
	for fd,event in events:
		if fd == efd.fileno() and event & select.EPOLLIN:
			# event file descriptor readable: read and exit loop
			print("{0:.3f}: event file received update, exiting...".format(t))
			efd.read()
			isrunning = False
		elif fd == sfd.fileno() and event & select.EPOLLIN:
			# signal file descriptor readable: write to event file
			siginfo = sfd.read()
			if siginfo["signo"] == signal.SIGINT:
				print("{0:.3f}: SIGINT received, notifying event file".format(t))
				efd.write(1)
		elif fd == tfd.fileno() and event & select.EPOLLIN:
			# timer file descriptor readable: display that timer has expired
			print("{0:.3f}: timer has expired".format(t))
			tfd.read()
print("{0:.3f}: Goodbye!".format(time.time()))
