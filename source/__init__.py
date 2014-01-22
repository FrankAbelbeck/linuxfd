#!/usr/bin/env python
"""linuxfd: Python interface for the Linux system calls eventfd/signalfd/timerfd
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

# import helper modules for the syscalls and constants
import linuxfd.eventfd_c
import linuxfd.signalfd_c
import linuxfd.timerfd_c

# modules used for raising own OSError 
import errno,os


class eventfd:
	"""Class to manage a file descriptor for event notification.

An event file descriptor is created, which represents a kernel-managed counter.
Reading and writing this file increments/decrements/resets this counter. As the
file is pollable via select/poll/epoll it can be used as event notification in
asynchronous I/O algorithms."""
	
	def __init__(self,initval=0,semaphore=False,nonBlocking=False,closeOnExec=False):
		"""Constructor: Initialise an event file descriptor. The descriptor itself can be
retrieved via the fileno() method.

The counter is set to 'initval', an integer in the range [0,2**64-2].

Every value written to the file will be added to this initial value.

If 'semaphore' is True, this event file will act like a counting semaphore and
every reading operation will decrease the counter by one and return 1.
Otherwise every reading operation will return the last counter value and reset
the counter to zero.

Any reading operation on this event file will either fail with error EAGAIN (if
'nonBlocking' is set to True) or block if the current counter value is zero.

If 'closeOnExec' is True, the close-on-exec flag for this event file descriptor
is set. This can be useful in multithreaded programs to close a parent's file
descriptors when a child takes control via exec(). Please refer to the
documentation on exec() for further details."""
		self.is_nonBlocking = bool(nonBlocking)
		self.is_closeOnExec = bool(closeOnExec)
		self.is_semaphore   = bool(semaphore)
		flags = 0
		if self.is_nonBlocking: flags |= eventfd_c.EFD_NONBLOCK
		if self.is_closeOnExec: flags |= eventfd_c.EFD_CLOEXEC
		if self.is_semaphore:   flags |= eventfd_c.EFD_SEMAPHORE
		try:
			# convert initval to an integer and clip it to uint (assuming 32 bit)
			initval = min(max(int(initval),0),0xffffffff)
		except:
			# something went wrong: raise EINVAL (like providing wrong flags)
			raise OSError(errno.EINVAL,os.strerror(errno.EINVAL))
		self.fd = eventfd_c.eventfd(initval,flags)
	
	def __del__(self):
		"""Destructor: Close the file descriptor."""
		try:    os.close(self.fd)
		except: pass
	
	def fileno(self):
		"""Return the file descriptor of this event file object."""
		return self.fd
	
	def read(self):
		"""Read the event file and return its value.

If this file acts like a counting semaphore, the counter's value is decreased by
one and 1 is returned. Otherwise the current counter value is returned and the
counter value is reset to zero.

If the counter value is zero, this method either blocks or fails with error
EAGAIN if set to non-blocking behaviour."""
		return eventfd_c.eventfd_read(self.fd)
	
	def write(self,value=1):
		"""Write a value to the event file. The value is added to the counter.
No value is returned."""
		try:
			# convert value to an integer and clip it to uint64
			value = min(max(int(value),0),0xfffffffffffffffe)
		except:
			# something went wrong: raise EINVAL (like providing wrong flags)
			raise OSError(errno.EINVAL,os.strerror(errno.EINVAL))
		eventfd_c.eventfd_write(self.fd,value)
	
	def isSemaphore(self):
		"""Return True if this event file has semaphore properties."""
		return self.is_semaphore
	
	def isNonBlocking(self):
		"""Return True if this event file does not block when no data is available."""
		return self.is_nonBlocking
	
	def isCloseOnExec(self):
		"""Return True if the close-on-exec flag is set."""
		return self.is_closeOnExec


class signalfd:
	"""Class to manage a file descriptor for signal notification.

A signal file descriptor is created, which accepts signals targeted at the
caller and becomes readable if triggered. Reading this file returns the pending
signals for the process. As the file is pollable via select/poll/epoll it can be
used as an alternative to the usual signal handlers."""
	
	def __init__(self,signalset,nonBlocking=False,closeOnExec=False):
		"""Constructor: Initialise a signal file descriptor. The descriptor itself can be
retrieved via the fileno() method.

'signalset' is expected to be a set of valid signal numbers. Please refer to the
'signal' module for valid constants like SIGTERM.

Every value written to the file will be added to this initial value.

Any reading operation on this event file will either fail with error EAGAIN (if
'nonBlocking' is set to True) or block if currently no signals are pending.

If 'closeOnExec' is True, the close-on-exec flag for this event file descriptor
is set. This can be useful in multithreaded programs to close a parent's file
descriptors when a child takes control via exec(). Please refer to the
documentation on exec() for further details."""
		self.is_nonBlocking = bool(nonBlocking)
		self.is_closeOnExec = bool(closeOnExec)
		flags = 0
		if self.is_nonBlocking: flags |= signalfd_c.SFD_NONBLOCK
		if self.is_closeOnExec: flags |= signalfd_c.SFD_CLOEXEC
		try:
			# evaluate signal set
			self.signalset = tuple([int(i) for i in set(signalset)])
		except:
			# something went wrong: raise EINVAL (like providing wrong flags)
			raise OSError(errno.EINVAL,os.strerror(errno.EINVAL))
		self.fd = signalfd_c.signalfd(-1,self.signalset,flags)
	
	def __del__(self):
		"""Destructor: Close the file descriptor."""
		try:    os.close(self.fd)
		except: pass
	
	def fileno(self):
		"""Return the file descriptor of this event file object."""
		return self.fd
	
	def modify(self,signalset,nonBlocking=None,closeOnExec=None):
		"""Modify the signal set guarded by this signal file object.

Both blocking behaviour and close-on-exec can be set. If these arguments are
left set to None, the previously defined behaviour is kept."""
		if nonBlocking != None: self.is_nonBlocking = bool(nonBlocking)
		if closeOnExec != None: self.is_closeOnExec = bool(closeOnExec)
		flags = 0
		if self.is_nonBlocking: flags |= signalfd_c.SFD_NONBLOCK
		if self.is_closeOnExec: flags |= signalfd_c.SFD_CLOEXEC
		try:
			self.signalset = tuple([int(i) for i in set(signalset)])
		except:
			# something went wrong: raise EINVAL (like providing wrong flags)
			raise OSError(errno.EINVAL,os.strerror(errno.EINVAL))
		self.fd = signalfd_c.signalfd(self.fd,self.signalset,flags)
	
	def read(self):
		"""Read the signal file and return a dictionary holding information on
the recently received signal. In addition, the signal is consumed, so that it is
no longer pending for the process.

The returned dictionaries have the following structure according to signalfd(2):
{
   "signo":   int # Signal number
   "errno":   int # Error number (unused)
   "code":    int # Signal code
   "pid":     int # PID of sender
   "uid":     int # Real UID of sender
   "fd":      int # File descriptor (SIGIO)
   "tid":     int # Kernel timer ID (POSIX timers)
   "band":    int # Band event (SIGIO)
   "overrun": int # POSIX timer overrun count
   "trapno":  int # Trap number that caused signal
   "status":  int # Exit status or signal (SIGCHLD)
   "int":     int # Integer sent by sigqueue(3)
   "ptr":     int # Pointer sent by sigqueue(3)
   "utime":   int # User CPU time consumed (SIGCHLD)
   "stime":   int # System CPU time consumed (SIGCHLD)
   "addr":    int # Address that generated this signal (hardware-generated?)
}

If multiple signals got caught, multiple calls to read are necessary until all
pending signals are consumed. When there are no signals pending, this method
either blocks or fails with error EAGAIN if in non-blocking mode."""
		return signalfd_c.signalfd_read(self.fd)

	def signals(self):
		"""Return the set of guarded signal numbers."""
		return self.signalset
	
	def isNonBlocking(self):
		"""Return True if this event file does not block when no data is available."""
		return self.is_nonBlocking
	
	def isCloseOnExec(self):
		"""Return True if the close-on-exec flag is set."""
		return self.is_closeOnExec


class timerfd:
	"""Class to manage a file descriptor for timer notification.

A timer file descriptor is created, which represents a timer and becomes
readable if this timer expires. Reading this file returns the number of
expirations that have occurred since the last read operation."""
	
	def __init__(self,rtc=False,nonBlocking=False,closeOnExec=False):
		"""Constructor: Initialise a timer file descriptor. The descriptor itself can be
retrieved via the fileno() method.

If 'rtc' is True, this timer will access the system-wide realtime clock for time
measurement. Otherwise a monotonic timed counter will be used. While the RTC can
be changed by the SysAdmin and thus might exhibit discontinuous jumps, the
monotonic clock is only affected through incremental adjustments by adjtime(3)
and NTP.

Any reading operation on this timer file will either fail with error EAGAIN (if
'nonBlocking' is set to True) or block if the timer does not have expired yet.

If 'closeOnExec' is True, the close-on-exec flag for this event file descriptor
is set. This can be useful in multithreaded programs to close a parent's file
descriptors when a child takes control via exec(). Please refer to the
documentation on exec() for further details."""
		self.is_rtc         = bool(rtc)
		self.is_nonBlocking = bool(nonBlocking)
		self.is_closeOnExec = bool(closeOnExec)
		if self.is_rtc:
			clockid = timerfd_c.CLOCK_REALTIME
		else:
			clockid = timerfd_c.CLOCK_MONOTONIC
		flags = 0
		if self.is_nonBlocking: flags |= timerfd_c.TFD_NONBLOCK
		if self.is_closeOnExec: flags |= timerfd_c.TFD_CLOEXEC
		self.fd = timerfd_c.timerfd_create(clockid,flags)
	
	def __del__(self):
		"""Destructor: Close the file descriptor."""
		try:    os.close(self.fd)
		except: pass
	
	def fileno(self):
		"""Return the file descriptor of this event file object."""
		return self.fd
	
	def gettime(self):
		"""Return a tuple (value,interval) with the current timer setting.

The float variable 'value' specifies the amount of time in seconds until the
timer will expire. If it is zero the timer is disabled. This time value is
always a relative value.

The period in seconds of a periodically expiring timer is given in the float
variable 'interval'. If this is zero, the timer will expire just once, after
'value' seconds."""
		return timerfd_c.timerfd_gettime(self.fd)
	
	def settime(self,value=0,interval=0,absolute=False):
		"""Start or stop the timer.

Initial expiration time is specified in seconds with the float argument 'value'.

If the timer should periodically expire after its first expiration, the float
argument 'interval' has to be set to the desired amount of seconds.

If 'absolute' is True, an absolute timer is started. In this case value is
interpreted as an absolute value the clock has to reach. In case of a RTC source
this is the UNIX time of the desired point of time.

This method returns the old timer setting as a float-tuple (interval,value)."""
		if bool(absolute):
			flags = timerfd_c.TFD_TIMER_ABSTIME
		else:
			flags = 0
		return timerfd_c.timerfd_settime(self.fd,flags,value,interval)
	
	def read(self):
		"""Read the timer file and return an integer denoting the number of
expirations since the last reading operation.

If the timer has not expired yet, this method will either block or fail with
error EAGAIN if in non-blocking mode."""
		return timerfd_c.timerfd_read(self.fd)
	
	def isRTC(self):
		"""Return True if this timer uses the system-wide realtime clock.
If this returns false, a monotonic clock source is used."""
		return self.is_rtc
	
	def isNonBlocking(self):
		"""Return True if this event file does not block when no data is available."""
		return self.is_nonBlocking
	
	def isCloseOnExec(self):
		"""Return True if the close-on-exec flag is set."""
		return self.is_closeOnExec


