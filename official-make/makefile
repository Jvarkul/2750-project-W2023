CC=clang
CFLAGS=-Wall -std=c99 -pedantic
LIBS=-lm
PYTHON_INCLUDE_PATH=/usr/include/python3.7m/
PYTHON_LIB=/usr/lib/
PYTHON_VERSION=python3.7m



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

test1: test1.o mol.o libmol.so
	$(CC) test1.o mol.o -o test1 $(LIBS)

test2: test2.o mol.o libmol.so
	$(CC) test2.o mol.o -o test2 $(LIBS)

test3: test3.o mol.o libmol.so
	$(CC) test3.o mol.o -o test3 $(LIBS)

test6: test6.o mol.o libmol.so
	$(CC) test6.o mol.o -o test6 $(LIBS)

test1.o: test1.c mol.h
	$(CC) $(CFLAGS) -c test1.c

test2.o: test2.c mol.h
	$(CC) $(CFLAGS) -c test2.c

test3.o: test3.c mol.h
	$(CC) $(CFLAGS) -c test3.c

test6.0: test6.c mol.h
	$(CC) $(CFLAGS) -c test6.c

clean:
	rm -f *.o *.so a.out 