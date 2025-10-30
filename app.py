import json
from datetime import date
from copy import deepcopy

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

st.set_page_config(layout="wide", page_title="Labor Capacity Dashboard")
st.image("citadel_logo.png", width=200)

# --------------------- DEFAULT DATA ---------------------
DEFAULT_PROJECTS = [
  {"number":"P7578","customer":"ADFAM","aircraftModel":"A340","scope":"Center Gear Replacement","induction":"2025-02-10","delivery":"2025-02-17","Maintenance":688,"Interiors":0,"Avionics":0,"SheetMetal":0,"FinishPaint":0,"Engineering":0,"Upholstery":0,"Cabinetry":0},
  {"number":"P7476","customer":"GE","aircraftModel":"747-400","scope":"Multi Check, AD's & SB's","induction":"2025-02-18","delivery":"2025-04-03","Maintenance":4955,"Interiors":100,"Avionics":0,"SheetMetal":0,"FinishPaint":0,"Engineering":0,"Upholstery":0,"Cabinetry":0},
  {"number":"P7591","customer":"Freedom II","aircraftModel":"757-200","scope":"B Check, AD's & SB's","induction":"2025-02-23","delivery":"2025-03-02","Maintenance":871.5,"Interiors":0,"Avionics":0,"SheetMetal":0,"FinishPaint":0,"Engineering":0,"Upholstery":0,"Cabinetry":0},
  {"number":"P7560","customer":"BEFO","aircraftModel":"737","scope":"96mnth Check","induction":"2025-03-23","delivery":"2025-06-15","Maintenance":4038,"Interiors":1921,"Avionics":0,"SheetMetal":0,"FinishPaint":0,"Engineering":8,"Upholstery":14,"Cabinetry":0},
  {"number":"P7517","customer":"Parallel","aircraftModel":"757-200","scope":"Interior Mod","induction":"2025-04-15","delivery":"2025-08-31","Maintenance":584,"Interiors":5997,"Avionics":7114,"SheetMetal":1885,"FinishPaint":4920,"Engineering":0,"Upholstery":6885,"Cabinetry":2272},
  {"number":"P7561","customer":"L3-FBI","aircraftModel":"757-200","scope":"Maintenance & Interior Mod","induction":"2025-07-31","delivery":"2025-10-14","Maintenance":6882,"Interiors":1029,"Avionics":276,"SheetMetal":90,"FinishPaint":116,"Engineering":244,"Upholstery":0,"Cabinetry":228},
  {"number":"P7426","customer":"Celestial","aircraftModel":"757","scope":"Maintenance & Interior Mod","induction":"2025-02-06","delivery":"2025-03-28","Maintenance":0,"Interiors":2840,"Avionics":0,"SheetMetal":0,"FinishPaint":953,"Engineering":0,"Upholstery":1025,"Cabinetry":100},
  {"number":"P7592","customer":"LJ Aviation","aircraftModel":"","scope":"GOGO WAP","induction":"2025-02-23","delivery":"2025-03-06","Maintenance":0,"Interiors":0,"Avionics":0,"SheetMetal":0,"FinishPaint":0,"Engineering":0,"Upholstery":0,"Cabinetry":0},
  {"number":"P7392","customer":"L3-FBI","aircraftModel":"757","scope":"Maintenance & Interior Mod","induction":"2025-05-01","delivery":"2025-06-01","Maintenance":0,"Interiors":695,"Avionics":300,"SheetMetal":90,"FinishPaint":16,"Engineering":220,"Upholstery":0,"Cabinetry":240}
]
DEFAULT_POTENTIAL = [
  {"number":"P7580","customer":"Polaris","aircraftModel":"B737","scope":"144 Mo. Check","induction":"2025-09-01","delivery":"2025-11-10","Maintenance":4162,"Interiors":3783,"Avionics":1135,"SheetMetal":2270,"FinishPaint":0,"Engineering":0,"Upholstery":0,"Cabinetry":0},
  {"number":"P7560","customer":"BEFO","aircraftModel":"737","scope":"Additional Interior Work","induction":"2025-03-23","delivery":"2025-05-23","Maintenance":0,"Interiors":103,"Avionics":8,"SheetMetal":0,"FinishPaint":0,"Engineering":8,"Upholstery":14,"Cabinetry":0}
]
DEFAULT_ACTUAL = [
  {"number":"P7578","customer":"ADFAM","aircraftModel":"A340","scope":"Center Gear Replacement","induction":"2025-02-10","delivery":"2025-02-17","Maintenance":458.9,"Interiors":5.59,"Avionics":0,"SheetMetal":107.37,"FinishPaint":0,"Engineering":0,"Upholstery":0,"Cabinetry":0},
  {"number":"P7476","customer":"GE","aircraftModel":"747-400","scope":"Multi Check, AD's & SB's","induction":"2025-02-18","delivery":"2025-04-03","Maintenance":391.71,"Interiors":355.79,"Avionics":110.46,"SheetMetal":175.23,"FinishPaint":0,"Engineering":0,"Upholstery":574.34,"Cabinetry":0},
  {"number":"P7591","customer":"Freedom II","aircraftModel":"757-200","scope":"B Check, AD's & SB's","induction":"2025-02-23","delivery":"2025-03-02","Maintenance":220.56,"Interiors":23.42,"Avionics":55.82,"SheetMetal":58.39,"FinishPaint":0,"Engineering":0,"Upholstery":17.22,"Cabinetry":25.02},
  {"number":"P7560","customer":"BEFO","aircraftModel":"737","scope":"96mnth Check","induction":"2025-03-23","delivery":"2025-06-15","Maintenance":0,"Interiors":0,"Avionics":0,"SheetMetal":0,"FinishPaint":0,"Engineering":0,"Upholstery":0,"Cabinetry":0},
  {"number":"P7517","customer":"Parallel","aircraftModel":"757-200","scope":"Interior Mod","induction":"2025-04-15","delivery":"2025-08-31","Maintenance":140.97,"Interiors":309.74,"Avionics":438,"SheetMetal":12.32,"FinishPaint":89.67,"Engineering":0,"Upholstery":912.77,"Cabinetry":123.05},
  {"number":"P7561","customer":"L3-FBI","aircraftModel":"757-200","scope":"Maintenance & Interior Mod","induction":"2025-07-31","delivery":"2025-10-14","Maintenance":0,"Interiors":0,"Avionics":0,"SheetMetal":0,"FinishPaint":0,"Engineering":0,"Upholstery":0,"Cabinetry":0},
  {"number":"P7426","customer":"Celestial","aircraftModel":"757","scope":"Maintenance & Interior Mod","induction":"2025-02-06","delivery":"2025-03-28","Maintenance":2032.27,"Interiors":3769.69,"Avionics":3.61,"SheetMetal":1043.93,"FinishPaint":384.49,"Engineering":0,"Upholstery":948.44,"Cabinetry":116.5},
  {"number":"P7592","customer":"LJ Aviation","aircraftModel":"","scope":"GOGO WAP","induction":"2025-02-23","delivery":"2025-03-06","Maintenance":0,"Interiors":0,"Avionics":125.73,"SheetMetal":0,"FinishPaint":0,"Engineering":0,"Upholstery":0,"Cabinetry":0},
  {"number":"P7392","customer":"L3-FBI","aircraftModel":"757","scope":"Maintenance & Interior Mod","induction":"2025-05-01","delivery":"2025-06-01","Maintenance":0,"Interiors":27.13,"Avionics":0,"SheetMetal":0,"FinishPaint":0,"Engineering":0,"Upholstery":0,"Cabinetry":0}
]
DEFAULT_DEPTS = [
  {"name":"Interiors","headcount":14,"key":"Interiors"},
  {"name":"Finish","headcount":4,"key":"FinishPaint"},
  {"name":"Cabinetry","headcount":2,"key":"Cabinetry"},
  {"name":"Upholstery","headcount":6,"key":"Upholstery"},
  {"name":"Avionics","headcount":7,"key":"Avionics"},
  {"name":"Sheet Metal","headcount":10,"key":"SheetMetal"},
  {"name":"Engineering","headcount":3,"key":"Engineering"}
]
DEPT_KEYS = ["Maintenance","Interiors","Avionics","SheetMetal","FinishPaint","Engineering","Upholstery","Cabinetry"]

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
st.sidebar.header("Quick Edit (fast changes during meeting)")
dataset_choice = st.sidebar.selectbox("Dataset to modify", ["Confirmed","Potential","Actual"])
dataset_key = {"Confirmed":"projects","Potential":"potential","Actual":"actual"}[dataset_choice]
current_list = st.session_state[dataset_key]

project_ids = [f'{p["number"]} — {p["customer"]}' for p in current_list]
select_existing = st.sidebar.selectbox("Project", ["➕ New Project"] + project_ids)

with st.sidebar.form("quick_edit"):
    if select_existing == "➕ New Project":
        number = st.text_input("Project Number", "PXXXX")
        customer = st.text_input("Customer", "")
        aircraft = st.text_input("Aircraft Model", "")
        scope = st.text_input("Scope", "")
        induction = st.date_input("Induction", date(2025, 1, 1)).isoformat()
        delivery = st.date_input("Delivery", date(2025, 1, 8)).isoformat()
        hours_inputs = {}
        for k in DEPT_KEYS:
            hours_inputs[k] = st.number_input(f"{k} hours", min_value=0.0, value=0.0, step=1.0)
    else:
        idx = project_ids.index(select_existing)
        proj = deepcopy(current_list[idx])
        number = st.text_input("Project Number", proj["number"])
        customer = st.text_input("Customer", proj["customer"])
        aircraft = st.text_input("Aircraft Model", proj.get("aircraftModel",""))
        scope = st.text_input("Scope", proj.get("scope",""))
        # accept both iso and "YYYY-MM-DD" strings
        induction = st.date_input("Induction", date.fromisoformat(proj["induction"])).isoformat()
        delivery  = st.date_input("Delivery",  date.fromisoformat(proj["delivery"])).isoformat()
        hours_inputs = {}
        for k in DEPT_KEYS:
            hours_inputs[k] = st.number_input(f"{k} hours", min_value=0.0, value=float(proj.get(k,0) or 0), step=1.0)

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
        st.session_state.projects = df_proj.fillna(0).astype(object).to_dict(orient="records")
    with c2:
        df_pot = st.data_editor(pd.DataFrame(st.session_state.potential), key="ed_potential", height=350)
        st.session_state.potential = df_pot.fillna(0).astype(object).to_dict(orient="records")
    with c3:
        df_act = st.data_editor(pd.DataFrame(st.session_state.actual), key="ed_actual", height=350)
        st.session_state.actual = df_act.fillna(0).astype(object).to_dict(orient="records")

with st.expander("Edit Department Headcounts", expanded=False):
    df_depts = st.data_editor(pd.DataFrame(st.session_state.depts), key="ed_depts", height=200)
    # Ensure headcount numeric
    df_depts["headcount"] = pd.to_numeric(df_depts["headcount"], errors="coerce").fillna(0).astype(int)
    st.session_state.depts = df_depts.to_dict(orient="records")

with st.expander("Save / Load Data", expanded=False):
    bundle = {
        "projects": st.session_state.projects,
        "potential": st.session_state.potential,
        "actual": st.session_state.actual,
        "departments": st.session_state.depts,
    }
    st.download_button(
        "Download current data (JSON)",
        data=json.dumps(bundle, indent=2),
        file_name="capacity_data.json",
        mime="application/json",
        use_container_width=True
    )
    uploaded = st.file_uploader("Load data (JSON bundle)", type=["json"])
    if uploaded:
        try:
            loaded = json.load(uploaded)
            st.session_state.projects  = loaded.get("projects", st.session_state.projects)
            st.session_state.potential = loaded.get("potential", st.session_state.potential)
            st.session_state.actual    = loaded.get("actual", st.session_state.actual)
            st.session_state.depts     = loaded.get("departments", st.session_state.depts)
            st.success("Data loaded into the app.")
        except Exception as e:
            st.error(f"Failed to load JSON: {e}")

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
  <label><input type="checkbox" id="showActual" checked> Show Actual</label>

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
function parseDate(s){ return s.includes("/") ? (()=>{const [m,d,y]=s.split("/");return new Date(+y,+m-1,+d)})() : new Date(s); }
function formatDateLocal(d){ const y=d.getFullYear(); const m=String(d.getMonth()+1).padStart(2,"0"); const da=String(d.getDate()).padStart(2,"0"); return `${y}-${m}-${da}`; }
function mondayOf(d){ const t=new Date(d); const day=(t.getDay()+6)%7; t.setDate(t.getDate()-day); t.setHours(0,0,0,0); return t; }

function getWeekList(){
  let minD=null,maxD=null;
  function expand(arr){ for(const p of arr){ const a=parseDate(p.induction), b=parseDate(p.delivery); if(!minD||a<minD)minD=a; if(!maxD||b>maxD)maxD=b; } }
  expand(projects); expand(potentialProjects); expand(projectsActual);
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
      for(let w=s; w<=e; w++){ total[w]+=per; breakdown[w].push({customer:p.customer, hours:per}); }
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
      for(let w=s; w<=e; w++){ total[w]+=per; breakdown[w].push({customer:p.customer, hours:per}); }
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
sel.value="Interiors";

// -------------------- CHART --------------------
const ctx = document.getElementById('myChart').getContext('2d');
let currentKey = sel.value;
function weeklyCapacityFor(key){
  const dept = departmentCapacities.find(x=>x.key===key);
  const capPerWeek = dept.headcount * HOURS_PER_FTE * PRODUCTIVITY_FACTOR;
  return weekLabels.map(()=>capPerWeek);
}
function utilizationArray(key, includePotential){
  const conf = dataConfirmed[key].weeklyTotal;
  const pot  = dataPotential[key].weeklyTotal;
  const cap  = weeklyCapacityFor(key);
  return conf.map((v,i)=>{ const load = includePotential ? (v + pot[i]) : v; return cap[i] ? (100 * load / cap[i]) : 0; });
}

const todayLabel = (()=>{ const m = mondayOf(new Date()); return formatDateLocal(m); })();
const annos = { annotations:{ todayLine:{ type:'line', xMin: todayLabel, xMax: todayLabel, borderColor:'#9ca3af', borderWidth:1, borderDash:[4,4],
  label:{ display:true, content:'Today', position:'start', color:'#6b7280', backgroundColor:'rgba(255,255,255,0.8)' } } } };

let showPotential = true;
let showActual = true;

let chart = new Chart(ctx,{
  type:'line',
  data:{
    labels: weekLabels,
    datasets:[
      { label: () => `${dataConfirmed[currentKey].name} Load (hrs)`, data: dataConfirmed[currentKey].weeklyTotal,
        borderColor: getComputedStyle(document.documentElement).getPropertyValue('--brand').trim(),
        backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--brand-20').trim(),
        borderWidth:2, fill:true, tension:0.1, pointRadius:0 },
      { label: () => `${dataConfirmed[currentKey].name} Capacity (hrs)`, data: weeklyCapacityFor(currentKey),
        borderColor: getComputedStyle(document.documentElement).getPropertyValue('--capacity').trim(),
        backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--capacity-20').trim(),
        borderWidth:2, fill:false, borderDash:[6,6], tension:0.1, pointRadius:0 },
      { label: () => `${dataConfirmed[currentKey].name} Potential (hrs)`, data: dataPotential[currentKey].weeklyTotal,
        borderColor: getComputedStyle(document.documentElement).getPropertyValue('--potential').trim(),
        backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--potential-20').trim(),
        borderWidth:2, fill:true, tension:0.1, pointRadius:0, hidden: !showPotential },
      { label: () => `${dataConfirmed[currentKey].name} Actual (hrs)`, data: dataActual[currentKey].weeklyTotal,
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
      title:{ display:true, text: ()=>'Weekly Load vs. Capacity - ' + dataConfirmed[currentKey].name } },
    onClick:(evt, elems)=>{
      if(!elems||!elems.length) return;
      const {datasetIndex, index:weekIndex} = elems[0];
      if(datasetIndex===1 || datasetIndex===4) return;
      let breakdownArr=null, label='';
      if(datasetIndex===0){ breakdownArr = dataConfirmed[currentKey].breakdown[weekIndex]; label='Confirmed'; }
      else if(datasetIndex===2){ breakdownArr = dataPotential[currentKey].breakdown[weekIndex]; label='Potential'; }
      else if(datasetIndex===3){ breakdownArr = dataActual[currentKey].breakdown[weekIndex]; label='Actual'; }
      if(!breakdownArr || breakdownArr.length===0){ openModal(`No ${label} hours in week ${weekLabels[weekIndex]}.`, []); return; }
      openModal(`Week ${weekLabels[weekIndex]} · ${dataConfirmed[currentKey].name} · ${label}`, breakdownArr);
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
  chart.options.plugins.title.text = 'Weekly Load vs. Capacity - ' + dataConfirmed[currentKey].name;
  chart.update();
  updateKPIs();
}
function updateKPIs(){
  const cap = weeklyCapacityFor(currentKey)[0] || 0;
  const conf = dataConfirmed[currentKey].weeklyTotal;
  const pot  = dataPotential[currentKey].weeklyTotal;
  const combined = conf.map((v,i)=> v + (showPotential ? pot[i] : 0));
  let peak=0, peakIdx=0;
  for(let i=0;i<combined.length;i++){ const u = cap? (combined[i]/cap*100):0; if(u>peak){ peak=u; peakIdx=i; } }
  let worstDiff = -Infinity, worstIdx = 0;
  for(let i=0;i<combined.length;i++){ const diff = combined[i] - cap; if(diff>worstDiff){ worstDiff=diff; worstIdx=i; } }
  document.getElementById('peakUtil').textContent = `${peak.toFixed(0)}% (wk ${weekLabels[peakIdx]})`;
  const status = worstDiff>=0 ? `+${worstDiff.toFixed(0)} hrs over` : `${(-worstDiff).toFixed(0)} hrs under`;
  document.getElementById('worstWeek').textContent = `${weekLabels[worstIdx]} · ${status}`;
  document.getElementById('weeklyCap').textContent = `${cap.toFixed(0)} hrs / wk`;
}

sel.addEventListener('change', e=>{
  currentKey = e.target.value;
  chart.data.datasets[0].label = `${dataConfirmed[currentKey].name} Load (hrs)`;
  chart.data.datasets[0].data  = dataConfirmed[currentKey].weeklyTotal;
  chart.data.datasets[1].label = `${dataConfirmed[currentKey].name} Capacity (hrs)`;
  chart.data.datasets[2].label = `${dataConfirmed[currentKey].name} Potential (hrs)`;
  chart.data.datasets[3].label = `${dataConfirmed[currentKey].name} Actual (hrs)`;
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

# Inject the live data into the HTML (avoid f-string brace issues)
html_code = (
    html_template
      .replace("__PROJECTS__", json.dumps(st.session_state.projects))
      .replace("__POTENTIAL__", json.dumps(st.session_state.potential))
      .replace("__ACTUAL__", json.dumps(st.session_state.actual))
      .replace("__DEPTS__", json.dumps(st.session_state.depts))
)

components.html(html_code, height=900, scrolling=True)
