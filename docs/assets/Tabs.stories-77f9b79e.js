import{K as I}from"./index-b5da178e.js";import{s as v}from"./stroke-library-916344a8.js";import{s as y}from"./stroke-user-4375f005.js";import{j as e}from"./jsx-runtime-ffb262ed.js";import{c as N}from"./index-a587463d.js";import{u as O,L as j}from"./index-d4657265.js";import{B as T,a as K}from"./Button-9d8c04a1.js";import{S as L}from"./SvgIcon-c0bf369c.js";import"./index-76fb7be0.js";import"./_commonjsHelpers-de833af9.js";import"./full-right-83efe067.js";import"./Button.module-ec1646c9.js";import"./stroke-pass-cf331655.js";import"./Tooltip-7f0a196a.js";import"./useTooltipProps-b20503ef.js";const B="_tabs_fpbne_2",t={tabs:B,"tabs-tab":"_tabs-tab_fpbne_6","tabs-tab-label":"_tabs-tab-label_fpbne_13","tabs-tab-icon":"_tabs-tab-icon_fpbne_16","tabs-tab-link":"_tabs-tab-link_fpbne_23","tabs-tab-button":"_tabs-tab-button_fpbne_31","is-selected":"_is-selected_fpbne_39"},C="24",o=({nav:s,selectedKey:k,tabs:g})=>{const h=O(),l=e.jsx("ul",{className:t.tabs,children:g.map(({key:c,label:b,url:a,icon:r,onClick:x})=>e.jsx("li",{className:N(t["tabs-tab"],{[t["is-selected"]]:k===c}),children:a?e.jsxs(j,{className:t["tabs-tab-link"],to:a,"aria-current":s&&h.pathname===a?"page":void 0,children:[r&&e.jsx(L,{src:r,alt:"",className:t["tabs-tab-icon"],width:C}),e.jsx("span",{className:t["tabs-tab-label"],children:b})]},`tab${a}`):e.jsx(T,{variant:K.TERNARY,icon:r,onClick:x,className:t["tabs-tab-button"],children:b})},`tab_${c}`))});return s?e.jsx("nav",{"aria-label":s,children:l}):l},E=o;try{o.displayName="Tabs",o.__docgenInfo={description:"",displayName:"Tabs",props:{nav:{defaultValue:null,description:"",name:"nav",required:!1,type:{name:"string"}},tabs:{defaultValue:null,description:"",name:"tabs",required:!0,type:{name:"Tab[]"}},selectedKey:{defaultValue:null,description:"",name:"selectedKey",required:!1,type:{name:"string"}}}}}catch{}const G={title:"ui-kit/Tabs",decorators:[I],component:E},n={args:{selectedKey:"individual",tabs:[{label:"Offres individuelles",url:"offres/indiv",key:"individual",icon:y},{label:"Offres collectives",url:"offres/collectives",key:"collective",icon:v}]}},i={args:{selectedKey:"individual",tabs:[{label:"Offres individuelles",onClick:()=>{},key:"individual",icon:y},{label:"Offres collectives",onClick:()=>{},key:"collective",icon:v}]}};var d,u,p;n.parameters={...n.parameters,docs:{...(d=n.parameters)==null?void 0:d.docs,source:{originalSource:`{
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
}`,...(p=(u=n.parameters)==null?void 0:u.docs)==null?void 0:p.source}}};var f,m,_;i.parameters={...i.parameters,docs:{...(f=i.parameters)==null?void 0:f.docs,source:{originalSource:`{
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
}`,...(_=(m=i.parameters)==null?void 0:m.docs)==null?void 0:_.source}}};const H=["Default","DefaultWithButton"];export{n as Default,i as DefaultWithButton,H as __namedExportsOrder,G as default};
