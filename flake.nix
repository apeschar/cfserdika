{
  inputs = {
    poetry2nix.url = "github:nix-community/poetry2nix";
  };

  outputs = {
    self,
    poetry2nix,
  }: let
    eachSystem = f: builtins.mapAttrs (system: _: f system) poetry2nix.legacyPackages;
  in {
    packages = eachSystem (system: let
      app = poetry2nix.legacyPackages.${system}.mkPoetryApplication {
        projectDir = ./.;
      };
    in {default = app.dependencyEnv;});

    apps = eachSystem (system: {
      default = {
        type = "app";
        program = "${self.packages.${system}.default}/bin/cfserdika";
      };
    });

    devShell = eachSystem (system: let
      env = poetry2nix.legacyPackages.${system}.mkPoetryEnv {
        projectDir = ./.;
      };
    in
      env.env);
  };
}
