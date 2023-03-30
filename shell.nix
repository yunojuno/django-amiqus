# YunoJuno's Dev Environment
# ==========================
#
# We base our developer environment on Nix, the functional package
# manager and its sister package nix-shell which allows for per-
# directory "virtual environments".
#
# We use `nix-shell` alongside `direnv`, so that the environment
# gets loaded as soon as you enter the directory with your shell.
#
# We choose to use the rolling Nix Channel named `nixpgks-unstable`,
# as we stay fairly up-to-date with new versions of Python.
# Read more about Channels here: https://nixos.wiki/wiki/Nix_channels
#
#
# Re-pinning
# ----------
#
# Re-pinning is the act of updating which version of a specific
# channel (tree of packages) we are relying on at a given moment
# in time. If you require the Python & NodeJS versions to bump,
# re-pinning is what you want. The process is simple:
#
# 1. Visit https://status.nixos.org/
# 2. Record the `nixpkgs-unstable`.
# 3. Update the `fetchTarball` URL below with new commit.
# 4. Create a pull request, and mention new Py/JS versions.
#
# If you need to find out which exact version of a package is defined
# at which exact commit in the channel, use https://lazamar.co.uk/nix-versions/

{ pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/8ad5e8132c5dcf977e308e7bf5517cc6cc0bf7d8.tar.gz") {}
, lib ? pkgs.lib
, stdenv ? pkgs.stdenv
, frameworks ? pkgs.darwin.apple_sdk.frameworks
}:

let
    basePackages = [
        # Dev-env tooling
        pkgs.go-task

        # Python deps
        pkgs.python310
        pkgs.python310Packages.pip
        pkgs.poetry
        pkgs.pre-commit

        # for many deps
        pkgs.pkg-config
        pkgs.fontconfig
        pkgs.openssl

        # for lxml
        pkgs.libxml2.dev
        pkgs.libxslt.dev


    ];

    inputs = basePackages
        ++ lib.optional stdenv.isDarwin [
            pkgs.xcodebuild
        ] ++ lib.optional stdenv.isLinux [
            pkgs.stdenv.cc.cc.lib
            pkgs.libuuid.lib
        ];

    shellExports = "" + lib.optionalString stdenv.isLinux ''
        export LD_LIBRARY_PATH=${stdenv.cc.cc.lib}/lib/:${pkgs.libuuid.lib}/lib/
    '';

in pkgs.mkShell {

     nativeBuildInputs = inputs;

     # Needed to avoid error message when using fonts (weasyprint)
     FONTCONFIG_FILE = "${pkgs.fontconfig.out}/etc/fonts/fonts.conf";

     shellHook = shellExports + ''
        set -e

        # Setup the language & locale vars
        export LANG="en_GB.UTF-8"
        export LANGUAGE="en_GB.UTF-8"
        export LC_ALL="en_GB.UTF-8"

        # Allow the use of wheels.
        export SOURCE_DATE_EPOCH=$(date +%s)

        # TODO(remove): Mid-Jan 2022. This is cleanup that
        # will no longer be required as the file has moved.
        rm -f $(pwd)/poetry.lock.sha1

        # Force poetry to install the environment locally.
        # NB(darian) Do NOT remove this; poetry does not always
        # abide by poetry.toml's rule and this line stops it
        # ever snooping around your home files finding incorrect
        # environments from yesteryear.
        export POETRY_VIRTUALENVS_PATH=$(pwd)/.venv/

        # The poetry venv may have been setup under a different version
        # of Python, so we force it to switch to using the currently
        # installed nix-supplied version.
        poetry env use $(which python)

        echo ""
        echo ""
        echo "__     __                     _                   "
        echo "\ \   / /                    | |                  "
        echo " \ \_/ /   _ _ __   ___      | |_   _ _ __   ___  "
        echo "  \   / | | | '_ \ / _ \ _   | | | | | '_ \ / _ \ "
        echo "   | || |_| | | | | (_) | |__| | |_| | | | | (_) |"
        echo "   |_| \__,_|_| |_|\___/ \____/ \__,_|_| |_|\___/ "
        echo "   =============================================  "
        echo "   ========== Development Environment ==========  "
        echo "   ============== [`python --version`] =============  "
        echo ""

        # Install poetry deps if the poetry.lock has changed since
        # the last installation completed successfully.
        if ! sha1sum -c ./.venv/poetry.lock.sha1 --status --strict > /dev/null 2>&1
        then
            echo -e "    Python deps: \e[31mNeed update\e[0m, run 'task install-env'"
        else
            echo -e "    Python deps: \e[32mUp-to-date\e[0m"
        fi

        echo -e "    Run \e[36mtask\e[0m to see available commands            "

        echo ""
    '';
}
