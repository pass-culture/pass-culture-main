import{K as I}from"./index-b5da178e.js";import{s as v}from"./stroke-library-916344a8.js";import{s as y}from"./stroke-user-4375f005.js";import{j as e}from"./jsx-runtime-ffb262ed.js";import{c as N}from"./index-a587463d.js";import{u as O,L as j}from"./index-d4657265.js";import{B as T,a as K}from"./Button-9d8c04a1.js";import{S as L}from"./SvgIcon-c0bf369c.js";import"./index-76fb7be0.js";import"./_commonjsHelpers-de833af9.js";import"./full-right-83efe067.js";import"./Button.module-ec1646c9.js";import"./stroke-pass-cf331655.js";import"./Tooltip-7f0a196a.js";import"./useTooltipProps-b20503ef.js";const B="_tabs_ca771_2",a={tabs:B,"tabs-tab":"_tabs-tab_ca771_8","tabs-tab-label":"_tabs-tab-label_ca771_14","tabs-tab-icon":"_tabs-tab-icon_ca771_17","tabs-tab-link":"_tabs-tab-link_ca771_24","tabs-tab-button":"_tabs-tab-button_ca771_30","is-selected":"_is-selected_ca771_38"},C="24",o=({nav:t,selectedKey:k,tabs:g})=>{const h=O(),l=e.jsx("ul",{className:a.tabs,children:g.map(({key:c,label:d,url:s,icon:r,onClick:x})=>e.jsx("li",{className:N(a["tabs-tab"],{[a["is-selected"]]:k===c}),children:s?e.jsxs(j,{className:a["tabs-tab-link"],to:s,"aria-current":t&&h.pathname===s?"page":void 0,children:[r&&e.jsx(L,{src:r,alt:"",className:a["tabs-tab-icon"],width:C}),e.jsx("span",{className:a["tabs-tab-label"],children:d})]},`tab${s}`):e.jsx(T,{variant:K.TERNARY,icon:r,onClick:x,className:a["tabs-tab-button"],children:d})},`tab_${c}`))});return t?e.jsx("nav",{"aria-label":t,children:l}):l},E=o;try{o.displayName="Tabs",o.__docgenInfo={description:"",displayName:"Tabs",props:{nav:{defaultValue:null,description:"",name:"nav",required:!1,type:{name:"string"}},tabs:{defaultValue:null,description:"",name:"tabs",required:!0,type:{name:"Tab[]"}},selectedKey:{defaultValue:null,description:"",name:"selectedKey",required:!1,type:{name:"string"}}}}}catch{}const G={title:"ui-kit/Tabs",decorators:[I],component:E},i={args:{selectedKey:"individual",tabs:[{label:"Offres individuelles",url:"offres/indiv",key:"individual",icon:y},{label:"Offres collectives",url:"offres/collectives",key:"collective",icon:v}]}},n={args:{selectedKey:"individual",tabs:[{label:"Offres individuelles",onClick:()=>{},key:"individual",icon:y},{label:"Offres collectives",onClick:()=>{},key:"collective",icon:v}]}};var b,u,m;i.parameters={...i.parameters,docs:{...(b=i.parameters)==null?void 0:b.docs,source:{originalSource:`{
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
}`,...(m=(u=i.parameters)==null?void 0:u.docs)==null?void 0:m.source}}};var p,f,_;n.parameters={...n.parameters,docs:{...(p=n.parameters)==null?void 0:p.docs,source:{originalSource:`{
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
}`,...(_=(f=n.parameters)==null?void 0:f.docs)==null?void 0:_.source}}};const H=["Default","DefaultWithButton"];export{i as Default,n as DefaultWithButton,H as __namedExportsOrder,G as default};
