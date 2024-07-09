#!/bin/bash

set -e

cd /home/test/tools/SmarTest

# Install dependencies
opam init --disable-sandboxing -y
eval $(opam env)
opam install -y ocaml-lsp-server odoc ocamlformat\
    utop conf-m4.1 ocamlfind ocamlbuild num yojson batteries ocamlgraph zarith

# Install Z3
cd /home/test/tools
wget https://github.com/Z3Prover/z3/releases/download/z3-4.7.1/z3-4.7.1.tar.gz
tar -xvzf z3-4.7.1.tar.gz
rm -rf z3-4.7.1.tar.gz
cd /home/test/tools/z3rel
python3 /home/test/tools/z3rel/scripts/mk_make.py --ml --prefix="/home/test/.opam/default"

cd /home/test/tools/z3rel/build
eval $(opam env)
make -j 16

(sudo make install || true)
ocamlfind ocamlc -package num\
  -ccopt "-D_MP_INTERNAL -DNDEBUG -D_EXTERNAL_RELEASE -D_AMD64_ -D_USE_THREAD_LOCAL -fvisibility=hidden \\
  -c -mfpmath=sse -msse -msse2 -fopenmp -O3 -D_LINUX_ -fPIC -I /usr/lib/ocaml -I \\
  /home/test/tools/z3rel/src/api -I /home/test/tools/z3rel/src/api/ml -o api/ml/z3native_stubs.o" \
  -c /home/test/tools/z3rel/src/api/ml/z3native_stubs.c
(sudo make install || true)
sudo cp /home/test/tools/z3rel/build/libz3.so /lib
ocamlmklib -o api/ml/z3ml -I api/ml api/ml/z3native_stubs.o api/ml/z3enums.cmo\
    api/ml/z3native.cmo api/ml/z3.cmo  -L. -lz3
ocamlmklib -o api/ml/z3ml -I api/ml api/ml/z3native_stubs.o  api/ml/z3enums.cmx\
    api/ml/z3native.cmx api/ml/z3.cmx -L. -lz3
ocamlfind ocamlopt -package num -linkall -shared -o api/ml/z3ml.cmxs -I api/ml api/ml/z3ml.cmxa
(sudo make install || true)

# Install SmarTest
cd /home/test/tools/SmarTest
git init
git remote add origin https://github.com/kupl/VeriSmart-public.git
git pull origin master --allow-unrelated-histories
patch -p1 < /home/test/tools/SmarTest/SmarTest.patch 
chmod +x build
eval $(opam env)
./build