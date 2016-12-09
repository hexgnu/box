depends:
	sudo dnf install ansible python2-dnf
all:
	ansible-playbook -K -i hosts fedora.yml
