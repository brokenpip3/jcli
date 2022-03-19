# Jcli


Small cli to list, run, and check jenkins jobs

https://user-images.githubusercontent.com/40476330/159119721-a55d2f7c-7dff-4fa0-91cd-08f33a78494d.mp4


## Installation

`pip install jenkins-job-cli`

Archlinux users: you can find the pkgbuild [here](https://aur.archlinux.org/packages/jcli)

## Usage

* `config`: setup the `jcli` configuration

* `jobs`:
  * `list`: list all jenkins jobs (default deep = 1)
  * `run`: run a specific jenkins job

* `jenkins`: show jenkins server info like version (`version`) and security options (`info`)
