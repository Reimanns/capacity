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
      --ink:#111827;
    }
    html, body { height:100%; }
    body { font-family: Arial, sans-serif; margin: 16px 32px 24px; overflow-y:auto; }
    h1 { text-align:center; margin: 8px 0 12px; color:var(--ink); }
    .controls {
      display:flex; gap:16px; flex-wrap:wrap; align-items:center;
      justify-content:center; margin: 10px auto 12px;
    }
    .controls label { font-size:14px; display:flex; align-items:center; gap:6px; }
    select, input[type="number"] { font-size:14px; padding:4px 6px; }
    .metric-bar {
      display:flex; gap:16px; justify-content:center; flex-wrap:wrap; margin: 10px 0 18px;
    }
    .metric {
      border:1px solid #e5e7eb; border-radius:10px; padding:10px 14px; min-width:220px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05); background:#fff;
    }
    .metric .label { font-size:12px; color:var(--muted); margin-bottom:4px; }
    .metric .value { font-weight:700; font-size:18px; }
    .row {
      display:grid; grid-template-columns: 1fr; gap:16px; margin-top:8px;
    }
    .chart-card {
      border:1px solid #e5e7eb; border-radius:12px; background:#fff; padding:10px 12px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .chart-title { font-size:14px; color:var(--muted); margin:2px 0 8px; text-align:center; }
    .chart-wrap { width:100%; height:760px; position:relative; }
    .chart-wrap-small { width:100%; height:260px; position:relative; }
    .footnote { text-align:center; color:#6b7280; font-size:12px; margin-top:4px; }

    /* Modal */
    .modal-backdrop {
      display:none; position:fixed; inset:0; background:rgba(0,0,0,0.4); z-index:9998;
    }
    .modal {
      display:none; position:fixed; left:50%; transform:translate(-50%, 0);
      background:#fff; border-radius:12px; width:min(900px,92vw);
      max-height:74vh; overflow:auto; z-index:9999; box-shadow:0 8px 32px rgba(0,0,0,0.2);
    }
    .modal header { padding:14px 16px; border-bottom:1px solid #eee; display:flex; justify-content:space-between; align-items:center;}
    .modal header h3 { margin:0; font-size:16px;}
    .modal .content { padding:12px 16px 18px; }
    .modal table { width:100%; border-collapse:collapse; }
    .modal th, .modal td { border-bottom:1px solid #eee; padding:8px; text-align:left; font-size:14px;}
    .close-btn { cursor:pointer; border:none; background:#f3f4f6; padding:6px 10px; border-radius:8px; }

    details.data-panel {
      max-width: 1000px; margin: 0 auto 8px; background:#fcfcfd; border:1px solid #eaeaea; border-radius:10px;
      padding: 8px 12px;
    }
    details.data-panel summary { cursor:pointer; font-weight:600; color:#374151; }
    .data-row { display:flex; gap:8px; align-items:center; margin-top:8px; }
    .data-row textarea { width:100%; height:160px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size:12.5px; padding:8px; }
    .btn { border:1px solid #e5e7eb; border-radius:8px; padding:6px 10px; background:#fff; cursor:pointer; }
    .btn.primary { background:#111827; color:#fff; border-color:#111827; }
  </style>
</head>
<body>

<h1>Capacity-Load By Discipline</h1>

<!-- Quick dataset editor (paste JSON and reload fast) -->
<details class="data-panel">
  <summary>Data (JSON) – click to show/hide</summary>
  <div class="data-row">
    <textarea id="jsonInput"></textarea>
  </div>
  <div class="data-row" style="justify-content:flex-end;">
    <button class="btn" id="btnReset">Reset</button>
    <button class="btn primary" id="btnLoad">Load Data</button>
  </div>
</details>

<div class="controls">
  <label for="disciplineSelect"><strong>Discipline:</strong></label>
  <select id="disciplineSelect"></select>

  <label><strong>Timeline:</strong>
    <select id="timelineMode">
      <option value="weekly">Weekly</option>
      <option value="monthly">Monthly</option>
    </select>
  </label>

  <label><input type="checkbox" id="showPotential" checked> Show Potential</label>

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

<div class="row">
  <div class="chart-card">
    <div class="chart-title">Load, Capacity, and Potential</div>
    <div class="chart-wrap">
      <canvas id="mainChart"></canvas>
    </div>
    <p class="footnote">Tip: click a line/area at any time point to see customer breakdown. If "Show Potential" is on, the modal shows <em>Confirmed + Potential</em> with totals.</p>
  </div>

  <div class="chart-card">
    <div class="chart-title">Utilization % (with 100% reference)</div>
    <div class="chart-wrap-small">
      <canvas id="utilChart"></canvas>
    </div>
  </div>
</div>

<!-- Drilldown Modal -->
<div class="modal-backdrop" id="modalBackdrop"></div>
<div class="modal" id="drilldownModal">
  <header>
    <h3 id="modalTitle">Breakdown</h3>
    <button class="close-btn" id="closeModal">Close</button>
  </header>
  <div class="content">
    <table>
      <thead id="modalHead"><tr><th>Customer</th><th>Hours</th></tr></thead>
      <tbody id="modalBody"></tbody>
    </table>
  </div>
</div>

<script>
/* =========================
   Default dataset
   ========================= */
const defaultData = {
  "projects": [
    { "number":"P7657","customer":"Kaiser","aircraftModel":"B737","scope":"Starlink","induction":"2025-11-15T00:00:00","delivery":"2025-11-25T00:00:00","Maintenance":93.57,"Structures":240.61,"Avionics":294.07,"Inspection":120.3,"Interiors":494.58,"Engineering":80.2,"Cabinet":0,"Upholstery":0,"Finish":13.37 },
    { "number":"P7611","customer":"Alpha Star","aircraftModel":null,"scope":null,"induction":"2025-10-20T00:00:00","delivery":"2025-12-04T00:00:00","Maintenance":2432.23,"Structures":1252.97,"Avionics":737.04,"Inspection":1474.08,"Interiors":1474.08,"Engineering":0.0,"Cabinet":0,"Upholstery":0,"Finish":0.0 },
    { "number":"P7645","customer":"Kaiser","aircraftModel":"B737","scope":"Starlink","induction":"2025-11-30T00:00:00","delivery":"2025-12-10T00:00:00","Maintenance":93.57,"Structures":240.61,"Avionics":294.07,"Inspection":120.3,"Interiors":494.58,"Engineering":80.2,"Cabinet":0,"Upholstery":0,"Finish":13.37 },
    { "number":"P7426","customer":"Celestial","aircraftModel":"B757","scope":"Post Maintenance Discrepancies","induction":"2026-01-05T00:00:00","delivery":"2026-01-15T00:00:00","Maintenance":0.0,"Structures":0.0,"Avionics":0.0,"Inspection":0.0,"Interiors":0.0,"Engineering":0.0,"Cabinet":0,"Upholstery":0,"Finish":0.0 },
    { "number":"P7548","customer":"Ty Air","aircraftModel":"B737","scope":"CMS Issues","induction":"2025-10-20T00:00:00","delivery":"2025-10-30T00:00:00","Maintenance":0.0,"Structures":0.0,"Avionics":0.0,"Inspection":0.0,"Interiors":0.0,"Engineering":0.0,"Cabinet":0,"Upholstery":0,"Finish":0.0 },
    { "number":"P7706","customer":"Valkyrie","aircraftModel":"B737-MAX","scope":"Starlink, Mods","induction":"2025-10-31T00:00:00","delivery":"2025-12-09T00:00:00","Maintenance":102.75,"Structures":328.8,"Avionics":411.0,"Inspection":164.4,"Interiors":945.3,"Engineering":82.2,"Cabinet":0,"Upholstery":0,"Finish":20.55 },
    { "number":"P7685","customer":"Sands","aircraftModel":"B737-700","scope":"Starlink","induction":"2025-11-03T00:00:00","delivery":"2025-11-17T00:00:00","Maintenance":105.44,"Structures":224.06,"Avionics":303.14,"Inspection":118.62,"Interiors":474.48,"Engineering":79.08,"Cabinet":0,"Upholstery":0,"Finish":13.18 }
  ],
  "potential": [
    { "number":"P7661","customer":"Sands","aircraftModel":"A340-500","scope":"C Check","induction":"2026-01-29T00:00:00","delivery":"2026-02-28T00:00:00","Maintenance":2629.44,"Structures":1709.14,"Avionics":723.1,"Inspection":1248.98,"Interiors":262.94,"Engineering":0,"Cabinet":0,"Upholstery":0,"Finish":0 },
    { "number":"P7669","customer":"Sands","aircraftModel":"A319-133","scope":"C Check","induction":"2025-12-08T00:00:00","delivery":"2026-01-28T00:00:00","Maintenance":2029.67,"Structures":984.08,"Avionics":535.55,"Inspection":675.56,"Interiors":1906.66,"Engineering":0,"Cabinet":0,"Upholstery":0,"Finish":0 },
    { "number":null,"customer":"Sands","aircraftModel":"B767-300","scope":"C Check","induction":"2026-09-15T00:00:00","delivery":"2026-12-04T00:00:00","Maintenance":0.0,"Structures":0.0,"Avionics":0.0,"Inspection":0.0,"Interiors":0.0,"Engineering":0,"Cabinet":0,"Upholstery":0,"Finish":0 },
    { "number":"P7686","customer":"Polaris","aircraftModel":"B777","scope":"1A & 3A Mx Checks","induction":"2025-12-01T00:00:00","delivery":"2025-12-09T00:00:00","Maintenance":643.15,"Structures":287.36,"Avionics":150.52,"Inspection":177.89,"Interiors":109.47,"Engineering":0,"Cabinet":0,"Upholstery":0,"Finish":0 },
    { "number":"P7430","customer":"Turkmen","aircraftModel":"B777","scope":"Maint/Recon/Refub","induction":"2025-11-10T00:00:00","delivery":"2026-07-13T00:00:00","Maintenance":12720.0,"Structures":12720.0,"Avionics":3180.0,"Inspection":3180.0,"Interiors":19080.0,"Engineering":3180,"Cabinet":3180,"Upholstery":3180,"Finish":3180 },
    { "number":"P7649","customer":"NEP","aircraftModel":"B767-300","scope":"Refurb","induction":"2026-02-02T00:00:00","delivery":"2026-07-13T00:00:00","Maintenance":2000.0,"Structures":2400.0,"Avionics":2800.0,"Inspection":800.0,"Interiors":4400.0,"Engineering":1800,"Cabinet":1600,"Upholstery":1200,"Finish":3000 },
    { "number":"P7689","customer":"Sands","aircraftModel":"B737-700","scope":"C1,C3,C6C7 Mx","induction":"2025-09-10T00:00:00","delivery":"2026-11-07T00:00:00","Maintenance":8097.77,"Structures":1124.69,"Avionics":899.75,"Inspection":787.28,"Interiors":337.14,"Engineering":0,"Cabinet":0,"Upholstery":0,"Finish":0 },
    { "number":"P7690","customer":"Sands","aircraftModel":null,"scope":"C1,C2,C7 Mx","induction":"2025-05-25T00:00:00","delivery":"2025-07-22T00:00:00","Maintenance":3227.14,"Structures":2189.85,"Avionics":922.04,"Inspection":1152.55,"Interiors":4033.92,"Engineering":0,"Cabinet":0,"Upholstery":0,"Finish":0 },
    { "number":"P7691","customer":"Sands","aircraftModel":"B737-700","scope":"C1,C2,C3,C7 Mx","induction":"2026-10-13T00:00:00","delivery":"2026-12-22T00:00:00","Maintenance":4038.3,"Structures":5115.18,"Avionics":1076.88,"Inspection":1346.1,"Interiors":1884.54,"Engineering":0,"Cabinet":0,"Upholstery":0,"Finish":0 }
  ],
  "departments": [
    { "Name":"Maintenance","Headcount":36,"Key":"Maintenance" },
    { "Name":"Structures","Headcount":22,"Key":"Structures" },
    { "Name":"Avionics","Headcount":15,"Key":"Avionics" },
    { "Name":"Inspection","Headcount":10,"Key":"Inspection" },
    { "Name":"Interiors","Headcount":11,"Key":"Interiors" },
    { "Name":"Engineering","Headcount":7,"Key":"Engineering" },
    { "Name":"Cabinet","Headcount":3,"Key":"Cabinet" },
    { "Name":"Upholstery","Headcount":7,"Key":"Upholstery" },
    { "Name":"Finish","Headcount":6,"Key":"Finish" }
  ]
};

// State
let DATA = JSON.parse(JSON.stringify(defaultData));
let PRODUCTIVITY_FACTOR = 0.85;
let HOURS_PER_FTE = 40;
let timelineMode = 'weekly'; // 'weekly' | 'monthly'
let showPotential = true;

const sel = document.getElementById('disciplineSelect');
const timelineSel = document.getElementById('timelineMode');
const prodSlider = document.getElementById('prodFactor');
const prodVal = document.getElementById('prodVal');
const hoursInput = document.getElementById('hoursPerFTE');
const chkPot = document.getElementById('showPotential');
const jsonBox = document.getElementById('jsonInput');
const btnLoad = document.getElementById('btnLoad');
const btnReset = document.getElementById('btnReset');

jsonBox.value = JSON.stringify(defaultData, null, 2);
btnReset.onclick = ()=>{ jsonBox.value = JSON.stringify(defaultData, null, 2); };
btnLoad.onclick = ()=>{
  try{
    const obj = JSON.parse(jsonBox.value);
    if(!obj.projects || !obj.potential || !obj.departments) throw new Error("Missing keys in JSON (need projects, potential, departments).");
    DATA = obj;
    rebuildEverything();
  }catch(e){
    alert("Invalid JSON: " + e.message);
  }
};

// ===== Utilities =====
function parseDate(s){ return new Date(s); }
function formatDateLocal(d){
  const y=d.getFullYear(), m=String(d.getMonth()+1).padStart(2,'0'), da=String(d.getDate()).padStart(2,'0');
  return `${y}-${m}-${da}`;
}
function isWorkday(d){ const day=d.getDay(); return day>=1 && day<=5; }
function mondayOf(d){
  const t=new Date(d); const day=(t.getDay()+6)%7; t.setDate(t.getDate()-day); t.setHours(0,0,0,0); return t;
}
function firstDayOfMonth(d){ return new Date(d.getFullYear(), d.getMonth(), 1); }
function lastDayOfMonth(d){ return new Date(d.getFullYear(), d.getMonth()+1, 0); }
function monthKey(d){ return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}`; }
function clamp(v,min,max){ return Math.max(min, Math.min(max, v)); }

// Build labels
function getWeeklyLabels(){
  let minD=null, maxD=null;
  const expand = (arr)=>{
    for(const p of arr){
      const a=parseDate(p.induction), b=parseDate(p.delivery);
      if(!minD||a<minD) minD=a;
      if(!maxD||b>maxD) maxD=b;
    }
  };
  expand(DATA.projects); expand(DATA.potential);
  if(!minD||!maxD) return [];
  const start=mondayOf(minD); const labels=[]; const cur=new Date(start);
  while(cur<=maxD){ labels.push(formatDateLocal(cur)); cur.setDate(cur.getDate()+7); }
  return labels;
}
function getMonthlyLabels(){
  let minD=null, maxD=null;
  const expand = (arr)=>{
    for(const p of arr){
      const a=parseDate(p.induction), b=parseDate(p.delivery);
      if(!minD||a<minD) minD=a;
      if(!maxD||b>maxD) maxD=b;
    }
  };
  expand(DATA.projects); expand(DATA.potential);
  if(!minD||!maxD) return [];
  const start = firstDayOfMonth(minD);
  const end   = lastDayOfMonth(maxD);
  const labels=[];
  const cur = new Date(start);
  cur.setDate(1);
  while(cur<=end){
    labels.push(monthKey(cur)); // e.g., "2025-11"
    cur.setMonth(cur.getMonth()+1);
  }
  return labels;
}

// Count workdays between two dates inclusive
function workdaysBetween(a, b){
  let count = 0;
  const d = new Date(a);
  while(d <= b){
    if(isWorkday(d)) count++;
    d.setDate(d.getDate()+1);
  }
  return count;
}

// Compute loads
function computeLoadsDetailed(arr, key, labels, mode){
  const total = new Array(labels.length).fill(0);
  const breakdown = labels.map(()=>[]);
  if(mode === 'weekly'){
    for(const p of arr){
      const hrs = p[key] || 0; if(!hrs) continue;
      const a = parseDate(p.induction), b = parseDate(p.delivery);
      let s=-1,e=-1;
      for(let i=0;i<labels.length;i++){
        const L = new Date(labels[i]);
        if(L>=a && s===-1) s=i;
        if(L<=b) e=i;
      }
      if(s!==-1 && e!==-1 && e>=s){
        const n = e - s + 1;
        const per = hrs / n;
        for(let w=s; w<=e; w++){
          total[w] += per;
          breakdown[w].push({ customer:`${p.customer} (${p.number ?? "N/A"})`, hours:per });
        }
      }
    }
  } else {
    // monthly: distribute only across workdays, then sum by monthKey
    const idxByMonth = new Map();
    labels.forEach((mk, i)=> idxByMonth.set(mk, i));
    for(const p of arr){
      const hrs = p[key] || 0; if(!hrs) continue;
      const a = parseDate(p.induction), b = parseDate(p.delivery);
      const wd = workdaysBetween(a,b);
      if(wd===0) continue;
      const perDay = hrs / wd;

      // accumulate project hours per month
      const perMonth = new Map(); // mk -> sum
      const d = new Date(a);
      while(d <= b){
        if(isWorkday(d)){
          const mk = monthKey(d);
          perMonth.set(mk, (perMonth.get(mk)||0) + perDay);
        }
        d.setDate(d.getDate()+1);
      }
      for(const [mk, val] of perMonth.entries()){
        const idx = idxByMonth.get(mk);
        if(idx!=null){
          total[idx] += val;
          breakdown[idx].push({ customer:`${p.customer} (${p.number ?? "N/A"})`, hours:val });
        }
      }
    }
  }
  return { weeklyTotal: total, breakdown };
}

// Capacity series per label
function capacitySeries(key, labels, mode){
  const dept = DATA.departments.find(x=>x.Key===key);
  const basePerWeek = (dept ? dept.Headcount : 0) * HOURS_PER_FTE * PRODUCTIVITY_FACTOR;
  if(mode==='weekly'){
    return labels.map(()=> basePerWeek);
  } else {
    // monthly capacity scaled to workdays/5
    const caps = [];
    for(const mk of labels){
      const [y,m] = mk.split('-').map(Number);
      const start = new Date(y, m-1, 1);
      const end   = new Date(y, m, 0);
      const wd = workdaysBetween(start, end);
      const weeksEquivalent = wd / 5; // 5 workdays per week
      caps.push(basePerWeek * weeksEquivalent);
    }
    return caps;
  }
}

// Utilization array (%)
function utilizationArray(key, confArr, potArr, capArr){
  return confArr.map((v,i)=>{
    const load = v + (showPotential ? (potArr[i]||0) : 0);
    return capArr[i] ? (100 * load / capArr[i]) : 0;
  });
}

// Build discipline selector
function populateDisciplines(){
  sel.innerHTML = "";
  for(const d of DATA.departments){
    const o=document.createElement('option');
    o.value=d.Key; o.textContent=d.Name; sel.appendChild(o);
  }
  // default pick first with any demand; else first item
  sel.value = DATA.departments[0]?.Key || "";
}

// Global charts
let mainChart = null;
let utilChart = null;

// Today line (weekly only)
function todayLabelWeekly(){
  const m = mondayOf(new Date());
  return formatDateLocal(m);
}

// Compose series for current selection
function buildSeriesFor(key, labels, mode){
  const conf = computeLoadsDetailed(DATA.projects, key, labels, mode);
  const pot  = computeLoadsDetailed(DATA.potential, key, labels, mode);
  const cap  = capacitySeries(key, labels, mode);
  return {conf, pot, cap};
}

// Rebuild everything (after data change or setting change)
function rebuildEverything(){
  populateDisciplines();
  updateVisuals();
}

let currentKey = null;
let lastClickY = null; // For anchoring modals

function updateVisuals(){
  currentKey = sel.value || (DATA.departments[0]?.Key || "");
  const labels = (timelineMode==='weekly') ? getWeeklyLabels() : getMonthlyLabels();
  const { conf, pot, cap } = buildSeriesFor(currentKey, labels, timelineMode);

  const labelText = (timelineMode==='weekly') ? 'Week Starting' : 'Month (workdays)';
  const xLabels = labels;

  // MAIN CHART
  const brand       = getComputedStyle(document.documentElement).getPropertyValue('--brand').trim();
  const brand20     = getComputedStyle(document.documentElement).getPropertyValue('--brand-20').trim();
  const capacity    = getComputedStyle(document.documentElement).getPropertyValue('--capacity').trim();
  const capacity20  = getComputedStyle(document.documentElement).getPropertyValue('--capacity-20').trim();
  const potential   = getComputedStyle(document.documentElement).getPropertyValue('--potential').trim();
  const potential20 = getComputedStyle(document.documentElement).getPropertyValue('--potential-20').trim();

  const mainCtx = document.getElementById('mainChart').getContext('2d');
  if(mainChart) mainChart.destroy();

  const annos = (timelineMode==='weekly') ? {
    annotations:{
      todayLine:{
        type:'line',
        xMin: todayLabelWeekly(),
        xMax: todayLabelWeekly(),
        borderColor:'#9ca3af', borderWidth:1, borderDash:[4,4],
        label:{ display:true, content:'Today', position:'start', color:'#6b7280', backgroundColor:'rgba(255,255,255,0.8)' }
      }
    }
  } : { annotations:{} };

  mainChart = new Chart(mainCtx,{
    type:'line',
    data:{
      labels: xLabels,
      datasets:[
        { // 0 Confirmed
          label: ()=> `${(DATA.departments.find(d=>d.Key===currentKey)?.Name)||currentKey} Load (hrs)`,
          data: conf.weeklyTotal,
          borderColor: brand,
          backgroundColor: brand20,
          borderWidth:2, fill:true, tension:0.1, pointRadius:0
        },
        { // 1 Capacity
          label: ()=> `${(DATA.departments.find(d=>d.Key===currentKey)?.Name)||currentKey} Capacity (hrs)`,
          data: cap,
          borderColor: capacity,
          backgroundColor: capacity20,
          borderWidth:2, fill:false, borderDash:[6,6], tension:0.1, pointRadius:0
        },
        { // 2 Potential
          label: ()=> `${(DATA.departments.find(d=>d.Key===currentKey)?.Name)||currentKey} Potential (hrs)`,
          data: pot.weeklyTotal,
          borderColor: potential,
          backgroundColor: potential20,
          borderWidth:2, fill:true, tension:0.1, pointRadius:0,
          hidden: !showPotential
        }
      ]
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      interaction:{ mode:'index', intersect:false },
      scales:{
        x:{ title:{display:true, text:labelText} },
        y:{ title:{display:true, text:'Hours'}, beginAtZero:true }
      },
      plugins:{
        annotation: annos,
        legend:{ position:'top' },
        title:{ display:true, text: ()=>'Load vs. Capacity - ' + ((DATA.departments.find(d=>d.Key===currentKey)?.Name)||currentKey) }
      },
      onClick:(evt, elems)=>{
        if(!elems||!elems.length) return;
        // capture click Y for anchoring
        lastClickY = (evt?.native?.clientY ?? evt?.clientY ?? null);

        const {datasetIndex, index:idx} = elems[0];
        if(datasetIndex===1) return; // ignore capacity
        const title = (timelineMode==='weekly' ? `Week ${xLabels[idx]}` : `Month ${xLabels[idx]}`) + ` · ${ (DATA.departments.find(d=>d.Key===currentKey)?.Name)||currentKey }`;

        if(showPotential){
          // Combine by customer label
          const map = new Map();
          (conf.breakdown[idx]||[]).forEach(r=>{
            map.set(r.customer, {conf:r.hours, pot:0});
          });
          (pot.breakdown[idx]||[]).forEach(r=>{
            if(!map.has(r.customer)) map.set(r.customer, {conf:0, pot:r.hours});
            else { const o=map.get(r.customer); o.pot += r.hours; }
          });

          const rows = Array.from(map.entries()).map(([customer,vals])=>({
            customer, conf: vals.conf, pot: vals.pot, total: vals.conf + vals.pot
          })).sort((a,b)=> b.total - a.total);

          openModalCombined(title, rows);
        }else{
          const rows = (datasetIndex===0 ? conf.breakdown[idx] : pot.breakdown[idx]) || [];
          // Sort desc by hours
          const rowsSorted = rows.slice().sort((a,b)=> b.hours - a.hours);
          openModalSingle(title, rowsSorted);
        }
      }
    }
  });

  // UTILIZATION CHART
  const utilCtx = document.getElementById('utilChart').getContext('2d');
  if(utilChart) utilChart.destroy();
  const utilData = utilizationArray(currentKey, conf.weeklyTotal, pot.weeklyTotal, cap);
  utilChart = new Chart(utilCtx, {
    type:'line',
    data:{
      labels: xLabels,
      datasets:[
        {
          label: 'Utilization %',
          data: utilData,
          borderColor:'#374151',
          backgroundColor:'rgba(55,65,81,0.10)',
          borderWidth:1.8, fill:true, tension:0.1, pointRadius:0
        }
      ]
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      scales:{
        x:{ title:{display:true, text:labelText} },
        y:{ title:{display:true, text:'% Utilization'}, beginAtZero:true, suggestedMax:150 }
      },
      plugins:{
        legend:{ display:false },
        annotation:{
          annotations:{
            ref100:{
              type:'line', yMin:100, yMax:100, borderColor:'#9ca3af', borderWidth:1, borderDash:[6,6],
              label:{ display:true, content:'100%', position:'end', color:'#6b7280', backgroundColor:'rgba(255,255,255,0.8)'}
            }
          }
        }
      }
    }
  });

  // KPIs
  const capPer = cap[0] || 0;
  let combined = conf.weeklyTotal.map((v,i)=> v + (showPotential ? (pot.weeklyTotal[i]||0) : 0));
  let peak=0, peakIdx=0;
  for(let i=0;i<combined.length;i++){
    const u = cap[i] ? (combined[i]/cap[i]*100) : 0;
    if(u>peak){ peak=u; peakIdx=i; }
  }
  let worstDiff = -Infinity, worstIdx = 0;
  for(let i=0;i<combined.length;i++){
    const diff = combined[i] - cap[i];
    if(diff>worstDiff){ worstDiff=diff; worstIdx=i; }
  }
  document.getElementById('peakUtil').textContent = `${peak.toFixed(0)}% (${labelText.split(' ')[0]} ${xLabels[peakIdx]||'—'})`;
  const status = worstDiff>=0 ? `+${worstDiff.toFixed(0)} hrs over` : `${(-worstDiff).toFixed(0)} hrs under`;
  document.getElementById('worstWeek').textContent = `${labelText.split(' ')[0]} ${xLabels[worstIdx]||'—'} · ${status}`;
  // capacity per period:
  document.getElementById('weeklyCap').textContent = `${(capPer).toFixed(0)} hrs / ${labelText.split(' ')[0].toLowerCase()}`;
}

// Controls
sel.addEventListener('change', ()=> updateVisuals());
timelineSel.addEventListener('change', e=>{ timelineMode = e.target.value; updateVisuals(); });
chkPot.addEventListener('change', e=>{ showPotential = e.target.checked; updateVisuals(); });

prodSlider.addEventListener('input', e=>{
  PRODUCTIVITY_FACTOR = parseFloat(e.target.value||'0.85'); prodVal.textContent = PRODUCTIVITY_FACTOR.toFixed(2);
  updateVisuals();
});
hoursInput.addEventListener('change', e=>{
  const v = parseInt(e.target.value||'40',10);
  HOURS_PER_FTE = isNaN(v) ? 40 : clamp(v, 30, 60);
  e.target.value = HOURS_PER_FTE;
  updateVisuals();
});

// ===== Modal (anchored near click) =====
const backdrop = document.getElementById('modalBackdrop');
const modal = document.getElementById('drilldownModal');
const modalTitle = document.getElementById('modalTitle');
const modalHead = document.getElementById('modalHead');
const modalBody = document.getElementById('modalBody');
document.getElementById('closeModal').addEventListener('click', closeModal);
backdrop.addEventListener('click', closeModal);

function positionModalNearClick(){
  // Measure to compute a good top position near the click, clamped to viewport
  const minPad = 16;
  const defaultTop = Math.round(window.innerHeight * 0.16);
  // pre-display to get height
  modal.style.visibility = 'hidden';
  modal.style.display = 'block';
  const mh = modal.getBoundingClientRect().height || 360;
  let topPx = defaultTop;
  if(lastClickY != null){
    // try to anchor ~a bit above the click
    topPx = Math.round(lastClickY - mh * 0.35);
  }
  topPx = clamp(topPx, minPad, window.innerHeight - mh - minPad);
  modal.style.top = topPx + 'px';
  // show
  modal.style.visibility = 'visible';
}

function openModalSingle(title, rows){
  modalTitle.textContent = title;
  modalHead.innerHTML = "<tr><th>Customer / Project</th><th>Hours</th></tr>";
  modalBody.innerHTML = (rows&&rows.length)
    ? rows.map(r=>`<tr><td>${r.customer}</td><td>${r.hours.toFixed(1)}</td></tr>`).join('')
    : `<tr><td colspan="2">No data</td></tr>`;
  backdrop.style.display='block';
  positionModalNearClick();
}
function openModalCombined(title, rows){
  modalTitle.textContent = title + " · Confirmed + Potential";
  modalHead.innerHTML = "<tr><th>Customer / Project</th><th>Confirmed</th><th>Potential</th><th>Total</th></tr>";
  modalBody.innerHTML = (rows&&rows.length)
    ? rows.map(r=>`<tr><td>${r.customer}</td><td>${r.conf.toFixed(1)}</td><td>${r.pot.toFixed(1)}</td><td>${r.total.toFixed(1)}</td></tr>`).join('')
    : `<tr><td colspan="4">No data</td></tr>`;
  backdrop.style.display='block';
  positionModalNearClick();
}
function closeModal(){
  backdrop.style.display='none'; modal.style.display='none';
  lastClickY = null;
}

// Initial render
rebuildEverything();

</script>
</body>
</html>
"""

# Render the HTML code in the Streamlit app.
components.html(html_code, height=1200, scrolling=False)
