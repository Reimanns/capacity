import json
from datetime import date
from copy import deepcopy

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

st.set_page_config(layout="wide", page_title="Labor Capacity Dashboard")
st.image("citadel_logo.png", width=200)

# --------------------- DEFAULT DATA (YOUR NEW SET) ---------------------
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
DEFAULT_ACTUAL = []  # no "actual" provided; keep empty
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

# Which hour columns exist (used by Quick Edit)
DEPT_KEYS = ["Maintenance","Structures","Avionics","Inspection","Interiors","Engineering","Cabinet","Upholstery","Finish"]

# --------------------- SESSION STATE ---------------------
if "projects" not in st.session_state:
    st.session_state.projects = deepcopy(DEFAULT_PROJECTS)
if "potential" not in st.session_state:
    st.session_state.potential = deepcopy(DEFAULT_POTENTIAL)
if "actual" not in st.session_state:
    st.session_state.actual = deepcopy(DEFAULT_ACTUAL)
if "depts" not in st.session_state:
    st.session_state.depts = deepcopy(DEFAULT_DEPTS)

# --------------------- SIDEBAR: QUICK EDIT ---------------------
st.sidebar.header("Quick Edit")
dataset_choice = st.sidebar.selectbox("Dataset to modify", ["Confirmed","Potential","Actual"])
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
        hours_inputs = {k: st.number_input(f"{k} hours", min_value=0.0, value=0.0, step=1.0) for k in DEPT_KEYS}
    else:
        idx = project_ids.index(select_existing)
        proj = deepcopy(current_list[idx])
        number = st.text_input("Project Number", str(proj.get("number") or ""))
        customer = st.text_input("Customer", str(proj.get("customer") or ""))
        aircraft = st.text_input("Aircraft Model", str(proj.get("aircraftModel") or ""))
        scope = st.text_input("Scope", str(proj.get("scope") or ""))
        # support ISO strings with time
        induction = st.date_input("Induction", date.fromisoformat(str(proj["induction"])[:10])).isoformat()
        delivery  = st.date_input("Delivery",  date.fromisoformat(str(proj["delivery"])[:10])).isoformat()
        hours_inputs = {
            k: st.number_input(f"{k} hours", min_value=0.0, value=float(proj.get(k, 0) or 0), step=1.0)
            for k in DEPT_KEYS
        }

    colA, colB = st.columns(2)
    with colA:
        apply_btn = st.form_submit_button("Apply Changes", use_container_width=True)
    with colB:
        reset_btn = st.form_submit_button("Reset to Defaults", use_container_width=True)

if apply_btn:
    entry = {
        "number": number.strip(),
        "customer": customer.strip(),
        "aircraftModel": aircraft.strip(),
        "scope": scope.strip(),
        "induction": induction,
        "delivery": delivery,
    }
    for k in DEPT_KEYS:
        entry[k] = float(hours_inputs[k] or 0.0)

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

# --------------------- MAIN: BULK EDIT + SAVE/LOAD ---------------------
with st.expander("Bulk Edit: Confirmed / Potential / Actual", expanded=False):
    c1, c2, c3 = st.columns(3)
    with c1:
        df_proj = st.data_editor(pd.DataFrame(st.session_state.projects), key="ed_confirmed", height=350)
        st.session_state.projects = df_proj.astype(object).to_dict(orient="records")
    with c2:
        df_pot = st.data_editor(pd.DataFrame(st.session_state.potential), key="ed_potential", height=350)
        st.session_state.potential = df_pot.astype(object).to_dict(orient="records")
    with c3:
        df_act = st.data_editor(pd.DataFrame(st.session_state.actual), key="ed_actual", height=350)
        st.session_state.actual = df_act.astype(object).to_dict(orient="records")

with st.expander("Edit Department Headcounts", expanded=False):
    df_depts = st.data_editor(pd.DataFrame(st.session_state.depts), key="ed_depts", height=240)
    df_depts["headcount"] = pd.to_numeric(df_depts["headcount"], errors="coerce").fillna(0).astype(int)
    st.session_state.depts = df_depts.to_dict(orient="records")

st.markdown("---")

# --------------------- BUILD HTML (JS gets live data) ---------------------
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
    body { font-family: Arial, sans-serif; margin: 8px 20px 24px; }
    h1 { text-align:center; margin: 6px 0 4px; }
    .controls { display:flex; gap:16px; flex-wrap:wrap; align-items:center; justify-content:center; margin: 8px auto 10px; }
    .controls label { font-size:14px; display:flex; align-items:center; gap:6px; }
    .metric-bar { display:flex; gap:16px; justify-content:center; flex-wrap:wrap; margin: 8px 0 14px; }
    .metric { border:1px solid #e5e7eb; border-radius:10px; padding:10px 14px; min-width:220px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); background:#fff; }
    .metric .label { font-size:12px; color:var(--muted); margin-bottom:4px; }
    .metric .value { font-weight:700; font-size:18px; }
    .chart-wrap { width:100%; height:620px; margin-bottom: 6px; position:relative; }
    .footnote { text-align:center; color:#6b7280; font-size:12px; }

    .modal-backdrop { display:none; position:fixed; inset:0; background:rgba(0,0,0,0.4); z-index:9998; }
    .modal { display:none; position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); background:#fff; border-radius:12px; width:min(800px,92vw); max-height:80vh; overflow:auto; z-index:9999; box-shadow:0 8px 32px rgba(0,0,0,0.2); }
    .modal header { padding:14px 16px; border-bottom:1px solid #eee; display:flex; justify-content:space-between; align-items:center;}
    .modal header h3 { margin:0; font-size:16px;}
    .modal .content { padding:12px 16px 18px; }
    .modal table { width:100%; border-collapse:collapse; }
    .modal th, .modal td { border-bottom:1px solid #eee; padding:8px; text-align:left; font-size:14px;}
    .close-btn { cursor:pointer; border:none; background:#f3f4f6; padding:6px 10px; border-radius:8px; }
  </style>
</head>
<body>

<h1>Capacity-Load By Discipline</h1>

<div class="controls">
  <label for="disciplineSelect"><strong>Discipline:</strong></label>
  <select id="disciplineSelect"></select>

  <label><input type="checkbox" id="showPotential" checked> Show Potential</label>
  <label><input type="checkbox" id="showActual"> Show Actual</label>

  <label><strong>Productivity:</strong>
    <input type="range" id="prodFactor" min="0.50" max="1.00" step="0.01" value="0.85">
    <span id="prodVal">0.85</span>
  </label>

  <label><strong>Hours / FTE / wk:</strong>
    <input type="number" id="hoursPerFTE" min="30" max="60" step="1" value="40" style="width:64px;">
  </label>
</div>

<div class="metric-bar">
  <div class="metric"><div class="label">Peak Utilization</div><div class="value" id="peakUtil">—</div></div>
  <div class="metric"><div class="label">Worst Week (Max Over/Under)</div><div class="value" id="worstWeek">—</div></div>
  <div class="metric"><div class="label">Weekly Capacity</div><div class="value" id="weeklyCap">—</div></div>
</div>

<div class="chart-wrap"><canvas id="myChart"></canvas></div>
<p class="footnote">Tip: click a line/area (Load, Potential, Actual) at any week to see customer breakdown.</p>

<div class="modal-backdrop" id="modalBackdrop"></div>
<div class="modal" id="drilldownModal">
  <header><h3 id="modalTitle">Breakdown</h3><button class="close-btn" id="closeModal">Close</button></header>
  <div class="content"><table><thead><tr><th>Customer</th><th>Hours</th></tr></thead><tbody id="modalBody"></tbody></table></div>
</div>

<script>
// ---- LIVE DATA INJECTION ----
const projects = __PROJECTS__;
const potentialProjects = __POTENTIAL__;
const projectsActual = __ACTUAL__;
const departmentCapacities = __DEPTS__;

// Defaults for in-chart controls (can be changed in UI)
let PRODUCTIVITY_FACTOR = 0.85;
let HOURS_PER_FTE = 40;

// -------------------- HELPERS --------------------
function parseDate(s){ return s && typeof s === "string" ? new Date(s) : new Date(s); }
function formatDateLocal(d){ const y=d.getFullYear(); const m=String(d.getMonth()+1).padStart(2,"0"); const da=String(d.getDate()).padStart(2,"0"); return `${y}-${m}-${da}`; }
function mondayOf(d){ const t=new Date(d); const day=(t.getDay()+6)%7; t.setDate(t.getDate()-day); t.setHours(0,0,0,0); return t; }

function getWeekList(){
  let minD=null,maxD=null;
  function expand(arr){ for(const p of arr){ const a=parseDate(p.induction), b=parseDate(p.delivery); if(!minD||a<minD)minD=a; if(!maxD||b>maxD)maxD=b; } }
  if(projects.length) expand(projects);
  if(potentialProjects.length) expand(potentialProjects);
  if(projectsActual.length) expand(projectsActual);
  if(!minD || !maxD){ const t=new Date(); const start=mondayOf(t); return [formatDateLocal(start)]; }
  const start=mondayOf(minD); const weeks=[]; const cur=new Date(start);
  while(cur<=maxD){ weeks.push(new Date(cur)); cur.setDate(cur.getDate()+7); }
  return weeks.map(formatDateLocal);
}
function computeWeeklyLoadsDetailed(arr, key, labels){
  const total=new Array(labels.length).fill(0); const breakdown=labels.map(()=>[]);
  for(const p of arr){
    const hrs=p[key]||0; if(!hrs) continue;
    const a=parseDate(p.induction), b=parseDate(p.delivery);
    let s=-1,e=-1;
    for(let i=0;i<labels.length;i++){ const L=new Date(labels[i]); if(L>=a && s===-1) s=i; if(L<=b) e=i; }
    if(s!==-1 && e!==-1 && e>=s){
      const n=e-s+1, per=hrs/n;
      for(let w=s; w<=e; w++){ total[w]+=per; breakdown[w].push({customer:(p.customer||"Unknown"), hours:per}); }
    }
  }
  return {weeklyTotal:total, breakdown};
}
function computeWeeklyLoadsActual(arr, key, labels){
  const total=new Array(labels.length).fill(0); const breakdown=labels.map(()=>[]);
  const today=new Date();
  for(const p of arr){
    const hrs=p[key]||0; if(!hrs) continue;
    const a=parseDate(p.induction), planned=parseDate(p.delivery);
    const end = (a>today) ? planned : (planned<today? planned : today);
    if(end<a) continue;
    let s=-1,e=-1;
    for(let i=0;i<labels.length;i++){ const L=new Date(labels[i]); if(L>=a && s===-1) s=i; if(L<=end) e=i; }
    if(s!==-1 && e!==-1 && e>=s){
      const n=e-s+1, per=hrs/n;
      for(let w=s; w<=e; w++){ total[w]+=per; breakdown[w].push({customer:(p.customer||"Unknown"), hours:per}); }
    }
  }
  return {weeklyTotal:total, breakdown};
}

// -------------------- PREP --------------------
const weekLabels = getWeekList();
const dataConfirmed = {};
const dataPotential = {};
const dataActual    = {};
departmentCapacities.forEach(d=>{
  const c=computeWeeklyLoadsDetailed(projects, d.key, weekLabels);
  const p=computeWeeklyLoadsDetailed(potentialProjects, d.key, weekLabels);
  const a=computeWeeklyLoadsActual(projectsActual, d.key, weekLabels);
  dataConfirmed[d.key]={name:d.name, weeklyTotal:c.weeklyTotal, breakdown:c.breakdown};
  dataPotential[d.key]={name:d.name, weeklyTotal:p.weeklyTotal, breakdown:p.breakdown};
  dataActual[d.key]   ={name:d.name, weeklyTotal:a.weeklyTotal, breakdown:a.breakdown};
});

const sel = document.getElementById('disciplineSelect');
departmentCapacities.forEach(d=>{ const o=document.createElement('option'); o.value=d.key; o.textContent=d.name; sel.appendChild(o); });
sel.value=departmentCapacities[0]?.key || "";

// -------------------- CHART --------------------
const ctx = document.getElementById('myChart').getContext('2d');
let currentKey = sel.value;
function weeklyCapacityFor(key){
  const dept = departmentCapacities.find(x=>x.key===key);
  const capPerWeek = (dept?.headcount || 0) * HOURS_PER_FTE * PRODUCTIVITY_FACTOR;
  return weekLabels.map(()=>capPerWeek);
}
function utilizationArray(key, includePotential){
  const conf = dataConfirmed[key]?.weeklyTotal || [];
  const pot  = dataPotential[key]?.weeklyTotal || [];
  const cap  = weeklyCapacityFor(key);
  return conf.map((v,i)=>{ const load = includePotential ? (v + (pot[i]||0)) : v; return cap[i] ? (100 * load / cap[i]) : 0; });
}

const todayLabel = (()=>{ const m = mondayOf(new Date()); return formatDateLocal(m); })();
const annos = { annotations:{ todayLine:{ type:'line', xMin: todayLabel, xMax: todayLabel, borderColor:'#9ca3af', borderWidth:1, borderDash:[4,4],
  label:{ display:true, content:'Today', position:'start', color:'#6b7280', backgroundColor:'rgba(255,255,255,0.8)' } } } };

let showPotential = true;
let showActual = false; // no actual data by default

let chart = new Chart(ctx,{
  type:'line',
  data:{
    labels: weekLabels,
    datasets:[
      { label: () => `${(dataConfirmed[currentKey]?.name)||'Dept'} Load (hrs)`, data: (dataConfirmed[currentKey]?.weeklyTotal)||[],
        borderColor: getComputedStyle(document.documentElement).getPropertyValue('--brand').trim(),
        backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--brand-20').trim(),
        borderWidth:2, fill:true, tension:0.1, pointRadius:0 },
      { label: () => `${(dataConfirmed[currentKey]?.name)||'Dept'} Capacity (hrs)`, data: weeklyCapacityFor(currentKey),
        borderColor: getComputedStyle(document.documentElement).getPropertyValue('--capacity').trim(),
        backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--capacity-20').trim(),
        borderWidth:2, fill:false, borderDash:[6,6], tension:0.1, pointRadius:0 },
      { label: () => `${(dataConfirmed[currentKey]?.name)||'Dept'} Potential (hrs)`, data: (dataPotential[currentKey]?.weeklyTotal)||[],
        borderColor: getComputedStyle(document.documentElement).getPropertyValue('--potential').trim(),
        backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--potential-20').trim(),
        borderWidth:2, fill:true, tension:0.1, pointRadius:0, hidden: !showPotential },
      { label: () => `${(dataConfirmed[currentKey]?.name)||'Dept'} Actual (hrs)`, data: (dataActual[currentKey]?.weeklyTotal)||[],
        borderColor: getComputedStyle(document.documentElement).getPropertyValue('--actual').trim(),
        backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--actual-20').trim(),
        borderWidth:2, fill:true, tension:0.1, pointRadius:0, hidden: !showActual },
      { label: 'Utilization %', data: utilizationArray(currentKey, showPotential),
        borderColor:'#374151', backgroundColor:'rgba(55,65,81,0.12)',
        yAxisID:'y2', borderWidth:1.5, fill:false, tension:0.1, pointRadius:0 }
    ]
  },
  options:{
    responsive:true, maintainAspectRatio:false,
    interaction:{ mode:'index', intersect:false },
    scales:{ x:{ title:{display:true, text:'Week Starting'} }, y:{ title:{display:true, text:'Hours'}, beginAtZero:true },
      y2:{ title:{display:true, text:'Utilization %'}, beginAtZero:true, position:'right', grid:{ drawOnChartArea:false }, suggestedMax:150 } },
    plugins:{ annotation: annos, legend:{ position:'top' },
      title:{ display:true, text: ()=>'Weekly Load vs. Capacity - ' + ((dataConfirmed[currentKey]?.name)||'Dept') } },
    onClick:(evt, elems)=>{
      if(!elems||!elems.length) return;
      const {datasetIndex, index:weekIndex} = elems[0];
      if(datasetIndex===1 || datasetIndex===4) return;
      let breakdownArr=null, label='';
      if(datasetIndex===0){ breakdownArr = (dataConfirmed[currentKey]?.breakdown||[])[weekIndex]; label='Confirmed'; }
      else if(datasetIndex===2){ breakdownArr = (dataPotential[currentKey]?.breakdown||[])[weekIndex]; label='Potential'; }
      else if(datasetIndex===3){ breakdownArr = (dataActual[currentKey]?.breakdown||[])[weekIndex]; label='Actual'; }
      if(!breakdownArr || breakdownArr.length===0){ openModal(`No ${label} hours in week ${weekLabels[weekIndex]}.`, []); return; }
      openModal(`Week ${weekLabels[weekIndex]} · ${(dataConfirmed[currentKey]?.name)||'Dept'} · ${label}`, breakdownArr);
    }
  }
});

// -------------------- KPIs + UI --------------------
const prodSlider = document.getElementById('prodFactor');
const prodVal = document.getElementById('prodVal');
const hoursInput = document.getElementById('hoursPerFTE');
const chkPot = document.getElementById('showPotential');
const chkAct = document.getElementById('showActual');

function refreshDatasets(){
  chart.data.datasets[1].data = weeklyCapacityFor(currentKey);
  chart.data.datasets[2].hidden = !showPotential;
  chart.data.datasets[3].hidden = !showActual;
  chart.data.datasets[4].data = utilizationArray(currentKey, showPotential);
  chart.options.plugins.title.text = 'Weekly Load vs. Capacity - ' + ((dataConfirmed[currentKey]?.name)||'Dept');
  chart.update();
  updateKPIs();
}
function updateKPIs(){
  const cap = weeklyCapacityFor(currentKey)[0] || 0;
  const conf = (dataConfirmed[currentKey]?.weeklyTotal)||[];
  const pot  = (dataPotential[currentKey]?.weeklyTotal)||[];
  const combined = conf.map((v,i)=> v + (showPotential ? (pot[i]||0) : 0));
  let peak=0, peakIdx=0, worstDiff=-Infinity, worstIdx=0;
  for(let i=0;i<combined.length;i++){
    const u = cap? (combined[i]/cap*100):0;
    if(u>peak){ peak=u; peakIdx=i; }
    const diff = combined[i] - cap;
    if(diff>worstDiff){ worstDiff=diff; worstIdx=i; }
  }
  document.getElementById('peakUtil').textContent = combined.length? `${peak.toFixed(0)}% (wk ${weekLabels[peakIdx]})` : '—';
  const status = worstDiff>=0 ? `+${isFinite(worstDiff)?worstDiff.toFixed(0):0} hrs over` : `${isFinite(worstDiff)?(-worstDiff).toFixed(0):0} hrs under`;
  document.getElementById('worstWeek').textContent = combined.length? `${weekLabels[worstIdx]} · ${status}` : '—';
  document.getElementById('weeklyCap').textContent = `${cap.toFixed(0)} hrs / wk`;
}

sel.addEventListener('change', e=>{
  currentKey = e.target.value;
  chart.data.datasets[0].label = `${(dataConfirmed[currentKey]?.name)||'Dept'} Load (hrs)`;
  chart.data.datasets[0].data  = (dataConfirmed[currentKey]?.weeklyTotal)||[];
  chart.data.datasets[1].label = `${(dataConfirmed[currentKey]?.name)||'Dept'} Capacity (hrs)`;
  chart.data.datasets[2].label = `${(dataConfirmed[currentKey]?.name)||'Dept'} Potential (hrs)`;
  chart.data.datasets[3].label = `${(dataConfirmed[currentKey]?.name)||'Dept'} Actual (hrs)`;
  refreshDatasets();
});
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

// -------------------- Modal --------------------
const backdrop = document.getElementById('modalBackdrop');
const modal = document.getElementById('drilldownModal');
const modalTitle = document.getElementById('modalTitle');
const modalBody = document.getElementById('modalBody');
document.getElementById('closeModal').addEventListener('click', closeModal);
backdrop.addEventListener('click', closeModal);

function openModal(title, rows){
  modalTitle.textContent = title;
  modalBody.innerHTML = rows.map(r=>`<tr><td>${r.customer}</td><td>${r.hours.toFixed(1)}</td></tr>`).join('') || `<tr><td colspan="2">No data</td></tr>`;
  backdrop.style.display='block'; modal.style.display='block';
}
function closeModal(){ backdrop.style.display='none'; modal.style.display='none'; }

refreshDatasets();
</script>
</body>
</html>
"""

# Inject the live data into the HTML
html_code = (
    html_template
      .replace("__PROJECTS__", json.dumps(st.session_state.projects))
      .replace("__POTENTIAL__", json.dumps(st.session_state.potential))
      .replace("__ACTUAL__", json.dumps(st.session_state.actual))
      .replace("__DEPTS__", json.dumps(st.session_state.depts))
)

components.html(html_code, height=900, scrolling=True)
