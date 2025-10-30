import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")
st.image("citadel_logo.png", width=200)

html_code = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <title>Labor Capacity Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
  <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3"></script>
  <style>
    :root{
      --brand:#003366;
      --brand-20: rgba(0,51,102,0.2);
      --capacity:#d32f2f;
      --capacity-20: rgba(211,47,47,0.2);
      --potential:#2e7d32;
      --potential-20: rgba(46,125,50,0.2);
      --actual:#ef6c00;
      --actual-20: rgba(239,108,0,0.2);
      --muted:#6b7280;
    }
    body { font-family: Arial, sans-serif; margin: 24px 40px; }
    h1 { text-align:center; margin: 8px 0 4px; }
    .controls {
      display:flex; gap:16px; flex-wrap:wrap; align-items:center;
      justify-content:center; margin: 12px auto 10px;
    }
    .controls label { font-size:14px; display:flex; align-items:center; gap:6px; }
    .metric-bar {
      display:flex; gap:16px; justify-content:center; flex-wrap:wrap; margin: 10px 0 18px;
    }
    .metric {
      border:1px solid #e5e7eb; border-radius:10px; padding:10px 14px; min-width:220px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05); background:#fff;
    }
    .metric .label { font-size:12px; color:var(--muted); margin-bottom:4px; }
    .metric .value { font-weight:700; font-size:18px; }
    .chart-wrap { width:100%; height:540px; margin-bottom: 16px; position:relative; }
    .footnote { text-align:center; color:#6b7280; font-size:12px; }

    /* Modal */
    .modal-backdrop {
      display:none; position:fixed; inset:0; background:rgba(0,0,0,0.4); z-index:9998;
    }
    .modal {
      display:none; position:fixed; top:50%; left:50%; transform:translate(-50%,-50%);
      background:#fff; border-radius:12px; width:min(800px,92vw);
      max-height:80vh; overflow:auto; z-index:9999; box-shadow:0 8px 32px rgba(0,0,0,0.2);
    }
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

  <label><strong>Time Grain:</strong>
    <select id="timeGrain">
      <option value="week" selected>Weekly</option>
      <option value="month">Monthly</option>
    </select>
  </label>

  <label><input type="checkbox" id="showPotential" checked> Show Potential</label>
  <label><input type="checkbox" id="showActual" checked> Show Actual</label>

  <label><strong>Stack Source:</strong>
    <select id="stackSource">
      <option value="confirmed">Confirmed</option>
      <option value="potential">Potential</option>
      <option value="confirmedPotential" selected>Confirmed + Potential</option>
      <option value="actual">Actual</option>
    </select>
  </label>

  <label><input type="checkbox" id="showCapacityInStack" checked> Show Capacity on Stack</label>

  <label><strong>Productivity:</strong>
    <input type="range" id="prodFactor" min="0.50" max="1.00" step="0.01" value="0.85">
    <span id="prodVal">0.85</span>
  </label>

  <label><strong>Hours / FTE / wk:</strong>
    <input type="number" id="hoursPerFTE" min="30" max="60" step="1" value="40" style="width:64px;">
  </label>
</div>

<div class="metric-bar">
  <div class="metric">
    <div class="label">Peak Utilization</div>
    <div class="value" id="peakUtil">—</div>
  </div>
  <div class="metric">
    <div class="label">Worst Period (Max Over/Under)</div>
    <div class="value" id="worstWeek">—</div>
  </div>
  <div class="metric">
    <div class="label">Capacity / Period</div>
    <div class="value" id="weeklyCap">—</div>
  </div>
</div>

<div class="chart-wrap">
  <canvas id="aggChart"></canvas>
</div>
<div class="chart-wrap">
  <canvas id="stackChart"></canvas>
</div>

<p class="footnote">Top: totals vs capacity (with Utilization%). Bottom: literal project stack. Hover is synced; click for drilldown. Switch Weekly/Monthly to change the timeline bins.</p>

<!-- Drilldown Modal -->
<div class="modal-backdrop" id="modalBackdrop"></div>
<div class="modal" id="drilldownModal">
  <header>
    <h3 id="modalTitle">Breakdown</h3>
    <button class="close-btn" id="closeModal">Close</button>
  </header>
  <div class="content">
    <table>
      <thead><tr><th>Customer / Project</th><th>Hours</th></tr></thead>
      <tbody id="modalBody"></tbody>
    </table>
  </div>
</div>

<script>
// -------------------- DATA --------------------
const projects = [
  {number:"P7578",customer:"ADFAM",aircraftModel:"A340",scope:"Center Gear Replacement",induction:"2025-02-10",delivery:"2025-02-17",Maintenance:688,Interiors:0,Avionics:0,SheetMetal:0,FinishPaint:0,Engineering:0,Upholstery:0,Cabinetry:0},
  {number:"P7476",customer:"GE",aircraftModel:"747-400",scope:"Multi Check, AD's & SB's",induction:"2025-02-18",delivery:"2025-04-03",Maintenance:4955,Interiors:100,Avionics:0,SheetMetal:0,FinishPaint:0,Engineering:0,Upholstery:0,Cabinetry:0},
  {number:"P7591",customer:"Freedom II",aircraftModel:"757-200",scope:"B Check, AD's & SB's",induction:"2025-02-23",delivery:"2025-03-02",Maintenance:871.5,Interiors:0,Avionics:0,SheetMetal:0,FinishPaint:0,Engineering:0,Upholstery:0,Cabinetry:0},
  {number:"P7560",customer:"BEFO",aircraftModel:"737",scope:"96mnth Check",induction:"2025-03-23",delivery:"2025-06-15",Maintenance:4038,Interiors:1921,Avionics:0,SheetMetal:0,FinishPaint:0,Engineering:8,Upholstery:14,Cabinetry:0},
  {number:"P7517",customer:"Parallel",aircraftModel:"757-200",scope:"Interior Mod",induction:"2025-04-15",delivery:"2025-08-31",Maintenance:584,Interiors:5997,Avionics:7114,SheetMetal:1885,FinishPaint:4920,Engineering:0,Upholstery:6885,Cabinetry:2272},
  {number:"P7561",customer:"L3-FBI",aircraftModel:"757-200",scope:"Maintenance & Interior Mod",induction:"2025-07-31",delivery:"2025-10-14",Maintenance:6882,Interiors:1029,Avionics:276,SheetMetal:90,FinishPaint:116,Engineering:244,Upholstery:0,Cabinetry:228},
  {number:"P7426",customer:"Celestial",aircraftModel:"757",scope:"Maintenance & Interior Mod",induction:"2025-02-06",delivery:"2025-03-28",Maintenance:0,Interiors:2840,Avionics:0,SheetMetal:0,FinishPaint:953,Engineering:0,Upholstery:1025,Cabinetry:100},
  {number:"P7592",customer:"LJ Aviation",aircraftModel:"",scope:"GOGO WAP",induction:"2025-02-23",delivery:"2025-03-06",Maintenance:0,Interiors:0,Avionics:0,SheetMetal:0,FinishPaint:0,Engineering:0,Upholstery:0,Cabinetry:0},
  {number:"P7392",customer:"L3-FBI",aircraftModel:"757",scope:"Maintenance & Interior Mod",induction:"2025-05-01",delivery:"2025-06-01",Maintenance:0,Interiors:695,Avionics:300,SheetMetal:90,FinishPaint:16,Engineering:220,Upholstery:0,Cabinetry:240}
];

const potentialProjects = [
  {number:"P7580",customer:"Polaris",aircraftModel:"B737",scope:"144 Mo. Check",induction:"2025-09-01",delivery:"2025-11-10",Maintenance:4162,Interiors:3783,Avionics:1135,SheetMetal:2270,FinishPaint:0,Engineering:0,Upholstery:0,Cabinetry:0},
  {number:"P7560",customer:"BEFO",aircraftModel:"737",scope:"Additional Interior Work",induction:"2025-03-23",delivery:"2025-05-23",Maintenance:0,Interiors:103,Avionics:8,SheetMetal:0,FinishPaint:0,Engineering:8,Upholstery:14,Cabinetry:0}
];

const projectsActual = [
  {number:"P7578",customer:"ADFAM",aircraftModel:"A340",scope:"Center Gear Replacement",induction:"2025-02-10",delivery:"2025-02-17",Maintenance:458.9,Interiors:5.59,Avionics:0,SheetMetal:107.37,FinishPaint:0,Engineering:0,Upholstery:0,Cabinetry:0},
  {number:"P7476",customer:"GE",aircraftModel:"747-400",scope:"Multi Check, AD's & SB's",induction:"2025-02-18",delivery:"2025-04-03",Maintenance:391.71,Interiors:355.79,Avionics:110.46,SheetMetal:175.23,FinishPaint:0,Engineering:0,Upholstery:574.34,Cabinetry:0},
  {number:"P7591",customer:"Freedom II",aircraftModel:"757-200",scope:"B Check, AD's & SB's",induction:"2025-02-23",delivery:"2025-03-02",Maintenance:220.56,Interiors:23.42,Avionics:55.82,SheetMetal:58.39,FinishPaint:0,Engineering:0,Upholstery:17.22,Cabinetry:25.02},
  {number:"P7560",customer:"BEFO",aircraftModel:"737",scope:"96mnth Check",induction:"2025-03-23",delivery:"2025-06-15",Maintenance:0,Interiors:0,Avionics:0,SheetMetal:0,FinishPaint:0,Engineering:0,Upholstery:0,Cabinetry:0},
  {number:"P7517",customer:"Parallel",aircraftModel:"757-200",scope:"Interior Mod",induction:"2025-04-15",delivery:"2025-08-31",Maintenance:140.97,Interiors:309.74,Avionics:438,SheetMetal:12.32,FinishPaint:89.67,Engineering:0,Upholstery:912.77,Cabinetry:123.05},
  {number:"P7561",customer:"L3-FBI",aircraftModel:"757-200",scope:"Maintenance & Interior Mod",induction:"2025-07-31",delivery:"2025-10-14",Maintenance:0,Interiors:0,Avionics:0,SheetMetal:0,FinishPaint:0,Engineering:0,Upholstery:0,Cabinetry:0},
  {number:"P7426",customer:"Celestial",aircraftModel:"757",scope:"Maintenance & Interior Mod",induction:"2025-02-06",delivery:"2025-03-28",Maintenance:2032.27,Interiors:3769.69,Avionics:3.61,SheetMetal:1043.93,FinishPaint:384.49,Engineering:0,Upholstery:948.44,Cabinetry:116.5},
  {number:"P7592",customer:"LJ Aviation",aircraftModel:"",scope:"GOGO WAP",induction:"2025-02-23",delivery:"2025-03-06",Maintenance:0,Interiors:0,Avionics:125.73,SheetMetal:0,FinishPaint:0,Engineering:0,Upholstery:0,Cabinetry:0},
  {number:"P7392",customer:"L3-FBI",aircraftModel:"757",scope:"Maintenance & Interior Mod",induction:"2025-05-01",delivery:"2025-06-01",Maintenance:0,Interiors:27.13,Avionics:0,SheetMetal:0,FinishPaint:0,Engineering:0,Upholstery:0,Cabinetry:0}
];

const departmentCapacities = [
  { name:"Interiors",   headcount:14, key:"Interiors" },
  { name:"Finish",      headcount:4,  key:"FinishPaint" },
  { name:"Cabinetry",   headcount:2,  key:"Cabinetry" },
  { name:"Upholstery",  headcount:6,  key:"Upholstery" },
  { name:"Avionics",    headcount:7,  key:"Avionics" },
  { name:"Sheet Metal", headcount:10, key:"SheetMetal" },
  { name:"Engineering", headcount:3,  key:"Engineering" }
];

// Defaults (can be changed by controls)
let PRODUCTIVITY_FACTOR = 0.85;
let HOURS_PER_FTE = 40;

// -------------------- HELPERS --------------------
function parseDate(s){
  return s.includes("/") ? (()=>{const [m,d,y]=s.split("/");return new Date(+y,+m-1,+d)})() : new Date(s);
}
function formatDateLocal(d){
  const y=d.getFullYear(); const m=String(d.getMonth()+1).padStart(2,"0"); const da=String(d.getDate()).padStart(2,"0");
  return `${y}-${m}-${da}`;
}
function mondayOf(d){
  const t=new Date(d); const day=(t.getDay()+6)%7; t.setDate(t.getDate()-day); t.setHours(0,0,0,0); return t;
}
function firstOfMonth(d){
  return new Date(d.getFullYear(), d.getMonth(), 1);
}
function getWeekList(){
  let minD=null,maxD=null;
  function expand(arr){
    for(const p of arr){ const a=parseDate(p.induction), b=parseDate(p.delivery);
      if(!minD||a<minD)minD=a; if(!maxD||b>maxD)maxD=b;
    }
  }
  expand(projects); expand(potentialProjects); expand(projectsActual);
  const start=mondayOf(minD); const weeks=[]; const cur=new Date(start);
  while(cur<=maxD){ weeks.push(new Date(cur)); cur.setDate(cur.getDate()+7); }
  return weeks.map(formatDateLocal);
}
function getMonthList(){
  let minD=null,maxD=null;
  function expand(arr){
    for(const p of arr){ const a=parseDate(p.induction), b=parseDate(p.delivery);
      if(!minD||a<minD)minD=a; if(!maxD||b>maxD)maxD=b;
    }
  }
  expand(projects); expand(potentialProjects); expand(projectsActual);
  const start = firstOfMonth(minD||new Date());
  const end   = firstOfMonth(maxD||new Date());
  const months = [];
  const cur = new Date(start);
  while(cur <= end){
    months.push(new Date(cur));
    cur.setMonth(cur.getMonth()+1);
  }
  return months.map(formatDateLocal); // label as YYYY-MM-01
}

// Generic loaders over label bins
function computeLoadsDetailedOverLabels(arr, key, labels){
  const total=new Array(labels.length).fill(0); const breakdown=labels.map(()=>[]);
  for(const p of arr){
    const hrs=p[key]||0; if(!hrs) continue;
    const a=parseDate(p.induction), b=parseDate(p.delivery);
    let s=-1,e=-1;
    for(let i=0;i<labels.length;i++){
      const L=new Date(labels[i]);
      if(L>=a && s===-1) s=i;
      if(L<=b) e=i;
    }
    if(s!==-1 && e!==-1 && e>=s){
      const n=e-s+1, per=hrs/n;
      for(let w=s; w<=e; w++){ total[w]+=per; breakdown[w].push({customer:`${p.customer} (${p.number})`, hours:per}); }
    }
  }
  return {weeklyTotal:total, breakdown};
}
function computeLoadsActualOverLabels(arr, key, labels){
  const total=new Array(labels.length).fill(0); const breakdown=labels.map(()=>[]);
  const today=new Date();
  for(const p of arr){
    const hrs=p[key]||0; if(!hrs) continue;
    const a=parseDate(p.induction), planned=parseDate(p.delivery);
    const end = (a>today) ? planned : (planned<today? planned : today);
    if(end<a) continue;
    let s=-1,e=-1;
    for(let i=0;i<labels.length;i++){
      const L=new Date(labels[i]);
      if(L>=a && s===-1) s=i;
      if(L<=end) e=i;
    }
    if(s!==-1 && e!==-1 && e>=s){
      const n=e-s+1, per=hrs/n;
      for(let w=s; w<=e; w++){ total[w]+=per; breakdown[w].push({customer:`${p.customer} (${p.number})`, hours:per}); }
    }
  }
  return {weeklyTotal:total, breakdown};
}

// Per-project series maps for stack view (over arbitrary labels)
function buildProjectSeriesMapOverLabels(arr, key, labels){
  const map = new Map();
  for(const p of arr){
    const hrs=p[key]||0; if(!hrs) continue;
    const a=parseDate(p.induction), b=parseDate(p.delivery);
    let s=-1,e=-1;
    for(let i=0;i<labels.length;i++){
      const L=new Date(labels[i]);
      if(L>=a && s===-1) s=i;
      if(L<=b) e=i;
    }
    if(s!==-1 && e!==-1 && e>=s){
      const n=e-s+1, per=hrs/n;
      const label = `${p.customer} (${p.number})`;
      if(!map.has(label)) map.set(label, new Array(labels.length).fill(0));
      const arrData = map.get(label);
      for(let w=s; w<=e; w++){ arrData[w]+=per; }
    }
  }
  return map;
}
function buildProjectSeriesMapActualOverLabels(arr, key, labels){
  const map = new Map();
  const today=new Date();
  for(const p of arr){
    const hrs=p[key]||0; if(!hrs) continue;
    const a=parseDate(p.induction), planned=parseDate(p.delivery);
    const end=(a>today)?planned:(planned<today?planned:today);
    if(end<a) continue;
    let s=-1,e=-1;
    for(let i=0;i<labels.length;i++){
      const L=new Date(labels[i]);
      if(L>=a && s===-1) s=i;
      if(L<=end) e=i;
    }
    if(s!==-1 && e!==-1 && e>=s){
      const n=e-s+1, per=hrs/n;
      const label = `${p.customer} (${p.number})`;
      if(!map.has(label)) map.set(label, new Array(labels.length).fill(0));
      const arrData = map.get(label);
      for(let w=s; w<=e; w++){ arrData[w]+=per; }
    }
  }
  return map;
}
function mergeSeriesMaps(mapA, mapB){
  const out = new Map();
  for(const [k,v] of mapA.entries()) out.set(k, v.slice());
  for(const [k,v] of mapB.entries()){
    if(!out.has(k)) out.set(k, v.slice());
    else { const d=out.get(k); for(let i=0;i<d.length;i++) d[i]+=v[i]; }
  }
  return out;
}

// Palette
function palette(idx){
  const h = (idx*37)%360;
  const border = `hsl(${h} 65% 45%)`;
  const fill   = `hsl(${h} 65% 45% / 0.18)`;
  return {border, fill};
}

// -------------------- STATE (grain-aware) --------------------
let currentGrain = 'week'; // 'week' | 'month'
let periodLabels = [];     // array of label strings
let dataConfirmed = {};
let dataPotential = {};
let dataActual    = {};
let seriesConfirmed = {};
let seriesPotential = {};
let seriesActualMap = {};
let currentKey; // discipline key

// build labels for grain
function buildLabelsForGrain(){
  return (currentGrain==='week') ? getWeekList() : getMonthList();
}

// capacity per period (week => constant; month => scale by days/7)
function capacityArrayFor(key, labels){
  const dept = departmentCapacities.find(x=>x.key===key);
  const weeklyCap = dept.headcount * HOURS_PER_FTE * PRODUCTIVITY_FACTOR;
  if(currentGrain==='week'){
    return labels.map(()=>weeklyCap);
  } else {
    // monthly: scale by (days_in_month / 7)
    return labels.map(lbl=>{
      const d=new Date(lbl);
      const y=d.getFullYear(), m=d.getMonth();
      const days = new Date(y, m+1, 0).getDate();
      return weeklyCap * (days/7);
    });
  }
}

// utilization %
function utilizationArray(key){
  const conf = dataConfirmed[key].weeklyTotal;
  const pot  = dataPotential[key].weeklyTotal;
  const cap  = capacityArrayFor(key, periodLabels);
  return conf.map((v,i)=>{
    const load = v + (document.getElementById('showPotential').checked ? pot[i] : 0);
    return cap[i] ? (100 * load / cap[i]) : 0;
  });
}

// annotations (show Today only if it exists in labels)
function buildAnnotations(){
  let label;
  if(currentGrain==='week'){
    label = formatDateLocal(mondayOf(new Date()));
  } else {
    const f = firstOfMonth(new Date());
    label = formatDateLocal(f);
  }
  if(!periodLabels.includes(label)){
    return { annotations:{} }; // no-op if label not present
  }
  return {
    annotations:{
      todayLine:{
        type:'line', xMin: label, xMax: label,
        borderColor:'#9ca3af', borderWidth:1, borderDash:[4,4],
        label:{ display:true, content:'Today', position:'start', color:'#6b7280', backgroundColor:'rgba(255,255,255,0.8)' }
      }
    }
  };
}

// recompute all data for (grain, labels, discipline list)
function recomputeAll(){
  periodLabels = buildLabelsForGrain();
  dataConfirmed = {};
  dataPotential = {};
  dataActual    = {};
  seriesConfirmed = {};
  seriesPotential = {};
  seriesActualMap = {};

  departmentCapacities.forEach(d=>{
    const c=computeLoadsDetailedOverLabels(projects, d.key, periodLabels);
    const p=computeLoadsDetailedOverLabels(potentialProjects, d.key, periodLabels);
    const a=computeLoadsActualOverLabels(projectsActual, d.key, periodLabels);
    dataConfirmed[d.key]={name:d.name, weeklyTotal:c.weeklyTotal, breakdown:c.breakdown};
    dataPotential[d.key]={name:d.name, weeklyTotal:p.weeklyTotal, breakdown:p.breakdown};
    dataActual[d.key]   ={name:d.name, weeklyTotal:a.weeklyTotal, breakdown:a.breakdown};

    seriesConfirmed[d.key] = buildProjectSeriesMapOverLabels(projects, d.key, periodLabels);
    seriesPotential[d.key] = buildProjectSeriesMapOverLabels(potentialProjects, d.key, periodLabels);
    seriesActualMap[d.key] = buildProjectSeriesMapActualOverLabels(projectsActual, d.key, periodLabels);
  });
}

// -------------------- PREP + CHARTS --------------------
const sel = document.getElementById('disciplineSelect');
departmentCapacities.forEach(d=>{
  const o=document.createElement('option'); o.value=d.key; o.textContent=d.name; sel.appendChild(o);
});
sel.value = "Interiors";
currentKey = sel.value;

const chkPot = document.getElementById('showPotential');
const chkAct = document.getElementById('showActual');
const stackSourceSel = document.getElementById('stackSource');
const chkCapInStack = document.getElementById('showCapacityInStack');
const prodSlider = document.getElementById('prodFactor');
const prodVal = document.getElementById('prodVal');
const hoursInput = document.getElementById('hoursPerFTE');
const grainSel = document.getElementById('timeGrain');

recomputeAll();
let annos = buildAnnotations();

function buildAggregateDatasets(key){
  return [
    { // Confirmed Load
      label: `${dataConfirmed[key].name} Load (hrs)`,
      data: dataConfirmed[key].weeklyTotal,
      borderColor: getComputedStyle(document.documentElement).getPropertyValue('--brand').trim(),
      backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--brand-20').trim(),
      borderWidth:2, fill:true, tension:0.1, pointRadius:0
    },
    { // Capacity / Period
      label: `${dataConfirmed[key].name} Capacity (hrs/period)`,
      data: capacityArrayFor(key, periodLabels),
      borderColor: getComputedStyle(document.documentElement).getPropertyValue('--capacity').trim(),
      backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--capacity-20').trim(),
      borderWidth:2, fill:false, borderDash:[6,6], tension:0.1, pointRadius:0, _isCapacity:true
    },
    { // Potential
      label: `${dataConfirmed[key].name} Potential (hrs)`,
      data: dataPotential[key].weeklyTotal,
      borderColor: getComputedStyle(document.documentElement).getPropertyValue('--potential').trim(),
      backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--potential-20').trim(),
      borderWidth:2, fill:true, tension:0.1, pointRadius:0, hidden: !chkPot.checked
    },
    { // Actual
      label: `${dataConfirmed[key].name} Actual (hrs)`,
      data: dataActual[key].weeklyTotal,
      borderColor: getComputedStyle(document.documentElement).getPropertyValue('--actual').trim(),
      backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--actual-20').trim(),
      borderWidth:2, fill:true, tension:0.1, pointRadius:0, hidden: !chkAct.checked
    },
    { // Utilization %
      label: 'Utilization %',
      data: utilizationArray(key),
      borderColor:'#374151',
      backgroundColor:'rgba(55,65,81,0.12)',
      yAxisID:'y2', borderWidth:1.5, fill:false, tension:0.1, pointRadius:0
    }
  ];
}

function buildStackDatasets(key, stackMode, showCapacity){
  let map;
  if (stackMode==='potential') map = seriesPotential[key];
  else if (stackMode==='confirmedPotential') map = mergeSeriesMaps(seriesConfirmed[key], seriesPotential[key]);
  else if (stackMode==='actual') map = seriesActualMap[key];
  else map = seriesConfirmed[key];

  const items = Array.from(map.entries()).map(([label,data])=>({
    label, data, total: data.reduce((a,b)=>a+b,0)
  })).sort((a,b)=>b.total-a.total);

  const running = new Array(items[0]?.data.length || 0).fill(0);
  const ds = items.map((it, idx)=>{
    const col = palette(idx);
    const cumulative = it.data.map((v,i)=> v + running[i]);
    for(let i=0;i<running.length;i++) running[i] = cumulative[i];
    return {
      label: it.label,
      data: cumulative,
      type: 'line',
      borderColor: col.border,
      backgroundColor: col.fill,
      borderWidth:1.5, pointRadius:0, tension:0.1,
      stack:'projects', fill: idx===0 ? 'origin' : '-1', spanGaps:true, order: idx+1
    };
  });

  if (showCapacity){
    ds.push({
      label: `${dataConfirmed[key].name} Capacity (hrs/period)`,
      data: capacityArrayFor(key, periodLabels),
      borderColor: getComputedStyle(document.documentElement).getPropertyValue('--capacity').trim(),
      backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--capacity-20').trim(),
      borderWidth: 2, fill: false, borderDash: [6,6],
      tension: 0.1, pointRadius: 0, _isCapacity: true, order: 9999
    });
  }
  return ds;
}

const aggCtx = document.getElementById('aggChart').getContext('2d');
const stackCtx = document.getElementById('stackChart').getContext('2d');

let chartAgg = new Chart(aggCtx, {
  type:'line',
  data:{ labels: periodLabels, datasets: buildAggregateDatasets(currentKey) },
  options:{
    responsive:true, maintainAspectRatio:false,
    interaction:{ mode:'index', intersect:false },
    scales:{
      x:{ title:{display:true, text: (currentGrain==='week'?'Week Starting':'Month Starting')} },
      y:{ title:{display:true, text:'Hours'}, beginAtZero:true, stacked:false },
      y2:{ title:{display:true, text:'Utilization %'}, beginAtZero:true, position:'right', grid:{ drawOnChartArea:false }, suggestedMax:150 }
    },
    plugins:{ annotation: annos, legend:{position:'top'}, title:{ display:true, text: 'Totals vs Capacity - '+dataConfirmed[currentKey].name } },
    onClick:(evt, elems)=>{
      if(!elems||!elems.length) return;
      const {datasetIndex, index:idx} = elems[0];
      if(datasetIndex===1 || datasetIndex===4) return;
      let breakdownArr=null, label='';
      if(datasetIndex===0){ breakdownArr = dataConfirmed[currentKey].breakdown[idx]; label='Confirmed'; }
      else if(datasetIndex===2){ breakdownArr = dataPotential[currentKey].breakdown[idx]; label='Potential'; }
      else if(datasetIndex===3){ breakdownArr = dataActual[currentKey].breakdown[idx]; label='Actual'; }
      if(!breakdownArr || breakdownArr.length===0){ openModal(`No ${label} hours in ${periodLabels[idx]}.`, []); return; }
      openModal(`${periodLabels[idx]} · ${dataConfirmed[currentKey].name} · ${label}`, breakdownArr);
    }
  }
});

let chartStack = new Chart(stackCtx, {
  type:'line',
  data:{ labels: periodLabels, datasets: buildStackDatasets(currentKey, stackSourceSel.value, chkCapInStack.checked) },
  options:{
    responsive:true, maintainAspectRatio:false,
    interaction:{ mode:'index', intersect:false },
    scales:{
      x:{ title:{display:true, text: (currentGrain==='week'?'Week Starting':'Month Starting')} },
      y:{ title:{display:true, text:'Hours'}, beginAtZero:true, stacked:false },
      y2:{ display:false }
    },
    plugins:{ annotation: annos, legend:{position:'top'}, title:{ display:true, text: 'Project Stack - '+dataConfirmed[currentKey].name+' ('+stackSourceSel.selectedOptions[0].text+')' } },
    onClick:(evt, elems)=>{
      if(!elems||!elems.length) return;
      const {datasetIndex, index:idx} = elems[0];
      const dsArr = chartStack.data.datasets;
      const cur = dsArr[datasetIndex];
      if (cur && cur._isCapacity) return;
      const prev = (datasetIndex>0 && dsArr[datasetIndex-1] && !dsArr[datasetIndex-1]._isCapacity) ? (dsArr[datasetIndex-1].data[idx] || 0) : 0;
      const contrib = (cur.data[idx] || 0) - prev;
      openModal(`${periodLabels[idx]} · ${cur.label}`, [{customer: cur.label, hours: contrib}]);
    }
  }
});

// Tooltip for stack band range
chartStack.options.plugins.tooltip = chartStack.options.plugins.tooltip || {};
chartStack.options.plugins.tooltip.callbacks = {
  label: (ctx) => {
    const i = ctx.dataIndex;
    const dsIndex = ctx.datasetIndex;
    const dsArr = chartStack.data.datasets;
    const cur = dsArr[dsIndex];
    if (cur._isCapacity) return `${cur.label}: ${ctx.formattedValue} hrs`;
    const prev = (dsIndex>0 && dsArr[dsIndex-1] && !dsArr[dsIndex-1]._isCapacity) ? (dsArr[dsIndex-1].data[i] || 0) : 0;
    const val = (cur.data[i] || 0) - prev;
    const upper = cur.data[i] || 0;
    return `${cur.label}: ${val.toFixed(0)} hrs (range ${prev.toFixed(0)}–${upper.toFixed(0)})`;
  }
};

// -------------------- KPIs --------------------
function getCombinedLoadArrayForKPIs(){
  const conf = dataConfirmed[currentKey].weeklyTotal;
  const pot  = dataPotential[currentKey].weeklyTotal;
  return conf.map((v,i)=> v + (chkPot.checked ? pot[i] : 0));
}
function updateKPIs(){
  const capArr = capacityArrayFor(currentKey, periodLabels);
  const combined = getCombinedLoadArrayForKPIs();
  let peak=0, peakIdx=0;
  for(let i=0;i<combined.length;i++){
    const u = capArr[i]? (combined[i]/capArr[i]*100):0;
    if(u>peak){ peak=u; peakIdx=i; }
  }
  let worstDiff = -Infinity, worstIdx = 0;
  for(let i=0;i<combined.length;i++){
    const diff = combined[i] - capArr[i];
    if(diff>worstDiff){ worstDiff=diff; worstIdx=i; }
  }
  document.getElementById('peakUtil').textContent = `${peak.toFixed(0)}% (${periodLabels[peakIdx]})`;
  const status = worstDiff>=0 ? `+${worstDiff.toFixed(0)} hrs over` : `${(-worstDiff).toFixed(0)} hrs under`;
  document.getElementById('worstWeek').textContent = `${periodLabels[worstIdx]} · ${status}`;
  const capDisp = capArr[0] || 0;
  document.getElementById('weeklyCap').textContent = `${capDisp.toFixed(0)} hrs / ${currentGrain}`;
}

// -------------------- HOVER SYNC --------------------
function syncHover(src, dst){
  const active = src.getActiveElements();
  if(!active.length){ dst.setActiveElements([]); dst.update('none'); return; }
  const idx = active[0].index;
  const targets = dst.data.datasets.map((_, di)=>({datasetIndex: di, index: idx}));
  dst.setActiveElements(targets); dst.update('none');
}
chartAgg.options.onHover = (e, els)=> syncHover(chartAgg, chartStack);
chartStack.options.onHover = (e, els)=> syncHover(chartStack, chartAgg);

// -------------------- LISTENERS --------------------
sel.addEventListener('change', e=>{
  currentKey = e.target.value;
  refreshBoth();
});

document.getElementById('timeGrain').addEventListener('change', e=>{
  currentGrain = e.target.value;
  // Recompute all data, labels, annotations; update charts
  recomputeAll();
  annos = buildAnnotations();

  chartAgg.data.labels = periodLabels;
  chartStack.data.labels = periodLabels;

  chartAgg.options.scales.x.title.text = (currentGrain==='week'?'Week Starting':'Month Starting');
  chartStack.options.scales.x.title.text = (currentGrain==='week'?'Week Starting':'Month Starting');

  chartAgg.options.plugins.annotation = annos;
  chartStack.options.plugins.annotation = annos;

  refreshBoth(); // rebuild datasets & KPIs
});

chkPot.addEventListener('change', ()=>{
  chartAgg.data.datasets = buildAggregateDatasets(currentKey);
  chartAgg.options.plugins.title.text = 'Totals vs Capacity - ' + dataConfirmed[currentKey].name;
  chartAgg.update();
  chartStack.data.datasets = buildStackDatasets(currentKey, stackSourceSel.value, chkCapInStack.checked);
  chartStack.update();
  updateKPIs();
});

chkAct.addEventListener('change', ()=>{
  chartAgg.data.datasets = buildAggregateDatasets(currentKey);
  chartAgg.update();
});

stackSourceSel.addEventListener('change', ()=>{
  chartStack.data.datasets = buildStackDatasets(currentKey, stackSourceSel.value, chkCapInStack.checked);
  chartStack.options.plugins.title.text = 'Project Stack - ' + dataConfirmed[currentKey].name + ' (' + stackSourceSel.selectedOptions[0].text + ')';
  chartStack.update();
});

chkCapInStack.addEventListener('change', ()=>{
  chartStack.data.datasets = buildStackDatasets(currentKey, stackSourceSel.value, chkCapInStack.checked);
  chartStack.update();
});

prodSlider.addEventListener('input', e=>{
  PRODUCTIVITY_FACTOR = parseFloat(e.target.value||'0.85'); prodVal.textContent = PRODUCTIVITY_FACTOR.toFixed(2);
  chartAgg.data.datasets = buildAggregateDatasets(currentKey);
  chartAgg.update();
  chartStack.data.datasets = buildStackDatasets(currentKey, stackSourceSel.value, chkCapInStack.checked);
  chartStack.update();
  updateKPIs();
});

hoursInput.addEventListener('change', e=>{
  const v = parseInt(e.target.value||'40',10);
  HOURS_PER_FTE = isNaN(v) ? 40 : Math.min(60, Math.max(30, v));
  e.target.value = HOURS_PER_FTE;
  chartAgg.data.datasets = buildAggregateDatasets(currentKey);
  chartAgg.update();
  chartStack.data.datasets = buildStackDatasets(currentKey, stackSourceSel.value, chkCapInStack.checked);
  chartStack.update();
  updateKPIs();
});

// Convenience
function refreshBoth(){
  chartAgg.data.datasets = buildAggregateDatasets(currentKey);
  chartAgg.options.plugins.title.text = 'Totals vs Capacity - ' + dataConfirmed[currentKey].name;
  chartAgg.update();

  chartStack.data.datasets = buildStackDatasets(currentKey, stackSourceSel.value, chkCapInStack.checked);
  chartStack.options.plugins.title.text = 'Project Stack - ' + dataConfirmed[currentKey].name + ' (' + stackSourceSel.selectedOptions[0].text + ')';
  chartStack.update();

  updateKPIs();
}

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
function closeModal(){
  backdrop.style.display='none'; modal.style.display='none';
}

// Initial render
refreshBoth();
</script>
</body>
</html>
"""

components.html(html_code, height=1350, scrolling=True)
