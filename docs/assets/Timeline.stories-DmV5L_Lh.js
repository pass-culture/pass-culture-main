import{j as s}from"./jsx-runtime-u17CrQMm.js";import{c as i}from"./index-BDMQMPaG.js";import{f as u}from"./full-clear-Q4kCtSRL.js";import{f as _}from"./full-validate-CbMNulkZ.js";import{s as y}from"./stroke-wrong-BAouvvNg.js";import{S as o}from"./SvgIcon-DuZPzNRk.js";import"./iframe-BRW0TAsj.js";import"./preload-helper-PPVm8Dsz.js";const m=""+new URL("full-ellipse-FKO427Iz.svg",import.meta.url).href,E="_container_15z7y_1",C="_line_15z7y_21",f="_step_15z7y_77",e={container:E,"icon-line-container":"_icon-line-container_15z7y_6","icon-container":"_icon-container_15z7y_15",line:C,"line-error":"_line-error_15z7y_32","line-success":"_line-success_15z7y_38","line-disabled":"_line-disabled_15z7y_43","line-waiting":"_line-waiting_15z7y_44","icon-error":"_icon-error_15z7y_48","icon-success":"_icon-success_15z7y_54","icon-waiting":"_icon-waiting_15z7y_60","icon-disabled":"_icon-disabled_15z7y_66","icon-wrong":"_icon-wrong_15z7y_73",step:f,"step-content":"_step-content_15z7y_85","step-content-last":"_step-content-last_15z7y_91"};var n=(t=>(t.SUCCESS="SUCCESS",t.ERROR="ERROR",t.WAITING="WAITING",t.DISABLED="DISABLED",t.CANCELLED="CANCELLED",t.REFUSED="REFUSED",t))(n||{});const h=t=>{switch(t){case"SUCCESS":return s.jsx(o,{src:_,alt:"Étape en succès",className:e["icon-success"]});case"ERROR":return s.jsx(o,{src:u,alt:"Étape en erreur",className:e["icon-error"]});case"WAITING":return s.jsx(o,{src:m,alt:"Étape en attente",className:e["icon-waiting"]});case"DISABLED":return s.jsx(o,{src:m,alt:"Étape non disponible",className:e["icon-disabled"]});case"CANCELLED":return s.jsx(o,{src:u,alt:"Étape annulée",className:e["icon-error"]});case"REFUSED":return s.jsx(o,{src:y,className:e["icon-wrong"],alt:"Étape refusée"});default:throw new Error(`Unsupported step type: ${t}`)}},I=(t,r)=>{if(r!==void 0){if(t==="ERROR")return i(e.line,e["line-error"]);if(t==="SUCCESS")return i(e.line,e["line-success"]);if(t==="WAITING")return i(e.line,e["line-waiting"]);switch(r){case"SUCCESS":return i(e.line,e["line-success"]);case"ERROR":return i(e.line,e["line-error"]);case"WAITING":return i(e.line,e["line-waiting"]);case"DISABLED":return i(e.line,e["line-disabled"]);default:return}}},p=({steps:t})=>s.jsx("ol",{className:e.container,children:t.map((r,l)=>{const S=t[l+1]?.type,d=l===t.length-1;return s.jsxs("li",{className:e.step,children:[s.jsxs("div",{className:e["icon-line-container"],children:[s.jsx("div",{className:e["icon-container"],children:h(r.type)}),s.jsx("div",{className:I(r.type,S)})]}),s.jsx("div",{className:i(e["step-content"],{[e["step-content-last"]]:d}),children:r.content})]},`${r.type}-${l}`)})});try{n.displayName="TimelineStepType",n.__docgenInfo={description:"Enum for the types of steps in the timeline.",displayName:"TimelineStepType",props:{}}}catch{}try{p.displayName="Timeline",p.__docgenInfo={description:`The Timeline component is used to display a sequence of steps in a timeline.
Each step can represent different statuses such as success, error, waiting, etc.

---
**Important: Use the \`steps\` prop to provide the list of steps in the timeline.**
---`,displayName:"Timeline",props:{steps:{defaultValue:null,description:"An array of timeline steps to be displayed.",name:"steps",required:!0,type:{name:"TimelineStep[]"}}}}}catch{}const A={title:"@/ui-kit/Timeline",component:p},a={args:{steps:[{type:n.SUCCESS,content:"Tout s’est bien passé"},{type:n.SUCCESS,content:"Ça a marché, nous sommes sauvés !"},{type:n.WAITING,content:"En attente de validation par notre PO et UX préférée"},{type:n.DISABLED,content:"Cette étape n’est pas encore disponible..."},{type:n.DISABLED,content:"Celle-ci non plus d’ailleurs"}]}},c={args:{steps:[{type:n.SUCCESS,content:"C’est l’histoire d’un homme qui tombe d’un immeuble de 50 étages"},{type:n.SUCCESS,content:'Le mec, au fur et à mesure de sa chute, il se répète sans cesse pour se rassurer : "Jusqu’ici tout va bien"'},{type:n.SUCCESS,content:'"Jusqu’ici tout va bien"'},{type:n.SUCCESS,content:'"Jusqu’ici tout va bien"'},{type:n.SUCCESS,content:'"Jusqu’ici tout va bien"'},{type:n.ERROR,content:"Mais l’important, c’est pas la chute. C’est l’atterrissage."}]}};a.parameters={...a.parameters,docs:{...a.parameters?.docs,source:{originalSource:`{
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
}`,...a.parameters?.docs?.source}}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
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
}`,...c.parameters?.docs?.source}}};const L=["Default","WithError"];export{a as Default,c as WithError,L as __namedExportsOrder,A as default};
