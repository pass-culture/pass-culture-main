import{j as i}from"./jsx-runtime-HPyya8g_.js";import{c as n}from"./index-B7RZ2vmV.js";import{f as u}from"./full-clear-Q4kCtSRL.js";import{f as _}from"./full-validate-CbMNulkZ.js";import{s as E}from"./stroke-wrong-BAouvvNg.js";import{S as o}from"./SvgIcon-e_d6ISWp.js";import"./iframe-6tMzVOsT.js";import"./preload-helper-PPVm8Dsz.js";const m=""+new URL("full-ellipse-FKO427Iz.svg",import.meta.url).href,C="_container_18tkk_1",y="_line_18tkk_21",f="_step_18tkk_81",e={container:C,"icon-line-container":"_icon-line-container_18tkk_6","icon-container":"_icon-container_18tkk_15",line:y,"line-error":"_line-error_18tkk_32","line-success":"_line-success_18tkk_38","line-disabled":"_line-disabled_18tkk_43","line-waiting":"_line-waiting_18tkk_44","icon-error":"_icon-error_18tkk_48","icon-success":"_icon-success_18tkk_54","icon-waiting":"_icon-waiting_18tkk_64","icon-disabled":"_icon-disabled_18tkk_70","icon-wrong":"_icon-wrong_18tkk_77",step:f,"step-content":"_step-content_18tkk_89","step-content-last":"_step-content-last_18tkk_95"};var s=(t=>(t.SUCCESS="SUCCESS",t.ERROR="ERROR",t.WAITING="WAITING",t.DISABLED="DISABLED",t.CANCELLED="CANCELLED",t.REFUSED="REFUSED",t))(s||{});const k=t=>{switch(t){case"SUCCESS":return i.jsx(o,{src:_,alt:"Étape en succès",className:n(e.icon,e["icon-success"])});case"ERROR":return i.jsx(o,{src:u,alt:"Étape en erreur",className:n(e.icon,e["icon-error"])});case"WAITING":return i.jsx(o,{src:m,alt:"Étape en attente",className:n(e.icon,e["icon-waiting"])});case"DISABLED":return i.jsx(o,{src:m,alt:"Étape non disponible",className:n(e.icon,e["icon-disabled"])});case"CANCELLED":return i.jsx(o,{src:u,alt:"Étape annulée",className:n(e.icon,e["icon-error"])});case"REFUSED":return i.jsx(o,{src:E,className:n(e.icon,e["icon-wrong"]),alt:"Étape refusée"});default:throw new Error(`Unsupported step type: ${t}`)}},h=(t,r)=>{if(r!==void 0){if(t==="ERROR")return n(e.line,e["line-error"]);if(t==="SUCCESS")return n(e.line,e["line-success"]);if(t==="WAITING")return n(e.line,e["line-waiting"]);switch(r){case"SUCCESS":return n(e.line,e["line-success"]);case"ERROR":return n(e.line,e["line-error"]);case"WAITING":return n(e.line,e["line-waiting"]);case"DISABLED":return n(e.line,e["line-disabled"]);default:return}}},p=({steps:t})=>i.jsx("ol",{className:e.container,children:t.map((r,l)=>{const S=t[l+1]?.type,d=l===t.length-1;return i.jsxs("li",{className:e.step,children:[i.jsxs("div",{className:e["icon-line-container"],children:[i.jsx("div",{className:e["icon-container"],children:k(r.type)}),i.jsx("div",{className:h(r.type,S)})]}),i.jsx("div",{className:n(e["step-content"],{[e["step-content-last"]]:d}),children:r.content})]},`${r.type}-${l}`)})});try{s.displayName="TimelineStepType",s.__docgenInfo={description:"Enum for the types of steps in the timeline.",displayName:"TimelineStepType",props:{}}}catch{}try{p.displayName="Timeline",p.__docgenInfo={description:`The Timeline component is used to display a sequence of steps in a timeline.
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
