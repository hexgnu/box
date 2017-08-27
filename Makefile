depends:
	sudo dnf install ansible python2-dnf libselinux-python
all:
	ansible-playbook -K -i hosts fedora.yml -vvv
