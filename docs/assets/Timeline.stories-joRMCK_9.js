import{i as e,s as t}from"./preload-helper-Cs4UwXAW.js";import{t as n}from"./jsx-runtime-C1HxNEhm.js";import{t as r}from"./classnames-KziLZib3.js";import{n as i,t as a}from"./SvgIcon-B_ThAUcg.js";import{n as o,t as s}from"./full-validate-8NO6zJ3p.js";import{n as c,t as l}from"./full-clear-DmkYaWP6.js";import{n as u,t as d}from"./stroke-wrong-Cr-2hjg2.js";var f,p=e((()=>{f=``+new URL(`full-ellipse-nprA6jem.svg`,import.meta.url).href})),m,h,g,_,v=e((()=>{m=`_container_15z7y_1`,h=`_line_15z7y_21`,g=`_step_15z7y_77`,_={container:m,"icon-line-container":`_icon-line-container_15z7y_6`,"icon-container":`_icon-container_15z7y_15`,line:h,"line-error":`_line-error_15z7y_32`,"line-success":`_line-success_15z7y_38`,"line-disabled":`_line-disabled_15z7y_43`,"line-waiting":`_line-waiting_15z7y_44`,"icon-error":`_icon-error_15z7y_48`,"icon-success":`_icon-success_15z7y_54`,"icon-waiting":`_icon-waiting_15z7y_60`,"icon-disabled":`_icon-disabled_15z7y_66`,"icon-wrong":`_icon-wrong_15z7y_73`,step:g,"step-content":`_step-content_15z7y_85`,"step-content-last":`_step-content-last_15z7y_91`}})),y,b,x,S,C,w,T=e((()=>{y=t(r(),1),c(),p(),o(),d(),i(),v(),b=n(),x=function(e){return e.SUCCESS=`SUCCESS`,e.ERROR=`ERROR`,e.WAITING=`WAITING`,e.DISABLED=`DISABLED`,e.CANCELLED=`CANCELLED`,e.REFUSED=`REFUSED`,e}({}),S=e=>{switch(e){case`SUCCESS`:return(0,b.jsx)(a,{src:s,alt:`Étape en succès`,className:_[`icon-success`]});case`ERROR`:return(0,b.jsx)(a,{src:l,alt:`Étape en erreur`,className:_[`icon-error`]});case`WAITING`:return(0,b.jsx)(a,{src:f,alt:`Étape en attente`,className:_[`icon-waiting`]});case`DISABLED`:return(0,b.jsx)(a,{src:f,alt:`Étape non disponible`,className:_[`icon-disabled`]});case`CANCELLED`:return(0,b.jsx)(a,{src:l,alt:`Étape annulée`,className:_[`icon-error`]});case`REFUSED`:return(0,b.jsx)(a,{src:u,className:_[`icon-wrong`],alt:`Étape refusée`});default:throw Error(`Unsupported step type: ${e}`)}},C=(e,t)=>{if(t!==void 0){if(e===`ERROR`)return(0,y.default)(_.line,_[`line-error`]);if(e===`SUCCESS`)return(0,y.default)(_.line,_[`line-success`]);if(e===`WAITING`)return(0,y.default)(_.line,_[`line-waiting`]);switch(t){case`SUCCESS`:return(0,y.default)(_.line,_[`line-success`]);case`ERROR`:return(0,y.default)(_.line,_[`line-error`]);case`WAITING`:return(0,y.default)(_.line,_[`line-waiting`]);case`DISABLED`:return(0,y.default)(_.line,_[`line-disabled`]);default:return}}},w=({steps:e})=>(0,b.jsx)(`ol`,{className:_.container,children:e.map((t,n)=>{let r=e[n+1]?.type,i=n===e.length-1;return(0,b.jsxs)(`li`,{className:_.step,children:[(0,b.jsxs)(`div`,{className:_[`icon-line-container`],children:[(0,b.jsx)(`div`,{className:_[`icon-container`],children:S(t.type)}),(0,b.jsx)(`div`,{className:C(t.type,r)})]}),(0,b.jsx)(`div`,{className:(0,y.default)(_[`step-content`],{[_[`step-content-last`]]:i}),children:t.content})]},`${t.type}-${n}`)})});try{w.displayName=`Timeline`,w.__docgenInfo={description:`The Timeline component is used to display a sequence of steps in a timeline.
Each step can represent different statuses such as success, error, waiting, etc.

---
**Important: Use the \`steps\` prop to provide the list of steps in the timeline.**
---`,displayName:`Timeline`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/Timeline/Timeline.tsx`,methods:[],props:{steps:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Timeline/Timeline.tsx`,name:`TimelineProps`}],description:`An array of timeline steps to be displayed.`,name:`steps`,parent:{fileName:`pro/src/ui-kit/Timeline/Timeline.tsx`,name:`TimelineProps`},required:!0,tags:{},type:{name:`TimelineStep[]`}}},tags:{param:`props - The props for the Timeline component.`,returns:`The rendered Timeline component.`,example:`<Timeline
  steps={[
    { type: TimelineStepType.SUCCESS, content: 'Step 1 completed' },
    { type: TimelineStepType.ERROR, content: 'Step 2 failed' },
    { type: TimelineStepType.WAITING, content: 'Step 3 pending' }
  ]}
/>`}}}catch{}})),E,D,O,k;e((()=>{T(),E={title:`@/ui-kit/Timeline`,component:w},D={args:{steps:[{type:x.SUCCESS,content:`Tout s’est bien passé`},{type:x.SUCCESS,content:`Ça a marché, nous sommes sauvés !`},{type:x.WAITING,content:`En attente de validation par notre PO et UX préférée`},{type:x.DISABLED,content:`Cette étape n’est pas encore disponible...`},{type:x.DISABLED,content:`Celle-ci non plus d’ailleurs`}]}},O={args:{steps:[{type:x.SUCCESS,content:`C’est l’histoire d’un homme qui tombe d’un immeuble de 50 étages`},{type:x.SUCCESS,content:`Le mec, au fur et à mesure de sa chute, il se répète sans cesse pour se rassurer : "Jusqu’ici tout va bien"`},{type:x.SUCCESS,content:`"Jusqu’ici tout va bien"`},{type:x.SUCCESS,content:`"Jusqu’ici tout va bien"`},{type:x.SUCCESS,content:`"Jusqu’ici tout va bien"`},{type:x.ERROR,content:`Mais l’important, c’est pas la chute. C’est l’atterrissage.`}]}},D.parameters={...D.parameters,docs:{...D.parameters?.docs,source:{originalSource:`{
  args: {
    steps: [{
      type: TimelineStepType.SUCCESS,
      content: 'Tout s’est bien passé'
    }, {
      type: TimelineStepType.SUCCESS,
      content: 'Ça a marché, nous sommes sauvés !'
    }, {
      type: TimelineStepType.WAITING,
      content: 'En attente de validation par notre PO et UX préférée'
    }, {
      type: TimelineStepType.DISABLED,
      content: 'Cette étape n’est pas encore disponible...'
    }, {
      type: TimelineStepType.DISABLED,
      content: 'Celle-ci non plus d’ailleurs'
    }]
  }
}`,...D.parameters?.docs?.source}}},O.parameters={...O.parameters,docs:{...O.parameters?.docs,source:{originalSource:`{
  args: {
    steps: [{
      type: TimelineStepType.SUCCESS,
      content: 'C’est l’histoire d’un homme qui tombe d’un immeuble de 50 étages'
    }, {
      type: TimelineStepType.SUCCESS,
      content: 'Le mec, au fur et à mesure de sa chute, il se répète sans cesse pour se rassurer : "Jusqu’ici tout va bien"'
    }, {
      type: TimelineStepType.SUCCESS,
      content: '"Jusqu’ici tout va bien"'
    }, {
      type: TimelineStepType.SUCCESS,
      content: '"Jusqu’ici tout va bien"'
    }, {
      type: TimelineStepType.SUCCESS,
      content: '"Jusqu’ici tout va bien"'
    }, {
      type: TimelineStepType.ERROR,
      content: 'Mais l’important, c’est pas la chute. C’est l’atterrissage.'
    }]
  }
}`,...O.parameters?.docs?.source}}},k=[`Default`,`WithError`]}))();export{D as Default,O as WithError,k as __namedExportsOrder,E as default};