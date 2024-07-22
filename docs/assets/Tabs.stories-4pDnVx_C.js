import{K as j}from"./index-CAlw3Dpn.js";import{s as k}from"./stroke-library-B87NDtez.js";import{s as g}from"./stroke-user-JNyZapNG.js";import{j as e}from"./jsx-runtime-Nms4Y4qS.js";import{c as m}from"./index-BpvXyOxN.js";import{L as O}from"./index-DVQ4BpCr.js";import{B as K}from"./Button-FYdVlZ70.js";import{B as T}from"./types-DjX_gQD6.js";import{S as B}from"./SvgIcon-Cibea2Sc.js";import{u as L}from"./index-ZWEForty.js";import"./index-BwDkhjyp.js";import"./_commonjsHelpers-BosuxZz1.js";import"./index-CReuRBEY.js";import"./stroke-pass-C0Oiu4_F.js";import"./Tooltip-BpwAz3An.js";import"./useTooltipProps-DNYEmy4z.js";import"./Button.module-DJTvdY49.js";const V="_tabs_1a67p_2",a={tabs:V,"tabs-tab":"_tabs-tab_1a67p_8","tabs-tab-label":"_tabs-tab-label_1a67p_15","tabs-tab-icon":"_tabs-tab-icon_1a67p_18","tabs-tab-link":"_tabs-tab-link_1a67p_25","tabs-tab-button":"_tabs-tab-button_1a67p_31","is-selected":"_is-selected_1a67p_39"},C="24",l=({nav:t,selectedKey:N,tabs:o,className:h})=>{const x=L(),c=o.length>0?e.jsx("ul",{className:m(a.tabs,h),children:o.map(({key:d,label:b,url:s,icon:r,onClick:I})=>e.jsx("li",{className:m(a["tabs-tab"],{[a["is-selected"]]:N===d}),children:s?e.jsxs(O,{className:a["tabs-tab-link"],to:s,"aria-current":t&&x.pathname===s?"page":void 0,children:[r&&e.jsx(B,{src:r,alt:"",className:a["tabs-tab-icon"],width:C}),e.jsx("span",{className:a["tabs-tab-label"],children:b})]},`tab${s}`):e.jsx(K,{variant:T.TERNARY,icon:r,onClick:I,className:a["tabs-tab-button"],children:b})},`tab_${d}`))}):e.jsx(e.Fragment,{});return t?e.jsx("nav",{"aria-label":t,children:c}):c};try{l.displayName="Tabs",l.__docgenInfo={description:"",displayName:"Tabs",props:{nav:{defaultValue:null,description:"",name:"nav",required:!1,type:{name:"string"}},tabs:{defaultValue:null,description:"",name:"tabs",required:!0,type:{name:"Tab[]"}},selectedKey:{defaultValue:null,description:"",name:"selectedKey",required:!1,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}const J={title:"ui-kit/Tabs",decorators:[j],component:l},i={args:{selectedKey:"individual",tabs:[{label:"Offres individuelles",url:"offres/indiv",key:"individual",icon:g},{label:"Offres collectives",url:"offres/collectives",key:"collective",icon:k}]}},n={args:{selectedKey:"individual",tabs:[{label:"Offres individuelles",onClick:()=>{},key:"individual",icon:g},{label:"Offres collectives",onClick:()=>{},key:"collective",icon:k}]}};var u,p,f;i.parameters={...i.parameters,docs:{...(u=i.parameters)==null?void 0:u.docs,source:{originalSource:`{
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
