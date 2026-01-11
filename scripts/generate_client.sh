#!/usr/bin/env bash
#
# Generate Python API client from OpenAPI specification.
#
# Usage:
#   ./scripts/generate_client.sh [openapi_spec_path]
#
# Arguments:
#   openapi_spec_path  Path to OpenAPI YAML file (default: specs/openapi.yaml)
#

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEFAULT_SPEC_PATH="${PROJECT_ROOT}/specs/openapi.yaml"
OUTPUT_DIR="${PROJECT_ROOT}/src/generated_client"
CLIENT_NAME="mistral_client"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse arguments
SPEC_PATH="${1:-$DEFAULT_SPEC_PATH}"

# Validate spec file exists
if [[ ! -f "$SPEC_PATH" ]]; then
    log_error "OpenAPI spec not found at: $SPEC_PATH"
    exit 1
fi

log_info "Using OpenAPI spec: $SPEC_PATH"

# Check if openapi-python-client is available
if ! command -v uv &> /dev/null; then
    log_error "uv is not installed. Please install it first: https://docs.astral.sh/uv/"
    exit 1
fi

# Remove existing generated client
if [[ -d "$OUTPUT_DIR" ]]; then
    log_warn "Removing existing generated client at: $OUTPUT_DIR"
    rm -rf "$OUTPUT_DIR"
fi

# Generate the client
log_info "Generating Python client..."

cd "$PROJECT_ROOT"

# Use openapi-python-client to generate the client
uv run openapi-python-client generate \
    --path "$SPEC_PATH" \
    --output-path "$OUTPUT_DIR" \
    --overwrite

# Check if generation was successful
if [[ -d "$OUTPUT_DIR" ]]; then
    log_info "Client generated successfully at: $OUTPUT_DIR"

    # Create __init__.py if it doesn't exist
    if [[ ! -f "$OUTPUT_DIR/__init__.py" ]]; then
        echo '"""Generated Mistral API client."""' > "$OUTPUT_DIR/__init__.py"
    fi

    # Count generated files
    FILE_COUNT=$(find "$OUTPUT_DIR" -type f -name "*.py" | wc -l | tr -d ' ')
    log_info "Generated $FILE_COUNT Python files"
else
    log_error "Client generation failed - output directory not created"
    exit 1
fi

log_info "Done! You can now import the client from 'src.generated_client'"
