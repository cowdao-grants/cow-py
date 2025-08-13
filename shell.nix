with import <nixpkgs> {};

let
  python = pkgs.python311;

  poetry = pkgs.poetry.override {
    python3 = python;
  };
in

mkShell {
  NIX_LD_LIBRARY_PATH = lib.makeLibraryPath [
    nss
    sane-backends
    nspr
    zlib
    libglvnd
    gcc
    openssl
    openssl_legacy
    bzip2
    libffi
    readline
    libgcc
    ncurses
    stdenv.cc
    stdenv.cc.libc stdenv.cc.libc_dev
  ];

  buildInputs = [
    pkgs.poetry
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python311Packages.virtualenv
    pkgs.python311Packages.unicurses
    pkgs.python311Packages.gnureadline
    pkgs.python311Packages.pyopenssl
    pkgs.python311Packages.cython
    pkgs.python311Packages.cytoolz
    pkgs.pythonManylinuxPackages.manylinux2014Package
    pkgs.cmake
  ];

  # NIX_LD = builtins.readFile "${stdenv.cc}/nix-support/dynamic-linker";

  shellHook = ''
    set -e
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib.outPath}/lib:${pkgs.pythonManylinuxPackages.manylinux2014Package}/lib:$LD_LIBRARY_PATH";
    echo 'Spinning up Python Virtual Environment in .nix-venv directory 🐍'
    ${pkgs.python311.interpreter} -m venv .nix-venv
    export PATH=$PWD/.nix-venv/bin:$PATH
  '';
}

