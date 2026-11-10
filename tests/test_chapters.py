"""
Comprehensive 4-Tier Automated Test Suite for Free Range VHDL Technical Summaries.

Tiers:
- Tier 1: Feature Coverage (Files exist, naming, non-empty, headings match TOC)
- Tier 2: Boundary & Quality Cases (No fluff/filler, no basic gate tutorials, proper code fences, non-empty snippets, no truncation)
- Tier 3: Technical Substance & Hardware Semantics (Explicit hardware implications, concurrency, latches, sensitivity lists, 2-process FSM, registers, numeric_std)
- Tier 4: VHDL Syntax Validation (Extracts snippets and validates with GHDL compiler)
"""

import os
from pathlib import Path
import re
import pytest

from tests.vhdl_validator import (
    extract_vhdl_snippets,
    strip_vhdl_comments,
    check_truncation_markers,
    check_syntax_traps,
    validate_vhdl_with_ghdl,
)

# Helper function to read a chapter file
def get_chapter_path(chapters_dir: Path, chapter_num: int) -> Path:
    return chapters_dir / f"chapter_{chapter_num:02d}.md"

def read_chapter(chapters_dir: Path, chapter_num: int) -> str:
    path = get_chapter_path(chapters_dir, chapter_num)
    if not path.exists():
        pytest.fail(f"Required chapter summary file does not exist: {path}")
    return path.read_text(encoding="utf-8")


# ==============================================================================
# Tier 1: Feature Coverage
# ==============================================================================
@pytest.mark.tier1
class TestTier1FeatureCoverage:
    """Verifies that all 12 chapters are present, correctly named, non-empty, and structurally mapped to the book TOC."""

    def test_chapters_directory_exists(self, chapters_dir: Path):
        """The chapters/ directory must exist."""
        assert chapters_dir.exists(), f"Missing required directory: {chapters_dir}"
        assert chapters_dir.is_dir(), f"Expected {chapters_dir} to be a directory"

    def test_all_12_chapter_files_exist(self, chapters_dir: Path):
        """All 12 files (chapter_01.md to chapter_12.md) must be present."""
        if not chapters_dir.exists():
            pytest.fail(f"Directory {chapters_dir} does not exist.")
        missing = []
        for i in range(1, 13):
            expected = chapters_dir / f"chapter_{i:02d}.md"
            if not expected.exists():
                missing.append(f"chapter_{i:02d}.md")
        assert not missing, f"Missing {len(missing)} required chapter file(s): {', '.join(missing)}"

    def test_no_extraneous_chapter_files(self, chapters_dir: Path):
        """No extraneous or misnamed markdown files in chapters/."""
        if not chapters_dir.exists():
            pytest.skip("chapters directory not created yet")
        allowed = {f"chapter_{i:02d}.md" for i in range(1, 13)}
        present_md = {f.name for f in chapters_dir.glob("*.md")}
        extraneous = present_md - allowed
        assert not extraneous, f"Extraneous markdown file(s) found in chapters/: {extraneous}"

    @pytest.mark.parametrize("chapter_num", range(1, 13))
    def test_files_non_empty_and_substantive(self, chapters_dir: Path, chapter_num: int):
        """Each chapter file must be non-empty and substantive (> 30 lines, > 1000 characters)."""
        content = read_chapter(chapters_dir, chapter_num)
        lines = [line for line in content.splitlines() if line.strip()]
        assert len(content) >= 1000, f"Chapter {chapter_num:02d} content too short ({len(content)} chars < 1000 chars)"
        assert len(lines) >= 30, f"Chapter {chapter_num:02d} has too few non-empty lines ({len(lines)} < 30)"

    @pytest.mark.parametrize("chapter_num", range(1, 13))
    def test_top_level_headings_match_book_toc(self, chapters_dir: Path, chapter_specs: dict, chapter_num: int):
        """Top-level H1 heading must match the chapter title from the book TOC."""
        content = read_chapter(chapters_dir, chapter_num)
        spec = chapter_specs[chapter_num]
        
        # Look for # Chapter ... or # Title
        h1_matches = re.findall(r"^#\s+(.+)$", content, re.MULTILINE)
        assert h1_matches, f"Chapter {chapter_num:02d} missing top-level '# ' heading"
        
        h1_text = h1_matches[0]
        # Verify title keywords
        matched = any(kw.lower() in h1_text.lower() for kw in spec["title_keywords"])
        assert matched, (
            f"Chapter {chapter_num:02d} top-level heading '{h1_text}' does not match expected "
            f"title keywords: {spec['title_keywords']}"
        )

    @pytest.mark.parametrize("chapter_num", range(1, 13))
    def test_chapter_essential_subsections(self, chapters_dir: Path, chapter_specs: dict, chapter_num: int):
        """Each chapter must have section headings covering the essential topics from the book."""
        content = read_chapter(chapters_dir, chapter_num)
        spec = chapter_specs[chapter_num]
        headings = re.findall(r"^#{1,3}\s+(.+)$", content, re.MULTILINE)
        heading_text = " ".join(headings).lower()

        missing_topics = []
        for topic_pat in spec["essential_topics"]:
            if not re.search(topic_pat, heading_text, re.IGNORECASE):
                missing_topics.append(topic_pat)

        assert not missing_topics, (
            f"Chapter {chapter_num:02d} is missing headings for essential topics: {missing_topics}. "
            f"Found headings: {headings[:6]}..."
        )


# ==============================================================================
# Tier 2: Boundary & Quality Cases
# ==============================================================================
@pytest.mark.tier2
class TestTier2QualityAndBoundary:
    """Verifies that summaries avoid beginner fluff and elementary logic tutorials, and use correct formatting."""

    FLUFF_PATTERNS = [
        r"\bin this chapter\b.*?\b(?:we will|you will|i will|we'll|we shall)\b",
        r"\bwelcome to vhdl\b",
        r"\bthis chapter introduces the basics\b",
        r"\blet'?s get started\b",
        r"\bas we all know\b",
        r"\bin the previous chapter we\b",
        r"\bthis chapter is designed to\b",
        r"\bhope you enjoy\b",
    ]

    TUTORIAL_PATTERNS = [
        r"\ban AND gate (?:outputs|produces|yields) (?:a\s+)?1 (?:when|if|only if) both\b",
        r"\ban OR gate (?:outputs|produces|yields) (?:a\s+)?1 if either\b",
        r"\btruth table of an? (?:and|or|not|xor) gate\b",
        r"\bwhat is a binary digit\b",
        r"\ba 1 represents high voltage and 0 represents ground\b",
    ]

    @pytest.mark.parametrize("chapter_num", range(1, 13))
    def test_no_introductory_filler_or_fluff(self, chapters_dir: Path, chapter_num: int):
        """Summaries must NOT contain beginner fluff or introductory filler."""
        content = read_chapter(chapters_dir, chapter_num)
        # Check against prohibited filler patterns
        for pattern in self.FLUFF_PATTERNS:
            match = re.search(pattern, content, re.IGNORECASE)
            assert not match, (
                f"Chapter {chapter_num:02d} contains prohibited introductory filler: '{match.group(0)}'. "
                f"Content must be dense, direct, and tailored for experienced engineers."
            )

    @pytest.mark.parametrize("chapter_num", range(1, 13))
    def test_no_elementary_digital_logic_tutorials(self, chapters_dir: Path, chapter_num: int):
        """Summaries must NOT explain elementary boolean logic gates to experienced readers."""
        content = read_chapter(chapters_dir, chapter_num)
        for pattern in self.TUTORIAL_PATTERNS:
            match = re.search(pattern, content, re.IGNORECASE)
            assert not match, (
                f"Chapter {chapter_num:02d} contains elementary digital logic tutorial content: '{match.group(0)}'. "
                f"Target audience already has digital/FPGA background."
            )

    @pytest.mark.parametrize("chapter_num", range(1, 13))
    def test_code_blocks_use_vhdl_fence(self, chapters_dir: Path, chapter_num: int):
        """All code blocks must use proper fenced syntax with 'vhdl' or 'vhd' language specifier."""
        content = read_chapter(chapters_dir, chapter_num)
        fences = re.findall(r"^```\s*(\w*)\s*$", content, re.MULTILINE)
        
        # Must have at least one code fence in the file
        assert len(fences) >= 2, f"Chapter {chapter_num:02d} has no fenced code blocks"
        
        # Check opening fences
        opening_fences = fences[0::2]
        has_vhdl_fence = any(lang.lower() in ("vhdl", "vhd") for lang in opening_fences)
        assert has_vhdl_fence, f"Chapter {chapter_num:02d} must have at least one code block tagged with '```vhdl'"

        for lang in opening_fences:
            assert lang.lower() in ("vhdl", "vhd", "bash", "text", "none", ""), (
                f"Chapter {chapter_num:02d} contains code block with disallowed language tag: '```{lang}'"
            )

    @pytest.mark.parametrize("chapter_num", range(1, 13))
    def test_code_snippets_not_empty_or_placeholders(self, chapters_dir: Path, chapter_num: int):
        """VHDL code blocks must not be empty or purely comment placeholders."""
        content = read_chapter(chapters_dir, chapter_num)
        snippets = extract_vhdl_snippets(content)
        assert snippets, f"Chapter {chapter_num:02d} has no extractable ```vhdl code blocks"
        
        for snippet in snippets:
            clean = strip_vhdl_comments(snippet["code"]).strip()
            assert clean, (
                f"Chapter {chapter_num:02d} at line {snippet['line_number']} contains an empty "
                f"or comment-only VHDL code block"
            )

    @pytest.mark.parametrize("chapter_num", range(1, 13))
    def test_code_snippets_no_truncation_markers(self, chapters_dir: Path, chapter_num: int):
        """VHDL code snippets must not contain truncation markers like '...' or '-- TODO'."""
        content = read_chapter(chapters_dir, chapter_num)
        snippets = extract_vhdl_snippets(content)
        for snippet in snippets:
            markers = check_truncation_markers(snippet["code"])
            assert not markers, (
                f"Chapter {chapter_num:02d} contains truncation markers in VHDL snippet at line {snippet['line_number']}:\n"
                + "\n".join(markers)
            )


# ==============================================================================
# Tier 3: Technical Substance & Hardware Semantics
# ==============================================================================
@pytest.mark.tier3
class TestTier3TechnicalSubstanceAndHardwareSemantics:
    """Verifies that chapters thoroughly address synthesized hardware architecture implications."""

    @pytest.mark.parametrize("chapter_num", range(1, 13))
    def test_hardware_synthesis_keywords_present(self, chapters_dir: Path, chapter_specs: dict, chapter_num: int):
        """Every chapter must explicitly contain required hardware synthesis keywords."""
        content = read_chapter(chapters_dir, chapter_num)
        spec = chapter_specs[chapter_num]
        missing_concepts = []
        for pat in spec["hardware_concepts"]:
            if not re.search(pat, content, re.IGNORECASE):
                missing_concepts.append(pat)
        assert not missing_concepts, (
            f"Chapter {chapter_num:02d} is missing required hardware architecture concepts: {missing_concepts}"
        )

    def test_ch01_hardware_concurrency_and_golden_rules(self, chapters_dir: Path):
        """Chapter 1 must contrast hardware concurrency with software sequentiality, and cover golden rules."""
        content = read_chapter(chapters_dir, 1)
        assert re.search(r"concurr", content, re.IGNORECASE), "Ch 1 must explain hardware concurrency"
        assert re.search(r"sequential", content, re.IGNORECASE), "Ch 1 must contrast with sequential software"
        assert re.search(r"golden rule", content, re.IGNORECASE), "Ch 1 must present the Golden Rules of VHDL"
        assert re.search(r"synthesis|synthesiz", content, re.IGNORECASE), "Ch 1 must explain synthesis"

    def test_ch02_vhdl_invariants_lexical_rules(self, chapters_dir: Path):
        """Chapter 2 must document case insensitivity, comments, elsif, and identifier rules."""
        content = read_chapter(chapters_dir, 2)
        assert re.search(r"case\s+insensitiv", content, re.IGNORECASE), "Ch 2 must explain case insensitivity"
        assert "--" in content, "Ch 2 must explain single-line comment '--' syntax"
        assert re.search(r"\belsif\b", content, re.IGNORECASE), "Ch 2 must emphasize 'elsif' keyword requirement"
        assert re.search(r"identifier", content, re.IGNORECASE), "Ch 2 must cover identifier rules"

    def test_ch03_design_units_ports_and_std_logic(self, chapters_dir: Path):
        """Chapter 3 must cover entity/architecture separation, port modes, std_logic 9-state system, and numeric_std."""
        content = read_chapter(chapters_dir, 3)
        assert re.search(r"entity", content, re.IGNORECASE) and re.search(r"architecture", content, re.IGNORECASE)
        assert re.search(r"\bport\b", content, re.IGNORECASE)
        assert re.search(r"\bstd_logic\b", content, re.IGNORECASE)
        assert re.search(r"9-value|nine-value|'U'|'X'|'Z'", content, re.IGNORECASE), "Ch 3 must mention std_logic 9-value system"
        assert re.search(r"numeric_std", content, re.IGNORECASE), "Ch 3 must specify standard IEEE.numeric_std"

    def test_ch04_concurrent_signal_assignments_and_output_restriction(self, chapters_dir: Path):
        """Chapter 4 must cover concurrent <=, conditional when-else, selected with-select, and intermediate signal idiom."""
        content = read_chapter(chapters_dir, 4)
        assert re.search(r"when\s+.*?else", content, re.IGNORECASE), "Ch 4 must detail conditional signal assignment (when-else)"
        assert re.search(r"with\s+.*?select", content, re.IGNORECASE), "Ch 4 must detail selected signal assignment (with-select)"
        assert re.search(r"when\s+others", content, re.IGNORECASE), "Ch 4 must explain when others requirement"
        assert re.search(r"intermediate\s+signal|read\s+(?:back\s+)?out\s+port", content, re.IGNORECASE), (
            "Ch 4 must document intermediate signals for entity output port read limitation"
        )

    def test_ch05_processes_sequential_statements_and_latch_prevention(self, chapters_dir: Path):
        """Chapter 5 must cover process semantics, sensitivity list, sequential if/case, and latch avoidance."""
        content = read_chapter(chapters_dir, 5)
        assert re.search(r"process", content, re.IGNORECASE)
        assert re.search(r"sensitiv", content, re.IGNORECASE), "Ch 5 must explain sensitivity lists"
        assert re.search(r"latch", content, re.IGNORECASE), "Ch 5 must address unintended latch inference"
        assert re.search(r"\bif\b", content, re.IGNORECASE) and re.search(r"\bcase\b", content, re.IGNORECASE)

    def test_ch06_operators_storage_induction_and_edge_detection(self, chapters_dir: Path):
        """Chapter 6 must cover operator precedence, rising_edge, synchronous vs asynchronous resets, and storage induction."""
        content = read_chapter(chapters_dir, 6)
        assert re.search(r"operator", content, re.IGNORECASE)
        assert re.search(r"rising_edge", content, re.IGNORECASE), "Ch 6 must specify rising_edge() function"
        assert re.search(r"asynchronous", content, re.IGNORECASE) and re.search(r"synchronous", content, re.IGNORECASE), (
            "Ch 6 must compare synchronous and asynchronous reset mechanisms"
        )

    def test_ch07_fsm_two_process_model_and_encoding(self, chapters_dir: Path):
        """Chapter 7 must cover 2-process FSM model, Moore vs Mealy outputs, state enumeration, and one-hot encoding."""
        content = read_chapter(chapters_dir, 7)
        assert re.search(r"two-process|2-process|sync.*comb", content, re.IGNORECASE), "Ch 7 must present the 2-process FSM architecture"
        assert re.search(r"moore", content, re.IGNORECASE) and re.search(r"mealy", content, re.IGNORECASE), (
            "Ch 7 must distinguish Moore and Mealy outputs"
        )
        assert re.search(r"one-hot|1-hot", content, re.IGNORECASE), "Ch 7 must explain one-hot state encoding"

    def test_ch08_structural_modeling_and_generics(self, chapters_dir: Path):
        """Chapter 8 must cover components, port map (positional vs named), and generics."""
        content = read_chapter(chapters_dir, 8)
        assert re.search(r"component", content, re.IGNORECASE), "Ch 8 must explain component declaration"
        assert re.search(r"port\s+map", content, re.IGNORECASE), "Ch 8 must explain port map"
        assert re.search(r"generic(?:\s+map)?", content, re.IGNORECASE), "Ch 8 must explain generics"
        assert re.search(r"named|positional", content, re.IGNORECASE), "Ch 8 must contrast named vs positional port mapping"

    def test_ch09_registers_rtl_and_clock_isolation(self, chapters_dir: Path):
        """Chapter 9 must cover register inference, clock-isolation nested if, and RTL datapath vs control."""
        content = read_chapter(chapters_dir, 9)
        assert re.search(r"register", content, re.IGNORECASE)
        assert re.search(r"rtl|register\s+transfer\s+level", content, re.IGNORECASE), "Ch 9 must cover RTL architecture"
        assert re.search(r"enable|load", content, re.IGNORECASE), "Ch 9 must cover register load enable"

    def test_ch10_data_objects_timing_and_numeric_std(self, chapters_dir: Path):
        """Chapter 10 must cover signals vs variables delta delays, user types, integer range constraints, and numeric_std."""
        content = read_chapter(chapters_dir, 10)
        assert re.search(r"signal", content, re.IGNORECASE) and re.search(r"variable", content, re.IGNORECASE)
        assert re.search(r"delta", content, re.IGNORECASE), "Ch 10 must explain delta-cycle delay"
        assert re.search(r"integer\s+range|range\s+\d+\s+to\s+\d+", content, re.IGNORECASE), (
            "Ch 10 must explain integer range constraints and flip-flop synthesis sizing"
        )
        assert re.search(r"numeric_std", content, re.IGNORECASE), "Ch 10 must cover numeric_std typing"

    def test_ch11_looping_constructs_hardware_unrolling(self, chapters_dir: Path):
        """Chapter 11 must cover spatial hardware unrolling of loops, while synthesizability limits, and next/exit."""
        content = read_chapter(chapters_dir, 11)
        assert re.search(r"for\s+.*?loop", content, re.IGNORECASE), "Ch 11 must cover for loops"
        assert re.search(r"unroll|spatial", content, re.IGNORECASE), "Ch 11 must explain spatial hardware unrolling"
        assert re.search(r"while", content, re.IGNORECASE), "Ch 11 must cover while loops and synthesis boundaries"
        assert re.search(r"\bnext\b", content, re.IGNORECASE) and re.search(r"\bexit\b", content, re.IGNORECASE), (
            "Ch 11 must cover loop control statements next and exit"
        )

    def test_ch12_standard_digital_circuits(self, chapters_dir: Path):
        """Chapter 12 must provide standard reference circuits and critique/correct textbook quirks."""
        content = read_chapter(chapters_dir, 12)
        assert re.search(r"flip-flop|dff", content, re.IGNORECASE)
        assert re.search(r"counter", content, re.IGNORECASE)
        assert re.search(r"shift\s+register", content, re.IGNORECASE)
        assert re.search(r"comparator", content, re.IGNORECASE)
        assert re.search(r"multiplexer|mux", content, re.IGNORECASE)
        assert re.search(r"decoder", content, re.IGNORECASE)


# ==============================================================================
# Tier 4: VHDL Syntax Validation
# ==============================================================================
@pytest.mark.tier4
class TestTier4VhdlSyntaxValidation:
    """Extracts all VHDL code snippets and compiles them with GHDL syntax check."""

    @pytest.mark.parametrize("chapter_num", range(1, 13))
    def test_each_chapter_contains_extractable_vhdl(self, chapters_dir: Path, chapter_num: int):
        """Every chapter must contain at least one extractable VHDL code snippet."""
        content = read_chapter(chapters_dir, chapter_num)
        snippets = extract_vhdl_snippets(content)
        assert len(snippets) >= 1, f"Chapter {chapter_num:02d} does not contain any ```vhdl code snippets"

    @pytest.mark.parametrize("chapter_num", range(1, 13))
    def test_all_vhdl_snippets_compile_with_ghdl(self, chapters_dir: Path, chapter_num: int):
        """All VHDL snippets in the chapter must pass GHDL syntax check with 0 errors."""
        content = read_chapter(chapters_dir, chapter_num)
        snippets = extract_vhdl_snippets(content)
        assert snippets, f"Chapter {chapter_num:02d} has no ```vhdl code snippets to validate"

        failed_snippets = []
        for idx, snippet in enumerate(snippets, 1):
            code = snippet["code"]
            line = snippet["line_number"]
            ok, err = validate_vhdl_with_ghdl(code)
            if not ok:
                failed_snippets.append(
                    f"Snippet #{idx} (starting line {line}):\n"
                    f"--- VHDL Code ---\n{code[:300]}...\n"
                    f"--- GHDL Error ---\n{err}\n"
                )

        assert not failed_snippets, (
            f"Chapter {chapter_num:02d} has {len(failed_snippets)} syntactically invalid VHDL snippet(s):\n\n"
            + "\n".join(failed_snippets)
        )
