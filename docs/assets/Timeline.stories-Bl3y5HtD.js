import{j as r}from"./jsx-runtime-Nms4Y4qS.js";import{c as a}from"./index-BpvXyOxN.js";import{f as S}from"./full-clear-CvNWe6Ae.js";import{f as b}from"./full-validate-C6eD2hog.js";import{s as f}from"./stroke-wrong-DoNMVBgE.js";import{S as o}from"./SvgIcon-Cibea2Sc.js";import"./index-BwDkhjyp.js";import"./_commonjsHelpers-BosuxZz1.js";const d=""+new URL("empty-circle-DShTDM6G.svg",import.meta.url).href,D="_container_8ar27_1",R="_icon_8ar27_7",T="_step_8ar27_44",e={container:D,icon:R,"icon-error":"_icon-error_8ar27_17","icon-success":"_icon-success_8ar27_24","icon-success-disabled":"_icon-success-disabled_8ar27_28","icon-waiting":"_icon-waiting_8ar27_32","icon-disabled":"_icon-disabled_8ar27_36","icon-wrong":"_icon-wrong_8ar27_40",step:T,"line-success":"_line-success_8ar27_57","line-error":"_line-error_8ar27_62","line-waiting":"_line-waiting_8ar27_67","line-disabled":"_line-disabled_8ar27_72"};var n=(t=>(t.SUCCESS="SUCCESS",t.ERROR="ERROR",t.WAITING="WAITING",t.DISABLED="DISABLED",t.CANCELLED="CANCELLED",t.REFUSED="REFUSED",t))(n||{});const U=(t,s)=>{switch(t){case"SUCCESS":return r.jsx(o,{src:b,alt:"Étape en succès",className:a(e.icon,s?e["icon-success-disabled"]:e["icon-success"])});case"ERROR":return r.jsx(o,{src:S,alt:"Étape en erreur",className:a(e.icon,e["icon-error"])});case"WAITING":return r.jsx(o,{src:d,alt:"Étape en attente",className:a(e.icon,e["icon-waiting"]),viewBox:"0 0 21 20"});case"DISABLED":return r.jsx(o,{src:d,alt:"Étape non disponible",className:a(e.icon,e["icon-disabled"]),viewBox:"0 0 21 20"});case"CANCELLED":return r.jsx(o,{src:S,alt:"Étape annulée",className:a(e.icon,e["icon-error"])});case"REFUSED":return r.jsx(o,{src:f,className:a(e.icon,e["icon-wrong"]),alt:"Étape refusée"});default:throw new Error(`Unsupported step type: ${t}`)}},h=(t,s,i)=>{if(s===void 0)return null;if(t==="WAITING")return e["line-waiting"];switch(s){case"SUCCESS":return i?e["line-error"]:e["line-success"];case"ERROR":return e["line-error"];case"WAITING":return e["line-waiting"];case"DISABLED":return e["line-disabled"];default:throw new Error(`Unsupported step type: ${s}`)}},l=({steps:t})=>{const s=t.filter(i=>i.type==="ERROR").length>0;return r.jsx("ol",{className:e.container,children:t.map((i,u)=>{var m;return r.jsxs("li",{className:a(e.step,h(i.type,(m=t[u+1])==null?void 0:m.type,s)),children:[U(i.type,s),i.content]},u)})})};try{l.displayName="Timeline",l.__docgenInfo={description:"",displayName:"Timeline",props:{steps:{defaultValue:null,description:"",name:"steps",required:!0,type:{name:"TimelineStep[]"}}}}}catch{}const B={title:"ui-kit/Timeline",component:l},c={args:{steps:[{type:n.SUCCESS,content:"Tout s’est bien passé"},{type:n.SUCCESS,content:"Ça a marché, nous sommes sauvés !"},{type:n.WAITING,content:"En attente de validation par notre PO et UX préférée"},{type:n.DISABLED,content:"Cette étape n’est pas encore disponible..."},{type:n.DISABLED,content:"Celle-ci non plus d’ailleurs"}]}},p={args:{steps:[{type:n.SUCCESS,content:"C’est l’histoire d’un homme qui tombe d’un immeuble de 50 étages"},{type:n.SUCCESS,content:'Le mec, au fur et à mesure de sa chute, il se répète sans cesse pour se rassurer : "Jusqu’ici tout va bien"'},{type:n.SUCCESS,content:'"Jusqu’ici tout va bien"'},{type:n.SUCCESS,content:'"Jusqu’ici tout va bien"'},{type:n.SUCCESS,content:'"Jusqu’ici tout va bien"'},{type:n.ERROR,content:"Mais l’important, c’est pas la chute. C’est l’atterrissage."}]}};var E,C,_;c.parameters={...c.parameters,docs:{...(E=c.parameters)==null?void 0:E.docs,source:{originalSource:`{
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
}`,...(_=(C=c.parameters)==null?void 0:C.docs)==null?void 0:_.source}}};var y,g,I;p.parameters={...p.parameters,docs:{...(y=p.parameters)==null?void 0:y.docs,source:{originalSource:`{
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
}`,...(I=(g=p.parameters)==null?void 0:g.docs)==null?void 0:I.source}}};const O=["Default","WithError"];export{c as Default,p as WithError,O as __namedExportsOrder,B as default};
