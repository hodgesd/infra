export PATH := justfile_directory() + "/env/bin:" + env_var("PATH")

# Recipes
@default:
  just --list

### Run/Builds
build_pro:
	ansible-playbook -u root -b run.yml --limit pro --ask-pass

build +HOST:
	ansible-playbook -b run.yml --limit {{ HOST }}

### Updates
update:
	ansible-playbook update.yml

docker:
	ansible-playbook docker.yml

test:
	ansible-playbook -b test.yml

### Vault
decrypt:
	ansible-vault decrypt vars/vault.yaml

encrypt:
	ansible-vault encrypt vars/vault.yaml

### Lint
yamllint:
    yamllint -s .

ansible-lint: yamllint
    #!/usr/bin/env bash
    ansible-lint .
    ansible-playbook run.yml update.yml bootstrap.yml docker.yml --syntax-check

### Bootstrap/Setup
bootstrap_pro:
	ansible-playbook -b bootstrap.yml --limit pro

bootstrap +HOST:
	ansible-playbook -b bootstrap.yml --limit {{ HOST }} --ask-pass --ask-become-pass

install:
	@./prereqs.sh
	@echo "Ansible Vault pre-hook script setup and vault password set"

### Git
# git submodule - repo URL + optional local folder name
add-submodule URL *NAME:
    #!/usr/bin/env sh
    if [ -z "{{NAME}}" ]; then
        # Extract repo name from URL if no name provided
        basename=$(basename "{{URL}}" .git)
        git submodule add {{URL}} "roles/${basename}"
        git submodule update --init --recursive
        git add .gitmodules "roles/${basename}"
        git commit -m "Adds ${basename} as a submodule"
    else
        git submodule add {{URL}} "roles/{{NAME}}"
        git submodule update --init --recursive
        git add .gitmodules "roles/{{NAME}}"
        git commit -m "Adds {{NAME}} as a submodule"
    fi