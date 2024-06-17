import{K as j}from"./index-D8J9PAlt.js";import{s as k}from"./stroke-library-B87NDtez.js";import{s as g}from"./stroke-user-JNyZapNG.js";import{j as e}from"./jsx-runtime-X2b_N9AH.js";import{c as u}from"./index-BpvXyOxN.js";import{L as O}from"./index-CWNn-QuQ.js";import{B as K}from"./Button-8V_iIDLg.js";import{B as T}from"./types-DjX_gQD6.js";import{S as B}from"./SvgIcon-DP_815J1.js";import{u as L}from"./index-DoMt6nTV.js";import"./index-uCp2LrAq.js";import"./_commonjsHelpers-BosuxZz1.js";import"./index-NGkXgOa-.js";import"./stroke-pass-C0Oiu4_F.js";import"./Tooltip-B_yv2e98.js";import"./useTooltipProps-B8Mr20U1.js";import"./Button.module-CufKSpV2.js";const V="_tabs_nu5fv_2",t={tabs:V,"tabs-tab":"_tabs-tab_nu5fv_8","tabs-tab-label":"_tabs-tab-label_nu5fv_14","tabs-tab-icon":"_tabs-tab-icon_nu5fv_17","tabs-tab-link":"_tabs-tab-link_nu5fv_24","tabs-tab-button":"_tabs-tab-button_nu5fv_30","is-selected":"_is-selected_nu5fv_38"},C="24",l=({nav:a,selectedKey:N,tabs:o,className:h})=>{const x=L(),c=o.length>0?e.jsx("ul",{className:u(t.tabs,h),children:o.map(({key:d,label:b,url:s,icon:r,onClick:I})=>e.jsx("li",{className:u(t["tabs-tab"],{[t["is-selected"]]:N===d}),children:s?e.jsxs(O,{className:t["tabs-tab-link"],to:s,"aria-current":a&&x.pathname===s?"page":void 0,children:[r&&e.jsx(B,{src:r,alt:"",className:t["tabs-tab-icon"],width:C}),e.jsx("span",{className:t["tabs-tab-label"],children:b})]},`tab${s}`):e.jsx(K,{variant:T.TERNARY,icon:r,onClick:I,className:t["tabs-tab-button"],children:b})},`tab_${d}`))}):e.jsx(e.Fragment,{});return a?e.jsx("nav",{"aria-label":a,children:c}):c};try{l.displayName="Tabs",l.__docgenInfo={description:"",displayName:"Tabs",props:{nav:{defaultValue:null,description:"",name:"nav",required:!1,type:{name:"string"}},tabs:{defaultValue:null,description:"",name:"tabs",required:!0,type:{name:"Tab[]"}},selectedKey:{defaultValue:null,description:"",name:"selectedKey",required:!1,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}const J={title:"ui-kit/Tabs",decorators:[j],component:l},n={args:{selectedKey:"individual",tabs:[{label:"Offres individuelles",url:"offres/indiv",key:"individual",icon:g},{label:"Offres collectives",url:"offres/collectives",key:"collective",icon:k}]}},i={args:{selectedKey:"individual",tabs:[{label:"Offres individuelles",onClick:()=>{},key:"individual",icon:g},{label:"Offres collectives",onClick:()=>{},key:"collective",icon:k}]}};var m,f,p;n.parameters={...n.parameters,docs:{...(m=n.parameters)==null?void 0:m.docs,source:{originalSource:`{
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
