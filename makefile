marauder:
	ansible-playbook -b run.yaml --limit marauder --ask-become-pass

docker_host:
	ansible-playbook -b run.yaml --limit docker_host --ask-become-pass

docker:
	ansible-playbook -b run.yaml --limit docker --ask-become-pass

web:
	ansible-playbook -b run.yaml --limit web --ask-become-pass

dev:
	ansible-playbook -b run.yaml --limit dev --ask-become-pass

cdocker_host:
	ansible-playbook run.yaml --limit docker_host --tags compose

update:
	ansible-playbook update.yaml --limit servers 

reqs:
	ansible-galaxy install -r requirements.yaml

forcereqs:
	ansible-galaxy install -r requirements.yaml --force

decrypt:
	ansible-vault decrypt vars/vault.yaml

encrypt:
	ansible-vault encrypt vars/vault.yaml

venv:
	source /Users/derrickhodges/code/ansible/venv/bin/activate

gitinit:
	@./git-init.sh
	@echo "ansible vault pre-commit hook installed"
	@echo "don't forget to create a .vault-password too"
