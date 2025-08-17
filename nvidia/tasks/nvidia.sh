#!/usr/bin/env bash

sudo dnf upgrade --refresh

sudo dnf autoremove nvidia* --purge

sudo /usr/bin/nvidia-uninstall

sudo /usr/local/cuda-X.Y/bin/cuda-uninstall

sudo dnf config-manager --add-repo https://developer.download.nvidia.com/compute/cuda/repos/fedora37/x86_64/cuda-fedora37.repo

sudo dnf install kernel-headers kernel-devel tar bzip2 make automake gcc gcc-c++ pciutils elfutils-libelf-devel libglvnd-opengl libglvnd-glx libglvnd-devel acpid pkgconfig dkms

sudo dnf module install nvidia-driver:latest-dkms
