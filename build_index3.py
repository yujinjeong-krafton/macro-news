# -*- coding: utf-8 -*-
"""Merge index1.1.html and Index2.1.html into index3.html with namespaced IDs."""
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent


def split_html(t: str):
    m_body = re.search(r"<body[^>]*>", t, re.I)
    m_script = re.search(r"<script>", t, re.I)
    m_end = re.search(r"</script>\s*</body>", t, re.I)
    if not (m_body and m_script and m_end):
        raise SystemExit("parse fail: body/script boundaries")
    body_pre = t[m_body.end() : m_script.start()]
    script = t[m_script.end() : m_end.start()]
    return body_pre, script


def prefix_body_ids(html: str, pfx: str) -> str:
    def repl(m):
        return 'id="' + pfx + m.group(1) + '"'

    return re.sub(r'\bid="([^"]+)"', repl, html)


def prefix_script_news(s: str) -> str:
    s = s.replace('onclick="refreshAll()"', 'onclick="macroRefreshAll()"')
    s = s.replace('onclick="setClassifyFilter(', 'onclick="macroSetClassifyFilter(')
    s = s.replace('onclick="toggleClassifySection(', 'onclick="macroToggleClassifySection(')
    s = s.replace("function setClassifyFilter(cat) {", "function macroSetClassifyFilter(cat) {")
    s = s.replace("function toggleClassifySection(sectionId) {", "function macroToggleClassifySection(sectionId) {")
    s = re.sub(
        r"getElementById\('([^']+)'\)",
        lambda m: "getElementById('macro-" + m.group(1) + "')",
        s,
    )
    s = re.sub(
        r'getElementById\("([^"]+)"\)',
        lambda m: 'getElementById("macro-' + m.group(1) + '")',
        s,
    )
    s = s.replace("const sectionId = 'classify-section-", "const sectionId = 'macro-classify-section-")
    s = s.replace("'classify-section-untagged'", "'macro-classify-section-untagged'")
    s = s.replace("document.querySelectorAll('.tab')", "document.querySelectorAll('#view-macro .tab')")
    s = s.replace("document.querySelectorAll('.panel')", "document.querySelectorAll('#view-macro .panel')")
    s = s.replace(
        "document.getElementById('panel-' + tab.dataset.tab)",
        "document.getElementById('macro-panel-' + tab.dataset.tab)",
    )
    s = s.replace(
        "getElementById('statHot' + (i + 1))",
        "getElementById('macro-statHot' + (i + 1))",
    )
    s = s.replace(
        "document.getElementById(id).addEventListener('change', renderAll));",
        "document.getElementById('macro-' + id).addEventListener('change', renderAll));",
    )
    s = s.replace("function refreshAll() { collectAll(); }", "function macroRefreshAll() { collectAll(); }")
    s = (
        "(function () {\n'use strict';\n"
        + s.strip()
        + "\nwindow.macroRefreshAll = macroRefreshAll;\n"
        "window.macroSetClassifyFilter = macroSetClassifyFilter;\n"
        "window.macroToggleClassifySection = macroToggleClassifySection;\n})();\n"
    )
    return s


def prefix_script_rep(s: str) -> str:
    s = s.replace('onclick="refreshAll()"', 'onclick="repRefreshAll()"')
    s = s.replace('onclick="setClassifyFilter(', 'onclick="repSetClassifyFilter(')
    s = s.replace('onclick="toggleClassifySection(', 'onclick="repToggleClassifySection(')
    s = s.replace('onclick="setSourceFilter(', 'onclick="repSetSourceFilter(')
    s = re.sub(
        r"getElementById\('([^']+)'\)",
        lambda m: "getElementById('rep-" + m.group(1) + "')",
        s,
    )
    s = re.sub(
        r'getElementById\("([^"]+)"\)',
        lambda m: 'getElementById("rep-' + m.group(1) + '")',
        s,
    )
    s = s.replace("const sectionId = 'classify-section-", "const sectionId = 'rep-classify-section-")
    s = s.replace("'classify-section-untagged'", "'rep-classify-section-untagged'")
    s = s.replace("const sectionId = 'source-section-' + i", "const sectionId = 'rep-source-section-' + i")
    s = s.replace("document.querySelectorAll('.tab')", "document.querySelectorAll('#view-report .tab')")
    s = s.replace("document.querySelectorAll('.panel')", "document.querySelectorAll('#view-report .panel')")
    s = s.replace(
        "document.getElementById('panel-' + tab.dataset.tab)",
        "document.getElementById('rep-panel-' + tab.dataset.tab)",
    )
    s = s.replace(
        "getElementById('statHot' + (i + 1))",
        "getElementById('rep-statHot' + (i + 1))",
    )
    s = s.replace(
        "document.getElementById(id).addEventListener('change', renderAll));",
        "document.getElementById('rep-' + id).addEventListener('change', renderAll));",
    )
    s = s.replace("function refreshAll() { collectAll(); }", "function repRefreshAll() { collectAll(); }")
    s = s.replace("function setClassifyFilter(cat) {", "function repSetClassifyFilter(cat) {")
    s = s.replace("function toggleClassifySection(sectionId) {", "function repToggleClassifySection(sectionId) {")
    s = s.replace("function setSourceFilter(key) {", "function repSetSourceFilter(key) {")
    inner = (
        "(function () {\n'use strict';\n"
        + s.strip()
        + "\nwindow.repRefreshAll = repRefreshAll;\n"
        "window.repSetClassifyFilter = repSetClassifyFilter;\n"
        "window.repToggleClassifySection = repToggleClassifySection;\n"
        "window.repSetSourceFilter = repSetSourceFilter;\n})();\n"
    )
    return (
        "window.__bootstrapRepHub = function () {\n"
        "  if (window.__repHubLoaded) return;\n"
        "  window.__repHubLoaded = true;\n"
        + inner
        + "};\n"
    )


def main():
    t1 = (BASE / "index1.1.html").read_text(encoding="utf-8")
    t2 = (BASE / "Index2.1.html").read_text(encoding="utf-8")

    b1, s1 = split_html(t1)
    b2, s2 = split_html(t2)

    b1p = prefix_body_ids(b1, "macro-")
    b1p = b1p.replace('onclick="refreshAll()"', 'onclick="macroRefreshAll()"')
    b2p = prefix_body_ids(b2, "rep-")
    b2p = b2p.replace('onclick="refreshAll()"', 'onclick="repRefreshAll()"')
    s1p = prefix_script_news(s1)
    s2p = prefix_script_rep(s2)

    hc = t1.split("<body", 1)[0]
    hc = re.sub(r"<title>[^<]+</title>", "<title>매크로 뉴스 &amp; 연구보고서 | 통합 허브</title>", hc, count=1)

    extra_css = """
    .app-switch-bar {
      background: var(--white);
      border-bottom: 1px solid var(--gray-200);
      position: sticky;
      top: 0;
      z-index: 55;
      box-shadow: 0 1px 0 rgba(0,0,0,.04);
    }
    .app-switch-inner {
      max-width: 1200px;
      margin: 0 auto;
      padding: 10px 24px 12px;
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }
    .app-switch-label {
      font-size: 12px;
      font-weight: 600;
      color: var(--gray-500);
      margin-right: 4px;
    }
    .app-switch-btn {
      padding: 8px 16px;
      border-radius: var(--radius-full);
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      border: 1.5px solid var(--gray-200);
      background: var(--white);
      color: var(--gray-600);
      transition: var(--transition);
    }
    .app-switch-btn:hover {
      border-color: var(--gray-300);
      background: var(--gray-50);
    }
    .app-switch-btn.active {
      background: var(--accent-gradient);
      border-color: transparent;
      color: var(--white);
      box-shadow: 0 2px 8px rgba(37, 99, 235, 0.22);
    }
    .system-view { display: none; }
    .system-view.active { display: block; }
    body.hub-combined .app-switch-bar { z-index: 60; }
    body.hub-combined .system-view .site-header { top: 52px; }
    @media (max-width: 768px) {
      .app-switch-inner { padding: 8px 16px 10px; }
    }
"""
    hc = hc.replace("</style>", extra_css + "\n  </style>", 1)

    switcher = """  <div class="app-switch-bar" role="tablist" aria-label="시스템 선택">
    <div class="app-switch-inner">
      <span class="app-switch-label">시스템</span>
      <button type="button" class="app-switch-btn active" id="btnViewMacro" data-view="macro" role="tab" aria-selected="true">📊 매크로 뉴스 모니터</button>
      <button type="button" class="app-switch-btn" id="btnViewReport" data-view="report" role="tab" aria-selected="false">📑 연구보고서 크롤러</button>
    </div>
  </div>
"""

    switch_js = """
(function () {
  var vm = document.getElementById('view-macro');
  var vr = document.getElementById('view-report');
  var bm = document.getElementById('btnViewMacro');
  var br = document.getElementById('btnViewReport');
  function show(which) {
    var isMacro = which === 'macro';
    vm.classList.toggle('active', isMacro);
    vr.classList.toggle('active', !isMacro);
    if (isMacro) {
      vm.removeAttribute('hidden');
      vr.setAttribute('hidden', '');
    } else {
      vr.removeAttribute('hidden');
      vm.setAttribute('hidden', '');
    }
    bm.classList.toggle('active', isMacro);
    br.classList.toggle('active', !isMacro);
    bm.setAttribute('aria-selected', isMacro ? 'true' : 'false');
    br.setAttribute('aria-selected', isMacro ? 'false' : 'true');
  }
  bm.addEventListener('click', function () { show('macro'); });
  br.addEventListener('click', function () {
    show('report');
    if (window.__bootstrapRepHub) window.__bootstrapRepHub();
  });
  vr.setAttribute('hidden', '');
})();
"""

    final = (
        hc
        + '<body class="hub-combined">\n'
        + switcher
        + '\n<div id="view-macro" class="system-view active" role="tabpanel">\n'
        + b1p.strip()
        + "\n</div>\n"
        + '<div id="view-report" class="system-view" role="tabpanel" hidden>\n'
        + b2p.strip()
        + "\n</div>\n"
        + "<script>"
        + switch_js
        + "\n</script>\n"
        + "<script>"
        + s1p
        + "</script>\n"
        + "<script>"
        + s2p
        + "</script>\n</body>\n</html>\n"
    )

    (BASE / "index3.html").write_text(final, encoding="utf-8")
    print("OK:", BASE / "index3.html", "chars", len(final))


if __name__ == "__main__":
    main()
