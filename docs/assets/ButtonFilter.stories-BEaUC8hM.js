import{j as o}from"./jsx-runtime-BYYWji4R.js";import{V}from"./index-BQRgOAGl.js";import{c as I}from"./index-DeARc5FM.js";import{f as S}from"./full-down-Cmbtr9nI.js";import{f as q}from"./full-up-D6TPt2ju.js";import{S as D}from"./SvgIcon-CyWUmZpn.js";import"./index-ClcD9ViR.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./index-DOYoWpww.js";import"./index-J01lmiDr.js";const t={"button-filter":"_button-filter_1e3ux_1","button-filter-icon":"_button-filter-icon_1e3ux_16","button-filter-active":"_button-filter-active_1e3ux_23","button-filter-open":"_button-filter-open_1e3ux_37"},l=({className:e,children:x,isOpen:s=!1,isActive:A=!1,type:B="button",testId:F,...O})=>o.jsxs("button",{className:I(t["button-filter"],{[t["button-filter-open"]]:s},{[t["button-filter-active"]]:A},e),type:B,"data-testid":F,...O,children:[x,o.jsx(D,{src:s?q:S,alt:"Ouvert/Fermé",className:t["button-filter-icon"],width:"20"})]});l.displayName="ButtonFilter";try{l.displayName="ButtonFilter",l.__docgenInfo={description:`The Button filter component provides a customizable button element.

---
**Important: Ensure to use descriptive labels for buttons to improve accessibility.**
When using icons only, make sure to provide an accessible label or \`aria-label\`.
---`,displayName:"ButtonFilter",props:{isOpen:{defaultValue:{value:"false"},description:"Whether the button is open.",name:"isOpen",required:!1,type:{name:"boolean"}},isActive:{defaultValue:{value:"false"},description:"Whether the button is active.",name:"isActive",required:!1,type:{name:"boolean"}},icon:{defaultValue:null,description:`The icon to display within the button (or button-link).
If provided, the icon will be displayed as an SVG.`,name:"icon",required:!1,type:{name:"string | null"}},iconAlt:{defaultValue:null,description:`An alternative text for the icon.
If provided and non-empty, the SVG will have a role="img" and an aria-label attribute.
If undefined or empty, the SVG will have an aria-hidden attribute instead, as a
decorative icon.`,name:"iconAlt",required:!1,type:{name:"string"}},variant:{defaultValue:null,description:"",name:"variant",required:!1,type:{name:"enum",value:[{value:'"primary"'},{value:'"secondary"'},{value:'"ternary"'},{value:'"ternary-brand"'},{value:'"quaternary"'},{value:'"box"'}]}},iconPosition:{defaultValue:null,description:"",name:"iconPosition",required:!1,type:{name:"enum",value:[{value:'"right"'},{value:'"left"'},{value:'"center"'}]}},testId:{defaultValue:null,description:"",name:"testId",required:!1,type:{name:"string"}}}}}catch{}const R={title:"ui-kit/ButtonFilter",decorators:[V,e=>o.jsx("div",{style:{margin:"50px",display:"flex"},children:o.jsx(e,{})})],argTypes:{isOpen:{control:"boolean",defaultValue:!0},isActive:{control:"boolean",defaultValue:!1},children:{control:"text",defaultValue:"Filter Button"},testId:{control:"text",defaultValue:"button-filter"}},component:l},n={args:{isOpen:!1,isActive:!1,children:"Filter Button"}},a={args:{isOpen:!0,isActive:!1,children:"Open Filter"}},r={args:{isOpen:!1,isActive:!0,children:"Active Filter"}},i={args:{isOpen:!1,isActive:!1,disabled:!0,children:"Disabled Filter"}};var u,c,d;n.parameters={...n.parameters,docs:{...(u=n.parameters)==null?void 0:u.docs,source:{originalSource:`{
  args: {
    isOpen: false,
    isActive: false,
    children: 'Filter Button'
  }
}`,...(d=(c=n.parameters)==null?void 0:c.docs)==null?void 0:d.source}}};var p,f,m;a.parameters={...a.parameters,docs:{...(p=a.parameters)==null?void 0:p.docs,source:{originalSource:`{
  args: {
    isOpen: true,
    isActive: false,
    children: 'Open Filter'
  }
}`,...(m=(f=a.parameters)==null?void 0:f.docs)==null?void 0:m.source}}};var v,b,h;r.parameters={...r.parameters,docs:{...(v=r.parameters)==null?void 0:v.docs,source:{originalSource:`{
  args: {
    isOpen: false,
    isActive: true,
    children: 'Active Filter'
  }
}`,...(h=(b=r.parameters)==null?void 0:b.docs)==null?void 0:h.source}}};var y,g,_;i.parameters={...i.parameters,docs:{...(y=i.parameters)==null?void 0:y.docs,source:{originalSource:`{
  args: {
    isOpen: false,
    isActive: false,
    disabled: true,
    children: 'Disabled Filter'
  }
}`,...(_=(g=i.parameters)==null?void 0:g.docs)==null?void 0:_.source}}};const U=["DefaultButton","OpenButton","ActiveButton","DisabledButton"];export{r as ActiveButton,n as DefaultButton,i as DisabledButton,a as OpenButton,U as __namedExportsOrder,R as default};
