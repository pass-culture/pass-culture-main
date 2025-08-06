import{j as i}from"./jsx-runtime-DF2Pcvd1.js";import{c as n}from"./index-DeARc5FM.js";import{f as m}from"./full-clear-Q4kCtSRL.js";import{f as g}from"./full-validate-CbMNulkZ.js";import{s as T}from"./stroke-wrong-BAouvvNg.js";import{S as o}from"./SvgIcon-DfLnDDE5.js";import"./index-B2-qRKKC.js";import"./_commonjsHelpers-Cpj98o6Y.js";const S=""+new URL("full-ellipse-FKO427Iz.svg",import.meta.url).href,x="_container_qei0x_1",q="_line_qei0x_21",U="_step_qei0x_81",e={container:x,"icon-line-container":"_icon-line-container_qei0x_6","icon-container":"_icon-container_qei0x_15",line:q,"line-error":"_line-error_qei0x_32","line-success":"_line-success_qei0x_38","line-disabled":"_line-disabled_qei0x_43","line-waiting":"_line-waiting_qei0x_44","icon-error":"_icon-error_qei0x_48","icon-success":"_icon-success_qei0x_54","icon-waiting":"_icon-waiting_qei0x_64","icon-disabled":"_icon-disabled_qei0x_70","icon-wrong":"_icon-wrong_qei0x_77",step:U,"step-content":"_step-content_qei0x_89","step-content-last":"_step-content-last_qei0x_95"};var s=(t=>(t.SUCCESS="SUCCESS",t.ERROR="ERROR",t.WAITING="WAITING",t.DISABLED="DISABLED",t.CANCELLED="CANCELLED",t.REFUSED="REFUSED",t))(s||{});const N=t=>{switch(t){case"SUCCESS":return i.jsx(o,{src:g,alt:"Étape en succès",className:n(e.icon,e["icon-success"])});case"ERROR":return i.jsx(o,{src:m,alt:"Étape en erreur",className:n(e.icon,e["icon-error"])});case"WAITING":return i.jsx(o,{src:S,alt:"Étape en attente",className:n(e.icon,e["icon-waiting"])});case"DISABLED":return i.jsx(o,{src:S,alt:"Étape non disponible",className:n(e.icon,e["icon-disabled"])});case"CANCELLED":return i.jsx(o,{src:m,alt:"Étape annulée",className:n(e.icon,e["icon-error"])});case"REFUSED":return i.jsx(o,{src:T,className:n(e.icon,e["icon-wrong"]),alt:"Étape refusée"});default:throw new Error(`Unsupported step type: ${t}`)}},R=(t,r)=>{if(r!==void 0){if(t==="ERROR")return n(e.line,e["line-error"]);if(t==="SUCCESS")return n(e.line,e["line-success"]);if(t==="WAITING")return n(e.line,e["line-waiting"]);switch(r){case"SUCCESS":return n(e.line,e["line-success"]);case"ERROR":return n(e.line,e["line-error"]);case"WAITING":return n(e.line,e["line-waiting"]);case"DISABLED":return n(e.line,e["line-disabled"]);case"CANCELLED":case"REFUSED":default:return}}},p=({steps:t})=>i.jsx("ol",{className:e.container,children:t.map((r,l)=>{var u;const h=(u=t[l+1])==null?void 0:u.type,I=l===t.length-1;return i.jsxs("li",{className:e.step,children:[i.jsxs("div",{className:e["icon-line-container"],children:[i.jsx("div",{className:e["icon-container"],children:N(r.type)}),i.jsx("div",{className:R(r.type,h)})]}),i.jsx("div",{className:n(e["step-content"],{[e["step-content-last"]]:I}),children:r.content})]},l)})});try{s.displayName="TimelineStepType",s.__docgenInfo={description:"Enum for the types of steps in the timeline.",displayName:"TimelineStepType",props:{}}}catch{}try{p.displayName="Timeline",p.__docgenInfo={description:`The Timeline component is used to display a sequence of steps in a timeline.
Each step can represent different statuses such as success, error, waiting, etc.

---
**Important: Use the \`steps\` prop to provide the list of steps in the timeline.**
---`,displayName:"Timeline",props:{steps:{defaultValue:null,description:"An array of timeline steps to be displayed.",name:"steps",required:!0,type:{name:"TimelineStep[]"}}}}}catch{}const W={title:"@/ui-kit/Timeline",component:p},a={args:{steps:[{type:s.SUCCESS,content:"Tout s’est bien passé"},{type:s.SUCCESS,content:"Ça a marché, nous sommes sauvés !"},{type:s.WAITING,content:"En attente de validation par notre PO et UX préférée"},{type:s.DISABLED,content:"Cette étape n’est pas encore disponible..."},{type:s.DISABLED,content:"Celle-ci non plus d’ailleurs"}]}},c={args:{steps:[{type:s.SUCCESS,content:"C’est l’histoire d’un homme qui tombe d’un immeuble de 50 étages"},{type:s.SUCCESS,content:'Le mec, au fur et à mesure de sa chute, il se répète sans cesse pour se rassurer : "Jusqu’ici tout va bien"'},{type:s.SUCCESS,content:'"Jusqu’ici tout va bien"'},{type:s.SUCCESS,content:'"Jusqu’ici tout va bien"'},{type:s.SUCCESS,content:'"Jusqu’ici tout va bien"'},{type:s.ERROR,content:"Mais l’important, c’est pas la chute. C’est l’atterrissage."}]}};var d,_,E;a.parameters={...a.parameters,docs:{...(d=a.parameters)==null?void 0:d.docs,source:{originalSource:`{
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
}`,...(E=(_=a.parameters)==null?void 0:_.docs)==null?void 0:E.source}}};var C,y,f;c.parameters={...c.parameters,docs:{...(C=c.parameters)==null?void 0:C.docs,source:{originalSource:`{
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
}`,...(f=(y=c.parameters)==null?void 0:y.docs)==null?void 0:f.source}}};const B=["Default","WithError"];export{a as Default,c as WithError,B as __namedExportsOrder,W as default};
