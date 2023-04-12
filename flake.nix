{
  inputs = {
    poetry2nix.url = "github:nix-community/poetry2nix";
  };

  outputs = {
    self,
    poetry2nix,
  }: {
    devShell = builtins.mapAttrs (system: poetry2nix:
      (poetry2nix.mkPoetryEnv {
        projectDir = ./.;
      })
      .env)
    poetry2nix.legacyPackages;
  };
}
