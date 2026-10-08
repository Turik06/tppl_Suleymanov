ASM = nasm
ASMFLAGS = -felf64
CC = gcc
CFLAGS = -no-pie
TARGET = average
SRC = main.asm
OBJ = main.o

all: $(TARGET)

$(OBJ): $(SRC)
	$(ASM) $(ASMFLAGS) $(SRC) -o $(OBJ)

$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) $(OBJ) -o $(TARGET)

run: $(TARGET)
	./$(TARGET) data.txt

clean:
	rm -f $(OBJ) $(TARGET)

.PHONY: all run clean
