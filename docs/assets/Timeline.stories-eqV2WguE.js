import{j as i}from"./jsx-runtime-iXOPPpZ7.js";import{c as o}from"./index-XNbs-YUW.js";import{f as S}from"./full-clear-A1Nwc76P.js";import{f}from"./full-validate-noa8P220.js";import{s as I}from"./stroke-wrong-h8vVUZVz.js";import{S as c}from"./SvgIcon-UUSKXfrA.js";import"./index-7OBYoplD.js";import"./_commonjsHelpers-4gQjN7DL.js";const d="data:image/svg+xml,%3csvg%20width='21'%20height='20'%20viewBox='0%200%2021%2020'%20fill='none'%20xmlns='http://www.w3.org/2000/svg'%3e%3cpath%20id='icon'%20fill-rule='evenodd'%20clip-rule='evenodd'%20d='M10.5%2017.335C14.551%2017.335%2017.835%2014.051%2017.835%2010C17.835%205.94903%2014.551%202.66504%2010.5%202.66504C6.44903%202.66504%203.16504%205.94903%203.16504%2010C3.16504%2014.051%206.44903%2017.335%2010.5%2017.335ZM10.5%2018.335C15.1033%2018.335%2018.835%2014.6033%2018.835%2010C18.835%205.39675%2015.1033%201.66504%2010.5%201.66504C5.89675%201.66504%202.16504%205.39675%202.16504%2010C2.16504%2014.6033%205.89675%2018.335%2010.5%2018.335Z'%20fill='currentColor'/%3e%3c/svg%3e",b="_container_m2g3h_1",x="_icon_m2g3h_8",T="_step_m2g3h_45",e={container:b,icon:x,"icon-error":"_icon-error_m2g3h_18","icon-success":"_icon-success_m2g3h_25","icon-success-disabled":"_icon-success-disabled_m2g3h_29","icon-waiting":"_icon-waiting_m2g3h_33","icon-disabled":"_icon-disabled_m2g3h_37","icon-wrong":"_icon-wrong_m2g3h_41",step:T,"line-success":"_line-success_m2g3h_59","line-error":"_line-error_m2g3h_64","line-waiting":"_line-waiting_m2g3h_69","line-disabled":"_line-disabled_m2g3h_74"};var n=(t=>(t.SUCCESS="SUCCESS",t.ERROR="ERROR",t.WAITING="WAITING",t.DISABLED="DISABLED",t.CANCELLED="CANCELLED",t.REFUSED="REFUSED",t))(n||{});const R=(t,s)=>{switch(t){case"SUCCESS":return i.jsx(c,{src:f,alt:"Étape en succès",className:o(e.icon,s?e["icon-success-disabled"]:e["icon-success"])});case"ERROR":return i.jsx(c,{src:S,alt:"Étape en erreur",className:o(e.icon,e["icon-error"])});case"WAITING":return i.jsx(c,{src:d,alt:"Étape en attente",className:o(e.icon,e["icon-waiting"]),viewBox:"0 0 21 20"});case"DISABLED":return i.jsx(c,{src:d,alt:"Étape non disponible",className:o(e.icon,e["icon-disabled"]),viewBox:"0 0 21 20"});case"CANCELLED":return i.jsx(c,{src:S,alt:"Étape annulée",className:o(e.icon,e["icon-error"])});case"REFUSED":return i.jsx(c,{src:I,className:o(e.icon,e["icon-wrong"]),alt:"Étape refusée"});default:throw new Error(`Unsupported step type: ${t}`)}},U=(t,s,r)=>{if(s===void 0)return null;if(t==="WAITING")return e["line-waiting"];switch(s){case"SUCCESS":return r?e["line-error"]:e["line-success"];case"ERROR":return e["line-error"];case"WAITING":return e["line-waiting"];case"DISABLED":return e["line-disabled"];default:throw new Error(`Unsupported step type: ${s}`)}},l=({steps:t})=>{const s=t.filter(r=>r.type==="ERROR").length>0;return i.jsx("ol",{className:e.container,children:t.map((r,p)=>{var m;return i.jsxs("li",{className:o(e.step,U(r.type,(m=t[p+1])==null?void 0:m.type,s)),children:[R(r.type,s),r.content]},p)})})},v=l;try{l.displayName="Timeline",l.__docgenInfo={description:"",displayName:"Timeline",props:{steps:{defaultValue:null,description:"",name:"steps",required:!0,type:{name:"TimelineStep[]"}}}}}catch{}const O={title:"ui-kit/Timeline",component:v},a={args:{steps:[{type:n.SUCCESS,content:"Tout s’est bien passé"},{type:n.SUCCESS,content:"Ça a marché, nous sommes sauvés !"},{type:n.WAITING,content:"En attente de validation par notre PO et UX préférée"},{type:n.DISABLED,content:"Cette étape n’est pas encore disponible..."},{type:n.DISABLED,content:"Celle-ci non plus d’ailleurs"}]}},u={args:{steps:[{type:n.SUCCESS,content:"C’est l’histoire d’un homme qui tombe d’un immeuble de 50 étages"},{type:n.SUCCESS,content:'Le mec, au fur et à mesure de sa chute, il se répète sans cesse pour se rassurer : "Jusqu’ici tout va bien"'},{type:n.SUCCESS,content:'"Jusqu’ici tout va bien"'},{type:n.SUCCESS,content:'"Jusqu’ici tout va bien"'},{type:n.SUCCESS,content:'"Jusqu’ici tout va bien"'},{type:n.ERROR,content:"Mais l’important, c’est pas la chute. C’est l’atterrissage."}]}};var E,C,_;a.parameters={...a.parameters,docs:{...(E=a.parameters)==null?void 0:E.docs,source:{originalSource:`{
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
}`,...(_=(C=a.parameters)==null?void 0:C.docs)==null?void 0:_.source}}};var g,h,y;u.parameters={...u.parameters,docs:{...(g=u.parameters)==null?void 0:g.docs,source:{originalSource:`{
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
}`,...(y=(h=u.parameters)==null?void 0:h.docs)==null?void 0:y.source}}};const W=["Default","WithError"];export{a as Default,u as WithError,W as __namedExportsOrder,O as default};
