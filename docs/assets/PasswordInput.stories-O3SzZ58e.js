import{i as e}from"./chunk-DseTPa7n.js";import{r as t}from"./iframe-zMGudiS2.js";import{t as n}from"./jsx-runtime-BuabnPLX.js";import{t as r}from"./classnames-MYlGWOUq.js";import{t as i}from"./SvgIcon-DK-x56iF.js";import{t as a}from"./full-validate-tbjPXq7-.js";import{n as o}from"./index.module-Cgg_Hfqk.js";import{t as s}from"./TextInput-Dy9_9upv.js";import{t as c}from"./full-clear-QmSxd4ht.js";import{n as l,t as u}from"./full-show-C6y_VETP.js";var d=e(t(),1),f=e(r(),1),p={"password-input-wrapper":`_password-input-wrapper_25hj2_1`,"password-input-wrapper-error":`_password-input-wrapper-error_25hj2_7`},m={message:`_message_1t1al_1`,"message-icon":`_message-icon_1t1al_9`,"message-error":`_message-error_1t1al_15`,"message-success":`_message-success_1t1al_19`,"message-pristine":`_message-pristine_1t1al_23`},h=n(),g=({isPristine:e,isOnError:t,message:n})=>e?(0,h.jsx)(y,{message:n}):t?(0,h.jsx)(v,{message:n}):(0,h.jsx)(_,{message:n}),_=({message:e})=>(0,h.jsxs)(`div`,{className:(0,f.default)(m.message,m[`message-success`]),"data-testid":`success-${e}`,children:[(0,h.jsx)(i,{src:a,alt:``,className:m[`message-icon`]}),(0,h.jsx)(`span`,{children:e})]}),v=({message:e})=>(0,h.jsxs)(`div`,{className:(0,f.default)(m.message,m[`message-error`]),"data-testid":`error-${e}`,children:[(0,h.jsx)(i,{src:c,alt:``,className:m[`message-icon`]}),(0,h.jsx)(`span`,{children:e})]}),y=({message:e})=>(0,h.jsx)(`div`,{className:(0,f.default)(m.message,m[`message-pristine`]),children:(0,h.jsx)(`span`,{children:e})});try{g.displayName=`MessageDispatcher`,g.__docgenInfo={description:``,displayName:`MessageDispatcher`,props:{isPristine:{defaultValue:null,description:``,name:`isPristine`,required:!0,type:{name:`boolean`}},isOnError:{defaultValue:null,description:``,name:`isOnError`,required:!0,type:{name:`boolean`}},message:{defaultValue:null,description:``,name:`message`,required:!0,type:{name:`string`}}}}}catch{}var b=e=>{if(!e||e.length<12)return!1;let t=/[A-Z]/.test(e),n=/[a-z]/.test(e),r=/\d/.test(e),i=/[!"#$%&'()*+,-./:;<=>?@[\\^_`{|}~\]]/.test(e);return!!(t&&n&&r&&i)},x=function(e){return e.LENGTH=`LENGTH`,e.UPPER_CASE=`UPPER_CASE`,e.LOWER_CASE=`LOWER_CASE`,e.NUMBER=`NUMBER`,e.SYMBOLE=`SYMBOLE`,e}({}),S=e=>{switch(e){case x.LENGTH:return`12 caractères`;case x.UPPER_CASE:return`1 majuscule`;case x.LOWER_CASE:return`1 minuscule`;case x.NUMBER:return`1 chiffre`;case x.SYMBOLE:return`1 caractère spécial`;default:return``}},C=e=>{let t={};t[x.LENGTH]=e.length<12;let n=/[A-Z]/.test(e);t[x.UPPER_CASE]=!n;let r=/[a-z]/.test(e);t[x.LOWER_CASE]=!r;let i=/\d/.test(e);t[x.NUMBER]=!i;let a=/[!"#$%&'()*+,-./:;<=>?@[\\^_`{|}~\]]/.test(e);return t[x.SYMBOLE]=!a,t},w={"validation-message-list":`_validation-message-list_1hht7_1`,"sr-only":`_sr-only_1hht7_5`},T=({passwordValue:e,fieldName:t})=>{let[n,r]=(0,d.useState)({}),[i]=o(e,2e3);(0,d.useEffect)(()=>{r(C(e))},[e]);let a=!i,s=Object.keys(n).map(e=>{let t=S(e);return`${n[e]?`Il manque : `:`Il y a bien : `} ${t}`}).join(`. `),c=Object.keys(n).map(e=>`${S(e)}`).join(` `);return(0,h.jsxs)(`div`,{id:t,children:[a&&(0,h.jsxs)(`div`,{className:w[`sr-only`],children:[`Le mot de passe doit comporter : `,c]}),(0,h.jsx)(`div`,{className:w[`sr-only`],"aria-live":`polite`,"aria-atomic":`true`,children:!a&&`Mises à jour des critères : ${s}`}),(0,h.jsx)(`ul`,{className:w[`validation-message-list`],"aria-hidden":!0,children:Object.keys(n).map(e=>(0,h.jsx)(`li`,{children:(0,h.jsx)(g,{isPristine:a,isOnError:n[e],message:S(e)})},e))})]})};try{T.displayName=`ValidationMessageList`,T.__docgenInfo={description:``,displayName:`ValidationMessageList`,props:{passwordValue:{defaultValue:null,description:``,name:`passwordValue`,required:!0,type:{name:`string`}},fieldName:{defaultValue:null,description:``,name:`fieldName`,required:!0,type:{name:`string`}}}}}catch{}var E=d.forwardRef(({value:e,label:t,name:n,description:r,autoComplete:i,error:a,requiredIndicator:o,required:c,disabled:m,displayValidation:g,onBlur:_,...v},y)=>{let x=(0,d.useId)(),[S,C]=(0,d.useState)(!0),[w,E]=(0,d.useState)(!1),D=!!a||w&&g&&!b(e),O=e=>{e.preventDefault(),C(e=>!e)},k=e=>{E(!0),_&&_(e)},A=S?l:u;return(0,h.jsxs)(h.Fragment,{children:[(0,h.jsx)(`div`,{className:(0,f.default)([p[`password-input-wrapper`]],{[p[`password-input-wrapper-error`]]:D}),children:(0,h.jsx)(s,{ref:y,label:t,name:n,description:r,type:S||m?`password`:`text`,autoComplete:i,error:D?a||`Veuillez respecter les conditions requises`:void 0,requiredIndicator:o,required:c,iconButton:{icon:m?``:A,label:S?`Afficher le mot de passe`:`Cacher le mot de passe`,onClick:O},disabled:m,describedBy:x,onBlur:k,...v})}),g&&(0,h.jsx)(T,{passwordValue:e,fieldName:x})]})});E.displayName=`PasswordInput`;try{E.displayName=`PasswordInput`,E.__docgenInfo={description:``,displayName:`PasswordInput`,props:{label:{defaultValue:null,description:``,name:`label`,required:!0,type:{name:`string`}},name:{defaultValue:null,description:``,name:`name`,required:!0,type:{name:`string`}},description:{defaultValue:null,description:``,name:`description`,required:!1,type:{name:`string`}},autoComplete:{defaultValue:null,description:``,name:`autoComplete`,required:!1,type:{name:`string`}},value:{defaultValue:null,description:``,name:`value`,required:!0,type:{name:`string`}},onChange:{defaultValue:null,description:``,name:`onChange`,required:!0,type:{name:`ChangeEventHandler<HTMLInputElement>`}},error:{defaultValue:null,description:``,name:`error`,required:!1,type:{name:`string`}},requiredIndicator:{defaultValue:null,description:``,name:`requiredIndicator`,required:!1,type:{name:`enum`,value:[{value:`"symbol"`},{value:`"hidden"`},{value:`"explicit"`}]}},required:{defaultValue:null,description:``,name:`required`,required:!1,type:{name:`boolean`}},disabled:{defaultValue:null,description:``,name:`disabled`,required:!1,type:{name:`boolean`}},displayValidation:{defaultValue:null,description:``,name:`displayValidation`,required:!1,type:{name:`boolean`}}}}}catch{}var D={title:`@/design-system/PasswordInput`,component:E},O={args:{label:`Default`,value:`,`}},k={render:e=>{let[t,n]=(0,d.useState)(``);return(0,h.jsx)(E,{...e,value:t,onChange:e=>n(e.target.value)})},args:{label:`Mot de passe interactif`,name:`password`,displayValidation:!0}},A={args:{label:`Label`,description:`description`}},j={args:{label:`Disabled`,disabled:!0,value:`coucou`,onChange:()=>{}}},M={args:{label:`Disabled`,error:`This is an error message`}},N={args:{label:`Required`,required:!0,requiredIndicator:`symbol`}},P={args:{label:`Required`,required:!0,requiredIndicator:`explicit`}},F={args:{label:`With everything`,description:`Format: test@test.co`,error:`This is an error message`,required:!0,requiredIndicator:`explicit`,displayValidation:!0}};O.parameters={...O.parameters,docs:{...O.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Default',
    value: ','
  }
}`,...O.parameters?.docs?.source}}},k.parameters={...k.parameters,docs:{...k.parameters?.docs,source:{originalSource:`{
  render: args => {
    const [value, setValue] = useState('');
    return <PasswordInput {...args} value={value} onChange={(e: ChangeEvent<HTMLInputElement>) => setValue(e.target.value)} />;
  },
  args: {
    label: 'Mot de passe interactif',
    name: 'password',
    displayValidation: true
  }
}`,...k.parameters?.docs?.source}}},A.parameters={...A.parameters,docs:{...A.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Label',
    description: 'description'
  }
}`,...A.parameters?.docs?.source}}},j.parameters={...j.parameters,docs:{...j.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Disabled',
    disabled: true,
    value: 'coucou',
    onChange: () => {}
  }
}`,...j.parameters?.docs?.source}}},M.parameters={...M.parameters,docs:{...M.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Disabled',
    error: 'This is an error message'
  }
}`,...M.parameters?.docs?.source}}},N.parameters={...N.parameters,docs:{...N.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Required',
    required: true,
    requiredIndicator: 'symbol'
  }
}`,...N.parameters?.docs?.source}}},P.parameters={...P.parameters,docs:{...P.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Required',
    required: true,
    requiredIndicator: 'explicit'
  }
}`,...P.parameters?.docs?.source}}},F.parameters={...F.parameters,docs:{...F.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'With everything',
    description: 'Format: test@test.co',
    error: 'This is an error message',
    required: true,
    requiredIndicator: 'explicit',
    displayValidation: true
  }
}`,...F.parameters?.docs?.source}}};var I=[`Default`,`Interactive`,`HasDescription`,`IsDisabled`,`HasError`,`IsRequiredSymbol`,`IsRequiredExplicit`,`WithEverything`];export{O as Default,A as HasDescription,M as HasError,k as Interactive,j as IsDisabled,P as IsRequiredExplicit,N as IsRequiredSymbol,F as WithEverything,I as __namedExportsOrder,D as default};