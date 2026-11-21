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
.stat-value { display: block; margin-top: 11px; color: var(--ink); font-size: 27px; font-weight: 700; letter-spacing: -.05em; line-height: 1; }
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
}


def build_protected_page(markup: str, path: str, csrf_token: str):
    page_names = {"/": "New analysis", "/dashboard": "Overview", "/pipeline": "Pipeline"}
    page_name = page_names.get(path, "Workspace")
    nav = []
    for href, label in (("/", "Message lab"), ("/dashboard", "Overview"), ("/pipeline", "Pipeline")):
        active = " active" if href == path else ""
        current = ' aria-current="page"' if href == path else ""
        nav.append(
            f'<a class="nav-link{active}" href="{href}"{current} aria-label="{escape(label, quote=True)}">'
            f'<span class="nav-icon">{NAV_ICONS[href]}</span><span class="nav-label">{label}</span></a>'
        )
    csrf_meta = f'<meta name="csrf-token" content="{escape(csrf_token, quote=True)}">'
    markup = markup.replace("<head>", "<head>\n" + csrf_meta, 1)
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
    <p class="sidebar-footnote">Single-owner workspace · Local data</p>
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
        <p class="field-help">Only submit messages you’re authorised to process. The app keeps records in its configured database.</p>
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


