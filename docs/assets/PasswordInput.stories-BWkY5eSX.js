import{j as r}from"./jsx-runtime-C_uOM0Gm.js";import{c as q}from"./index-TscbDd2H.js";import{r as c,R as U}from"./iframe-CTnXOULQ.js";import{T as F}from"./TextInput-DOsfrCQI.js";import{s as k,a as z}from"./full-show-BUp4jmvL.js";import{l as G}from"./index.module-DEHgy3-r.js";import{f as Y}from"./full-clear-Q4kCtSRL.js";import{f as Z}from"./full-validate-CbMNulkZ.js";import{S as M}from"./SvgIcon-CJiY4LCz.js";import"./preload-helper-PPVm8Dsz.js";import"./FieldFooter-CL0tzobd.js";import"./full-error-BFAmjN4t.js";import"./FieldHeader-DxZ9joXq.js";import"./Tooltip-GJ5PEk5n.js";const R={"password-input-wrapper":"_password-input-wrapper_25hj2_1","password-input-wrapper-error":"_password-input-wrapper-error_25hj2_7"},J="_message_rcuut_1",i={message:J,"message-error":"_message-error_rcuut_17","message-success":"_message-success_rcuut_21","message-pristine":"_message-pristine_rcuut_25"},S=({isPristine:e,isOnError:a,message:s})=>e?r.jsx(X,{message:s}):a?r.jsx(Q,{message:s}):r.jsx(K,{message:s}),K=({message:e})=>r.jsxs("div",{className:q(i.message,i["message-success"]),"data-testid":`success-${e}`,children:[r.jsx(M,{src:Z,alt:"",width:"16"}),r.jsx("span",{className:i["message-success-text"],children:e})]}),Q=({message:e})=>r.jsxs("div",{className:q(i.message,i["message-error"]),"data-testid":`error-${e}`,children:[r.jsx(M,{src:Y,alt:"",width:"16"}),r.jsx("span",{className:i["message-error-text"],children:e})]}),X=({message:e})=>r.jsx("div",{className:q(i.message,i["message-pristine"]),children:r.jsx("span",{className:i["message-error-text"],children:e})});try{S.displayName="MessageDispatcher",S.__docgenInfo={description:"",displayName:"MessageDispatcher",props:{isPristine:{defaultValue:null,description:"",name:"isPristine",required:!0,type:{name:"boolean"}},isOnError:{defaultValue:null,description:"",name:"isOnError",required:!0,type:{name:"boolean"}},message:{defaultValue:null,description:"",name:"message",required:!0,type:{name:"string"}}}}}catch{}const ee=e=>{if(!e||e.length<12)return!1;const a=/[A-Z]/.test(e),s=/[a-z]/.test(e),n=/\d/.test(e),l=/[!"#$%&'()*+,-./:;<=>?@[\\^_`{|}~\]]/.test(e);return!!(a&&s&&n&&l)},V=e=>{switch(e){case"LENGTH":return"12 caractères";case"UPPER_CASE":return"1 majuscule";case"LOWER_CASE":return"1 minuscule";case"NUMBER":return"1 chiffre";case"SYMBOLE":return"1 caractère spécial";default:return""}},re=e=>{const a={};a.LENGTH=e.length<12;const s=/[A-Z]/.test(e);a.UPPER_CASE=!s;const n=/[a-z]/.test(e);a.LOWER_CASE=!n;const l=/\d/.test(e);a.NUMBER=!l;const o=/[!"#$%&'()*+,-./:;<=>?@[\\^_`{|}~\]]/.test(e);return a.SYMBOLE=!o,a},w={"validation-message-list":"_validation-message-list_1hht7_1","sr-only":"_sr-only_1hht7_5"},N=({passwordValue:e,fieldName:a})=>{const[s,n]=c.useState({}),[l]=G(e,2e3);c.useEffect(()=>{n(re(e))},[e]);const o=!l,x=Object.keys(s).map(t=>{const u=V(t);return`${s[t]?"Il manque : ":"Il y a bien : "} ${u}`}).join(". "),I=Object.keys(s).map(t=>`${V(t)}`).join(" ");return r.jsxs("div",{id:a,children:[o&&r.jsxs("div",{className:w["sr-only"],children:["Le mot de passe doit comporter : ",I]}),r.jsx("div",{className:w["sr-only"],"aria-live":"polite","aria-atomic":"true",children:!o&&`Mises à jour des critères : ${x}`}),r.jsx("ul",{className:w["validation-message-list"],"aria-hidden":!0,children:Object.keys(s).map(t=>r.jsx("li",{children:r.jsx(S,{isPristine:o,isOnError:s[t],message:V(t)})},t))})]})};try{N.displayName="ValidationMessageList",N.__docgenInfo={description:"",displayName:"ValidationMessageList",props:{passwordValue:{defaultValue:null,description:"",name:"passwordValue",required:!0,type:{name:"string"}},fieldName:{defaultValue:null,description:"",name:"fieldName",required:!0,type:{name:"string"}}}}}catch{}const d=U.forwardRef(({value:e,label:a,name:s,description:n,autoComplete:l,error:o,requiredIndicator:x,required:I,disabled:t,displayValidation:u,onBlur:v,...L},D)=>{const C=c.useId(),[j,H]=c.useState(!0),[T,O]=c.useState(!1),P=!!o||T&&u&&!ee(e),$=E=>{E.preventDefault(),H(W=>!W)},B=E=>{O(!0),v&&v(E)},A=j?k:z;return r.jsxs(r.Fragment,{children:[r.jsx("div",{className:q([R["password-input-wrapper"]],{[R["password-input-wrapper-error"]]:P}),children:r.jsx(F,{ref:D,label:a,name:s,description:n,type:j||t?"password":"text",autoComplete:l,error:P?o||"Veuillez respecter les conditions requises":void 0,requiredIndicator:x,required:I,iconButton:{icon:t?"":A,label:j?"Afficher le mot de passe":"Cacher le mot de passe",onClick:$},disabled:t,describedBy:C,onBlur:B,...L})}),u&&r.jsx(N,{passwordValue:e,fieldName:C})]})});d.displayName="PasswordInput";try{d.displayName="PasswordInput",d.__docgenInfo={description:"",displayName:"PasswordInput",props:{label:{defaultValue:null,description:"",name:"label",required:!0,type:{name:"string"}},name:{defaultValue:null,description:"",name:"name",required:!0,type:{name:"string"}},description:{defaultValue:null,description:"",name:"description",required:!1,type:{name:"string"}},autoComplete:{defaultValue:null,description:"",name:"autoComplete",required:!1,type:{name:"string"}},value:{defaultValue:null,description:"",name:"value",required:!0,type:{name:"string"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!0,type:{name:"ChangeEventHandler<HTMLInputElement>"}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}},requiredIndicator:{defaultValue:null,description:"",name:"requiredIndicator",required:!1,type:{name:"enum",value:[{value:'"symbol"'},{value:'"hidden"'},{value:'"explicit"'}]}},required:{defaultValue:null,description:"",name:"required",required:!1,type:{name:"boolean"}},disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},displayValidation:{defaultValue:null,description:"",name:"displayValidation",required:!1,type:{name:"boolean"}}}}}catch{}const he={title:"@/design-system/PasswordInput",component:d},p={args:{label:"Default",value:","}},m={render:e=>{const[a,s]=c.useState("");return r.jsx(d,{...e,value:a,onChange:n=>s(n.target.value)})},args:{label:"Mot de passe interactif",name:"password",displayValidation:!0}},g={args:{label:"Label",description:"description"}},f={args:{label:"Disabled",disabled:!0,value:"coucou",onChange:()=>{}}},h={args:{label:"Disabled",error:"This is an error message"}},y={args:{label:"Required",required:!0,requiredIndicator:"symbol"}},_={args:{label:"Required",required:!0,requiredIndicator:"explicit"}},b={args:{label:"With everything",description:"Format: test@test.co",error:"This is an error message",required:!0,requiredIndicator:"explicit",displayValidation:!0}};p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Default',
    value: ','
  }
}`,...p.parameters?.docs?.source}}};m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  render: args => {
    const [value, setValue] = useState('');
    return <PasswordInput {...args} value={value} onChange={(e: ChangeEvent<HTMLInputElement>) => setValue(e.target.value)} />;
  },
  args: {
    label: 'Mot de passe interactif',
    name: 'password',
    displayValidation: true
  }
}`,...m.parameters?.docs?.source}}};g.parameters={...g.parameters,docs:{...g.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Label',
    description: 'description'
  }
}`,...g.parameters?.docs?.source}}};f.parameters={...f.parameters,docs:{...f.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Disabled',
    disabled: true,
    value: 'coucou',
    onChange: () => {}
  }
}`,...f.parameters?.docs?.source}}};h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Disabled',
    error: 'This is an error message'
  }
}`,...h.parameters?.docs?.source}}};y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Required',
    required: true,
    requiredIndicator: 'symbol'
  }
}`,...y.parameters?.docs?.source}}};_.parameters={..._.parameters,docs:{..._.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Required',
    required: true,
    requiredIndicator: 'explicit'
  }
}`,..._.parameters?.docs?.source}}};b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'With everything',
    description: 'Format: test@test.co',
    error: 'This is an error message',
    required: true,
    requiredIndicator: 'explicit',
    displayValidation: true
  }
}`,...b.parameters?.docs?.source}}};const ye=["Default","Interactive","HasDescription","IsDisabled","HasError","IsRequiredSymbol","IsRequiredExplicit","WithEverything"];export{p as Default,g as HasDescription,h as HasError,m as Interactive,f as IsDisabled,_ as IsRequiredExplicit,y as IsRequiredSymbol,b as WithEverything,ye as __namedExportsOrder,he as default};
