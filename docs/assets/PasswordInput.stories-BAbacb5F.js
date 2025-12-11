import{j as i}from"./jsx-runtime-Cem4gMhj.js";import{c as I}from"./index-COB1Bk3q.js";import{R as x,r as v}from"./iframe-DiJafrk9.js";import{T as C}from"./TextInput-wxX4lWuE.js";import{a as b,s as D}from"./full-show-DR1VeCnl.js";import"./preload-helper-PPVm8Dsz.js";import"./SvgIcon-CN_E_sKF.js";import"./FieldFooter-Cmm33Ery.js";import"./full-error-BFAmjN4t.js";import"./index.module-KDWWLmuU.js";import"./FieldHeader-C77zxlAK.js";import"./Tooltip-BFLoC6f6.js";const p={"password-input-wrapper":"_password-input-wrapper_25hj2_1","password-input-wrapper-error":"_password-input-wrapper-error_25hj2_7"},a=x.forwardRef(({label:o,name:d,description:u,autoComplete:l,error:n,requiredIndicator:c,required:m,...f},w)=>{const[t,g]=v.useState(!0),h=!!n,_=q=>{q.preventDefault(),g(y=>!y)};return i.jsx("div",{className:I([p["password-input-wrapper"]],{[p["password-input-wrapper-error"]]:h}),children:i.jsx(C,{ref:w,label:o,name:d,description:u,type:t?"password":"text",autoComplete:l,error:n,requiredIndicator:c,required:m,iconButton:{icon:t?b:D,label:t?"Afficher le mot de passe":"Cacher le mot de passe",onClick:_},...f})})});a.displayName="PasswordInput";try{a.displayName="PasswordInput",a.__docgenInfo={description:"",displayName:"PasswordInput",props:{label:{defaultValue:null,description:"",name:"label",required:!0,type:{name:"string"}},name:{defaultValue:null,description:"",name:"name",required:!0,type:{name:"string"}},description:{defaultValue:null,description:"",name:"description",required:!1,type:{name:"string"}},autoComplete:{defaultValue:null,description:"",name:"autoComplete",required:!1,type:{name:"string"}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}},requiredIndicator:{defaultValue:null,description:"",name:"requiredIndicator",required:!1,type:{name:"enum",value:[{value:'"symbol"'},{value:'"hidden"'},{value:'"explicit"'}]}},required:{defaultValue:null,description:"",name:"required",required:!1,type:{name:"boolean"}}}}}catch{}const M={title:"@/ui-kit/forms/PasswordInput",component:a},e={args:{name:"password",label:"Mot de passe *"}},r={args:{...e.args,error:"Ce champs est requis"}},s={args:{...e.args,description:"Choisissez un mot de passe fort et difficile à deviner"}};e.parameters={...e.parameters,docs:{...e.parameters?.docs,source:{originalSource:`{
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
