import{K as x}from"./index-b5da178e.js";import{s as y}from"./stroke-library-916344a8.js";import{s as v}from"./stroke-user-4375f005.js";import{j as e}from"./jsx-runtime-ffb262ed.js";import{c as I}from"./index-a587463d.js";import{u as N,L as O}from"./index-d4657265.js";import{B as j,a as T}from"./Button-4f27956d.js";import{S as K}from"./SvgIcon-c0bf369c.js";import"./index-76fb7be0.js";import"./_commonjsHelpers-de833af9.js";import"./full-right-83efe067.js";import"./Button.module-a8fe741a.js";import"./stroke-pass-cf331655.js";import"./Tooltip-7f0a196a.js";import"./useTooltipProps-b20503ef.js";const L="_tabs_opqqy_2",s={tabs:L,"tabs-tab":"_tabs-tab_opqqy_6","tabs-tab-icon":"_tabs-tab-icon_opqqy_13","tabs-tab-link":"_tabs-tab-link_opqqy_20","tabs-tab-button":"_tabs-tab-button_opqqy_28","is-selected":"_is-selected_opqqy_36"},B="24",r=({nav:t,selectedKey:k,tabs:q})=>{const g=N(),l=e.jsx("ul",{className:s.tabs,children:q.map(({key:c,label:d,url:a,icon:o,onClick:h})=>e.jsx("li",{className:I(s["tabs-tab"],{[s["is-selected"]]:k===c}),children:a?e.jsxs(O,{className:s["tabs-tab-link"],to:a,"aria-current":t&&g.pathname===a?"page":void 0,children:[o&&e.jsx(K,{src:o,alt:"",className:s["tabs-tab-icon"],width:B}),e.jsx("span",{children:d})]},`tab${a}`):e.jsx(j,{variant:T.TERNARY,icon:o,onClick:h,className:s["tabs-tab-button"],children:d})},`tab_${c}`))});return t?e.jsx("nav",{"aria-label":t,children:l}):l},C=r;try{r.displayName="Tabs",r.__docgenInfo={description:"",displayName:"Tabs",props:{nav:{defaultValue:null,description:"",name:"nav",required:!1,type:{name:"string"}},tabs:{defaultValue:null,description:"",name:"tabs",required:!0,type:{name:"Tab[]"}},selectedKey:{defaultValue:null,description:"",name:"selectedKey",required:!1,type:{name:"string"}}}}}catch{}const G={title:"ui-kit/Tabs",decorators:[x],component:C},i={args:{selectedKey:"individual",tabs:[{label:"Offres individuelles",url:"offres/indiv",key:"individual",icon:v},{label:"Offres collectives",url:"offres/collectives",key:"collective",icon:y}]}},n={args:{selectedKey:"individual",tabs:[{label:"Offres individuelles",onClick:()=>{},key:"individual",icon:v},{label:"Offres collectives",onClick:()=>{},key:"collective",icon:y}]}};var b,u,p;i.parameters={...i.parameters,docs:{...(b=i.parameters)==null?void 0:b.docs,source:{originalSource:`{
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
}`,...(p=(u=i.parameters)==null?void 0:u.docs)==null?void 0:p.source}}};var m,f,_;n.parameters={...n.parameters,docs:{...(m=n.parameters)==null?void 0:m.docs,source:{originalSource:`{
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
//# sourceMappingURL=Tabs.stories-725d0f5c.js.map
