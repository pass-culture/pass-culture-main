import{V as u}from"./index-C-zIjT2c.js";import{j as e}from"./jsx-runtime-Cf8x2fCZ.js";import{c as r}from"./index-B0pXE9zJ.js";import{L as p}from"./chunk-S5YDGZLY-CNwzCxw0.js";import"./index-QQMyt9Ur.js";import"./_commonjsHelpers-CqkleIqs.js";import"./index-yBjzXJbu.js";const i={"menu-list":"_menu-list_1ei89_1","menu-list-item":"_menu-list-item_1ei89_7","is-selected":"_is-selected_1ei89_22","visually-hidden":"_visually-hidden_1ei89_34"},n=({navLabel:a,selectedKey:t,links:d,className:c})=>e.jsx("nav",{"aria-label":a,children:e.jsx("ul",{className:r(i["menu-list"],c),children:d.map(({key:l,label:o,url:m})=>e.jsx("li",{children:e.jsx(p,{to:m,className:r(i["menu-list-item"],{[i["is-selected"]]:t===l}),children:e.jsxs("span",{className:i["menu-list-item-label"],children:[t===l&&e.jsx("span",{className:i["visually-hidden"],children:"Lien actif"}),o]})})},l))})});try{n.displayName="NavLinkItems",n.__docgenInfo={description:"The NavLinkItems component is used to render a list of navigation links.",displayName:"NavLinkItems",props:{navLabel:{defaultValue:null,description:"Navigation accessible name",name:"navLabel",required:!0,type:{name:"string"}},links:{defaultValue:null,description:"An array of links to be rendered.",name:"links",required:!0,type:{name:"NavLinkItem[]"}},selectedKey:{defaultValue:null,description:"The key of the selected link.",name:"selectedKey",required:!1,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}const L={title:"@/ui-kit/NavLinkItems",decorators:[u],component:n},s={args:{selectedKey:"individual",links:[{label:"Offres individuelles",url:"#",key:"individual"},{label:"Offres collectives",url:"#",key:"collective"}]}};s.parameters={...s.parameters,docs:{...s.parameters?.docs,source:{originalSource:`{
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
}`,...s.parameters?.docs?.source}}};const b=["Default"];export{s as Default,b as __namedExportsOrder,L as default};
