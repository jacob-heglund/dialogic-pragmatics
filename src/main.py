"""Dialogic Pragmatics Inquiry Generator

This script allows the user to generate random material semantics frames and then generate inquiries of dialogic
pragmatic games from any material semantic frames.

Some comments:

in this script, I operate on indexes of sentences in the enumerated language whenever it's possible,
instead of operating on sentences as strings. Some functions, designed to be used by users, require inputting sentences
as strings. But those functions are considered as user-interface. Inside the engine, I'm always dealing with integers
as indexes of sentences.

I always work with frozensets instead of sets. I occasionally say sets for short, but it always means frozensets.

I always talk about enumerated language, which is represented as a list of strings in the script.
E.g. ['a_0', 'a_1', 'a_2'] would be an enumerated language with 3 sentences. So is ['red', 'Bob is nice', 'dsakfdsa'].

"""

import ast
from env.user_interface import UserInterface

import pdb


def main():
    lang = ['a_0', 'a_1', 'a_2', 'a_3', 'a_4', 'a_5', 'a_6']
    UserInterface(lang)


if __name__ == "__main__":
    main()
