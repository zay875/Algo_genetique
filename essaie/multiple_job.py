print("Hello World!")

import sys
args = sys.argv[1:]
if (len(args) > 0):
    print(f"I am a python program running in a Slurm job having the index", args[0])
else:
    print("I am a python program running in a Slurm having no index")
