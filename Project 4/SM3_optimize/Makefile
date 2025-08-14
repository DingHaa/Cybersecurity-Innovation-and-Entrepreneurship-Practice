CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -O2 -fopenmp
LDFLAGS = -lssl -lcrypto

TARGET = sm3_optimize
SOURCES = SM3_optimize.cpp
HEADERS = SM3_optimize.h SM3_Primitive.h SM3_Promote.h

.PHONY: all clean run

all: $(TARGET)

$(TARGET): $(SOURCES) $(HEADERS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SOURCES) $(LDFLAGS)

clean:
	rm -f $(TARGET)

run: $(TARGET)
	./$(TARGET)

install-deps:
	sudo apt-get update
	sudo apt-get install -y libssl-dev build-essential
