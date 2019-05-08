depends:
	sudo dnf install ansible make automake gcc gcc-c++ kernel-devel python-unversioned-command libselinux-python
all:
	ansible-playbook -K -i hosts fedora.yml
