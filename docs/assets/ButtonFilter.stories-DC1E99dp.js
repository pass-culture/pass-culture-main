import{i as e}from"./chunk-DseTPa7n.js";import{t}from"./jsx-runtime-BuabnPLX.js";import{t as n}from"./classnames-MYlGWOUq.js";import{t as r}from"./SvgIcon-DK-x56iF.js";import{t as i}from"./dist-BdS2QMCY.js";import{t as a}from"./full-down-BRWJ0t1l.js";import{t as o}from"./full-up-9DeG_flt.js";var s=e(n(),1),c={"button-filter":`_button-filter_p2led_1`,"button-filter-icon":`_button-filter-icon_p2led_16`,"button-filter-active":`_button-filter-active_p2led_23`,"button-filter-open":`_button-filter-open_p2led_37`},l=t(),u=({className:e,children:t,isOpen:n=!1,isActive:i=!1,type:u=`button`,...d})=>(0,l.jsxs)(`button`,{className:(0,s.default)(c[`button-filter`],{[c[`button-filter-open`]]:n},{[c[`button-filter-active`]]:i},e),type:u,...d,children:[t,(0,l.jsx)(r,{src:n?o:a,alt:`Ouvert/Fermé`,className:c[`button-filter-icon`],width:`20`})]});u.displayName=`ButtonFilter`;try{u.displayName=`ButtonFilter`,u.__docgenInfo={description:`The Button filter component provides a customizable button element.

---
**Important: Ensure to use descriptive labels for buttons to improve accessibility.**
When using icons only, make sure to provide an accessible label or \`aria-label\`.
---`,displayName:`ButtonFilter`,props:{isOpen:{defaultValue:{value:`false`},description:`Whether the button is open.`,name:`isOpen`,required:!1,type:{name:`boolean`}},isActive:{defaultValue:{value:`false`},description:`Whether the button is active.`,name:`isActive`,required:!1,type:{name:`boolean`}}}}}catch{}var d={title:`@/ui-kit/ButtonFilter`,decorators:[i,e=>(0,l.jsx)(`div`,{style:{margin:`50px`,display:`flex`},children:(0,l.jsx)(e,{})})],argTypes:{isOpen:{control:`boolean`,defaultValue:!0},isActive:{control:`boolean`,defaultValue:!1},children:{control:`text`,defaultValue:`Filter Button`},testId:{control:`text`,defaultValue:`button-filter`}},component:u},f={args:{isOpen:!1,isActive:!1,children:`Filter Button`}},p={args:{isOpen:!0,isActive:!1,children:`Open Filter`}},m={args:{isOpen:!1,isActive:!0,children:`Active Filter`}};f.parameters={...f.parameters,docs:{...f.parameters?.docs,source:{originalSource:`{
  args: {
    isOpen: false,
    isActive: false,
    children: 'Filter Button'
  }
}`,...f.parameters?.docs?.source}}},p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  args: {
    isOpen: true,
    isActive: false,
    children: 'Open Filter'
  }
}`,...p.parameters?.docs?.source}}},m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  args: {
    isOpen: false,
    isActive: true,
    children: 'Active Filter'
  }
}`,...m.parameters?.docs?.source}}};var h=[`DefaultButton`,`OpenButton`,`ActiveButton`];export{m as ActiveButton,f as DefaultButton,p as OpenButton,h as __namedExportsOrder,d as default};