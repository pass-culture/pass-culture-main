import{j as c}from"./jsx-runtime-DF2Pcvd1.js";import{R as W,r as t}from"./index-B2-qRKKC.js";import{C as O}from"./Checkbox-DPzdcoeb.js";import{T as $}from"./TextInput-CJKsFLSd.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./index-DeARc5FM.js";import"./Tag-ClYlfzfP.js";import"./full-thumb-up-Bb4kpRpM.js";import"./SvgIcon-DfLnDDE5.js";import"./BaseInput-C6hUc365.js";import"./FieldError-B3RhE53I.js";import"./stroke-error-DSZD431a.js";import"./FieldLayoutCharacterCount-DKTgIOgC.js";import"./index.module-D7-Ko2QV.js";const z={"input-layout-small-label":"_input-layout-small-label_kaqxt_1"},u=W.forwardRef(({className:p,name:d,label:R,max:N,rightIcon:P,disabled:f,smallLabel:S,showFreeCheckbox:b,hideAsterisk:h=!1,error:A,updatePriceValue:g},L)=>{var x,y;const a=t.useRef(null),j=`${d}.free`,l=t.useRef(null),[n,m]=t.useState(!1);t.useEffect(()=>{var k;const r=document.activeElement===l.current;!n&&r&&((k=a.current)==null||k.focus())},[n]),t.useEffect(()=>{var e;l.current&&((e=a.current)==null?void 0:e.value)==="0"&&m(!0)},[(x=a.current)==null?void 0:x.value,(y=l.current)==null?void 0:y.value]);const T=e=>{g(e.target.value),b&&m(e.target.value==="0")},D=()=>{const e=!n;m(e);let r="";e&&(r="0"),a.current&&(g(r),a.current.value=r)},G=c.jsx(O,{ref:l,label:"Gratuit",checked:n,name:j,onChange:D,disabled:f});return c.jsx("div",{ref:L,children:c.jsx($,{ref:a,className:p,labelClassName:S?z["input-layout-small-label"]:"",required:!h,name:d,label:R,type:"number",step:"0.01",min:0,max:N,rightIcon:P,disabled:f,asterisk:!h,onChange:T,hasError:!!A,...b?{InputExtension:G}:{}})})});u.displayName="PriceInput";try{u.displayName="PriceInput",u.__docgenInfo={description:`The PriceInput component is a combination of a TextInput and a Checkbox to define prices.
It integrates with Formik for form state management and is used when an null price is meant to be interpreted as free.

---`,displayName:"PriceInput",props:{className:{defaultValue:null,description:`A custom class for the field layout,
where label, description, input, and footer are displayed.`,name:"className",required:!1,type:{name:"string"}},name:{defaultValue:null,description:"",name:"name",required:!1,type:{name:"string"}},rightIcon:{defaultValue:null,description:"",name:"rightIcon",required:!1,type:{name:"string"}},smallLabel:{defaultValue:null,description:"A flag to display a smaller label.",name:"smallLabel",required:!1,type:{name:"boolean"}},label:{defaultValue:null,description:`A label for the input,
also used as the aria-label for the group.`,name:"label",required:!0,type:{name:"string"}},showFreeCheckbox:{defaultValue:null,description:'A flag to show the "Gratuit" checkbox.',name:"showFreeCheckbox",required:!1,type:{name:"boolean"}},hideAsterisk:{defaultValue:{value:"false"},description:"",name:"hideAsterisk",required:!1,type:{name:"boolean"}},error:{defaultValue:null,description:`A custom error message to be displayed.
If this prop is provided, the error message will be displayed and the field will be marked as errored`,name:"error",required:!1,type:{name:"string"}},updatePriceValue:{defaultValue:null,description:"",name:"updatePriceValue",required:!0,type:{name:"(value: string) => void"}}}}}catch{}const le={title:"ui-kit/formsV2/PriceInput",component:u},s={args:{name:"email",label:"Email"}},o={args:{name:"email",label:"Email",smallLabel:!0}},i={args:{name:"email",label:"Email",showFreeCheckbox:!0}};var E,I,C;s.parameters={...s.parameters,docs:{...(E=s.parameters)==null?void 0:E.docs,source:{originalSource:`{
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
}`,...(V=(v=o.parameters)==null?void 0:v.docs)==null?void 0:V.source}}};var q,w,F;i.parameters={...i.parameters,docs:{...(q=i.parameters)==null?void 0:q.docs,source:{originalSource:`{
  args: {
    name: 'email',
    label: 'Email',
    showFreeCheckbox: true
  }
}`,...(F=(w=i.parameters)==null?void 0:w.docs)==null?void 0:F.source}}};const ne=["Default","SmallLabel","WithCheckbox"];export{s as Default,o as SmallLabel,i as WithCheckbox,ne as __namedExportsOrder,le as default};
