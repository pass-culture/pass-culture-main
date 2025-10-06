import{j as i}from"./jsx-runtime-CEGThwQL.js";import{c as x}from"./index-C4JHdPXH.js";import{R as I,r as C}from"./iframe-PD1HQGep.js";import{T as b}from"./TextInput-h6lpFtsK.js";import{a as D,s as P}from"./full-show-DR1VeCnl.js";import"./preload-helper-PPVm8Dsz.js";import"./SvgIcon-6AAZ9AcB.js";import"./FieldFooter-dGyr_1ni.js";import"./full-error-BFAmjN4t.js";import"./index.module-CtwNT083.js";import"./FieldHeader-Bk9yRhQ4.js";import"./Tooltip-B3D5cJ5U.js";const p={"password-input-wrapper":"_password-input-wrapper_25hj2_1","password-input-wrapper-error":"_password-input-wrapper-error_25hj2_7"},a=I.forwardRef(({label:o,name:d,description:u,autoComplete:l,error:n,asterisk:c=!0,required:m,...f},w)=>{const[t,g]=C.useState(!0),h=!!n,_=y=>{y.preventDefault(),g(q=>!q)};return i.jsx("div",{className:x([p["password-input-wrapper"]],{[p["password-input-wrapper-error"]]:h}),children:i.jsx(b,{ref:w,label:o,name:d,description:u,type:t?"password":"text",autoComplete:l,error:n,asterisk:c,required:m,iconButton:{icon:t?D:P,label:t?"Afficher le mot de passe":"Cacher le mot de passe",onClick:_},...f})})});a.displayName="PasswordInput";try{a.displayName="PasswordInput",a.__docgenInfo={description:"",displayName:"PasswordInput",props:{label:{defaultValue:null,description:"",name:"label",required:!0,type:{name:"string"}},name:{defaultValue:null,description:"",name:"name",required:!0,type:{name:"string"}},description:{defaultValue:null,description:"",name:"description",required:!1,type:{name:"string"}},autoComplete:{defaultValue:null,description:"",name:"autoComplete",required:!1,type:{name:"string"}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}},asterisk:{defaultValue:{value:"true"},description:"",name:"asterisk",required:!1,type:{name:"boolean"}},required:{defaultValue:null,description:"",name:"required",required:!1,type:{name:"boolean"}}}}}catch{}const M={title:"@/ui-kit/forms/PasswordInput",component:a},e={args:{name:"password",label:"Mot de passe *"}},r={args:{...e.args,error:"Ce champs est requis"}},s={args:{...e.args,description:"Choisissez un mot de passe fort et difficile à deviner"}};e.parameters={...e.parameters,docs:{...e.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'password',
    label: 'Mot de passe *'
  }
}`,...e.parameters?.docs?.source}}};r.parameters={...r.parameters,docs:{...r.parameters?.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    error: 'Ce champs est requis'
  }
}`,...r.parameters?.docs?.source}}};s.parameters={...s.parameters,docs:{...s.parameters?.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    description: 'Choisissez un mot de passe fort et difficile à deviner'
  }
}`,...s.parameters?.docs?.source}}};const A=["Default","WithRequiredError","WithDescription"];export{e as Default,s as WithDescription,r as WithRequiredError,A as __namedExportsOrder,M as default};
