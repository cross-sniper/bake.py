import os
import subprocess

# Default variables
VARS = {"compiler": "g++"}

# Define functions
def set_var(name, val):
    VARS[name] = val
    print(f"'{name}' set to '{val}'")

def build_exe(source, name, libs=[], flags=[]):
    compiler = VARS.get('compiler', 'g++')
    command = [compiler, source, '-o', name] + libs + flags
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error building '{name}': {e}")
        exit(1)

# Initialize builtins dictionary
GLOBAL = {
    "__builtins__": {
        "build_exe": build_exe,
        "set": set_var,
        **VARS  # Include default variables in builtins
    }
}

def main():
    if not os.path.isfile("bake.conf"):
        print("Error: You need a bake.conf file")
        exit(1)
    
    with open("bake.conf") as f:
        build_conf = f.read()
    
    print(build_conf)
    
    try:
        exec(build_conf, GLOBAL)
    except Exception as e:
        print(f"Error executing build configuration: {e}")
        exit(1)

if __name__ == '__main__':
    main()
