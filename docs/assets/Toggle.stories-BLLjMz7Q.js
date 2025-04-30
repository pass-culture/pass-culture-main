import{j as n}from"./jsx-runtime-BYYWji4R.js";import{c as r}from"./index-DeARc5FM.js";import{r as l}from"./index-ClcD9ViR.js";import"./_commonjsHelpers-Cpj98o6Y.js";const b="_toggle_1o6et_1",c={toggle:b,"toggle-display":"_toggle-display_1o6et_22"},o=({isActiveByDefault:e=!1,isDisabled:p=!1,label:f="Label",handleClick:t})=>{const[s,i]=l.useState(e);l.useEffect(()=>{i(e)},[e]);const m=l.useCallback(()=>{i(!s),t==null||t()},[s,t]);return n.jsxs("button",{className:r(c.toggle),type:"button",disabled:p,"aria-pressed":s,onClick:m,children:[f,n.jsx("span",{className:r(c["toggle-display"]),hidden:!0})]})};try{o.displayName="Toggle",o.__docgenInfo={description:`The Toggle component is used to render a button that represents an on/off state.
It allows users to control a setting between two states (active/inactive).

---
**Important: Use \`isActiveByDefault\` to initialize the state and \`handleClick\` to handle changes in the toggle state.**
---`,displayName:"Toggle",props:{isActiveByDefault:{defaultValue:{value:"false"},description:"Indicates if the toggle is active by default.",name:"isActiveByDefault",required:!1,type:{name:"boolean"}},isDisabled:{defaultValue:{value:"false"},description:"Indicates if the toggle is disabled.",name:"isDisabled",required:!1,type:{name:"boolean"}},label:{defaultValue:{value:"Label"},description:"The label text for the toggle.",name:"label",required:!1,type:{name:"string"}},handleClick:{defaultValue:null,description:"Callback function triggered when the toggle is clicked.",name:"handleClick",required:!1,type:{name:"(() => void)"}}}}}catch{}const D={title:"ui-kit/Toggle",component:o},a={args:{isActiveByDefault:!1,isDisabled:!1}};var d,g,u;a.parameters={...a.parameters,docs:{...(d=a.parameters)==null?void 0:d.docs,source:{originalSource:`{
  args: {
    isActiveByDefault: false,
    isDisabled: false
  }
}`,...(u=(g=a.parameters)==null?void 0:g.docs)==null?void 0:u.source}}};const x=["Default"];export{a as Default,x as __namedExportsOrder,D as default};
