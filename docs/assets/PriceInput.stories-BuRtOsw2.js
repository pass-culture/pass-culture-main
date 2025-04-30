import{j as m}from"./jsx-runtime-BYYWji4R.js";import{R as D,r}from"./index-ClcD9ViR.js";import{B as G}from"./BaseCheckbox-DKrWbv5n.js";import{T as W}from"./TextInput-CVZu0z03.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./index-DeARc5FM.js";import"./SvgIcon-CyWUmZpn.js";import"./BaseInput-BrnVefEj.js";import"./FieldError-azuIsM2E.js";import"./stroke-error-DSZD431a.js";import"./FieldLayoutCharacterCount-Bc4HS3VB.js";import"./index.module-DF6qn1Ex.js";const O={"input-layout-small-label":"_input-layout-small-label_kaqxt_1"},u=D.forwardRef(({className:p,name:d,label:R,max:N,rightIcon:P,disabled:f,smallLabel:S,showFreeCheckbox:b,hideAsterisk:h=!1,updatePriceValue:g},L)=>{var x,y;const a=r.useRef(null),j=`${d}.free`,n=r.useRef(null),[l,c]=r.useState(!1);r.useEffect(()=>{var k;const t=document.activeElement===n.current;!l&&t&&((k=a.current)==null||k.focus())},[l]),r.useEffect(()=>{var e;n.current&&((e=a.current)==null?void 0:e.value)==="0"&&c(!0)},[(x=a.current)==null?void 0:x.value,(y=n.current)==null?void 0:y.value]);const A=e=>{g(e.target.value),b&&c(e.target.value==="0")},T=()=>{const e=!l;c(e);let t="";e&&(t="0"),a.current&&(g(t),a.current.value=t)},B=m.jsx(G,{ref:n,label:"Gratuit",checked:l,name:j,onChange:T,disabled:f});return m.jsx("div",{ref:L,children:m.jsx(W,{ref:a,className:p,labelClassName:S?O["input-layout-small-label"]:"",required:!h,name:d,label:R,type:"number",step:"0.01",min:0,max:N,rightIcon:P,disabled:f,asterisk:!h,onChange:A,...b?{InputExtension:B}:{}})})});u.displayName="PriceInput";try{u.displayName="PriceInput",u.__docgenInfo={description:`The PriceInput component is a combination of a TextInput and a Checkbox to define prices.
It integrates with Formik for form state management and is used when an null price is meant to be interpreted as free.

---`,displayName:"PriceInput",props:{className:{defaultValue:null,description:`A custom class for the field layout,
where label, description, input, and footer are displayed.`,name:"className",required:!1,type:{name:"string"}},name:{defaultValue:null,description:"",name:"name",required:!1,type:{name:"string"}},smallLabel:{defaultValue:null,description:"A flag to display a smaller label.",name:"smallLabel",required:!1,type:{name:"boolean"}},rightIcon:{defaultValue:null,description:"",name:"rightIcon",required:!1,type:{name:"string"}},label:{defaultValue:null,description:`A label for the input,
also used as the aria-label for the group.`,name:"label",required:!0,type:{name:"string"}},showFreeCheckbox:{defaultValue:null,description:'A flag to show the "Gratuit" checkbox.',name:"showFreeCheckbox",required:!1,type:{name:"boolean"}},hideAsterisk:{defaultValue:{value:"false"},description:"",name:"hideAsterisk",required:!1,type:{name:"boolean"}},updatePriceValue:{defaultValue:null,description:"",name:"updatePriceValue",required:!0,type:{name:"(value: string) => void"}}}}}catch{}const ae={title:"ui-kit/formsV2/PriceInput",component:u},s={args:{name:"email",label:"Email"}},o={args:{name:"email",label:"Email",smallLabel:!0}},i={args:{name:"email",label:"Email",showFreeCheckbox:!0}};var E,I,C;s.parameters={...s.parameters,docs:{...(E=s.parameters)==null?void 0:E.docs,source:{originalSource:`{
  args: {
    name: 'email',
    label: 'Email'
  }
}`,...(C=(I=s.parameters)==null?void 0:I.docs)==null?void 0:C.source}}};var _,v,V;o.parameters={...o.parameters,docs:{...(_=o.parameters)==null?void 0:_.docs,source:{originalSource:`{
  args: {
    name: 'email',
    label: 'Email',
    smallLabel: true
  }
}`,...(V=(v=o.parameters)==null?void 0:v.docs)==null?void 0:V.source}}};var q,F,w;i.parameters={...i.parameters,docs:{...(q=i.parameters)==null?void 0:q.docs,source:{originalSource:`{
  args: {
    name: 'email',
    label: 'Email',
    showFreeCheckbox: true
  }
}`,...(w=(F=i.parameters)==null?void 0:F.docs)==null?void 0:w.source}}};const te=["Default","SmallLabel","WithCheckbox"];export{s as Default,o as SmallLabel,i as WithCheckbox,te as __namedExportsOrder,ae as default};
