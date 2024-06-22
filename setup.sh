#! /usr/bin/bash

read -p "What type of system is this (1. Linux x86 2. WSL 3. ARM64)? " systype

# Get and link dotfiles github
# dotfiles_url="https://github.com/siddn/.dotfiles"
# git clone https://github.com/siddn/.dotfiles $HOME

# Get apt setup and install zsh
sudo apt update
sudo apt upgrade

# Install ZSH, Oh My ZSH, and Link up the .zshrc
/usr/bin/bash $HOME/.dotfiles/oh_my_zsh/zsh_setup.sh

# Install tmux and link files


# Install Conda/Python Stuff
miniconda_root_url="https://repo.anaconda.com/miniconda/"
if [ "$systype" = 3 ]; then
    conda_ext_url="Miniconda3-latest-Linux-aarch64.sh"
else
    conda_ext_url="Miniconda3-latest-Linux-x86_64.sh"
fi

miniconda_url="${miniconda_root_url}${conda_ext_url}"

curl -O $miniconda_url
sh $conda_ext_url -b -p $HOME/miniconda
source $HOME/miniconda/bin/activate
conda init --all
rm $conda_ext_url

