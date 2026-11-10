#!/usr/bin/env bash
# ==============================================================================
# Free Range VHDL E2E Test Suite Runner
# Runs 4 tiers of automated validation across chapter summaries.
# ==============================================================================

set -uo pipefail

PROJECT_DIR="/home/abok-omen/Desktop/Abok/embedded/fpga_project"
TESTS_DIR="${PROJECT_DIR}/tests"

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS] [TIER]

Automated test runner for Free Range VHDL technical chapter summaries.

Arguments:
  TIER                   Specific test tier to run (tier1, tier2, tier3, tier4, or 1..4).
                         Default: runs all tiers.

Options:
  -v, --verbose          Run pytest with verbose output (-vv)
  -q, --quiet            Run pytest in quiet mode
  -k EXPRESSION          Run tests matching given keyword expression
  -h, --help             Show this help message and exit

Tiers:
  tier1 (Feature)        Coverage: 12 chapter files exist, naming, non-empty, headings match TOC
  tier2 (Quality)        Boundary cases: no fluff/filler, no elementary tutorials, valid code blocks
  tier3 (Substance)      Hardware semantics: processes, latch avoidance, FSMs, registers, numeric_std
  tier4 (Syntax)         VHDL compiler validation: extracts code snippets and compiles with GHDL
EOF
}

TARGET_TIER=""
PYTEST_OPTS=("-rA" "--tb=short")

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            PYTEST_OPTS+=("-vv")
            shift
            ;;
        -q|--quiet)
            PYTEST_OPTS+=("-q")
            shift
            ;;
        -k)
            if [[ -n "${2:-}" ]]; then
                PYTEST_OPTS+=("-k" "$2")
                shift 2
            else
                echo -e "${RED}Error: -k requires an argument${NC}" >&2
                exit 1
            fi
            ;;
        tier1|1)
            TARGET_TIER="tier1"
            shift
            ;;
        tier2|2)
            TARGET_TIER="tier2"
            shift
            ;;
        tier3|3)
            TARGET_TIER="tier3"
            shift
            ;;
        tier4|4)
            TARGET_TIER="tier4"
            shift
            ;;
        all)
            TARGET_TIER=""
            shift
            ;;
        *)
            echo -e "${RED}Unknown option or tier: $1${NC}" >&2
            show_help
            exit 1
            ;;
    esac
done

echo -e "${CYAN}${BOLD}========================================================================${NC}"
echo -e "${CYAN}${BOLD}        Free Range VHDL Summary Validation Suite (4 Tiers)              ${NC}"
echo -e "${CYAN}${BOLD}========================================================================${NC}"

# Check environment tools
PYTHON_BIN="$(which python3 || true)"
PYTEST_BIN="$(which pytest || true)"
GHDL_BIN="$(which ghdl || true)"

echo -e "${BOLD}Environment:${NC}"
echo -e "  Python:  ${PYTHON_BIN:-not found} ($(${PYTHON_BIN} --version 2>&1 || echo 'N/A'))"
echo -e "  Pytest:  ${PYTEST_BIN:-not found} ($(${PYTEST_BIN} --version 2>&1 | head -n 1 || echo 'N/A'))"
echo -e "  GHDL:    ${GHDL_BIN:-not found} ($(${GHDL_BIN} --version 2>&1 | head -n 1 || echo 'N/A'))"

if [[ -z "${PYTHON_BIN}" || -z "${PYTEST_BIN}" ]]; then
    echo -e "${RED}${BOLD}Fatal: python3 and pytest are required to run this suite.${NC}" >&2
    exit 2
fi

cd "${PROJECT_DIR}"

# Build pytest marker argument
if [[ -n "${TARGET_TIER}" ]]; then
    echo -e "${BLUE}${BOLD}Running Target:${NC} ${TARGET_TIER}"
    PYTEST_OPTS+=("-m" "${TARGET_TIER}")
else
    echo -e "${BLUE}${BOLD}Running Target:${NC} All Tiers (Tier 1, Tier 2, Tier 3, Tier 4)"
fi

echo -e "${CYAN}------------------------------------------------------------------------${NC}"

# Execute tests
PYTHONPATH="${PROJECT_DIR}" "${PYTEST_BIN}" "${TESTS_DIR}/test_chapters.py" "${PYTEST_OPTS[@]}"
EXIT_CODE=$?

echo -e "${CYAN}------------------------------------------------------------------------${NC}"
if [[ ${EXIT_CODE} -eq 0 ]]; then
    echo -e "${GREEN}${BOLD}✓ ALL TEST CHECKS PASSED SUCCESSFULLY${NC}"
else
    echo -e "${RED}${BOLD}✗ TEST SUITE FAILED (exit code: ${EXIT_CODE})${NC}"
fi
echo -e "${CYAN}${BOLD}========================================================================${NC}"

exit ${EXIT_CODE}
