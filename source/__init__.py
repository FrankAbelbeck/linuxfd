#!/usr/bin/env python
"""linuxfd: Python interface for the Linux system calls eventfd/signalfd/timerfd
Copyright (C) 2014-2016 Frank Abelbeck <frank.abelbeck@googlemail.com>

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
import linuxfd.inotify_c

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

If the current value of this event file is zero, any reading operation will
either fail with error EAGAIN (if "nonBlocking" is set to True) or will block.

Args:
   initval: an integer, range [0;2**64-2], defining an initial counter value.
   semaphore: a boolean; if True, this event file will act like a counting
              semaphore -- every reading operation will decrease the counter by
              one and returns 1; otherwise every reading operation will return
              the last counter value and reset the counter to zero.
   nonBlocking: a boolean.
   closeOnExec: a boolean; if True, the close-on-exec flag for this event file
                descriptor is set. This can be useful in multithreaded programs
                to close a parent's file descriptors when a child takes control
                via exec(). Please refer to the documentation on exec() for
                further details.

Raises:
   OSError.EINVAL: initval is out of bounds or unsupported value in flags.
   OSError.EMFILE: per-process limit on number of open file descriptors reached.
   OSError.ENFILE: system-wide limit on total number of open files reached.
   OSError.ENODEV: could not mount (internal) anonymous inode device.
   OSError.ENOMEM: insufficient memory to create a new eventfd file descriptor."""
		self._isNonBlocking = bool(nonBlocking)
		self._isCloseOnExec = bool(closeOnExec)
		self._isSemaphore   = bool(semaphore)
		flags = 0
		if self._isNonBlocking: flags |= eventfd_c.EFD_NONBLOCK
		if self._isCloseOnExec: flags |= eventfd_c.EFD_CLOEXEC
		if self._isSemaphore:   flags |= eventfd_c.EFD_SEMAPHORE
		try:
			# convert initval to an integer and clip it to uint (assuming 64 bit)
			initval = min(max(int(initval),0),0xfffffffffffffffe)
		except:
			# something went wrong: raise EINVAL (like providing wrong flags)
			raise OSError(errno.EINVAL,os.strerror(errno.EINVAL))
		self._fd = eventfd_c.eventfd(initval,flags)
	
	
	def __del__(self):
		"""Destructor: Close the file descriptor."""
		self.close()
	
	
	def close(self):
		"""Close the file descriptor."""
		try:    os.close(self._fd)
		except: pass
	
	
	def fileno(self):
		"""Return the file descriptor of this event file object.

Returns:
   An integer."""
		return self._fd
	
	
	def read(self):
		"""Read the event file and return its value.

If this file acts like a counting semaphore, the counter's value is decreased by
one and 1 is returned. Otherwise the current counter value is returned and the
counter value is reset to zero.

If the counter value is zero and this event file is set non-blocking, this
method will block until the counter value becomes non-zero

Returns:
   An integer.

Raises:
   OSError.EAGAIN: file is non-blocking and value is zero.
   OSError.EBADF: eventfd file descriptor already closed."""
		return eventfd_c.eventfd_read(self._fd)
	
	
	def write(self,value=1):
		"""Write a value to the event file. The value is added to the counter.
No value is returned. If the counter will reach its maximum value, the operation
will either block or raise OSError.EAGAIN (if set to non-blocking behaviour).

Args:
   value: an integer in range [0;2**64-2], defaults to one.

Raises:
   OSError.EINVAL: value is out of bounds.
   OSError.EAGAIN: maximum counter value reached and file is non-blocking.
   OSError.EBADF: eventfd file descriptor already closed."""
		try:
			# convert value to an integer and clip it to uint64
			value = min(max(int(value),0),0xfffffffffffffffe)
		except:
			# something went wrong: raise EINVAL (like providing wrong flags)
			raise OSError(errno.EINVAL,os.strerror(errno.EINVAL))
		eventfd_c.eventfd_write(self._fd,value)
	
	
	def isSemaphore(self):
		"""Return True if this event file has semaphore properties.

Returns:
   A boolean."""
		return self._isSemaphore
	
	
	def isNonBlocking(self):
		"""Return True if this event file does not block when no data is available.

Returns:
   A boolean."""
		return self._isNonBlocking
	
	
	def isCloseOnExec(self):
		"""Return True if the close-on-exec flag is set.

Returns:
   A boolean."""
		return self._isCloseOnExec



class signalfd:
	"""Class to manage a file descriptor for signal notification.

A signal file descriptor is created, which accepts signals targeted at the
caller and becomes readable if triggered. Reading this file returns the pending
signals for the process. As the file is pollable via select/poll/epoll it can be
used as an alternative to the usual signal handlers."""
	
	def __init__(self,signalset,nonBlocking=False,closeOnExec=False):
		"""Constructor: Initialise a signal file descriptor. The descriptor itself can be
retrieved via the fileno() method.

If no signals are currently pending, any reading operation will either fail with
error EAGAIN (if "nonBlocking" is set to True) or will block.

Args:
   signalset: a set of valid signal numbers; please refer to the 'signal' module
              for valid constants (like signal.SIGTERM); a list or tuple of
              signal numbers is also accepted and will be cast to a set.
   nonBlocking: a boolean.
   closeOnExec: a boolean; if True, the close-on-exec flag for this event file
                descriptor is set. This can be useful in multithreaded programs
                to close a parent's file descriptors when a child takes control
                via exec(). Please refer to the documentation on exec() for
                further details.

Raises:
   OSError.EINVAL: invalid signalset.
   OSError.EMFILE: per-process limit on number of open file descriptors reached.
   OSError.ENFILE: system-wide limit on total number of open files reached.
   OSError.ENODEV: could not mount (internal) anonymous inode device.
   OSError.ENOMEM: insufficient memory to create a new singalfd file descriptor."""
		self._isNonBlocking = bool(nonBlocking)
		self._isCloseOnExec = bool(closeOnExec)
		flags = 0
		if self._isNonBlocking: flags |= signalfd_c.SFD_NONBLOCK
		if self._isCloseOnExec: flags |= signalfd_c.SFD_CLOEXEC
		try:
			# evaluate signal set
			self._signalset = tuple([int(i) for i in set(signalset)])
		except:
			# something went wrong: raise EINVAL (like providing wrong flags)
			raise OSError(errno.EINVAL,os.strerror(errno.EINVAL))
		self._fd = signalfd_c.signalfd(-1,self._signalset,flags)
	
	
	def __del__(self):
		"""Destructor: Close the file descriptor."""
		self.close()
	
	
	def close(self):
		"""Close the file descriptor."""
		try:    os.close(self._fd)
		except: pass
	
	
	def fileno(self):
		"""Return the file descriptor of this event file object.

Returns:
   An integer."""
		return self._fd
	
	
	def modify(self,signalset,nonBlocking,closeOnExec):
		"""Modify the signalset guarded by this signal file descriptor. The descriptor
itself can be retrieved via the fileno() method. For details on the arguments,
please refer to __init__().

Args:
   signalset: a set of valid signal numbers.
   nonBlocking: a boolean.
   closeOnExec: a boolean.

Raises:
   OSError.EINVAL: invalid signalset.
   OSError.ENODEV: could not mount (internal) anonymous inode device.
   OSError.EBADF: signalfd file descriptor already closed."""
		self._isNonBlocking = bool(nonBlocking)
		self._isCloseOnExec = bool(closeOnExec)
		flags = 0
		if self._isNonBlocking: flags |= signalfd_c.SFD_NONBLOCK
		if self._isCloseOnExec: flags |= signalfd_c.SFD_CLOEXEC
		try:
			# evaluate signal set
			self._signalset = tuple([int(i) for i in set(signalset)])
		except:
			# something went wrong: raise EINVAL (like providing wrong flags)
			raise OSError(errno.EINVAL,os.strerror(errno.EINVAL))
		self._fd = signalfd_c.signalfd(self._fd,self._signalset,flags)
	
	
	def read(self):
		"""Read the signal file and return a dictionary holding information on
the recently received signal. In addition, the signal is consumed, so that it is
no longer pending for the process.

If multiple signals got caught, multiple calls to read are necessary until all
pending signals are consumed. When there are no signals pending, this method
either blocks or fails with error EAGAIN (if in non-blocking mode).

Returns:
   A dictionary of the following structure (according to signalfd(2)):
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

Raises:
   OSError.EAGAIN: no pending signals.
   OSError.EWOULDBLOCK: no pending signals.
   OSError.EINTR: read() call interrupted by a signal.
   OSError.EBADF: signalfd file descriptor already closed."""
		return signalfd_c.signalfd_read(self._fd)
	
	
	def signals(self):
		"""Return the set of guarded signal numbers.

Returns:
   A set of integers (signal numbers like signal.SIGTERM)."""
		return self._signalset
	
	
	def isNonBlocking(self):
		"""Return True if this event file does not block when no data is available.

Returns:
   A boolean."""
		return self._isNonBlocking
	
	
	def isCloseOnExec(self):
		"""Return True if the close-on-exec flag is set.

Returns:
   A boolean."""
		return self._isCloseOnExec



class timerfd:
	"""Class to manage a file descriptor for timer notification.

A timer file descriptor is created, which represents a timer and becomes
readable if this timer expires. Reading this file returns the number of
expirations that have occurred since the last read operation."""
	
	def __init__(self,rtc=False,nonBlocking=False,closeOnExec=False):
		"""Constructor: Initialise a timer file descriptor. The descriptor itself can be
retrieved via the fileno() method.

If the timer does not have expired yet, any reading operation will either fail
with error EAGAIN (if "nonBlocking" is set to True) or will block.

Args:
   rtc: a boolean; if True, this timer will access the system-wide realtime clock
        for time measurement. Otherwise a monotonic timed counter will be used.
        While the RTC can be changed by the SysAdmin and thus might exhibit
        discontinuous jumps, the monotonic clock is only affected through
        incremental adjustments by adjtime(3) and NTP.
   nonBlocking: a boolean.
   closeOnExec: a boolean; if True, the close-on-exec flag for this event file
                descriptor is set. This can be useful in multithreaded programs
                to close a parent's file descriptors when a child takes control
                via exec(). Please refer to the documentation on exec() for
                further details.

Raises:
   OSError.EMFILE: per-process limit on number of open file descriptors reached.
   OSError.ENFILE: system-wide limit on total number of open files reached.
   OSError.ENODEV: could not mount (internal) anonymous inode device.
   OSError.ENOMEM: insufficient memory to create a new singalfd file descriptor."""
		self._isRTC         = bool(rtc)
		self._isNonBlocking = bool(nonBlocking)
		self._isCloseOnExec = bool(closeOnExec)
		if self._isRTC:
			clockid = timerfd_c.CLOCK_REALTIME
		else:
			clockid = timerfd_c.CLOCK_MONOTONIC
		flags = 0
		if self._isNonBlocking: flags |= timerfd_c.TFD_NONBLOCK
		if self._isCloseOnExec: flags |= timerfd_c.TFD_CLOEXEC
		self._fd = timerfd_c.timerfd_create(clockid,flags)
	
	
	def __del__(self):
		"""Destructor: Close the file descriptor."""
		self.close()
	
	
	def close(self):
		"""Close the file descriptor."""
		try:    os.close(self._fd)
		except: pass
	
	
	def fileno(self):
		"""Return the file descriptor of this event file object.

Returns:
   An integer."""
		return self._fd
	
	
	def gettime(self):
		"""Return the current timer setting.

Returns:
    A 2-tuple (value, interval) of floats;
    "value" specifies the amount of time in seconds until the timer will expire;
    "interval" defines the period in seconds of a periodically expiring timer.
    
    If "value" is zero, the timer is disabled.
    If "interval" is zero, the timer will just expire once.

Raises:
   OSError.EBADF: timerfd file descriptor already closed."""
		return timerfd_c.timerfd_gettime(self._fd)
	
	
	def settime(self,value=0,interval=0,absolute=False):
		"""Start or stop the timer.

In case of an absolute timer based on an RTC source, "value" is expected to be
a UNIX time value of the desired point of time.

Args:
   value: a float >= 0 defining the initial expiration time in seconds;
          if zero (default), the timer is disabled.
   interval: a float >= 0 defining the period in seconds of a periodically
             expiring timer; if zero (default), the timer will only expire once.
   absolute: a boolean; if True, an absolute timer is started; in this case
             "value" is interpreted as an absolute clock value; otherwise
             a relative timer is started (default).

Returns:
   A 2-tuple (value,interval) of floats; the old timer setting.

Raises:
   OSError.EINVAL: invalid timer values specified.
   OSError.EBADF: timerfd file descriptor already closed."""
		if bool(absolute):
			flags = timerfd_c.TFD_TIMER_ABSTIME
		else:
			flags = 0
		return timerfd_c.timerfd_settime(self._fd,flags,value,interval)
	
	
	def read(self):
		"""Read the timer file and return an integer denoting the number of
expirations since the last reading operation.

If the timer has not expired yet, this method will either block or fail with
error EAGAIN if in non-blocking mode.

Raises:
   OSError.EAGAIN: timer has not yet expired.
   OSError.EBADF: timerfd file descriptor already closed."""
		return timerfd_c.timerfd_read(self._fd)
	
	
	def isRTC(self):
		"""Return True if this timer uses the system-wide realtime clock.
If this returns False, a monotonic clock source is used.

Returns:
   A boolean."""
		return self._isRTC
	
	
	def isNonBlocking(self):
		"""Return True if this event file does not block when no data is available.

Returns:
   A boolean."""
		return self._isNonBlocking
	
	
	def isCloseOnExec(self):
		"""Return True if the close-on-exec flag is set.

Returns:
   A boolean."""
		return self._isCloseOnExec



class inotify:
	"""Class to manage an inotify instance.

An inotify file descriptor is created, which represents an inotify instance.
Files and directories can be added in order to monitor them. The inotify file
descriptor becomes readable when such a file alternation event occurs."""
	
	def __init__(self,nonBlocking=False,closeOnExec=False):
		"""Constructor: Initialise an inotify file descriptor. The descriptor itself can be
retrieved via the fileno() method.

If no file changes were detected by this inotify instance, any reading operation
will either fail with error EAGAIN (if "nonBlocking" is set) or will block.

Args:
   nonBlocking: a boolean.
   closeOnExec: a boolean; if True, the close-on-exec flag for this event file
                descriptor is set. This can be useful in multithreaded programs
                to close a parent's file descriptors when a child takes control
                via exec(). Please refer to the documentation on exec() for
                further details.

Raises:
   OSError.EMFILE: user limit on total number of inotify instances reached.
   OSError.EMFILE: per-process limit on number of open file descriptors reached.
   OSError.ENFILE: system-wide limit on total number of open files reached.
   OSError.ENOMEM: insufficient kernel memory available."""
		self._isNonBlocking = bool(nonBlocking)
		self._isCloseOnExec = bool(closeOnExec)
		self._wd = dict() # mapping pathnames to watch descriptors
		flags = 0
		if self._isNonBlocking: flags |= inotify_c.IN_NONBLOCK
		if self._isCloseOnExec: flags |= inotify_c.IN_CLOEXEC
		self._fd = inotify_c.inotify_init1(flags)
	
	
	def __del__(self):
		"""Destructor: Close the file descriptor."""
		self.close()
	
	
	def close(self):
		"""Close the file descriptor."""
		try:    os.close(self._fd)
		except: pass
	
	
	def fileno(self):
		"""Return the file descriptor of this event file object.

Returns:
   An integer."""
		return self._fd
	
	
	def add(self,pathname,mask):
		"""
Raises:
   OSError.EACCES: read access to given file is not permitted.
   OSError.EBADF: inotify file descriptor already closed.
   OSError.EFAULT: pathname points outside of the process's address space.
   OSError.EINVAL: given event mask contains no valid events.
   OSError.ENAMETOOLONG: pathname too long.
   OSError.ENOENT: a directory component in pathname does not exist or is a
                   dangling symbolic link.
   OSError.ENOMEM: insufficient kernel memory available.
   OSError.ENOSPC: user limit on total number of inotify watches was reached or
                   the kernel failed to allocate a needed resource."""
		self._wd[pathname] = inotify_c.inotify_add_watch(self._fd,pathname,mask)
	
	
	def remove(self,pathname):
		"""
Raises:
   OSError.EBADF: inotify file descriptor already closed.
"""
		inotify_c.inotify_rm_watch(self._wd[pathname])
		del self._wd[pathname]
	
	
	def read(self):
		eventlist = inotify_c.inotify_read(self._fd)
		result = list()
		for wd,mask,cookie,name in eventlist:
			# reverse look-up watch descriptor
			pathname = [key for key,value in self._wd.items() if value == wd][0]
			result.append(pathname,name,mask,cookie)
		return result
	
	
	def watchedPaths(self):
		"""Return a tuple of all pathnames watched by this inotify instance.

Returns:
   A tuple of strings."""
		return tuple(self._wd.keys())
	
	
	def isNonBlocking(self):
		"""Return True if this event file does not block when no data is available.

Returns:
   A boolean."""
		return self._isNonBlocking
	
	
	def isCloseOnExec(self):
		"""Return True if the close-on-exec flag is set.

Returns:
   A boolean."""
		return self._isCloseOnExec


