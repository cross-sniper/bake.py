#!/usr/bin/env python
import yaml
import json
import sys
import os

config = {}
# e.g:
""" (Keep this comment here)
target needs to build something else

[<target>, <other thing>]

if said other thing also needs something else

[<target>, <other thing>, <yet another thing>]

once its done, pop it

[<target>, <other thing>]

if we are back to the actual target, then we can proceed

"""
walkedtree = []
# to handle the case where something allready built something else
built_targets = set()  # Track which targets have already been built



def joinLibs(libs, joiner="-l"):
    if not libs:
        return ""
    return " ".join(f"{joiner}{l}" for l in libs)

def help():
    print("bake.py")
    print(
        "bake.py is meant to make it easier to build your projects(compared to makefile and cmake)"
    )
    print("how to use:")
    print(" python bake.py <name>")
    print("e.g:")
    print(" python bake.py main")
    print("targets: ")
    for target in config:
        print(f" - {target}", end="")
        if config[target].get("description"):
            print(f" | {config[target].get("description")}")
        else:
            print("") # to add the new line
        if config[target].get("dependsOn"):
            print("  ^ dependency tree:")
            print(f"    {" | ".join(config[target].get("dependsOn"))}")

    exit(0)


def loadConfig(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def build(target_name: str,argv=[]):
    # Check if we've already built this target
    if target_name in built_targets:
        return

    # If we're currently working on this target, there's a circular dependency
    if target_name in walkedtree:
        print(
            f"Circular dependency detected: {' -> '.join(walkedtree)} -> {target_name}"
        )
        exit(1)

    # Add this target to the current path
    walkedtree.append(target_name)
    target = config.get(target_name)
    if "-d" in argv:
        print(walkedtree)
    if target is None:
        print(f"Error: Target {target_name} not found.")
        exit(2)

    # Build dependencies first
    dependencies = target.get("dependsOn", [])
    for dep in dependencies:
        build(dep,argv)

    # Now build the current target
    compiler = target.get("compiler", "g++")
    src = target.get("src")
    output = target.get("output")
    libs = joinLibs(target.get("libs"))
    extraFlags = joinLibs(target.get("extraFlags", []), "-")
    linkWith = joinLibs(target.get("linkWith", []), "")

    # Construct and execute the build command
    build_command = f"{compiler} {src} -o {output} {linkWith} {libs} {extraFlags}"
    print(f"Building {target_name}: {build_command}")
    os.system(build_command)

    # Mark this target as built
    built_targets.add(target_name)

    # Remove from walkedtree (finished building)
    walkedtree.pop()


def main():
    global config
    config = loadConfig("bake.yml")

    if len(sys.argv) < 2:
        help()
        return 1

    target = sys.argv[1]
    if not config.get(target):
        print("Error: Target not found.")
        return 2

    build(target,sys.argv[1:])
    return 0


if __name__ == "__main__":
    exit(main())
