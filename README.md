# Jcli

Small cli to list, run, and check jenkins jobs

## Installation

`pip install jenkins-job-cli`

Archlinux users: you can find the pkgbuild [here](https://aur.archlinux.org/packages/jcli)

## Usage

* `config`: setup the `jcli` configuration

* `jobs`:
  * `list`: list all jenkins jobs (default deep = 1)
  * `run`: run a specific jenkins job

* `jenkins`: show jenkins server info like version (`version`) and security options (`info`)
