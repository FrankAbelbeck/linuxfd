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
#include <signal.h>
#include <sys/signalfd.h>


/* Python: signalfd(fd,signalset,flags) -> fd
   C:      int signalfd(int fd, const sigset_t *mask, int flags); */
static PyObject * _signalfd(PyObject *self, PyObject *args) {
	/* variable definitions */
	int fd;
	int flags;
	int result;
	sigset_t mask;
	int setsize;
	int i;
	
	/* problem: signalset is a tuple of variable length 
	   => parse it as generic object and check if a tuple was received */
	PyObject* pySignalSet;
	if (!PyArg_ParseTuple(args, "iOi", &fd, &pySignalSet, &flags) || !PyTuple_Check(pySignalSet)) return NULL;
	
	/* iterate over python tuple and add signals to empty signal set */
	result = sigemptyset(&mask);
	setsize = PyTuple_Size(pySignalSet);
	for (i = 0; i < setsize; i++) {
		result = sigaddset(&mask,(int)PyLong_AsLong(PyTuple_GetItem(pySignalSet,i)));
		/* if -1 is returned, the item did not specify a valid signal number
		   errno will be set to EINVAL, thus OSError is raised */
		if (result == -1) return PyErr_SetFromErrno(PyExc_OSError);
	}
	
	/* call signalfd; catch errors by raising an exception */
	Py_BEGIN_ALLOW_THREADS
	result = signalfd(fd, &mask, flags);
	Py_END_ALLOW_THREADS
	if (result == -1) return PyErr_SetFromErrno(PyExc_OSError);
	
	/* everything's fine, return file descriptor returned by signalfd() */
	return PyLong_FromLong(result);
};


/* Python: signalfd_read(fd) -> value
   C:      int signalfd_read(int fd, eventfd_t *value); */
static PyObject * _signalfd_read(PyObject *self, PyObject *args) {
	/* variable definitions */
	int fd;
	struct signalfd_siginfo value;
	int result;
	PyObject *dictvalue;
	
	/* parse the function's arguments: int fd */
	if (!PyArg_ParseTuple(args, "i", &fd)) return NULL;
	
	/* call read; catch errors by raising an exception */
	Py_BEGIN_ALLOW_THREADS
	result = read(fd, &value, sizeof(struct signalfd_siginfo));
	Py_END_ALLOW_THREADS
	if (result == -1)
		/* read failed, raise OSError with current error number */
		return PyErr_SetFromErrno(PyExc_OSError);
	else if (result != sizeof(struct signalfd_siginfo)) {
		/* read succeeded, but returned not the expected number of bytes;
		   perhaps interrupted, raise an I/O error */
		errno = EIO;
		return PyErr_SetFromErrno(PyExc_OSError);
	}
	
	/* construct signal dictionary */
	dictvalue = Py_BuildValue(
		"{s:i,s:i,s:i,s:i,s:i,s:i,s:i,s:i,s:i,s:i,s:i,s:i,s:i,s:i,s:i,s:i}",
		"signo",   value.ssi_signo,
		"errno",   value.ssi_errno,
		"code",    value.ssi_code,
		"pid",     value.ssi_pid,
		"uid",     value.ssi_uid,
		"fd",      value.ssi_fd,
		"tid",     value.ssi_tid,
		"band",    value.ssi_band,
		"overrun", value.ssi_overrun,
		"trapno",  value.ssi_trapno,
		"status",  value.ssi_status,
		"int",     value.ssi_int,
		"ptr",     value.ssi_ptr,
		"utime",   value.ssi_utime,
		"stime",   value.ssi_stime,
		"addr",    value.ssi_addr
	);

	/* everything's fine, return read value */
	return dictvalue;
}


static PyMethodDef methods[] = {
	{ "signalfd",       _signalfd,      METH_VARARGS, NULL },
	{ "signalfd_read",  _signalfd_read, METH_VARARGS, NULL },
    { NULL,             NULL,           0,            NULL }
};

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef signalfdmodule = { PyModuleDef_HEAD_INIT, "signalfd_c", NULL, -1, methods };
#endif

#if PY_MAJOR_VERSION >= 3
PyMODINIT_FUNC PyInit_signalfd_c(void) {
#else
void initsignalfd_c(void) {
#endif
	PyObject *m;
#if PY_MAJOR_VERSION >= 3
	m = PyModule_Create(&signalfdmodule);
#else
	m = Py_InitModule("signalfd_c",methods);
#endif
	if (m != NULL) {
		/* define signalfd constants */
		PyModule_AddIntConstant( m, "SFD_CLOEXEC",   SFD_CLOEXEC );
		PyModule_AddIntConstant( m, "SFD_NONBLOCK",  SFD_NONBLOCK );
	}
#if PY_MAJOR_VERSION >= 3
	return m;
#endif
}
                                                                                                                                                                                 
