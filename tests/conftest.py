"""
Pytest configuration and shared fixtures for Free Range VHDL E2E tests.
"""

from pathlib import Path
import pytest

PROJECT_ROOT = Path("/home/abok-omen/Desktop/Abok/embedded/fpga_project").resolve()
CHAPTERS_DIR = PROJECT_ROOT / "chapters"

# Authoritative Table of Contents & Technical Ground Truth Specification
CHAPTER_SPECS = {
    1: {
        "filename": "chapter_01.md",
        "title_keywords": ["Introduction To VHDL", "Introduction to VHDL"],
        "essential_topics": [
            r"Golden Rules",
            r"Tools|Toolchain",
            r"Concurrency",
            r"Modeling|Synthesis|Simulation",
        ],
        "hardware_concepts": [
            r"concurr",
            r"synthes",
            r"simulat",
            r"golden rule",
        ],
    },
    2: {
        "filename": "chapter_02.md",
        "title_keywords": ["VHDL Invariants"],
        "essential_topics": [
            r"Case Sensitivity",
            r"Comments",
            r"Parentheses",
            r"Statements|Terminator",
            r"Identifier",
            r"Reserved",
        ],
        "hardware_concepts": [
            r"case\s+insensitiv",
            r"comment",
            r"elsif",
            r"identifier",
            r"reserved",
        ],
    },
    3: {
        "filename": "chapter_03.md",
        "title_keywords": ["VHDL Design Units"],
        "essential_topics": [
            r"Entity",
            r"Architecture",
            r"Port",
            r"Librar",
            r"Signal.*Variable|Variable.*Signal",
        ],
        "hardware_concepts": [
            r"entity",
            r"architecture",
            r"port",
            r"std_logic",
            r"numeric_std",
            r"signal",
            r"variable",
        ],
    },
    4: {
        "filename": "chapter_04.md",
        "title_keywords": ["VHDL Programming Paradigm"],
        "essential_topics": [
            r"Concurrent",
            r"Signal Assignment|<=|CSA",
            r"Conditional|when.*else",
            r"Selected|with.*select",
        ],
        "hardware_concepts": [
            r"concurrent",
            r"<=",
            r"when.*else",
            r"with.*select",
            r"intermediate signal",
        ],
    },
    5: {
        "filename": "chapter_05.md",
        "title_keywords": ["Standard Models in VHDL Architectures"],
        "essential_topics": [
            r"Data-flow",
            r"Behavioral",
            r"Process",
            r"Sequential",
            r"if|case",
            r"Latch",
        ],
        "hardware_concepts": [
            r"data-flow",
            r"behavioral",
            r"process",
            r"sensitiv",
            r"latch",
            r"case",
        ],
    },
    6: {
        "filename": "chapter_06.md",
        "title_keywords": ["VHDL Operators"],
        "essential_topics": [
            r"Operator",
            r"Storage|Memory",
            r"rising_edge|Edge",
            r"Reset|Synchronous|Asynchronous",
        ],
        "hardware_concepts": [
            r"operator",
            r"rising_edge",
            r"asynchronous",
            r"synchronous",
            r"flip-flop|storage",
        ],
    },
    7: {
        "filename": "chapter_07.md",
        "title_keywords": ["Finite State Machine Design"],
        "essential_topics": [
            r"FSM|State Machine",
            r"Moore|Mealy",
            r"One-Hot|Encoding",
        ],
        "hardware_concepts": [
            r"state machine|fsm",
            r"moore",
            r"mealy",
            r"one-hot",
            r"state_type|type.*state",
        ],
    },
    8: {
        "filename": "chapter_08.md",
        "title_keywords": ["Structural Modeling"],
        "essential_topics": [
            r"Component",
            r"Port Map",
            r"Generic",
        ],
        "hardware_concepts": [
            r"component",
            r"port\s+map",
            r"generic",
            r"structural",
        ],
    },
    9: {
        "filename": "chapter_09.md",
        "title_keywords": ["Registers and Register Transfer Level"],
        "essential_topics": [
            r"Register",
            r"RTL|Register Transfer Level",
        ],
        "hardware_concepts": [
            r"register",
            r"rtl|register transfer level",
            r"rising_edge",
            r"enable|load",
        ],
    },
    10: {
        "filename": "chapter_10.md",
        "title_keywords": ["Data Objects"],
        "essential_topics": [
            r"Signal.*Variable|Variable.*Signal",
            r"Type",
            r"numeric_std|Integer",
        ],
        "hardware_concepts": [
            r"signal",
            r"variable",
            r"delta",
            r"integer.*range",
            r"signed|unsigned",
        ],
    },
    11: {
        "filename": "chapter_11.md",
        "title_keywords": ["Looping Constructs"],
        "essential_topics": [
            r"Loop|for|while",
            r"Unroll|Control|next|exit",
        ],
        "hardware_concepts": [
            r"for.*loop",
            r"while",
            r"unroll",
            r"next",
            r"exit",
        ],
    },
    12: {
        "filename": "chapter_12.md",
        "title_keywords": ["Standard Digital Circuits"],
        "essential_topics": [
            r"Flip-Flop|Register",
            r"Counter",
            r"Shift Register|Comparator",
            r"Multiplexer|Decoder",
        ],
        "hardware_concepts": [
            r"flip-flop|dff",
            r"counter",
            r"shift register",
            r"multiplexer|mux",
            r"decoder",
        ],
    },
}


@pytest.fixture(scope="session")
def project_root() -> Path:
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def chapters_dir() -> Path:
    return CHAPTERS_DIR


@pytest.fixture(scope="session")
def chapter_specs():
    return CHAPTER_SPECS
