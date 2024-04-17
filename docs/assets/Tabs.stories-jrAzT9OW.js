import{K as j}from"./index-CghiRVmc.js";import{s as k}from"./stroke-library-B87NDtez.js";import{s as g}from"./stroke-user-JNyZapNG.js";import{j as e}from"./jsx-runtime-CKrituN3.js";import{c as u}from"./index-BpvXyOxN.js";import{u as O,L as T}from"./index-D-qxk1LK.js";import{B as K}from"./ButtonLink-BL2xBbQK.js";import{B}from"./Button-aDWHYLKz.js";import{S as L}from"./SvgIcon-B4BQC89V.js";import"./index-CBqU2yxZ.js";import"./_commonjsHelpers-BosuxZz1.js";import"./index-Bc47ZfBr.js";import"./Button.module-D1-_wviZ.js";import"./stroke-pass-C0Oiu4_F.js";import"./Tooltip-DQk13cIf.js";import"./useTooltipProps-DrCYBs0a.js";const V="_tabs_nu5fv_2",a={tabs:V,"tabs-tab":"_tabs-tab_nu5fv_8","tabs-tab-label":"_tabs-tab-label_nu5fv_14","tabs-tab-icon":"_tabs-tab-icon_nu5fv_17","tabs-tab-link":"_tabs-tab-link_nu5fv_24","tabs-tab-button":"_tabs-tab-button_nu5fv_30","is-selected":"_is-selected_nu5fv_38"},C="24",l=({nav:s,selectedKey:x,tabs:o,className:N})=>{const h=O(),c=o.length>0?e.jsx("ul",{className:u(a.tabs,N),children:o.map(({key:d,label:b,url:t,icon:r,onClick:I})=>e.jsx("li",{className:u(a["tabs-tab"],{[a["is-selected"]]:x===d}),children:t?e.jsxs(T,{className:a["tabs-tab-link"],to:t,"aria-current":s&&h.pathname===t?"page":void 0,children:[r&&e.jsx(L,{src:r,alt:"",className:a["tabs-tab-icon"],width:C}),e.jsx("span",{className:a["tabs-tab-label"],children:b})]},`tab${t}`):e.jsx(B,{variant:K.TERNARY,icon:r,onClick:I,className:a["tabs-tab-button"],children:b})},`tab_${d}`))}):e.jsx(e.Fragment,{});return s?e.jsx("nav",{"aria-label":s,children:c}):c},E=l;try{l.displayName="Tabs",l.__docgenInfo={description:"",displayName:"Tabs",props:{nav:{defaultValue:null,description:"",name:"nav",required:!1,type:{name:"string"}},tabs:{defaultValue:null,description:"",name:"tabs",required:!0,type:{name:"Tab[]"}},selectedKey:{defaultValue:null,description:"",name:"selectedKey",required:!1,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}const J={title:"ui-kit/Tabs",decorators:[j],component:E},n={args:{selectedKey:"individual",tabs:[{label:"Offres individuelles",url:"offres/indiv",key:"individual",icon:g},{label:"Offres collectives",url:"offres/collectives",key:"collective",icon:k}]}},i={args:{selectedKey:"individual",tabs:[{label:"Offres individuelles",onClick:()=>{},key:"individual",icon:g},{label:"Offres collectives",onClick:()=>{},key:"collective",icon:k}]}};var m,f,p;n.parameters={...n.parameters,docs:{...(m=n.parameters)==null?void 0:m.docs,source:{originalSource:`{
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
}`,...(p=(f=n.parameters)==null?void 0:f.docs)==null?void 0:p.source}}};var _,v,y;i.parameters={...i.parameters,docs:{...(_=i.parameters)==null?void 0:_.docs,source:{originalSource:`{
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
}`,...(y=(v=i.parameters)==null?void 0:v.docs)==null?void 0:y.source}}};const P=["Default","DefaultWithButton"];export{n as Default,i as DefaultWithButton,P as __namedExportsOrder,J as default};
