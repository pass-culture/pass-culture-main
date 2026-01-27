import{j as i}from"./jsx-runtime-C_uOM0Gm.js";import{c as n}from"./index-TscbDd2H.js";import{f as u}from"./full-clear-Q4kCtSRL.js";import{f as d}from"./full-validate-CbMNulkZ.js";import{s as _}from"./stroke-wrong-BAouvvNg.js";import{S as o}from"./SvgIcon-CJiY4LCz.js";import"./iframe-CTnXOULQ.js";import"./preload-helper-PPVm8Dsz.js";const m=""+new URL("full-ellipse-FKO427Iz.svg",import.meta.url).href,E="_container_1yyjf_1",C="_line_1yyjf_21",f="_step_1yyjf_81",e={container:E,"icon-line-container":"_icon-line-container_1yyjf_6","icon-container":"_icon-container_1yyjf_15",line:C,"line-error":"_line-error_1yyjf_32","line-success":"_line-success_1yyjf_38","line-disabled":"_line-disabled_1yyjf_43","line-waiting":"_line-waiting_1yyjf_44","icon-error":"_icon-error_1yyjf_48","icon-success":"_icon-success_1yyjf_54","icon-waiting":"_icon-waiting_1yyjf_64","icon-disabled":"_icon-disabled_1yyjf_70","icon-wrong":"_icon-wrong_1yyjf_77",step:f,"step-content":"_step-content_1yyjf_89","step-content-last":"_step-content-last_1yyjf_95"};var s=(t=>(t.SUCCESS="SUCCESS",t.ERROR="ERROR",t.WAITING="WAITING",t.DISABLED="DISABLED",t.CANCELLED="CANCELLED",t.REFUSED="REFUSED",t))(s||{});const h=t=>{switch(t){case"SUCCESS":return i.jsx(o,{src:d,alt:"Étape en succès",className:n(e.icon,e["icon-success"])});case"ERROR":return i.jsx(o,{src:u,alt:"Étape en erreur",className:n(e.icon,e["icon-error"])});case"WAITING":return i.jsx(o,{src:m,alt:"Étape en attente",className:n(e.icon,e["icon-waiting"])});case"DISABLED":return i.jsx(o,{src:m,alt:"Étape non disponible",className:n(e.icon,e["icon-disabled"])});case"CANCELLED":return i.jsx(o,{src:u,alt:"Étape annulée",className:n(e.icon,e["icon-error"])});case"REFUSED":return i.jsx(o,{src:_,className:n(e.icon,e["icon-wrong"]),alt:"Étape refusée"});default:throw new Error(`Unsupported step type: ${t}`)}},I=(t,r)=>{if(r!==void 0){if(t==="ERROR")return n(e.line,e["line-error"]);if(t==="SUCCESS")return n(e.line,e["line-success"]);if(t==="WAITING")return n(e.line,e["line-waiting"]);switch(r){case"SUCCESS":return n(e.line,e["line-success"]);case"ERROR":return n(e.line,e["line-error"]);case"WAITING":return n(e.line,e["line-waiting"]);case"DISABLED":return n(e.line,e["line-disabled"]);default:return}}},p=({steps:t})=>i.jsx("ol",{className:e.container,children:t.map((r,l)=>{const S=t[l+1]?.type,y=l===t.length-1;return i.jsxs("li",{className:e.step,children:[i.jsxs("div",{className:e["icon-line-container"],children:[i.jsx("div",{className:e["icon-container"],children:h(r.type)}),i.jsx("div",{className:I(r.type,S)})]}),i.jsx("div",{className:n(e["step-content"],{[e["step-content-last"]]:y}),children:r.content})]},`${r.type}-${l}`)})});try{s.displayName="TimelineStepType",s.__docgenInfo={description:"Enum for the types of steps in the timeline.",displayName:"TimelineStepType",props:{}}}catch{}try{p.displayName="Timeline",p.__docgenInfo={description:`The Timeline component is used to display a sequence of steps in a timeline.
Each step can represent different statuses such as success, error, waiting, etc.

---
**Important: Use the \`steps\` prop to provide the list of steps in the timeline.**
---`,displayName:"Timeline",props:{steps:{defaultValue:null,description:"An array of timeline steps to be displayed.",name:"steps",required:!0,type:{name:"TimelineStep[]"}}}}}catch{}const v={title:"@/ui-kit/Timeline",component:p},a={args:{steps:[{type:s.SUCCESS,content:"Tout s’est bien passé"},{type:s.SUCCESS,content:"Ça a marché, nous sommes sauvés !"},{type:s.WAITING,content:"En attente de validation par notre PO et UX préférée"},{type:s.DISABLED,content:"Cette étape n’est pas encore disponible..."},{type:s.DISABLED,content:"Celle-ci non plus d’ailleurs"}]}},c={args:{steps:[{type:s.SUCCESS,content:"C’est l’histoire d’un homme qui tombe d’un immeuble de 50 étages"},{type:s.SUCCESS,content:'Le mec, au fur et à mesure de sa chute, il se répète sans cesse pour se rassurer : "Jusqu’ici tout va bien"'},{type:s.SUCCESS,content:'"Jusqu’ici tout va bien"'},{type:s.SUCCESS,content:'"Jusqu’ici tout va bien"'},{type:s.SUCCESS,content:'"Jusqu’ici tout va bien"'},{type:s.ERROR,content:"Mais l’important, c’est pas la chute. C’est l’atterrissage."}]}};a.parameters={...a.parameters,docs:{...a.parameters?.docs,source:{originalSource:`{
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
}`,...c.parameters?.docs?.source}}};const A=["Default","WithError"];export{a as Default,c as WithError,A as __namedExportsOrder,v as default};
