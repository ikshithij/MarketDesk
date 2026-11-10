import {useEffect,useRef} from 'react';
import {createChart,ColorType,AreaSeries,CandlestickSeries,LineSeries} from 'lightweight-charts';
export default function Chart({bars,kind='area',compare=false}:{bars:any[];kind?:string;compare?:boolean}){
 const ref=useRef<HTMLDivElement>(null);
 useEffect(()=>{
  if(!ref.current||!bars.length)return;
  const chart=createChart(ref.current,{autoSize:true,height:300,layout:{background:{type:ColorType.Solid,color:'transparent'},textColor:'#849093',fontFamily:'Inter, sans-serif',attributionLogo:true},grid:{vertLines:{visible:false},horzLines:{color:'#263239'}},rightPriceScale:{borderVisible:false},timeScale:{borderVisible:false,timeVisible:typeof bars[0]?.time==='number',secondsVisible:false},crosshair:{vertLine:{color:'#6cbcb1'},horzLine:{color:'#6cbcb1'}}});
  if(kind==='candles')chart.addSeries(CandlestickSeries,{upColor:'#81c9b8',downColor:'#e99b8e',borderVisible:false,wickUpColor:'#81c9b8',wickDownColor:'#e99b8e'}).setData(bars);
  else chart.addSeries(AreaSeries,{lineColor:'#8fd5bd',topColor:'#8fd5bd22',bottomColor:'#8fd5bd00',lineWidth:2}).setData(bars.map(b=>({time:b.time,value:b.value??b.close})));
  if(compare)chart.addSeries(LineSeries,{color:'#a8a0e8',lineWidth:2}).setData(bars.map(b=>({time:b.time,value:b.benchmark})));
  chart.timeScale().fitContent();return()=>chart.remove();
 },[bars,kind,compare]);
 return <div ref={ref} className="chart" aria-label="Interactive financial chart"/>;
}
