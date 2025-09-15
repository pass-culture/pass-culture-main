import{j as c}from"./jsx-runtime-Cf8x2fCZ.js";import{c as d}from"./index-B0pXE9zJ.js";import{r as s}from"./index-QQMyt9Ur.js";import"./index-yBjzXJbu.js";import"./_commonjsHelpers-CqkleIqs.js";const p="_toggle_1xt79_1",u={toggle:p,"toggle-display":"_toggle-display_1xt79_18"},l=({isActiveByDefault:e=!1,isDisabled:g=!1,label:i,labelPosition:o="left",handleClick:n})=>{const[a,r]=s.useState(e);s.useEffect(()=>{r(e)},[e]);const f=s.useCallback(()=>{r(!a),n?.()},[a,n]);return c.jsxs("button",{className:d(u.toggle),type:"button",disabled:g,"aria-pressed":a,onClick:f,children:[o==="left"?i:null,c.jsx("span",{className:d(u["toggle-display"]),hidden:!0}),o==="right"?i:null]})};try{l.displayName="Toggle",l.__docgenInfo={description:`The Toggle component is used to render a button that represents an on/off state.
It allows users to control a setting between two states (active/inactive).

---
**Important: Use \`isActiveByDefault\` to initialize the state and \`handleClick\` to handle changes in the toggle state.**
---`,displayName:"Toggle",props:{isActiveByDefault:{defaultValue:{value:"false"},description:"Indicates if the toggle is active by default.",name:"isActiveByDefault",required:!1,type:{name:"boolean"}},isDisabled:{defaultValue:{value:"false"},description:"Indicates if the toggle is disabled.",name:"isDisabled",required:!1,type:{name:"boolean"}},label:{defaultValue:null,description:"The label text for the toggle.",name:"label",required:!0,type:{name:"string"}},labelPosition:{defaultValue:{value:"left"},description:"",name:"labelPosition",required:!1,type:{name:"enum",value:[{value:'"left"'},{value:'"right"'}]}},handleClick:{defaultValue:null,description:"Callback function triggered when the toggle is clicked.",name:"handleClick",required:!1,type:{name:"(() => void)"}}}}}catch{}const v={title:"@/ui-kit/forms/Toggle",component:l},t={args:{isActiveByDefault:!1,isDisabled:!1}};t.parameters={...t.parameters,docs:{...t.parameters?.docs,source:{originalSource:`{
  args: {
    isActiveByDefault: false,
    isDisabled: false
  }
}`,...t.parameters?.docs?.source}}};const x=["Default"];export{t as Default,x as __namedExportsOrder,v as default};
