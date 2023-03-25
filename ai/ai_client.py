import sys
import os

FIFO_PATH = "/tmp/chatbot_fifo"
RESPONSE_FIFO_PATH = "/tmp/chatbot_response_fifo"


def main():
    if not os.path.exists(RESPONSE_FIFO_PATH):
        os.mkfifo(RESPONSE_FIFO_PATH)

    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:])
    else:
        command = input("Enter a command: ")

    with open(FIFO_PATH, "w") as fifo:
        fifo.write(command + "\n")

    with open(RESPONSE_FIFO_PATH, "r") as response_fifo:
        while True:
            char = response_fifo.read(1)
            if not char:
                break
            print(char, end="", flush=True)

    if command.lower() == "exit":
        os.remove(RESPONSE_FIFO_PATH)


if __name__ == "__main__":
    main()
