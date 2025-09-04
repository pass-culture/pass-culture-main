import{j as c}from"./jsx-runtime-DF2Pcvd1.js";import{R as W,r as t}from"./index-B2-qRKKC.js";import{C as O}from"./Checkbox-DcgCepTx.js";import{T as $}from"./TextInput-BXnJurHW.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./index-DeARc5FM.js";import"./Tag-DoB-Hjk-.js";import"./full-thumb-up-Bb4kpRpM.js";import"./SvgIcon-DfLnDDE5.js";import"./BaseInput-JKfrEs2s.js";import"./stroke-search-dgesjRZH.js";import"./FieldError-B3RhE53I.js";import"./stroke-error-DSZD431a.js";import"./FieldLayoutCharacterCount-Cg7wcWeq.js";import"./index.module-BDmDBTbR.js";const z={"input-layout-small-label":"_input-layout-small-label_kaqxt_1"},u=W.forwardRef(({className:p,name:d,label:N,max:P,rightIcon:S,disabled:f,smallLabel:A,showFreeCheckbox:b,hideAsterisk:h=!1,error:g,updatePriceValue:x},L)=>{var y,k;const a=t.useRef(null),j=`${d}.free`,l=t.useRef(null),[n,m]=t.useState(!1);t.useEffect(()=>{var E;const r=document.activeElement===l.current;!n&&r&&((E=a.current)==null||E.focus())},[n]),t.useEffect(()=>{var e;l.current&&((e=a.current)==null?void 0:e.value)==="0"&&m(!0)},[(y=a.current)==null?void 0:y.value,(k=l.current)==null?void 0:k.value]);const T=e=>{x(e.target.value),b&&m(e.target.value==="0")},D=()=>{const e=!n;m(e);let r="";e&&(r="0"),a.current&&(x(r),a.current.value=r)},G=c.jsx(O,{ref:l,label:"Gratuit",checked:n,name:j,onChange:D,disabled:f});return c.jsx("div",{ref:L,children:c.jsx($,{ref:a,className:p,labelClassName:A?z["input-layout-small-label"]:"",required:!h,name:d,label:N,type:"number",step:"0.01",min:0,max:P,rightIcon:S,disabled:f,asterisk:!h,onChange:T,hasError:!!g,error:g,...b?{InputExtension:G}:{}})})});u.displayName="PriceInput";try{u.displayName="PriceInput",u.__docgenInfo={description:`The PriceInput component is a combination of a TextInput and a Checkbox to define prices.
It integrates with Formik for form state management and is used when an null price is meant to be interpreted as free.

---`,displayName:"PriceInput",props:{className:{defaultValue:null,description:`A custom class for the field layout,
where label, description, input, and footer are displayed.`,name:"className",required:!1,type:{name:"string"}},name:{defaultValue:null,description:"",name:"name",required:!1,type:{name:"string"}},rightIcon:{defaultValue:null,description:"",name:"rightIcon",required:!1,type:{name:"string"}},smallLabel:{defaultValue:null,description:"A flag to display a smaller label.",name:"smallLabel",required:!1,type:{name:"boolean"}},label:{defaultValue:null,description:`A label for the input,
also used as the aria-label for the group.`,name:"label",required:!0,type:{name:"string"}},showFreeCheckbox:{defaultValue:null,description:'A flag to show the "Gratuit" checkbox.',name:"showFreeCheckbox",required:!1,type:{name:"boolean"}},hideAsterisk:{defaultValue:{value:"false"},description:"",name:"hideAsterisk",required:!1,type:{name:"boolean"}},error:{defaultValue:null,description:`A custom error message to be displayed.
If this prop is provided, the error message will be displayed and the field will be marked as errored`,name:"error",required:!1,type:{name:"string"}},updatePriceValue:{defaultValue:null,description:"",name:"updatePriceValue",required:!0,type:{name:"(value: string) => void"}}}}}catch{}const ne={title:"@/ui-kit/forms/PriceInput",component:u},s={args:{name:"email",label:"Email"}},o={args:{name:"email",label:"Email",smallLabel:!0}},i={args:{name:"email",label:"Email",showFreeCheckbox:!0}};var I,C,_;s.parameters={...s.parameters,docs:{...(I=s.parameters)==null?void 0:I.docs,source:{originalSource:`{
  args: {
    name: 'email',
    label: 'Email'
  }
}`,...(_=(C=s.parameters)==null?void 0:C.docs)==null?void 0:_.source}}};var v,q,V;o.parameters={...o.parameters,docs:{...(v=o.parameters)==null?void 0:v.docs,source:{originalSource:`{
  args: {
    name: 'email',
    label: 'Email',
    smallLabel: true
  }
}`,...(V=(q=o.parameters)==null?void 0:q.docs)==null?void 0:V.source}}};var w,F,R;i.parameters={...i.parameters,docs:{...(w=i.parameters)==null?void 0:w.docs,source:{originalSource:`{
  args: {
    name: 'email',
    label: 'Email',
    showFreeCheckbox: true
  }
}`,...(R=(F=i.parameters)==null?void 0:F.docs)==null?void 0:R.source}}};const se=["Default","SmallLabel","WithCheckbox"];export{s as Default,o as SmallLabel,i as WithCheckbox,se as __namedExportsOrder,ne as default};
