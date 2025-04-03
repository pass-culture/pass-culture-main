import{j as i}from"./jsx-runtime-BYYWji4R.js";import{c as o}from"./index-DeARc5FM.js";import{f as S}from"./full-clear-Q4kCtSRL.js";import{f as g}from"./full-validate-CbMNulkZ.js";import{s as h}from"./stroke-wrong-BAouvvNg.js";import{S as a}from"./SvgIcon-CyWUmZpn.js";import"./index-ClcD9ViR.js";import"./_commonjsHelpers-Cpj98o6Y.js";const d=""+new URL("empty-circle-B2wH-kqX.svg",import.meta.url).href,T="_container_1b58u_1",I="_icon_1b58u_7",U="_step_1b58u_44",e={container:T,icon:I,"icon-error":"_icon-error_1b58u_17","icon-success":"_icon-success_1b58u_24","icon-success-disabled":"_icon-success-disabled_1b58u_28","icon-waiting":"_icon-waiting_1b58u_32","icon-disabled":"_icon-disabled_1b58u_36","icon-wrong":"_icon-wrong_1b58u_40",step:U,"line-success":"_line-success_1b58u_57","line-error":"_line-error_1b58u_62","line-waiting":"_line-waiting_1b58u_67","line-disabled":"_line-disabled_1b58u_72"};var n=(t=>(t.SUCCESS="SUCCESS",t.ERROR="ERROR",t.WAITING="WAITING",t.DISABLED="DISABLED",t.CANCELLED="CANCELLED",t.REFUSED="REFUSED",t))(n||{});const R=(t,s)=>{switch(t){case"SUCCESS":return i.jsx(a,{src:g,alt:"Étape en succès",className:o(e.icon,s?e["icon-success-disabled"]:e["icon-success"])});case"ERROR":return i.jsx(a,{src:S,alt:"Étape en erreur",className:o(e.icon,e["icon-error"])});case"WAITING":return i.jsx(a,{src:d,alt:"Étape en attente",className:o(e.icon,e["icon-waiting"]),viewBox:"0 0 21 20"});case"DISABLED":return i.jsx(a,{src:d,alt:"Étape non disponible",className:o(e.icon,e["icon-disabled"]),viewBox:"0 0 21 20"});case"CANCELLED":return i.jsx(a,{src:S,alt:"Étape annulée",className:o(e.icon,e["icon-error"])});case"REFUSED":return i.jsx(a,{src:h,className:o(e.icon,e["icon-wrong"]),alt:"Étape refusée"});default:throw new Error(`Unsupported step type: ${t}`)}},D=(t,s,r)=>{if(s===void 0)return null;if(t==="WAITING")return e["line-waiting"];switch(s){case"SUCCESS":return r?e["line-error"]:e["line-success"];case"ERROR":return e["line-error"];case"WAITING":return e["line-waiting"];case"DISABLED":return e["line-disabled"];case"CANCELLED":case"REFUSED":default:throw new Error(`Unsupported step type: ${s}`)}},u=({steps:t})=>{const s=t.filter(r=>r.type==="ERROR").length>0;return i.jsx("ol",{className:e.container,children:t.map((r,l)=>{var m;return i.jsxs("li",{className:o(e.step,D(r.type,(m=t[l+1])==null?void 0:m.type,s)),children:[R(r.type,s),r.content]},l)})})};try{n.displayName="TimelineStepType",n.__docgenInfo={description:"Enum for the types of steps in the timeline.",displayName:"TimelineStepType",props:{}}}catch{}try{u.displayName="Timeline",u.__docgenInfo={description:`The Timeline component is used to display a sequence of steps in a timeline.
Each step can represent different statuses such as success, error, waiting, etc.

---
**Important: Use the \`steps\` prop to provide the list of steps in the timeline.**
---`,displayName:"Timeline",props:{steps:{defaultValue:null,description:"An array of timeline steps to be displayed.",name:"steps",required:!0,type:{name:"TimelineStep[]"}}}}}catch{}const j={title:"ui-kit/Timeline",component:u},c={args:{steps:[{type:n.SUCCESS,content:"Tout s’est bien passé"},{type:n.SUCCESS,content:"Ça a marché, nous sommes sauvés !"},{type:n.WAITING,content:"En attente de validation par notre PO et UX préférée"},{type:n.DISABLED,content:"Cette étape n’est pas encore disponible..."},{type:n.DISABLED,content:"Celle-ci non plus d’ailleurs"}]}},p={args:{steps:[{type:n.SUCCESS,content:"C’est l’histoire d’un homme qui tombe d’un immeuble de 50 étages"},{type:n.SUCCESS,content:'Le mec, au fur et à mesure de sa chute, il se répète sans cesse pour se rassurer : "Jusqu’ici tout va bien"'},{type:n.SUCCESS,content:'"Jusqu’ici tout va bien"'},{type:n.SUCCESS,content:'"Jusqu’ici tout va bien"'},{type:n.SUCCESS,content:'"Jusqu’ici tout va bien"'},{type:n.ERROR,content:"Mais l’important, c’est pas la chute. C’est l’atterrissage."}]}};var E,_,C;c.parameters={...c.parameters,docs:{...(E=c.parameters)==null?void 0:E.docs,source:{originalSource:`{
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
}`,...(C=(_=c.parameters)==null?void 0:_.docs)==null?void 0:C.source}}};var y,b,f;p.parameters={...p.parameters,docs:{...(y=p.parameters)==null?void 0:y.docs,source:{originalSource:`{
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
}`,...(f=(b=p.parameters)==null?void 0:b.docs)==null?void 0:f.source}}};const O=["Default","WithError"];export{c as Default,p as WithError,O as __namedExportsOrder,j as default};
