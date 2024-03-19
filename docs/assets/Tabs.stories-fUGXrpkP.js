import{K as j}from"./index-6U0dCUY_.js";import{s as k}from"./stroke-library-pK3ZobR5.js";import{s as g}from"./stroke-user-_jU816YT.js";import{j as e}from"./jsx-runtime-vNq4Oc-g.js";import{c as m}from"./index-XNbs-YUW.js";import{u as O,L as T}from"./index-kapi_vjX.js";import{B as w}from"./ButtonLink-3YIwl7lt.js";import{B as K}from"./Button-sBHdmzA3.js";import{S as B}from"./SvgIcon-QVOPtTle.js";import"./index-4g5l5LRQ.js";import"./_commonjsHelpers-4gQjN7DL.js";import"./index-CQtvWCGL.js";import"./Button.module-ZSasnFkE.js";import"./stroke-pass-84wyy11D.js";import"./Tooltip-kKBX527K.js";import"./useTooltipProps-5VZ0BXiJ.js";const L="_tabs_1ie1w_2",a={tabs:L,"tabs-tab":"_tabs-tab_1ie1w_8","tabs-tab-label":"_tabs-tab-label_1ie1w_14","tabs-tab-icon":"_tabs-tab-icon_1ie1w_17","tabs-tab-link":"_tabs-tab-link_1ie1w_24","tabs-tab-button":"_tabs-tab-button_1ie1w_30","is-selected":"_is-selected_1ie1w_38"},V="24",l=({nav:s,selectedKey:x,tabs:o,className:N})=>{const h=O(),c=o.length>0?e.jsx("ul",{className:m(a.tabs,N),children:o.map(({key:d,label:b,url:t,icon:r,onClick:I})=>e.jsx("li",{className:m(a["tabs-tab"],{[a["is-selected"]]:x===d}),children:t?e.jsxs(T,{className:a["tabs-tab-link"],to:t,"aria-current":s&&h.pathname===t?"page":void 0,children:[r&&e.jsx(B,{src:r,alt:"",className:a["tabs-tab-icon"],width:V}),e.jsx("span",{className:a["tabs-tab-label"],children:b})]},`tab${t}`):e.jsx(K,{variant:w.TERNARY,icon:r,onClick:I,className:a["tabs-tab-button"],children:b})},`tab_${d}`))}):e.jsx(e.Fragment,{});return s?e.jsx("nav",{"aria-label":s,children:c}):c},C=l;try{l.displayName="Tabs",l.__docgenInfo={description:"",displayName:"Tabs",props:{nav:{defaultValue:null,description:"",name:"nav",required:!1,type:{name:"string"}},tabs:{defaultValue:null,description:"",name:"tabs",required:!0,type:{name:"Tab[]"}},selectedKey:{defaultValue:null,description:"",name:"selectedKey",required:!1,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}const J={title:"ui-kit/Tabs",decorators:[j],component:C},i={args:{selectedKey:"individual",tabs:[{label:"Offres individuelles",url:"offres/indiv",key:"individual",icon:g},{label:"Offres collectives",url:"offres/collectives",key:"collective",icon:k}]}},n={args:{selectedKey:"individual",tabs:[{label:"Offres individuelles",onClick:()=>{},key:"individual",icon:g},{label:"Offres collectives",onClick:()=>{},key:"collective",icon:k}]}};var u,p,f;i.parameters={...i.parameters,docs:{...(u=i.parameters)==null?void 0:u.docs,source:{originalSource:`{
  args: {
    selectedKey: 'individual',
    tabs: [{
      label: 'Offres individuelles',
      url: 'offres/indiv',
      key: 'individual',
      icon: strokeUserIcon
    }, {
      label: 'Offres collectives',
      url: 'offres/collectives',
      key: 'collective',
      icon: strokeLibraryIcon
    }]
  }
}`,...(f=(p=i.parameters)==null?void 0:p.docs)==null?void 0:f.source}}};var _,v,y;n.parameters={...n.parameters,docs:{...(_=n.parameters)==null?void 0:_.docs,source:{originalSource:`{
  args: {
    selectedKey: 'individual',
    tabs: [{
      label: 'Offres individuelles',
      onClick: () => {},
      key: 'individual',
      icon: strokeUserIcon
    }, {
      label: 'Offres collectives',
      onClick: () => {},
      key: 'collective',
      icon: strokeLibraryIcon
    }]
  }
}`,...(y=(v=n.parameters)==null?void 0:v.docs)==null?void 0:y.source}}};const P=["Default","DefaultWithButton"];export{i as Default,n as DefaultWithButton,P as __namedExportsOrder,J as default};
