// Runs Python (Pyodide) off the main thread so the page stays responsive.
const PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/v0.27.7/full/";
importScripts(PYODIDE_URL + "pyodide.js");

const status = (text) => self.postMessage({ type: "status", text });

const ready = (async () => {
  status("Loading Python…");
  const py = await loadPyodide({ indexURL: PYODIDE_URL });
  status("Loading numpy, scipy and matplotlib…");
  await py.loadPackage(["numpy", "scipy", "matplotlib"]);
  const runner = await (await fetch("runner.py", { cache: "no-cache" })).text();
  py.runPython(runner);
  return py;
})();
ready.then(() => self.postMessage({ type: "ready" }),
           (err) => self.postMessage({ type: "fatal", text: String(err) }));

async function sha256(text) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

self.onmessage = async (e) => {
  const { id, design, name } = e.data;
  try {
    const py = await ready;
    status("Fetching evaluation.py…");
    const resp = await fetch("../evaluation.py", { cache: "no-cache" });
    if (!resp.ok) throw new Error(`Could not load evaluation.py (HTTP ${resp.status})`);
    const evalSrc = await resp.text();
    status("Running evaluation.py…");
    py.globals.set("EVAL_SRC", evalSrc);
    py.globals.set("DESIGN_SRC", design);
    py.globals.set("DESIGN_NAME", name || "design.py");
    const proxy = py.runPython("run(EVAL_SRC, DESIGN_SRC, DESIGN_NAME)");
    const res = proxy.toJs({ dict_converter: Object.fromEntries });
    proxy.destroy();
    self.postMessage({ type: "result", id, ...res, evalSha: (await sha256(evalSrc)).slice(0, 12) });
  } catch (err) {
    self.postMessage({ type: "result", id, ok: false, error: String(err), stdout: "", png: "", summary: {} });
  }
};
