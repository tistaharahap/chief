#!/bin/bash

# Chief-AI Installation Script
# Creates wrapper scripts for chen and chief commands

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Chief-AI Installation Script${NC}"
echo "=================================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${RED}Error: uv is not installed${NC}"
    echo "Please install uv first: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# Check if uvx is available
if ! command -v uvx &> /dev/null; then
    echo -e "${RED}Error: uvx is not available${NC}"
    echo "Please ensure you have a recent version of uv that includes uvx"
    exit 1
fi

# Create ~/.local/bin directory if it doesn't exist
LOCAL_BIN="$HOME/.local/bin"
if [ ! -d "$LOCAL_BIN" ]; then
    echo "Creating $LOCAL_BIN directory..."
    mkdir -p "$LOCAL_BIN"
fi

# Create chen wrapper script
CHEN_SCRIPT="$LOCAL_BIN/chen"
echo "Creating chen wrapper script..."
cat > "$CHEN_SCRIPT" << 'EOF'
#!/bin/bash
exec uvx --python 3.13 --from chief-ai chen "$@"
EOF

# Create chief wrapper script
CHIEF_SCRIPT="$LOCAL_BIN/chief"
echo "Creating chief wrapper script..."
cat > "$CHIEF_SCRIPT" << 'EOF'
#!/bin/bash
exec uvx --python 3.13 --from chief-ai chief "$@"
EOF

# Make scripts executable
chmod +x "$CHEN_SCRIPT"
chmod +x "$CHIEF_SCRIPT"

echo -e "${GREEN}✅ Installation complete!${NC}"
echo ""
echo -e "${YELLOW}Wrapper scripts created:${NC}"
echo "  - $CHEN_SCRIPT"
echo "  - $CHIEF_SCRIPT"
echo ""

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$LOCAL_BIN:"* ]]; then
    echo -e "${YELLOW}⚠️  Warning: $LOCAL_BIN is not in your PATH${NC}"
    echo ""
    echo "Add this line to your shell profile (~/.bashrc, ~/.zshrc, etc.):"
    echo -e "${GREEN}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
    echo ""
    echo "Then reload your shell:"
    echo -e "${GREEN}source ~/.bashrc${NC} (or source ~/.zshrc)"
    echo ""
else
    echo -e "${GREEN}✅ $LOCAL_BIN is already in your PATH${NC}"
    echo ""
fi

echo -e "${GREEN}You can now run:${NC}"
echo "  chen --help"
echo "  chief --help"
echo "  chen         # Start Chen (triggers onboarding on first run)"
echo ""
echo -e "${YELLOW}Note:${NC} On first run, uvx will download Python 3.13 and install chief-ai automatically."