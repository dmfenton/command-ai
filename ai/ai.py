#!/usr/bin/env python

import argparse
import os
from datetime import datetime
from os import path
from sys import stdout
from typing import NamedTuple, Optional
import threading
import openai
import errno
from chat_service import ChatCompletionParams, ChatConfig, ChatService

FIFO_PATH = "/tmp/chatbot_fifo"
RESPONSE_FIFO_PATH = "/tmp/chatbot_response_fifo"


def read_args() -> argparse.Namespace:
    """Create a CompletionParams object from command line arguments."""
    default = ChatCompletionParams()

    parser = argparse.ArgumentParser()

    parser.add_argument("-m", "--model", default=default.model)
    parser.add_argument("-M", "--max_tokens", type=int,
                        default=default.max_tokens)
    parser.add_argument("-t", "--temperature", type=float,
                        default=default.temperature)

    return parser.parse_args()


def create_chat_config() -> ChatConfig:
    context = load_context()

    args = read_args()
    params = ChatCompletionParams(**vars(args))

    config = ChatConfig(context=context, params=params)
    return config


def load_context() -> str:
    """Read the chat context from `~/.ai/context.txt` and return as a string."""
    home_dir = path.expanduser("~")
    context_file = path.join(home_dir, ".ai", "context.txt")

    context = ""

    now = datetime.now()
    current_time = now.strftime("%a, %b %d %Y %I:%M %p")
    timezone = now.astimezone().tzname()
    context += f"Current time: {current_time} {timezone}\n\n"

    if path.exists(context_file):
        with open(context_file, mode="r") as f:
            context += f.read().strip()
    else:
        context += f"The following is a conversation with an AI assistant that is running on the terminal of a MacOS computer."
    return context


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
                if full_message.startswith("/"):
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
