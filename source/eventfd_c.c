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
#include <sys/eventfd.h>


/* Python: eventfd(initval,flags) -> fd
   C:      int eventfd(unsigned int initval, int flags); */
static PyObject * _eventfd(PyObject *self, PyObject *args) {
	/* variable definitions */
	unsigned int initval;
	int flags;
	int result;
	
	/* parse the function's arguments: unsigned int initval, int flags */
	if (!PyArg_ParseTuple(args, "Ii", &initval, &flags)) return NULL;
	
	/* call eventfd; catch errors by raising an exception */
	Py_BEGIN_ALLOW_THREADS
	result = eventfd(initval, flags);
	Py_END_ALLOW_THREADS
	if (result == -1) return PyErr_SetFromErrno(PyExc_OSError);
	
	/* everything's fine, return file descriptor returned by eventfd() */
	return PyLong_FromLong(result);
};


/* Python: eventfd_read(fd) -> value
   C:      int eventfd_read(int fd, eventfd_t *value); */
static PyObject * _eventfd_read(PyObject *self, PyObject *args) {
	/* variable definitions */
	int fd;
	eventfd_t value;
	int result;
	
	/* parse the function's arguments: int fd */
	if (!PyArg_ParseTuple(args, "i", &fd)) return NULL;
	
	/* call eventfd_read; catch errors by raising an exception */
	Py_BEGIN_ALLOW_THREADS
	result = eventfd_read(fd, &value);
	Py_END_ALLOW_THREADS
	if (result == -1) return PyErr_SetFromErrno(PyExc_OSError);
	
	/* everything's fine, return read value */
	return PyLong_FromLong(value);
}


/* Python: eventfd_write(fd,value) -> None
   C:      int eventfd_write(int fd, eventfd_t value); */
static PyObject * _eventfd_write(PyObject *self, PyObject *args) {
	/* variable definitions */
	int fd;
	eventfd_t value;
	int result;
	
	/* parse the function's arguments: int fd, uint64_t value */
	/* uint64_t in Python API? --> unsigned long long = K */
	if (!PyArg_ParseTuple(args, "iK", &fd, &value)) return NULL;
	
	/* call eventfd_write; catch errors by raising an exception */
	Py_BEGIN_ALLOW_THREADS
	result = eventfd_write(fd,value);
	Py_END_ALLOW_THREADS
	if (result == -1) return PyErr_SetFromErrno(PyExc_OSError);
	
	/* everything's fine, return None value */
	Py_INCREF(Py_None);
	return Py_None;
}


static PyMethodDef methods[] = {
	{ "eventfd",       _eventfd,      METH_VARARGS, NULL },
	{ "eventfd_read",  _eventfd_read, METH_VARARGS, NULL },
	{ "eventfd_write", _eventfd_write,METH_VARARGS, NULL },
    { NULL,            NULL,          0,            NULL }
};

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef eventfdmodule = { PyModuleDef_HEAD_INIT, "eventfd_c", NULL, -1, methods };
#endif

#if PY_MAJOR_VERSION >= 3
PyMODINIT_FUNC PyInit_eventfd_c(void) {
#else
void initeventfd_c(void) {
#endif
	PyObject *m;
#if PY_MAJOR_VERSION >= 3
	m = PyModule_Create(&eventfdmodule);
#else
	m = Py_InitModule("eventfd_c",methods);
#endif
	if (m != NULL) {
		/* define eventfd constants */
		PyModule_AddIntConstant( m, "EFD_CLOEXEC",   EFD_CLOEXEC );
		PyModule_AddIntConstant( m, "EFD_NONBLOCK",  EFD_NONBLOCK );
		PyModule_AddIntConstant( m, "EFD_SEMAPHORE", EFD_SEMAPHORE );
	}
#if PY_MAJOR_VERSION >= 3
	return m;
#endif
}
                                                                                                                                                                                 
