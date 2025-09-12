import{V as v}from"./index-QnyK0pSJ.js";import{j as e}from"./jsx-runtime-DF2Pcvd1.js";import{c as r}from"./index-DeARc5FM.js";import{L as _}from"./chunk-PVWAREVJ-Bt0DAUl0.js";import"./index-B2-qRKKC.js";import"./_commonjsHelpers-Cpj98o6Y.js";const i={"menu-list":"_menu-list_1ei89_1","menu-list-item":"_menu-list-item_1ei89_7","is-selected":"_is-selected_1ei89_22","visually-hidden":"_visually-hidden_1ei89_34"},n=({navLabel:a,selectedKey:t,links:m,className:u})=>e.jsx("nav",{"aria-label":a,children:e.jsx("ul",{className:r(i["menu-list"],u),children:m.map(({key:l,label:p,url:f})=>e.jsx("li",{children:e.jsx(_,{to:f,className:r(i["menu-list-item"],{[i["is-selected"]]:t===l}),children:e.jsxs("span",{className:i["menu-list-item-label"],children:[t===l&&e.jsx("span",{className:i["visually-hidden"],children:"Lien actif"}),p]})})},l))})});try{n.displayName="NavLinkItems",n.__docgenInfo={description:"The NavLinkItems component is used to render a list of navigation links.",displayName:"NavLinkItems",props:{navLabel:{defaultValue:null,description:"Navigation accessible name",name:"navLabel",required:!0,type:{name:"string"}},links:{defaultValue:null,description:"An array of links to be rendered.",name:"links",required:!0,type:{name:"NavLinkItem[]"}},selectedKey:{defaultValue:null,description:"The key of the selected link.",name:"selectedKey",required:!1,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}const g={title:"@/ui-kit/NavLinkItems",decorators:[v],component:n},s={args:{selectedKey:"individual",links:[{label:"Offres individuelles",url:"#",key:"individual"},{label:"Offres collectives",url:"#",key:"collective"}]}};var d,c,o;s.parameters={...s.parameters,docs:{...(d=s.parameters)==null?void 0:d.docs,source:{originalSource:`{
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
}`,...(o=(c=s.parameters)==null?void 0:c.docs)==null?void 0:o.source}}};const x=["Default"];export{s as Default,x as __namedExportsOrder,g as default};
