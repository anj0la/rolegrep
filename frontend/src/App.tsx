import {useEffect,useState} from 'react';
import {request} from './api';
import {JobDecision} from './JobDecision';
import type {Card,Decision} from './types';
export default function App(){
 const [mode,setMode]=useState('url'),[input,setInput]=useState(''),[cards,setCards]=useState<Card[]>([]),[decision,setDecision]=useState<Decision|null>(null),[error,setError]=useState(''),[busy,setBusy]=useState(false);
 const refresh=()=>request<Card[]>('/jobs').then(setCards);
 useEffect(()=>{refresh().catch(()=>setError('Start the local backend to load jobs.'));},[]);
 async function ingest(e:React.FormEvent){e.preventDefault();setBusy(true);setError('');try{setDecision(await request<Decision>('/jobs/ingest',mode==='url'?{url:input}:{text:input}));await refresh();}catch(e){setError(String(e));}finally{setBusy(false);}}
 return <main><header><h1>rolegrep</h1><p>Review a posting, then decide whether to apply.</p><aside>Phase 1 · Synthetic candidate fixture · Provisional scores · Data resets when the backend restarts.</aside></header>
 <form onSubmit={ingest}><label>Input type <select value={mode} onChange={e=>setMode(e.target.value)}><option value="url">Public Greenhouse URL</option><option value="text">Pasted job description</option></select></label><label>{mode==='url'?'Posting URL':'Job description'}<textarea required maxLength={mode==='url'?2000:40000} value={input} onChange={e=>setInput(e.target.value)} /></label><button disabled={busy}>{busy?'Reading posting…':'Review job'}</button></form>
 {error&&<p role="alert">{error} Supply a public employer Greenhouse URL or pasted description.</p>}
 <div className="layout"><section aria-label="Job inbox"><h2>Reviewed jobs</h2>{cards.length===0&&<p>No postings yet.</p>}{cards.map(card=><button className="card" key={card.id} onClick={()=>request<Decision>('/jobs/'+encodeURIComponent(card.id)).then(setDecision).catch(e=>setError(String(e)))}><strong>{card.score===null?'Unscored':`${card.score}% provisional`} · {card.title??'Title unknown'}</strong><span>{card.company??'Company unknown'} · {card.level??'Level unknown'}</span><span>{card.location??'Location unknown'} · {card.arrangement??'Arrangement unknown'}</span><span>{card.technologies.join(' · ')||'Technologies unknown'}</span><small>{card.posted_at?`Posted ${new Date(card.posted_at).toLocaleDateString()}`:'Posting date unknown'} · {card.source} · {card.eligibility}</small></button>)}</section>{decision&&<JobDecision decision={decision}/>}</div></main>;
}
