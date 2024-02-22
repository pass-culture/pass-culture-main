import{j as r}from"./jsx-runtime-vNq4Oc-g.js";import{c as o}from"./index-XNbs-YUW.js";import{f as S}from"./full-clear-0L2gsxg_.js";import{f as I}from"./full-validate-UsEvEnOv.js";import{s as U}from"./stroke-wrong-rXi3gDvD.js";import{S as c}from"./SvgIcon-QVOPtTle.js";import"./index-4g5l5LRQ.js";import"./_commonjsHelpers-4gQjN7DL.js";const E=""+new URL("empty-circle-0oUwzOhu.svg",import.meta.url).href,f="_container_11qb9_1",R="_icon_11qb9_8",T="_step_11qb9_45",e={container:f,icon:R,"icon-error":"_icon-error_11qb9_18","icon-success":"_icon-success_11qb9_25","icon-success-disabled":"_icon-success-disabled_11qb9_29","icon-waiting":"_icon-waiting_11qb9_33","icon-disabled":"_icon-disabled_11qb9_37","icon-wrong":"_icon-wrong_11qb9_41",step:T,"line-success":"_line-success_11qb9_59","line-error":"_line-error_11qb9_64","line-waiting":"_line-waiting_11qb9_69","line-disabled":"_line-disabled_11qb9_74"};var n=(t=>(t.SUCCESS="SUCCESS",t.ERROR="ERROR",t.WAITING="WAITING",t.DISABLED="DISABLED",t.CANCELLED="CANCELLED",t.REFUSED="REFUSED",t))(n||{});const q=(t,s)=>{switch(t){case"SUCCESS":return r.jsx(c,{src:I,alt:"Étape en succès",className:o(e.icon,s?e["icon-success-disabled"]:e["icon-success"])});case"ERROR":return r.jsx(c,{src:S,alt:"Étape en erreur",className:o(e.icon,e["icon-error"])});case"WAITING":return r.jsx(c,{src:E,alt:"Étape en attente",className:o(e.icon,e["icon-waiting"]),viewBox:"0 0 21 20"});case"DISABLED":return r.jsx(c,{src:E,alt:"Étape non disponible",className:o(e.icon,e["icon-disabled"]),viewBox:"0 0 21 20"});case"CANCELLED":return r.jsx(c,{src:S,alt:"Étape annulée",className:o(e.icon,e["icon-error"])});case"REFUSED":return r.jsx(c,{src:U,className:o(e.icon,e["icon-wrong"]),alt:"Étape refusée"});default:throw new Error(`Unsupported step type: ${t}`)}},x=(t,s,i)=>{if(s===void 0)return null;if(t==="WAITING")return e["line-waiting"];switch(s){case"SUCCESS":return i?e["line-error"]:e["line-success"];case"ERROR":return e["line-error"];case"WAITING":return e["line-waiting"];case"DISABLED":return e["line-disabled"];default:throw new Error(`Unsupported step type: ${s}`)}},l=({steps:t})=>{const s=t.filter(i=>i.type==="ERROR").length>0;return r.jsx("ol",{className:e.container,children:t.map((i,p)=>{var m;return r.jsxs("li",{className:o(e.step,x(i.type,(m=t[p+1])==null?void 0:m.type,s)),children:[q(i.type,s),i.content]},p)})})},D=l;try{l.displayName="Timeline",l.__docgenInfo={description:"",displayName:"Timeline",props:{steps:{defaultValue:null,description:"",name:"steps",required:!0,type:{name:"TimelineStep[]"}}}}}catch{}const B={title:"ui-kit/Timeline",component:D},a={args:{steps:[{type:n.SUCCESS,content:"Tout s’est bien passé"},{type:n.SUCCESS,content:"Ça a marché, nous sommes sauvés !"},{type:n.WAITING,content:"En attente de validation par notre PO et UX préférée"},{type:n.DISABLED,content:"Cette étape n’est pas encore disponible..."},{type:n.DISABLED,content:"Celle-ci non plus d’ailleurs"}]}},u={args:{steps:[{type:n.SUCCESS,content:"C’est l’histoire d’un homme qui tombe d’un immeuble de 50 étages"},{type:n.SUCCESS,content:'Le mec, au fur et à mesure de sa chute, il se répète sans cesse pour se rassurer : "Jusqu’ici tout va bien"'},{type:n.SUCCESS,content:'"Jusqu’ici tout va bien"'},{type:n.SUCCESS,content:'"Jusqu’ici tout va bien"'},{type:n.SUCCESS,content:'"Jusqu’ici tout va bien"'},{type:n.ERROR,content:"Mais l’important, c’est pas la chute. C’est l’atterrissage."}]}};var d,C,_;a.parameters={...a.parameters,docs:{...(d=a.parameters)==null?void 0:d.docs,source:{originalSource:`{
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
}`,...(_=(C=a.parameters)==null?void 0:C.docs)==null?void 0:_.source}}};var y,b,g;u.parameters={...u.parameters,docs:{...(y=u.parameters)==null?void 0:y.docs,source:{originalSource:`{
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
}`,...(g=(b=u.parameters)==null?void 0:b.docs)==null?void 0:g.source}}};const W=["Default","WithError"];export{a as Default,u as WithError,W as __namedExportsOrder,B as default};
