{
  inputs = {
    poetry2nix.url = "github:nix-community/poetry2nix";
  };

  outputs = {
    self,
    poetry2nix,
  }: {
    packages = builtins.mapAttrs (system: poetry2nix: let
      app = poetry2nix.mkPoetryApplication {
        projectDir = ./.;
      };
    in {default = app.dependencyEnv;})
    poetry2nix.legacyPackages;

    devShell = builtins.mapAttrs (system: poetry2nix: let
      env = poetry2nix.mkPoetryEnv {
        projectDir = ./.;
      };
    in
      env.env)
    poetry2nix.legacyPackages;
  };
}
