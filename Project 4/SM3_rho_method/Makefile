CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -O2 -march=native
LDFLAGS = -lssl -lcrypto

TARGET = sm3_rho_method
SOURCES = SM3_rho_method.cpp
HEADERS = SM3_rho_method.h

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

help:
	@echo "Available targets:"
	@echo "  all          - Build the program"
	@echo "  clean        - Remove executable"
	@echo "  run          - Build and run the program"
	@echo "  install-deps - Install required dependencies"
	@echo "  help         - Show this help message"
