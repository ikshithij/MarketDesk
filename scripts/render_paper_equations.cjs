// Run with the bundled document runtime and NODE_PATH from load_workspace_dependencies.
const fs = require('node:fs');
const path = require('node:path');
const sharp = require('sharp');
const {mathjax}=require('mathjax-full/js/mathjax.js');
const {TeX}=require('mathjax-full/js/input/tex.js');
const {SVG}=require('mathjax-full/js/output/svg.js');
const {liteAdaptor}=require('mathjax-full/js/adaptors/liteAdaptor.js');
const {RegisterHTMLHandler}=require('mathjax-full/js/handlers/html.js');
require('mathjax-full/js/input/tex/ams/AmsConfiguration.js');
const adaptor=liteAdaptor();RegisterHTMLHandler(adaptor);
const math=mathjax.document('',{InputJax:new TeX({packages:['base','ams']}),OutputJax:new SVG({fontCache:'local'})});
(async()=>{
 const source=fs.readFileSync(process.argv[2],'utf8');const out=process.argv[3];fs.mkdirSync(out,{recursive:true});
 const equations=[...source.matchAll(/\$\$([\s\S]*?)\$\$/g)];
 const sizes=[];
 for(let i=0;i<equations.length;i++){
  const latex=equations[i][1].trim();const html=adaptor.outerHTML(math.convert(latex,{display:true}));
  let svg=html.slice(html.indexOf('<svg'),html.indexOf('</svg>')+6).replace(/currentColor/g,'#000000');
  if(!svg.includes('xmlns='))svg=svg.replace('<svg ','<svg xmlns="http://www.w3.org/2000/svg" ');
  let originalWidth=0;
  svg=svg.replace(/(width|height)="([0-9.]+)(ex|em)"/g,(_,attr,num)=>{const px=Number(num)*8.5;if(attr==='width')originalWidth=px;return `${attr}="${px}px"`});
  const name=`equation-${i+1}.png`;await sharp(Buffer.from(svg),{density:400}).png().toFile(path.join(out,name));
  sizes.push({file:name,width_inches:Math.min(6.8,Math.max(1.7,originalWidth/76)),latex});
 }
 fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify(sizes,null,2));
 process.stdout.write(`Rendered ${equations.length} equations\n`);
})().catch(e=>{process.stderr.write(String(e));process.exit(1)});
