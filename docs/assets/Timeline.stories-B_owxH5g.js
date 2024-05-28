import{j as r}from"./jsx-runtime-X2b_N9AH.js";import{c as o}from"./index-BpvXyOxN.js";import{f as S}from"./full-clear-CvNWe6Ae.js";import{f as g}from"./full-validate-C6eD2hog.js";import{s as I}from"./stroke-wrong-DoNMVBgE.js";import{S as c}from"./SvgIcon-DP_815J1.js";import"./index-uCp2LrAq.js";import"./_commonjsHelpers-BosuxZz1.js";const E=""+new URL("empty-circle-DShTDM6G.svg",import.meta.url).href,f="_container_30bmw_1",D="_icon_30bmw_9",R="_step_30bmw_46",e={container:f,icon:D,"icon-error":"_icon-error_30bmw_19","icon-success":"_icon-success_30bmw_26","icon-success-disabled":"_icon-success-disabled_30bmw_30","icon-waiting":"_icon-waiting_30bmw_34","icon-disabled":"_icon-disabled_30bmw_38","icon-wrong":"_icon-wrong_30bmw_42",step:R,"line-success":"_line-success_30bmw_59","line-error":"_line-error_30bmw_64","line-waiting":"_line-waiting_30bmw_69","line-disabled":"_line-disabled_30bmw_74"};var n=(t=>(t.SUCCESS="SUCCESS",t.ERROR="ERROR",t.WAITING="WAITING",t.DISABLED="DISABLED",t.CANCELLED="CANCELLED",t.REFUSED="REFUSED",t))(n||{});const T=(t,s)=>{switch(t){case"SUCCESS":return r.jsx(c,{src:g,alt:"Étape en succès",className:o(e.icon,s?e["icon-success-disabled"]:e["icon-success"])});case"ERROR":return r.jsx(c,{src:S,alt:"Étape en erreur",className:o(e.icon,e["icon-error"])});case"WAITING":return r.jsx(c,{src:E,alt:"Étape en attente",className:o(e.icon,e["icon-waiting"]),viewBox:"0 0 21 20"});case"DISABLED":return r.jsx(c,{src:E,alt:"Étape non disponible",className:o(e.icon,e["icon-disabled"]),viewBox:"0 0 21 20"});case"CANCELLED":return r.jsx(c,{src:S,alt:"Étape annulée",className:o(e.icon,e["icon-error"])});case"REFUSED":return r.jsx(c,{src:I,className:o(e.icon,e["icon-wrong"]),alt:"Étape refusée"});default:throw new Error(`Unsupported step type: ${t}`)}},U=(t,s,i)=>{if(s===void 0)return null;if(t==="WAITING")return e["line-waiting"];switch(s){case"SUCCESS":return i?e["line-error"]:e["line-success"];case"ERROR":return e["line-error"];case"WAITING":return e["line-waiting"];case"DISABLED":return e["line-disabled"];default:throw new Error(`Unsupported step type: ${s}`)}},p=({steps:t})=>{const s=t.filter(i=>i.type==="ERROR").length>0;return r.jsx("ol",{className:e.container,children:t.map((i,l)=>{var m;return r.jsxs("li",{className:o(e.step,U(i.type,(m=t[l+1])==null?void 0:m.type,s)),children:[T(i.type,s),i.content]},l)})})};try{p.displayName="Timeline",p.__docgenInfo={description:"",displayName:"Timeline",props:{steps:{defaultValue:null,description:"",name:"steps",required:!0,type:{name:"TimelineStep[]"}}}}}catch{}const B={title:"ui-kit/Timeline",component:p},a={args:{steps:[{type:n.SUCCESS,content:"Tout s’est bien passé"},{type:n.SUCCESS,content:"Ça a marché, nous sommes sauvés !"},{type:n.WAITING,content:"En attente de validation par notre PO et UX préférée"},{type:n.DISABLED,content:"Cette étape n’est pas encore disponible..."},{type:n.DISABLED,content:"Celle-ci non plus d’ailleurs"}]}},u={args:{steps:[{type:n.SUCCESS,content:"C’est l’histoire d’un homme qui tombe d’un immeuble de 50 étages"},{type:n.SUCCESS,content:'Le mec, au fur et à mesure de sa chute, il se répète sans cesse pour se rassurer : "Jusqu’ici tout va bien"'},{type:n.SUCCESS,content:'"Jusqu’ici tout va bien"'},{type:n.SUCCESS,content:'"Jusqu’ici tout va bien"'},{type:n.SUCCESS,content:'"Jusqu’ici tout va bien"'},{type:n.ERROR,content:"Mais l’important, c’est pas la chute. C’est l’atterrissage."}]}};var d,C,_;a.parameters={...a.parameters,docs:{...(d=a.parameters)==null?void 0:d.docs,source:{originalSource:`{
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
}`,...(_=(C=a.parameters)==null?void 0:C.docs)==null?void 0:_.source}}};var y,b,w;u.parameters={...u.parameters,docs:{...(y=u.parameters)==null?void 0:y.docs,source:{originalSource:`{
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
}`,...(w=(b=u.parameters)==null?void 0:b.docs)==null?void 0:w.source}}};const O=["Default","WithError"];export{a as Default,u as WithError,O as __namedExportsOrder,B as default};
