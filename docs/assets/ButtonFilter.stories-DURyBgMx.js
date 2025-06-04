import{j as i}from"./jsx-runtime-BYYWji4R.js";import{V as B}from"./index-C3rdP_4p.js";import{c as V}from"./index-DeARc5FM.js";import{f as x}from"./full-down-Cmbtr9nI.js";import{f as F}from"./full-up-D6TPt2ju.js";import{S as O}from"./SvgIcon-CyWUmZpn.js";import"./index-ClcD9ViR.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./chunk-NL6KNZEE-BZw6og_i.js";const t={"button-filter":"_button-filter_14qc2_1","button-filter-icon":"_button-filter-icon_14qc2_16","button-filter-active":"_button-filter-active_14qc2_23","button-filter-open":"_button-filter-open_14qc2_37"},o=({className:e,children:h,isOpen:l=!1,isActive:y=!1,type:_="button",testId:g,...A})=>i.jsxs("button",{className:V(t["button-filter"],{[t["button-filter-open"]]:l},{[t["button-filter-active"]]:y},e),type:_,"data-testid":g,...A,children:[h,i.jsx(O,{src:l?F:x,alt:"Ouvert/Fermé",className:t["button-filter-icon"],width:"20"})]});o.displayName="ButtonFilter";try{o.displayName="ButtonFilter",o.__docgenInfo={description:`The Button filter component provides a customizable button element.

---
**Important: Ensure to use descriptive labels for buttons to improve accessibility.**
When using icons only, make sure to provide an accessible label or \`aria-label\`.
---`,displayName:"ButtonFilter",props:{isOpen:{defaultValue:{value:"false"},description:"Whether the button is open.",name:"isOpen",required:!1,type:{name:"boolean"}},isActive:{defaultValue:{value:"false"},description:"Whether the button is active.",name:"isActive",required:!1,type:{name:"boolean"}},icon:{defaultValue:null,description:`The icon to display within the button (or button-link).
If provided, the icon will be displayed as an SVG.`,name:"icon",required:!1,type:{name:"string | null"}},iconAlt:{defaultValue:null,description:`An alternative text for the icon.
If provided and non-empty, the SVG will have a role="img" and an aria-label attribute.
If undefined or empty, the SVG will have an aria-hidden attribute instead, as a
decorative icon.`,name:"iconAlt",required:!1,type:{name:"string"}},variant:{defaultValue:null,description:"",name:"variant",required:!1,type:{name:"enum",value:[{value:'"primary"'},{value:'"secondary"'},{value:'"ternary"'},{value:'"ternary-brand"'},{value:'"quaternary"'},{value:'"box"'}]}},iconPosition:{defaultValue:null,description:"",name:"iconPosition",required:!1,type:{name:"enum",value:[{value:'"right"'},{value:'"left"'},{value:'"center"'}]}},testId:{defaultValue:null,description:"",name:"testId",required:!1,type:{name:"string"}}}}}catch{}const G={title:"ui-kit/ButtonFilter",decorators:[B,e=>i.jsx("div",{style:{margin:"50px",display:"flex"},children:i.jsx(e,{})})],argTypes:{isOpen:{control:"boolean",defaultValue:!0},isActive:{control:"boolean",defaultValue:!1},children:{control:"text",defaultValue:"Filter Button"},testId:{control:"text",defaultValue:"button-filter"}},component:o},n={args:{isOpen:!1,isActive:!1,children:"Filter Button"}},a={args:{isOpen:!0,isActive:!1,children:"Open Filter"}},r={args:{isOpen:!1,isActive:!0,children:"Active Filter"}};var s,u,c;n.parameters={...n.parameters,docs:{...(s=n.parameters)==null?void 0:s.docs,source:{originalSource:`{
  args: {
    isOpen: false,
    isActive: false,
    children: 'Filter Button'
  }
}`,...(c=(u=n.parameters)==null?void 0:u.docs)==null?void 0:c.source}}};var d,p,f;a.parameters={...a.parameters,docs:{...(d=a.parameters)==null?void 0:d.docs,source:{originalSource:`{
  args: {
    isOpen: true,
    isActive: false,
    children: 'Open Filter'
  }
}`,...(f=(p=a.parameters)==null?void 0:p.docs)==null?void 0:f.source}}};var m,v,b;r.parameters={...r.parameters,docs:{...(m=r.parameters)==null?void 0:m.docs,source:{originalSource:`{
  args: {
    isOpen: false,
    isActive: true,
    children: 'Active Filter'
  }
}`,...(b=(v=r.parameters)==null?void 0:v.docs)==null?void 0:b.source}}};const T=["DefaultButton","OpenButton","ActiveButton"];export{r as ActiveButton,n as DefaultButton,a as OpenButton,T as __namedExportsOrder,G as default};
