# Free Range VHDL E2E Test Infrastructure Specification

## 1. Overview & Objective
This document specifies the architecture, components, test tiers, and operational procedures for the automated End-to-End (E2E) Test Suite validating technical chapter summaries of *Free Range VHDL* (Bryan Mealy & Fabrizio Tappero, Release 1.17).

The test harness enforces strict compliance with the core project requirements:
1. **Dense, High-Signal Technical Content**: Zero introductory fluff, zero elementary digital logic tutorials.
2. **Explicit Hardware Synthesis Semantics**: Concurrency, latch avoidance, sensitivity list effects, clock edge isolation, 2-process FSMs, signal vs. variable timing, and FPGA mapping.
3. **Syntactically Valid VHDL Code**: Extraction and formal compilation of all code snippets using the open-source **GHDL** compiler (`ghdl -s --std=08`).

---

## 2. Directory Layout & Artifacts

```
/home/abok-omen/Desktop/Abok/embedded/fpga_project/
├── pytest.ini                      # Pytest marker registration (tier1 - tier4)
├── TEST_INFRA.md                   # Infrastructure documentation (this file)
├── TEST_READY.md                   # Readiness publication artifact
├── chapters/                       # Authoritative chapter summaries
│   ├── chapter_01.md ... chapter_12.md
└── tests/                          # E2E Test Suite
    ├── __init__.py                 # Package declaration
    ├── conftest.py                 # Shared fixtures, paths, and TOC ground truth
    ├── vhdl_validator.py           # VHDL snippet extraction & GHDL compilation engine
    ├── test_chapters.py            # 4-tier Pytest test suite (147 test cases)
    └── run_tests.sh                # Executable CLI test runner with tier selection
```

---

## 3. The 4-Tier Test Architecture

The test suite is organized into four complementary validation tiers:

### Tier 1: Feature Coverage & Structural Integrity
- **Scope**: Structural existence, file naming, non-emptiness, and chapter table-of-contents alignment.
- **Test Classes**: `TestTier1FeatureCoverage`
- **Invariants Verified**:
  - `test_chapters_directory_exists`: Verifies `chapters/` directory exists.
  - `test_all_12_chapter_files_exist`: Verifies all files `chapter_01.md` through `chapter_12.md` exist.
  - `test_no_extraneous_chapter_files`: Rejects unexpected or misnamed files in `chapters/`.
  - `test_files_non_empty_and_substantive`: Ensures each chapter has $\ge 30$ substantive lines and $\ge 1000$ characters.
  - `test_top_level_headings_match_book_toc`: H1 heading (`# Chapter X: ...`) must match official book TOC titles.
  - `test_chapter_essential_subsections`: Sub-headings (`## `) must cover the essential core topics of each chapter.
- **Test Count**: 39 test cases.

### Tier 2: Boundary & Quality Cases
- **Scope**: Tone enforcement, fluff elimination, elementary logic gate prohibition, and code block formatting.
- **Test Classes**: `TestTier2QualityAndBoundary`
- **Invariants Verified**:
  - `test_no_introductory_filler_or_fluff`: Rejects textbook introductory filler phrases (e.g., *"In this chapter we will learn..."*, *"Welcome to VHDL"*, *"Let's get started"*).
  - `test_no_elementary_digital_logic_tutorials`: Rejects elementary gate tutorials (e.g., explaining basic AND/OR gate truth tables to an experienced FPGA engineer).
  - `test_code_blocks_use_vhdl_fence`: Enforces valid code block language specifiers (`vhdl`, `vhd`, `text`, `bash`).
  - `test_code_snippets_not_empty_or_placeholders`: Rejects empty code blocks or blocks containing only comments.
  - `test_code_snippets_no_truncation_markers`: Detects and rejects truncation markers (`...`, `// TODO`, `-- to be completed`) in synthesizable code examples.
- **Test Count**: 60 test cases.

### Tier 3: Technical Substance & Hardware Semantics
- **Scope**: FPGA architecture implications, synthesis vs. simulation semantics, and idioms.
- **Test Classes**: `TestTier3TechnicalSubstanceAndHardwareSemantics`
- **Invariants Verified**:
  - `test_hardware_synthesis_keywords_present`: Parameterized across all 12 chapters, checking for required hardware concept keywords.
  - `test_ch01_hardware_concurrency_and_golden_rules`: Concurrency paradigm, synthesis vs. simulation vs. modeling, Golden Rules of VHDL.
  - `test_ch02_vhdl_invariants_lexical_rules`: Case insensitivity, `--` comments, `elsif` keyword requirement, identifier naming rules.
  - `test_ch03_design_units_ports_and_std_logic`: Entity/architecture separation, port modes, `std_logic` 9-state system, standard `numeric_std` library.
  - `test_ch04_concurrent_signal_assignments_and_output_restriction`: Concurrent signal assignment `<=`, `when-else` priority logic, `with-select-when` balanced muxing, intermediate signals to overcome `out` port read limitations.
  - `test_ch05_processes_sequential_statements_and_latch_prevention`: Process containers, sensitivity lists, sequential `if`/`case`, latch avoidance / latch prevention.
  - `test_ch06_operators_storage_induction_and_edge_detection`: Operator precedence, `rising_edge()`, synchronous vs asynchronous resets, memory induction via incomplete specification.
  - `test_ch07_fsm_two_process_model_and_encoding`: 2-process FSM architecture (sync state register + comb next-state/output logic), Moore vs Mealy outputs, state enumeration, one-hot encoding.
  - `test_ch08_structural_modeling_and_generics`: Component declaration vs instantiation, named (`=>`) vs positional `port map`, `generic` and `generic map`.
  - `test_ch09_registers_rtl_and_clock_isolation`: Register inference via uncompleted `if`, clock-isolation nested `if`, multi-bit registers with load enable, multi-process RTL datapaths.
  - `test_ch10_data_objects_timing_and_numeric_std`: Signals (`<=`, delta delay) vs variables (`:=`, immediate update), constrained integer types for flip-flop sizing, `numeric_std` arithmetic vs `std_logic_vector` bit bundles.
  - `test_ch11_looping_constructs_hardware_unrolling`: Spatial hardware unrolling of `for` loops, non-synthesizability of unbounded `while` loops, implicit/immutable loop index, `next` and `exit` loop control.
  - `test_ch12_standard_digital_circuits`: Reference building blocks (DFFs, registers with enable, counters, shift registers, comparators, BCD decoders, MUXes, decoders), critique and correction of textbook quirks.
- **Test Count**: 24 test cases.

### Tier 4: VHDL Syntax Validation Engine
- **Scope**: Compiler validation of all extracted VHDL code snippets using GHDL.
- **Test Classes**: `TestTier4VhdlSyntaxValidation`
- **Engine Mechanics** (`tests/vhdl_validator.py`):
  1. **Snippet Extraction**: Parses Markdown AST and extracts all code blocks tagged ```` ```vhdl ```` or ```` ```vhd ````.
  2. **Multi-Strategy GHDL Compilation** (`ghdl -s --std=08` & `--std=93c`):
     - *Strategy 1*: Direct compilation for full design units (`entity` + `architecture`).
     - *Strategy 2*: Library injection (`library IEEE; use IEEE.std_logic_1164.all; use IEEE.numeric_std.all;`).
     - *Strategy 3*: Entity auto-synthesis for standalone architecture bodies.
     - *Strategy 4*: Architecture declarative wrapping for standalone type, signal, constant, or component declarations.
     - *Strategy 5*: Sensitized and unsensitized architectural wrapping for sequential processes and concurrent signal assignments.
     - *Strategy 6*: Recognition of intentional textbook errata / malformed negative examples (`-- TEXTBOOK ERRATUM`, `-- MALFORMED`).
  3. **Diagnostic Reporting**: Reports exact line numbers and GHDL compiler error diagnostics on failure.
- **Test Count**: 24 test cases.

---

## 4. Environment & Prerequisites

The test suite runs natively on Linux with:
- **Python**: $\ge 3.10$ (validated on Python 3.12.3)
- **Pytest**: $\ge 7.0$ (validated on pytest 7.4.4)
- **GHDL**: $\ge 4.0$ (validated on GHDL 4.1.0, Dunoon edition)

---

## 5. Execution Instructions

The test suite can be run via the shell runner or directly via pytest:

### Running via `tests/run_tests.sh`
```bash
# Run all 4 tiers
./tests/run_tests.sh

# Run specific tiers
./tests/run_tests.sh tier1   # Feature Coverage
./tests/run_tests.sh tier2   # Boundary & Quality Cases
./tests/run_tests.sh tier3   # Technical Substance & Hardware Semantics
./tests/run_tests.sh tier4   # VHDL Syntax Validation via GHDL

# Verbose output
./tests/run_tests.sh -v tier4
```

### Running via Pytest
```bash
# All tests
pytest tests/test_chapters.py

# Specific tier by marker
pytest -m tier1 tests/test_chapters.py
pytest -m tier2 tests/test_chapters.py
pytest -m tier3 tests/test_chapters.py
pytest -m tier4 tests/test_chapters.py
```

---

## 6. Current Validation Status & Baseline Metrics

| Tier | Category | Test Count | Pass Rate | Status |
|---|---|---|---|---|
| **Tier 1** | Feature Coverage | 39 | 100% (39/39) | **PASS** |
| **Tier 2** | Boundary & Quality | 60 | 100% (60/60) | **PASS** |
| **Tier 3** | Technical Substance | 24 | 100% (24/24) | **PASS** |
| **Tier 4** | VHDL Syntax (GHDL) | 24 | 100% (24/24) | **PASS** |
| **Total** | **Full E2E Suite** | **147** | **100% (147/147)** | **PASS** |
