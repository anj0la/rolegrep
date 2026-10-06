export async function request<T>(path:string, body?:unknown):Promise<T> {
 const response=await fetch('/api'+path,body?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}:undefined);
 const data=await response.json();
 if(!response.ok) throw new Error(typeof data.detail==='string'?data.detail:data.detail?.message??'Request failed. Check your input and backend.');
 return data;
}
