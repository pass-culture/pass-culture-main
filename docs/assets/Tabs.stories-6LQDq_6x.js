import{K as I}from"./index-DPbpeW37.js";import{s as y}from"./stroke-library-pK3ZobR5.js";import{s as k}from"./stroke-user-_jU816YT.js";import{j as e}from"./jsx-runtime-iXOPPpZ7.js";import{c as N}from"./index-XNbs-YUW.js";import{u as j,L as O}from"./index-Odt4icYv.js";import{B as T,a as K}from"./Button-8IihqDqY.js";import{S as L}from"./SvgIcon-UUSKXfrA.js";import"./index-7OBYoplD.js";import"./_commonjsHelpers-4gQjN7DL.js";import"./index-NZh7eYUr.js";import"./Button.module-yhzTO7gk.js";import"./stroke-pass-84wyy11D.js";import"./Tooltip-ryJtHgPl.js";import"./useTooltipProps-Xf9SOXrU.js";const B="_tabs_18dtl_2",t={tabs:B,"tabs-tab":"_tabs-tab_18dtl_8","tabs-tab-label":"_tabs-tab-label_18dtl_14","tabs-tab-icon":"_tabs-tab-icon_18dtl_17","tabs-tab-link":"_tabs-tab-link_18dtl_24","tabs-tab-button":"_tabs-tab-button_18dtl_30","is-selected":"_is-selected_18dtl_38"},C="24",l=({nav:s,selectedKey:g,tabs:o})=>{const x=j(),c=o.length>0?e.jsx("ul",{className:t.tabs,children:o.map(({key:d,label:b,url:a,icon:r,onClick:h})=>e.jsx("li",{className:N(t["tabs-tab"],{[t["is-selected"]]:g===d}),children:a?e.jsxs(O,{className:t["tabs-tab-link"],to:a,"aria-current":s&&x.pathname===a?"page":void 0,children:[r&&e.jsx(L,{src:r,alt:"",className:t["tabs-tab-icon"],width:C}),e.jsx("span",{className:t["tabs-tab-label"],children:b})]},`tab${a}`):e.jsx(T,{variant:K.TERNARY,icon:r,onClick:h,className:t["tabs-tab-button"],children:b})},`tab_${d}`))}):e.jsx(e.Fragment,{});return s?e.jsx("nav",{"aria-label":s,children:c}):c},E=l;try{l.displayName="Tabs",l.__docgenInfo={description:"",displayName:"Tabs",props:{nav:{defaultValue:null,description:"",name:"nav",required:!1,type:{name:"string"}},tabs:{defaultValue:null,description:"",name:"tabs",required:!0,type:{name:"Tab[]"}},selectedKey:{defaultValue:null,description:"",name:"selectedKey",required:!1,type:{name:"string"}}}}}catch{}const G={title:"ui-kit/Tabs",decorators:[I],component:E},i={args:{selectedKey:"individual",tabs:[{label:"Offres individuelles",url:"offres/indiv",key:"individual",icon:k},{label:"Offres collectives",url:"offres/collectives",key:"collective",icon:y}]}},n={args:{selectedKey:"individual",tabs:[{label:"Offres individuelles",onClick:()=>{},key:"individual",icon:k},{label:"Offres collectives",onClick:()=>{},key:"collective",icon:y}]}};var u,m,p;i.parameters={...i.parameters,docs:{...(u=i.parameters)==null?void 0:u.docs,source:{originalSource:`{
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
}`,...(p=(m=i.parameters)==null?void 0:m.docs)==null?void 0:p.source}}};var f,_,v;n.parameters={...n.parameters,docs:{...(f=n.parameters)==null?void 0:f.docs,source:{originalSource:`{
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
}`,...(v=(_=n.parameters)==null?void 0:_.docs)==null?void 0:v.source}}};const H=["Default","DefaultWithButton"];export{i as Default,n as DefaultWithButton,H as __namedExportsOrder,G as default};
