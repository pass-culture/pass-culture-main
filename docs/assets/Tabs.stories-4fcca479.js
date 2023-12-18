import{K as I}from"./index-35a6a567.js";import{s as v}from"./stroke-library-916344a8.js";import{s as y}from"./stroke-user-4375f005.js";import{j as e}from"./jsx-runtime-ffb262ed.js";import{c as N}from"./index-a587463d.js";import{u as O,L as j}from"./index-c6e8a24e.js";import{B as T,a as K}from"./Button-b5b8096d.js";import{S as L}from"./SvgIcon-c0bf369c.js";import"./index-76fb7be0.js";import"./_commonjsHelpers-de833af9.js";import"./index-48a71f03.js";import"./full-right-83efe067.js";import"./Button.module-ec1646c9.js";import"./stroke-pass-cf331655.js";import"./Tooltip-7f0a196a.js";import"./useTooltipProps-b20503ef.js";const B="_tabs_18dtl_2",t={tabs:B,"tabs-tab":"_tabs-tab_18dtl_8","tabs-tab-label":"_tabs-tab-label_18dtl_14","tabs-tab-icon":"_tabs-tab-icon_18dtl_17","tabs-tab-link":"_tabs-tab-link_18dtl_24","tabs-tab-button":"_tabs-tab-button_18dtl_30","is-selected":"_is-selected_18dtl_38"},C="24",l=({nav:s,selectedKey:k,tabs:g})=>{const h=O(),o=e.jsx("ul",{className:t.tabs,children:g.map(({key:c,label:d,url:a,icon:r,onClick:x})=>e.jsx("li",{className:N(t["tabs-tab"],{[t["is-selected"]]:k===c}),children:a?e.jsxs(j,{className:t["tabs-tab-link"],to:a,"aria-current":s&&h.pathname===a?"page":void 0,children:[r&&e.jsx(L,{src:r,alt:"",className:t["tabs-tab-icon"],width:C}),e.jsx("span",{className:t["tabs-tab-label"],children:d})]},`tab${a}`):e.jsx(T,{variant:K.TERNARY,icon:r,onClick:x,className:t["tabs-tab-button"],children:d})},`tab_${c}`))});return s?e.jsx("nav",{"aria-label":s,children:o}):o},E=l;try{l.displayName="Tabs",l.__docgenInfo={description:"",displayName:"Tabs",props:{nav:{defaultValue:null,description:"",name:"nav",required:!1,type:{name:"string"}},tabs:{defaultValue:null,description:"",name:"tabs",required:!0,type:{name:"Tab[]"}},selectedKey:{defaultValue:null,description:"",name:"selectedKey",required:!1,type:{name:"string"}}}}}catch{}const H={title:"ui-kit/Tabs",decorators:[I],component:E},i={args:{selectedKey:"individual",tabs:[{label:"Offres individuelles",url:"offres/indiv",key:"individual",icon:y},{label:"Offres collectives",url:"offres/collectives",key:"collective",icon:v}]}},n={args:{selectedKey:"individual",tabs:[{label:"Offres individuelles",onClick:()=>{},key:"individual",icon:y},{label:"Offres collectives",onClick:()=>{},key:"collective",icon:v}]}};var b,u,m;i.parameters={...i.parameters,docs:{...(b=i.parameters)==null?void 0:b.docs,source:{originalSource:`{
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
}`,...(_=(f=n.parameters)==null?void 0:f.docs)==null?void 0:_.source}}};const J=["Default","DefaultWithButton"];export{i as Default,n as DefaultWithButton,J as __namedExportsOrder,H as default};
