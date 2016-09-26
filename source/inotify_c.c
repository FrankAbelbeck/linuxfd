/* This file is part of linuxfd (Python wrapper eventfd/signalfd/timerfd)
Copyright (C) 2016 Frank Abelbeck <frank.abelbeck@googlemail.com>

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
#include <limits.h> /* provides NAME_MAX */
#include <stdlib.h> /* provides malloc and free */
#include <sys/inotify.h>


/* Python: inotify_init(flags) -> fd
   C:      int inotify_init1(int flags); */
static PyObject * _inotify_init(PyObject *self, PyObject *args) {
	/* variable definitions */
	int fd,flags;
	
	/* parse argument: integer -> flags */
	if (!PyArg_ParseTuple(args, "i", &flags)) return NULL;
	
	/* call inotify_init1; catch errors by raising an exception */
	Py_BEGIN_ALLOW_THREADS
	fd = inotify_init1(flags);
	Py_END_ALLOW_THREADS
	if (fd == -1) return PyErr_SetFromErrno(PyExc_OSError);
	
	/* everything's fine, return file descriptor */
	return PyLong_FromLong(fd);
};


/* Python: inotify_add_watch(fd,pathname,mask) -> wd
   C:      int inotify_add_watch(int fd, const char *pathname, uint32_t mask); */
static PyObject * _inotify_add_watch(PyObject *self, PyObject *args) {
	/* variable definitions */
	int fd,wd;
	char *pathname;
	uint32_t mask;
	
	/* parse the function's arguments: int fd */
	if (!PyArg_ParseTuple(args, "isI", &fd, &pathname, &mask)) return NULL;
	
	/* call inotify_add_watch; catch errors by raising an exception */
	Py_BEGIN_ALLOW_THREADS
	wd = inotify_add_watch(fd, pathname, mask);
	Py_END_ALLOW_THREADS
	if (wd == -1) return PyErr_SetFromErrno(PyExc_OSError);
	
	/* everything's fine, return watch descriptor */
	return PyLong_FromLong(wd);
}


/* Python: inotify_rm_watch(fd,wd)
   C:      int inotify_rm_watch(int fd, int wd); */
static PyObject * _inotify_rm_watch(PyObject *self, PyObject *args) {
	/* variable definitions */
	int fd,wd,result;
	
	/* parse the function's arguments: int fd */
	if (!PyArg_ParseTuple(args, "ii", &fd, &wd)) return NULL;
	
	/* call inotify_rm_watch; catch errors by raising an exception */
	Py_BEGIN_ALLOW_THREADS
	result = inotify_rm_watch(fd, wd);
	Py_END_ALLOW_THREADS
	if (result == -1) return PyErr_SetFromErrno(PyExc_OSError);
	
	/* everything's fine, return None value */
	Py_INCREF(Py_None);
	return Py_None;
}


/* Python: inotify_read(fd,size) -> value
   C:      ssize_t read(int fd, void *buf, size_t count); */
static PyObject * _inotify_read(PyObject *self, PyObject *args) {
	/* variable definitions */
	int fd,size,length,n_events;
	char *pointer;
	const struct inotify_event *event;
	char *buffer;
	PyObject *result;
	
	/* parse the function's argument: int fd */
	if (!PyArg_ParseTuple(args, "ii", &fd, &size)) return NULL;
	
	/* prepare buffer by allocating enough memory */
	/* taken from the example in man 7 inotify:
	   "Some systems cannot read integer variables if they are not properly
	    aligned. On other systems, incorrect alignment may decrease performance.
	    Hence, the buffer used for reading from the inotify file descriptor
	    should have the same alignment as struct inotify_event. */
	/* char buffer[size] __attribute__ ((aligned(__alignof__(struct inotify_event)))); */
	/* since this won't work in C, aligned_alloc() has to be used */
	buffer = (char *)aligned_alloc(__alignof__(struct inotify_event),size);
	if (buffer == NULL) {
		/* read failed, raise OSError with either EINVAL (alignment not a power of two) or ENOMEM (insufficient memory) */
		return PyErr_SetFromErrno(PyExc_OSError);
	}
	
	/* call read; catch OSErrors */
	Py_BEGIN_ALLOW_THREADS
	length = read(fd, buffer, size);
	Py_END_ALLOW_THREADS
	
	if (length == -1) {
		/* read failed, raise OSError with current error number */
		free(buffer); /* thou shalt always free allocated memory! */
		return PyErr_SetFromErrno(PyExc_OSError);
	}
	
	/* loop over all events in the buffer (example again adapted from the one in man 7 inotify) */
	/* first run: determine number of events */
	n_events = 0;
	for (pointer = buffer; pointer < buffer + length; pointer += sizeof(struct inotify_event) + event->len) {
		/* cast current pointer to an inotify_event structure */
		event = (const struct inotify_event *)pointer;
		n_events++;
	}
	/* second run: correctly size result list and populate it with the events via PyList_SetItem */
	result = PyList_New(n_events);
	n_events = 0;
	for (pointer = buffer; pointer < buffer + length; pointer += sizeof(struct inotify_event) + event->len) {
		/* cast current pointer to an inotify_event structure */
		event = (const struct inotify_event *)pointer;
		PyList_SetItem(
			result,
			n_events,
			Py_BuildValue("(i,i,i,s)",event->wd,event->mask,event->cookie,event->name)
		);
		n_events++;
	}
	free(buffer); /* thou shalt always free allocated memory! */
	return result;
}


static PyMethodDef methods[] = {
	{ "inotify_init",      _inotify_init,      METH_VARARGS, NULL },
	{ "inotify_add_watch", _inotify_add_watch, METH_VARARGS, NULL },
	{ "inotify_rm_watch",  _inotify_rm_watch,  METH_VARARGS, NULL },
	{ "inotify_read",      _inotify_read,      METH_VARARGS, NULL },
    { NULL   ,             NULL,               0,            NULL }
};

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef inotifymodule = { PyModuleDef_HEAD_INIT, "inotify_c", NULL, -1, methods };
#endif

#if PY_MAJOR_VERSION >= 3
PyMODINIT_FUNC PyInit_inotify_c(void) {
#else
void initinotify_c(void) {
#endif
	PyObject *m;
#if PY_MAJOR_VERSION >= 3
	m = PyModule_Create(&inotifymodule);
#else
	m = Py_InitModule("inotify_c",methods);
#endif
	if (m != NULL) {
		/* define inotify constants: init flags */
		PyModule_AddIntConstant( m, "IN_NONBLOCK",      IN_NONBLOCK );
		PyModule_AddIntConstant( m, "IN_CLOEXEC",       IN_CLOEXEC );
		/* define inotify constants: events */
		PyModule_AddIntConstant( m, "IN_ACCESS",        IN_ACCESS );
		PyModule_AddIntConstant( m, "IN_ATTRIB",        IN_ATTRIB );
		PyModule_AddIntConstant( m, "IN_CLOSE_WRITE",   IN_CLOSE_WRITE );
		PyModule_AddIntConstant( m, "IN_CLOSE_NOWRITE", IN_CLOSE_NOWRITE );
		PyModule_AddIntConstant( m, "IN_CREATE",        IN_CREATE );
		PyModule_AddIntConstant( m, "IN_DELETE",        IN_DELETE );
		PyModule_AddIntConstant( m, "IN_DELETE_SELF",   IN_DELETE_SELF );
		PyModule_AddIntConstant( m, "IN_MODIFY",        IN_MODIFY );
		PyModule_AddIntConstant( m, "IN_MOVE_SELF",     IN_MOVE_SELF );
		PyModule_AddIntConstant( m, "IN_MOVED_FROM",    IN_MOVED_FROM );
		PyModule_AddIntConstant( m, "IN_MOVED_TO",      IN_MOVED_TO );
		PyModule_AddIntConstant( m, "IN_OPEN",          IN_OPEN );
		/* define inotify constants: event macros (combinations of events) */
		PyModule_AddIntConstant( m, "IN_ALL_EVENTS",    IN_ALL_EVENTS ); /* = all event flags set */
		PyModule_AddIntConstant( m, "IN_MOVE",          IN_MOVE ); /* IN_MOVED_FROM | IN_MOVED_TO */
		PyModule_AddIntConstant( m, "IN_CLOSE",         IN_CLOSE ); /* IN_CLOSE_WRITE | IN_CLOSE_NOWRITE */
		/* define inotify constants: flags for inotify_add_watch */
		PyModule_AddIntConstant( m, "IN_DONT_FOLLOW",   IN_DONT_FOLLOW );
		PyModule_AddIntConstant( m, "IN_EXCL_UNLINK",   IN_EXCL_UNLINK );
		PyModule_AddIntConstant( m, "IN_MASK_ADD",      IN_MASK_ADD );
		PyModule_AddIntConstant( m, "IN_ONESHOT",       IN_ONESHOT );
		PyModule_AddIntConstant( m, "IN_ONLYDIR",       IN_ONLYDIR );
		/* define inotify constants: mask returned by read */
		PyModule_AddIntConstant( m, "IN_IGNORED",       IN_IGNORED );
		PyModule_AddIntConstant( m, "IN_ISDIR",         IN_ISDIR );
		PyModule_AddIntConstant( m, "IN_Q_OVERFLOW",    IN_Q_OVERFLOW );
		PyModule_AddIntConstant( m, "IN_UNMOUNT",       IN_UNMOUNT );
	}
#if PY_MAJOR_VERSION >= 3
	return m;
#endif
}
                                                                                                                                                                                 
