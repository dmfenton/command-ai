import argparse
from datetime import datetime
from os import path
from typing import NamedTuple
from chat_service import ChatCompletionParams, ChatConfig


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
