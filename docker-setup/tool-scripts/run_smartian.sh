#!/bin/bash

# Arg1 : Time limit
# Arg2 : Source file
# Arg3 : Bytecode file
# Arg4 : ABI file
# Arg5 : Main contract name
# Arg6 : Optional argument to pass

mkdir -p /home/test/output
dotnet /home/test/tools/Smartian/build/Smartian.dll fuzz \
  --useothersoracle -t $1 -p $3 -a $4 -v 1 $6 -o /home/test/output \
  > /home/test/output/log.txt 2>&1
