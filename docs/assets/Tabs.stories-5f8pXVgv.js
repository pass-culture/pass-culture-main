import{K as j}from"./index-C4Y-b_h4.js";import{s as y}from"./stroke-library-B87NDtez.js";import{s as g}from"./stroke-user-JNyZapNG.js";import{j as e}from"./jsx-runtime-Nms4Y4qS.js";import{c as m}from"./index-BpvXyOxN.js";import{u as O,L as K}from"./index-C_BCaKYK.js";import{B as T}from"./Button-OPe0WAQ7.js";import{B}from"./types-DjX_gQD6.js";import{S as L}from"./SvgIcon-Cibea2Sc.js";import"./index-BwDkhjyp.js";import"./_commonjsHelpers-BosuxZz1.js";import"./index-CReuRBEY.js";import"./stroke-pass-C0Oiu4_F.js";import"./Tooltip-4sMgqXzt.js";import"./useTooltipProps-DNYEmy4z.js";import"./Button.module-9zQJcsLA.js";const V="_tabs_1kr25_1",a={tabs:V,"tabs-tab":"_tabs-tab_1kr25_7","tabs-tab-label":"_tabs-tab-label_1kr25_14","tabs-tab-icon":"_tabs-tab-icon_1kr25_17","tabs-tab-link":"_tabs-tab-link_1kr25_24","tabs-tab-button":"_tabs-tab-button_1kr25_30","is-selected":"_is-selected_1kr25_38"},C="24",l=({nav:t,selectedKey:N,tabs:o,className:h})=>{const x=O(),c=o.length>0?e.jsx("ul",{className:m(a.tabs,h),children:o.map(({key:d,label:b,url:s,icon:n,onClick:I})=>e.jsx("li",{className:m(a["tabs-tab"],{[a["is-selected"]]:N===d}),children:s?e.jsxs(K,{className:a["tabs-tab-link"],to:s,"aria-current":t&&x.pathname===s?"page":void 0,children:[n&&e.jsx(L,{src:n,alt:"",className:a["tabs-tab-icon"],width:C}),e.jsx("span",{className:a["tabs-tab-label"],children:b})]},`tab${s}`):e.jsx(T,{variant:B.TERNARY,icon:n,onClick:I,className:a["tabs-tab-button"],children:b})},`tab_${d}`))}):e.jsx(e.Fragment,{});return t?e.jsx("nav",{"aria-label":t,children:c}):c};try{l.displayName="Tabs",l.__docgenInfo={description:"",displayName:"Tabs",props:{nav:{defaultValue:null,description:"",name:"nav",required:!1,type:{name:"string"}},tabs:{defaultValue:null,description:"",name:"tabs",required:!0,type:{name:"Tab[]"}},selectedKey:{defaultValue:null,description:"",name:"selectedKey",required:!1,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}const H={title:"ui-kit/Tabs",decorators:[j],component:l},r={args:{selectedKey:"individual",tabs:[{label:"Offres individuelles",url:"offres/indiv",key:"individual",icon:g},{label:"Offres collectives",url:"offres/collectives",key:"collective",icon:y}]}},i={args:{selectedKey:"individual",tabs:[{label:"Offres individuelles",onClick:()=>{},key:"individual",icon:g},{label:"Offres collectives",onClick:()=>{},key:"collective",icon:y}]}};var u,p,f;r.parameters={...r.parameters,docs:{...(u=r.parameters)==null?void 0:u.docs,source:{originalSource:`{
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
}`,...(f=(p=r.parameters)==null?void 0:p.docs)==null?void 0:f.source}}};var _,k,v;i.parameters={...i.parameters,docs:{...(_=i.parameters)==null?void 0:_.docs,source:{originalSource:`{
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
}`,...(v=(k=i.parameters)==null?void 0:k.docs)==null?void 0:v.source}}};const J=["Default","DefaultWithButton"];export{r as Default,i as DefaultWithButton,J as __namedExportsOrder,H as default};
