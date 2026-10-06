const fs=require('fs');
const EXISTING="behaviorism infoprocessing cogload piaget vygotsky socialcognitive situated kolb knowles mezirow sdt srl connectivism multimedia desirable bloom freire crp udl mindset expectancyvalue attribution backward svr schema rosenblatt nls chall flowerhayes writing_sociocultural math_cra math_rme skemp conceptualchange inquiry wineburg bruner_narrative dissonance maslow erikson flow bourdieu funds interactionism prospect nudge dualprocess literary_crit toulmin fallacies dewey epistemology transfer hcd dbr wtl discovery ericsson gardner_mi eisner schon agency pbl constructionism practitioner barkley dualpathway_adhd implementation adhd_strategies digital_writing formative improvement".split(' ');
const raw=fs.readFileSync('new_theories_1.js','utf8')+fs.readFileSync('new_theories_2.js','utf8');
let objs;
try{ objs=eval('[null'+raw.replace(/^\s*\/\*[\s\S]*?\*\/\s*/gm,'')+']').filter(Boolean); }
catch(e){ console.log('PARSE ERROR:',e.message); process.exit(1); }
console.log('new theories parsed:',objs.length);
const ALL=new Set([...EXISTING,...objs.map(o=>o.id)]);
console.log('total ids after patch:',ALL.size);
let bad=0;
const req=['id','name','discipline','depth','theorists','tagline','claims','constructs','applications','critiques','related','refs'];
objs.forEach(o=>{
  req.forEach(f=>{ if(!o[f]||(Array.isArray(o[f])&&!o[f].length)){console.log('  MISSING',o.id,f);bad++;} });
  (o.related||[]).forEach(r=>{ if(!ALL.has(r)){console.log('  BROKEN related:',o.id,'->',r);bad++;} });
  o.constructs.forEach(c=>{ if(!c.term||!c.def){console.log('  BAD construct in',o.id);bad++;} });
  if(o.depth!=='starter'&&o.depth!=='deep'){console.log('  BAD depth',o.id);bad++;}
});
// SUBJ check
const subjSrc=fs.readFileSync('subj.js','utf8');
const SUBJ=eval(subjSrc.replace(/^[\s\S]*?const SUBJ=/,'').replace(/;\s*$/,''));
console.log('\nSUBJ clusters:',SUBJ.length);
let cov=new Set();
SUBJ.forEach(c=>{
  c.ids.forEach(i=>{ cov.add(i); if(!ALL.has(i)){console.log('  BROKEN SUBJ id:',c.label,'->',i);bad++;} });
  console.log('  '+String(c.ids.length).padStart(2)+'  '+c.label);
});
const uncovered=[...ALL].filter(i=>!cov.has(i));
console.log('\ntheories in no subject cluster ('+uncovered.length+'):');
console.log('  '+uncovered.join(' '));
console.log('\n'+(bad===0?'ALL CHECKS PASSED':bad+' PROBLEMS'));
