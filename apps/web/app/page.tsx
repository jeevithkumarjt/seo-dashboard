"use client";
import {useEffect,useState} from "react";
import {LineChart,Line,XAxis,YAxis,Tooltip,ResponsiveContainer,CartesianGrid} from "recharts";

const API=process.env.NEXT_PUBLIC_API_BASE_URL||"http://localhost:8000";

type Site={id:number;name:string;url:string;verified_at:string|null};
type Dashboard={site:Site;rank:any[];cwv:any[];gsc:any[]};

function State({source,last,error}:{source:string;last?:string|null;error?:string|null}) {
  return <div className="text-sm muted">
    <div>Source: {source}</div>
    <div>Last successful: {last ? new Date(last).toLocaleString() : "Never"}</div>
    {error && <div className="mt-1 text-amber-300">Data unavailable: {error}</div>}
  </div>
}
function Card({title,children}:{title:string;children:React.ReactNode}) {
  return <section className="card p-5"><h2 className="font-semibold mb-4">{title}</h2>{children}</section>
}

export default function Home(){
 const [sites,setSites]=useState<Site[]>([]); const [siteId,setSiteId]=useState<number|null>(null);
 const [dash,setDash]=useState<Dashboard|null>(null); const [loading,setLoading]=useState(true);
 useEffect(()=>{fetch(API+"/api/v1/sites").then(r=>r.json()).then((x)=>{setSites(x); if(x[0]) setSiteId(x[0].id)}).finally(()=>setLoading(false))},[]);
 useEffect(()=>{if(siteId) fetch(API+`/api/v1/sites/${siteId}/dashboard`).then(r=>r.json()).then(setDash)},[siteId]);
 const gsc=dash?.gsc||[]; const ranks=dash?.rank||[]; const cwv=dash?.cwv||[];
 const chart=ranks.slice().reverse().map((x:any)=>({date:new Date(x.observed_at).toLocaleDateString(),rank:x.rank}));
 return <main className="min-h-screen">
  <header className="border-b border-[#1d2636] px-8 py-5 flex items-center justify-between">
   <div><div className="text-xs uppercase tracking-[.2em] muted">Internal only</div><h1 className="text-2xl font-bold">SEO Monitoring</h1></div>
   <select className="bg-[#111827] border border-[#263247] rounded-lg px-3 py-2" value={siteId??""} onChange={e=>setSiteId(Number(e.target.value))}>
    {sites.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}
   </select>
  </header>
  <div className="p-8 max-w-[1500px] mx-auto space-y-6">
   {loading && <div className="muted">Loading…</div>}
   {!loading&&!dash&&<div className="card p-8">No site data available.</div>}
   {dash && <>
    <div className="flex justify-between items-end"><div><h2 className="text-3xl font-semibold">{dash.site.name}</h2><p className="muted">{dash.site.url}</p></div><div className="text-sm">{dash.site.verified_at ? "✓ Verified" : "Not verified"}</div></div>
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      <Card title="GSC clicks"><div className="text-3xl">{gsc[0]?.clicks ?? "—"}</div><State source="Google Search Console" last={gsc[0]?.observed_at} error={!gsc.length?"No successful GSC sync":null}/></Card>
      <Card title="GSC impressions"><div className="text-3xl">{gsc[0]?.impressions ?? "—"}</div><State source="Google Search Console" last={gsc[0]?.observed_at} error={!gsc.length?"No successful GSC sync":null}/></Card>
      <Card title="Average position"><div className="text-3xl">{gsc[0]?.position ?? "—"}</div><State source="Google Search Console" last={gsc[0]?.observed_at} error={!gsc.length?"No successful GSC sync":null}/></Card>
      <Card title="Tracked keywords"><div className="text-3xl">{new Set(ranks.map(x=>x.keyword_id)).size || "—"}</div><State source="Self-built SERP scraper" last={ranks[0]?.observed_at} error={!ranks.length?"No successful rank observation":null}/></Card>
    </div>
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card title="Keyword rank history">
       {chart.length ? <div className="h-72"><ResponsiveContainer><LineChart data={chart}><CartesianGrid strokeDasharray="3 3" opacity={.2}/><XAxis dataKey="date"/><YAxis reversed/><Tooltip/><Line type="monotone" dataKey="rank" strokeWidth={2} dot={false}/></LineChart></ResponsiveContainer></div> : <State source="Self-built Playwright SERP scraper" error="No successful observations. CAPTCHA/blocked/not-found observations remain explicitly unavailable."/>}
      </Card>
      <Card title="Core Web Vitals">
       <div className="grid grid-cols-2 gap-4">
        {["lcp_ms","inp_ms","cls","fcp_ms"].map(k=><div key={k} className="bg-[#0a101a] rounded-xl p-4"><div className="muted text-xs">{k.toUpperCase()}</div><div className="text-2xl mt-2">{cwv[0]?.[k] ?? "—"}</div></div>)}
       </div>
       <div className="mt-4"><State source="PageSpeed Insights — Lighthouse / CrUX stored separately" last={cwv[0]?.observed_at} error={!cwv.length?"No successful PageSpeed observation":null}/></div>
      </Card>
    </div>
    <Card title="Google Search Console">
      {gsc.length ? <div className="overflow-auto"><table className="w-full text-sm"><thead><tr className="text-left muted"><th className="p-2">Date</th><th>Clicks</th><th>Impressions</th><th>CTR</th><th>Position</th></tr></thead><tbody>{gsc.map((x:any)=><tr key={x.id} className="border-t border-[#1d2636]"><td className="p-2">{x.start_date}</td><td>{x.clicks}</td><td>{x.impressions}</td><td>{x.ctr}</td><td>{x.position}</td></tr>)}</tbody></table></div> : <State source="Google Search Console" error="No GSC data has been successfully synchronized."/>}
    </Card>
    <Card title="Backlinks">
      <div className="text-xl">—</div>
      <State source="Google Search Console Links report only" error="Unavailable: the GSC API does not provide the complete Links UI report as a generic backlink-count API. No third-party backlink index or estimate is used."/>
    </Card>
   </>}
  </div>
 </main>
}
