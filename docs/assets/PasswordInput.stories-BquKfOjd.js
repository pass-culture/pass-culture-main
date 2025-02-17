import{j as o}from"./jsx-runtime-CfatFE5O.js";import{c as V}from"./index-DeARc5FM.js";import{R as N,r as j}from"./index-ClcD9ViR.js";import{s as v,a as B}from"./stroke-show-B6taz1DI.js";import{B as S}from"./Button-CSQAIFQX.js";import{B as b}from"./types-DjX_gQD6.js";import{T as k}from"./TextInput-YRVsr3K9.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./stroke-pass-CALgybTM.js";import"./SvgIcon-CUWb-Ez8.js";import"./Tooltip-CPMX2zM9.js";import"./useTooltipProps-C5TDwaI9.js";import"./Button.module-CvOOzViS.js";import"./BaseInput-zpkrYXWy.js";import"./FieldError-DblMbt5C.js";import"./stroke-error-DSZD431a.js";import"./FieldLayoutCharacterCount-DooUcf1c.js";const i={"password-input-wrapper":"_password-input-wrapper_1css3_1","password-input-wrapper-error":"_password-input-wrapper-error_1css3_7"},t=N.forwardRef(({label:n,name:_,description:y,autoComplete:x,error:p,...q},I)=>{const[a,C]=j.useState(!0),R=!!p,D=E=>{E.preventDefault(),C(P=>!P)};return o.jsx("div",{className:V([i["password-input-wrapper"]],{[i["password-input-wrapper-error"]]:R}),children:o.jsx(k,{ref:I,className:i["password-input"],label:n,name:_,description:y,type:a?"password":"text",autoComplete:x,error:p,rightButton:()=>o.jsx(S,{icon:a?v:B,iconAlt:a?"Afficher le mot de passe":"Cacher le mot de passe",onClick:D,variant:b.TERNARY}),...q})})});t.displayName="PasswordInput";try{t.displayName="PasswordInput",t.__docgenInfo={description:"",displayName:"PasswordInput",props:{label:{defaultValue:null,description:"",name:"label",required:!0,type:{name:"string"}},name:{defaultValue:null,description:"",name:"name",required:!0,type:{name:"string"}},description:{defaultValue:null,description:"",name:"description",required:!1,type:{name:"string"}},autoComplete:{defaultValue:null,description:"",name:"autoComplete",required:!1,type:{name:"string"}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}}}}}catch{}const $={title:"ui-kit/formsV2/PasswordInput",component:t},r={args:{name:"password",label:"Mot de passe *"}},e={args:{...r.args,error:"Ce champs est requis"}},s={args:{...r.args,description:"Choisissez un mot de passe fort et difficile à deviner"}};var d,m,c;r.parameters={...r.parameters,docs:{...(d=r.parameters)==null?void 0:d.docs,source:{originalSource:`{
  args: {
    name: 'password',
    label: 'Mot de passe *'
  }
}`,...(c=(m=r.parameters)==null?void 0:m.docs)==null?void 0:c.source}}};var u,l,f;e.parameters={...e.parameters,docs:{...(u=e.parameters)==null?void 0:u.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    error: 'Ce champs est requis'
  }
}`,...(f=(l=e.parameters)==null?void 0:l.docs)==null?void 0:f.source}}};var w,g,h;s.parameters={...s.parameters,docs:{...(w=s.parameters)==null?void 0:w.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    description: 'Choisissez un mot de passe fort et difficile à deviner'
  }
}`,...(h=(g=s.parameters)==null?void 0:g.docs)==null?void 0:h.source}}};const rr=["Default","WithRequiredError","WithDescription"];export{r as Default,s as WithDescription,e as WithRequiredError,rr as __namedExportsOrder,$ as default};
