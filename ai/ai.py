#!/usr/bin/env python


import os
import threading
import openai
import errno
from chat_service import ChatService
from config_utils import create_chat_config


FIFO_PATH = "/tmp/chatbot_fifo"
RESPONSE_FIFO_PATH = "/tmp/chatbot_response_fifo"


def start_fifo_server(chat):
    if not os.path.exists(FIFO_PATH):
        try:
            os.mkfifo(FIFO_PATH)
        except OSError as oe:
            if oe.errno != errno.EEXIST:
                raise

    if not os.path.exists(RESPONSE_FIFO_PATH):
        try:
            os.mkfifo(RESPONSE_FIFO_PATH)
        except OSError as oe:
            if oe.errno != errno.EEXIST:
                raise

    while True:
        with open(FIFO_PATH, "r") as fifo:
            with open(RESPONSE_FIFO_PATH, "w") as response_fifo:
                full_message = fifo.read()
                if full_message.strip() == "exit":
                    os.remove(FIFO_PATH)
                    os.remove(RESPONSE_FIFO_PATH)
                    break
                elif full_message.startswith("/"):
                    chat.handle_command(full_message)
                    response_fifo.write("ack")
                    response_fifo.flush()  # Make sure the fifo is flushed
                else:
                    chat.stream_completion(
                        full_message, chat.params, response_fifo)


def main():
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        print("Please set OPENAI_API_KEY environment variable.")
        exit()

    config = create_chat_config()
    chat_service = ChatService(config=config)

    # Run the chatbot in the background
    t = threading.Thread(target=start_fifo_server, args=(chat_service,))
    t.daemon = True
    t.start()
    chat_service.start()

    while True:
        try:
            cmd = input().strip()
            if cmd == "exit":

                break
        except (KeyboardInterrupt, EOFError):
            break


if __name__ == "__main__":
    main()
