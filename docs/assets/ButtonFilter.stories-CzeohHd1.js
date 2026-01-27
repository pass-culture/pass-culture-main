import{j as i}from"./jsx-runtime-C_uOM0Gm.js";import{V as f}from"./index-vSssAp4U.js";import{c as m}from"./index-TscbDd2H.js";import{f as v}from"./full-down-Cmbtr9nI.js";import{f as b}from"./full-up-D6TPt2ju.js";import{S as h}from"./SvgIcon-CJiY4LCz.js";import"./iframe-CTnXOULQ.js";import"./preload-helper-PPVm8Dsz.js";import"./chunk-EPOLDU6W-u6n6pb5J.js";const t={"button-filter":"_button-filter_p2led_1","button-filter-icon":"_button-filter-icon_p2led_16","button-filter-active":"_button-filter-active_p2led_23","button-filter-open":"_button-filter-open_p2led_37"},o=({className:e,children:s,isOpen:l=!1,isActive:u=!1,type:c="button",testId:d,...p})=>i.jsxs("button",{className:m(t["button-filter"],{[t["button-filter-open"]]:l},{[t["button-filter-active"]]:u},e),type:c,"data-testid":d,...p,children:[s,i.jsx(h,{src:l?b:v,alt:"Ouvert/Fermé",className:t["button-filter-icon"],width:"20"})]});o.displayName="ButtonFilter";try{o.displayName="ButtonFilter",o.__docgenInfo={description:`The Button filter component provides a customizable button element.

---
**Important: Ensure to use descriptive labels for buttons to improve accessibility.**
When using icons only, make sure to provide an accessible label or \`aria-label\`.
---`,displayName:"ButtonFilter",props:{isOpen:{defaultValue:{value:"false"},description:"Whether the button is open.",name:"isOpen",required:!1,type:{name:"boolean"}},isActive:{defaultValue:{value:"false"},description:"Whether the button is active.",name:"isActive",required:!1,type:{name:"boolean"}},icon:{defaultValue:null,description:`The icon to display within the button (or button-link).
If provided, the icon will be displayed as an SVG.`,name:"icon",required:!1,type:{name:"string | null"}},iconAlt:{defaultValue:null,description:`An alternative text for the icon.
If provided and non-empty, the SVG will have a role="img" and an aria-label attribute.
If undefined or empty, the SVG will have an aria-hidden attribute instead, as a
decorative icon.`,name:"iconAlt",required:!1,type:{name:"string"}},variant:{defaultValue:null,description:"",name:"variant",required:!1,type:{name:"enum",value:[{value:'"primary"'},{value:'"secondary"'},{value:'"ternary"'},{value:'"ternary-brand"'},{value:'"quaternary"'},{value:'"box"'}]}},iconPosition:{defaultValue:null,description:"",name:"iconPosition",required:!1,type:{name:"enum",value:[{value:'"right"'},{value:'"left"'},{value:'"center"'}]}},testId:{defaultValue:null,description:"",name:"testId",required:!1,type:{name:"string"}}}}}catch{}const I={title:"@/ui-kit/ButtonFilter",decorators:[f,e=>i.jsx("div",{style:{margin:"50px",display:"flex"},children:i.jsx(e,{})})],argTypes:{isOpen:{control:"boolean",defaultValue:!0},isActive:{control:"boolean",defaultValue:!1},children:{control:"text",defaultValue:"Filter Button"},testId:{control:"text",defaultValue:"button-filter"}},component:o},n={args:{isOpen:!1,isActive:!1,children:"Filter Button"}},a={args:{isOpen:!0,isActive:!1,children:"Open Filter"}},r={args:{isOpen:!1,isActive:!0,children:"Active Filter"}};n.parameters={...n.parameters,docs:{...n.parameters?.docs,source:{originalSource:`{
  args: {
    isOpen: false,
    isActive: false,
    children: 'Filter Button'
  }
}`,...n.parameters?.docs?.source}}};a.parameters={...a.parameters,docs:{...a.parameters?.docs,source:{originalSource:`{
  args: {
    isOpen: true,
    isActive: false,
    children: 'Open Filter'
  }
}`,...a.parameters?.docs?.source}}};r.parameters={...r.parameters,docs:{...r.parameters?.docs,source:{originalSource:`{
  args: {
    isOpen: false,
    isActive: true,
    children: 'Active Filter'
  }
}`,...r.parameters?.docs?.source}}};const q=["DefaultButton","OpenButton","ActiveButton"];export{r as ActiveButton,n as DefaultButton,a as OpenButton,q as __namedExportsOrder,I as default};
