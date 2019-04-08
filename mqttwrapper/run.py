import sys

from .paho_backend import run_script

if __name__ == "__main__":
    try:
        from callback import callback
        run_script(callback)
    except ImportError:
        print("""Couldn't import callback function from callback module.
Please ensure there is a function called 'callback' defined in a file called callback.py in the current directory.""", file=sys.stderr)
