import{i as e}from"./chunk-DseTPa7n.js";import{t}from"./jsx-runtime-BuabnPLX.js";import{t as n}from"./classnames-MYlGWOUq.js";import{t as r}from"./SvgIcon-DK-x56iF.js";import{t as i}from"./full-validate-tbjPXq7-.js";import{t as a}from"./full-clear-QmSxd4ht.js";import{t as o}from"./stroke-wrong-ChU_uE-6.js";var s=e(n(),1),c=``+new URL(`full-ellipse-nprA6jem.svg`,import.meta.url).href,l=`_container_15z7y_1`,u=`_line_15z7y_21`,d=`_step_15z7y_77`,f={container:l,"icon-line-container":`_icon-line-container_15z7y_6`,"icon-container":`_icon-container_15z7y_15`,line:u,"line-error":`_line-error_15z7y_32`,"line-success":`_line-success_15z7y_38`,"line-disabled":`_line-disabled_15z7y_43`,"line-waiting":`_line-waiting_15z7y_44`,"icon-error":`_icon-error_15z7y_48`,"icon-success":`_icon-success_15z7y_54`,"icon-waiting":`_icon-waiting_15z7y_60`,"icon-disabled":`_icon-disabled_15z7y_66`,"icon-wrong":`_icon-wrong_15z7y_73`,step:d,"step-content":`_step-content_15z7y_85`,"step-content-last":`_step-content-last_15z7y_91`},p=t(),m=function(e){return e.SUCCESS=`SUCCESS`,e.ERROR=`ERROR`,e.WAITING=`WAITING`,e.DISABLED=`DISABLED`,e.CANCELLED=`CANCELLED`,e.REFUSED=`REFUSED`,e}({}),h=e=>{switch(e){case m.SUCCESS:return(0,p.jsx)(r,{src:i,alt:`Étape en succès`,className:f[`icon-success`]});case m.ERROR:return(0,p.jsx)(r,{src:a,alt:`Étape en erreur`,className:f[`icon-error`]});case m.WAITING:return(0,p.jsx)(r,{src:c,alt:`Étape en attente`,className:f[`icon-waiting`]});case m.DISABLED:return(0,p.jsx)(r,{src:c,alt:`Étape non disponible`,className:f[`icon-disabled`]});case m.CANCELLED:return(0,p.jsx)(r,{src:a,alt:`Étape annulée`,className:f[`icon-error`]});case m.REFUSED:return(0,p.jsx)(r,{src:o,className:f[`icon-wrong`],alt:`Étape refusée`});default:throw Error(`Unsupported step type: ${e}`)}},g=(e,t)=>{if(t!==void 0){if(e===m.ERROR)return(0,s.default)(f.line,f[`line-error`]);if(e===m.SUCCESS)return(0,s.default)(f.line,f[`line-success`]);if(e===m.WAITING)return(0,s.default)(f.line,f[`line-waiting`]);switch(t){case m.SUCCESS:return(0,s.default)(f.line,f[`line-success`]);case m.ERROR:return(0,s.default)(f.line,f[`line-error`]);case m.WAITING:return(0,s.default)(f.line,f[`line-waiting`]);case m.DISABLED:return(0,s.default)(f.line,f[`line-disabled`]);default:return}}},_=({steps:e})=>(0,p.jsx)(`ol`,{className:f.container,children:e.map((t,n)=>{let r=e[n+1]?.type,i=n===e.length-1;return(0,p.jsxs)(`li`,{className:f.step,children:[(0,p.jsxs)(`div`,{className:f[`icon-line-container`],children:[(0,p.jsx)(`div`,{className:f[`icon-container`],children:h(t.type)}),(0,p.jsx)(`div`,{className:g(t.type,r)})]}),(0,p.jsx)(`div`,{className:(0,s.default)(f[`step-content`],{[f[`step-content-last`]]:i}),children:t.content})]},`${t.type}-${n}`)})});try{m.displayName=`TimelineStepType`,m.__docgenInfo={description:`Enum for the types of steps in the timeline.`,displayName:`TimelineStepType`,props:{}}}catch{}try{_.displayName=`Timeline`,_.__docgenInfo={description:`The Timeline component is used to display a sequence of steps in a timeline.
Each step can represent different statuses such as success, error, waiting, etc.

---
**Important: Use the \`steps\` prop to provide the list of steps in the timeline.**
---`,displayName:`Timeline`,props:{steps:{defaultValue:null,description:`An array of timeline steps to be displayed.`,name:`steps`,required:!0,type:{name:`TimelineStep[]`}}}}}catch{}var v={title:`@/ui-kit/Timeline`,component:_},y={args:{steps:[{type:m.SUCCESS,content:`Tout s’est bien passé`},{type:m.SUCCESS,content:`Ça a marché, nous sommes sauvés !`},{type:m.WAITING,content:`En attente de validation par notre PO et UX préférée`},{type:m.DISABLED,content:`Cette étape n’est pas encore disponible...`},{type:m.DISABLED,content:`Celle-ci non plus d’ailleurs`}]}},b={args:{steps:[{type:m.SUCCESS,content:`C’est l’histoire d’un homme qui tombe d’un immeuble de 50 étages`},{type:m.SUCCESS,content:`Le mec, au fur et à mesure de sa chute, il se répète sans cesse pour se rassurer : "Jusqu’ici tout va bien"`},{type:m.SUCCESS,content:`"Jusqu’ici tout va bien"`},{type:m.SUCCESS,content:`"Jusqu’ici tout va bien"`},{type:m.SUCCESS,content:`"Jusqu’ici tout va bien"`},{type:m.ERROR,content:`Mais l’important, c’est pas la chute. C’est l’atterrissage.`}]}};y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
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
}`,...y.parameters?.docs?.source}}},b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
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
}`,...b.parameters?.docs?.source}}};var x=[`Default`,`WithError`];export{y as Default,b as WithError,x as __namedExportsOrder,v as default};