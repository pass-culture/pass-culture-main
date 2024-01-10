import{K as I}from"./index-MnnsouR9.js";import{s as v}from"./stroke-library-pK3ZobR5.js";import{s as y}from"./stroke-user-_jU816YT.js";import{j as e}from"./jsx-runtime-iXOPPpZ7.js";import{c as N}from"./index-XNbs-YUW.js";import{u as O,L as j}from"./index-qxkmzToN.js";import{B as T,a as K}from"./Button-DBB44s9R.js";import{S as L}from"./SvgIcon-UUSKXfrA.js";import"./index-7OBYoplD.js";import"./_commonjsHelpers-4gQjN7DL.js";import"./index-NZh7eYUr.js";import"./Button.module-yhzTO7gk.js";import"./stroke-pass-84wyy11D.js";import"./Tooltip-b2Ucs1Op.js";import"./useTooltipProps-Xf9SOXrU.js";const B="_tabs_18dtl_2",t={tabs:B,"tabs-tab":"_tabs-tab_18dtl_8","tabs-tab-label":"_tabs-tab-label_18dtl_14","tabs-tab-icon":"_tabs-tab-icon_18dtl_17","tabs-tab-link":"_tabs-tab-link_18dtl_24","tabs-tab-button":"_tabs-tab-button_18dtl_30","is-selected":"_is-selected_18dtl_38"},C="24",l=({nav:s,selectedKey:k,tabs:g})=>{const h=O(),o=e.jsx("ul",{className:t.tabs,children:g.map(({key:c,label:d,url:a,icon:r,onClick:x})=>e.jsx("li",{className:N(t["tabs-tab"],{[t["is-selected"]]:k===c}),children:a?e.jsxs(j,{className:t["tabs-tab-link"],to:a,"aria-current":s&&h.pathname===a?"page":void 0,children:[r&&e.jsx(L,{src:r,alt:"",className:t["tabs-tab-icon"],width:C}),e.jsx("span",{className:t["tabs-tab-label"],children:d})]},`tab${a}`):e.jsx(T,{variant:K.TERNARY,icon:r,onClick:x,className:t["tabs-tab-button"],children:d})},`tab_${c}`))});return s?e.jsx("nav",{"aria-label":s,children:o}):o},E=l;try{l.displayName="Tabs",l.__docgenInfo={description:"",displayName:"Tabs",props:{nav:{defaultValue:null,description:"",name:"nav",required:!1,type:{name:"string"}},tabs:{defaultValue:null,description:"",name:"tabs",required:!0,type:{name:"Tab[]"}},selectedKey:{defaultValue:null,description:"",name:"selectedKey",required:!1,type:{name:"string"}}}}}catch{}const G={title:"ui-kit/Tabs",decorators:[I],component:E},i={args:{selectedKey:"individual",tabs:[{label:"Offres individuelles",url:"offres/indiv",key:"individual",icon:y},{label:"Offres collectives",url:"offres/collectives",key:"collective",icon:v}]}},n={args:{selectedKey:"individual",tabs:[{label:"Offres individuelles",onClick:()=>{},key:"individual",icon:y},{label:"Offres collectives",onClick:()=>{},key:"collective",icon:v}]}};var b,u,m;i.parameters={...i.parameters,docs:{...(b=i.parameters)==null?void 0:b.docs,source:{originalSource:`{
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
