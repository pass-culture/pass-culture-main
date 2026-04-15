import{i as e}from"./chunk-DseTPa7n.js";import{t}from"./jsx-runtime-BUC2lftT.js";import{t as n}from"./classnames-BHgbbynn.js";import{t as r}from"./SvgIcon-zPyG_A85.js";import{t as i}from"./full-validate-Djz4Q_HD.js";import{t as a}from"./full-clear-17rGb0a3.js";import{t as o}from"./stroke-wrong-DaWWBSmr.js";var s=e(n(),1),c=``+new URL(`full-ellipse-nprA6jem.svg`,import.meta.url).href,l={container:`_container_15z7y_1`,"icon-line-container":`_icon-line-container_15z7y_6`,"icon-container":`_icon-container_15z7y_15`,line:`_line_15z7y_21`,"line-error":`_line-error_15z7y_32`,"line-success":`_line-success_15z7y_38`,"line-disabled":`_line-disabled_15z7y_43`,"line-waiting":`_line-waiting_15z7y_44`,"icon-error":`_icon-error_15z7y_48`,"icon-success":`_icon-success_15z7y_54`,"icon-waiting":`_icon-waiting_15z7y_60`,"icon-disabled":`_icon-disabled_15z7y_66`,"icon-wrong":`_icon-wrong_15z7y_73`,step:`_step_15z7y_77`,"step-content":`_step-content_15z7y_85`,"step-content-last":`_step-content-last_15z7y_91`},u=t(),d=function(e){return e.SUCCESS=`SUCCESS`,e.ERROR=`ERROR`,e.WAITING=`WAITING`,e.DISABLED=`DISABLED`,e.CANCELLED=`CANCELLED`,e.REFUSED=`REFUSED`,e}({}),f=e=>{switch(e){case d.SUCCESS:return(0,u.jsx)(r,{src:i,alt:`Étape en succès`,className:l[`icon-success`]});case d.ERROR:return(0,u.jsx)(r,{src:a,alt:`Étape en erreur`,className:l[`icon-error`]});case d.WAITING:return(0,u.jsx)(r,{src:c,alt:`Étape en attente`,className:l[`icon-waiting`]});case d.DISABLED:return(0,u.jsx)(r,{src:c,alt:`Étape non disponible`,className:l[`icon-disabled`]});case d.CANCELLED:return(0,u.jsx)(r,{src:a,alt:`Étape annulée`,className:l[`icon-error`]});case d.REFUSED:return(0,u.jsx)(r,{src:o,className:l[`icon-wrong`],alt:`Étape refusée`});default:throw Error(`Unsupported step type: ${e}`)}},p=(e,t)=>{if(t!==void 0){if(e===d.ERROR)return(0,s.default)(l.line,l[`line-error`]);if(e===d.SUCCESS)return(0,s.default)(l.line,l[`line-success`]);if(e===d.WAITING)return(0,s.default)(l.line,l[`line-waiting`]);switch(t){case d.SUCCESS:return(0,s.default)(l.line,l[`line-success`]);case d.ERROR:return(0,s.default)(l.line,l[`line-error`]);case d.WAITING:return(0,s.default)(l.line,l[`line-waiting`]);case d.DISABLED:return(0,s.default)(l.line,l[`line-disabled`]);default:return}}},m=({steps:e})=>(0,u.jsx)(`ol`,{className:l.container,children:e.map((t,n)=>{let r=e[n+1]?.type,i=n===e.length-1;return(0,u.jsxs)(`li`,{className:l.step,children:[(0,u.jsxs)(`div`,{className:l[`icon-line-container`],children:[(0,u.jsx)(`div`,{className:l[`icon-container`],children:f(t.type)}),(0,u.jsx)(`div`,{className:p(t.type,r)})]}),(0,u.jsx)(`div`,{className:(0,s.default)(l[`step-content`],{[l[`step-content-last`]]:i}),children:t.content})]},`${t.type}-${n}`)})});try{d.displayName=`TimelineStepType`,d.__docgenInfo={description:`Enum for the types of steps in the timeline.`,displayName:`TimelineStepType`,props:{}}}catch{}try{m.displayName=`Timeline`,m.__docgenInfo={description:`The Timeline component is used to display a sequence of steps in a timeline.
Each step can represent different statuses such as success, error, waiting, etc.

---
**Important: Use the \`steps\` prop to provide the list of steps in the timeline.**
---`,displayName:`Timeline`,props:{steps:{defaultValue:null,description:`An array of timeline steps to be displayed.`,name:`steps`,required:!0,type:{name:`TimelineStep[]`}}}}}catch{}var h={title:`@/ui-kit/Timeline`,component:m},g={args:{steps:[{type:d.SUCCESS,content:`Tout s’est bien passé`},{type:d.SUCCESS,content:`Ça a marché, nous sommes sauvés !`},{type:d.WAITING,content:`En attente de validation par notre PO et UX préférée`},{type:d.DISABLED,content:`Cette étape n’est pas encore disponible...`},{type:d.DISABLED,content:`Celle-ci non plus d’ailleurs`}]}},_={args:{steps:[{type:d.SUCCESS,content:`C’est l’histoire d’un homme qui tombe d’un immeuble de 50 étages`},{type:d.SUCCESS,content:`Le mec, au fur et à mesure de sa chute, il se répète sans cesse pour se rassurer : "Jusqu’ici tout va bien"`},{type:d.SUCCESS,content:`"Jusqu’ici tout va bien"`},{type:d.SUCCESS,content:`"Jusqu’ici tout va bien"`},{type:d.SUCCESS,content:`"Jusqu’ici tout va bien"`},{type:d.ERROR,content:`Mais l’important, c’est pas la chute. C’est l’atterrissage.`}]}};g.parameters={...g.parameters,docs:{...g.parameters?.docs,source:{originalSource:`{
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
}`,...g.parameters?.docs?.source}}},_.parameters={..._.parameters,docs:{..._.parameters?.docs,source:{originalSource:`{
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
}`,..._.parameters?.docs?.source}}};var v=[`Default`,`WithError`];export{g as Default,_ as WithError,v as __namedExportsOrder,h as default};