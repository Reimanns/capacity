import json
from datetime import date
from copy import deepcopy

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

st.set_page_config(layout="wide", page_title="Labor Capacity Dashboard")
try:
    st.image("citadel_logo.png", width=200)
except Exception:
    pass

# --------------------- DEFAULT DATA (YOUR SET) ---------------------
DEFAULT_PROJECTS = [
    {"number":"P7657","customer":"Kaiser","aircraftModel":"B737","scope":"Starlink","induction":"2025-11-15T00:00:00","delivery":"2025-11-25T00:00:00","Maintenance":93.57,"Structures":240.61,"Avionics":294.07,"Inspection":120.3,"Interiors":494.58,"Engineering":80.2,"Cabinet":0,"Upholstery":0,"Finish":13.37},
    {"number":"P7611","customer":"Alpha Star","aircraftModel":None,"scope":None,"induction":"2025-10-20T00:00:00","delivery":"2025-12-04T00:00:00","Maintenance":2432.23,"Structures":1252.97,"Avionics":737.04,"Inspection":1474.08,"Interiors":1474.08,"Engineering":0.0,"Cabinet":0,"Upholstery":0,"Finish":0.0},
    {"number":"P7645","customer":"Kaiser","aircraftModel":"B737","scope":"Starlink","induction":"2025-11-30T00:00:00","delivery":"2025-12-10T00:00:00","Maintenance":93.57,"Structures":240.61,"Avionics":294.07,"Inspection":120.3,"Interiors":494.58,"Engineering":80.2,"Cabinet":0,"Upholstery":0,"Finish":13.37},
    {"number":"P7426","customer":"Celestial","aircraftModel":"B757","scope":"Post Maintenance Discrepancies","induction":"2026-01-05T00:00:00","delivery":"2026-01-15T00:00:00","Maintenance":0.0,"Structures":0.0,"Avionics":0.0,"Inspection":0.0,"Interiors":0.0,"Engineering":0.0,"Cabinet":0,"Upholstery":0,"Finish":0.0},
    {"number":"P7548","customer":"Ty Air","aircraftModel":"B737","scope":"CMS Issues","induction":"2025-10-20T00:00:00","delivery":"2025-10-30T00:00:00","Maintenance":0.0,"Structures":0.0,"Avionics":0.0,"Inspection":0.0,"Interiors":0.0,"Engineering":0.0,"Cabinet":0,"Upholstery":0,"Finish":0.0},
    {"number":"P7706","customer":"Valkyrie","aircraftModel":"B737-MAX","scope":"Starlink, Mods","induction":"2025-10-31T00:00:00","delivery":"2025-12-09T00:00:00","Maintenance":102.75,"Structures":328.8,"Avionics":411.0,"Inspection":164.4,"Interiors":945.3,"Engineering":82.2,"Cabinet":0,"Upholstery":0,"Finish":20.55},
    {"number":"P7685","customer":"Sands","aircraftModel":"B737-700","scope":"Starlink","induction":"2025-11-03T00:00:00","delivery":"2025-11-17T00:00:00","Maintenance":105.44,"Structures":224.06,"Avionics":303.14,"Inspection":118.62,"Interiors":474.48,"Engineering":79.08,"Cabinet":0,"Upholstery":0,"Finish":13.18},
]
DEFAULT_POTENTIAL = [
    {"number":"P7661","customer":"Sands","aircraftModel":"A340-500","scope":"C Check","induction":"2026-01-29T00:00:00","delivery":"2026-02-28T00:00:00","Maintenance":2629.44,"Structures":1709.14,"Avionics":723.1,"Inspection":1248.98,"Interiors":262.94,"Engineering":0,"Cabinet":0,"Upholstery":0,"Finish":0},
    {"number":"P7669","customer":"Sands","aircraftModel":"A319-133","scope":"C Check","induction":"2025-12-08T00:00:00","delivery":"2026-01-28T00:00:00","Maintenance":2029.67,"Structures":984.08,"Avionics":535.55,"Inspection":675.56,"Interiors":1906.66,"Engineering":0,"Cabinet":0,"Upholstery":0,"Finish":0},
    {"number":None,"customer":"Sands","aircraftModel":"B767-300","scope":"C Check","induction":"2026-09-15T00:00:00","delivery":"2026-12-04T00:00:00","Maintenance":0.0,"Structures":0.0,"Avionics":0.0,"Inspection":0.0,"Interiors":0.0,"Engineering":0,"Cabinet":0,"Upholstery":0,"Finish":0},
    {"number":"P7686","customer":"Polaris","aircraftModel":"B777","scope":"1A & 3A Mx Checks","induction":"2025-12-01T00:00:00","delivery":"2025-12-09T00:00:00","Maintenance":643.15,"Structures":287.36,"Avionics":150.52,"Inspection":177.89,"Interiors":109.47,"Engineering":0,"Cabinet":0,"Upholstery":0,"Finish":0},
    {"number":"P7430","customer":"Turkmen","aircraftModel":"B777","scope":"Maint/Recon/Refub","induction":"2025-11-10T00:00:00","delivery":"2026-07-13T00:00:00","Maintenance":12720.0,"Structures":12720.0,"Avionics":3180.0,"Inspection":3180.0,"Interiors":19080.0,"Engineering":3180,"Cabinet":3180,"Upholstery":3180,"Finish":3180},
    {"number":"P7649","customer":"NEP","aircraftModel":"B767-300","scope":"Refurb","induction":"2026-02-02T00:00:00","delivery":"2026-07-13T00:00:00","Maintenance":2000.0,"Structures":2400.0,"Avionics":2800.0,"Inspection":800.0,"Interiors":4400.0,"Engineering":1800,"Cabinet":1600,"Upholstery":1200,"Finish":3000},
    {"number":"P7689","customer":"Sands","aircraftModel":"B737-700","scope":"C1,C3,C6C7 Mx","induction":"2025-09-10T00:00:00","delivery":"2026-11-07T00:00:00","Maintenance":8097.77,"Structures":1124.69,"Avionics":899.75,"Inspection":787.28,"Interiors":337.14,"Engineering":0,"Cabinet":0,"Upholstery":0,"Finish":0},
    {"number":"P7690","customer":"Sands","aircraftModel":None,"scope":"C1,C2,C7 Mx","induction":"2025-05-25T00:00:00","delivery":"2025-07-22T00:00:00","Maintenance":3227.14,"Structures":2189.85,"Avionics":922.04,"Inspection":1152.55,"Interiors":4033.92,"Engineering":0,"Cabinet":0,"Upholstery":0,"Finish":0},
    {"number":"P7691","customer":"Sands","aircraftModel":"B737-700","scope":"C1,C2,C3,C7 Mx","induction":"2026-10-13T00:00:00","delivery":"2026-12-22T00:00:00","Maintenance":4038.3,"Structures":5115.18,"Avionics":1076.88,"Inspection":1346.1,"Interiors":1884.54,"Engineering":0,"Cabinet":0,"Upholstery":0,"Finish":0},
]
DEFAULT_ACTUAL = []
DEFAULT_DEPTS = [
    {"name":"Maintenance","headcount":36,"key":"Maintenance"},
    {"name":"Structures","headcount":22,"key":"Structures"},
    {"name":"Avionics","headcount":15,"key":"Avionics"},
    {"name":"Inspection","headcount":10,"key":"Inspection"},
    {"name":"Interiors","headcount":11,"key":"Interiors"},
    {"name":"Engineering","headcount":7,"key":"Engineering"},
    {"name":"Cabinet","headcount":3,"key":"Cabinet"},
    {"name":"Upholstery","headcount":7,"key":"Upholstery"},
    {"name":"Finish","headcount":6,"key":"Finish"},
]

# --------------------- SESSION STATE ---------------------
if "projects" not in st.session_state:
    st.session_state.projects = deepcopy(DEFAULT_PROJECTS)
if "potential" not in st.session_state:
    st.session_state.potential = deepcopy(DEFAULT_POTENTIAL)
if "actual" not in st.session_state:
    st.session_state.actual = deepcopy(DEFAULT_ACTUAL)
if "depts" not in st.session_state:
    st.session_state.depts = deepcopy(DEFAULT_DEPTS)

def dept_keys():
    return [d["key"] for d in st.session_state.depts]

# --------------------- QUICK EDIT (sidebar) ---------------------
st.sidebar.header("Quick Edit")
dataset_choice = st.sidebar.selectbox("Dataset", ["Confirmed","Potential","Actual"])
dataset_key = {"Confirmed":"projects","Potential":"potential","Actual":"actual"}[dataset_choice]
current_list = st.session_state[dataset_key]
project_ids = [f'{(p.get("number") or "—")} — {(p.get("customer") or "Unknown")}' for p in current_list]
select_existing = st.sidebar.selectbox("Project", ["➕ New Project"] + project_ids)

with st.sidebar.form("quick_edit"):
    if select_existing == "➕ New Project":
        number = st.text_input("Project Number", "PXXXX")
        customer = st.text_input("Customer", "")
        aircraft = st.text_input("Aircraft Model", "")
        scope = st.text_input("Scope", "")
        induction = st.date_input("Induction", date(2025, 11, 1)).isoformat()
        delivery  = st.date_input("Delivery",  date(2025, 11, 8)).isoformat()
        hours_inputs = {k: st.number_input(f"{k} hours", min_value=0.0, value=0.0, step=1.0) for k in dept_keys()}
    else:
        idx = project_ids.index(select_existing)
        proj = deepcopy(current_list[idx])
        number = st.text_input("Project Number", str(proj.get("number") or ""))
        customer = st.text_input("Customer", str(proj.get("customer") or ""))
        aircraft = st.text_input("Aircraft Model", str(proj.get("aircraftModel") or ""))
        scope = st.text_input("Scope", str(proj.get("scope") or ""))
        induction = st.date_input("Induction", date.fromisoformat(str(proj["induction"])[:10])).isoformat()
        delivery  = st.date_input("Delivery",  date.fromisoformat(str(proj["delivery"])[:10])).isoformat()
        hours_inputs = {k: st.number_input(f"{k} hours", min_value=0.0, value=float(proj.get(k, 0) or 0), step=1.0) for k in dept_keys()}

    colA, colB = st.columns(2)
    with colA:
        apply_btn = st.form_submit_button("Apply Changes", use_container_width=True)
    with colB:
        reset_btn = st.form_submit_button("Reset to Defaults", use_container_width=True)

if apply_btn:
    entry = {"number": number.strip(), "customer": customer.strip(), "aircraftModel": aircraft.strip(),
             "scope": scope.strip(), "induction": induction, "delivery": delivery}
    for k in dept_keys(): entry[k] = float(hours_inputs[k] or 0.0)
    if select_existing == "➕ New Project":
        st.session_state[dataset_key].append(entry)
    else:
        st.session_state[dataset_key][idx] = entry
    st.toast("Dataset updated", icon="✅")

if reset_btn:
    st.session_state.projects  = deepcopy(DEFAULT_PROJECTS)
    st.session_state.potential = deepcopy(DEFAULT_POTENTIAL)
    st.session_state.actual    = deepcopy(DEFAULT_ACTUAL)
    st.session_state.depts     = deepcopy(DEFAULT_DEPTS)
    st.toast("All datasets reset to defaults", icon="↩️")

# --------------------- BULK EDIT ---------------------
with st.expander("Bulk Edit: Confirmed / Potential / Actual", expanded=False):
    c1, c2, c3 = st.columns(3)
    with c1:
        df_proj = st.data_editor(pd.DataFrame(st.session_state.projects), key="ed_confirmed", height=300)
        st.session_state.projects = df_proj.astype(object).to_dict(orient="records")
    with c2:
        df_pot = st.data_editor(pd.DataFrame(st.session_state.potential), key="ed_potential", height=300)
        st.session_state.potential = df_pot.astype(object).to_dict(orient="records")
    with c3:
        df_act = st.data_editor(pd.DataFrame(st.session_state.actual), key="ed_actual", height=300)
        st.session_state.actual = df_act.astype(object).to_dict(orient="records")

with st.expander("Edit Department Headcounts", expanded=False):
    df_depts = st.data_editor(pd.DataFrame(st.session_state.depts), key="ed_depts", height=240)
    df_depts["headcount"] = pd.to_numeric(df_depts["headcount"], errors="coerce").fillna(0).astype(int)
    st.session_state.depts = df_depts.to_dict(orient="records")

st.markdown("---")

# --------------------- HTML/JS ---------------------
html_template = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <title>Labor Capacity Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
  <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3"></script>
  <style>
    :root{
      --brand:#003366; --brand-20: rgba(0,51,102,0.2);
      --capacity:#d32f2f; --capacity-20: rgba(211,47,47,0.2);
      --potential:#2e7d32; --potential-20: rgba(46,125,50,0.2);
      --actual:#ef6c00; --actual-20: rgba(239,108,0,0.2);
      --muted:#6b7280;
    }
    html, body { height:100%; }
    body { font-family: Arial, sans-serif; margin: 8px 14px 24px; overflow-x:hidden; }
    h1 { text-align:center; margin: 6px 0 4px; }
    .controls { display:flex; gap:16px; flex-wrap:wrap; align-items:center; justify-content:center; margin: 8px auto 10px; }
    .controls label { font-size:14px; display:flex; align-items:center; gap:6px; }
    .metric-bar { display:flex; gap:16px; justify-content:center; flex-wrap:wrap; margin: 8px 0 10px; }
    .metric { border:1px solid #e5e7eb; border-radius:10px; padding:10px 14px; min-width:220px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); background:#fff; }
    .metric .label { font-size:12px; color:var(--muted); margin-bottom:4px; }
    .metric .value { font-weight:700; font-size:18px; }
    .chart-wrap { width:100%; height:720px; margin-bottom: 8px; position:relative; }
    .chart-wrap.util { height:380px; margin-top: 8px; }
    .chart-wrap.sand { height:420px; margin-top: 6px; }
    .footnote { text-align:center; color:#6b7280; font-size:12px; }

    /* Anchored popover */
    .popover {
      display:none; position:fixed; z-index:9999; max-width:min(92vw, 900px);
      background:#fff; border:1px solid #e5e7eb; border-radius:12px; box-shadow:0 12px 30px rgba(0,0,0,0.2);
    }
    .popover header { padding:10px 12px; border-bottom:1px solid #eee; font-weight:600; display:flex; justify-content:space-between; gap:10px; align-items:center; }
    .popover header button { border:none; background:#f3f4f6; border-radius:8px; padding:4px 8px; cursor:pointer; }
    .popover .content { padding:10px 12px 12px; max-height:60vh; overflow:auto; }
    .popover table { width:100%; border-collapse:collapse; }
    .popover th, .popover td { border-bottom:1px solid #eee; padding:6px 8px; text-align:left; font-size:13px; }

    /* What-If panel */
    .impact-grid{
      display:grid; gap:10px; grid-template-columns: repeat(6, minmax(120px,1fr));
      align-items:end; margin:10px 0 6px;
    }
    .impact-grid label{ font-size:12px; color:#374151; display:flex; flex-direction:column; gap:6px; }
    .impact-grid input, .impact-grid select, .impact-grid button{ padding:8px; border:1px solid #e5e7eb; border-radius:8px; font-size:13px;}
    .impact-grid button{ cursor:pointer; background:#111827; color:#fff; border-color:#111827; }
    .impact-box{ border:1px solid #e5e7eb; border-radius:10px; padding:10px 12px; background:#fff; font-size:13px;}
    .impact-table{ width:100%; border-collapse:collapse; margin-top:6px; }
    .impact-table th,.impact-table td{ border-bottom:1px solid #eee; padding:6px 8px; text-align:left; }

    .inline-actions { display:flex; gap:10px; align-items:center; }
    .ghost { background:#fff; color:#111827; border:1px solid #e5e7eb; }

    details.impact{ border:1px solid #e5e7eb; border-radius:10px; padding:8px 12px; background:#fafafa; margin:8px 0 14px; }
    details.impact summary{ cursor:pointer; font-weight:600; }

    /* Manual What-If box */
    .manual-box{ display:none; border:1px dashed #d1d5db; border-radius:10px; padding:10px; background:#fff; }
    .manual-grid{ display:grid; gap:8px; grid-template-columns: repeat(4, minmax(120px,1fr)); }
    .manual-grid label{ font-size:12px; color:#374151; display:flex; flex-direction:column; gap:6px; }
  </style>
</head>
<body>

<h1>Capacity-Load By Discipline</h1>

<div class="controls">
  <label for="disciplineSelect"><strong>Discipline:</strong></label>
  <select id="disciplineSelect"></select>

  <label><input type="checkbox" id="showConfirmed" checked> Show Confirmed</label>
  <label><input type="checkbox" id="showPotential" checked> Show Potential</label>
  <label><input type="checkbox" id="showActual"> Show Actual</label>

  <label><strong>Timeline:</strong>
    <select id="periodSel">
      <option value="weekly" selected>Weekly</option>
      <option value="monthly">Monthly (workdays)</option>
    </select>
  </label>

  <label><strong>Productivity:</strong>
    <input type="range" id="prodFactor" min="0.50" max="1.00" step="0.01" value="0.85">
    <span id="prodVal">0.85</span>
  </label>

  <label><strong>Hours / FTE / wk:</strong>
    <input type="number" id="hoursPerFTE" min="30" max="60" step="1" value="40" style="width:64px;">
  </label>

  <label><input type="checkbox" id="utilSeparate" checked> Utilization in separate chart</label>
</div>

<div class="metric-bar">
  <div class="metric"><div class="label">Peak Utilization</div><div class="value" id="peakUtil">—</div></div>
  <div class="metric"><div class="label">Worst Period (Max Over/Under)</div><div class="value" id="worstWeek">—</div></div>
  <div class="metric"><div class="label">Capacity</div><div class="value" id="weeklyCap">—</div></div>
</div>

<!-- What-If Schedule Impact -->
<details class="impact" open>
  <summary>What-If Schedule Impact</summary>
  <div class="impact-grid">
    <label>Source dataset
      <select id="impactSource">
        <option value="potential" selected>Potential</option>
        <option value="confirmed">Confirmed</option>
        <option value="manual">Manual</option>
      </select>
    </label>
    <label>Project
      <select id="impactProject"></select>
    </label>
    <label>Scope multiplier
      <input id="impactMult" type="number" step="0.05" value="1.00">
    </label>
    <label>Min lead (days)
      <input id="impactLead" type="number" step="1" value="14">
    </label>
    <label>Overtime (+% cap)
      <input id="impactOT" type="number" step="5" value="0">
    </label>
    <label>Target util (%)
      <input id="impactTarget" type="number" step="5" value="100">
    </label>

    <label>Induction override
      <input type="date" id="impactInd">
    </label>
    <label>Delivery override
      <input type="date" id="impactDel">
    </label>

    <div class="inline-actions" style="grid-column: span 2;">
      <button id="impactRun">Calculate Impact</button>
      <button id="impactClear" class="ghost">Clear What-If</button>
    </div>
  </div>

  <!-- Manual project inputs (hidden unless manual source chosen) -->
  <div id="manualBox" class="manual-box">
    <div class="manual-grid" id="manualFixed">
      <label>Manual Project #
        <input id="mNum" type="text" placeholder="PXXXX" />
      </label>
      <label>Customer
        <input id="mCust" type="text" placeholder="Customer" />
      </label>
      <label>Induction
        <input id="mInd" type="date" />
      </label>
      <label>Delivery
        <input id="mDel" type="date" />
      </label>
    </div>
    <div class="manual-grid" id="manualHours" style="margin-top:8px;"></div>
  </div>

  <div id="impactResult" class="impact-box"></div>
</details>

<div class="chart-wrap"><canvas id="myChart"></canvas></div>
<div class="chart-wrap util" style="display:block;"><canvas id="utilChart"></canvas></div>
<div class="chart-wrap sand"><canvas id="sandChart"></canvas></div>

<p class="footnote">Tip: click the <em>Confirmed</em> line; if “Show Potential” is on, the popup includes both Confirmed and Potential for that period.</p>

<!-- Anchored popover -->
<div class="popover" id="drillPopover" role="dialog" aria-modal="true" aria-labelledby="popTitle">
  <header>
    <div id="popTitle">Breakdown</div>
    <button id="closePop">Close</button>
  </header>
  <div class="content">
    <table>
      <thead id="popHead"><tr><th>Customer</th><th>Hours</th></tr></thead>
      <tbody id="popBody"></tbody>
    </table>
  </div>
</div>

<script>
// ---- LIVE DATA ----
const projects = __PROJECTS__;
const potentialProjects = __POTENTIAL__;
const projectsActual = __ACTUAL__;
const departmentCapacities = __DEPTS__;

let PRODUCTIVITY_FACTOR = 0.85;
let HOURS_PER_FTE = 40;

// -------------------- TZ-SAFE DATE HELPERS --------------------
function parseDateLocalISO(s){
  if(!s) return new Date(NaN);
  const t = String(s).split('T')[0];
  const [y,m,d] = t.split('-').map(Number);
  return new Date(y, (m||1)-1, d||1);
}
function ymd(d){ return [d.getFullYear(), String(d.getMonth()+1).padStart(2,'0'), String(d.getDate()).padStart(2,'0')].join('-'); }
function mondayOf(d){ const t=new Date(d.getFullYear(), d.getMonth(), d.getDate()); const day=(t.getDay()+6)%7; t.setDate(t.getDate()-day); return t; }
function firstOfMonth(d){ return new Date(d.getFullYear(), d.getMonth(), 1); }
function lastOfMonth(d){ return new Date(d.getFullYear(), d.getMonth()+1, 0); }
function isWorkday(d){ const day = d.getDay(); return day >= 1 && day <= 5; }
function workdaysInclusive(a,b){
  const start = new Date(a.getFullYear(), a.getMonth(), a.getDate());
  const end   = new Date(b.getFullYear(), b.getMonth(), b.getDate());
  let c = 0, d = new Date(start);
  while (d <= end) { if (isWorkday(d)) c++; d.setDate(d.getDate()+1); }
  return c;
}
function workdaysInMonth(d){
  const mStart = firstOfMonth(d);
  const mEnd   = lastOfMonth(d);
  return workdaysInclusive(mStart, mEnd);
}

// -------------------- LABELS --------------------
function getWeekList(){
  let minD=null,maxD=null;
  function expand(arr){ for(const p of arr){ const a=parseDateLocalISO(p.induction), b=parseDateLocalISO(p.delivery); if(!minD||a<minD)minD=a; if(!maxD||b>maxD)maxD=b; } }
  if(projects.length) expand(projects);
  if(potentialProjects.length) expand(potentialProjects);
  if(projectsActual.length) expand(projectsActual);
  if(!minD||!maxD){ const start=mondayOf(new Date()); return [ymd(start)]; }
  const start=mondayOf(minD); const weeks=[]; const cur=new Date(start);
  while(cur<=maxD){ weeks.push(new Date(cur)); cur.setDate(cur.getDate()+7); }
  return weeks.map(ymd);
}
function getMonthList(){
  let minD=null,maxD=null;
  function expand(arr){ for(const p of arr){ const a=parseDateLocalISO(p.induction), b=parseDateLocalISO(p.delivery); if(!minD||a<minD)minD=a; if(!maxD||b>maxD)maxD=b; } }
  if(projects.length) expand(projects);
  if(potentialProjects.length) expand(potentialProjects);
  if(projectsActual.length) expand(projectsActual);
  if(!minD||!maxD){ const start=firstOfMonth(new Date()); return [ymd(start)]; }
  const start=firstOfMonth(minD); const end=firstOfMonth(maxD);
  const months=[]; const cur=new Date(start);
  while(cur<=end){ months.push(new Date(cur)); cur.setMonth(cur.getMonth()+1); }
  return months.map(ymd);
}

// -------------------- WEEKLY LOADS --------------------
function computeWeeklyLoadsDetailed(arr, key, labels){
  const total=new Array(labels.length).fill(0); const breakdown=labels.map(()=>[]);
  for(const p of arr){
    const hrs=p[key]||0; if(!hrs) continue;
    const a=parseDateLocalISO(p.induction), b=parseDateLocalISO(p.delivery);
    let s=-1,e=-1;
    for(let i=0;i<labels.length;i++){ const L=parseDateLocalISO(labels[i]); if(L>=a && s===-1) s=i; if(L<=b) e=i; }
    if(s!==-1 && e!==-1 && e>=s){
      const n=e-s+1, per=hrs/n;
      for(let w=s; w<=e; w++){ total[w]+=per; breakdown[w].push({customer:(p.customer||"Unknown"), hours:per}); }
    }
  }
  return {series:total, breakdown};
}
function computeWeeklyLoadsActual(arr, key, labels){
  const total=new Array(labels.length).fill(0); const breakdown=labels.map(()=>[]);
  const today=new Date();
  for(const p of arr){
    const hrs=p[key]||0; if(!hrs) continue;
    const a=parseDateLocalISO(p.induction), planned=parseDateLocalISO(p.delivery);
    const end = (a>today) ? planned : (planned<today? planned : today);
    if(end<a) continue;
    let s=-1,e=-1;
    for(let i=0;i<labels.length;i++){ const L=parseDateLocalISO(labels[i]); if(L>=a && s===-1) s=i; if(L<=end) e=i; }
    if(s!==-1 && e!==-1 && e>=s){
      const n=e-s+1, per=hrs/n;
      for(let w=s; w<=e; w++){ total[w]+=per; breakdown[w].push({customer:(p.customer||"Unknown"), hours:per}); }
    }
  }
  return {series:total, breakdown};
}

// -------------------- MONTHLY LOADS (workdays only) --------------------
function computeMonthlyLoadsDetailed(arr, key, monthLabels){
  const total=new Array(monthLabels.length).fill(0); const breakdown=monthLabels.map(()=>[]);
  for(const p of arr){
    const hrs=p[key]||0; if(!hrs) continue;
    const start=parseDateLocalISO(p.induction), end=parseDateLocalISO(p.delivery);
    const projWD = Math.max(1, workdaysInclusive(start, end));
    for(let i=0;i<monthLabels.length;i++){
      const mStart = parseDateLocalISO(monthLabels[i]);
      const mEnd   = lastOfMonth(mStart);
      const overlapStart = new Date(Math.max(mStart, start));
      const overlapEnd   = new Date(Math.min(mEnd, end));
      if(overlapEnd >= overlapStart){
        const overlapWD = workdaysInclusive(overlapStart, overlapEnd);
        const hoursMonth = hrs * (overlapWD / projWD);
        total[i] += hoursMonth;
        breakdown[i].push({customer:(p.customer||"Unknown"), hours:hoursMonth});
      }
    }
  }
  return {series:total, breakdown};
}
function computeMonthlyLoadsActual(arr, key, monthLabels){
  const total=new Array(monthLabels.length).fill(0); const breakdown=monthLabels.map(()=>[]);
  const today=new Date();
  for(const p of arr){
    const hrs=p[key]||0; if(!hrs) continue;
    const a=parseDateLocalISO(p.induction), planned=parseDateLocalISO(p.delivery);
    const end = (a>today) ? planned : (planned<today? planned : today);
    if(end<a) continue;
    const projWD = Math.max(1, workdaysInclusive(a, end));
    for(let i=0;i<monthLabels.length;i++){
      const mStart = parseDateLocalISO(monthLabels[i]);
      const mEnd   = lastOfMonth(mStart);
      const overlapStart = new Date(Math.max(mStart, a));
      const overlapEnd   = new Date(Math.min(mEnd, end));
      if(overlapEnd >= overlapStart){
        const overlapWD = workdaysInclusive(overlapStart, overlapEnd);
        const hoursMonth = hrs * (overlapWD / projWD);
        total[i] += hoursMonth;
        breakdown[i].push({customer:(p.customer||"Unknown"), hours:hoursMonth});
      }
    }
  }
  return {series:total, breakdown};
}

// -------------------- LABELS & DATA MAPS --------------------
const weekLabels = getWeekList();
const monthLabels = getMonthList();

const dataWConfirmed = {}, dataWPotential = {}, dataWActual = {};
const dataMConfirmed = {}, dataMPotential = {}, dataMActual = {};

departmentCapacities.forEach(d=>{
  const cw=computeWeeklyLoadsDetailed(projects, d.key, weekLabels);
  const pw=computeWeeklyLoadsDetailed(potentialProjects, d.key, weekLabels);
  const aw=computeWeeklyLoadsActual(projectsActual, d.key, weekLabels);
  dataWConfirmed[d.key]={name:d.name, series:cw.series, breakdown:cw.breakdown};
  dataWPotential[d.key]={name:d.name, series:pw.series, breakdown:pw.breakdown};
  dataWActual[d.key]   ={name:d.name, series:aw.series, breakdown:aw.breakdown};

  const cm=computeMonthlyLoadsDetailed(projects, d.key, monthLabels);
  const pm=computeMonthlyLoadsDetailed(potentialProjects, d.key, monthLabels);
  const am=computeMonthlyLoadsActual(projectsActual, d.key, monthLabels);
  dataMConfirmed[d.key]={name:d.name, series:cm.series, breakdown:cm.breakdown};
  dataMPotential[d.key]={name:d.name, series:pm.series, breakdown:pm.breakdown};
  dataMActual[d.key]   ={name:d.name, series:am.series, breakdown:am.breakdown};
});

// -------------------- UI ELEMENTS --------------------
const sel = document.getElementById('disciplineSelect');
departmentCapacities.forEach(d=>{ const o=document.createElement('option'); o.value=d.key; o.textContent=d.name; sel.appendChild(o); });
sel.value=departmentCapacities[0]?.key || "";

const prodSlider = document.getElementById('prodFactor');
const prodVal = document.getElementById('prodVal');
const hoursInput = document.getElementById('hoursPerFTE');
const chkConf = document.getElementById('showConfirmed');
const chkPot = document.getElementById('showPotential');
const chkAct = document.getElementById('showActual');
const periodSel = document.getElementById('periodSel');
const utilSepChk = document.getElementById('utilSeparate');

// -------------------- CAPACITY & UTILIZATION --------------------
function capacityArray(key, labels, period){
  const dept = departmentCapacities.find(x=>x.key===key);
  const capPerWeek = (dept?.headcount || 0) * HOURS_PER_FTE * PRODUCTIVITY_FACTOR;
  if(period==='weekly') return labels.map(()=>capPerWeek);
  return labels.map(lbl=>{
    const d = parseDateLocalISO(lbl);
    const wd = workdaysInMonth(d);
    return (capPerWeek / 5) * wd;  // scale by workdays in that month
  });
}
function zeros(n){ return new Array(n).fill(0); }
function utilizationArray(period, key, includeConfirmed, includePotential){
  const mapC = (period==='weekly') ? dataWConfirmed : dataMConfirmed;
  const mapP = (period==='weekly') ? dataWPotential : dataMPotential;
  const labels = (period==='weekly') ? weekLabels : monthLabels;
  const conf = mapC[key]?.series || [];
  const pot  = mapP[key]?.series || [];
  const cap  = capacityArray(key, labels, period);
  return cap.map((c,i)=>{
    const load = (includeConfirmed ? (conf[i]||0) : 0) + (includePotential ? (pot[i]||0) : 0);
    return c ? (100*load/c) : 0;
  });
}

const weekTodayLabel = ymd(mondayOf(new Date()));
const monthTodayLabel = ymd(firstOfMonth(new Date()));
const annos = { annotations:{ todayLine:{ type:'line', xMin: weekTodayLabel, xMax: weekTodayLabel,
  borderColor:'#9ca3af', borderWidth:1, borderDash:[4,4],
  label:{ display:true, content:'Today', position:'start', color:'#6b7280', backgroundColor:'rgba(255,255,255,0.8)' } } } };

// -------------------- CHARTS --------------------
const ctx = document.getElementById('myChart').getContext('2d');
let currentKey = sel.value;
let currentPeriod = 'weekly';
let showConfirmed = true;
let showPotential = true;
let showActual = false;
let utilSeparate = true;
let utilChart = null;

function currentLabels(){ return currentPeriod==='weekly' ? weekLabels : monthLabels; }
function dataMap(kind){
  if(currentPeriod==='weekly'){
    return kind==='c'?dataWConfirmed:kind==='p'?dataWPotential:dataWActual;
  } else {
    return kind==='c'?dataMConfirmed:kind==='p'?dataMPotential:dataMActual;
  }
}

let chart = new Chart(ctx,{
  type:'line',
  data:{
    labels: currentLabels(),
    datasets:[
      { label: ((dataMap('c')[currentKey]?.name)||'Dept') + ' Load (hrs)', data: (dataMap('c')[currentKey]?.series)||[],
        borderColor: getComputedStyle(document.documentElement).getPropertyValue('--brand').trim(),
        backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--brand-20').trim(),
        borderWidth:2, fill:true, tension:0.1, pointRadius:0, hidden: !showConfirmed },
      { label: ((dataMap('c')[currentKey]?.name)||'Dept') + ' Capacity (hrs)', data: capacityArray(currentKey, currentLabels(), currentPeriod),
        borderColor: getComputedStyle(document.documentElement).getPropertyValue('--capacity').trim(),
        backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--capacity-20').trim(),
        borderWidth:2, fill:false, borderDash:[6,6], tension:0.1, pointRadius:0 },
      { label: ((dataMap('c')[currentKey]?.name)||'Dept') + ' Potential (hrs)', data: (dataMap('p')[currentKey]?.series)||[],
        borderColor: getComputedStyle(document.documentElement).getPropertyValue('--potential').trim(),
        backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--potential-20').trim(),
        borderWidth:2, fill:true, tension:0.1, pointRadius:0, hidden: !showPotential },
      { label: ((dataMap('c')[currentKey]?.name)||'Dept') + ' Actual (hrs)', data: (dataMap('a')[currentKey]?.series)||[],
        borderColor: getComputedStyle(document.documentElement).getPropertyValue('--actual').trim(),
        backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--actual-20').trim(),
        borderWidth:2, fill:true, tension:0.1, pointRadius:0, hidden: !showActual },
      { label: 'Utilization %', data: utilizationArray(currentPeriod, currentKey, showConfirmed, showPotential),
        borderColor:'#374151', backgroundColor:'rgba(55,65,81,0.12)',
        yAxisID:'y2', borderWidth:1.5, fill:false, tension:0.1, pointRadius:0 }
    ]
  },
  options:{
    responsive:true, maintainAspectRatio:false,
    interaction:{ mode:'index', intersect:false },
    scales:{
      x:{ title:{display:true, text:'Week Starting'} },
      y:{ title:{display:true, text:'Hours'}, beginAtZero:true },
      y2:{ title:{display:true, text:'Utilization %'}, beginAtZero:true, position:'right', grid:{ drawOnChartArea:false }, suggestedMax:150 }
    },
    plugins:{
      annotation: annos,
      legend:{ position:'top' },
      title:{ display:true, text: 'Weekly Load vs. Capacity - ' + ((dataMap('c')[currentKey]?.name)||'Dept') }
    },
    onClick:(evt, elems)=>{
      if(!elems||!elems.length) return;
      const {datasetIndex, index:idx} = elems[0];
      if(datasetIndex===1 || datasetIndex===4) return; // ignore capacity & utilization

      const labels = currentLabels();
      const name = (dataMap('c')[currentKey]?.name)||'Dept';
      const isMonthly = currentPeriod==='monthly';

      const mapC = dataMap('c')[currentKey]?.breakdown || [];
      const mapP = dataMap('p')[currentKey]?.breakdown || [];
      const mapA = dataMap('a')[currentKey]?.breakdown || [];

      const includePot = document.getElementById('showPotential').checked;

      let title='', rows=null, combined=false;
      if(datasetIndex===0){
        const bc = mapC[idx] || [];
        const bp = includePot ? (mapP[idx] || []) : [];
        if(includePot && bp.length){
          rows = mergeConfirmedPotential(bc, bp); combined=true;
          title = `${labels[idx]} · ${name} · ${isMonthly?'Monthly':'Weekly'} · Confirmed + Potential`;
        } else {
          rows = bc;
          title = `${labels[idx]} · ${name} · ${isMonthly?'Confirmed (mo, workdays)':'Confirmed (wk)'}`;
        }
      } else if(datasetIndex===2){
        rows = mapP[idx] || [];
        title = `${labels[idx]} · ${name} · ${isMonthly?'Potential (mo, workdays)':'Potential (wk)'}`;
      } else if(datasetIndex===3){
        rows = mapA[idx] || [];
        title = `${labels[idx]} · ${name} · ${isMonthly?'Actual (mo, workdays)':'Actual (wk)'}`;
      } else { return; }

      const native = evt?.native || evt?.nativeEvent || evt;
      const cx = (native?.clientX ?? 200);
      const cy = (native?.clientY ?? 200);
      if(combined) openPopoverCombined(title, rows, cx, cy);
      else openPopoverSingle(title, rows, cx, cy);
    }
  }
});

// -------- Utilization mini-chart handling --------
function createUtilChart(){
  const ctx2 = document.getElementById('utilChart').getContext('2d');
  const todayX = (currentPeriod==='weekly') ? weekTodayLabel : monthTodayLabel;
  utilChart = new Chart(ctx2, {
    type: 'line',
    data: {
      labels: currentLabels(),
      datasets: [{
        label: 'Utilization %',
        data: utilizationArray(currentPeriod, currentKey, showConfirmed, showPotential),
        borderColor: '#111827',
        backgroundColor: 'rgba(17,24,39,0.10)',
        borderWidth: 2,
        pointRadius: 0,
        fill: false,
        tension: (currentPeriod==='monthly') ? 0 : 0.1,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      scales: {
        x: { title: { display: true, text: currentPeriod==='weekly' ? 'Week Starting' : 'Month Starting' } },
        y: {
          title: { display: true, text: 'Utilization %' },
          beginAtZero: true,
          suggestedMax: 160,
          ticks: { callback: (val) => `${val}%` }
        }
      },
      plugins: {
        legend: { display: false },
        title: { display: true, text: 'Utilization %' },
        annotation: {
          annotations: {
            todayLine: {
              type: 'line', xMin: todayX, xMax: todayX,
              borderColor: '#9ca3af', borderWidth: 1, borderDash: [4,4],
              label: { display: true, content: 'Today', position: 'start', color: '#6b7280',
                       backgroundColor: 'rgba(255,255,255,0.8)' }
            },
            target100: {
              type: 'line',
              yMin: 100, yMax: 100,
              borderColor: getComputedStyle(document.documentElement).getPropertyValue('--capacity').trim(),
              borderWidth: 2,
              borderDash: [6,3],
              label: {
                display: true,
                content: '100% target',
                position: 'end',
                backgroundColor: 'rgba(255,255,255,0.9)',
                color: getComputedStyle(document.documentElement).getPropertyValue('--capacity').trim(),
              }
            }
          }
        }
      }
    }
  });
}

function rebuildUtilChart(){
  const wrap = document.querySelector('.chart-wrap.util');
  if (utilSeparate) {
    wrap.style.display = 'block';
    if (utilChart) { utilChart.destroy(); utilChart = null; }
    createUtilChart();
    chart.data.datasets[4].hidden = true; // hide on main chart
  } else {
    wrap.style.display = 'none';
    if (utilChart) { utilChart.destroy(); utilChart = null; }
    chart.data.datasets[4].hidden = false; // show on main chart
  }
  chart.update();
}

// -------------------- SAND CHART (stacked per-project) --------------------
let sandChart = null;
function sumArrays(a,b){ const n=Math.max(a.length,b.length), out=new Array(n).fill(0);
  for(let i=0;i<n;i++){ out[i]=(a[i]||0)+(b[i]||0); } return out; }
function colorFromIndex(i, alpha=1){
  const hue = (i*47) % 360;
  return `hsla(${hue}, 65%, 55%, ${alpha})`;
}
function perProjectWeekly(arr, key, labels){
  const out = [];
  for(const p of arr){
    const hrs = p[key]||0; if(!hrs) continue;
    const a = parseDateLocalISO(p.induction), b = parseDateLocalISO(p.delivery);
    if(isNaN(a) || isNaN(b) || b<a) continue;
    const data = new Array(labels.length).fill(0);
    let s=-1,e=-1;
    for(let i=0;i<labels.length;i++){
      const L=parseDateLocalISO(labels[i]);
      if(L>=a && s===-1) s=i;
      if(L<=b) e=i;
    }
    if(s!==-1 && e!==-1 && e>=s){
      const n=e-s+1, per=hrs/n;
      for(let i=s;i<=e;i++){ data[i]+=per; }
      const label = `${p.number || '—'} — ${p.customer || 'Unknown'}`;
      out.push({ label, data, total: hrs });
    }
  }
  return out;
}
function perProjectMonthly(arr, key, labels){
  const out = [];
  for(const p of arr){
    const hrs = p[key]||0; if(!hrs) continue;
    const a = parseDateLocalISO(p.induction), b = parseDateLocalISO(p.delivery);
    if(isNaN(a) || isNaN(b) || b<a) continue;
    const projWD = Math.max(1, workdaysInclusive(a,b));
    const data = new Array(labels.length).fill(0);
    for(let i=0;i<labels.length;i++){
      const mStart = parseDateLocalISO(labels[i]);
      const mEnd   = lastOfMonth(mStart);
      const ovS = new Date(Math.max(mStart, a));
      const ovE = new Date(Math.min(mEnd, b));
      if(ovE >= ovS){
        const monWD = workdaysInclusive(ovS, ovE);
        data[i] += hrs * (monWD / projWD);
      }
    }
    const label = `${p.number || '—'} — ${p.customer || 'Unknown'}`;
    out.push({ label, data, total: hrs });
  }
  return out;
}
function mergeProjectLists(A, B){
  const map = new Map();
  A.forEach(x => map.set(x.label, { label:x.label, data:x.data.slice(), total:x.total }));
  B.forEach(x => {
    if(map.has(x.label)){
      const cur = map.get(x.label);
      cur.data = sumArrays(cur.data, x.data);
      cur.total += x.total;
    } else {
      map.set(x.label, { label:x.label, data:x.data.slice(), total:x.total });
    }
  });
  return Array.from(map.values());
}
function rebuildSandChart(){
  const labels = currentLabels();
  const period = currentPeriod;
  const key     = currentKey;
  const includeConfirmed = showConfirmed;
  const includePotential = showPotential;

  const perProjFn = (period==='weekly') ? perProjectWeekly : perProjectMonthly;
  const listC = includeConfirmed ? perProjFn(projects, key, labels) : [];
  const listP = includePotential ? perProjFn(potentialProjects, key, labels) : [];

  // Combine whichever sources are enabled so stack matches visible total
  const combined = mergeProjectLists(listC, listP);

  // Rank & cut to Top N and "Other"
  const TOP_N = 10;
  combined.sort((a,b)=> b.total - a.total);
  const top = combined.slice(0, TOP_N - 1);
  const rest = combined.slice(TOP_N - 1);
  if(rest.length){
    const other = rest.reduce((acc, x) => {
      acc.total += x.total;
      acc.data = sumArrays(acc.data, x.data);
      return acc;
    }, { label: "Other", total: 0, data: new Array(labels.length).fill(0) });
    top.push(other);
  }

  // Build datasets
  const ds = top.map((p,i)=>({
    label: p.label,
    data: p.data,
    type: 'line',
    fill: true,
    tension: (period==='monthly') ? 0 : 0.15,
    pointRadius: 0,
    borderWidth: 1,
    backgroundColor: colorFromIndex(i, 0.25),
    borderColor: colorFromIndex(i, 1),
    stack: 'all'
  }));

  // Capacity overlay
  ds.push({
    label: 'Capacity (hrs)',
    data: capacityArray(key, labels, period),
    type: 'line',
    fill: false,
    pointRadius: 0,
    borderWidth: 2,
    borderDash: [6,6],
    borderColor: getComputedStyle(document.documentElement).getPropertyValue('--capacity').trim(),
    yAxisID: 'y'
  });

  const ctxSand = document.getElementById('sandChart').getContext('2d');
  const todayX = (period==='weekly') ? weekTodayLabel : monthTodayLabel;

  if(sandChart){ sandChart.destroy(); sandChart = null; }
  sandChart = new Chart(ctxSand, {
    type: 'line',
    data: { labels, datasets: ds },
    options: {
      responsive: true, maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      scales: {
        x: { title: { display: true, text: period==='weekly' ? 'Week Starting' : 'Month Starting' } },
        y: { title: { display: true, text: 'Hours' }, stacked: true, beginAtZero: true }
      },
      plugins: {
        legend: { position: 'top' },
        title: { display: true, text: 'Sand Chart — Per-Project Contribution (matches visible Load)' },
        annotation: {
          annotations: {
            todayLine: {
              type: 'line', xMin: todayX, xMax: todayX,
              borderColor: '#9ca3af', borderWidth: 1, borderDash: [4,4],
              label: { display: true, content: 'Today', position: 'start',
                       color: '#6b7280', backgroundColor: 'rgba(255,255,255,0.8)' }
            }
          }
        }
      }
    }
  });
}

// -------------------- KPIs & REFRESH --------------------
function updateKPIs(){
  const labels = currentLabels();
  const capArr = capacityArray(currentKey, labels, currentPeriod);
  const conf = (dataMap('c')[currentKey]?.series)||zeros(labels.length);
  const pot  = (dataMap('p')[currentKey]?.series)||zeros(labels.length);
  const combined = conf.map((v,i)=> (showConfirmed ? v : 0) + (showPotential ? (pot[i]||0) : 0));
  let peak=0, peakIdx=0, worstDiff=-Infinity, worstIdx=0;
  for(let i=0;i<combined.length;i++){
    const u = capArr[i] ? (combined[i]/capArr[i]*100) : 0;
    if(u>peak){ peak=u; peakIdx=i; }
    const diff = combined[i] - capArr[i];
    if(diff>worstDiff){ worstDiff=diff; worstIdx=i; }
  }
  document.getElementById('peakUtil').textContent = combined.length? `${peak.toFixed(0)}% (${currentPeriod==='weekly'?'wk':'mo'} ${labels[peakIdx]})` : '—';
  const status = worstDiff>=0 ? `+${isFinite(worstDiff)?worstDiff.toFixed(0):0} hrs over` : `${isFinite(worstDiff)?(-worstDiff).toFixed(0):0} hrs under`;
  document.getElementById('worstWeek').textContent = combined.length? `${labels[worstIdx]} · ${status}` : '—';
  const capUnit = currentPeriod==='weekly' ? `${capArr[0]?.toFixed(0)||0} hrs / wk` : `~${(capArr[0]||0).toFixed(0)} hrs / mo (workdays)`;
  document.getElementById('weeklyCap').textContent = capUnit;
}

function refreshDatasets(){
  const labels = currentLabels();
  chart.data.labels = labels;

  const deptName = (dataMap('c')[currentKey]?.name)||'Dept';
  chart.data.datasets[0].label = `${deptName} Load (hrs)`;
  chart.data.datasets[0].data  = (dataMap('c')[currentKey]?.series)||[];
  chart.data.datasets[1].label = `${deptName} Capacity (hrs)`;
  chart.data.datasets[1].data  = capacityArray(currentKey, labels, currentPeriod);
  chart.data.datasets[2].label = `${deptName} Potential (hrs)`;
  chart.data.datasets[2].data  = (dataMap('p')[currentKey]?.series)||[];
  chart.data.datasets[3].label = `${deptName} Actual (hrs)`;
  chart.data.datasets[3].data  = (dataMap('a')[currentKey]?.series)||[];

  chart.data.datasets[0].hidden = !showConfirmed;
  chart.data.datasets[2].hidden = !showPotential;
  chart.data.datasets[3].hidden = !showActual;

  chart.data.datasets[4].data = utilizationArray(currentPeriod, currentKey, showConfirmed, showPotential);

  const monthly = currentPeriod==='monthly';
  chart.data.datasets.forEach((ds, i)=>{
    ds.tension = monthly ? 0 : 0.1;
    if(i===1){ ds.stepped = monthly ? true : false; }
  });
  chart.options.scales.x.title.text = monthly ? 'Month Starting' : 'Week Starting';
  chart.options.plugins.title.text = (monthly ? 'Monthly (workdays)' : 'Weekly') + ' Load vs. Capacity - ' + deptName;

  chart.options.plugins.annotation.annotations.todayLine.xMin = monthly ? monthTodayLabel : weekTodayLabel;
  chart.options.plugins.annotation.annotations.todayLine.xMax = monthly ? monthTodayLabel : weekTodayLabel;

  chart.update();
  updateKPIs();

  if (utilChart) {
    utilChart.data.labels = currentLabels();
    utilChart.data.datasets[0].data = utilizationArray(currentPeriod, currentKey, showConfirmed, showPotential);
    utilChart.options.scales.x.title.text = (currentPeriod==='weekly' ? 'Week Starting' : 'Month Starting');
    const todayX = (currentPeriod==='weekly') ? weekTodayLabel : monthTodayLabel;
    utilChart.options.plugins.annotation.annotations.todayLine.xMin = todayX;
    utilChart.options.plugins.annotation.annotations.todayLine.xMax = todayX;
    utilChart.data.datasets[0].tension = (currentPeriod==='monthly') ? 0 : 0.1;
    utilChart.update();
  }

  rebuildSandChart();
}

// -------------------- LISTENERS --------------------
sel.addEventListener('change', e=>{ currentKey = e.target.value; refreshDatasets(); });
chkConf.addEventListener('change', e=>{ showConfirmed = e.target.checked; refreshDatasets(); });
chkPot.addEventListener('change', e=>{ showPotential = e.target.checked; refreshDatasets(); });
chkAct.addEventListener('change', e=>{ showActual = e.target.checked; refreshDatasets(); });
prodSlider.addEventListener('input', e=>{
  PRODUCTIVITY_FACTOR = parseFloat(e.target.value||'0.85'); prodVal.textContent = PRODUCTIVITY_FACTOR.toFixed(2);
  refreshDatasets();
});
hoursInput.addEventListener('change', e=>{
  const v = parseInt(e.target.value||'40',10);
  HOURS_PER_FTE = isNaN(v) ? 40 : Math.min(60, Math.max(30, v));
  e.target.value = HOURS_PER_FTE;
  refreshDatasets();
});
periodSel.addEventListener('change', e=>{
  currentPeriod = e.target.value; 
  refreshDatasets();
});
utilSepChk.addEventListener('change', e=>{
  utilSeparate = e.target.checked;
  rebuildUtilChart();
});

// -------------------- POPOVER --------------------
const pop = document.getElementById('drillPopover');
const popTitle = document.getElementById('popTitle');
const popHead = document.getElementById('popHead');
const popBody = document.getElementById('popBody');
document.getElementById('closePop').addEventListener('click', ()=>{ pop.style.display='none'; });

function placePopoverAt(x, y){
  pop.style.display='block'; // to get size
  const rect = pop.getBoundingClientRect();
  const pad = 12;
  const vw = window.innerWidth; const vh = window.innerHeight;
  let left = x + 14;
  let top  = y - 10;
  if (left + rect.width + pad > vw) left = vw - rect.width - pad;
  if (top + rect.height + pad > vh) top = vh - rect.height - pad;
  if (top < pad) top = pad;
  if (left < pad) left = pad;
  pop.style.left = left + "px";
  pop.style.top  = top  + "px";
}
function openPopoverSingle(title, rows, x, y){
  popTitle.textContent = title;
  popHead.innerHTML = "<tr><th>Customer</th><th>Hours</th></tr>";
  popBody.innerHTML = (rows&&rows.length)
    ? rows.map(r=>`<tr><td>${r.customer}</td><td>${r.hours.toFixed(1)}</td></tr>`).join('')
    : `<tr><td colspan="2">No data</td></tr>`;
  placePopoverAt(x, y);
}
function mergeConfirmedPotential(bc, bp){
  const map = new Map();
  (bc||[]).forEach(r=>{
    map.set(r.customer, {customer:r.customer, conf: (r.hours||0), pot: 0});
  });
  (bp||[]).forEach(r=>{
    if(map.has(r.customer)){ map.get(r.customer).pot += (r.hours||0); }
    else { map.set(r.customer, {customer:r.customer, conf:0, pot:(r.hours||0)}); }
  });
  const rows = Array.from(map.values()).map(x=>({ ...x, total: (x.conf + x.pot) }));
  rows.sort((a,b)=> b.total - a.total);
  return rows;
}
function openPopoverCombined(title, rows, x, y){
  popTitle.textContent = title;
  popHead.innerHTML = "<tr><th>Customer</th><th>Confirmed</th><th>Potential</th><th>Total</th></tr>";
  if(rows&&rows.length){
    popBody.innerHTML = rows.map(r=>`<tr><td>${r.customer}</td><td>${r.conf.toFixed(1)}</td><td>${r.pot.toFixed(1)}</td><td>${r.total.toFixed(1)}</td></tr>`).join('');
  } else {
    popBody.innerHTML = `<tr><td colspan="4">No data</td></tr>`;
  }
  placePopoverAt(x, y);
}

// ------- WHAT-IF SCHEDULE IMPACT -------
const impactSource = document.getElementById('impactSource');
const impactProjectSel = document.getElementById('impactProject');
const impactMult = document.getElementById('impactMult');
const impactLead = document.getElementById('impactLead');
const impactOT = document.getElementById('impactOT');
const impactTarget = document.getElementById('impactTarget'); // reserved for future
const impactInd = document.getElementById('impactInd');
const impactDel = document.getElementById('impactDel');
const impactRun = document.getElementById('impactRun');
const impactClear = document.getElementById('impactClear');
const impactResult = document.getElementById('impactResult');

function fmtDateInput(d){
  const y=d.getFullYear(); const m=String(d.getMonth()+1).padStart(2,'0'); const da=String(d.getDate()).padStart(2,'0');
  return `${y}-${m}-${da}`;
}
function addWorkdays(d, n){
  const t = new Date(d.getFullYear(), d.getMonth(), d.getDate());
  let left = Math.max(0, Math.floor(n));
  while(left>0){
    t.setDate(t.getDate()+1);
    const dow=t.getDay(); if(dow>=1 && dow<=5) left--;
  }
  return t;
}
function maxDate(a,b){ return (a>b) ? a : b; }
function minDate(a,b){ return (a<b) ? a : b; }
function impactSourceProjects(){
  const src = impactSource.value;
  return (src==='potential') ? potentialProjects : projects;
}
function setImpactProjects(){
  const src = impactSource.value;
  const arr = (src==='manual') ? [] : impactSourceProjects();
  impactProjectSel.innerHTML = "";
  if(src!=='manual'){
    arr.forEach((p, i)=>{
      const label = `${p.number || '—'} — ${p.customer || 'Unknown'}`;
      const opt = document.createElement('option');
      opt.value = String(i); opt.textContent = label;
      impactProjectSel.appendChild(opt);
    });
    if(arr.length){
      const p = arr[0];
      impactInd.value = p?.induction ? String(p.induction).slice(0,10) : "";
      impactDel.value = p?.delivery ? String(p.delivery).slice(0,10) : "";
    } else {
      impactInd.value = ""; impactDel.value = "";
    }
  }
  // toggle manual box visibility
  document.getElementById('manualBox').style.display = (src==='manual') ? 'block' : 'none';
  // disable project dropdown if manual
  impactProjectSel.disabled = (src==='manual');
}
impactSource.addEventListener('change', setImpactProjects);
impactProjectSel.addEventListener('change', ()=>{
  const arr = impactSourceProjects();
  const p = arr[Number(impactProjectSel.value)||0];
  if(!p) return;
  impactInd.value = p?.induction ? String(p.induction).slice(0,10) : "";
  impactDel.value = p?.delivery ? String(p.delivery).slice(0,10) : "";
});

// Build manual hours fields based on departments
(function buildManualHours(){
  const wrap = document.getElementById('manualHours');
  wrap.innerHTML = "";
  departmentCapacities.forEach(d=>{
    const lbl = document.createElement('label');
    lbl.innerHTML = `${d.name} hours <input type="number" step="1" min="0" id="mH_${d.key}" value="0">`;
    wrap.appendChild(lbl);
  });
  // default manual dates to two weeks from today and +10 workdays
  const today = new Date();
  const ind = addWorkdays(today, 10);
  const del = addWorkdays(ind, 10);
  document.getElementById('mInd').value = fmtDateInput(ind);
  document.getElementById('mDel').value = fmtDateInput(del);
})();

setImpactProjects();

// Compute capacity per day for a department
function capPerDay(key, overtimePct){
  const dept = departmentCapacities.find(x=>x.key===key);
  const perWeek = (dept?.headcount||0) * HOURS_PER_FTE * PRODUCTIVITY_FACTOR;
  const uplift = 1 + Math.max(0, (parseFloat(overtimePct)||0))/100;
  return (perWeek * uplift) / 5.0;
}
function baselineSeries(period, key){
  const mapC = (period==='weekly') ? dataWConfirmed : dataMConfirmed;
  return (mapC[key]?.series || []).slice();
}
function periodRange(period, labels, start, end){
  let s=-1, e=-1;
  for(let i=0;i<labels.length;i++){
    const L=parseDateLocalISO(labels[i]);
    const Pstart = (period==='weekly') ? mondayOf(L) : firstOfMonth(L);
    const Pend   = (period==='weekly') ? new Date(Pstart.getFullYear(), Pstart.getMonth(), Pstart.getDate()+6) : lastOfMonth(L);
    if(s===-1 && Pend>=start) s=i;
    if(Pstart<=end) e=i;
  }
  if(s===-1 || e===-1 || e<s) return null;
  return {s,e};
}
function projectHoursSeries(period, key, proj, mult, labels){
  const total = new Array(labels.length).fill(0);
  const hrs = (proj[key]||0) * (mult||1);
  if(hrs<=0) return total;

  const a = parseDateLocalISO( proj.__ind || proj.induction );
  const b = parseDateLocalISO( proj.__del || proj.delivery  );
  if(isNaN(a)||isNaN(b) || b<a) return total;

  if(period==='weekly'){
    const rng = periodRange('weekly', labels, a, b);
    if(!rng) return total;
    const n = rng.e - rng.s + 1; const per = hrs / n;
    for(let i=rng.s;i<=rng.e;i++){ total[i]+=per; }
  } else {
    for(let i=0;i<labels.length;i++){
      const mStart=parseDateLocalISO(labels[i]);
      const mEnd=lastOfMonth(mStart);
      const ovS = maxDate(mStart, a), ovE = minDate(mEnd, b);
      if(ovE>=ovS){
        const projWD = workdaysInclusive(a,b);
        const monWD  = workdaysInclusive(ovS,ovE);
        const share  = projWD>0 ? (monWD/projWD) : 0;
        total[i] += hrs*share;
      }
    }
  }
  return total;
}
function sumHeadroom(period, key, start, end, overtimePct){
  const labels = (period==='weekly') ? weekLabels : monthLabels;
  const cap = capacityArray(key, labels, period);
  const base = baselineSeries(period, key);
  const uplift = 1 + Math.max(0,(parseFloat(overtimePct)||0))/100;
  const rng = periodRange(period, labels, start, end);
  if(!rng) return 0;
  let sum = 0;
  for(let i=rng.s;i<=rng.e;i++){
    const hr = Math.max(0, cap[i]*uplift - (base[i]||0));
    sum += hr;
  }
  return sum;
}
function renderImpactResult(obj){
  const {earliestStart, targetStart, targetEnd, newEnd, slipDays, rows} = obj;
  const dfmt = d=>fmtDateInput(d);
  let html = `
    <div><strong>Earliest allowable induction:</strong> ${dfmt(earliestStart)}</div>
    <div><strong>Requested induction:</strong> ${dfmt(targetStart)}</div>
    <div><strong>Requested delivery:</strong> ${dfmt(targetEnd)}</div>
    <div><strong>New delivery (what-if):</strong> ${dfmt(newEnd)} <em>${slipDays>0?`(+${slipDays} workdays)`:''}</em></div>
    <table class="impact-table">
      <thead><tr><th>Department</th><th>Proj Hours</th><th>Headroom</th><th>Shortfall</th><th>Slip (wd)</th></tr></thead>
      <tbody>
        ${rows.map(r=>`<tr>
          <td>${r.name}</td>
          <td>${r.h.toFixed(0)}</td>
          <td>${r.head.toFixed(0)}</td>
          <td style="color:${r.short>0?'#b91c1c':'#065f46'};">${r.short>0?(''+r.short.toFixed(0)):'0'}</td>
          <td><strong>${r.slip}</strong></td>
        </tr>`).join('')}
      </tbody>
    </table>
  `;
  impactResult.innerHTML = html;

  // annotate on main chart
  const startLbl = (currentPeriod==='weekly') ? ymd(mondayOf(earliestStart)) : ymd(firstOfMonth(earliestStart));
  const endLbl   = (currentPeriod==='weekly') ? ymd(mondayOf(newEnd))       : ymd(firstOfMonth(newEnd));
  chart.options.plugins.annotation.annotations.whatIfStart = {
    type:'line', xMin:startLbl, xMax:startLbl, borderColor:'#2563eb', borderWidth:2,
    label:{display:true, content:'What-If Start', position:'start', backgroundColor:'rgba(37,99,235,0.1)', color:'#2563eb'}
  };
  chart.options.plugins.annotation.annotations.whatIfEnd = {
    type:'line', xMin:endLbl, xMax:endLbl, borderColor:'#7c3aed', borderWidth:2,
    label:{display:true, content:'What-If End', position:'end', backgroundColor:'rgba(124,58,237,0.1)', color:'#7c3aed'}
  };
  chart.update();
}
impactRun.addEventListener('click', ()=>{
  const src = impactSource.value;

  let proj = null;
  if(src==='manual'){
    proj = { number: document.getElementById('mNum').value || 'Manual',
             customer: document.getElementById('mCust').value || '—',
             induction: document.getElementById('mInd').value,
             delivery:  document.getElementById('mDel').value };
    // collect manual hours
    departmentCapacities.forEach(d=>{
      const v = parseFloat(document.getElementById('mH_'+d.key).value||'0')||0;
      proj[d.key] = v;
    });
  } else {
    const arr = impactSourceProjects();
    const idx = Number(impactProjectSel.value)||0;
    proj = arr[idx];
  }
  if(!proj){ impactResult.textContent = "No project selected."; return; }

  const mult = Math.max(0, parseFloat(impactMult.value||'1')||1);
  const minLead = Math.max(0, parseInt(impactLead.value||'0',10)||0);
  const otPct = Math.max(0, parseFloat(impactOT.value||'0')||0);

  const rawStart = parseDateLocalISO(impactInd.value ? impactInd.value : (proj.__ind || proj.induction));
  const rawEnd   = parseDateLocalISO(impactDel.value ? impactDel.value : (proj.__del || proj.delivery));
  if(isNaN(rawStart) || isNaN(rawEnd) || rawEnd<rawStart){
    impactResult.textContent = "Invalid induction/delivery dates."; return;
  }

  const today = new Date();
  const leadReady = addWorkdays(today, minLead);
  const earliestStart = maxDate(rawStart, leadReady);
  const targetStart = rawStart;
  const targetEnd   = rawEnd;

  const rows = [];
  let overallSlip = 0;

  departmentCapacities.forEach(d=>{
    const key = d.key;
    const name = d.name;
    const capDay = capPerDay(key, otPct);

    const H = (proj[key]||0)*mult;

    const head = sumHeadroom(currentPeriod, key, earliestStart, targetEnd, otPct);

    let short = Math.max(0, H - head);
    let slip = (short>0 && capDay>0) ? Math.ceil(short / capDay) : 0;

    overallSlip = Math.max(overallSlip, slip);
    rows.push({name, h:H, head, short, slip});
  });

  const newEnd = addWorkdays(targetEnd, overallSlip);

  renderImpactResult({
    earliestStart, targetStart, targetEnd, newEnd, slipDays: overallSlip, rows
  });
});
impactClear.addEventListener('click', ()=>{
  delete chart.options.plugins.annotation.annotations.whatIfStart;
  delete chart.options.plugins.annotation.annotations.whatIfEnd;
  chart.update();
  impactResult.innerHTML = "";
});

// initial render
refreshDatasets();
rebuildUtilChart();
</script>
</body>
</html>
"""

# Inject live data
html_code = (
    html_template
      .replace("__PROJECTS__", json.dumps(st.session_state.projects))
      .replace("__POTENTIAL__", json.dumps(st.session_state.potential))
      .replace("__ACTUAL__", json.dumps(st.session_state.actual))
      .replace("__DEPTS__", json.dumps(st.session_state.depts))
)

# Taller iframe; no inner scroll (prevents double scrollbars)
components.html(html_code, height=2100, scrolling=False)
