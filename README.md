# Work Environment Setup

Tools to check and install Frappe v16 development dependencies on Ubuntu 24.04+ or Debian 13+.

## Root scripts

| Script | Purpose |
|--------|---------|
| `start.sh` | Open the GUI to check versions and install selected dependencies |
| `upgrade.sh` | Run upgrade scripts from the terminal (no GUI) |

Run both from a terminal so `sudo` can prompt for your password when needed.

### `start.sh`

Opens the work environment checker GUI.

```bash
./start.sh
```

**Requires:** Python 3 and `tkinter` (`sudo apt install python3-tk`).

**What it does:**

- Compares installed versions on your machine against `versions.json`
- Shows **green** for OK, **red** for missing or outdated
- Lets you check dependencies and run **Update selected** or **Update all**
- Shows install output in the log panel at the bottom

**CLI alternative** (no GUI):

```bash
python3 check_env.py --cli
```

### `upgrade.sh`

Runs the per-dependency upgrade scripts without opening the GUI.

```bash
./upgrade.sh                  # upgrade everything (in order)
./upgrade.sh mariadb          # upgrade one dependency
./upgrade.sh git redis node   # upgrade several
./upgrade.sh --list           # list available dependency names
./upgrade.sh --help           # usage and list
```

**Available upgrades** (run `./upgrade.sh --list`):

| Name | What it installs |
|------|------------------|
| `git` | Git via apt |
| `mariadb` | MariaDB 11.8 (MariaDB.org repo + `mariadb-upgrade`) |
| `redis` | Redis via apt |
| `wkhtmltopdf` | wkhtmltopdf .deb + dependencies |
| `nvm` | Node Version Manager |
| `node` | Node.js 24 (via nvm) |
| `yarn` | Yarn (via npm) |
| `uv` | uv Python package manager |
| `python` | Python 3.14 (via uv) |
| `pip` | pip ≥ 25.3 |
| `bench` | frappe-bench CLI (via uv) |

Upgrade order matters when running everything: `nvm` before `node`/`yarn`, `uv` before `python`/`pip`/`bench`. `./upgrade.sh` with no arguments follows the correct order automatically.

Individual scripts live in `scripts/upgrades/` and can be run directly:

```bash
bash scripts/upgrades/mariadb.sh
```

## `versions.json`

Central config for required versions, how each dependency is checked, and which script installs it. Used by the GUI (`check_env.py`) and aligned with the upgrade scripts.

### Top-level fields

| Field | Description |
|-------|-------------|
| `frappe_version` | Label shown in the GUI (e.g. `v16`) |
| `description` | Short description of the config |
| `os_requirements` | Minimum OS versions (`ubuntu_min`, `debian_min`, `message`) |

### Dependency entry fields

Each object in `dependencies` describes one tool:

| Field | Description |
|-------|-------------|
| `id` | Short identifier (matches upgrade script name, e.g. `mariadb`) |
| `name` | Display name in the GUI |
| `required` | Human-readable requirement shown in the GUI (e.g. `11.8+`, `installed`) |
| `check` | How to detect the installed version: `command`, `os`, `nvm`, or `pip` |
| `command` | Command to run for `check: command` (e.g. `["mariadb", "--version"]`) |
| `pattern` | Regex to extract version from command output |
| `min_version` | Minimum version for pass/fail (e.g. `11.8.0`) |
| `updatable` | `false` to disable install checkbox (e.g. OS) |
| `install_hint` | Hint shown in the GUI when a row is selected |
| `install_script` | Path to upgrade script relative to project root (e.g. `scripts/upgrades/git.sh`) |

### Check types

| `check` | Behavior |
|---------|----------|
| `os` | Reads Ubuntu/Debian version via `lsb_release` |
| `command` | Runs `command`, parses version with `pattern` |
| `nvm` | Checks `~/.nvm/nvm.sh` exists and runs `nvm --version` |
| `pip` | Runs `python3 -m pip --version` |

### Example entry

```json
{
  "id": "mariadb",
  "name": "MariaDB",
  "required": "11.8+",
  "min_version": "11.8.0",
  "check": "command",
  "command": ["mariadb", "--version"],
  "pattern": "Distrib ([\\d.]+)-MariaDB",
  "install_hint": "scripts/upgrades/mariadb.sh",
  "install_script": "scripts/upgrades/mariadb.sh"
}
```

### Changing requirements

1. Edit `versions.json` (`required`, `min_version`, etc.)
2. Update the matching script in `scripts/upgrades/` if install steps need to change
3. Recheck with `./start.sh` or `python3 check_env.py --cli`

To add a new dependency: add an entry to `versions.json`, create `scripts/upgrades/<id>.sh`, and add `<id>` to the `ALL_UPGRADES` array in `scripts/upgrade_all.sh`.

## Project layout

```
setup_workenv/
├── start.sh              # GUI launcher
├── upgrade.sh            # CLI upgrade launcher
├── versions.json         # version requirements and install script paths
├── check_env.py          # checker entry point
├── env_checker/          # Python checker + GUI + installer
└── scripts/
    ├── upgrade_all.sh    # orchestrates all upgrade scripts
    ├── lib/common.sh     # shared shell helpers
    └── upgrades/         # one script per dependency
```

## `init_bench.sh` (standalone)

Separate from the checker/upgrade tools. Initializes a Frappe v16 bench, creates a site, clones `tevind_studio`, and installs it.

```bash
./init_bench.sh
./init_bench.sh -d /home/user/projects
./init_bench.sh --help
```

If `-d` is not passed, you are prompted for the parent directory (defaults to the current directory). The bench folder (`tevind_bench` by default) is created inside that path.

**What it runs:**

1. `bench init tevind_bench --frappe-branch version-16 --python <python3.14>`
2. `bench new-site tevind.localhost` (prompts for MariaDB `frappe` user password)
3. `bench get-app git@github.com:TeddyViberg/tevind_studio.git --branch master`
4. `bench --site tevind.localhost install-app tevind_studio`

**Requires:** `bench`, Python 3.14, MariaDB, and SSH access to the private GitHub repo.

Override defaults with flags (`--bench-name`, `--site`, `--db-user`, etc.) or environment variables. See `./init_bench.sh --help`.
