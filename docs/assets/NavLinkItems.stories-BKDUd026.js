import{V as p}from"./index-CYbs_6Vt.js";import{j as e}from"./jsx-runtime-BogwL2Pw.js";import{r as f}from"./iframe-BKFiZcnj.js";import{c as r}from"./index-ArAheYEK.js";import{L as v}from"./chunk-NISHYRIK-Hawuz7KL.js";import"./preload-helper-PPVm8Dsz.js";const s={"menu-list":"_menu-list_1ei89_1","menu-list-item":"_menu-list-item_1ei89_7","is-selected":"_is-selected_1ei89_22","visually-hidden":"_visually-hidden_1ei89_34"},a=({navLabel:n,selectedKey:d,links:c,className:o})=>e.jsx("nav",{"aria-label":n,children:e.jsx("ul",{id:"tablist",className:r(s["menu-list"],o),children:c.map(({key:t,label:m,url:u})=>{const l=d===t;return f.createElement("li",{...l?{id:"selected"}:{},key:t},e.jsx(v,{to:u,className:r(s["menu-list-item"],{[s["is-selected"]]:l}),children:e.jsxs("span",{className:s["menu-list-item-label"],children:[l&&e.jsx("span",{className:s["visually-hidden"],children:"Lien actif"}),m]})}))})})});try{a.displayName="NavLinkItems",a.__docgenInfo={description:"The NavLinkItems component is used to render a list of navigation links.",displayName:"NavLinkItems",props:{navLabel:{defaultValue:null,description:"Navigation accessible name",name:"navLabel",required:!0,type:{name:"string"}},links:{defaultValue:null,description:"An array of links to be rendered.",name:"links",required:!0,type:{name:"NavLinkItem[]"}},selectedKey:{defaultValue:null,description:"The key of the selected link.",name:"selectedKey",required:!1,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}const b={title:"@/ui-kit/NavLinkItems",decorators:[p],component:a},i={args:{selectedKey:"individual",links:[{label:"Offres individuelles",url:"#",key:"individual"},{label:"Offres collectives",url:"#",key:"collective"}]}};i.parameters={...i.parameters,docs:{...i.parameters?.docs,source:{originalSource:`{
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
}`,...i.parameters?.docs?.source}}};const g=["Default"];export{i as Default,g as __namedExportsOrder,b as default};
