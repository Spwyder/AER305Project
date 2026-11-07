"""Runs evaluation.py with an uploaded design block, inside the browser (Pyodide).

The design block replaces the lines between the two "#=====" marker lines that
follow "#design parameters to change!" in evaluation.py, which is the same swap
evaluation_from_file.py does. evaluation.py itself is never modified: it is
fetched from the site as-is on every run, so pushing a new evaluation.py to the
repo updates the site.
"""
import base64
import contextlib
import io
import os
import re
import traceback
import warnings

os.environ["MPLBACKEND"] = "Agg"
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

START_MARK = "#design parameters to change!"
BLOCK_MARK = "#====="
WORKDIR = "/home/pyodide/run"
PNG_NAME = "spar_summary.png"  # the file name evaluation.py saves to


def find_block(lines):
    """Return (a, b): indices of the opening and closing "#=====" marker lines."""
    starts = [i for i, l in enumerate(lines) if l.startswith(START_MARK)]
    if len(starts) != 1:
        raise ValueError(f"evaluation.py should contain exactly one '{START_MARK}' line (found {len(starts)}).")
    a = starts[0] + 1
    if a >= len(lines) or not lines[a].startswith(BLOCK_MARK):
        raise ValueError(f"evaluation.py: the line after '{START_MARK}' should start with '{BLOCK_MARK}'.")
    for b in range(a + 1, len(lines)):
        if lines[b].startswith(BLOCK_MARK):
            return a, b
    raise ValueError("evaluation.py: no closing '#=====' line after the design block.")


def splice(eval_src, design_src):
    if START_MARK in design_src:
        raise ValueError("This looks like a whole evaluation.py. Upload only the design block "
                         "(the lines that go between the two '#=====' lines).")
    lines = eval_src.splitlines(keepends=True)
    a, b = find_block(lines)
    if not design_src.endswith("\n"):
        design_src += "\n"
    n_design = design_src.count("\n")
    src = "".join(lines[: a + 1]) + design_src + "".join(lines[b:])
    return src, a + 1, n_design, b - a - 1  # source, lines before design, design length, original block length


def remap_traceback(tb, n_before, n_design, n_block, design_name):
    """Point traceback line numbers at the design file or the real evaluation.py lines."""
    def fix(m):
        line = int(m.group(1))
        if n_before < line <= n_before + n_design:
            return f'File "{design_name}", line {line - n_before}'
        if line > n_before + n_design:
            line = line - n_design + n_block
        return f'File "evaluation.py", line {line}'
    tb = "".join(l for l in tb.splitlines(keepends=True) if not l.startswith('  File "<exec>"'))  # hide this runner's own frame
    return re.sub(r'File "evaluation\.py", line (\d+)', fix, tb)


def summary(g):
    """A few headline numbers pulled from the script's variables (best effort)."""
    out = {}
    try:
        best = g["best"]
        out["Best engine position (ft)"] = f"{g['leBest']:.2f}"
        out["Minimum factor of safety"] = f"{g['fsMin'][best]:.3f}"
        out["Spar weight per wing (lb)"] = f"{g['wSpar']:,.0f}"
        out["Cost per wing ($)"] = f"{g['cost']:,.0f}"
        if g.get("nStringers", 0) > 0 and "fsBuckling" in g:
            out["Stringer buckling FS"] = f"{g['fsBuckling']:.3g}"
        out["Ribs"] = str(len(g["ribLocations"]))
    except Exception:
        pass
    return out


def run(eval_src, design_src, design_name="design.py"):
    result = {"ok": False, "stdout": "", "error": "", "png": "", "summary": {}}
    try:
        src, n_before, n_design, n_block = splice(eval_src, design_src)
    except ValueError as e:
        result["error"] = str(e)
        return result

    os.makedirs(WORKDIR, exist_ok=True)
    png_path = os.path.join(WORKDIR, PNG_NAME)
    if os.path.exists(png_path):
        os.remove(png_path)

    out = io.StringIO()
    g = {"__name__": "__main__"}
    old_cwd = os.getcwd()
    os.chdir(WORKDIR)
    plt.close("all")
    try:
        with contextlib.redirect_stdout(out), warnings.catch_warnings():
            warnings.simplefilter("ignore")  # plt.show() warns under the Agg backend
            exec(compile(src, "evaluation.py", "exec"), g)
        if not os.path.exists(png_path):
            raise RuntimeError(f"evaluation.py finished but did not save {PNG_NAME}.")
        with open(png_path, "rb") as f:
            result["png"] = base64.b64encode(f.read()).decode()
        result["ok"] = True
        result["summary"] = summary(g)
    except Exception:
        result["error"] = remap_traceback(traceback.format_exc(), n_before, n_design, n_block, design_name)
    finally:
        os.chdir(old_cwd)
        plt.close("all")
    result["stdout"] = out.getvalue()
    return result
