import{j as c}from"./jsx-runtime-Cf8x2fCZ.js";import{R as w,r as t}from"./index-QQMyt9Ur.js";import{C as F}from"./Checkbox-8jeYcLLy.js";import{T as R}from"./TextInput-C-6M7uLs.js";import"./index-yBjzXJbu.js";import"./_commonjsHelpers-CqkleIqs.js";import"./index-B0pXE9zJ.js";import"./Tag-DpLUbPXr.js";import"./full-thumb-up-Bb4kpRpM.js";import"./SvgIcon-B5V96DYN.js";import"./BaseInput-B8c5gx_3.js";import"./stroke-search-dgesjRZH.js";import"./FieldError-2mFOl_uD.js";import"./stroke-error-DSZD431a.js";import"./FieldLayoutCharacterCount-CCjrqBrG.js";import"./index.module-DTkZ18fI.js";const N={"input-layout-small-label":"_input-layout-small-label_kaqxt_1"},i=w.forwardRef(({className:p,name:d,label:y,max:k,rightIcon:E,disabled:f,smallLabel:I,showFreeCheckbox:b,hideAsterisk:h=!1,error:g,updatePriceValue:x},C)=>{const a=t.useRef(null),_=`${d}.free`,u=t.useRef(null),[l,m]=t.useState(!1);t.useEffect(()=>{const r=document.activeElement===u.current;!l&&r&&a.current?.focus()},[l]),t.useEffect(()=>{u.current&&a.current?.value==="0"&&m(!0)},[]);const q=e=>{x(e.target.value),b&&m(e.target.value==="0")},V=()=>{const e=!l;m(e);let r="";e&&(r="0"),a.current&&(x(r),a.current.value=r)},v=c.jsx(F,{ref:u,label:"Gratuit",checked:l,name:_,onChange:V,disabled:f});return c.jsx("div",{ref:C,children:c.jsx(R,{ref:a,className:p,labelClassName:I?N["input-layout-small-label"]:"",required:!h,name:d,label:y,type:"number",step:"0.01",min:0,max:k,rightIcon:E,disabled:f,asterisk:!h,onChange:q,hasError:!!g,error:g,...b?{InputExtension:v}:{}})})});i.displayName="PriceInput";try{i.displayName="PriceInput",i.__docgenInfo={description:`The PriceInput component is a combination of a TextInput and a Checkbox to define prices.
It integrates with Formik for form state management and is used when an null price is meant to be interpreted as free.

---`,displayName:"PriceInput",props:{className:{defaultValue:null,description:`A custom class for the field layout,
where label, description, input, and footer are displayed.`,name:"className",required:!1,type:{name:"string"}},name:{defaultValue:null,description:"",name:"name",required:!1,type:{name:"string"}},rightIcon:{defaultValue:null,description:"",name:"rightIcon",required:!1,type:{name:"string"}},smallLabel:{defaultValue:null,description:"A flag to display a smaller label.",name:"smallLabel",required:!1,type:{name:"boolean"}},label:{defaultValue:null,description:`A label for the input,
also used as the aria-label for the group.`,name:"label",required:!0,type:{name:"string"}},showFreeCheckbox:{defaultValue:null,description:'A flag to show the "Gratuit" checkbox.',name:"showFreeCheckbox",required:!1,type:{name:"boolean"}},hideAsterisk:{defaultValue:{value:"false"},description:"",name:"hideAsterisk",required:!1,type:{name:"boolean"}},error:{defaultValue:null,description:`A custom error message to be displayed.
If this prop is provided, the error message will be displayed and the field will be marked as errored`,name:"error",required:!1,type:{name:"string"}},updatePriceValue:{defaultValue:null,description:"",name:"updatePriceValue",required:!0,type:{name:"(value: string) => void"}}}}}catch{}const M={title:"@/ui-kit/forms/PriceInput",component:i},n={args:{name:"email",label:"Email"}},s={args:{name:"email",label:"Email",smallLabel:!0}},o={args:{name:"email",label:"Email",showFreeCheckbox:!0}};n.parameters={...n.parameters,docs:{...n.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'email',
    label: 'Email'
  }
}`,...n.parameters?.docs?.source}}};s.parameters={...s.parameters,docs:{...s.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'email',
    label: 'Email',
    smallLabel: true
  }
}`,...s.parameters?.docs?.source}}};o.parameters={...o.parameters,docs:{...o.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'email',
    label: 'Email',
    showFreeCheckbox: true
  }
}`,...o.parameters?.docs?.source}}};const Q=["Default","SmallLabel","WithCheckbox"];export{n as Default,s as SmallLabel,o as WithCheckbox,Q as __namedExportsOrder,M as default};
