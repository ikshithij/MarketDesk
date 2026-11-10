export async function api<T=any>(path:string, method='GET', body?:unknown):Promise<T>{
  const response=await fetch('/api'+path,{method,headers:body?{'Content-Type':'application/json'}:undefined,body:body?JSON.stringify(body):undefined});
  const data=await response.json();
  if(!response.ok) throw new Error(typeof data.detail==='string'?data.detail:'Please check the entered values.');
  return data;
}
export const money=(n:number|null|undefined,currency='USD')=>n==null?'—':new Intl.NumberFormat('en-GB',{style:'currency',currency,maximumFractionDigits:2,notation:Math.abs(n)>=1e6?'compact':'standard'}).format(n);
export const percent=(n:number|null|undefined)=>n==null?'—':`${n>0?'+':''}${n.toFixed(1)}%`;
export const date=(value:string|undefined)=>value?new Date(value).toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric'}):'Not available';
export type Company={symbol:string;name:string;cik:string;sector:string;metrics:Record<string,number|string|null>;quote:any;fetched_at:string|null;reasons?:string[]};

export const timestamp=(value:string|undefined)=>value?new Date(value).toLocaleString('en-GB',{day:'numeric',month:'short',hour:'2-digit',minute:'2-digit',timeZoneName:'short'}):'Not available';
