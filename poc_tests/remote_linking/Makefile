CC=gcc
CFLAGS=-c -Wall

all: calypso

calypso: main.o func_one.o func_two.o func_three.o
	$(MAKE) remote
	$(CC) main.o func_one.o func_two.o func_three.o -o calypso

main.o: main.c
	$(CC) $(CFLAGS) main.c

func_one.o: func_one.c
	$(CC) $(CFLAGS) func_one.c

func_two.o: func_two.c
	$(CC) $(CFLAGS) func_two.c

func_three.o: func_three.c
	$(CC) $(CFLAGS) func_three.c

.PHONY: remote
remote:
	@echo "Remote linking ..."	
	sleep 5
	@echo "Done."

clean:
	rm -rf *o calypso
