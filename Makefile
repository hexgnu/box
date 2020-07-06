depends:
	sudo dnf install ansible make
all:
	ansible-playbook -K -i hosts fedora.yml -vvvv
