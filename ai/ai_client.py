import os
import sys
import time

FIFO_PATH = "/tmp/chatbot_fifo"
RESPONSE_FIFO_PATH = "/tmp/chatbot_response_fifo"


def main():
    if not os.path.exists(FIFO_PATH):
        print("Error: Chatbot server is not running.")
        sys.exit(1)

    if not os.path.exists(RESPONSE_FIFO_PATH):
        os.mkfifo(RESPONSE_FIFO_PATH)

    if len(sys.argv) > 1:
        message = ' '.join(sys.argv[1:])
    else:
        message = sys.stdin.read().strip()

    with open(FIFO_PATH, "w") as fifo:
        fifo.write(message + "\n")

    with open(RESPONSE_FIFO_PATH, "r") as response_fifo:
        while True:
            line = response_fifo.readline()
            if not line:
                break
            print(line.strip())


if __name__ == "__main__":
    main()
