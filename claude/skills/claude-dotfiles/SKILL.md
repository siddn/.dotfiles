---
name: claude-dotfiles
description: Explains and maintains the user's Claude Code dotfiles (the `claude/` folder of the ~/.dotfiles repo) and the install scripts (`install.sh`, `install.ps1`) that symlink them into ~/.claude. Use when the user wants to add or edit a global skill, change global CLAUDE.md or settings.json, run or debug the install script, sync Claude config between machines (macOS, Windows), or asks where Claude Code config lives.
---

# Claude dotfiles

The repo `~/.dotfiles` is the source of truth for the user's global Claude Code config. The folder `claude/` holds the files. The install scripts link them into `~/.claude`.

## Layout

```
~/.dotfiles/claude/
  CLAUDE.md          -> ~/.claude/CLAUDE.md      (global instructions)
  settings.json      -> ~/.claude/settings.json  (global settings)
  skills/<name>/     -> ~/.claude/skills/<name>  (one symlink per skill)
  install.sh                                     (macOS / Linux / Git Bash)
  install.ps1                                    (Windows PowerShell)
```

Other folders in `~/.dotfiles` (`nvim`, `tmux`, `prompt`, `bash`, `oh_my_zsh`) are not part of the Claude config. `setup.sh` in the repo root does not call the Claude install scripts.

## How the install scripts work

- The scripts create symlinks. They do not copy files.
- `CLAUDE_CONFIG_DIR` overrides the target. The default is `~/.claude`.
- For each target, the script does one of three things:
  - `ok`: the symlink already points to the repo. The script does nothing.
  - `backup`: a real file or a wrong link exists. The script renames it to `<name>.bak.<timestamp>`. Then it links.
  - `linked`: nothing exists. The script links.
- The scripts are safe to run again.
- The scripts link each skill on its own. They do not link `~/.claude/skills` as a whole. Claude Code keeps its own folders there (`synced/`, `.trash/`).
- `install.ps1` needs Developer Mode or an elevated shell to create symlinks.
- The scripts only add or fix links. They never remove a link for a deleted skill. Remove stale links by hand.

## Procedures

### Install or update on a machine

1. Pull the repo: `git -C ~/.dotfiles pull`.
2. Run the script for the platform:
   - macOS: `bash ~/.dotfiles/claude/install.sh`
   - Windows: `& $HOME\.dotfiles\claude\install.ps1`
3. Read the output. Find every `backup` line.
4. Clean up the backups (see "Clean up backups").

A new skill in `claude/skills/` appears in `~/.claude/skills` only after the script runs. Run it again after each new skill.

### Clean up backups

Do this after every install run that printed a `backup` line. Nothing else removes `.bak.*` files.

1. For each backup, compare it with the file it replaced. The live path is a symlink, so compare against the repo file:
   - File: `diff <backup> <live path>`
   - Skill folder: `diff -r <backup> <live path>`
2. If there is no difference, delete the backup.
3. If there is a difference, keep the backup. Show the user the diff. Ask whether to merge the changes into the repo file.
4. Delete a kept backup only after the user confirms. Merge first, run `diff` again, then delete.
5. Report which backups you deleted and which you kept.

Delete only `.bak.<timestamp>` files that the install script made. Do not delete other files in `~/.claude`.

### Add a global skill

1. Create `claude/skills/<name>/SKILL.md` with `name` and `description` frontmatter. The `name` must match the folder name.
2. Put helper files (scripts, `environment.yml`) in the same folder.
3. Run the install script to create the link.
4. Do not create skills directly in `~/.claude/skills`. The repo would not track them.
5. Commit and push when the user asks.

### Edit global CLAUDE.md or settings.json

1. Edit the file in `~/.dotfiles/claude/`. A linked `~/.claude` file is the same file.
2. For `settings.json`, check that the JSON is valid.
3. Tell the user that global instructions affect every project.

## Checks before you act

1. Check the platform (`uname` or `$env:OS`). Use the matching script.
2. Check the link state. Run `ls -la ~/.claude ~/.claude/skills` on macOS.
3. If `~/.claude/CLAUDE.md` or `settings.json` is a regular file, the install script has not replaced it yet. Compare it with the repo file using `diff` before you run the script.
   - Claude Code can write to `settings.json` itself (for example `/config`, model, theme). If the live file has extra keys, merge them into the repo file first. Otherwise the script moves them to a `.bak` file.
4. Do not use `--force` style fixes. Delete a `.bak` file only if it is identical to the repo file, or the user confirms.
5. Do not commit machine-specific settings (paths, tokens) to the repo.
6. Do not put secrets in `settings.json`. The repo may sync to a remote.

## Known state (verify; it can change)

- Repo skills: `figtheme`, `ste`, `claude-dotfiles`.
- `figtheme` has its own Conda environment file: `skills/figtheme/environment.yml`.
- The user uses macOS and Windows 11. Keep both install scripts in step. When you change one, change the other.
