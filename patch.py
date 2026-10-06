#!/usr/bin/env python3
"""
Patch The Theory Lab index.html:
  1. add 24 new theories (6 Physical Education, 9 Leadership, 7 Critical & Social,
     Community of Inquiry, Identity Formation)
  2. add the SUBJ cluster bank and a 4th Library view mode, "By school subject"
  3. register the new disciplines and KIND badges
Idempotent: refuses to run twice.
Usage: patch.py <index.html> <parts-dir>
"""
import io, re, sys, os

target, parts = sys.argv[1], sys.argv[2]
src = io.open(target, encoding="utf-8").read()
orig_len = len(src)

if 'id:"mosston"' in src or "const SUBJ=" in src:
    sys.exit("ALREADY PATCHED — nothing to do.")

def sub(pattern, repl, n=1, flags=0):
    global src
    out, k = re.subn(pattern, repl, src, count=n, flags=flags)
    assert k == n, "no match: " + pattern[:70]
    src = out

def anchor(find, repl, n=1):
    global src
    assert src.count(find) >= n, "anchor missing: " + find[:70]
    src = src.replace(find, repl, n)

read = lambda f: io.open(os.path.join(parts, f), encoding="utf-8").read()

# ── 1. new theories, spliced in before the THEORIES array closes ─────────────
new = read("new_theories_1.js").rstrip() + "\n" + read("new_theories_2.js").rstrip() + "\n"
anchor("\n];\n\nconst SCENARIOS = [", "\n" + new + "];\n\nconst SCENARIOS = [")

# ── 2. SUBJ bank, after the PROB array ──────────────────────────────────────
anchor("\n/* Kind classification (reviewer recommendation):",
       read("subj.js").rstrip() + "\n\n/* Kind classification (reviewer recommendation):")

# ── 3. a 4th view-mode chip ─────────────────────────────────────────────────
anchor("[['subject','📚 By subject'],['question','🧑‍🏫 By teaching question'],"
       "['problem','🩺 By classroom problem']]",
       "[['subject','📚 By field'],['classroom','🏫 By school subject'],"
       "['question','🧑‍🏫 By teaching question'],['problem','🩺 By classroom problem']]")

# ── 4. route the new mode through the cluster renderer ──────────────────────
anchor("  if(viewMode==='question'||viewMode==='problem'){\n"
       "    const bank=viewMode==='question'?TEACH:PROB;",
       "  if(viewMode==='question'||viewMode==='problem'||viewMode==='classroom'){\n"
       "    const bank=viewMode==='question'?TEACH:viewMode==='problem'?PROB:SUBJ;")

# one helper, so every label below reads from a single place
anchor("/* --- library --- */\nfunction renderChips(){",
       "/* --- library --- */\n"
       "const bankName=v=>v==='question'?'teaching question'"
       ":v==='problem'?'classroom problem':'school subject';\n"
       "function renderChips(){")

anchor("""<b>Searching every ${viewMode==='question'?'teaching question':'classroom problem'}</b>""",
       """<b>Searching every ${bankName(viewMode)}</b>""")
anchor("""Clear the search to browse by question.""",
       """Clear the search to browse by ${bankName(viewMode)}.""")
anchor("""← All ${viewMode==='question'?'teaching questions':'classroom problems'}""",
       """← All ${bankName(viewMode)}s""")

# the prompt above the picker list
anchor("""      ? (viewMode==='question'
          ? 'Pick the question closest to what you are trying to do.'
          : 'Pick the sentence closest to what you are hearing yourself say.')""",
       """      ? (viewMode==='question'
          ? 'Pick the question closest to what you are trying to do.'
          : viewMode==='classroom'
          ? 'Pick what you teach. Theories are listed by where they get used, not where they came from.'
          : 'Pick the sentence closest to what you are hearing yourself say.')""")

# ── 5. register the new disciplines in the chip groups ──────────────────────
anchor("['Subject teaching',      ['Mathematics Ed','Science Ed','Historical Thinking']],",
       "['Subject teaching',      ['Mathematics Ed','Science Ed','Historical Thinking','Physical Education']],")

# ── 6. kind badges for the new entries ──────────────────────────────────────
anchor(' desirable:"strategy",implementation:"strategy",adhd_strategies:"strategy",math_cra:"strategy",wtl:"strategy"};',
       ' desirable:"strategy",implementation:"strategy",adhd_strategies:"strategy",math_cra:"strategy",wtl:"strategy",\n'
       ' mosston:"framework",physlit:"framework",sported:"model",tpsr:"model",fitt:"strategy",\n'
       ' comm_inquiry:"framework",systems:"framework",change_theory:"framework",\n'
       ' lead_situational:"model",lead_behavioral:"model",lead_transformational:"model"};')

io.open(target, "w", encoding="utf-8").write(src)
print("patched  %s" % target)
print("  %d bytes -> %d bytes (+%d)" % (orig_len, len(src), len(src) - orig_len))

# ── 7. bump the service-worker cache so installed phones pick the update up ──
sw = os.path.join(os.path.dirname(os.path.abspath(target)), "sw.js")
if os.path.exists(sw):
    s = io.open(sw, encoding="utf-8").read()
    m = re.search(r"theory-lab-v(\d+)", s)
    if m:
        old, new_v = m.group(0), "theory-lab-v%d" % (int(m.group(1)) + 1)
        io.open(sw, "w", encoding="utf-8").write(s.replace(old, new_v))
        print("  sw.js cache %s -> %s" % (old, new_v))
