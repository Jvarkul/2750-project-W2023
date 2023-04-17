
CC=clang
CFLAGS=-Wall -std=c99 -pedantic
LIBS=-lm
PYTHON_INCLUDE_PATH=/usr/include/python3.10/
PYTHON_LIB=/usr/lib/
PYTHON_VERSION=python3.10

all: _molecule.so

mol.o: mol.c mol.h
	$(CC) $(CFLAGS) -fpic -c mol.c -o mol.o

libmol.so: mol.o mol.h
	$(CC) $(CFLAGS) -shared mol.o -o libmol.so -lm

_molecule.so: libmol.so molecule_wrap.o
	$(CC) $(CFLAGS) -shared -lmol -L. -l$(PYTHON_VERSION) -L $(PYTHON_INCLUDE_PATH) -dynamiclib -o _molecule.so molecule_wrap.o

molecule_wrap.o: molecule_wrap.c
	$(CC) $(CFLAGS) -fPIC -I$(PYTHON_INCLUDE_PATH) -o molecule_wrap.o -c molecule_wrap.c

molecule_wrap%c molecule_wrap%py:
	swig -python molecule.i

update_target:
	export LD_LIBRARY_PATH=.

clean:
	rm -f *.o *.so a.out 