CC = g++ -std=c++17 -O3

all: sm4 sm4_ttable sm4_aesni sm4_gcm

sm4: sm4.o
	$(CC) sm4.o -o sm4

sm4_ttable: sm4_ttable.o
	$(CC) sm4_ttable.o -o sm4_ttable

sm4_aesni: sm4_aesni.o
	$(CC) -maes -msse4.1 sm4_aesni.o -o sm4_aesni

sm4_gcm: sm4_gcm.o
	$(CC) -fopenmp sm4_gcm.o -o sm4_gcm

sm4.o: sm4.cpp sm4.h
	$(CC) -c sm4.cpp -o sm4.o

sm4_ttable.o: sm4_ttable.cpp sm4_ttable.h
	$(CC) -c sm4_ttable.cpp -o sm4_ttable.o

sm4_aesni.o: sm4_aesni.cpp sm4_aesni.h
	$(CC) -maes -msse4.1 -c sm4_aesni.cpp -o sm4_aesni.o

sm4_gcm.o: sm4_gcm.cpp sm4_gcm.h
	$(CC) -fopenmp -c sm4_gcm.cpp -o sm4_gcm.o

.PHONY: clean
clean:
	rm -rf *.o sm4 sm4_ttable sm4_aesni sm4_gcm