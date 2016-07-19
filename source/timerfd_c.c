/* This file is part of linuxfd (Python wrapper for eventfd/signalfd/timerfd)
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
    along with linuxfd.  If not, see <http://www.gnu.org/licenses/>.
*/

#include <Python.h>
#include <unistd.h>
#include <time.h>
#include <stdint.h> /* definition of uint64_t */
#include <sys/timerfd.h>


/* Python: timerfd_create(clockid,flags) -> fd
   C:      int timerfd_create(int clockid, int flags); */
static PyObject * _timerfd_create(PyObject *self, PyObject *args) {
	/* variable definitions */
	int clockid;
	int flags;
	int result;
	
	/* parse the function's arguments: int clockid, int flags */
	if (!PyArg_ParseTuple(args, "ii", &clockid, &flags)) return NULL;
	
	/* call timerfd_create; catch errors by raising an exception */
	Py_BEGIN_ALLOW_THREADS
	result = timerfd_create(clockid, flags);
	Py_END_ALLOW_THREADS
	if (result == -1) return PyErr_SetFromErrno(PyExc_OSError);
	
	/* everything's fine, return file descriptor returned by timerfd_create() */
	return PyLong_FromLong(result);
};

/* Python: timerfd_settime(fd,flags,value,interval) -> value,interval
   C:      int timerfd_settime(int fd, int flags,
                               const struct itimerspec *new_value,
                               struct itimerspec *old_value); */
static PyObject * _timerfd_settime(PyObject *self, PyObject *args) {
	/* variable definitions */
	int fd;
	int flags;
	int result;
	float value;
	float interval;
	struct itimerspec old_value;
	struct itimerspec new_value;
	PyObject *resulttuple;
	
	/* parse the function's arguments: int clockid, int flags */
	if (!PyArg_ParseTuple(args, "iiff", &fd, &flags, &value, &interval)) return NULL;
	
	/* prepare struct itimerspec */
	new_value.it_value.tv_sec  = (time_t)value;
	new_value.it_value.tv_nsec = (long int)( 1e9 * (value - (int)value) );
	
	new_value.it_interval.tv_sec  = (time_t)interval;
	new_value.it_interval.tv_nsec = (long int)( 1e9 * (interval - (int)interval) );
	
	/* call timerfd_settime; catch errors by raising an exception */
	Py_BEGIN_ALLOW_THREADS
	result = timerfd_settime(fd, flags, &new_value, &old_value);
	Py_END_ALLOW_THREADS
	if (result == -1) return PyErr_SetFromErrno(PyExc_OSError);
	
	/* convert returned struct old_value */
	value    = (float)old_value.it_value.tv_sec    + (float)old_value.it_value.tv_nsec / 1e9;
	interval = (float)old_value.it_interval.tv_sec + (float)old_value.it_interval.tv_nsec / 1e9;
	resulttuple = Py_BuildValue("(ff)", value, interval);
	
	/* everything's fine, return tuple (value,interval) created from old_value */
	return resulttuple;
};


/* Python: timerfd_gettime(fd) -> value,interval
   C:      int timerfd_gettime(int fd, struct itimerspec *curr_value); */
static PyObject * _timerfd_gettime(PyObject *self, PyObject *args) {
	/* variable definitions */
	int fd;
	int result;
	float value;
	float interval;
	struct itimerspec curr_value;
	PyObject *resulttuple;
	
	/* parse the function's arguments: int clockid, int flags */
	if (!PyArg_ParseTuple(args, "i", &fd)) return NULL;
	
	/* call timerfd_gettime; catch errors by raising an exception */
	Py_BEGIN_ALLOW_THREADS
	result = timerfd_gettime(fd, &curr_value);
	Py_END_ALLOW_THREADS
	if(result == -1) return PyErr_SetFromErrno(PyExc_OSError);
	
	/* convert returned struct old_value */
	value    = (float)curr_value.it_value.tv_sec    + (float)curr_value.it_value.tv_nsec / 1e9;
	interval = (float)curr_value.it_interval.tv_sec + (float)curr_value.it_interval.tv_nsec / 1e9;
	resulttuple = Py_BuildValue("(ff)", value, interval);
	
	/* everything's fine, return tuple (value,interval) created from old_value */
	return resulttuple;
};


/* Python: timerfd_read(fd) -> value
   C:      ssize_t read(int fd, void *buf, size_t count); */
static PyObject * _timerfd_read(PyObject *self, PyObject *args) {
	/* variable definitions */
	int fd;
	uint64_t buffer;
	ssize_t result;
	
	/* parse the function's arguments: int fd */
	if (!PyArg_ParseTuple(args, "i", &fd)) return NULL;
	
	/* call read; catch OSErrors */
	Py_BEGIN_ALLOW_THREADS
	result = read(fd, &buffer, sizeof(uint64_t));
	Py_END_ALLOW_THREADS
	if (result == -1)
		/* read failed, raise OSError with current error number */
		return PyErr_SetFromErrno(PyExc_OSError);
	else if (result != sizeof(uint64_t)) {
		/* read succeeded, but returned not the expected number of bytes;
		   perhaps interrupted, raise an I/O error */
		errno = EIO;
		return PyErr_SetFromErrno(PyExc_OSError);
	}
	
	return PyLong_FromLong(buffer);
}


static PyMethodDef methods[] = {
	{ "timerfd_create",  _timerfd_create,  METH_VARARGS, NULL },
	{ "timerfd_settime", _timerfd_settime, METH_VARARGS, NULL },
	{ "timerfd_gettime", _timerfd_gettime, METH_VARARGS, NULL },
	{ "timerfd_read",    _timerfd_read,    METH_VARARGS, NULL },
    { NULL,              NULL,     0,            NULL }
};

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef timerfdmodule = { PyModuleDef_HEAD_INIT, "timerfd_c", NULL, -1, methods };
#endif

#if PY_MAJOR_VERSION >= 3
PyMODINIT_FUNC PyInit_timerfd_c(void) {
#else
void inittimerfd_c(void) {
#endif
	PyObject *m;
#if PY_MAJOR_VERSION >= 3
	m = PyModule_Create(&timerfdmodule);
#else
	m = Py_InitModule("timerfd_c",methods);
#endif
	if (m != NULL) {
		/* define timerfd constants */
		PyModule_AddIntConstant( m, "CLOCK_REALTIME",    CLOCK_REALTIME );
		PyModule_AddIntConstant( m, "CLOCK_MONOTONIC",   CLOCK_MONOTONIC );
		PyModule_AddIntConstant( m, "TFD_CLOEXEC",       TFD_CLOEXEC );
		PyModule_AddIntConstant( m, "TFD_NONBLOCK",      TFD_NONBLOCK );
		PyModule_AddIntConstant( m, "TFD_TIMER_ABSTIME", TFD_TIMER_ABSTIME );
	}
#if PY_MAJOR_VERSION >= 3
	return m;
#endif
}
