import{V as v}from"./index-BNgFzG03.js";import{j as e}from"./jsx-runtime-BYYWji4R.js";import{c as r}from"./index-DeARc5FM.js";import{L as k}from"./chunk-DQRVZFIR-DDz1T7yI.js";import"./index-ClcD9ViR.js";import"./_commonjsHelpers-Cpj98o6Y.js";const s={"menu-list":"_menu-list_lkwo2_1","menu-list-item":"_menu-list-item_lkwo2_7","is-selected":"_is-selected_lkwo2_22","visually-hidden":"_visually-hidden_lkwo2_34"},n=({navLabel:a,selectedKey:t,links:m,className:u})=>e.jsx("nav",{"aria-label":a,children:e.jsx("ul",{className:r(s["menu-list"],u),children:m.map(({key:i,label:p,url:f})=>e.jsx("li",{children:e.jsx(k,{to:f,className:r(s["menu-list-item"],{[s["is-selected"]]:t===i}),children:e.jsxs("span",{className:s["menu-list-item-label"],children:[t===i&&e.jsx("span",{className:s["visually-hidden"],children:"Lien actif"}),p]})})},i))})});try{n.displayName="NavLinkItems",n.__docgenInfo={description:"The NavLinkItems component is used to render a list of navigation links.",displayName:"NavLinkItems",props:{navLabel:{defaultValue:null,description:"Navigation accessible name",name:"navLabel",required:!0,type:{name:"string"}},links:{defaultValue:null,description:"An array of links to be rendered.",name:"links",required:!0,type:{name:"NavLinkItem[]"}},selectedKey:{defaultValue:null,description:"The key of the selected link.",name:"selectedKey",required:!1,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}const g={title:"ui-kit/NavLinkItems",decorators:[v],component:n},l={args:{selectedKey:"individual",links:[{label:"Offres individuelles",url:"#",key:"individual"},{label:"Offres collectives",url:"#",key:"collective"}]}};var d,o,c;l.parameters={...l.parameters,docs:{...(d=l.parameters)==null?void 0:d.docs,source:{originalSource:`{
  args: {
    selectedKey: 'individual',
    links: [{
      label: 'Offres individuelles',
      url: '#',
      key: 'individual'
    }, {
      label: 'Offres collectives',
      url: '#',
      key: 'collective'
    }]
  }
}`,...(c=(o=l.parameters)==null?void 0:o.docs)==null?void 0:c.source}}};const x=["Default"];export{l as Default,x as __namedExportsOrder,g as default};
