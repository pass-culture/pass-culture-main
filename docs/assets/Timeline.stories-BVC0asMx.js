import{j as r}from"./jsx-runtime-CKrituN3.js";import{c as o}from"./index-BpvXyOxN.js";import{f as S}from"./full-clear-CvNWe6Ae.js";import{f as b}from"./full-validate-C6eD2hog.js";import{s as f}from"./stroke-wrong-DoNMVBgE.js";import{S as c}from"./SvgIcon-B4BQC89V.js";import"./index-CBqU2yxZ.js";import"./_commonjsHelpers-BosuxZz1.js";const d=""+new URL("empty-circle-DShTDM6G.svg",import.meta.url).href,D="_container_1l5qd_1",R="_icon_1l5qd_8",T="_step_1l5qd_45",e={container:D,icon:R,"icon-error":"_icon-error_1l5qd_18","icon-success":"_icon-success_1l5qd_25","icon-success-disabled":"_icon-success-disabled_1l5qd_29","icon-waiting":"_icon-waiting_1l5qd_33","icon-disabled":"_icon-disabled_1l5qd_37","icon-wrong":"_icon-wrong_1l5qd_41",step:T,"line-success":"_line-success_1l5qd_59","line-error":"_line-error_1l5qd_64","line-waiting":"_line-waiting_1l5qd_69","line-disabled":"_line-disabled_1l5qd_74"};var n=(t=>(t.SUCCESS="SUCCESS",t.ERROR="ERROR",t.WAITING="WAITING",t.DISABLED="DISABLED",t.CANCELLED="CANCELLED",t.REFUSED="REFUSED",t))(n||{});const U=(t,s)=>{switch(t){case"SUCCESS":return r.jsx(c,{src:b,alt:"Étape en succès",className:o(e.icon,s?e["icon-success-disabled"]:e["icon-success"])});case"ERROR":return r.jsx(c,{src:S,alt:"Étape en erreur",className:o(e.icon,e["icon-error"])});case"WAITING":return r.jsx(c,{src:d,alt:"Étape en attente",className:o(e.icon,e["icon-waiting"]),viewBox:"0 0 21 20"});case"DISABLED":return r.jsx(c,{src:d,alt:"Étape non disponible",className:o(e.icon,e["icon-disabled"]),viewBox:"0 0 21 20"});case"CANCELLED":return r.jsx(c,{src:S,alt:"Étape annulée",className:o(e.icon,e["icon-error"])});case"REFUSED":return r.jsx(c,{src:f,className:o(e.icon,e["icon-wrong"]),alt:"Étape refusée"});default:throw new Error(`Unsupported step type: ${t}`)}},q=(t,s,i)=>{if(s===void 0)return null;if(t==="WAITING")return e["line-waiting"];switch(s){case"SUCCESS":return i?e["line-error"]:e["line-success"];case"ERROR":return e["line-error"];case"WAITING":return e["line-waiting"];case"DISABLED":return e["line-disabled"];default:throw new Error(`Unsupported step type: ${s}`)}},u=({steps:t})=>{const s=t.filter(i=>i.type==="ERROR").length>0;return r.jsx("ol",{className:e.container,children:t.map((i,p)=>{var m;return r.jsxs("li",{className:o(e.step,q(i.type,(m=t[p+1])==null?void 0:m.type,s)),children:[U(i.type,s),i.content]},p)})})};try{u.displayName="Timeline",u.__docgenInfo={description:"",displayName:"Timeline",props:{steps:{defaultValue:null,description:"",name:"steps",required:!0,type:{name:"TimelineStep[]"}}}}}catch{}const B={title:"ui-kit/Timeline",component:u},a={args:{steps:[{type:n.SUCCESS,content:"Tout s’est bien passé"},{type:n.SUCCESS,content:"Ça a marché, nous sommes sauvés !"},{type:n.WAITING,content:"En attente de validation par notre PO et UX préférée"},{type:n.DISABLED,content:"Cette étape n’est pas encore disponible..."},{type:n.DISABLED,content:"Celle-ci non plus d’ailleurs"}]}},l={args:{steps:[{type:n.SUCCESS,content:"C’est l’histoire d’un homme qui tombe d’un immeuble de 50 étages"},{type:n.SUCCESS,content:'Le mec, au fur et à mesure de sa chute, il se répète sans cesse pour se rassurer : "Jusqu’ici tout va bien"'},{type:n.SUCCESS,content:'"Jusqu’ici tout va bien"'},{type:n.SUCCESS,content:'"Jusqu’ici tout va bien"'},{type:n.SUCCESS,content:'"Jusqu’ici tout va bien"'},{type:n.ERROR,content:"Mais l’important, c’est pas la chute. C’est l’atterrissage."}]}};var E,C,_;a.parameters={...a.parameters,docs:{...(E=a.parameters)==null?void 0:E.docs,source:{originalSource:`{
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
}`,...(_=(C=a.parameters)==null?void 0:C.docs)==null?void 0:_.source}}};var y,g,I;l.parameters={...l.parameters,docs:{...(y=l.parameters)==null?void 0:y.docs,source:{originalSource:`{
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
}`,...(I=(g=l.parameters)==null?void 0:g.docs)==null?void 0:I.source}}};const O=["Default","WithError"];export{a as Default,l as WithError,O as __namedExportsOrder,B as default};
