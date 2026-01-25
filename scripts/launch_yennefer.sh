#!/usr/bin/env bash
#
# launch_yennefer.sh - Launch Yennefer UI (hosted and/or local)
#
# Usage:
#   ./scripts/launch_yennefer.sh [OPTIONS]
#
# Options:
#   --no-open     Don't open the browser
#   --web-only    Only open hosted UI, skip local server
#   --dry-run     Print what would be executed without running
#   --help        Show this help message
#

set -euo pipefail

# Configuration
HOSTED_URL="https://yennefer.quest"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Flags
NO_OPEN=false
WEB_ONLY=false
DRY_RUN=false

# Colors (if terminal supports them)
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    PURPLE='\033[0;35m'
    NC='\033[0m' # No Color
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    PURPLE=''
    NC=''
fi

print_help() {
    cat << EOF
🔮 Yennefer Launcher

Usage: $(basename "$0") [OPTIONS]

Options:
  --no-open     Don't open the browser
  --web-only    Only open hosted UI, skip local server
  --dry-run     Print what would be executed without running
  --help        Show this help message

Examples:
  $(basename "$0")              # Open hosted UI + start local server
  $(basename "$0") --web-only   # Just open hosted UI
  $(basename "$0") --dry-run    # Preview commands

EOF
}

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}❌${NC} $1"
}

# Cross-platform browser opener
open_browser() {
    local url="$1"
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY-RUN] Would open: $url"
        return 0
    fi
    
    if [ "$NO_OPEN" = true ]; then
        log_info "Browser opening disabled. URL: $url"
        return 0
    fi
    
    log_info "Opening $url ..."
    
    case "$(uname -s)" in
        Darwin)
            open "$url"
            ;;
        Linux)
            if command -v xdg-open &> /dev/null; then
                xdg-open "$url" &> /dev/null &
            elif command -v python3 &> /dev/null; then
                python3 -m webbrowser "$url" &> /dev/null &
            else
                log_warn "No browser opener found. Please open manually: $url"
                return 1
            fi
            ;;
        MINGW*|MSYS*|CYGWIN*)
            cmd.exe /c start "" "$url" 2>/dev/null || python -m webbrowser "$url"
            ;;
        *)
            log_warn "Unknown OS. Please open manually: $url"
            return 1
            ;;
    esac
    
    log_success "Browser opened"
}

# Detect local UI stack
detect_ui() {
    local ui_type="none"
    local ui_path=""
    local ui_command=""
    local ui_port=""
    
    # Check for yennefer-observatory (Vite/React UI)
    if [ -f "$REPO_ROOT/yennefer-observatory/package.json" ]; then
        if grep -q '"dev"' "$REPO_ROOT/yennefer-observatory/package.json" 2>/dev/null; then
            ui_type="node-vite"
            ui_path="$REPO_ROOT/yennefer-observatory"
            ui_command="npm run dev"
            ui_port="5173"
        fi
    fi
    
    # Check root package.json for dev script
    if [ "$ui_type" = "none" ] && [ -f "$REPO_ROOT/package.json" ]; then
        if grep -q '"dev"' "$REPO_ROOT/package.json" 2>/dev/null; then
            ui_type="node"
            ui_path="$REPO_ROOT"
            ui_command="npm run dev"
            ui_port="3000"
        fi
    fi
    
    # Check for Python UI (streamlit/gradio)
    if [ "$ui_type" = "none" ]; then
        if [ -f "$REPO_ROOT/requirements.txt" ] || [ -f "$REPO_ROOT/pyproject.toml" ]; then
            # Look for streamlit
            if grep -qi "streamlit" "$REPO_ROOT/requirements.txt" 2>/dev/null; then
                local streamlit_app
                streamlit_app=$(find "$REPO_ROOT" -maxdepth 3 -name "app.py" -o -name "streamlit_app.py" 2>/dev/null | head -1)
                if [ -n "$streamlit_app" ]; then
                    ui_type="python-streamlit"
                    ui_path="$REPO_ROOT"
                    ui_command="streamlit run $streamlit_app --server.headless true"
                    ui_port="8501"
                fi
            fi
            # Look for gradio
            if [ "$ui_type" = "none" ] && grep -qi "gradio" "$REPO_ROOT/requirements.txt" 2>/dev/null; then
                local gradio_app
                gradio_app=$(find "$REPO_ROOT" -maxdepth 3 -name "app.py" -o -name "gradio_app.py" 2>/dev/null | head -1)
                if [ -n "$gradio_app" ]; then
                    ui_type="python-gradio"
                    ui_path="$REPO_ROOT"
                    ui_command="python $gradio_app"
                    ui_port="7860"
                fi
            fi
        fi
    fi
    
    # Check for yennefer-core Flask/FastAPI
    if [ "$ui_type" = "none" ] && [ -d "$REPO_ROOT/yennefer-core" ]; then
        if [ -f "$REPO_ROOT/yennefer-core/landing_server.py" ]; then
            ui_type="python-flask"
            ui_path="$REPO_ROOT/yennefer-core"
            ui_command="python landing_server.py"
            ui_port="8000"
        fi
    fi
    
    echo "$ui_type|$ui_path|$ui_command|$ui_port"
}

# Start local UI server
start_local_ui() {
    local ui_info="$1"
    local ui_type ui_path ui_command ui_port
    
    IFS='|' read -r ui_type ui_path ui_command ui_port <<< "$ui_info"
    
    if [ "$ui_type" = "none" ]; then
        log_info "No local UI detected; using hosted UI only."
        return 0
    fi
    
    log_info "Detected UI: $ui_type"
    log_info "Path: $ui_path"
    log_info "Command: $ui_command"
    log_info "Port: $ui_port"
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY-RUN] Would run: cd $ui_path && $ui_command"
        return 0
    fi
    
    echo ""
    log_info "Starting local UI server..."
    log_info "Local URL will be: http://localhost:$ui_port"
    echo ""
    
    cd "$ui_path"
    
    # Install dependencies if needed
    if [[ "$ui_type" == node* ]]; then
        if [ ! -d "node_modules" ]; then
            log_info "Installing Node dependencies..."
            npm install
        fi
    fi
    
    # Run the command
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${PURPLE}Starting: $ui_command${NC}"
    echo -e "${PURPLE}Press Ctrl+C to stop${NC}"
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    eval "$ui_command"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-open)
            NO_OPEN=true
            shift
            ;;
        --web-only)
            WEB_ONLY=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help|-h)
            print_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            print_help
            exit 1
            ;;
    esac
done

# Main execution
echo ""
echo -e "${PURPLE}🔮 Yennefer Launcher${NC}"
echo ""

# Always open hosted UI first
open_browser "$HOSTED_URL"

# Start local UI unless web-only mode
if [ "$WEB_ONLY" = false ]; then
    ui_info=$(detect_ui)
    start_local_ui "$ui_info"
else
    log_info "Web-only mode: skipping local UI"
fi

if [ "$DRY_RUN" = true ]; then
    log_success "[DRY-RUN] Complete - no changes made"
fi
