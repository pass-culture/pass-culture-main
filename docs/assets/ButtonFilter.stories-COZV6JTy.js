import{j as s}from"./jsx-runtime-u17CrQMm.js";import{V as f}from"./index-hpqgBpqt.js";import{c as d}from"./index-CM7mnkw0.js";import{f as m}from"./full-down-Cmbtr9nI.js";import{f as b}from"./full-up-D6TPt2ju.js";import{S as v}from"./SvgIcon-DuZPzNRk.js";import"./iframe-neuy9dc2.js";import"./preload-helper-PPVm8Dsz.js";import"./chunk-JZWAC4HX-Bv2K_H5s.js";const t={"button-filter":"_button-filter_p2led_1","button-filter-icon":"_button-filter-icon_p2led_16","button-filter-active":"_button-filter-active_p2led_23","button-filter-open":"_button-filter-open_p2led_37"},i=({className:e,children:l,isOpen:a=!1,isActive:c=!1,type:u="button",...p})=>s.jsxs("button",{className:d(t["button-filter"],{[t["button-filter-open"]]:a},{[t["button-filter-active"]]:c},e),type:u,...p,children:[l,s.jsx(v,{src:a?b:m,alt:"Ouvert/Fermé",className:t["button-filter-icon"],width:"20"})]});i.displayName="ButtonFilter";try{i.displayName="ButtonFilter",i.__docgenInfo={description:`The Button filter component provides a customizable button element.

---
**Important: Ensure to use descriptive labels for buttons to improve accessibility.**
When using icons only, make sure to provide an accessible label or \`aria-label\`.
---`,displayName:"ButtonFilter",props:{isOpen:{defaultValue:{value:"false"},description:"Whether the button is open.",name:"isOpen",required:!1,type:{name:"boolean"}},isActive:{defaultValue:{value:"false"},description:"Whether the button is active.",name:"isActive",required:!1,type:{name:"boolean"}}}}}catch{}const V={title:"@/ui-kit/ButtonFilter",decorators:[f,e=>s.jsx("div",{style:{margin:"50px",display:"flex"},children:s.jsx(e,{})})],argTypes:{isOpen:{control:"boolean",defaultValue:!0},isActive:{control:"boolean",defaultValue:!1},children:{control:"text",defaultValue:"Filter Button"},testId:{control:"text",defaultValue:"button-filter"}},component:i},r={args:{isOpen:!1,isActive:!1,children:"Filter Button"}},o={args:{isOpen:!0,isActive:!1,children:"Open Filter"}},n={args:{isOpen:!1,isActive:!0,children:"Active Filter"}};r.parameters={...r.parameters,docs:{...r.parameters?.docs,source:{originalSource:`{
  args: {
    isOpen: false,
    isActive: false,
    children: 'Filter Button'
  }
}`,...r.parameters?.docs?.source}}};o.parameters={...o.parameters,docs:{...o.parameters?.docs,source:{originalSource:`{
  args: {
    isOpen: true,
    isActive: false,
    children: 'Open Filter'
  }
}`,...o.parameters?.docs?.source}}};n.parameters={...n.parameters,docs:{...n.parameters?.docs,source:{originalSource:`{
  args: {
    isOpen: false,
    isActive: true,
    children: 'Active Filter'
  }
}`,...n.parameters?.docs?.source}}};const j=["DefaultButton","OpenButton","ActiveButton"];export{n as ActiveButton,r as DefaultButton,o as OpenButton,j as __namedExportsOrder,V as default};
