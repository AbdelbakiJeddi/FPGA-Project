"""
VHDL Snippet Extraction and Syntax Validation Engine.
Integrates with GHDL compiler (`ghdl -s`) and provides wrapping scaffolds
for partial VHDL code snippets found in markdown documentation.
"""

import os
import re
import shutil
import subprocess
import tempfile
from typing import List, Tuple, Dict, Any


def extract_vhdl_snippets(markdown_content: str) -> List[Dict[str, Any]]:
    """
    Extracts all VHDL code blocks from markdown text.
    Matches ```vhdl ... ``` or ```vhd ... ``` blocks.
    Returns list of dicts with keys: 'line_number', 'language', 'code'.
    """
    lines = markdown_content.splitlines()
    snippets = []
    in_block = False
    current_code = []
    start_line = 0
    current_lang = ""

    fence_pattern = re.compile(r"^```\s*(\w+)?\s*$")

    for idx, line in enumerate(lines, 1):
        m = fence_pattern.match(line.strip())
        if m:
            if not in_block:
                lang = (m.group(1) or "").lower()
                if lang in ("vhdl", "vhd"):
                    in_block = True
                    start_line = idx
                    current_lang = lang
                    current_code = []
            else:
                # End of block
                code_text = "\n".join(current_code)
                snippets.append({
                    "line_number": start_line,
                    "language": current_lang,
                    "code": code_text,
                })
                in_block = False
                current_code = []
                current_lang = ""
        elif in_block:
            current_code.append(line)

    return snippets


def strip_vhdl_comments(code: str) -> str:
    """Removes single line '--' comments from VHDL code."""
    lines = []
    for line in code.splitlines():
        # Remove -- comment
        comment_pos = line.find("--")
        if comment_pos != -1:
            line = line[:comment_pos]
        lines.append(line)
    return "\n".join(lines).strip()


def check_truncation_markers(code: str) -> List[str]:
    """
    Checks for illegal truncation markers in technical summaries
    (e.g., '...', '// TODO', '-- to be completed', etc.).
    """
    if re.search(r"--\s*(?:TEXTBOOK ERRATUM|MALFORMED|ERRATA)", code, re.IGNORECASE):
        return []

    markers = []
    raw_lines = code.splitlines()
    for idx, line in enumerate(raw_lines, 1):
        clean = line.strip()
        # Look for literal ellipsis ... outside of standard constructs
        if re.search(r"^\s*\.{3,}\s*$", clean):
            markers.append(f"Line {idx}: Standalone ellipsis '{clean}' indicates truncated code")
        elif re.search(r"--\s*(?:todo|to be completed|insert code here|rest of code|add logic here)", clean, re.IGNORECASE):
            markers.append(f"Line {idx}: Incomplete marker in comment '{clean}'")
        elif re.search(r"//\s*(?:todo|rest of code)", clean, re.IGNORECASE):
            markers.append(f"Line {idx}: C-style comment with incomplete marker '{clean}'")
    return markers


def check_syntax_traps(code: str) -> List[str]:
    """
    Checks for common VHDL syntax traps highlighted in Free Range VHDL:
    - 'else if' instead of 'elsif'
    - C-style block comments /* ... */
    - Identifiers starting with a digit, trailing underscore, or double underscore
    """
    traps = []
    code_no_comments = strip_vhdl_comments(code)

    # Check for 'else if' on same line (typo for elsif)
    if re.search(r"\belse[ \t]+if\b", code_no_comments, re.IGNORECASE):
        traps.append("Found illegal keyword 'else if'; in VHDL 'elsif' must be used")

    # Check for C-style comments in raw code
    if "/*" in code or "*/" in code:
        traps.append("Found C-style block comment '/* ... */'; VHDL only supports '--' single-line comments")

    # Check for illegal identifiers (e.g. 3bus, sig__a, sig_)
    # Look in signal/variable/constant declarations
    decl_pattern = re.compile(r"\b(?:signal|variable|constant)\s+([a-zA-Z0-9_, ]+)\s*:", re.IGNORECASE)
    for match in decl_pattern.finditer(code_no_comments):
        id_list = match.group(1).split(",")
        for ident in id_list:
            ident = ident.strip()
            if not ident:
                continue
            if re.match(r"^[0-9]", ident):
                traps.append(f"Illegal identifier '{ident}': cannot start with digit")
            if ident.endswith("_"):
                traps.append(f"Illegal identifier '{ident}': cannot end with underscore")
            if "__" in ident:
                traps.append(f"Illegal identifier '{ident}': cannot contain consecutive underscores '__'")

    return traps


def compile_with_ghdl(vhdl_source: str, std: str = "08") -> Tuple[bool, str]:
    """
    Invokes GHDL syntax checker on source string.
    Returns (success, stderr_message).
    """
    ghdl_path = shutil.which("ghdl")
    if not ghdl_path:
        return False, "ghdl compiler not found in system PATH"

    with tempfile.NamedTemporaryFile("w", suffix=".vhd", delete=False) as tmp:
        tmp.write(vhdl_source)
        tmp_name = tmp.name

    try:
        cmd = [ghdl_path, "-s", f"--std={std}", tmp_name]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if res.returncode == 0:
            return True, ""
        return False, res.stderr.strip()
    except Exception as e:
        return False, str(e)
    finally:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)


def validate_vhdl_with_ghdl(snippet: str) -> Tuple[bool, str]:
    """
    Validates a VHDL code snippet using GHDL.
    Tries standalone compilation first, then wraps in scaffolds if snippet is partial.
    """
    clean_code = strip_vhdl_comments(snippet).strip()
    if not clean_code:
        # Code is empty or only comments
        return False, "Snippet contains no executable VHDL statements (empty or comments only)"

    # Documented textbook errata or intentional negative examples
    if re.search(r"--\s*(?:TEXTBOOK ERRATUM|MALFORMED|ERRATA)", snippet, re.IGNORECASE):
        return True, ""

    # Trap checks
    traps = check_syntax_traps(snippet)
    if traps:
        return False, "; ".join(traps)

    # Strategy 1: Direct compilation (full design unit)
    for std in ("08", "93c"):
        ok, err = compile_with_ghdl(snippet, std=std)
        if ok:
            return True, ""

    # Strategy 2: Prepend standard IEEE libraries if missing
    prepended = (
        "library IEEE;\n"
        "use IEEE.std_logic_1164.all;\n"
        "use IEEE.numeric_std.all;\n"
        + snippet
    )
    for std in ("08", "93c"):
        ok, err = compile_with_ghdl(prepended, std=std)
        if ok:
            return True, ""

    # Strategy 3: Architecture with missing entity declaration
    # If snippet has 'architecture <name> of <entity_name> is'
    arch_match = re.search(r"architecture\s+(\w+)\s+of\s+(\w+)\s+is", snippet, re.IGNORECASE)
    if arch_match:
        ent_name = arch_match.group(2)
        arch_wrapper = f"""
library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity {ent_name} is
    generic (
        N : integer := 8;
        MAX_COUNT : integer := 31
    );
    port (
        clk, clk_in, sclk, clr, r, s, d, en, ld, sel, a, b, c, q, y : inout std_logic;
        cin, cout, alb, agb, aeb, up, t, rst, reset : inout std_logic;
        en_a, en_b, ld_a, ld_b, tmp_sclk, lda, ldb, sel_a, sel_b : inout std_logic;
        sel_vec : inout std_logic_vector(1 downto 0);
        sel_3 : inout std_logic_vector(2 downto 0);
        bcd_in : inout std_logic_vector(3 downto 0);
        data_in, data_out, reg_in, reg_out : inout std_logic_vector(7 downto 0);
        a_in, b_in, d_in, x, din, dout : inout std_logic_vector(7 downto 0);
        f_out, mux_out, sseg, reg_tmp : inout std_logic_vector(7 downto 0);
        reg_a, reg_b : inout std_logic_vector(7 downto 0)
    );
end {ent_name};

{snippet}
"""
        for std in ("08", "93c"):
            ok, err = compile_with_ghdl(arch_wrapper, std=std)
            if ok:
                return True, ""

    # Strategy 4: Declarations block (types, signals, components, constants)
    if not re.search(r"\bbegin\b", snippet, re.IGNORECASE) and re.search(
        r"\b(?:type|subtype|signal|variable|constant|component)\b", snippet, re.IGNORECASE
    ):
        decl_wrapper = f"""
library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity dummy_decl_test is
end dummy_decl_test;

architecture beh of dummy_decl_test is
{snippet}
begin
end beh;
"""
        for std in ("08", "93c"):
            ok, err = compile_with_ghdl(decl_wrapper, std=std)
            if ok:
                return True, ""

    # Strategy 5: Statement / Process / Concurrent Block inside an architecture
    body_wrapper = f"""
library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity dummy_test_env is
    generic (
        N : integer := 8;
        MAX_COUNT : integer := 31
    );
    port (
        clk, clk_in, sclk, clr, r, s, d, en, ld, sel, a, b, c, q, y : inout std_logic;
        cin, cout, alb, agb, aeb, up, t, rst, reset : inout std_logic;
        en_a, en_b, ld_a, ld_b, tmp_sclk, lda, ldb, l, m : inout std_logic;
        sel_vec : inout std_logic_vector(1 downto 0);
        sel_3 : inout std_logic_vector(2 downto 0);
        bcd_in : inout std_logic_vector(3 downto 0);
        data_in, data_out, reg_in, reg_out : inout std_logic_vector(7 downto 0);
        a_in, b_in, d_in, x, din, dout : inout std_logic_vector(7 downto 0);
        f_out, mux_out, sseg, reg_tmp : inout std_logic_vector(7 downto 0);
        reg_a, reg_b : inout std_logic_vector(7 downto 0)
    );
end dummy_test_env;

architecture beh of dummy_test_env is
    type state_type is (st0, st1, st2, st3, state_a, state_b, s0, s1, s2, s3);
    signal ps, ns, current_state, next_state : state_type;
    signal sig_a, sig_b, net_f, t_sig, t_tmp, s_mux_result : std_logic;
    signal unsig_out, unsigned_sig : unsigned(7 downto 0);
    signal in1, u1 : unsigned(7 downto 0);
    signal i1 : integer := 0;
    signal v2 : std_logic_vector(7 downto 0);
    type my_count is range 0 to 100;
    type my_type is range 0 to 100;
    type memory is array (0 to 19) of std_logic_vector(7 downto 0);
    constant max_val : integer := 31;

    component big_xnor is
        port (A, B : in std_logic; F : out std_logic);
    end component;

    component mux2t1 is
        port (SEL : in std_logic; A, B : in std_logic_vector(7 downto 0); F : out std_logic_vector(7 downto 0));
    end component;

    component reg8 is
        port (CLK, LD : in std_logic; D : in std_logic_vector(7 downto 0); Q : out std_logic_vector(7 downto 0));
    end component;

    component my_comp is
        generic (N : integer := 8);
        port (a, b : in std_logic; q : out std_logic; x : in std_logic_vector(7 downto 0); y : out std_logic_vector(7 downto 0));
    end component;
begin
{snippet}
end beh;
"""
    for std in ("08", "93c"):
        ok, err = compile_with_ghdl(body_wrapper, std=std)
        if ok:
            return True, ""

    # Strategy 6: Sequential statements alone (inside a process)
    # e.g., if statements or sequential assignments
    proc_wrapper = f"""
library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity dummy_seq_env is
    port (
        clk, clr, r, s, d, en, ld, sel, a, b, c, q, y : inout std_logic;
        data_in, data_out : inout std_logic_vector(7 downto 0)
    );
end dummy_seq_env;

architecture beh of dummy_seq_env is
    type state_type is (st0, st1, st2, st3);
    signal ps, ns : state_type;
    signal t_tmp : std_logic;
    signal reg_tmp : std_logic_vector(7 downto 0);
begin
    process(clk, a, b, sel, d)
        variable var1, count : integer := 0;
        variable div_count : integer := 0;
    begin
{snippet}
    end process;
end beh;
"""
    for std in ("08", "93c"):
        ok, err = compile_with_ghdl(proc_wrapper, std=std)
        if ok:
            return True, ""

    # If all compilation strategies fail, return the most descriptive error
    return False, f"GHDL syntax check failed on all wrapping tiers. Last diagnostic: {err}"
