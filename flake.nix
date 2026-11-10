{
  description = "Jev: macOS voice and AI assistant";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    nixpkgs-darwin-legacy.url = "github:NixOS/nixpkgs/nixpkgs-26.05-darwin";
  };

  outputs =
    {
      self,
      nixpkgs,
      nixpkgs-darwin-legacy,
    }:
    let
      version = builtins.replaceStrings [ "\n" ] [ "" ] (builtins.readFile ./VERSION);
      targetSystems = [
        "aarch64-darwin"
        "x86_64-darwin"
      ];
      forEachSystem =
        f:
        builtins.listToAttrs (
          map (system: {
            name = system;
            value = f system;
          }) targetSystems
        );
      pkgsFor =
        system:
        if system == "x86_64-darwin" then
          nixpkgs-darwin-legacy.legacyPackages.${system}
        else
          nixpkgs.legacyPackages.${system};
      packageFor =
        system:
        let
          pkgs = pkgsFor system;
        in
        pkgs.writeShellApplication {
          name = "jev";
          runtimeInputs = [ pkgs.python313 ];
          text = ''
            set -euo pipefail
            src=${./.}
            case "''${1:-}" in
              ""|install|--install|build|--build)
                exec bash "$src/build.sh"
                ;;
              --check)
                python3 -c 'import pathlib, sys; compile(pathlib.Path(sys.argv[1]).read_text(), sys.argv[1], "exec")' "$src/jev.py"
                bash -n "$src/build.sh"
                bash -n "$src/install.sh"
                printf '%s\n' 'jev source checks passed'
                ;;
              --version)
                printf '%s\n' "jev ${version}"
                ;;
              --help|-h|help)
                cat <<'EOF'
            Jev launcher for macOS.

            Usage:
              jev              Install or update Jev.app
              jev --install    Install or update Jev.app
              jev --check      Run packaged source checks
              jev --version    Print the packaged version
              jev --help       Show this help

            Building requires macOS 26 or later and Apple's command line tools.
            Full use also requires Claude Code (with Claude or a custom server), Devin, or Pi.
            EOF
                ;;
              *)
                printf 'Unknown option: %s\n\n' "$1" >&2
                exec "$0" --help
                ;;
            esac
          '';
          meta = with pkgs.lib; {
            description = "Jev macOS app launcher";
            homepage = "https://github.com/SaarthurR/atticus-mac";
            license = licenses.mit;
            mainProgram = "jev";
            platforms = targetSystems;
          };
        };
    in
    {
      packages = forEachSystem (
        system:
        let
          jev = packageFor system;
        in
        {
          inherit jev;
          atticus-mac = jev;
          source = jev;
          default = jev;
        }
      );

      apps = forEachSystem (
        system:
        let
          jev = self.packages.${system}.default;
          program = "${jev}/bin/jev";
          app = {
            type = "app";
            inherit program;
            inherit (jev) meta;
          };
        in
        {
          jev = app;
          atticus-mac = app;
          default = app;
        }
      );

      checks = forEachSystem (system: {
        package = self.packages.${system}.default;
      });

      devShells = forEachSystem (system: {
        default =
          let
            pkgs = pkgsFor system;
          in
          pkgs.mkShell {
            packages = [
              pkgs.python313
              pkgs.act
            ];
            shellHook = ''
              echo "Jev development shell. Building the app requires Apple's command line tools."
            '';
          };
      });

      formatter = forEachSystem (system: (pkgsFor system).nixfmt);
    };
}
