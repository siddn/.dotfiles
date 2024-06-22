export NEOVIM_PATH="$HOME/Software/nvim-linux64/bin/nvim"
alias vim="$NEOVIM_PATH"
export SUDO_EDITOR="$NEOVIM_PATH"
LS_COLORS=$LS_COLORS:'ow=1;34:' ; export LS_COLORS # Fixes LS colors in WSL
CD_COLORS=$CD_COLROS:'ow=1;34:' ; export CD_COLORS # Fixes CD colors in WSL

# Custom Aliases
source $HOME/.dotfiles/bash/custom_aliases

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/home/siddn/miniconda3/bin/conda' 'shell.zsh' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/home/siddn/miniconda3/etc/profile.d/conda.sh" ]; then
        . "/home/siddn/miniconda3/etc/profile.d/conda.sh"
    else
        export PATH="/home/siddn/miniconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<
export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="robbyrussell"
plugins=(git zsh-autosuggestions zsh-syntax-highlighting)
source $ZSH/oh-my-zsh.sh
