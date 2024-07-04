import{K as I}from"./index-BY6hXnbG.js";import{s as k}from"./stroke-library-B87NDtez.js";import{s as q}from"./stroke-user-JNyZapNG.js";import{j as e}from"./jsx-runtime-X2b_N9AH.js";import{c as m}from"./index-BpvXyOxN.js";import{L as j}from"./index-BnlysBpt.js";import{B as O}from"./Button-DnM-aOrW.js";import{B as K}from"./types-DjX_gQD6.js";import{S as T}from"./SvgIcon-DP_815J1.js";import{u as B}from"./index-BsMtPDqD.js";import"./index-uCp2LrAq.js";import"./_commonjsHelpers-BosuxZz1.js";import"./index-C74Dn3Vq.js";import"./stroke-pass-C0Oiu4_F.js";import"./Tooltip-B_yv2e98.js";import"./useTooltipProps-B8Mr20U1.js";import"./Button.module-DVCdx56u.js";const L="_tabs_8qqr5_2",t={tabs:L,"tabs-tab":"_tabs-tab_8qqr5_8","tabs-tab-label":"_tabs-tab-label_8qqr5_15","tabs-tab-icon":"_tabs-tab-icon_8qqr5_18","tabs-tab-link":"_tabs-tab-link_8qqr5_25","tabs-tab-button":"_tabs-tab-button_8qqr5_31","is-selected":"_is-selected_8qqr5_39"},V="24",l=({nav:a,selectedKey:g,tabs:o,className:N})=>{const h=B(),c=o.length>0?e.jsx("ul",{className:m(t.tabs,N),children:o.map(({key:d,label:b,url:s,icon:n,onClick:x})=>e.jsx("li",{className:m(t["tabs-tab"],{[t["is-selected"]]:g===d}),children:s?e.jsxs(j,{className:t["tabs-tab-link"],to:s,"aria-current":a&&h.pathname===s?"page":void 0,children:[n&&e.jsx(T,{src:n,alt:"",className:t["tabs-tab-icon"],width:V}),e.jsx("span",{className:t["tabs-tab-label"],children:b})]},`tab${s}`):e.jsx(O,{variant:K.TERNARY,icon:n,onClick:x,className:t["tabs-tab-button"],children:b})},`tab_${d}`))}):e.jsx(e.Fragment,{});return a?e.jsx("nav",{"aria-label":a,children:c}):c};try{l.displayName="Tabs",l.__docgenInfo={description:"",displayName:"Tabs",props:{nav:{defaultValue:null,description:"",name:"nav",required:!1,type:{name:"string"}},tabs:{defaultValue:null,description:"",name:"tabs",required:!0,type:{name:"Tab[]"}},selectedKey:{defaultValue:null,description:"",name:"selectedKey",required:!1,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}const J={title:"ui-kit/Tabs",decorators:[I],component:l},r={args:{selectedKey:"individual",tabs:[{label:"Offres individuelles",url:"offres/indiv",key:"individual",icon:q},{label:"Offres collectives",url:"offres/collectives",key:"collective",icon:k}]}},i={args:{selectedKey:"individual",tabs:[{label:"Offres individuelles",onClick:()=>{},key:"individual",icon:q},{label:"Offres collectives",onClick:()=>{},key:"collective",icon:k}]}};var u,p,f;r.parameters={...r.parameters,docs:{...(u=r.parameters)==null?void 0:u.docs,source:{originalSource:`{
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
}`,...(f=(p=r.parameters)==null?void 0:p.docs)==null?void 0:f.source}}};var _,v,y;i.parameters={...i.parameters,docs:{...(_=i.parameters)==null?void 0:_.docs,source:{originalSource:`{
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
}`,...(y=(v=i.parameters)==null?void 0:v.docs)==null?void 0:y.source}}};const P=["Default","DefaultWithButton"];export{r as Default,i as DefaultWithButton,P as __namedExportsOrder,J as default};
