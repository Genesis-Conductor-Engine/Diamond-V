# Launch Yennefer

This document describes how to launch the Yennefer UI using the hosted service, GitHub Actions workflow, or local development scripts.

## Quick Reference

| Method | Best For | Link |
|--------|----------|------|
| **Hosted UI** | Immediate access, no setup | [yennefer.quest](https://yennefer.quest) |
| **GitHub Actions** | CI/CD integration, smoke testing | [Launch Workflow](../../actions/workflows/launch-yennefer-ui.yml) |
| **Local Scripts** | Development, customization | `./scripts/launch_yennefer.sh` |

---

## 🌐 Hosted UI

The simplest way to use Yennefer is through the hosted UI:

**URL:** https://yennefer.quest

Features:
- Always available
- No local setup required
- Connected to Base Mainnet
- Real-time soul state visualization

Click the "Launch Yennefer" badge at the top of the README to open it directly.

---

## ⚡ GitHub Actions Workflow

The Launch UI workflow provides automated UI detection and smoke testing.

### How to Use

1. Navigate to the [Actions tab](../../actions)
2. Select "Launch Yennefer UI" from the left sidebar
3. Click the **"Run workflow"** button (green button on the right)
4. Configure options:
   - **UI Mode**: `auto` (default), `web-only`, or `local-ui-smoke`
   - **Include hosted URL in summary**: `true` (default)
5. Click **"Run workflow"** to start

### What It Does

The workflow:
1. **Detects** the local UI stack (Node/Vite, Python/Streamlit, etc.)
2. **Installs** dependencies if a local UI is found
3. **Smoke tests** the local server (starts it, verifies it responds, stops it)
4. **Generates** a Job Summary with:
   - Link to the hosted UI
   - Detected local UI type and commands
   - Smoke test results

### Workflow Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `ui_mode` | choice | `auto` | Detection mode: `auto`, `web-only`, `local-ui-smoke` |
| `open_url` | boolean | `true` | Include hosted URL in job summary |

### Job Summary

After the workflow completes, click on the run to see the **Job Summary** which includes:
- Direct link to hosted UI
- Local UI detection results
- Commands to run the UI locally
- Smoke test status

---

## 🖥️ Local Launcher Scripts

For local development, use the launcher scripts that auto-detect and start the UI.

### Bash (Linux/macOS)

```bash
# Make executable (first time only)
chmod +x scripts/launch_yennefer.sh

# Launch (opens browser + starts local server)
./scripts/launch_yennefer.sh

# Options
./scripts/launch_yennefer.sh --web-only   # Only open hosted UI
./scripts/launch_yennefer.sh --no-open    # Don't open browser
./scripts/launch_yennefer.sh --dry-run    # Preview commands
./scripts/launch_yennefer.sh --help       # Show help
```

### PowerShell (Windows)

```powershell
# Launch (opens browser + starts local server)
.\scripts\launch_yennefer.ps1

# Options
.\scripts\launch_yennefer.ps1 -WebOnly    # Only open hosted UI
.\scripts\launch_yennefer.ps1 -NoOpen     # Don't open browser
.\scripts\launch_yennefer.ps1 -DryRun     # Preview commands
.\scripts\launch_yennefer.ps1 -Help       # Show help
```

### Command Reference

| Option | Bash | PowerShell | Description |
|--------|------|------------|-------------|
| Web only | `--web-only` | `-WebOnly` | Skip local server, just open hosted UI |
| No browser | `--no-open` | `-NoOpen` | Don't open browser automatically |
| Dry run | `--dry-run` | `-DryRun` | Preview commands without executing |
| Help | `--help` | `-Help` | Show usage information |

### Auto-Detection

The scripts automatically detect these UI stacks:

| Stack | Detection Method | Default Port |
|-------|------------------|--------------|
| Vite/React | `yennefer-observatory/package.json` with `"dev"` script | 5173 |
| Node.js | Root `package.json` with `"dev"` script | 3000 |
| Streamlit | `requirements.txt` contains `streamlit` + `app.py` exists | 8501 |
| Gradio | `requirements.txt` contains `gradio` + `app.py` exists | 7860 |
| Flask | `yennefer-core/landing_server.py` exists | 8000 |

---

## 🔧 Troubleshooting

### Port Already in Use

If you see "port already in use" errors:

```bash
# Find process using port (e.g., 5173)
lsof -i :5173  # Linux/macOS
netstat -ano | findstr :5173  # Windows

# Kill the process
kill -9 <PID>  # Linux/macOS
taskkill /PID <PID> /F  # Windows
```

### Dependencies Not Installing

Ensure you have the required tools:

```bash
# Node.js (check version)
node --version  # Should be v20+
npm --version

# Python (if using Python UI)
python --version  # Should be 3.10+
pip --version
```

### Browser Won't Open

If the browser doesn't open automatically:
- **Linux**: Ensure `xdg-open` is installed (`sudo apt install xdg-utils`)
- **macOS**: Should work with default `open` command
- **Windows**: Falls back to Python's `webbrowser` module

Alternatively, manually open: https://yennefer.quest

### Local UI Not Detected

If the script says "No local UI detected" but you have a UI:

1. Ensure you're running from the repository root
2. Check that `package.json` has a `"dev"` script
3. For Python, ensure `requirements.txt` exists with the framework name

### GitHub Actions Smoke Test Fails

If the smoke test times out:
1. The server may need more than 30 seconds to start
2. Check if the UI requires environment variables
3. Review the workflow logs for specific errors

---

## 📁 File Locations

| File | Purpose |
|------|---------|
| `scripts/launch_yennefer.sh` | Bash launcher script |
| `scripts/launch_yennefer.ps1` | PowerShell launcher script |
| `.github/workflows/launch-yennefer-ui.yml` | GitHub Actions workflow |
| `docs/LAUNCH_YENNEFER.md` | This documentation |

---

## 🔗 Related Links

- [Yennefer Quest (Hosted UI)](https://yennefer.quest)
- [GitHub Repository](https://github.com/Genesis-Conductor-Engine/Yennefer)
- [Main README](../README.md)
