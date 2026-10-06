import type {Decision} from './types';
const value=(text:string|null)=>text??'Unknown';
export function JobDecision({decision}:{decision:Decision}) {
 const {job,eligibility,match}=decision;
 return <section aria-label="Job decision"><h2>{value(job.title)}</h2><p>{value(job.company)} · {value(job.location)}</p>
 <p><strong>{match.overall===null?'Score unavailable':`${match.overall}% provisional fixture match`}</strong> · Eligibility: {eligibility.status}</p>
 <p>{match.explanation}</p><p>Qualification: {match.qualification??'Unknown'} · Personal fit: {match.personal}</p>
 <dl>{Object.entries({Level:job.level,Arrangement:job.arrangement,Education:job.education,Salary:job.salary,Deadline:job.deadline,'Posted at':job.posted_at,'Cover letter':job.cover_letter}).map(([key,val])=><div key={key}><dt>{key}</dt><dd>{value(val)}</dd></div>)}</dl>
 <h3>Experience wording</h3>{job.experience.length?job.experience.map((r,i)=><p key={i}>{r.kind}: {r.wording}</p>):<p>Unknown</p>}
 {Object.entries({'Eligibility reasons':eligibility.reasons,'Strong evidence':match.strong,'Partial evidence':match.partial,'Gaps':match.gaps,'Concerns':match.concerns,'Extraction limitations':job.limitations}).map(([label,items])=><div key={label}><h3>{label}</h3>{items.length?<ul>{items.map((item,i)=><li key={i}>{item}</li>)}</ul>:<p>None identified</p>}</div>)}
 {job.conflicts.map((c,i)=><div key={i}><h3>Review conflict: {c.field}</h3><p>{c.values.join(' / ')}</p><ul>{c.evidence.map((e,j)=><li key={j}>{e}</li>)}</ul></div>)}
 {job.application_url&&<a href={job.application_url} target="_blank" rel="noopener noreferrer">Open application destination</a>}
 <details><summary>Retained posting and source evidence</summary><pre>{job.description}</pre>{job.sources.map((s,i)=><div key={i}><p>{s.provider} · fetched {s.fetched_at} · {s.submitted_url}</p><pre>{s.snapshot}</pre></div>)}</details>
 </section>;
}
