import{K as I}from"./index-zsCDaiFI.js";import{s as y}from"./stroke-library-pK3ZobR5.js";import{s as k}from"./stroke-user-_jU816YT.js";import{j as e}from"./jsx-runtime-vNq4Oc-g.js";import{c as N}from"./index-XNbs-YUW.js";import{u as j,L as O}from"./index-VkxvJQxW.js";import{B as T}from"./ButtonLink-iC8iNd8u.js";import{B as w}from"./Button-ySGmec_7.js";import{S as K}from"./SvgIcon-QVOPtTle.js";import"./index-4g5l5LRQ.js";import"./_commonjsHelpers-4gQjN7DL.js";import"./index-CQtvWCGL.js";import"./Button.module-fn58QZwY.js";import"./stroke-pass-84wyy11D.js";import"./Tooltip-kKBX527K.js";import"./useTooltipProps-5VZ0BXiJ.js";const B="_tabs_1ie1w_2",t={tabs:B,"tabs-tab":"_tabs-tab_1ie1w_8","tabs-tab-label":"_tabs-tab-label_1ie1w_14","tabs-tab-icon":"_tabs-tab-icon_1ie1w_17","tabs-tab-link":"_tabs-tab-link_1ie1w_24","tabs-tab-button":"_tabs-tab-button_1ie1w_30","is-selected":"_is-selected_1ie1w_38"},L="24",o=({nav:s,selectedKey:g,tabs:l})=>{const x=j(),c=l.length>0?e.jsx("ul",{className:t.tabs,children:l.map(({key:d,label:b,url:a,icon:r,onClick:h})=>e.jsx("li",{className:N(t["tabs-tab"],{[t["is-selected"]]:g===d}),children:a?e.jsxs(O,{className:t["tabs-tab-link"],to:a,"aria-current":s&&x.pathname===a?"page":void 0,children:[r&&e.jsx(K,{src:r,alt:"",className:t["tabs-tab-icon"],width:L}),e.jsx("span",{className:t["tabs-tab-label"],children:b})]},`tab${a}`):e.jsx(w,{variant:T.TERNARY,icon:r,onClick:h,className:t["tabs-tab-button"],children:b})},`tab_${d}`))}):e.jsx(e.Fragment,{});return s?e.jsx("nav",{"aria-label":s,children:c}):c},C=o;try{o.displayName="Tabs",o.__docgenInfo={description:"",displayName:"Tabs",props:{nav:{defaultValue:null,description:"",name:"nav",required:!1,type:{name:"string"}},tabs:{defaultValue:null,description:"",name:"tabs",required:!0,type:{name:"Tab[]"}},selectedKey:{defaultValue:null,description:"",name:"selectedKey",required:!1,type:{name:"string"}}}}}catch{}const H={title:"ui-kit/Tabs",decorators:[I],component:C},i={args:{selectedKey:"individual",tabs:[{label:"Offres individuelles",url:"offres/indiv",key:"individual",icon:k},{label:"Offres collectives",url:"offres/collectives",key:"collective",icon:y}]}},n={args:{selectedKey:"individual",tabs:[{label:"Offres individuelles",onClick:()=>{},key:"individual",icon:k},{label:"Offres collectives",onClick:()=>{},key:"collective",icon:y}]}};var m,u,p;i.parameters={...i.parameters,docs:{...(m=i.parameters)==null?void 0:m.docs,source:{originalSource:`{
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
}`,...(p=(u=i.parameters)==null?void 0:u.docs)==null?void 0:p.source}}};var f,_,v;n.parameters={...n.parameters,docs:{...(f=n.parameters)==null?void 0:f.docs,source:{originalSource:`{
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
}`,...(v=(_=n.parameters)==null?void 0:_.docs)==null?void 0:v.source}}};const J=["Default","DefaultWithButton"];export{i as Default,n as DefaultWithButton,J as __namedExportsOrder,H as default};
