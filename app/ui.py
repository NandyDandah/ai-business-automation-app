"""Presentation layer for the authenticated automation workspace."""

from html import escape


APP_THEME_CSS = """
:root {
  color-scheme: light;
  --canvas: #f4f6fa;
  --surface: #ffffff;
  --surface-soft: #f8f9fc;
  --ink: #17243b;
  --muted: #8190a5;
  --line: #e5eaf1;
  --navy: #14243b;
  --navy-2: #1d304b;
  --navy-3: #263b58;
  --lime: #c9f27e;
  --blue: #6678df;
  --teal: #56b89f;
  --coral: #e67c72;
  --amber: #e0ac54;
  --shadow: 0 18px 45px rgba(28, 45, 70, .07);
  --radius: 18px;
}
* { box-sizing: border-box; }
::selection { color: #17243b; background: rgba(201, 242, 126, .72); }
html { min-width: 320px; background: var(--canvas); }
body {
  margin: 0;
  max-width: none;
  min-height: 100vh;
  color: var(--ink);
  background: var(--canvas);
  font-family: Inter, "Segoe UI Variable", Aptos, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 14px;
  line-height: 1.55;
  -webkit-font-smoothing: antialiased;
}
button, input, textarea, select { font: inherit; }
button, a, select { -webkit-tap-highlight-color: transparent; }
a { color: inherit; text-decoration: none; }
button { color: inherit; }
button:focus-visible, a:focus-visible, input:focus-visible, textarea:focus-visible, select:focus-visible, summary:focus-visible {
  outline: 3px solid rgba(102, 120, 223, .35);
  outline-offset: 2px;
}
.app-shell { display: grid; grid-template-columns: 248px minmax(0, 1fr); min-height: 100vh; }
.app-sidebar {
  position: sticky; top: 0; display: flex; flex-direction: column; gap: 0;
  height: 100vh; min-height: 640px; padding: 27px 17px 20px;
  color: #eef3fa; background: var(--navy);
}
.brand { display: flex; align-items: center; gap: 12px; margin: 0 8px 42px; }
.brand-symbol {
  display: grid; width: 38px; height: 38px; place-items: center; border-radius: 13px;
  color: #15263c; background: linear-gradient(145deg, #d7f79b, #9ee0c7);
  box-shadow: 0 7px 18px rgba(169, 225, 149, .18);
}
.brand-title { display: block; color: #fff; font-size: 13px; font-weight: 750; letter-spacing: .09em; }
.brand-subtitle { display: block; margin-top: 1px; color: #93a4bb; font-size: 10px; letter-spacing: .03em; }
.sidebar-caption { margin: 0 12px 12px; color: #8294ad; font-size: 9px; font-weight: 750; letter-spacing: .17em; }
.sidebar-nav { display: grid; gap: 7px; }
.nav-link {
  display: flex; align-items: center; gap: 12px; min-height: 45px; padding: 0 12px;
  border: 1px solid transparent; border-radius: 11px; color: #aebbd0;
  font-size: 12px; font-weight: 600; transition: background .18s ease, color .18s ease, transform .18s ease;
}
.nav-link:hover { color: #fff; background: rgba(255,255,255,.055); transform: translateX(2px); }
.nav-link.active { color: #fff; border-color: rgba(255,255,255,.075); background: var(--navy-2); }
.nav-link.active .nav-icon { color: var(--lime); }
.nav-icon { display: grid; width: 19px; height: 19px; place-items: center; color: #8fa2bc; }
.nav-icon svg { width: 18px; height: 18px; }
.sidebar-spacer { flex: 1; }
.sidebar-status {
  display: flex; align-items: flex-start; gap: 10px; margin: 14px 4px 0; padding: 14px 12px;
  border: 1px solid rgba(255,255,255,.09); border-radius: 13px; background: rgba(255,255,255,.035);
}
.status-pip { flex: 0 0 auto; width: 7px; height: 7px; margin-top: 5px; border-radius: 99px; background: var(--lime); box-shadow: 0 0 0 4px rgba(201,242,126,.09); }
.sidebar-status strong { display: block; color: #e5edf6; font-size: 10px; font-weight: 650; }
.sidebar-status span { display: block; margin-top: 3px; color: #8fa1b9; font-size: 9px; line-height: 1.5; }
.sidebar-footnote { margin: 15px 8px 0; color: #7589a4; font-size: 9px; }
.main-area { min-width: 0; }
.topbar {
  display: flex; align-items: center; justify-content: space-between; gap: 16px; height: 76px;
  padding: 0 clamp(20px, 4vw, 54px); border-bottom: 1px solid rgba(222,228,237,.85);
  background: rgba(255,255,255,.74); backdrop-filter: blur(16px);
}
.breadcrumbs { display: flex; align-items: center; gap: 9px; color: #9aa6b7; font-size: 11px; }
.breadcrumbs strong { color: #34435a; font-weight: 650; }
.crumb-mark { color: #bec7d3; }
.topbar-actions { display: flex; align-items: center; gap: 10px; }
.session-pill { display: inline-flex; align-items: center; gap: 7px; padding: 7px 10px; border: 1px solid #e3eadf; border-radius: 99px; color: #557653; background: #f5faef; font-size: 10px; font-weight: 650; }
.session-pill svg { width: 13px; height: 13px; }
#logoutButton { padding: 8px 12px; border: 1px solid var(--line); border-radius: 9px; color: #65748b; background: #fff; font-size: 10px; font-weight: 650; cursor: pointer; transition: .18s ease; }
#logoutButton:hover { color: var(--ink); border-color: #cbd4e0; background: #f8f9fc; }
.page-content { width: min(100%, 1440px); margin: 0 auto; padding: 34px clamp(20px, 4vw, 54px) 54px; }
.eyebrow { display: flex; align-items: center; gap: 8px; margin: 0 0 10px; color: #8b98aa; font-size: 9px; font-weight: 750; letter-spacing: .16em; text-transform: uppercase; }
.eyebrow-dot { width: 6px; height: 6px; border-radius: 99px; background: var(--blue); }
.page-title-row { display: flex; align-items: flex-end; justify-content: space-between; gap: 20px; margin: 0 0 25px; }
.page-title-row h1, .hero-heading h1 { margin: 0; color: var(--ink); font-size: clamp(26px, 3vw, 36px); font-weight: 700; letter-spacing: -.045em; line-height: 1.14; }
.page-title-row p, .hero-heading p { max-width: 620px; margin: 9px 0 0; color: var(--muted); font-size: 13px; line-height: 1.7; }
.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 9px; min-height: 40px; padding: 0 15px;
  border: 1px solid var(--line); border-radius: 10px; color: #53627a; background: #fff;
  font-size: 11px; font-weight: 650; cursor: pointer; transition: .18s ease;
}
.btn:hover { border-color: #ccd5e1; background: #f9fafc; transform: translateY(-1px); }
.btn svg { width: 15px; height: 15px; }
.btn-primary {
  display: inline-flex; align-items: center; justify-content: center; gap: 10px; min-height: 44px; padding: 0 17px;
  border: 0; border-radius: 11px; color: #1c2c42; background: var(--lime);
  font-size: 12px; font-weight: 750; box-shadow: 0 8px 18px rgba(144,190,71,.18);
  cursor: pointer; transition: transform .18s ease, box-shadow .18s ease, background .18s ease;
}
.btn-primary:hover { background: #d5f69b; box-shadow: 0 11px 23px rgba(144,190,71,.24); transform: translateY(-1px); }
.btn-primary:disabled { opacity: .65; cursor: wait; transform: none; }
.panel { border: 1px solid rgba(225,230,238,.94); border-radius: var(--radius); background: var(--surface); box-shadow: var(--shadow); }
.home-intro { display: flex; align-items: flex-end; justify-content: space-between; gap: 22px; margin-bottom: 27px; }
.home-intro .hero-heading p { max-width: 590px; }
.home-layout { display: grid; grid-template-columns: minmax(0, 1.55fr) minmax(260px, .8fr); align-items: stretch; gap: 20px; }
.composer-panel { padding: clamp(22px, 3vw, 34px); }
.panel-heading { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; margin-bottom: 25px; }
.panel-heading h2, .section-heading h2 { margin: 0; color: var(--ink); font-size: 15px; font-weight: 700; letter-spacing: -.02em; }
.panel-heading p, .section-heading p { margin: 5px 0 0; color: var(--muted); font-size: 11px; }
.input-label { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin: 0 0 7px; color: #47566d; font-size: 11px; font-weight: 650; }
.optional-label { color: #9aa5b4; font-size: 9px; font-weight: 500; }
.field { margin-bottom: 17px; }
.text-input, .text-area, .filter-control, .inline-select, .notes-input {
  width: 100%; border: 1px solid #e1e7ef; border-radius: 10px; color: var(--ink); background: #fbfcfe;
  transition: border-color .16s ease, box-shadow .16s ease, background .16s ease;
}
.text-input, .filter-control, .inline-select { min-height: 42px; padding: 0 12px; }
.text-area { min-height: 168px; padding: 12px 13px; resize: vertical; line-height: 1.65; }
.text-input::placeholder, .text-area::placeholder, .notes-input::placeholder { color: #a8b2c0; }
.text-input:focus, .text-area:focus, .filter-control:focus, .inline-select:focus, .notes-input:focus { border-color: #98a3ed; background: #fff; box-shadow: 0 0 0 3px rgba(102,120,223,.10); outline: 0; }
.field-help { margin: 6px 0 0; color: #97a2b1; font-size: 9px; }
.sample-row { display: flex; flex-wrap: wrap; align-items: center; gap: 7px; margin: 0 0 21px; }
.sample-label { margin-right: 3px; color: #8c98aa; font-size: 9px; font-weight: 650; }
.sample-chip { padding: 6px 10px; border: 1px solid #e5eaf0; border-radius: 99px; color: #66758b; background: #fff; font-size: 9px; cursor: pointer; transition: .16s ease; }
.sample-chip:hover { border-color: #cbd4ee; color: #4f60cb; background: #f7f8ff; }
.form-footer { display: flex; align-items: center; justify-content: space-between; gap: 14px; padding-top: 17px; border-top: 1px solid #edf0f4; }
.privacy-note { display: flex; align-items: center; gap: 7px; color: #8d9aaa; font-size: 9px; }
.privacy-note svg { width: 14px; height: 14px; color: #76a16a; }
.workflow-panel { position: relative; overflow: hidden; padding: 24px; border-radius: var(--radius); color: #f1f5fb; background: radial-gradient(circle at 82% 8%, rgba(101,130,187,.30), transparent 29%), linear-gradient(145deg, #172941 0%, #203653 56%, #304761 100%); box-shadow: 0 18px 38px rgba(20,36,59,.16); }
.workflow-panel:after { position: absolute; right: -70px; bottom: -85px; width: 235px; height: 235px; border: 1px solid rgba(255,255,255,.09); border-radius: 50%; content: ""; }
.workflow-art { position: relative; display: grid; height: 178px; place-items: center; margin: -4px 0 8px; }
.workflow-art svg { width: min(100%, 265px); height: 180px; overflow: visible; }
.workflow-panel .eyebrow { color: #a7b7cd; }
.workflow-panel h2 { max-width: 260px; margin: 0; color: #fff; font-size: 19px; font-weight: 650; letter-spacing: -.035em; line-height: 1.35; }
.workflow-panel > p { margin: 8px 0 21px; color: #aebbd0; font-size: 10px; line-height: 1.7; }
.workflow-steps { display: grid; gap: 0; margin: 0; padding: 0; list-style: none; }
.workflow-step { display: grid; grid-template-columns: 25px minmax(0,1fr); gap: 10px; padding: 10px 0; border-top: 1px solid rgba(255,255,255,.11); }
.step-number { display: grid; width: 22px; height: 22px; place-items: center; border: 1px solid rgba(201,242,126,.32); border-radius: 8px; color: var(--lime); font-size: 9px; font-weight: 750; }
.workflow-step strong { display: block; color: #edf3fa; font-size: 10px; font-weight: 650; }
.workflow-step span { display: block; margin-top: 2px; color: #9eacc0; font-size: 9px; }
.result-slot { margin-top: 18px; }
.result-card { overflow: hidden; border: 1px solid #dce8d5; border-radius: 15px; background: #fbfdf8; }
.result-card-head { display: flex; align-items: center; justify-content: space-between; gap: 14px; padding: 17px 20px; border-bottom: 1px solid #e8efe3; }
.result-card-head h2 { margin: 0; font-size: 13px; }
.result-card-head p { margin: 4px 0 0; color: var(--muted); font-size: 10px; }
.result-score { display: grid; width: 54px; height: 54px; flex: 0 0 auto; place-items: center; border: 4px solid #d9f0b9; border-radius: 50%; color: #4e703f; background: #f2f9e9; font-size: 13px; font-weight: 750; }
.result-grid { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 12px; padding: 17px 20px; }
.result-field span { display: block; color: #8b9a84; font-size: 9px; font-weight: 650; text-transform: uppercase; letter-spacing: .08em; }
.result-field strong { display: block; margin-top: 4px; color: #344b35; font-size: 12px; text-transform: capitalize; }
.result-reply { margin: 0 20px 20px; padding: 14px 15px; border-radius: 10px; color: #52654e; background: #f1f6ec; font-size: 11px; line-height: 1.7; white-space: pre-wrap; }
.result-error { padding: 13px 15px; border: 1px solid #f0d0cb; border-radius: 11px; color: #984a43; background: #fff6f4; font-size: 11px; }
.stats-grid { display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 14px; margin: 0 0 16px; }
.stat-card { min-width: 0; padding: 17px 18px; border: 1px solid #e6eaf0; border-radius: 15px; background: #fff; box-shadow: 0 9px 24px rgba(28,45,70,.035); }
.stat-card-top { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.stat-icon { display: grid; width: 32px; height: 32px; place-items: center; border-radius: 10px; color: #596bd6; background: #f0f2ff; }
.stat-icon svg { width: 16px; height: 16px; }
.stat-icon.green { color: #568f76; background: #edf7f1; }
.stat-icon.orange { color: #b48236; background: #fff6e7; }
.stat-icon.pink { color: #ba6c67; background: #fff0ef; }
.stat-kicker { color: #a1aaba; font-size: 9px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; }
.stat-value { display: block; margin-top: 11px; color: var(--ink); font-size: 27px; font-weight: 700; letter-spacing: -.05em; line-height: 1; font-variant-numeric: tabular-nums; }
.stat-caption { display: block; margin-top: 7px; color: #8996a8; font-size: 9px; }
.overview-grid { display: grid; grid-template-columns: minmax(220px, .72fr) minmax(0, 1.8fr); gap: 15px; margin-bottom: 16px; }
.mix-panel { display: flex; align-items: center; gap: 20px; padding: 19px 20px; }
.mix-copy { min-width: 0; flex: 1; }
.mix-copy h2, .toolbar-title { margin: 0; color: var(--ink); font-size: 12px; font-weight: 700; }
.mix-copy p, .toolbar-subtitle { margin: 4px 0 0; color: var(--muted); font-size: 9px; }
.donut-chart { position: relative; display: grid; width: 90px; height: 90px; flex: 0 0 auto; place-items: center; border-radius: 50%; background: conic-gradient(var(--coral) 0 var(--high), var(--amber) var(--high) calc(var(--high) + var(--medium)), var(--teal) calc(var(--high) + var(--medium)) 100%); }
.donut-chart:after { position: absolute; width: 62px; height: 62px; border-radius: 50%; background: #fff; content: ""; }
.donut-center { position: relative; z-index: 1; text-align: center; }
.donut-center strong { display: block; color: var(--ink); font-size: 17px; line-height: 1; }
.donut-center span { display: block; margin-top: 4px; color: #9aa6b6; font-size: 8px; }
.mix-legend { display: flex; flex-wrap: wrap; gap: 8px 12px; margin-top: 15px; }
.legend-item { display: inline-flex; align-items: center; gap: 5px; color: #718096; font-size: 8px; }
.legend-dot { width: 6px; height: 6px; border-radius: 50%; }
.legend-dot.high { background: var(--coral); }
.legend-dot.medium { background: var(--amber); }
.legend-dot.low { background: var(--teal); }
.score-panel { padding: 19px 20px; }
.score-panel-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; margin-bottom: 16px; }
.score-bars { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 13px; }
.score-bar-label { display: flex; justify-content: space-between; gap: 6px; margin-bottom: 7px; color: #7c899c; font-size: 9px; }
.score-bar-track { overflow: hidden; height: 6px; border-radius: 99px; background: #eef1f5; }
.score-bar-fill { display: block; height: 100%; width: 0; border-radius: inherit; background: var(--blue); transition: width .35s ease; }
.score-bar-fill.green { background: var(--teal); }
.score-bar-fill.orange { background: var(--amber); }
.toolbar { display: flex; align-items: center; justify-content: space-between; gap: 15px; margin: 24px 0 12px; }
.toolbar-actions { display: flex; flex-wrap: wrap; align-items: center; gap: 7px; }
.filter-bar { display: grid; grid-template-columns: minmax(180px,1.5fr) repeat(3,minmax(120px, .8fr)); gap: 8px; margin-bottom: 12px; }
.search-control { position: relative; }
.search-control svg { position: absolute; top: 13px; left: 12px; width: 15px; height: 15px; color: #9ba7b6; pointer-events: none; }
.search-control .filter-control { padding-left: 35px; }
.filter-control { min-width: 0; border-radius: 9px; color: #637188; background-color: #fff; font-size: 10px; }
.quick-filters { display: flex; flex-wrap: wrap; gap: 7px; margin: 0 0 15px; }
.quick-filter { padding: 7px 11px; border: 1px solid transparent; border-radius: 99px; color: #8390a2; background: transparent; font-size: 9px; font-weight: 650; cursor: pointer; }
.quick-filter:hover { color: #5364cd; background: #f0f2ff; }
.quick-filter.active { border-color: #e2e6fb; color: #5364cd; background: #f3f4ff; }
.records-list { display: grid; gap: 10px; }
.record-card { padding: 16px 18px; border: 1px solid #e5eaf0; border-radius: 14px; background: #fff; box-shadow: 0 6px 18px rgba(28,45,70,.025); transition: box-shadow .18s ease, transform .18s ease; }
.record-card:hover { box-shadow: 0 11px 25px rgba(28,45,70,.065); transform: translateY(-1px); }
.record-top { display: grid; grid-template-columns: minmax(0,1fr) auto auto; align-items: center; gap: 18px; }
.record-identity { display: flex; align-items: center; gap: 12px; min-width: 0; }
.record-avatar { display: grid; width: 38px; height: 38px; flex: 0 0 auto; place-items: center; border: 1px solid #e6e9f7; border-radius: 12px; color: #5d6dd1; background: #f3f4ff; font-size: 11px; font-weight: 750; text-transform: uppercase; }
.record-copy { min-width: 0; }
.record-title { display: flex; flex-wrap: wrap; align-items: center; gap: 7px; color: #34435a; font-size: 11px; font-weight: 700; }
.record-preview { overflow: hidden; max-width: 670px; margin: 4px 0 0; color: #8491a3; font-size: 10px; text-overflow: ellipsis; white-space: nowrap; }
.badge { display: inline-flex; align-items: center; padding: 4px 8px; border-radius: 99px; color: #707e92; background: #f0f2f5; font-size: 8px; font-weight: 700; line-height: 1.2; text-transform: capitalize; }
.badge.category { color: #5969c9; background: #f0f2ff; }
.badge.priority.high { color: #b75f59; background: #fff0ee; }
.badge.priority.medium { color: #a4782f; background: #fff5e4; }
.badge.priority.low { color: #4f927c; background: #edf7f2; }
.status-badge { color: #557d6b; background: #eef7f1; }
.status-badge.contacted { color: #6676c8; background: #f0f2ff; }
.status-badge.closed { color: #798496; background: #f0f2f5; }
.record-score { display: flex; align-items: center; gap: 8px; color: #8592a4; font-size: 9px; white-space: nowrap; }
.score-track { overflow: hidden; width: 62px; height: 5px; border-radius: 99px; background: #eef1f5; }
.score-track span { display: block; height: 100%; border-radius: inherit; background: linear-gradient(90deg, #96d0a7, #74b991); }
.record-top-actions { display: flex; align-items: center; gap: 8px; }
.inline-select { width: 110px; min-height: 34px; padding: 0 8px; border-radius: 8px; color: #68768b; background: #fff; font-size: 9px; }
.record-details { margin-top: 12px; border-top: 1px solid #eff1f5; }
.record-details summary { width: fit-content; padding: 10px 0 0; color: #6878d6; font-size: 9px; font-weight: 650; cursor: pointer; list-style: none; }
.record-details summary::-webkit-details-marker { display: none; }
.record-details summary:after { display: inline-block; margin-left: 6px; content: "+"; font-size: 13px; }
.record-details[open] summary:after { content: "−"; }
.record-detail-grid { display: grid; grid-template-columns: minmax(0,1.2fr) minmax(220px,.8fr); gap: 15px; padding: 14px 0 2px; }
.detail-box { min-width: 0; padding: 13px; border-radius: 10px; background: #f8f9fc; }
.detail-label { margin: 0 0 6px; color: #8b98a9; font-size: 8px; font-weight: 750; letter-spacing: .1em; text-transform: uppercase; }
.detail-text { margin: 0; color: #536178; font-size: 10px; line-height: 1.65; white-space: pre-wrap; overflow-wrap: anywhere; }
.record-management { display: grid; grid-template-columns: minmax(180px,.7fr) minmax(260px,1.3fr); gap: 13px; margin-top: 12px; }
.management-field label { display: block; margin: 0 0 6px; color: #748198; font-size: 9px; font-weight: 650; }
.management-row { display: flex; align-items: center; gap: 7px; }
.management-row .text-input { min-height: 35px; padding: 0 9px; font-size: 9px; }
.management-row .btn { min-height: 35px; padding: 0 10px; font-size: 9px; white-space: nowrap; }
.notes-input { min-height: 60px; padding: 8px 9px; resize: vertical; font-size: 9px; }
.record-management .btn-danger { color: #b66059; border-color: #f1dddb; background: #fff8f7; }
.empty-state { display: grid; min-height: 185px; place-items: center; padding: 24px; border: 1px dashed #dce2eb; border-radius: 15px; color: #8390a3; background: rgba(255,255,255,.58); text-align: center; }
.empty-state svg { width: 35px; height: 35px; margin-bottom: 8px; color: #a5aed1; }
.empty-state strong { display: block; color: #536178; font-size: 12px; }
.empty-state p { margin: 5px 0 13px; font-size: 10px; }
.toast { position: fixed; right: 22px; bottom: 22px; z-index: 50; max-width: min(360px,calc(100vw - 36px)); padding: 12px 16px; border: 1px solid #dce9dd; border-radius: 11px; color: #42664a; background: #f6fbf5; box-shadow: 0 12px 35px rgba(24,40,62,.15); font-size: 11px; opacity: 0; pointer-events: none; transform: translateY(8px); transition: .2s ease; }
.toast.visible { opacity: 1; transform: translateY(0); }
.toast.error { border-color: #f0d2cc; color: #974c44; background: #fff7f5; }
.pipeline-board { display: grid; grid-template-columns: repeat(3,minmax(0,1fr)); align-items: start; gap: 14px; }
.pipeline-column { overflow: hidden; min-width: 0; border: 1px solid #e3e8ef; border-radius: 15px; background: #f8f9fc; }
.column-header { display: flex; align-items: center; justify-content: space-between; gap: 8px; padding: 14px 15px; border-bottom: 1px solid #e9edf2; background: #fff; }
.column-title { display: flex; align-items: center; gap: 9px; color: #394960; font-size: 11px; font-weight: 700; }
.column-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--blue); }
.column-dot.contacted { background: var(--amber); }
.column-dot.closed { background: var(--teal); }
.column-count { display: grid; min-width: 23px; height: 23px; place-items: center; padding: 0 6px; border-radius: 8px; color: #7d899b; background: #f0f2f6; font-size: 9px; font-weight: 700; }
.column-list { display: grid; gap: 9px; min-height: 190px; padding: 10px; }
.pipeline-card { min-width: 0; padding: 13px; border: 1px solid #e6eaf0; border-radius: 12px; background: #fff; box-shadow: 0 4px 12px rgba(28,45,70,.03); }
.pipeline-card-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; }
.pipeline-email { overflow: hidden; color: #3d4c62; font-size: 10px; font-weight: 700; text-overflow: ellipsis; white-space: nowrap; }
.pipeline-score { flex: 0 0 auto; padding: 4px 7px; border-radius: 7px; color: #4d8a70; background: #edf7f1; font-size: 8px; font-weight: 750; }
.pipeline-message { display: -webkit-box; overflow: hidden; min-height: 42px; margin: 8px 0 9px; color: #8592a4; font-size: 9px; line-height: 1.55; -webkit-box-orient: vertical; -webkit-line-clamp: 3; }
.pipeline-meta { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 11px; }
.pipeline-select { width: 100%; min-height: 33px; padding: 0 8px; border: 1px solid #e4e8ef; border-radius: 8px; color: #6c7a8e; background: #fbfcfe; font-size: 9px; }
.pipeline-empty { padding: 22px 10px; color: #a0aaba; font-size: 9px; text-align: center; }
.login-page { min-height: 100vh; padding: clamp(16px,4vw,40px); background: radial-gradient(circle at 12% 13%, rgba(193,231,158,.32), transparent 27%), radial-gradient(circle at 92% 85%, rgba(116,136,226,.13), transparent 26%), #f4f6fa; font-family: Inter, "Segoe UI Variable", Aptos, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
.login-shell { display: grid; grid-template-columns: minmax(0,1.05fr) minmax(360px,.95fr); overflow: hidden; width: min(100%,1040px); min-height: min(700px,calc(100vh - 80px)); margin: 0 auto; border: 1px solid #e7ebf0; border-radius: 24px; background: #fff; box-shadow: 0 28px 80px rgba(23,39,62,.12); }
.login-showcase { position: relative; display: flex; flex-direction: column; justify-content: space-between; overflow: hidden; padding: clamp(28px,5vw,55px); color: #f3f6fb; background: radial-gradient(circle at 87% 18%, rgba(105,135,192,.28), transparent 27%), linear-gradient(145deg,#14243b,#213652 75%,#304965); }
.login-showcase:before, .login-showcase:after { position: absolute; border: 1px solid rgba(255,255,255,.09); border-radius: 50%; content: ""; }
.login-showcase:before { top: 22%; right: -120px; width: 380px; height: 380px; }
.login-showcase:after { top: 29%; right: -60px; width: 260px; height: 260px; }
.login-brand { position: relative; z-index: 1; display: flex; align-items: center; gap: 12px; }
.login-brand-name { color: #fff; font-size: 12px; font-weight: 750; letter-spacing: .12em; }
.login-brand-sub { display: block; margin-top: 2px; color: #9baec5; font-size: 9px; letter-spacing: .04em; }
.login-visual { position: relative; z-index: 1; display: grid; place-items: center; min-height: 260px; }
.login-visual svg { width: min(100%,390px); }
.login-showcase-copy { position: relative; z-index: 1; max-width: 430px; }
.login-showcase-copy .eyebrow { color: #b5c6d9; }
.login-showcase-copy h2 { margin: 0; color: #fff; font-size: clamp(24px,3vw,36px); font-weight: 650; letter-spacing: -.045em; line-height: 1.2; }
.login-showcase-copy p { max-width: 390px; margin: 12px 0 0; color: #afbed1; font-size: 11px; line-height: 1.8; }
.login-form-panel { display: flex; flex-direction: column; justify-content: center; padding: clamp(28px,5vw,60px); }
.login-form-panel h1 { margin: 0; color: var(--ink); font-size: 29px; font-weight: 700; letter-spacing: -.045em; }
.login-form-panel > p { margin: 9px 0 27px; color: var(--muted); font-size: 11px; line-height: 1.7; }
.login-form-panel .input-label { margin-bottom: 8px; }
.login-form-panel .text-input { min-height: 46px; }
.login-submit { width: 100%; margin-top: 17px; }
.login-error { margin: 0 0 16px; padding: 10px 12px; border: 1px solid #f0d2cc; border-radius: 9px; color: #9a4d45; background: #fff6f4; font-size: 10px; }
.login-protect { display: flex; align-items: center; gap: 8px; margin-top: 22px; color: #92a0b0; font-size: 9px; }
.login-protect svg { width: 14px; height: 14px; color: #6fa16f; }
@media (max-width: 1120px) {
  .app-shell { grid-template-columns: 216px minmax(0,1fr); }
  .overview-grid { grid-template-columns: 1fr; }
  .mix-panel { justify-content: flex-start; }
}
@media (max-width: 850px) {
  .app-shell { grid-template-columns: 74px minmax(0,1fr); }
  .app-sidebar { align-items: center; padding: 20px 9px 15px; }
  .brand { justify-content: center; margin: 0 0 36px; }
  .brand-copy, .sidebar-caption, .nav-label, .sidebar-status, .sidebar-footnote { display: none; }
  .sidebar-nav { width: 100%; }
  .nav-link { justify-content: center; padding: 0; }
  .main-area .page-content { padding-right: 24px; padding-left: 24px; }
  .stats-grid { grid-template-columns: repeat(2,minmax(0,1fr)); }
  .pipeline-board { gap: 9px; }
  .record-top { grid-template-columns: minmax(0,1fr) auto; }
  .record-top-actions { grid-column: 1 / -1; justify-content: flex-end; }
  .record-score { display: none; }
}
@media (max-width: 650px) {
  .app-shell { display: block; }
  .app-sidebar { position: sticky; z-index: 20; top: 0; display: flex; flex-direction: row; justify-content: space-between; width: 100%; height: auto; min-height: 0; padding: 10px 15px; border-bottom: 1px solid rgba(255,255,255,.08); }
  .brand { margin: 0; }
  .brand-symbol { width: 34px; height: 34px; }
  .sidebar-nav { display: flex; width: auto; gap: 4px; }
  .nav-link { width: 38px; height: 38px; min-height: 38px; border-radius: 10px; }
  .main-area .page-content { padding: 24px 16px 38px; }
  .topbar { height: 59px; padding: 0 16px; }
  .session-pill { display: none; }
  .page-title-row, .home-intro { align-items: flex-start; flex-direction: column; }
  .home-layout { grid-template-columns: 1fr; }
  .workflow-panel { min-height: 380px; }
  .workflow-art { height: 155px; }
  .stats-grid { gap: 9px; }
  .stat-card { padding: 14px; }
  .stat-value { font-size: 23px; }
  .filter-bar { grid-template-columns: 1fr 1fr; }
  .filter-bar .search-control { grid-column: 1 / -1; }
  .toolbar { align-items: flex-start; flex-direction: column; }
  .score-bars { grid-template-columns: 1fr; gap: 9px; }
  .record-top { grid-template-columns: 1fr; gap: 10px; }
  .record-top-actions { grid-column: auto; justify-content: space-between; }
  .record-score { display: flex; }
  .record-detail-grid, .record-management { grid-template-columns: 1fr; }
  .pipeline-board { grid-template-columns: 1fr; }
  .column-list { min-height: 110px; }
  .result-grid { grid-template-columns: 1fr; gap: 10px; }
  .form-footer { align-items: flex-start; flex-direction: column; }
  .login-page { padding: 0; }
  .login-shell { grid-template-columns: 1fr; min-height: 100vh; border: 0; border-radius: 0; }
  .login-showcase { min-height: 290px; padding: 24px; }
  .login-visual { position: absolute; right: -5px; bottom: 1px; width: 45%; min-height: 0; opacity: .8; }
  .login-visual svg { width: 100%; }
  .login-showcase-copy { max-width: 72%; margin-top: 40px; }
  .login-showcase-copy h2 { font-size: 24px; }
  .login-form-panel { padding: 34px 26px 42px; }
}
@media (prefers-reduced-motion: reduce) {
  *, *:before, *:after { scroll-behavior: auto !important; animation-duration: .01ms !important; animation-iteration-count: 1 !important; transition-duration: .01ms !important; }
}
"""


NAV_ICONS = {
    "/": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 13.5 12 5l8 8.5"/><path d="M6.5 11v8h11v-8M10 19v-5h4v5"/></svg>',
    "/dashboard": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="4" y="4" width="6.5" height="7" rx="1.5"/><rect x="13.5" y="4" width="6.5" height="4" rx="1.5"/><rect x="13.5" y="10.5" width="6.5" height="9.5" rx="1.5"/><rect x="4" y="14" width="6.5" height="6" rx="1.5"/></svg>',
    "/pipeline": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3.5" y="4" width="5" height="16" rx="1.5"/><rect x="9.5" y="4" width="5" height="11" rx="1.5"/><rect x="15.5" y="4" width="5" height="7" rx="1.5"/></svg>',
    "/prospect-database": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5.5A1.5 1.5 0 0 1 9.5 4h5A1.5 1.5 0 0 1 16 5.5V7M3 12h18M10 12v2h4v-2"/></svg>',
    "/campaigns": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m4 13 4 4 11-11"/><path d="M15 6h4v4M4 7h6M4 20h10"/></svg>',
    "/retrofit-inquiries": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3.5 10.5 12 4l8.5 6.5M6 9v10h12V9M9.5 19v-5h5v5"/><path d="M17 5h3v3"/></svg>',
}


def build_protected_page(markup: str, path: str, csrf_token: str):
    page_names = {
        "/": "New analysis", "/dashboard": "Overview", "/pipeline": "Pipeline",
        "/prospect-database": "Business database", "/campaigns": "Campaign studio",
        "/retrofit-inquiries": "Retrofit enquiries",
    }
    page_name = page_names.get(path, "Workspace")
    nav = []
    for href, label in (
        ("/", "Message lab"), ("/dashboard", "Overview"),
        ("/pipeline", "Pipeline"), ("/prospect-database", "Businesses"),
        ("/campaigns", "Campaign studio"),
        ("/retrofit-inquiries", "Retrofit enquiries"),
    ):
        active = " active" if href == path else ""
        current = ' aria-current="page"' if href == path else ""
        nav.append(
            f'<a class="nav-link{active}" href="{href}"{current} aria-label="{escape(label, quote=True)}">'
            f'<span class="nav-icon">{NAV_ICONS[href]}</span><span class="nav-label">{label}</span></a>'
        )
    csrf_meta = f'<meta name="csrf-token" content="{escape(csrf_token, quote=True)}">'
    ui_meta = (
        '<meta name="theme-color" content="#14243b">'
        '<meta name="description" content="A private workspace to review customer messages and manage business prospects.">'
    )
    markup = markup.replace("<head>", "<head>\n" + csrf_meta + ui_meta, 1)
    markup = markup.replace("</head>", "<style>" + APP_THEME_CSS + "</style></head>", 1)
    shell = f"""
<div class="app-shell">
  <aside class="app-sidebar">
    <a class="brand" href="/" aria-label="Business AI workspace home">
      <span class="brand-symbol"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" aria-hidden="true"><path d="M12 2.8 14.3 9l6.2 2.6-6.2 2.3-2.3 6.2-2.6-6.2L3.2 11.6 9.4 9 12 2.8Z" fill="currentColor"/><circle cx="18.7" cy="5.3" r="1.4" fill="currentColor" opacity=".58"/></svg></span>
      <span class="brand-copy"><span class="brand-title">BUSINESS AI</span><span class="brand-subtitle">Automation workspace</span></span>
    </a>
    <p class="sidebar-caption">WORKSPACE</p>
    <nav class="sidebar-nav" aria-label="Primary navigation">{''.join(nav)}</nav>
    <div class="sidebar-spacer"></div>
    <div class="sidebar-status"><span class="status-pip"></span><div><strong>Private workspace</strong><span>Your records are protected by sign-in.</span></div></div>
    <p class="sidebar-footnote">Single-owner workspace · Private records</p>
  </aside>
  <main class="main-area">
    <header class="topbar">
      <div class="breadcrumbs"><span>Workspace</span><span class="crumb-mark">/</span><strong>{escape(page_name)}</strong></div>
      <div class="topbar-actions">
        <span class="session-pill"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><rect x="4.2" y="8.5" width="11.6" height="8.3" rx="2"/><path d="M6.8 8.5V6.2a3.2 3.2 0 0 1 6.4 0v2.3"/></svg>Protected session</span>
        <button type="button" id="logoutButton">Sign out</button>
      </div>
    </header>
    <div class="page-content">
"""
    markup = markup.replace("<body>", "<body>" + shell, 1)
    logout_script = """
<script>
document.getElementById("logoutButton").addEventListener("click", async function () {
  const csrf = document.querySelector('meta[name="csrf-token"]').content;
  const response = await fetch("/logout", {method: "POST", headers: {"X-CSRF-Token": csrf}});
  if (response.ok) window.location.href = "/login";
});
</script>
"""
    return markup.replace("</body>", "</div></main></div>" + logout_script + "</body>", 1)


def build_login_page(csrf_token: str, message: str = ""):
    error = f'<p class="login-error" role="alert">{escape(message)}</p>' if message else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="theme-color" content="#14243b">
  <meta name="description" content="A private workspace to review customer messages and manage business prospects.">
  <title>Sign in · Business AI</title>
  <style>
    :root {{ --canvas:#f4f6fa; --ink:#17243b; --muted:#8190a5; --lime:#c9f27e; }}
    * {{ box-sizing:border-box; }}
    html,body {{ min-width:320px; min-height:100%; margin:0; }}
    body {{ font-family:Inter,"Segoe UI Variable",Aptos,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; color:var(--ink); }}
    button,input {{ font:inherit; }}
    .login-page {{ min-height:100vh; padding:clamp(16px,4vw,40px); background:radial-gradient(circle at 12% 13%,rgba(193,231,158,.32),transparent 27%),radial-gradient(circle at 92% 85%,rgba(116,136,226,.13),transparent 26%),var(--canvas); }}
    .login-shell {{ display:grid; grid-template-columns:minmax(0,1.05fr) minmax(360px,.95fr); overflow:hidden; width:min(100%,1040px); min-height:min(700px,calc(100vh - 80px)); margin:0 auto; border:1px solid #e7ebf0; border-radius:24px; background:#fff; box-shadow:0 28px 80px rgba(23,39,62,.12); }}
    .login-showcase {{ position:relative; display:flex; flex-direction:column; justify-content:space-between; overflow:hidden; padding:clamp(28px,5vw,55px); color:#f3f6fb; background:radial-gradient(circle at 87% 18%,rgba(105,135,192,.28),transparent 27%),linear-gradient(145deg,#14243b,#213652 75%,#304965); }}
    .login-showcase:before,.login-showcase:after {{ position:absolute; border:1px solid rgba(255,255,255,.09); border-radius:50%; content:""; }}
    .login-showcase:before {{ top:22%; right:-120px; width:380px; height:380px; }}
    .login-showcase:after {{ top:29%; right:-60px; width:260px; height:260px; }}
    .login-brand {{ position:relative; z-index:1; display:flex; align-items:center; gap:12px; }}
    .login-brand-mark {{ display:grid; width:38px; height:38px; place-items:center; border-radius:13px; color:#15263c; background:linear-gradient(145deg,#d7f79b,#9ee0c7); }}
    .login-brand-name {{ color:#fff; font-size:12px; font-weight:750; letter-spacing:.12em; }}
    .login-brand-sub {{ display:block; margin-top:2px; color:#9baec5; font-size:9px; }}
    .login-visual {{ position:relative; z-index:1; display:grid; place-items:center; min-height:260px; }}
    .login-visual svg {{ width:min(100%,390px); }}
    .login-copy {{ position:relative; z-index:1; max-width:430px; }}
    .login-kicker {{ display:flex; align-items:center; gap:8px; margin:0 0 10px; color:#b5c6d9; font-size:9px; font-weight:750; letter-spacing:.16em; text-transform:uppercase; }}
    .login-copy h2 {{ margin:0; color:#fff; font-size:clamp(24px,3vw,36px); font-weight:650; letter-spacing:-.045em; line-height:1.2; }}
    .login-copy p {{ max-width:390px; margin:12px 0 0; color:#afbed1; font-size:11px; line-height:1.8; }}
    .login-form-panel {{ display:flex; flex-direction:column; justify-content:center; padding:clamp(28px,5vw,60px); }}
    .login-form-panel h1 {{ margin:0; font-size:29px; font-weight:700; letter-spacing:-.045em; }}
    .login-lede {{ margin:9px 0 27px; color:var(--muted); font-size:11px; line-height:1.7; }}
    .login-error {{ margin:0 0 16px; padding:10px 12px; border:1px solid #f0d2cc; border-radius:9px; color:#9a4d45; background:#fff6f4; font-size:10px; }}
    .login-label {{ display:block; margin:0 0 8px; color:#47566d; font-size:11px; font-weight:650; }}
    .login-password {{ width:100%; min-height:46px; padding:0 13px; border:1px solid #e1e7ef; border-radius:10px; color:var(--ink); background:#fbfcfe; }}
    .login-password:focus {{ border-color:#98a3ed; background:#fff; box-shadow:0 0 0 3px rgba(102,120,223,.10); outline:0; }}
    .login-password:focus-visible,.login-submit:focus-visible {{ outline:3px solid rgba(102,120,223,.38); outline-offset:3px; }}
    .login-submit {{ display:flex; align-items:center; justify-content:center; width:100%; min-height:45px; margin-top:17px; border:0; border-radius:11px; color:#1c2c42; background:var(--lime); font-size:12px; font-weight:750; cursor:pointer; }}
    .login-submit:hover {{ background:#d5f69b; }}
    .login-protect {{ display:flex; align-items:center; gap:8px; margin-top:22px; color:#92a0b0; font-size:9px; }}
    .login-protect svg {{ width:14px; height:14px; color:#6fa16f; }}
    @media(max-width:650px) {{ .login-page {{ padding:0; }} .login-shell {{ grid-template-columns:1fr; min-height:100vh; border:0; border-radius:0; }} .login-showcase {{ min-height:290px; padding:24px; }} .login-visual {{ position:absolute; right:-5px; bottom:1px; width:45%; min-height:0; opacity:.8; }} .login-visual svg {{ width:100%; }} .login-copy {{ max-width:72%; margin-top:40px; }} .login-copy h2 {{ font-size:24px; }} .login-form-panel {{ padding:34px 26px 42px; }} }}
  </style>
</head>
<body class="login-page">
  <main class="login-shell">
    <section class="login-showcase">
      <div class="login-brand"><span class="login-brand-mark"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" aria-hidden="true"><path d="M12 2.8 14.3 9l6.2 2.6-6.2 2.3-2.3 6.2-2.6-6.2L3.2 11.6 9.4 9 12 2.8Z" fill="currentColor"/></svg></span><span><span class="login-brand-name">BUSINESS AI</span><span class="login-brand-sub">Automation workspace</span></span></div>
      <div class="login-visual">
        <svg viewBox="0 0 390 255" fill="none" role="img" aria-label="Abstract workflow illustration">
          <circle cx="195" cy="126" r="83" stroke="#7386A5" stroke-opacity=".42"/>
          <circle cx="195" cy="126" r="60" stroke="#A4B4CC" stroke-opacity=".25" stroke-dasharray="3 7"/>
          <path d="M56 160c40-72 80 28 122-34 33-49 65-47 96-7 23 29 37 34 61 2" stroke="#C9F27E" stroke-width="2.5" stroke-linecap="round"/>
          <circle cx="57" cy="159" r="6" fill="#C9F27E"/><circle cx="179" cy="126" r="6" fill="#8ED3B5"/><circle cx="335" cy="121" r="6" fill="#C9F27E"/>
          <rect x="131" y="77" width="129" height="97" rx="18" fill="#F7FAFD" fill-opacity=".96"/>
          <rect x="147" y="94" width="49" height="7" rx="3.5" fill="#DCE4ED"/>
          <rect x="147" y="109" width="83" height="6" rx="3" fill="#E8EDF3"/>
          <rect x="147" y="124" width="61" height="6" rx="3" fill="#E8EDF3"/>
          <rect x="147" y="145" width="72" height="15" rx="7.5" fill="#E8F5D9"/>
          <path d="m157 152 3 3 6-6" stroke="#5C8750" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          <rect x="267" y="46" width="54" height="42" rx="12" fill="#2B4261" stroke="#68809F" stroke-opacity=".6"/>
          <path d="M281 73V63m9 10V57m9 16v-7" stroke="#C9F27E" stroke-width="4" stroke-linecap="round"/>
          <rect x="67" y="88" width="48" height="39" rx="12" fill="#2B4261" stroke="#68809F" stroke-opacity=".6"/>
          <circle cx="91" cy="101" r="5" stroke="#9DE0C7" stroke-width="2"/><path d="M81 117c2-6 6-8 10-8s8 2 10 8" stroke="#9DE0C7" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </div>
      <div class="login-copy"><p class="login-kicker">YOUR PRIVATE WORKSPACE</p><h2>Good decisions start with a little clarity.</h2><p>Review enquiries, spot the important details, and keep every next step in one calm place.</p></div>
    </section>
    <section class="login-form-panel">
      <p class="login-kicker" style="color:#8b98aa">SECURE SIGN-IN</p>
      <h1>Welcome back</h1>
      <p class="login-lede">Sign in to continue to your protected automation workspace.</p>
      {error}
      <form method="post" action="/login">
        <input type="hidden" name="csrf_token" value="{escape(csrf_token, quote=True)}">
        <label class="login-label" for="password">Workspace password</label>
        <input class="login-password" id="password" name="password" type="password" autocomplete="current-password" required>
        <button class="login-submit" type="submit">Continue to workspace <span aria-hidden="true">→</span></button>
      </form>
      <div class="login-protect"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><rect x="4.2" y="8.5" width="11.6" height="8.3" rx="2"/><path d="M6.8 8.5V6.2a3.2 3.2 0 0 1 6.4 0v2.3"/></svg>Your saved records stay behind sign-in.</div>
    </section>
  </main>
</body>
</html>"""


BUSINESS_DATABASE_PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Businesses · Business AI</title>
  <style>
    .business-intro { margin-bottom: 22px; }
    .business-toolbar { display:flex; align-items:center; justify-content:space-between; gap:15px; margin-bottom:14px; padding:14px 16px; }
    .business-count { color:#8290a2; font-size:10px; }
    .business-search { width:min(100%,360px); }
    .business-list { display:grid; gap:12px; }
    .business-card { padding:18px 20px; border:1px solid #e5eaf0; border-radius:15px; background:#fff; box-shadow:0 6px 18px rgba(28,45,70,.025); }
    .business-card-top { display:flex; align-items:flex-start; justify-content:space-between; gap:16px; }
    .business-card h2 { margin:0; color:#34435a; font-size:15px; letter-spacing:-.02em; }
    .business-tags { display:flex; flex-wrap:wrap; gap:6px; margin-top:7px; }
    .business-tag { padding:4px 8px; border:1px solid #e7eaf2; border-radius:99px; color:#727f94; background:#fafbfe; font-size:9px; }
    .business-location { margin:6px 0 0; color:#8794a5; font-size:10px; }
    .business-site { color:#5d6dd1; font-size:10px; font-weight:650; }
    .business-details { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; margin-top:16px; }
    .business-detail { min-width:0; padding:13px 14px; border:1px solid #edf0f4; border-radius:11px; background:#fbfcfe; }
    .business-detail h3 { margin:0 0 8px; color:#53627a; font-size:10px; font-weight:700; }
    .business-detail p { margin:4px 0; overflow-wrap:anywhere; color:#7a8799; font-size:10px; }
    .business-detail strong { color:#46566f; font-weight:650; }
    .business-sources { display:flex; flex-wrap:wrap; gap:12px; margin-top:12px; color:#6878cf; font-size:9px; }
    .business-empty { padding:34px 18px; border:1px dashed #dce2eb; border-radius:14px; color:#8794a5; background:#fff; font-size:11px; text-align:center; }
    @media(max-width:650px) { .business-toolbar { align-items:stretch; flex-direction:column; } .business-details { grid-template-columns:1fr; } .business-card-top { flex-direction:column; } }
  </style>
</head>
<body>
  <section class="page-title-row business-intro">
    <div>
      <p class="eyebrow"><span class="eyebrow-dot"></span>PROSPECTING</p>
      <h1>Business database</h1>
      <p>One private workspace for businesses across industries, with published details separated from Hunter or Apollo enrichment.</p>
    </div>
  </section>
  <section class="business-toolbar panel" aria-label="Business list tools">
    <span class="business-count" id="businessCount">Loading saved businesses…</span>
    <input class="filter-control business-search" id="businessSearch" type="search" placeholder="Search by name, industry, location or provider" aria-label="Search businesses">
  </section>
  <div class="business-list" id="businessList" aria-live="polite"></div>
  <script>
    let businessRows = [];
    function textNode(tag, className, value) {
      const node = document.createElement(tag);
      if (className) node.className = className;
      node.textContent = value == null ? "" : String(value);
      return node;
    }
    function safeLink(value, label, className) {
      if (!value) return null;
      try {
        const url = new URL(value, window.location.origin);
        if (url.protocol !== "https:" && url.protocol !== "http:") return null;
        const link = textNode("a", className || "", label || value);
        link.href = url.href;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        return link;
      } catch (_) { return null; }
    }
    function detailBlock(title, fields) {
      const panel = textNode("section", "business-detail", "");
      panel.appendChild(textNode("h3", "", title));
      fields.forEach(function (field) {
        if (!field.value) return;
        const row = textNode("p", "", "");
        row.appendChild(textNode("strong", "", field.label + ": "));
        row.appendChild(document.createTextNode(String(field.value)));
        panel.appendChild(row);
      });
      return panel;
    }
    function renderBusiness(row) {
      const card = textNode("article", "business-card", "");
      const top = textNode("div", "business-card-top", "");
      const identity = textNode("div", "", "");
      identity.appendChild(textNode("h2", "", row.business_name || "Unnamed business"));
      const tags = textNode("div", "business-tags", "");
      [row.industry, row.business_type].filter(Boolean).forEach(function (value) {
        tags.appendChild(textNode("span", "business-tag", value));
      });
      identity.appendChild(tags);
      const location = [row.city, row.region, row.country].filter(Boolean).join(", ");
      if (location) identity.appendChild(textNode("p", "business-location", location));
      top.appendChild(identity);
      const website = safeLink(row.website, row.website, "business-site");
      if (website) top.appendChild(website);
      card.appendChild(top);
      const details = textNode("div", "business-details", "");
      details.appendChild(detailBlock("Published by the business", [
        {label:"Email",value:row.business_email}, {label:"Phone",value:row.business_phone},
        {label:"Named contact",value:row.contact_name}, {label:"Role",value:row.contact_role}
      ]));
      const enriched = detailBlock("Third-party enrichment", [
        {label:"Provider",value:row.enrichment_provider},
        {label:"Status",value:row.enrichment_status},
        {label:"Confidence",value:row.enrichment_confidence},
        {label:"Email",value:row.enriched_email}, {label:"Phone",value:row.enriched_phone},
        {label:"Contact",value:row.enriched_contact_name}, {label:"Role",value:row.enriched_contact_role}
      ]);
      if (!row.enrichment_provider && !row.enriched_email && !row.enriched_phone && !row.enriched_contact_name) {
        enriched.appendChild(textNode("p", "", "No third-party enrichment saved."));
      }
      details.appendChild(enriched);
      card.appendChild(details);
      const sources = textNode("div", "business-sources", "");
      const source = safeLink(row.source_url, "Business source", "");
      const contactSource = safeLink(row.contact_source_url, "Published contact source", "");
      const enrichmentSource = safeLink(row.enrichment_source_url, "Enrichment source", "");
      [source, contactSource, enrichmentSource].filter(Boolean).forEach(function (link) { sources.appendChild(link); });
      if (sources.childNodes.length) card.appendChild(sources);
      return card;
    }
    function renderBusinesses() {
      const query = document.getElementById("businessSearch").value.trim().toLowerCase();
      const filtered = businessRows.filter(function (row) {
        return [row.business_name,row.industry,row.business_type,row.city,row.region,row.country,
          row.enrichment_provider,row.enrichment_status,row.enriched_contact_name,row.enriched_email]
          .some(function (value) { return String(value || "").toLowerCase().includes(query); });
      });
      const list = document.getElementById("businessList");
      list.replaceChildren();
      document.getElementById("businessCount").textContent = filtered.length + " of " + businessRows.length + " saved businesses";
      if (!filtered.length) {
        list.appendChild(textNode("div", "business-empty", businessRows.length ? "No businesses match that search." : "No businesses saved yet. Use the Business Prospect Finder skill with Agensi tools, then ask it to save selected results here."));
        return;
      }
      filtered.forEach(function (row) { list.appendChild(renderBusiness(row)); });
    }
    document.getElementById("businessSearch").addEventListener("input", renderBusinesses);
    fetch("/businesses?limit=500", {credentials:"same-origin"}).then(function (response) {
      if (!response.ok) throw new Error("Could not load the private business list.");
      return response.json();
    }).then(function (data) {
      businessRows = Array.isArray(data) ? data : [];
      renderBusinesses();
    }).catch(function (error) {
      document.getElementById("businessCount").textContent = "Business list unavailable";
      document.getElementById("businessList").appendChild(textNode("div", "business-empty", error.message));
    });
  </script>
</body>
</html>"""


CAMPAIGNS_PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Campaign studio · Business AI</title>
  <style>
    .campaign-intro { margin-bottom:22px; }
    .campaign-grid { display:grid; grid-template-columns:minmax(280px,.82fr) minmax(0,1.18fr); gap:16px; align-items:start; }
    .campaign-panel { padding:20px; }
    .campaign-panel h2 { margin:0; color:#34435a; font-size:14px; }
    .campaign-panel > p { color:#8290a2; font-size:10px; line-height:1.6; }
    .campaign-form { display:grid; gap:11px; }
    .campaign-form label { display:grid; gap:5px; color:#596980; font-size:10px; font-weight:650; }
    .campaign-form input,.campaign-form select,.campaign-form textarea,.campaign-discovery input,.campaign-discovery select,.draft-editor input,.draft-editor textarea { width:100%; padding:10px 11px; border:1px solid #dfe6ef; border-radius:9px; color:#26364d; background:#fbfcfe; font:inherit; font-size:11px; }
    .campaign-form textarea,.draft-editor textarea { min-height:76px; resize:vertical; line-height:1.55; }
    .campaign-row { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
    .campaign-list { display:grid; gap:9px; margin-top:12px; }
    .campaign-list-card { display:flex; align-items:center; justify-content:space-between; gap:12px; padding:13px; border:1px solid #e8edf3; border-radius:11px; background:#fff; }
    .campaign-list-card h3 { margin:0 0 4px; color:#34435a; font-size:11px; }
    .campaign-list-card p { margin:0; color:#8794a5; font-size:9px; }
    .campaign-workspace { margin-top:18px; }
    .campaign-workspace-head { display:flex; align-items:flex-start; justify-content:space-between; gap:15px; margin-bottom:14px; }
    .campaign-workspace-head h2 { margin:4px 0; color:#293a51; font-size:20px; }
    .campaign-workspace-head p { margin:0; max-width:700px; color:#7e8ca0; font-size:10px; line-height:1.6; }
    .campaign-tools { display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:14px; margin-bottom:14px; }
    .campaign-discovery { display:grid; grid-template-columns:1fr 1fr auto; gap:8px; margin-top:12px; }
    .campaign-discovery label { display:grid; gap:5px; color:#596980; font-size:9px; font-weight:650; }
    .campaign-privacy { padding:13px 14px; border:1px solid #e5e9f1; border-radius:11px; color:#76849a; background:#f8fafc; font-size:9px; line-height:1.6; }
    .campaign-privacy strong { color:#526178; }
    .campaign-leads-head { display:flex; align-items:center; justify-content:space-between; gap:12px; margin:18px 0 10px; }
    .campaign-leads-head h3 { margin:0; color:#34435a; font-size:13px; }
    .campaign-lead-list { display:grid; gap:11px; }
    .campaign-lead { padding:16px; border:1px solid #e5eaf0; border-radius:13px; background:#fff; box-shadow:0 6px 18px rgba(28,45,70,.025); }
    .campaign-lead-top { display:flex; justify-content:space-between; align-items:flex-start; gap:12px; }
    .campaign-lead-top h4 { margin:0 0 4px; color:#34435a; font-size:12px; }
    .campaign-lead-meta { color:#8794a5; font-size:9px; }
    .campaign-lead-link { margin-top:5px; color:#5d6dd1; font-size:9px; }
    .campaign-lead-actions { display:flex; flex-wrap:wrap; gap:7px; margin-top:9px; }
    .campaign-lead-actions button,.campaign-actions button { min-height:32px; padding:0 11px; border:1px solid #e2e8f0; border-radius:8px; color:#526178; background:#fff; font:inherit; font-size:9px; font-weight:650; cursor:pointer; }
    .campaign-lead-actions button:hover,.campaign-actions button:hover { border-color:#c7d1e0; background:#f8fafc; }
    .campaign-lead-actions .approve-button { border-color:#c9e3b5; color:#527345; background:#f4faef; }
    .campaign-lead-actions .reject-button { color:#8c5b55; }
    .campaign-status { display:inline-flex; padding:4px 8px; border:1px solid #e5eaf1; border-radius:99px; color:#758399; background:#f8fafc; font-size:8px; font-weight:750; text-transform:uppercase; letter-spacing:.06em; white-space:nowrap; }
    .campaign-status.status-approved { border-color:#d0e6c4; color:#527345; background:#f5faef; }
    .campaign-status.status-rejected { border-color:#f0d7d2; color:#925d56; background:#fff8f6; }
    .campaign-status.status-needs_review { border-color:#e6dfc8; color:#8d7641; background:#fffdf3; }
    .campaign-editor-label { display:grid; gap:5px; margin-top:12px; color:#68768b; font-size:9px; font-weight:650; }
    .campaign-select { margin:2px 6px 0 0; accent-color:#6577d2; }
    .campaign-empty { padding:24px 16px; border:1px dashed #dce2eb; border-radius:12px; color:#8794a5; background:#fff; font-size:10px; text-align:center; }
    .campaign-alert { display:none; margin:0 0 14px; padding:11px 13px; border:1px solid #dce9d3; border-radius:10px; color:#526e46; background:#f6fbf2; font-size:10px; }
    .campaign-alert.visible { display:block; }
    .campaign-alert.error { border-color:#f0d0cb; color:#984a43; background:#fff6f4; }
    .campaign-footnote { margin:10px 0 0; color:#98a2b0; font-size:8px; line-height:1.5; }
    @media(max-width:900px) { .campaign-grid,.campaign-tools { grid-template-columns:1fr; } }
    @media(max-width:620px) { .campaign-row,.campaign-discovery { grid-template-columns:1fr; } .campaign-workspace-head,.campaign-leads-head { align-items:stretch; flex-direction:column; } .campaign-list-card { align-items:flex-start; flex-direction:column; } }
  </style>
</head>
<body>
  <section class="page-title-row campaign-intro">
    <div><p class="eyebrow"><span class="eyebrow-dot"></span>PROSPECTING WORKFLOW</p><h1>Campaign studio</h1><p>Find source-linked local businesses, group them by offer, and prepare outreach drafts for your review.</p></div>
  </section>
  <div class="campaign-alert" id="campaignAlert" role="status" aria-live="polite"></div>
  <div class="campaign-grid" id="campaignListView">
    <section class="panel campaign-panel">
      <h2>Build a campaign brief</h2>
      <p>Describe the service you offer and who it helps. The brief keeps each draft on-topic.</p>
      <form class="campaign-form" id="campaignCreateForm">
        <label>Campaign name<input name="title" maxlength="160" required placeholder="Website refresh for independent clinics"></label>
        <div class="campaign-row"><label>Industry<input name="industry" maxlength="120" placeholder="Healthcare"></label><label>Business type<input name="business_type" maxlength="120" placeholder="Aesthetic clinic"></label></div>
        <div class="campaign-row"><label>Region<input name="region" maxlength="120" placeholder="West Midlands"></label><label>Country<input name="country" maxlength="120" placeholder="United Kingdom"></label></div>
        <label>Your offer<textarea name="offer" maxlength="3000" required placeholder="What you do, who it is for, and the problem it solves."></textarea></label>
        <label>Evidence you can honestly claim <span class="optional-label">Optional</span><textarea name="proof" maxlength="1500" placeholder="A result or experience you can verify. Leave blank if you have none."></textarea></label>
        <div class="campaign-row"><label>Tone<select name="tone"><option>Professional</option><option>Warm</option><option>Direct</option><option>Conversational</option></select></label><label>Draft language<input name="language" maxlength="80" value="English"></label></div>
        <button class="btn-primary" type="submit">Create campaign</button>
      </form>
    </section>
    <section class="panel campaign-panel">
      <h2>Your campaigns</h2>
      <p>Each campaign has its own selected businesses and review-only drafts.</p>
      <div class="campaign-list" id="campaignList"><div class="campaign-empty">Loading campaigns…</div></div>
    </section>
  </div>
  <section class="campaign-workspace" id="campaignWorkspace" hidden>
    <div class="campaign-workspace-head">
      <div><button class="btn" type="button" id="backToCampaigns">← All campaigns</button><p class="eyebrow" style="margin-top:14px">CAMPAIGN WORKSPACE</p><h2 id="workspaceTitle"></h2><p id="workspaceBrief"></p></div>
      <div class="campaign-actions"><a class="btn" id="exportCampaign" href="#">Export campaign CSV</a></div>
    </div>
    <div class="campaign-tools">
      <section class="panel campaign-panel">
        <h2>Find local businesses</h2>
        <p>Search named business listings in OpenStreetMap. Results can be incomplete; verify fit and contact details before use.</p>
        <form class="campaign-discovery" id="campaignDiscoveryForm">
          <label>Business type<input name="business_type" maxlength="120" required placeholder="Aesthetic clinic"></label>
          <label>City, town or postcode<input name="location" maxlength="120" required placeholder="Birmingham"></label>
          <label>Search radius<select name="radius_m"><option value="1000">1 km</option><option value="3000">3 km</option><option value="5000" selected>5 km</option><option value="10000">10 km</option></select></label>
          <button class="btn-primary" type="submit">Find businesses</button>
        </form>
        <p class="campaign-footnote">Source: <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">© OpenStreetMap contributors</a> · ODbL. Search by business area, not a person's address. The business type and location are sent to public map services only when you search. See the <a href="https://operations.osmfoundation.org/policies/nominatim/" target="_blank" rel="noopener noreferrer">Nominatim usage policy</a>.</p>
      </section>
      <aside class="campaign-privacy"><strong>Review before contact</strong><br>Without an AI key, the app creates a basic template locally. With a configured AI key, drafting sends your campaign brief and selected business listing fields (name, type, area and website) to that provider; saved contact names, email addresses and phone numbers are excluded. Do not put confidential or personal data in the brief. AI drafting may incur provider charges. No messages are sent from this page; approval only marks a draft ready for you to copy or export.</aside>
      <section class="panel campaign-panel">
        <h2>Add saved businesses</h2>
        <p>Bring leads you already saved through the Business Prospect Finder, Apollo, Hunter, or another trusted source into this campaign.</p>
        <label class="campaign-editor-label" for="savedBusinessFilter">Filter saved records<input id="savedBusinessFilter" type="search" placeholder="Search by business, type, or location"></label>
        <label class="campaign-editor-label" for="savedBusinessSelect">Select businesses<select id="savedBusinessSelect" multiple size="7" aria-label="Choose saved businesses"></select></label>
        <div class="campaign-lead-actions"><button type="button" class="approve-button" id="addSavedBusinesses">Add selected businesses</button></div>
        <p class="campaign-footnote">Only selected businesses are linked. Existing records and enrichment fields are left unchanged.</p>
      </section>
    </div>
    <section>
      <div class="campaign-leads-head"><div><h3 id="leadHeading">Campaign businesses</h3><span class="business-count" id="leadCounts"></span></div><button class="btn-primary" type="button" id="generateDrafts">Generate drafts for selected (up to 10)</button></div>
      <div class="campaign-lead-list" id="campaignLeads"><div class="campaign-empty">Create a campaign, then search for businesses to get started.</div></div>
    </section>
  </section>
  <script>
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    let currentCampaign = null;
    let savedBusinesses = [];
    function node(tag, className, value) {
      const item = document.createElement(tag);
      if (className) item.className = className;
      if (value !== undefined && value !== null) item.textContent = String(value);
      return item;
    }
    function showNotice(message, isError) {
      const box = document.getElementById("campaignAlert");
      box.textContent = message || "";
      box.className = "campaign-alert visible" + (isError ? " error" : "");
    }
    async function api(path, method, body) {
      const headers = {"Accept":"application/json"};
      if (body !== undefined) headers["Content-Type"] = "application/json";
      if (method && method !== "GET") headers["X-CSRF-Token"] = csrfToken;
      const response = await fetch(path, {method:method || "GET", headers:headers, credentials:"same-origin", body:body === undefined ? undefined : JSON.stringify(body)});
      if (!response.ok) {
        const data = await response.json().catch(function(){ return {}; });
        throw new Error(data.detail || "The request could not be completed.");
      }
      return response.json();
    }
    function safeLink(url, label) {
      if (!url) return null;
      try {
        const normalized = /^[a-z][a-z0-9+.-]*:\\/\\//i.test(url) ? url : "https://" + url;
        const parsed = new URL(normalized);
        if (parsed.protocol !== "http:" && parsed.protocol !== "https:") return null;
        const link = node("a", "campaign-lead-link", label || url);
        link.href = parsed.href;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        return link;
      } catch (_) { return null; }
    }
    function renderCampaigns(items) {
      const list = document.getElementById("campaignList");
      list.replaceChildren();
      if (!items.length) {
        list.appendChild(node("div", "campaign-empty", "No campaigns yet. Create a brief to start collecting leads."));
        return;
      }
      items.forEach(function(item) {
        const card = node("article", "campaign-list-card", "");
        const copy = node("div", "", "");
        copy.appendChild(node("h3", "", item.title));
        copy.appendChild(node("p", "", [item.business_type || item.industry, item.region, item.country].filter(Boolean).join(" · ") + " · " + item.lead_count + " businesses · " + item.draft_counts.needs_review + " to review"));
        const open = node("button", "btn", "Open campaign");
        open.type = "button";
        open.addEventListener("click", function(){ openCampaign(item.id); });
        card.append(copy, open);
        list.appendChild(card);
      });
    }
    async function loadCampaigns() {
      try { renderCampaigns(await api("/api/campaigns", "GET")); }
      catch (error) { showNotice(error.message, true); }
    }
    function renderSavedBusinesses() {
      const select = document.getElementById("savedBusinessSelect");
      const query = document.getElementById("savedBusinessFilter").value.trim().toLowerCase();
      select.replaceChildren();
      const matches = savedBusinesses.filter(function(item) {
        return [item.business_name,item.business_type,item.industry,item.city,item.region,item.country]
          .some(function(value){ return String(value || "").toLowerCase().includes(query); });
      });
      if (!matches.length) {
        const option = node("option", "", savedBusinesses.length ? "No saved businesses match." : "No saved businesses yet.");
        option.disabled = true;
        select.appendChild(option);
        return;
      }
      matches.forEach(function(item) {
        const option = node("option", "", [item.business_name,item.business_type,item.city,item.region].filter(Boolean).join(" · "));
        option.value = String(item.id);
        select.appendChild(option);
      });
    }
    async function loadSavedBusinesses() {
      try { savedBusinesses = await api("/businesses?limit=500", "GET"); renderSavedBusinesses(); }
      catch (error) { showNotice(error.message, true); }
    }
    async function openCampaign(id) {
      try {
        currentCampaign = await api("/api/campaigns/" + id, "GET");
        document.getElementById("campaignListView").hidden = true;
        document.getElementById("campaignWorkspace").hidden = false;
        document.getElementById("workspaceTitle").textContent = currentCampaign.title;
        const brief = [currentCampaign.offer, currentCampaign.proof ? "Evidence: " + currentCampaign.proof : "", currentCampaign.tone + " · " + currentCampaign.language].filter(Boolean).join(" — ");
        document.getElementById("workspaceBrief").textContent = brief;
        const discoveryForm = document.getElementById("campaignDiscoveryForm");
        discoveryForm.elements.business_type.value = currentCampaign.business_type || currentCampaign.industry || "";
        discoveryForm.elements.location.value = [currentCampaign.region, currentCampaign.country].filter(Boolean).join(", ");
        document.getElementById("exportCampaign").href = "/api/campaigns/" + id + "/export.csv";
        renderLeads(currentCampaign);
      } catch (error) { showNotice(error.message, true); }
    }
    function renderLeads(campaign) {
      const list = document.getElementById("campaignLeads");
      list.replaceChildren();
      document.getElementById("leadHeading").textContent = campaign.title + " businesses";
      const counts = campaign.draft_counts || {};
      document.getElementById("leadCounts").textContent = campaign.lead_count + " businesses · " + (counts.needs_review || 0) + " drafts to review · " + (counts.approved || 0) + " approved";
      if (!campaign.leads.length) {
        list.appendChild(node("div", "campaign-empty", "No businesses in this campaign yet. Use the search above or save businesses with your connected prospecting skill."));
        return;
      }
      campaign.leads.forEach(function(lead) {
        const card = node("article", "campaign-lead", "");
        const top = node("div", "campaign-lead-top", "");
        const identity = node("div", "", "");
        const title = node("h4", "", "");
        const select = document.createElement("input");
        select.type = "checkbox";
        select.className = "campaign-select draft-select";
        select.value = String(lead.id);
        select.checked = lead.draft_status === "not_drafted";
        title.append(select, document.createTextNode(lead.business_name));
        identity.appendChild(title);
        identity.appendChild(node("div", "campaign-lead-meta", [lead.business_type, lead.city, lead.region, lead.country].filter(Boolean).join(" · ")));
        const website = safeLink(lead.website, lead.website);
        const source = safeLink(lead.source_url, "OpenStreetMap source");
        if (website) identity.appendChild(website);
        const status = node("span", "campaign-status status-" + lead.draft_status, (lead.draft_status || "not_drafted").replaceAll("_", " "));
        top.append(identity, status);
        card.appendChild(top);
        const fit = node("p", "campaign-lead-meta", lead.fit_summary || "");
        fit.style.margin = "7px 0 0";
        card.appendChild(fit);
        if (source) card.appendChild(source);
        const stage = document.createElement("select");
        [["new","New"],["contacted","Contacted"],["replied","Replied"],["won","Won"],["lost","Lost"]].forEach(function(pair){
          const option = node("option", "", pair[1]);
          option.value = pair[0];
          stage.appendChild(option);
        });
        stage.value = lead.pipeline_stage || "new";
        const stageLabel = node("label", "campaign-editor-label", "Campaign stage");
        stageLabel.appendChild(stage);
        const subject = document.createElement("input");
        subject.maxLength = 240;
        subject.value = lead.draft_subject || "";
        subject.placeholder = "Optional email subject";
        const subjectLabel = node("label", "campaign-editor-label", "Subject");
        subjectLabel.appendChild(subject);
        const body = document.createElement("textarea");
        body.maxLength = 3000;
        body.value = lead.draft_body || "";
        body.placeholder = "Generate a draft, then edit it here before approving or copying.";
        const bodyLabel = node("label", "campaign-editor-label", "Review and edit draft");
        bodyLabel.appendChild(body);
        card.append(stageLabel, subjectLabel, bodyLabel);
        const actions = node("div", "campaign-lead-actions", "");
        function action(label, className, handler) {
          const button = node("button", className || "", label);
          button.type = "button";
          button.addEventListener("click", handler);
          actions.appendChild(button);
        }
        async function updateDraft(statusValue) {
          try {
            const payload = {draft_subject:subject.value, draft_body:body.value, pipeline_stage:stage.value};
            if (statusValue) payload.draft_status = statusValue;
            await api("/api/campaigns/" + campaign.id + "/leads/" + lead.id, "PATCH", payload);
            showNotice(statusValue === "approved" ? "Draft marked approved. It has not been sent." : statusValue === "rejected" ? "Draft rejected." : "Draft saved for review.", false);
            await openCampaign(campaign.id);
            await loadCampaigns();
          } catch (error) { showNotice(error.message, true); }
        }
        action("Save edits", "", function(){ updateDraft(); });
        action("Approve draft", "approve-button", function(){ updateDraft("approved"); });
        action("Reject", "reject-button", function(){ updateDraft("rejected"); });
        action("Copy text", "", async function(){
          if (!body.value.trim()) { showNotice("Write or generate a draft first.", true); return; }
          try { await navigator.clipboard.writeText(body.value); showNotice("Draft copied. Review it before sending.", false); }
          catch (_) { showNotice("Copy was blocked by the browser. Select and copy the draft text manually.", true); }
        });
        action("Remove from campaign", "", async function(){
          if (!window.confirm("Remove this business from the campaign? The saved business record will remain.")) return;
          try { await api("/api/campaigns/" + campaign.id + "/leads/" + lead.id, "DELETE"); showNotice("Business removed from this campaign.", false); await openCampaign(campaign.id); await loadCampaigns(); }
          catch (error) { showNotice(error.message, true); }
        });
        card.appendChild(actions);
        list.appendChild(card);
      });
    }
    document.getElementById("campaignCreateForm").addEventListener("submit", async function(event) {
      event.preventDefault();
      const form = event.currentTarget;
      const data = Object.fromEntries(new FormData(form).entries());
      try {
        const campaign = await api("/api/campaigns", "POST", data);
        form.reset();
        showNotice("Campaign created. Search for businesses to add them.", false);
        await loadCampaigns();
        await openCampaign(campaign.id);
      } catch (error) { showNotice(error.message, true); }
    });
    document.getElementById("campaignDiscoveryForm").addEventListener("submit", async function(event) {
      event.preventDefault();
      if (!currentCampaign) return;
      const data = Object.fromEntries(new FormData(event.currentTarget).entries());
      data.radius_m = Number(data.radius_m);
      const button = event.currentTarget.querySelector("button[type=submit]");
      button.disabled = true;
      button.textContent = "Searching…";
      try {
        const result = await api("/api/campaigns/" + currentCampaign.id + "/discover", "POST", data);
        showNotice("Found " + result.found + " listings; added " + result.added_to_campaign + " to this campaign. " + result.attribution + " · " + result.license + ".", false);
        currentCampaign = result.campaign;
        renderLeads(currentCampaign);
        await loadCampaigns();
      } catch (error) { showNotice(error.message, true); }
      finally { button.disabled = false; button.textContent = "Find businesses"; }
    });
    document.getElementById("savedBusinessFilter").addEventListener("input", renderSavedBusinesses);
    document.getElementById("addSavedBusinesses").addEventListener("click", async function() {
      if (!currentCampaign) return;
      const ids = Array.from(document.getElementById("savedBusinessSelect").selectedOptions)
        .map(function(option){ return Number(option.value); }).filter(function(id){ return Number.isInteger(id) && id > 0; });
      if (!ids.length) { showNotice("Select at least one saved business.", true); return; }
      if (ids.length > 50) { showNotice("Choose up to 50 businesses at a time.", true); return; }
      try {
        currentCampaign = await api("/api/campaigns/" + currentCampaign.id + "/leads", "POST", {prospect_ids:ids});
        showNotice("Added " + ids.length + " saved business selection(s) to this campaign.", false);
        renderLeads(currentCampaign);
        await loadCampaigns();
      } catch (error) { showNotice(error.message, true); }
    });
    document.getElementById("generateDrafts").addEventListener("click", async function() {
      if (!currentCampaign) return;
      const selected = Array.from(document.querySelectorAll(".draft-select:checked")).map(function(item){ return Number(item.value); });
      if (!selected.length) { showNotice("Select at least one business without a draft.", true); return; }
      if (selected.length > 10) { showNotice("Choose up to 10 businesses per AI request.", true); return; }
      const button = document.getElementById("generateDrafts");
      button.disabled = true;
      button.textContent = "Writing drafts…";
      try {
        currentCampaign = await api("/api/campaigns/" + currentCampaign.id + "/drafts", "POST", {prospect_ids:selected});
        const localTemplates = currentCampaign.leads.some(function(lead){ return selected.includes(lead.id) && String(lead.draft_reason || "").startsWith("Local template"); });
        showNotice(localTemplates ? "Local template drafts are ready for your review. Nothing has been sent." : "AI drafts are ready for your review. Nothing has been sent.", false);
        renderLeads(currentCampaign);
        await loadCampaigns();
      } catch (error) { showNotice(error.message, true); }
      finally { button.disabled = false; button.textContent = "Generate drafts for selected (up to 10)"; }
    });
    document.getElementById("backToCampaigns").addEventListener("click", function() {
      document.getElementById("campaignWorkspace").hidden = true;
      document.getElementById("campaignListView").hidden = false;
      loadCampaigns();
    });
    renderSavedBusinesses();
    loadCampaigns();
    loadSavedBusinesses();
  </script>
</body>
</html>"""


HOME_PAGE = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Message lab · Business AI</title></head>
<body>
  <section class="home-intro">
    <div class="hero-heading">
      <p class="eyebrow"><span class="eyebrow-dot"></span>SMART WORKFLOW</p>
      <h1>Turn every enquiry into a clear next step.</h1>
      <p>Paste a customer message and let AI organise the signal: category, urgency, lead score, and a reply draft you can review.</p>
    </div>
  </section>
  <div class="home-layout">
    <form class="panel composer-panel" id="automationForm">
      <div class="panel-heading">
        <div><h2>Analyse a customer message</h2><p>Start with a message you want to understand.</p></div>
        <span class="badge category">PRIVATE INPUT</span>
      </div>
      <div class="field">
        <label class="input-label" for="email">Customer email <span class="optional-label">Optional</span></label>
        <input class="text-input" id="email" name="email" type="email" maxlength="320" placeholder="name@company.com">
      </div>
      <div class="field">
        <label class="input-label" for="message">Message <span class="optional-label">Required</span></label>
        <textarea class="text-area" id="message" name="message" maxlength="5000" required placeholder="Paste an enquiry, support request, or customer note here…"></textarea>
        <p class="field-help">Only submit messages you’re authorised to process. When an AI key is configured, the message text is sent to that provider and may incur charges; the optional email field is not sent. The app stores the message and analysis in its database.</p>
      </div>
      <div class="sample-row" aria-label="Example messages">
        <span class="sample-label">TRY A SAMPLE</span>
        <button class="sample-chip" type="button" data-example="quote">Quote request</button>
        <button class="sample-chip" type="button" data-example="support">Support issue</button>
        <button class="sample-chip" type="button" data-example="followup">Follow-up</button>
      </div>
      <div class="form-footer">
        <span class="privacy-note"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><rect x="4.2" y="8.5" width="11.6" height="8.3" rx="2"/><path d="M6.8 8.5V6.2a3.2 3.2 0 0 1 6.4 0v2.3"/></svg>Saved records require your sign-in</span>
        <button class="btn-primary" id="runButton" type="submit">Analyse message <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M4 10h11M10 5l5 5-5 5"/></svg></button>
      </div>
      <div class="result-slot" id="result" aria-live="polite"></div>
    </form>
    <aside class="workflow-panel">
      <p class="eyebrow"><span class="eyebrow-dot"></span>FROM MESSAGE TO MOMENTUM</p>
      <div class="workflow-art" aria-hidden="true">
        <svg viewBox="0 0 280 180" fill="none">
          <circle cx="140" cy="89" r="69" stroke="#AFC0D6" stroke-opacity=".28"/>
          <circle cx="140" cy="89" r="52" stroke="#AFC0D6" stroke-opacity=".18" stroke-dasharray="3 7"/>
          <path d="M29 118c33-51 61 29 94-13 26-34 51-38 77-8 17 20 29 25 52 0" stroke="#C9F27E" stroke-width="2" stroke-linecap="round"/>
          <circle cx="29" cy="118" r="5" fill="#C9F27E"/><circle cx="123" cy="105" r="5" fill="#9DE0C7"/><circle cx="252" cy="97" r="5" fill="#C9F27E"/>
          <rect x="97" y="52" width="86" height="72" rx="14" fill="#F8FAFC"/>
          <rect x="110" y="66" width="38" height="5" rx="2.5" fill="#D7E0EA"/>
          <rect x="110" y="78" width="57" height="4" rx="2" fill="#E6EBF1"/>
          <rect x="110" y="88" width="47" height="4" rx="2" fill="#E6EBF1"/>
          <rect x="110" y="102" width="48" height="12" rx="6" fill="#E8F5D9"/>
          <path d="m118 108 2.4 2.4 4.6-4.8" stroke="#5C8750" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          <rect x="206" y="35" width="42" height="34" rx="10" fill="#263F60" stroke="#637D9E" stroke-opacity=".7"/>
          <path d="M217 59V50m9 9V44m9 15v-6" stroke="#C9F27E" stroke-width="3" stroke-linecap="round"/>
        </svg>
      </div>
      <h2>Good follow-through starts with a better first read.</h2>
      <p>Keep the human in control. Review the analysis, decide what to save, and choose the next step yourself.</p>
      <ol class="workflow-steps">
        <li class="workflow-step"><span class="step-number">01</span><div><strong>Understand the message</strong><span>Category, priority, and customer intent.</span></div></li>
        <li class="workflow-step"><span class="step-number">02</span><div><strong>See the opportunity</strong><span>A lead score with a suggested response.</span></div></li>
        <li class="workflow-step"><span class="step-number">03</span><div><strong>Choose what happens next</strong><span>Track it in your dashboard and pipeline.</span></div></li>
      </ol>
    </aside>
  </div>
  <script>
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    const form = document.getElementById("automationForm");
    const messageField = document.getElementById("message");
    const resultBox = document.getElementById("result");
    const runButton = document.getElementById("runButton");
    const examples = {
      quote: "Hello, I run a growing team and would like to know more about your services and pricing. Could we arrange a call this week?",
      support: "I have tried signing in several times today, but the password reset link never arrives. Please help me regain access.",
      followup: "Thanks for sending the proposal. We are reviewing it internally and expect to make a decision by the end of next week."
    };
    document.querySelectorAll("[data-example]").forEach(function (button) {
      button.addEventListener("click", function () {
        messageField.value = examples[button.dataset.example] || "";
        messageField.focus();
      });
    });
    function escapeHtml(value) {
      const replacements = {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"};
      return String(value ?? "").replace(/[&<>"']/g, function (character) { return replacements[character]; });
    }
    form.addEventListener("submit", async function (event) {
      event.preventDefault();
      if (!messageField.value.trim()) { messageField.focus(); return; }
      runButton.disabled = true;
      runButton.innerHTML = "Analysing…";
      resultBox.innerHTML = "";
      try {
        const response = await fetch("/automate", {
          method: "POST",
          headers: {"Content-Type":"application/json","X-CSRF-Token":csrfToken},
          body: JSON.stringify({email:document.getElementById("email").value,message:messageField.value})
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "The analysis could not be completed.");
        const score = Math.max(0, Math.min(100, Number(data.lead_score) || 0));
        resultBox.innerHTML =
          '<section class="result-card"><div class="result-card-head"><div><h2>Analysis complete</h2><p>Review this suggestion before taking action.</p></div><div class="result-score">' + score + '</div></div>' +
          '<div class="result-grid"><div class="result-field"><span>Category</span><strong>' + escapeHtml(data.category) + '</strong></div>' +
          '<div class="result-field"><span>Priority</span><strong>' + escapeHtml(data.priority) + '</strong></div>' +
          '<div class="result-field"><span>Lead score</span><strong>' + score + ' / 100</strong></div></div>' +
          '<p class="result-reply">' + escapeHtml(data.ai_reply) + '</p></section>';
      } catch (error) {
        resultBox.innerHTML = '<div class="result-error" role="alert">' + escapeHtml(error.message) + '</div>';
      } finally {
        runButton.disabled = false;
        runButton.innerHTML = 'Analyse message <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M4 10h11M10 5l5 5-5 5"/></svg>';
      }
    });
  </script>
</body>
</html>"""


DASHBOARD_PAGE = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Overview · Business AI</title></head>
<body>
  <div class="page-title-row">
    <div><p class="eyebrow"><span class="eyebrow-dot"></span>YOUR BUSINESS AT A GLANCE</p><h1>Lead overview</h1><p>A quick read on new conversations, priority, and the next steps waiting for you.</p></div>
    <a class="btn" href="/export"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M10 3v9m0 0 3.5-3.5M10 12 6.5 8.5M4 14v2.5h12V14"/></svg>Download CSV</a>
  </div>
  <section class="stats-grid" aria-label="Lead statistics">
    <article class="stat-card"><div class="stat-card-top"><span class="stat-kicker">All time</span><span class="stat-icon"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M4 16V9m6 7V4m6 12v-5"/></svg></span></div><strong class="stat-value" id="totalLeads">0</strong><span class="stat-caption">Total saved enquiries</span></article>
    <article class="stat-card"><div class="stat-card-top"><span class="stat-kicker">Score 70+</span><span class="stat-icon green"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="m4 13 4-4 3 2 5-6"/><path d="M12 5h4v4"/></svg></span></div><strong class="stat-value" id="hotLeads">0</strong><span class="stat-caption">High-fit opportunities</span></article>
    <article class="stat-card"><div class="stat-card-top"><span class="stat-kicker">Open loop</span><span class="stat-icon orange"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><circle cx="10" cy="10" r="6.5"/><path d="M10 6v4l2.5 1.7"/></svg></span></div><strong class="stat-value" id="followUps">0</strong><span class="stat-caption">Follow-ups scheduled</span></article>
    <article class="stat-card"><div class="stat-card-top"><span class="stat-kicker">Needs attention</span><span class="stat-icon pink"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M10 3.5 17 16H3L10 3.5Z"/><path d="M10 7.5v4m0 2v.1"/></svg></span></div><strong class="stat-value" id="highPriority">0</strong><span class="stat-caption">High-priority messages</span></article>
  </section>
  <section class="overview-grid">
    <article class="panel mix-panel">
      <div class="donut-chart" id="priorityDonut" style="--high:0%;--medium:0%;--low:0%"><div class="donut-center"><strong id="mixTotal">0</strong><span>messages</span></div></div>
      <div class="mix-copy"><h2>Priority mix</h2><p>A visual snapshot of saved messages.</p><div class="mix-legend"><span class="legend-item"><i class="legend-dot high"></i>High <b id="highCount">0</b></span><span class="legend-item"><i class="legend-dot medium"></i>Medium <b id="mediumCount">0</b></span><span class="legend-item"><i class="legend-dot low"></i>Low <b id="lowCount">0</b></span></div></div>
    </article>
    <article class="panel score-panel">
      <div class="score-panel-header"><div><h2 class="toolbar-title">Lead score distribution</h2><p class="toolbar-subtitle">Based on the current saved record set.</p></div><span class="badge category">0–100</span></div>
      <div class="score-bars">
        <div><div class="score-bar-label"><span>Strong fit <small>(70+)</small></span><b id="strongFitCount">0</b></div><div class="score-bar-track"><span class="score-bar-fill green" id="strongFitBar"></span></div></div>
        <div><div class="score-bar-label"><span>Developing <small>(40–69)</small></span><b id="developingCount">0</b></div><div class="score-bar-track"><span class="score-bar-fill" id="developingBar"></span></div></div>
        <div><div class="score-bar-label"><span>Early stage <small>(&lt;40)</small></span><b id="earlyStageCount">0</b></div><div class="score-bar-track"><span class="score-bar-fill orange" id="earlyStageBar"></span></div></div>
      </div>
    </article>
  </section>
  <div class="toolbar">
    <div><h2 class="toolbar-title">Recent conversations</h2><p class="toolbar-subtitle">Search, review, and update your next steps.</p></div>
    <div class="toolbar-actions"><a class="btn" href="/">+ New analysis</a></div>
  </div>
  <section class="filter-bar" aria-label="Filter conversations">
    <label class="search-control"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><circle cx="8.8" cy="8.8" r="5.5"/><path d="m13 13 4 4"/></svg><input class="filter-control" id="searchBox" placeholder="Search messages, email, or replies…" oninput="applyFilters()"></label>
    <select class="filter-control" id="categoryFilter" onchange="applyFilters()"><option value="">All categories</option><option value="sales">Sales</option><option value="support">Support</option><option value="complaint">Complaint</option><option value="follow_up">Follow-up</option><option value="admin">Admin</option></select>
    <select class="filter-control" id="priorityFilter" onchange="applyFilters()"><option value="">All priorities</option><option value="low">Low priority</option><option value="medium">Medium priority</option><option value="high">High priority</option></select>
    <select class="filter-control" id="statusFilter" onchange="applyFilters()"><option value="">All statuses</option><option value="New">New</option><option value="Contacted">Contacted</option><option value="Closed">Closed</option></select>
  </section>
  <div class="quick-filters" aria-label="Quick filters">
    <button class="quick-filter active" type="button" data-quick="all">All records</button>
    <button class="quick-filter" type="button" data-quick="hot">High-fit leads</button>
    <button class="quick-filter" type="button" data-quick="followups">Follow-ups</button>
  </div>
  <div class="records-list" id="records" aria-live="polite"><div class="empty-state">Loading your records…</div></div>
  <div class="toast" id="toast" role="status" aria-live="polite"></div>
  <script>
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    const recordsBox = document.getElementById("records");
    let allData = [];
    let quickFilter = "all";
    let toastTimer;
    function escapeHtml(value) {
      const replacements = {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"};
      return String(value ?? "").replace(/[&<>"']/g, function (character) { return replacements[character]; });
    }
    function notify(message, error) {
      const toast = document.getElementById("toast");
      toast.textContent = message;
      toast.classList.toggle("error", Boolean(error));
      toast.classList.add("visible");
      window.clearTimeout(toastTimer);
      toastTimer = window.setTimeout(function () { toast.classList.remove("visible"); }, 2800);
    }
    function priority(item) {
      const value = String(item.priority || "low").toLowerCase();
      return ["high","medium","low"].includes(value) ? value : "low";
    }
    function updateOverview() {
      const total = allData.length;
      const high = allData.filter(function (item) { return priority(item) === "high"; }).length;
      const medium = allData.filter(function (item) { return priority(item) === "medium"; }).length;
      const low = total - high - medium;
      const hot = allData.filter(function (item) { return Number(item.lead_score || 0) >= 70; }).length;
      const follow = allData.filter(function (item) { return Boolean(item.follow_up_date); }).length;
      const strong = hot;
      const developing = allData.filter(function (item) { const score=Number(item.lead_score||0); return score>=40 && score<70; }).length;
      const early = total - strong - developing;
      document.getElementById("totalLeads").textContent = total;
      document.getElementById("hotLeads").textContent = hot;
      document.getElementById("followUps").textContent = follow;
      document.getElementById("highPriority").textContent = high;
      document.getElementById("mixTotal").textContent = total;
      document.getElementById("highCount").textContent = high;
      document.getElementById("mediumCount").textContent = medium;
      document.getElementById("lowCount").textContent = low;
      document.getElementById("strongFitCount").textContent = strong;
      document.getElementById("developingCount").textContent = developing;
      document.getElementById("earlyStageCount").textContent = early;
      const donut = document.getElementById("priorityDonut");
      donut.style.setProperty("--high", total ? (high / total * 100) + "%" : "0%");
      donut.style.setProperty("--medium", total ? (medium / total * 100) + "%" : "0%");
      donut.style.setProperty("--low", total ? (low / total * 100) + "%" : "0%");
      const max = Math.max(total, 1);
      document.getElementById("strongFitBar").style.width = (strong / max * 100) + "%";
      document.getElementById("developingBar").style.width = (developing / max * 100) + "%";
      document.getElementById("earlyStageBar").style.width = (early / max * 100) + "%";
    }
    async function loadHistory() {
      try {
        const response = await fetch("/history", {headers: {"Accept":"application/json"}});
        if (!response.ok) throw new Error(response.status === 401 ? "Your sign-in expired. Please sign in again." : "Could not load saved conversations.");
        const data = await response.json();
        allData = Array.isArray(data) ? data : [];
        updateOverview();
        applyFilters();
      } catch (error) {
        recordsBox.innerHTML = '<div class="empty-state"><div><strong>Records could not be loaded</strong><p>' + escapeHtml(error.message) + '</p><a class="btn" href="/login">Sign in again</a></div></div>';
      }
    }
    function displayRecords(data) {
      if (!data.length) {
        const empty = allData.length ? ["No conversations match these filters","Try a different search or clear a filter."] : ["Your workspace is ready","Run your first analysis and it will appear here."];
        recordsBox.innerHTML = '<div class="empty-state"><div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M5 5.5A2.5 2.5 0 0 1 7.5 3H19v15H7.5A2.5 2.5 0 0 0 5 20.5v-15Z"/><path d="M5 18a2.5 2.5 0 0 1 2.5-2.5H19"/></svg><strong>' + empty[0] + '</strong><p>' + empty[1] + '</p>' + (allData.length ? '' : '<a class="btn" href="/">Start an analysis</a>') + '</div></div>';
        return;
      }
      recordsBox.innerHTML = data.map(function (item) {
        const id = Number(item.id) || 0;
        const score = Math.max(0, Math.min(100, Number(item.lead_score) || 0));
        const status = ["New","Contacted","Closed"].includes(item.status) ? item.status : "New";
        const level = priority(item);
        const category = String(item.category || "other").toLowerCase();
        const email = item.customer_email || "No email supplied";
        const initials = String(email).slice(0,2);
        const message = String(item.customer_message || "");
        const preview = message.length > 145 ? message.slice(0,145) + "…" : message;
        return '<article class="record-card"><div class="record-top">' +
          '<div class="record-identity"><span class="record-avatar">' + escapeHtml(initials) + '</span><div class="record-copy"><div class="record-title">' + escapeHtml(email) + '<span class="badge category">' + escapeHtml(category.replace("_"," ")) + '</span><span class="badge priority ' + level + '">' + level + '</span></div><p class="record-preview">' + escapeHtml(preview) + '</p></div></div>' +
          '<div class="record-score"><span>Score</span><span class="score-track"><span style="width:' + score + '%"></span></span><strong>' + score + '</strong></div>' +
          '<div class="record-top-actions"><span class="badge status-badge ' + status.toLowerCase() + '">' + status + '</span><select class="inline-select" aria-label="Update status for record ' + id + '" onchange="updateStatus(' + id + ',this.value)">' +
          '<option value="New" ' + (status === "New" ? "selected" : "") + '>New</option><option value="Contacted" ' + (status === "Contacted" ? "selected" : "") + '>Contacted</option><option value="Closed" ' + (status === "Closed" ? "selected" : "") + '>Closed</option></select></div></div>' +
          '<details class="record-details"><summary>Review message and manage follow-up</summary><div class="record-detail-grid">' +
          '<div class="detail-box"><p class="detail-label">Customer message</p><p class="detail-text">' + escapeHtml(message) + '</p></div>' +
          '<div class="detail-box"><p class="detail-label">Suggested reply</p><p class="detail-text">' + escapeHtml(item.ai_reply || "No reply draft saved.") + '</p></div></div>' +
          '<div class="record-management"><div class="management-field"><label for="followup-' + id + '">Follow-up date</label><div class="management-row"><input class="text-input" type="date" id="followup-' + id + '" value="' + escapeHtml(item.follow_up_date || "") + '"><button class="btn" type="button" onclick="updateFollowUp(' + id + ')">Save date</button><button class="btn" type="button" onclick="clearFollowUp(' + id + ')">Done</button></div></div>' +
          '<div class="management-field"><label for="notes-' + id + '">Private notes</label><div class="management-row"><textarea class="notes-input" id="notes-' + id + '" placeholder="Add a note for your team…">' + escapeHtml(item.notes || "") + '</textarea><button class="btn" type="button" onclick="updateNotes(' + id + ')">Save note</button></div></div>' +
          '<div><button class="btn btn-danger" type="button" onclick="deleteRecord(' + id + ')">Delete record</button></div></div></details></article>';
      }).join("");
    }
    function applyFilters() {
      const search = document.getElementById("searchBox").value.toLowerCase().trim();
      const category = document.getElementById("categoryFilter").value;
      const priorityFilter = document.getElementById("priorityFilter").value;
      const statusFilter = document.getElementById("statusFilter").value;
      const filtered = allData.filter(function (item) {
        const searchable = [item.customer_message,item.customer_email,item.ai_reply,item.notes].join(" ").toLowerCase();
        const textMatch = searchable.includes(search);
        const categoryMatch = !category || String(item.category || "").toLowerCase() === category;
        const priorityMatch = !priorityFilter || priority(item) === priorityFilter;
        const statusMatch = !statusFilter || (item.status || "New") === statusFilter;
        const quickMatch = quickFilter === "all" || (quickFilter === "hot" && Number(item.lead_score || 0) >= 70) || (quickFilter === "followups" && Boolean(item.follow_up_date));
        return textMatch && categoryMatch && priorityMatch && statusMatch && quickMatch;
      });
      displayRecords(filtered);
    }
    document.querySelectorAll("[data-quick]").forEach(function (button) {
      button.addEventListener("click", function () {
        quickFilter = button.dataset.quick;
        document.querySelectorAll("[data-quick]").forEach(function (item) { item.classList.toggle("active", item === button); });
        applyFilters();
      });
    });
    async function saveChange(url, method, successText) {
      try {
        const response = await fetch(url, {method:method,headers:{"X-CSRF-Token":csrfToken}});
        if (!response.ok) throw new Error("The change could not be saved.");
        notify(successText);
        await loadHistory();
      } catch (error) { notify(error.message, true); }
    }
    function updateStatus(id, status) {
      saveChange("/history/" + id + "/status?new_status=" + encodeURIComponent(status), "PUT", "Status updated.");
    }
    function updateNotes(id) {
      const notes = document.getElementById("notes-" + id).value;
      saveChange("/history/" + id + "/notes?notes=" + encodeURIComponent(notes), "PUT", "Note saved.");
    }
    function updateFollowUp(id) {
      const date = document.getElementById("followup-" + id).value;
      saveChange("/history/" + id + "/follow-up?follow_up_date=" + encodeURIComponent(date), "PUT", "Follow-up saved.");
    }
    function clearFollowUp(id) {
      saveChange("/history/" + id + "/follow-up?follow_up_date=", "PUT", "Follow-up marked done.");
    }
    async function deleteRecord(id) {
      if (!window.confirm("Delete this record? This cannot be undone.")) return;
      await saveChange("/history/" + id, "DELETE", "Record deleted.");
    }
    loadHistory();
  </script>
</body>
</html>"""


PIPELINE_PAGE = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Pipeline · Business AI</title></head>
<body>
  <div class="page-title-row">
    <div><p class="eyebrow"><span class="eyebrow-dot"></span>KEEP THE NEXT STEP MOVING</p><h1>Pipeline</h1><p>Move each conversation forward when you’re ready. Nothing is sent automatically.</p></div>
    <a class="btn" href="/"><span aria-hidden="true">+</span> New analysis</a>
  </div>
  <section class="pipeline-board" aria-label="Lead pipeline">
    <article class="pipeline-column"><header class="column-header"><div class="column-title"><span class="column-dot"></span>New</div><span class="column-count" id="newCount">0</span></header><div class="column-list" id="newCol"><div class="pipeline-empty">Loading…</div></div></article>
    <article class="pipeline-column"><header class="column-header"><div class="column-title"><span class="column-dot contacted"></span>Contacted</div><span class="column-count" id="contactedCount">0</span></header><div class="column-list" id="contactedCol"></div></article>
    <article class="pipeline-column"><header class="column-header"><div class="column-title"><span class="column-dot closed"></span>Closed</div><span class="column-count" id="closedCount">0</span></header><div class="column-list" id="closedCol"></div></article>
  </section>
  <div class="toast" id="toast" role="status" aria-live="polite"></div>
  <script>
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    let allData = [];
    let toastTimer;
    function escapeHtml(value) {
      const replacements = {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"};
      return String(value ?? "").replace(/[&<>"']/g, function (character) { return replacements[character]; });
    }
    function notify(message, error) {
      const toast = document.getElementById("toast");
      toast.textContent = message;
      toast.classList.toggle("error", Boolean(error));
      toast.classList.add("visible");
      window.clearTimeout(toastTimer);
      toastTimer = window.setTimeout(function () { toast.classList.remove("visible"); }, 2600);
    }
    async function loadPipeline() {
      try {
        const response = await fetch("/history");
        if (!response.ok) throw new Error("Could not load the pipeline.");
        const data = await response.json();
        allData = Array.isArray(data) ? data : [];
        render("New", "newCol", "newCount");
        render("Contacted", "contactedCol", "contactedCount");
        render("Closed", "closedCol", "closedCount");
      } catch (error) {
        document.getElementById("newCol").innerHTML = '<div class="pipeline-empty">' + escapeHtml(error.message) + '</div>';
      }
    }
    function render(status, elementId, countId) {
      const items = allData.filter(function (item) { return (item.status || "New") === status; });
      document.getElementById(countId).textContent = items.length;
      const column = document.getElementById(elementId);
      if (!items.length) { column.innerHTML = '<div class="pipeline-empty">Nothing here yet</div>'; return; }
      column.innerHTML = items.map(function (item) {
        const score = Math.max(0, Math.min(100, Number(item.lead_score) || 0));
        const level = ["high","medium","low"].includes(String(item.priority||"low").toLowerCase()) ? String(item.priority||"low").toLowerCase() : "low";
        const currentStatus = ["New","Contacted","Closed"].includes(item.status) ? item.status : "New";
        const email = item.customer_email || "No email supplied";
        return '<article class="pipeline-card"><div class="pipeline-card-top"><strong class="pipeline-email">' + escapeHtml(email) + '</strong><span class="pipeline-score">' + score + ' / 100</span></div>' +
          '<p class="pipeline-message">' + escapeHtml(item.customer_message || "") + '</p><div class="pipeline-meta"><span class="badge category">' + escapeHtml(String(item.category||"other").replace("_"," ")) + '</span><span class="badge priority ' + level + '">' + level + ' priority</span></div>' +
          '<div class="score-track" style="width:100%;height:4px;margin:0 0 11px"><span style="width:' + score + '%"></span></div>' +
          '<select class="pipeline-select" aria-label="Move record to another stage" onchange="updateStatus(' + Number(item.id) + ',this.value)"><option value="New" ' + (currentStatus==="New"?"selected":"") + '>Move to: New</option><option value="Contacted" ' + (currentStatus==="Contacted"?"selected":"") + '>Move to: Contacted</option><option value="Closed" ' + (currentStatus==="Closed"?"selected":"") + '>Move to: Closed</option></select></article>';
      }).join("");
    }
    async function updateStatus(id, status) {
      try {
        const response = await fetch("/history/" + id + "/status?new_status=" + encodeURIComponent(status), {method:"PUT",headers:{"X-CSRF-Token":csrfToken}});
        if (!response.ok) throw new Error("The status could not be updated.");
        notify("Pipeline updated.");
        await loadPipeline();
      } catch (error) { notify(error.message, true); }
    }
    loadPipeline();
  </script>
</body>
</html>"""


def build_public_retrofit_page(csrf_token: str, enabled: bool, controller: str = "",
                               privacy_url: str = "", message: str = "",
                               retention_days: int = 0, close_date: str = ""):
    """Render the consent-based, minimal-data public heat-pump enquiry page."""
    safe_controller = escape(controller)
    safe_privacy = escape(privacy_url, quote=True)
    pilot_note = (
        f'<div class="pilot-note">Pilot requests are accepted until {escape(close_date)} and kept for up to '
        f'{int(retention_days)} days.</div>'
    ) if close_date and retention_days else ""
    alert = f'<div class="alert" role="alert">{escape(message)}</div>' if message else ""
    if not enabled:
        content = """<section class="closed-card"><span class="eyebrow">PILOT IN PREPARATION</span>
          <h1>Home energy enquiries are getting ready.</h1>
          <p>This enquiry form is not accepting submissions yet. Please check back later.</p>
          <div class="trust"><span>Private by design</span><span>No unsolicited marketing</span></div>
        </section>"""
    else:
        content = f"""<section class="hero">
          <span class="eyebrow">A CLEARER NEXT STEP FOR YOUR HOME</span>
          <h1>Explore whether a heat pump could suit your home.</h1>
          <p>Share a few details and we’ll review your request. If you choose to be introduced, we’ll first select one installer for you to consider. This is not a grant eligibility check or a quote.</p>
          {pilot_note}
        </section>
        {alert}
        <form class="form-card" method="post" action="/retrofit/enquiries" id="enquiryForm">
          <input type="hidden" name="csrf_token" value="{escape(csrf_token, quote=True)}">
          <div class="field-grid">
            <label>Your name<input name="full_name" autocomplete="name" maxlength="120" required></label>
            <label>Email address <span class="optional">(optional if you give a phone number)</span><input name="email" type="email" autocomplete="email" maxlength="320"></label>
            <label>Phone number <span class="optional">(optional if you give an email)</span><input name="phone" type="tel" autocomplete="tel" maxlength="40"></label>
            <label>Home postcode<input name="postcode" autocomplete="postal-code" maxlength="16" placeholder="e.g. B1 1AA" required></label>
            <label>Property type<select name="property_type" required><option value="">Choose one</option><option>House</option><option>Bungalow</option><option>Flat</option><option>Other</option><option>Not sure</option></select></label>
            <label>Current heating<select name="heating_type" required><option value="">Choose one</option><option>Gas</option><option>Oil</option><option>Electric</option><option>LPG</option><option>Solid fuel</option><option>Other</option><option>Not sure</option></select></label>
            <label>Your relationship to the property<select name="ownership" required><option value="">Choose one</option><option>Owner occupier</option><option>Landlord</option><option>Buying the property</option><option>Other</option></select></label>
            <label>When are you considering a change?<select name="timeframe" required><option value="">Choose one</option><option>Just exploring</option><option>Within 3 months</option><option>3 to 6 months</option><option>More than 6 months</option></select></label>
          </div>
          <label class="consent"><input type="checkbox" name="consent_contact" value="true" required><span>I agree that {safe_controller} may use these details to respond to this heat-pump enquiry. I understand this is not a marketing subscription.</span></label>
          <label class="consent"><input type="checkbox" name="consent_share" value="true"><span>I’m happy for my relevant details to be shared with one installer selected for my area, so they can contact me about this request. This is optional and can be changed by contacting {safe_controller}.</span></label>
          <div class="form-foot"><span>We collect only the details needed to review your request. <a href="{safe_privacy}" target="_blank" rel="noopener noreferrer">Read the privacy notice</a>.</span><button type="submit">Send enquiry <b aria-hidden="true">→</b></button></div>
          <p class="controller">Data controller: {safe_controller}. No automatic installer sharing; each match is reviewed by a person.</p>
          <input class="trap" type="text" name="company" tabindex="-1" autocomplete="off" aria-hidden="true">
        </form>"""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#14243b"><title>Home energy enquiry</title>
<style>
:root{{--ink:#17243b;--muted:#718096;--line:#e5eaf1;--lime:#c9f27e;--blue:#6678df;--canvas:#f4f6fa}}*{{box-sizing:border-box}}body{{margin:0;min-height:100vh;color:var(--ink);background:radial-gradient(circle at 80% 0,#e8efd9,transparent 30%),var(--canvas);font:15px/1.6 Inter,"Segoe UI Variable",Aptos,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}.wrap{{width:min(100% - 36px,820px);margin:0 auto;padding:45px 0 70px}}.brand{{display:flex;align-items:center;gap:10px;margin-bottom:45px;font-size:11px;font-weight:800;letter-spacing:.12em}}.mark{{display:grid;width:34px;height:34px;place-items:center;border-radius:11px;background:linear-gradient(145deg,#d7f79b,#9ee0c7)}}.eyebrow{{color:#6f8299;font-size:10px;font-weight:800;letter-spacing:.15em}}h1{{max-width:700px;margin:12px 0;color:var(--ink);font-size:clamp(32px,6vw,52px);letter-spacing:-.055em;line-height:1.08}}.hero p,.closed-card p{{max-width:650px;color:var(--muted);font-size:15px}}.form-card,.closed-card{{margin-top:28px;padding:clamp(20px,4vw,34px);border:1px solid var(--line);border-radius:20px;background:#fff;box-shadow:0 20px 55px #1c2d4610}}.field-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:17px}}.field-grid label{{display:grid;gap:7px;color:#47566d;font-size:12px;font-weight:700}}input:not([type=checkbox]),select{{width:100%;height:46px;padding:0 12px;border:1px solid #dfe6ef;border-radius:10px;color:var(--ink);background:#fbfcfe;font:inherit}}input:focus,select:focus{{outline:3px solid #6678df33;border-color:#98a3ed}}.optional{{color:#8a97a8;font-size:10px;font-weight:500}}.pilot-note{{display:inline-block;margin:4px 0 0;padding:8px 11px;border:1px solid #e4eada;border-radius:9px;color:#61745d;background:#f7fbf2;font-size:10px}}.consent{{display:flex;align-items:flex-start;gap:10px;margin:19px 0;color:#5d6c81;font-size:11px;line-height:1.6}}.consent input{{flex:0 0 auto;width:17px;height:17px;margin-top:1px;accent-color:#638b4e}}.form-foot{{display:flex;align-items:center;justify-content:space-between;gap:15px;margin-top:21px;padding-top:19px;border-top:1px solid #edf0f4;color:#7b8798;font-size:10px}}.form-foot a{{color:#5368ca;text-decoration:underline;text-underline-offset:3px}}button{{min-height:46px;padding:0 18px;border:0;border-radius:11px;color:#1c2c42;background:var(--lime);font:700 12px inherit;cursor:pointer}}button:hover{{background:#d5f69b}}button b{{margin-left:10px;font-size:16px}}.controller{{margin:16px 0 0;color:#97a1af;font-size:9px}}.trust{{display:flex;gap:10px;margin-top:25px;color:#66758b;font-size:10px}}.trust span{{padding:8px 11px;border:1px solid var(--line);border-radius:99px;background:#fff}}.alert{{margin-top:16px;padding:12px 14px;border:1px solid #f0d0cb;border-radius:10px;color:#984a43;background:#fff6f4;font-size:12px}}.trap{{position:absolute!important;left:-10000px!important;width:1px!important;height:1px!important;opacity:0!important}}@media(max-width:620px){{.wrap{{padding-top:28px}}.brand{{margin-bottom:30px}}.field-grid{{grid-template-columns:1fr}}.form-foot{{align-items:stretch;flex-direction:column}}.form-foot button{{width:100%}}}}
</style></head><body><main class="wrap"><div class="brand"><span class="mark" aria-hidden="true">✦</span><span>HOME ENERGY ENQUIRIES</span></div>{content}</main>
<script>const f=document.getElementById('enquiryForm');if(f)f.addEventListener('submit',function(e){{const email=f.elements.email.value.trim(),phone=f.elements.phone.value.trim();if(!email&&!phone){{e.preventDefault();f.elements.email.setCustomValidity('Add an email address or phone number.');f.elements.email.reportValidity();}}else{{f.elements.email.setCustomValidity('');}}}});</script></body></html>"""


def build_retrofit_thanks_page(controller: str, contact_email: str):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#14243b"><title>Enquiry received</title><style>body{{margin:0;min-height:100vh;display:grid;place-items:center;background:#f4f6fa;color:#17243b;font:15px/1.6 Inter,"Segoe UI",sans-serif}}main{{width:min(100% - 36px,620px);padding:clamp(24px,5vw,42px);border:1px solid #e5eaf1;border-radius:20px;background:white;box-shadow:0 20px 55px #1c2d4610}}.mark{{color:#5d8551;font-size:28px}}h1{{margin:12px 0 8px;font-size:34px;letter-spacing:-.04em}}p{{color:#718096}}a{{color:#5368ca}}</style></head><body><main><span class="mark" aria-hidden="true">✓</span><h1>Thanks, we’ve received your request.</h1><p>{escape(controller)} will review it. If you agreed to an installer introduction, your details will only be shared after a person reviews a potential match.</p><p>Questions? Contact <a href="mailto:{escape(contact_email, quote=True)}">{escape(contact_email)}</a>.</p></main></body></html>"""


def build_public_privacy_page(controller: str, contact_email: str, retention_days: int,
                              close_date: str = ""):
    if not controller or not contact_email or not 1 <= retention_days <= 365:
        return """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Privacy notice</title></head><body><main><h1>Privacy notice</h1><p>The enquiry pilot is not accepting requests while its privacy settings are being prepared.</p></main></body></html>"""
    safe_controller = escape(controller)
    safe_email = escape(contact_email)
    safe_mailto = escape(contact_email, quote=True)
    safe_close = escape(close_date)
    close_note = (
        f"The current pilot is scheduled to pause on {safe_close}. We will not accept new requests after that date unless the pilot is extended."
        if safe_close else ""
    )
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#14243b"><meta name="robots" content="noindex,nofollow"><title>Privacy notice · Home Energy Enquiries</title><style>
:root{{--ink:#17243b;--muted:#718096;--line:#e5eaf1;--canvas:#f4f6fa;--lime:#c9f27e}}*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 85% 0,#e8efd9,transparent 28%),var(--canvas);color:var(--ink);font:14px/1.7 Inter,"Segoe UI Variable",Aptos,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}main{{width:min(100% - 36px,900px);margin:0 auto;padding:42px 0 70px}}.brand{{display:flex;align-items:center;gap:10px;margin-bottom:32px;font-size:10px;font-weight:800;letter-spacing:.13em}}.mark{{display:grid;width:34px;height:34px;place-items:center;border-radius:11px;background:linear-gradient(145deg,#d7f79b,#9ee0c7)}}article{{padding:clamp(22px,5vw,44px);border:1px solid var(--line);border-radius:20px;background:#fff;box-shadow:0 20px 55px #1c2d4610}}.eyebrow{{color:#73849a;font-size:9px;font-weight:800;letter-spacing:.15em;text-transform:uppercase}}h1{{margin:8px 0 8px;font-size:clamp(29px,5vw,40px);letter-spacing:-.05em;line-height:1.12}}.intro{{max-width:700px;margin:0 0 28px;color:var(--muted)}}h2{{margin:25px 0 5px;font-size:15px;letter-spacing:-.015em}}p,li{{color:#5d6c81;font-size:12px}}ul{{padding-left:20px}}a{{color:#5368ca;text-underline-offset:3px}}.contact{{padding:14px 16px;border:1px solid #e5eadf;border-radius:11px;background:#f7fbf2}}.contact a{{font-weight:700}}.updated{{margin-top:28px;padding-top:15px;border-top:1px solid #edf0f4;color:#93a0ae;font-size:9px}}
</style></head><body><main><div class="brand"><span class="mark" aria-hidden="true">✦</span><span>HOME ENERGY ENQUIRIES</span></div><article><p class="eyebrow">Privacy notice</p><h1>How we handle your enquiry</h1><p class="intro">This notice explains how {safe_controller} uses information submitted through the UK heat-pump enquiry form. The form is for responding to a request, not for marketing or deciding grant eligibility.</p>
<h2>Who is responsible</h2><p>{safe_controller} is the data controller for this enquiry service. You can contact us at <a href="mailto:{safe_mailto}">{safe_email}</a>.</p>
<h2>What we collect</h2><p>If you submit the form, we collect your name, email address and/or phone number, home postcode, property type, current heating type, relationship to the property, preferred timing, your consent choices, and the date of those choices. We do not ask for your full address.</p>
<h2>Why we use it</h2><p>We use the information to review your heat-pump request and contact you about it, based on the required contact permission you provide on the form. A separate optional checkbox lets you agree to an introduction: if selected, we may share relevant details with one installer chosen after a person reviews the postcode and request. You can withdraw consent by contacting us. This does not affect processing that happened before withdrawal.</p><p>We do not send marketing, make automated decisions, or determine whether you qualify for a grant.</p>
<h2>Who may receive it</h2><p>The service is hosted by Render Services, Inc. and its authorised subprocessors. The app and database are in Render’s Oregon, USA region, so information is processed in the United States. Render’s <a href="https://render.com/dpa" target="_blank" rel="noopener noreferrer">Data Processing Addendum</a> describes its processing terms and international-transfer provisions, including the UK Addendum to the standard contractual clauses. If you separately agree to an installer introduction, the selected installer may receive the relevant details and will handle them under its own privacy notice.</p>
<h2>How long we keep it</h2><p>We keep an enquiry for up to {int(retention_days)} days after submission, then delete it from our application database. We may delete it sooner if you withdraw consent or ask us to erase it. If you agree to an installer introduction, that installer’s copy is subject to its own retention policy.</p>{f'<p>{close_note}</p>' if close_note else ''}
<h2>Cookies and security</h2><p>The public form uses one short-lived, essential security cookie to protect submissions against cross-site request forgery. It expires after one hour. The form does not use advertising or analytics cookies. Access to saved enquiries is restricted to the signed-in app owner.</p>
<h2>Your choices and rights</h2><p>You can contact us to ask about your information, correct it, withdraw consent, or request deletion. Depending on the circumstances, you may also have rights to access, restrict, object to, or obtain a copy of personal data. You can complain to the <a href="https://ico.org.uk/make-a-complaint/" target="_blank" rel="noopener noreferrer">Information Commissioner’s Office</a>.</p>
<p class="contact">Privacy requests: <a href="mailto:{safe_mailto}">{safe_email}</a></p><p class="updated">This notice applies to the homeowner retrofit enquiry form.</p></article></main></body></html>"""


RETROFIT_INQUIRIES_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Retrofit enquiries</title></head><body>
<section class="page-title-row"><div><p class="eyebrow"><span class="eyebrow-dot"></span>HOME ENERGY PILOT</p><h1>Enquiry review</h1><p>Review requests privately, check consent, and choose an installer manually. No homeowner details are sent to an installer by this screen.</p></div><div class="toolbar-actions"><a class="btn" href="/retrofit" target="_blank" rel="noopener noreferrer">Preview public form</a><button class="btn" id="refreshButton" type="button">Refresh</button></div></section>
<div class="panel" style="padding:18px 20px;margin-bottom:16px"><strong>Before matching</strong><p style="margin:5px 0 0;color:#718096;font-size:11px">Check the postcode and installer service area, then confirm the installer’s current credentials and availability. Only assign an installer when the sharing checkbox is approved.</p></div>
<div id="inquiries" style="display:grid;gap:13px"><div class="panel" style="padding:24px;color:#718096">Loading enquiries…</div></div><div class="toast" id="toast" role="status" aria-live="polite"></div>
<script>
const csrfToken=document.querySelector('meta[name="csrf-token"]').content;let installerRows=[];let timer;
function esc(v){return String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
function notify(m,error){const t=document.getElementById('toast');t.textContent=m;t.classList.toggle('error',!!error);t.classList.add('visible');clearTimeout(timer);timer=setTimeout(()=>t.classList.remove('visible'),2600);}
async function load(){const target=document.getElementById('inquiries');target.innerHTML='<div class="panel" style="padding:24px;color:#718096">Loading enquiries…</div>';try{const rs=await Promise.all([fetch('/api/retrofit/inquiries'),fetch('/api/retrofit/installers')]);if(rs.some(r=>!r.ok))throw new Error('Could not load the enquiry list.');const items=await rs[0].json();installerRows=await rs[1].json();if(!items.length){target.innerHTML='<div class="panel" style="padding:30px;color:#718096">No homeowner enquiries yet.</div>';return;}target.innerHTML=items.map(item=>{const opts=['new','reviewing','qualified','matched','contacted','survey_booked','closed'].map(s=>'<option value="'+s+'" '+(item.status===s?'selected':'')+'>'+s.replaceAll('_',' ')+'</option>').join('');const installerOptions='<option value="">No installer selected</option>'+installerRows.map(x=>'<option value="'+Number(x.id)+'" '+(Number(item.matched_installer_id)===Number(x.id)?'selected':'')+'>'+esc(x.business_name)+' · '+esc([x.city,x.region].filter(Boolean).join(', ')||'area to confirm')+'</option>').join('');return '<article class="panel inquiry-card" data-id="'+Number(item.id)+'"><div class="inquiry-head"><div><span class="badge category">REQUEST #'+Number(item.id)+'</span><h2>'+esc(item.full_name)+'</h2><p>'+esc(item.postcode)+' · '+esc(item.property_type)+' · '+esc(item.heating_type)+'</p></div><span class="badge priority medium">'+esc(item.status.replaceAll('_',' '))+'</span></div><div class="inquiry-facts"><span><b>Contact</b>'+esc([item.email,item.phone].filter(Boolean).join(' · ')||'None supplied')+'</span><span><b>Ownership</b>'+esc(item.ownership)+'</span><span><b>Timing</b>'+esc(item.timeframe)+'</span><span><b>Received</b>'+esc(item.created_at)+'</span></div><p class="consent-state">Contact permission: <strong>'+ (item.consent_contact?'Yes':'No')+'</strong> · Installer sharing: <strong>'+ (item.consent_share?'Approved':'Not approved')+'</strong></p><div class="inquiry-controls"><label>Status<select class="inline-select status">'+opts+'</select></label><label>Manual installer match<select class="inline-select installer">'+installerOptions+'</select></label><button class="btn btn-primary save" type="button">Save review</button><button class="btn delete" type="button">Erase request</button></div></article>';}).join('');target.querySelectorAll('.save').forEach(b=>b.addEventListener('click',save));target.querySelectorAll('.delete').forEach(b=>b.addEventListener('click',erase));}catch(e){target.innerHTML='<div class="panel" style="padding:24px;color:#984a43">'+esc(e.message)+'</div>';}}
async function save(e){const card=e.currentTarget.closest('[data-id]');const id=Number(card.dataset.id);const installer=card.querySelector('.installer').value;const payload={status:card.querySelector('.status').value,matched_installer_id:installer?Number(installer):null};try{const r=await fetch('/api/retrofit/inquiries/'+id,{method:'PATCH',headers:{'Content-Type':'application/json','X-CSRF-Token':csrfToken},body:JSON.stringify(payload)});if(!r.ok){const d=await r.json().catch(()=>({}));throw new Error(d.detail||'The review could not be saved.');}notify('Review saved.');await load();}catch(err){notify(err.message,true);}}
async function erase(e){const card=e.currentTarget.closest('[data-id]');if(!window.confirm('Permanently erase this homeowner request?'))return;try{const r=await fetch('/api/retrofit/inquiries/'+Number(card.dataset.id),{method:'DELETE',headers:{'X-CSRF-Token':csrfToken}});if(!r.ok)throw new Error('The request could not be erased.');notify('Request erased.');await load();}catch(err){notify(err.message,true);}}
document.getElementById('refreshButton').addEventListener('click',load);load();
</script><style>.inquiry-card{padding:20px}.inquiry-head{display:flex;justify-content:space-between;gap:14px}.inquiry-head h2{margin:10px 0 2px;font-size:17px}.inquiry-head p{margin:0;color:#718096;font-size:11px}.inquiry-facts{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:18px 0}.inquiry-facts span{padding:11px;border-radius:10px;background:#f8f9fc;color:#59687d;font-size:10px;overflow-wrap:anywhere}.inquiry-facts b{display:block;margin-bottom:3px;color:#91a0b2;font-size:8px;text-transform:uppercase;letter-spacing:.08em}.consent-state{color:#65748b;font-size:10px}.inquiry-controls{display:grid;grid-template-columns:1fr 1.5fr auto auto;align-items:end;gap:9px;margin-top:14px}.inquiry-controls label{display:grid;gap:5px;color:#66758b;font-size:9px}.inquiry-controls .btn-primary{min-height:40px}.inquiry-controls .delete{min-height:40px;color:#994e48}.toast{position:fixed;right:22px;bottom:22px;padding:11px 15px;border-radius:10px;color:white;background:#213652;font-size:11px;opacity:0;transform:translateY(8px);transition:.18s;pointer-events:none}.toast.visible{opacity:1;transform:none}.toast.error{background:#984a43}@media(max-width:760px){.inquiry-facts{grid-template-columns:repeat(2,minmax(0,1fr))}.inquiry-controls{grid-template-columns:1fr 1fr}.inquiry-controls button{width:100%}}
</style></body></html>"""

