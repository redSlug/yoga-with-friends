let
  pkgs = import (builtins.fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/0c19708cf035f50d28eb4b2b8e7a79d4dc52f6bb.tar.gz";
  }) {};
in pkgs.mkShell {
  packages = with pkgs; [
    nodejs_22
    python310
  ];
}