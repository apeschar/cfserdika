{
  inputs = {
    poetry2nix.url = "github:nix-community/poetry2nix";
    nixpkgs.follows = "poetry2nix/nixpkgs";
  };

  outputs = {
    self,
    poetry2nix,
    nixpkgs,
  }: let
    eachSystem = f:
      builtins.mapAttrs (system: _:
        f {
          inherit system;
          poetry2nix = poetry2nix.lib.mkPoetry2Nix {pkgs = nixpkgs.legacyPackages.${system};};
        })
      nixpkgs.legacyPackages;
  in {
    packages = eachSystem ({poetry2nix, ...}: let
      app = poetry2nix.mkPoetryApplication {
        projectDir = ./.;
      };
    in {default = app.dependencyEnv;});

    apps = eachSystem ({system, ...}: {
      default = {
        type = "app";
        program = "${self.packages.${system}.default}/bin/cfserdika";
      };
    });

    devShell = eachSystem ({poetry2nix, ...}: let
      env = poetry2nix.mkPoetryEnv {
        projectDir = ./.;
      };
    in
      env.env);
  };
}
