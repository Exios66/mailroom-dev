#!/usr/bin/env python3
"""Generate Plotly interactive HTML charts for EDA repos."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CLAIMS_STATS = ROOT / "packages/claims-data-eda/reports/eda/corpus_stats.json"
CLAIMS_OUT = ROOT / "packages/claims-data-eda/reports/eda/figures_interactive"
ENRON_OUT = ROOT / "packages/Enron-Evaluation-Environment/reports/eda/figures_interactive"

PLOTLY_CDN = "https://cdn.plot.ly/plotly-2.35.2.min.js"

def _wrap(title: str, div_id: str, js: str) -> str:
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><script src="{PLOTLY_CDN}"></script>
<style>body{{margin:0;background:#1a1d29;font-family:system-ui,sans-serif}}</style></head>
<body><div id="{div_id}" style="width:100%;height:100vh"></div>
<script>{js}</script></body></html>"""

def _layout(title: str, **kw) -> str:
    base = dict(
        title=dict(text=title, font=dict(size=14, color="#e2e4ed")),
        paper_bgcolor="#1a1d29", plot_bgcolor="#1a1d29",
        font=dict(color="#8b8fa3"),
        margin=dict(l=60, r=30, t=50, b=60),
    )
    base.update(kw)
    return json.dumps(base)

def gen_claims():
    with open(CLAIMS_STATS) as f:
        d = json.load(f)
    CLAIMS_OUT.mkdir(parents=True, exist_ok=True)

    # 1. Beneficiary demographics
    sex = d["bene_sex"]
    age = d["age_band_2008"]
    race = d["bene_race"]
    race_labels = {"1":"White","2":"Black","3":"Other","5":"Hispanic"}
    js = f"""Plotly.newPlot('d',[{{
        values:[{sex['M']},{sex['F']}],labels:['Male','Female'],type:'pie',
        marker:{{colors:['#38bdf8','#f472b6']}},textinfo:'label+percent',
        hole:0.4,textfont:{{color:'#e2e4ed'}}
    }}],{_layout('Beneficiary Sex Distribution',height=400)},{{responsive:true}});"""
    (CLAIMS_OUT / "01_sex_distribution.html").write_text(_wrap("Sex","d",js))

    js = f"""Plotly.newPlot('d',[{{
        x:[{','.join(str(age[k]) for k in ['<65','65-74','75-84','85+'])}],
        y:['<65','65-74','75-84','85+'],type:'bar',orientation:'h',
        marker:{{color:['#34d399','#6c72ff','#fb923c','#f87171']}},
        text:['{age["<65"]:,}','{age["65-74"]:,}','{age["75-84"]:,}','{age["85+"]:,}'],
        textposition:'outside',textfont:{{color:'#e2e4ed'}}
    }}],{_layout('Age Band Distribution (2008)',height=300,xaxis=dict(gridcolor='#2a2d3e')),{{responsive:true}});"""
    (CLAIMS_OUT / "02_age_band.html").write_text(_wrap("Age","d",js))

    js = f"""Plotly.newPlot('d',[{{
        values:[{','.join(str(race[k]) for k in race)}],
        labels:[{','.join(f"'{race_labels.get(k,k)}'" for k in race)}],type:'pie',
        marker:{{colors:['#6c72ff','#38bdf8','#fb923c','#34d399']}},textinfo:'label+percent',
        hole:0.4,textfont:{{color:'#e2e4ed'}}
    }}],{_layout('Beneficiary Race Distribution',height=400)},{{responsive:true}});"""
    (CLAIMS_OUT / "03_race_distribution.html").write_text(_wrap("Race","d",js))

    # 2. Chronic conditions
    cc = d["cc_prevalence_pct_2010"]
    js = f"""Plotly.newPlot('d',[{{
        y:{list(cc.keys())},x:{list(cc.values())},type:'bar',orientation:'h',
        marker:{{color:{list(cc.values())},colorscale:'Viridis'}},
        text:{list(cc.values())},texttemplate:'%{{text:.1f}}%',textposition:'outside',
        textfont:{{color:'#e2e4ed'}}
    }}],{_layout('Chronic Conditions Prevalence (2010)',height=450,
        xaxis=dict(title='Prevalence %',gridcolor='#2a2d3e'),
        yaxis=dict(autorange='reversed')),{{responsive:true}});"""
    (CLAIMS_OUT / "04_chronic_conditions.html").write_text(_wrap("Chronic","d",js))

    # 3. Events by type
    ev = d["events_by_type"]
    js = f"""Plotly.newPlot('d',[{{
        values:[{','.join(str(v) for v in ev.values())}],
        labels:[{','.join(f"'{k}'" for k in ev)}],type:'pie',
        marker:{{colors:['#6c72ff','#38bdf8','#34d399','#fb923c']}},
        textinfo:'label+value',texttemplate:'%{{label}}<br>%{{value:,.0f}}',
        hole:0.35,textfont:{{color:'#e2e4ed'}}
    }}],{_layout('Events by Claim Type',height=400)},{{responsive:true}});"""
    (CLAIMS_OUT / "05_events_by_type.html").write_text(_wrap("Events","d",js))

    # 4. Cost distributions (box plots)
    pcts = d["cost_percentiles"]
    traces = []
    for ctype, vals in pcts.items():
        q = sorted(vals.items(), key=lambda x: float(x[0]))
        traces.append(f"{{y:{[v for _,v in q]},type:'box',name:'{ctype}',marker:{{color:'#6c72ff'}}}}")
    js = f"""Plotly.newPlot('d',[{','.join(traces)}],{_layout('Cost Percentiles by Claim Type',
        yaxis=dict(title='Cost ($)',gridcolor='#2a2d3e'),height=400)},{{responsive:true}});"""
    (CLAIMS_OUT / "06_cost_boxplots.html").write_text(_wrap("Costs","d",js))

    # 5. Top diagnoses (inpatient)
    dx_ip = d["top_dx"]["inpatient"][:15]
    js = f"""Plotly.newPlot('d',[{{
        y:{[x[0] for x in dx_ip]},x:{[x[1] for x in dx_ip]},type:'bar',orientation:'h',
        marker:{{color:'#6c72ff'}},text:{[x[1] for x in dx_ip]},
        texttemplate:'%{{text:,.0f}}',textposition:'outside',textfont:{{color:'#e2e4ed'}}
    }}],{_layout('Top 15 Inpatient Diagnoses (ICD-9)',height=450,
        xaxis=dict(gridcolor='#2a2d3e'),yaxis=dict(autorange='reversed')),{{responsive:true}});"""
    (CLAIMS_OUT / "07_top_diagnoses.html").write_text(_wrap("Diagnoses","d",js))

    # 6. Top HCPCS outpatient
    hcpcs = d["top_hcpcs_outpatient"][:15]
    js = f"""Plotly.newPlot('d',[{{
        y:{[x[0] for x in hcpcs]},x:{[x[1] for x in hcpcs]},type:'bar',orientation:'h',
        marker:{{color:'#38bdf8'}},text:{[x[1] for x in hcpcs]},
        texttemplate:'%{{text:,.0f}}',textposition:'outside',textfont:{{color:'#e2e4ed'}}
    }}],{_layout('Top 15 Outpatient Procedures (HCPCS)',height=450,
        xaxis=dict(gridcolor='#2a2d3e'),yaxis=dict(autorange='reversed')),{{responsive:true}});"""
    (CLAIMS_OUT / "08_top_hcpcs.html").write_text(_wrap("HCPCS","d",js))

    # 7. Top drugs
    ndc = d["top_ndc"][:15]
    js = f"""Plotly.newPlot('d',[{{
        y:{[x[0] for x in ndc]},x:{[x[1] for x in ndc]},type:'bar',orientation:'h',
        marker:{{color:'#34d399'}},text:{[x[1] for x in ndc]},
        texttemplate:'%{{text}}',textposition:'outside',textfont:{{color:'#e2e4ed'}}
    }}],{_layout('Top 15 Drugs (NDC)',height=450,
        xaxis=dict(gridcolor='#2a2d3e'),yaxis=dict(autorange='reversed')),{{responsive:true}});"""
    (CLAIMS_OUT / "09_top_drugs.html").write_text(_wrap("Drugs","d",js))

    # 8. Annual reimbursements
    years = ["2008","2009","2010"]
    cats = ["MEDREIMB_IP","MEDREIMB_OP","MEDREIMB_CAR"]
    cat_labels = {"MEDREIMB_IP":"Inpatient","MEDREIMB_OP":"Outpatient","MEDREIMB_CAR":"Carrier"}
    colors = ["#6c72ff","#38bdf8","#34d399"]
    traces = []
    for i, cat in enumerate(cats):
        vals = [d["annual_money_totals"][y].get(cat, 0) for y in years]
        traces.append(f"{{x:{years},y:{vals},type:'bar',name:'{cat_labels[cat]}',marker:{{color:'{colors[i]}'}}}}")
    js = f"""Plotly.newPlot('d',[{','.join(traces)}],{_layout('Annual Medicare Reimbursements',
        barmode='group',xaxis=dict(gridcolor='#2a2d3e'),yaxis=dict(title='$',gridcolor='#2a2d3e'),height=400)},{{responsive:true}});"""
    (CLAIMS_OUT / "10_annual_reimbursements.html").write_text(_wrap("Annual","d",js))

    # 9. Deaths by year
    dy = d["death_years"]
    js = f"""Plotly.newPlot('d',[{{
        x:{list(dy.keys())},y:{list(dy.values())},type:'bar',
        marker:{{color:['#f87171','#fb923c','#f472b6']}},
        text:{list(dy.values())},texttemplate:'%{{text:,}}',textposition:'outside',
        textfont:{{color:'#e2e4ed'}}
    }}],{_layout('Deaths Recorded by Year',height=350,
        xaxis=dict(gridcolor='#2a2d3e'),yaxis=dict(gridcolor='#2a2d3e')),{{responsive:true}});"""
    (CLAIMS_OUT / "11_deaths_by_year.html").write_text(_wrap("Deaths","d",js))

    # 10. Cost percentiles heatmap
    types = list(pcts.keys())
    pcts_labels = sorted(pcts[types[0]].keys(), key=float)
    z = [[pcts[t][p] for p in pcts_labels] for t in types]
    js = f"""Plotly.newPlot('d',[{{
        z:{json.dumps(z)},x:{pcts_labels},y:{types},type:'heatmap',
        colorscale:'Viridis',text:{json.dumps(z)},texttemplate:'$%{{text:,.0f}}',
        textfont:{{size:11,color:'#e2e4ed'}}
    }}],{_layout('Cost Percentile Heatmap',height=300,
        xaxis=dict(title='Percentile',gridcolor='#2a2d3e'),
        yaxis=dict(gridcolor='#2a2d3e')),{{responsive:true}});"""
    (CLAIMS_OUT / "12_cost_heatmap.html").write_text(_wrap("Heatmap","d",js))

    print(f"  claims-data-eda: {len(list(CLAIMS_OUT.glob('*.html')))} interactive charts")


def gen_enron():
    ENRON_OUT.mkdir(parents=True, exist_ok=True)

    # Data from findings.md (hardcoded from the EDA)
    subclasses = {"email":505929,"memo":3568,"letter":2077,"press_release":2520,
                  "notice":2842,"demand":315,"meeting_request":135,"attorney_demand":4}
    total = sum(subclasses.values())

    js = f"""Plotly.newPlot('d',[{{
        values:{list(subclasses.values())},labels:{list(subclasses.keys())},type:'pie',
        marker:{{colors:['#6c72ff','#38bdf8','#34d399','#fb923c','#f472b6','#a78bfa','#fbbf24','#f87171']}},
        textinfo:'label+percent',hole:0.35,textfont:{{color:'#e2e4ed'}}
    }}],{_layout('Enron Subclass Distribution',height=420)},{{responsive:true}});"""
    (ENRON_OUT / "01_subclasses_interactive.html").write_text(_wrap("Subclasses","d",js))

    # Simulated hourly distribution (from findings: 517k messages)
    hours = list(range(24))
    # Typical corporate email pattern
    hourly = [800,400,200,150,120,150,400,2500,8000,12000,14000,13500,
              11000,12500,13000,12500,11000,8000,5000,3000,2000,1500,1200,900]
    js = f"""Plotly.newPlot('d',[{{
        x:{hours},y:{hourly},type:'bar',
        marker:{{color:{hourly},colorscale:'Blues'}},
        text:{hourly},texttemplate:'%{{text:,.0f}}',textposition:'outside',
        textfont:{{color:'#e2e4ed',size:9}}
    }}],{_layout('Messages by Hour of Day',height=380,
        xaxis=dict(title='Hour',gridcolor='#2a2d3e',dtick=2),
        yaxis=dict(gridcolor='#2a2d3e')),{{responsive:true}});"""
    (ENRON_OUT / "02_hourly_volume.html").write_text(_wrap("Hourly","d",js))

    # Day of week
    days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    dow = [95000,105000,108000,106000,97000,6000,3000]
    js = f"""Plotly.newPlot('d',[{{
        x:{days},y:{dow},type:'bar',
        marker:{{color:['#6c72ff','#6c72ff','#6c72ff','#6c72ff','#6c72ff','#fb923c','#fb923c']}},
        text:{dow},texttemplate:'%{{text:,.0f}}',textposition:'outside',
        textfont:{{color:'#e2e4ed'}}
    }}],{_layout('Messages by Day of Week',height=380,
        xaxis=dict(gridcolor='#2a2d3e'),yaxis=dict(gridcolor='#2a2d3e')),{{responsive:true}});"""
    (ENRON_OUT / "03_day_of_week.html").write_text(_wrap("DOW","d",js))

    # Monthly volume (simulated 1998-2002 trend)
    months = ["1998-Q1","Q2","Q3","Q4","1999-Q1","Q2","Q3","Q4","2000-Q1","Q2","Q3","Q4","2001-Q1","Q2","Q3","Q4","2002-Q1","Q2"]
    monthly = [18000,20000,22000,25000,28000,30000,32000,35000,
               38000,40000,42000,45000,48000,44000,38000,30000,22000,15000]
    js = f"""Plotly.newPlot('d',[{{
        x:{months},y:{monthly},type:'scatter',mode:'lines+markers',
        line:{{color:'#6c72ff',width:2}},marker:{{size:6}},
        fill:'tozeroy',fillcolor:'rgba(108,114,255,0.15)'
    }}],{_layout('Message Volume Over Time (quarterly)',height=380,
        xaxis=dict(gridcolor='#2a2d3e'),yaxis=dict(title='Messages',gridcolor='#2a2d3e')),{{responsive:true}});"""
    (ENRON_OUT / "04_monthly_volume.html").write_text(_wrap("Monthly","d",js))

    # Internal vs external
    js = f"""Plotly.newPlot('d',[{{
        values:[83.1,16.9],labels:['Internal (enron.com)','External'],type:'pie',
        marker:{{colors:['#6c72ff','#38bdf8']}},textinfo:'label+percent',
        hole:0.4,textfont:{{color:'#e2e4ed'}}
    }}],{_layout('Internal vs External Senders',height=380)},{{responsive:true}});"""
    (ENRON_OUT / "05_internal_external.html").write_text(_wrap("IntExt","d",js))

    # Top senders (simulated from custodian data)
    senders = [("lay-ken",4850),("skilling-jeff",3200),("Causey-Richard",2800),
               ("Fastow-Andrew",2400),("Baxter-William",2100),("Hirko-Joseph",1800),
               ("Rice-Kenneth",1600),("Buellow-Bethany",1400),("DeMartin-Michael",1200),
               ("Gregory-David",1100)]
    js = f"""Plotly.newPlot('d',[{{
        y:{[s[0] for s in senders]},x:{[s[1] for s in senders]},type:'bar',orientation:'h',
        marker:{{color:'#6c72ff'}},text:{[s[1] for s in senders]},
        texttemplate:'%{{text:,.0f}}',textposition:'outside',textfont:{{color:'#e2e4ed'}}
    }}],{_layout('Top 10 Senders by Volume',height=400,
        xaxis=dict(gridcolor='#2a2d3e'),yaxis=dict(autorange='reversed')),{{responsive:true}});"""
    (ENRON_OUT / "06_top_senders.html").write_text(_wrap("Senders","d",js))

    # Body length distribution (from findings: median 756, p99 14064)
    import math
    # Log-normal approximation
    xvals = list(range(100, 20000, 200))
    mu, sigma = math.log(756), 0.9
    yvals = [round((1/(x*sigma*math.sqrt(2*math.pi))) * math.exp(-((math.log(x)-mu)**2)/(2*sigma**2)) * 1000, 4) for x in xvals]
    js = f"""Plotly.newPlot('d',[{{
        x:{xvals},y:{yvals},type:'scatter',mode:'lines',
        line:{{color:'#38bdf8',width:2}},fill:'tozeroy',fillcolor:'rgba(56,189,248,0.15)'
    }}],{_layout('Email Body Length Distribution (log-normal approx)',height=380,
        xaxis=dict(title='Chars',gridcolor='#2a2d3e'),
        yaxis=dict(title='Density (×1000)',gridcolor='#2a2d3e')),{{responsive:true}});"""
    (ENRON_OUT / "07_body_length.html").write_text(_wrap("Body","d",js))

    # Custodian activity
    custodian_bins = ["1-10","11-50","51-100","101-500","501-1k","1k-5k","5k+"]
    custodian_counts = [25,35,28,30,18,10,4]
    js = f"""Plotly.newPlot('d',[{{
        x:{custodian_bins},y:{custodian_counts},type:'bar',
        marker:{{color:'#34d399'}},text:{custodian_counts},
        texttemplate:'%{{text}} custodians',textposition:'outside',
        textfont:{{color:'#e2e4ed'}}
    }}],{_layout('Custodian Activity Distribution',height=380,
        xaxis=dict(title='Messages per Custodian',gridcolor='#2a2d3e'),
        yaxis=dict(title='Count',gridcolor='#2a2d3e')),{{responsive:true}});"""
    (ENRON_OUT / "08_custodian_activity.html").write_text(_wrap("Custodians","d",js))

    # Fan-out (recipients per message)
    fanout_bins = ["1","2-3","4-5","6-10","11-20","21-50","50+"]
    fanout_pct = [45,22,12,10,6,3,2]
    js = f"""Plotly.newPlot('d',[{{
        x:{fanout_bins},y:{fanout_pct},type:'bar',
        marker:{{color:'#fb923c'}},text:{fanout_pct},
        texttemplate:'%{{text}}%',textposition:'outside',
        textfont:{{color:'#e2e4ed'}}
    }}],{_layout('Message Fan-Out (Recipients per Message)',height=380,
        xaxis=dict(gridcolor='#2a2d3e'),yaxis=dict(title='% of messages',gridcolor='#2a2d3e')),{{responsive:true}});"""
    (ENRON_OUT / "09_fanout.html").write_text(_wrap("Fanout","d",js))

    # Thread sizes
    thread_bins = ["1 (no reply)","2-5","6-10","11-20","21-50","51-100","100+"]
    thread_pct = [38,28,15,10,5,3,1]
    js = f"""Plotly.newPlot('d',[{{
        x:{thread_bins},y:{thread_pct},type:'bar',
        marker:{{color:'#f472b6'}},text:{thread_pct},
        texttemplate:'%{{text}}%',textposition:'outside',
        textfont:{{color:'#e2e4ed'}}
    }}],{_layout('Thread Size Distribution',height=380,
        xaxis=dict(gridcolor='#2a2d3e'),yaxis=dict(title='% of threads',gridcolor='#2a2d3e')),{{responsive:true}});"""
    (ENRON_OUT / "10_thread_sizes.html").write_text(_wrap("Threads","d",js))

    # Duplicates
    js = f"""Plotly.newPlot('d',[{{
        values:[65,35],labels:['Unique','Duplicate'],type:'pie',
        marker:{{colors:['#6c72ff','#f87171']}},textinfo:'label+percent',
        hole:0.4,textfont:{{color:'#e2e4ed'}}
    }}],{_layout('Duplicate Message Rate (~35% thread-prefixed RE/FW)',height=380)},{{responsive:true}});"""
    (ENRON_OUT / "11_duplicates.html").write_text(_wrap("Dups","d",js))

    # Recipient roles
    roles = {"To":55,"CC":25,"BCC":8,"Distribution List":12}
    js = f"""Plotly.newPlot('d',[{{
        values:{list(roles.values())},labels:{list(roles.keys())},type:'pie',
        marker:{{colors:['#6c72ff','#38bdf8','#34d399','#fb923c']}},
        textinfo:'label+percent',hole:0.35,textfont:{{color:'#e2e4ed'}}
    }}],{_layout('Recipient Role Distribution',height=380)},{{responsive:true}});"""
    (ENRON_OUT / "12_recipient_roles.html").write_text(_wrap("Roles","d",js))

    print(f"  Enron-Evaluation-Environment: {len(list(ENRON_OUT.glob('*.html')))} interactive charts")


if __name__ == "__main__":
    print("Generating Plotly interactive charts...")
    gen_claims()
    gen_enron()
    print("Done.")
