#!/usr/bin/env python

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
while isrunning:
	# block until epoll detects changes in the registered files
	events = epl.poll(-1)
	t = time.time()
	# iterate over occurred events
	for fd,event in events:
		if fd == efd.fileno() and event & select.EPOLLIN:
			# event file descriptor readable: read and exit loop
			print("\n[{0:.3f}] event file received update, exiting...".format(t),end="")
			efd.read()
			isrunning = False
		elif fd == sfd.fileno() and event & select.EPOLLIN:
			# signal file descriptor readable: write to event file
			siginfo = sfd.read()
			if siginfo["signo"] == signal.SIGINT:
				print("\n[{0:.3f}] SIGINT received, notifying event file".format(t),end="")
				efd.write(1)
		elif fd == tfd.fileno() and event & select.EPOLLIN:
			# timer file descriptor readable: display that timer has expired
			print("\n[{0:.3f}] timer expired".format(t),end="")
			tfd.read()
