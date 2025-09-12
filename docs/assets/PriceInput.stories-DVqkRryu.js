import{j as c}from"./jsx-runtime-DF2Pcvd1.js";import{R as D,r as t}from"./index-B2-qRKKC.js";import{C as G}from"./Checkbox-CrDZoBy5.js";import{T as W}from"./TextInput-Drf4ZuYE.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./index-DeARc5FM.js";import"./Tag-BDZYioa0.js";import"./full-thumb-up-Bb4kpRpM.js";import"./SvgIcon-DfLnDDE5.js";import"./BaseInput-JKfrEs2s.js";import"./stroke-search-dgesjRZH.js";import"./FieldError-B3RhE53I.js";import"./stroke-error-DSZD431a.js";import"./FieldLayoutCharacterCount-Ba0T0OOt.js";import"./index.module-BDmDBTbR.js";const O={"input-layout-small-label":"_input-layout-small-label_kaqxt_1"},i=D.forwardRef(({className:p,name:d,label:F,max:R,rightIcon:N,disabled:f,smallLabel:P,showFreeCheckbox:b,hideAsterisk:h=!1,error:g,updatePriceValue:x},S)=>{const a=t.useRef(null),A=`${d}.free`,u=t.useRef(null),[l,m]=t.useState(!1);t.useEffect(()=>{var y;const r=document.activeElement===u.current;!l&&r&&((y=a.current)==null||y.focus())},[l]),t.useEffect(()=>{var e;u.current&&((e=a.current)==null?void 0:e.value)==="0"&&m(!0)},[]);const L=e=>{x(e.target.value),b&&m(e.target.value==="0")},j=()=>{const e=!l;m(e);let r="";e&&(r="0"),a.current&&(x(r),a.current.value=r)},T=c.jsx(G,{ref:u,label:"Gratuit",checked:l,name:A,onChange:j,disabled:f});return c.jsx("div",{ref:S,children:c.jsx(W,{ref:a,className:p,labelClassName:P?O["input-layout-small-label"]:"",required:!h,name:d,label:F,type:"number",step:"0.01",min:0,max:R,rightIcon:N,disabled:f,asterisk:!h,onChange:L,hasError:!!g,error:g,...b?{InputExtension:T}:{}})})});i.displayName="PriceInput";try{i.displayName="PriceInput",i.__docgenInfo={description:`The PriceInput component is a combination of a TextInput and a Checkbox to define prices.
It integrates with Formik for form state management and is used when an null price is meant to be interpreted as free.

---`,displayName:"PriceInput",props:{className:{defaultValue:null,description:`A custom class for the field layout,
where label, description, input, and footer are displayed.`,name:"className",required:!1,type:{name:"string"}},name:{defaultValue:null,description:"",name:"name",required:!1,type:{name:"string"}},rightIcon:{defaultValue:null,description:"",name:"rightIcon",required:!1,type:{name:"string"}},smallLabel:{defaultValue:null,description:"A flag to display a smaller label.",name:"smallLabel",required:!1,type:{name:"boolean"}},label:{defaultValue:null,description:`A label for the input,
also used as the aria-label for the group.`,name:"label",required:!0,type:{name:"string"}},showFreeCheckbox:{defaultValue:null,description:'A flag to show the "Gratuit" checkbox.',name:"showFreeCheckbox",required:!1,type:{name:"boolean"}},hideAsterisk:{defaultValue:{value:"false"},description:"",name:"hideAsterisk",required:!1,type:{name:"boolean"}},error:{defaultValue:null,description:`A custom error message to be displayed.
If this prop is provided, the error message will be displayed and the field will be marked as errored`,name:"error",required:!1,type:{name:"string"}},updatePriceValue:{defaultValue:null,description:"",name:"updatePriceValue",required:!0,type:{name:"(value: string) => void"}}}}}catch{}const te={title:"@/ui-kit/forms/PriceInput",component:i},n={args:{name:"email",label:"Email"}},s={args:{name:"email",label:"Email",smallLabel:!0}},o={args:{name:"email",label:"Email",showFreeCheckbox:!0}};var k,E,I;n.parameters={...n.parameters,docs:{...(k=n.parameters)==null?void 0:k.docs,source:{originalSource:`{
  args: {
    name: 'email',
    label: 'Email'
  }
}`,...(I=(E=n.parameters)==null?void 0:E.docs)==null?void 0:I.source}}};var C,_,q;s.parameters={...s.parameters,docs:{...(C=s.parameters)==null?void 0:C.docs,source:{originalSource:`{
  args: {
    name: 'email',
    label: 'Email',
    smallLabel: true
  }
}`,...(q=(_=s.parameters)==null?void 0:_.docs)==null?void 0:q.source}}};var V,v,w;o.parameters={...o.parameters,docs:{...(V=o.parameters)==null?void 0:V.docs,source:{originalSource:`{
  args: {
    name: 'email',
    label: 'Email',
    showFreeCheckbox: true
  }
}`,...(w=(v=o.parameters)==null?void 0:v.docs)==null?void 0:w.source}}};const le=["Default","SmallLabel","WithCheckbox"];export{n as Default,s as SmallLabel,o as WithCheckbox,le as __namedExportsOrder,te as default};
