import{K as j}from"./index-CIvHvQ2l.js";import{s as k}from"./stroke-library-B87NDtez.js";import{s as g}from"./stroke-user-JNyZapNG.js";import{j as e}from"./jsx-runtime-Nms4Y4qS.js";import{c as u}from"./index-BpvXyOxN.js";import{u as O,L as K}from"./index-Di_oCQuz.js";import{B as T}from"./Button-CZknAwTg.js";import{B}from"./types-DjX_gQD6.js";import{S as L}from"./SvgIcon-Cibea2Sc.js";import"./index-BwDkhjyp.js";import"./_commonjsHelpers-BosuxZz1.js";import"./index-QeuA_w2N.js";import"./stroke-pass-C0Oiu4_F.js";import"./Tooltip-Cv8JYvXq.js";import"./useTooltipProps-DoeIm4b6.js";import"./Button.module-CwyaUOYU.js";const V="_tabs_nu5fv_2",a={tabs:V,"tabs-tab":"_tabs-tab_nu5fv_8","tabs-tab-label":"_tabs-tab-label_nu5fv_14","tabs-tab-icon":"_tabs-tab-icon_nu5fv_17","tabs-tab-link":"_tabs-tab-link_nu5fv_24","tabs-tab-button":"_tabs-tab-button_nu5fv_30","is-selected":"_is-selected_nu5fv_38"},C="24",l=({nav:t,selectedKey:N,tabs:o,className:h})=>{const x=O(),c=o.length>0?e.jsx("ul",{className:u(a.tabs,h),children:o.map(({key:d,label:b,url:s,icon:r,onClick:I})=>e.jsx("li",{className:u(a["tabs-tab"],{[a["is-selected"]]:N===d}),children:s?e.jsxs(K,{className:a["tabs-tab-link"],to:s,"aria-current":t&&x.pathname===s?"page":void 0,children:[r&&e.jsx(L,{src:r,alt:"",className:a["tabs-tab-icon"],width:C}),e.jsx("span",{className:a["tabs-tab-label"],children:b})]},`tab${s}`):e.jsx(T,{variant:B.TERNARY,icon:r,onClick:I,className:a["tabs-tab-button"],children:b})},`tab_${d}`))}):e.jsx(e.Fragment,{});return t?e.jsx("nav",{"aria-label":t,children:c}):c};try{l.displayName="Tabs",l.__docgenInfo={description:"",displayName:"Tabs",props:{nav:{defaultValue:null,description:"",name:"nav",required:!1,type:{name:"string"}},tabs:{defaultValue:null,description:"",name:"tabs",required:!0,type:{name:"Tab[]"}},selectedKey:{defaultValue:null,description:"",name:"selectedKey",required:!1,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}const H={title:"ui-kit/Tabs",decorators:[j],component:l},n={args:{selectedKey:"individual",tabs:[{label:"Offres individuelles",url:"offres/indiv",key:"individual",icon:g},{label:"Offres collectives",url:"offres/collectives",key:"collective",icon:k}]}},i={args:{selectedKey:"individual",tabs:[{label:"Offres individuelles",onClick:()=>{},key:"individual",icon:g},{label:"Offres collectives",onClick:()=>{},key:"collective",icon:k}]}};var m,f,p;n.parameters={...n.parameters,docs:{...(m=n.parameters)==null?void 0:m.docs,source:{originalSource:`{
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
}`,...(y=(v=i.parameters)==null?void 0:v.docs)==null?void 0:y.source}}};const J=["Default","DefaultWithButton"];export{n as Default,i as DefaultWithButton,J as __namedExportsOrder,H as default};
