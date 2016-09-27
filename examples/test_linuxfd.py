#!/usr/bin/env python
"""This file is part of linuxfd (Python wrapper for eventfd/signalfd/timerfd)
Copyright (C) 2016 Frank Abelbeck <frank.abelbeck@googlemail.com>

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

import linuxfd,signal,pprint,time,tempfile,os

##
## test eventfd
##
#efd = linuxfd.eventfd(initval=0,nonBlocking=True)
#print("\ntesting eventfd (fd={})".format(efd.fileno()))
#for i in range(0,3):
	#print("   writing to sempahore")
	#efd.write()
#try:
	#while True:
		#value = efd.read()
		#print("   read '{}' from semaphore".format(value))
#except BlockingIOError:
	#print("   semaphore exhausted")

#print("\ntesting eventfd (fd={}, mode: counting)".format(efd.fileno()))
#efd = linuxfd.eventfd(initval=0,semaphore=True,nonBlocking=True)
#for i in range(0,3):
	#print("   writing to sempahore")
	#efd.write()
#try:
	#while True:
		#value = efd.read()
		#print("   read '{}' from semaphore".format(value))
#except BlockingIOError:
	#print("   semaphore exhausted")

##
## test signalfd
##
#sfd = linuxfd.signalfd(signalset={signal.SIGALRM})
#signal.pthread_sigmask(signal.SIG_SETMASK,{signal.SIGALRM})
#print("\ntesting signalfd (fd={}) with SIGALRM".format(sfd.fileno()))
#print("guarded signals = {}".format(sfd.signals()))
#print("starting alarm timer (3 seconds)")
#signal.alarm(3)
#value = sfd.read()
#print("received SIGALRM, signalfd.read() returned:")
#pprint.pprint(value)
#signal.alarm(0)

##
## test timerfd
##
#tfd = linuxfd.timerfd(rtc=True)
#print("\ntesting timerfd (fd={})".format(sfd.fileno()))
#print("   {:.2f}: setting timer (value=3,interval=1)".format(time.time()))
#tfd.settime(3,1)
#for i in range(0,3):
	#value = tfd.read()
	#print("   {:.2f}: received timer event".format(time.time()))
	#time.sleep(0.25)
	#print("   {:.2f}: timer will expire in {:.3f} seconds".format(time.time(),tfd.gettime()[0]))
#t = time.time()+5
#print("   {:.2f}: setting absolute timer (t={:.2f})".format(time.time(),t))
#tfd.settime(t,absolute=True)
#value = tfd.read()
#print("   {:.2f}: received timer event".format(time.time()))
#tfd.settime(0,0)

#
# test inotify
#
ifd = linuxfd.inotify(nonBlocking=True)
print("\ntesting inotify (fd={})".format(ifd.fileno()))
f,name = tempfile.mkstemp()
print("created temporary file '{}'".format(name))
ifd.add(name,linuxfd.IN_ALL_EVENTS)
print("inotify now guarding following files: {}; {}".format(ifd.watchedPaths(),ifd._wd))
print("writing to temporary file '{}'".format(name))
os.write(f,b"Test")
os.fsync(f)
os.lseek(f,0,os.SEEK_SET)
print("reading from temporary file '{}'".format(name))
print(os.read(f,1024))
print("closing and removing temporary file '{}'".format(name))
os.close(f)
os.remove(name)
time.sleep(5)
print("collecting inotify events:")
try:
	while True:
		events = ifd.read(1024)
		for event in events:
			print(event)
		for path,name,mask,cookie in events:
			print("   received event path='{}' name='{}' mask={} cookie={}".format(path,name,ifd.eventStrings(mask),cookie))
except BlockingIOError:
	print("inotify file descriptor exhausted")
