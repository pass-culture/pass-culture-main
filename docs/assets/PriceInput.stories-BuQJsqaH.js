import{j as u}from"./jsx-runtime-Cf8x2fCZ.js";import{R as N,r}from"./index-QQMyt9Ur.js";import{C as S}from"./Checkbox-CFp8fuv2.js";import{s as j,a as H}from"./stroke-franc-CFUtV4l2.js";import{T as U}from"./TextInput-C-6M7uLs.js";import"./index-yBjzXJbu.js";import"./_commonjsHelpers-CqkleIqs.js";import"./index-B0pXE9zJ.js";import"./Tag-DpLUbPXr.js";import"./full-thumb-up-Bb4kpRpM.js";import"./SvgIcon-B5V96DYN.js";import"./BaseInput-B8c5gx_3.js";import"./stroke-search-dgesjRZH.js";import"./FieldError-2mFOl_uD.js";import"./stroke-error-DSZD431a.js";import"./FieldLayoutCharacterCount-CCjrqBrG.js";import"./index.module-DTkZ18fI.js";const D={"input-layout-small-label":"_input-layout-small-label_kaqxt_1"},o=N.forwardRef(({className:m,name:c,label:I,value:p,max:k,rightIcon:q,disabled:d,smallLabel:C,showFreeCheckbox:f,hideAsterisk:h=!1,error:b,currency:i="EUR",onChange:g,onBlur:v},F)=>{const y=r.useRef(null),w=`${c}.free`,x=r.useRef(null),V=p===0,[a,E]=r.useState(V),_=i==="XPF"?j:H,R=i==="XPF"?1:.01,P=i==="EUR";r.useEffect(()=>{const t=document.activeElement===x.current;!a&&t&&y.current?.focus()},[a]);const T=e=>{g?.({target:{value:e.target.value}}),f&&E(e.target.value==="0")},A=()=>{const e=!a;E(e);let t="";e&&(t="0"),g?.({target:{value:t}})},L=u.jsx(S,{ref:x,label:"Gratuit",checked:a,name:w,onChange:A,disabled:d});return u.jsx("div",{ref:F,children:u.jsx(U,{ref:y,"data-testid":"input-price",className:m,labelClassName:C?D["input-layout-small-label"]:"",required:!h,name:c,label:I,value:p??"",type:"number",step:R,hasDecimal:P,min:0,max:k,rightIcon:q||_,disabled:d,asterisk:!h,onChange:T,onBlur:v,hasError:!!b,error:b,...f?{InputExtension:L}:{}})})});o.displayName="PriceInput";try{o.displayName="PriceInput",o.__docgenInfo={description:`The PriceInput component is a combination of a TextInput and a Checkbox to define prices.
It integrates with Formik for form state management and is used when an null price is meant to be interpreted as free.

---`,displayName:"PriceInput",props:{className:{defaultValue:null,description:`A custom class for the field layout,
where label, description, input, and footer are displayed.`,name:"className",required:!1,type:{name:"string"}},name:{defaultValue:null,description:"The name of the input, mind what's being used in the form.",name:"name",required:!1,type:{name:"string"}},rightIcon:{defaultValue:null,description:"",name:"rightIcon",required:!1,type:{name:"string"}},smallLabel:{defaultValue:null,description:"A flag to display a smaller label.",name:"smallLabel",required:!1,type:{name:"boolean"}},label:{defaultValue:null,description:`A label for the input,
also used as the aria-label for the group.`,name:"label",required:!0,type:{name:"string"}},onChange:{defaultValue:null,description:"A callback when the quantity changes.",name:"onChange",required:!1,type:{name:"ChangeEventHandler<HTMLInputElement>"}},onBlur:{defaultValue:null,description:"A callback when the quantity text input is blurred.",name:"onBlur",required:!1,type:{name:"FocusEventHandler<HTMLInputElement>"}},value:{defaultValue:null,description:"The quantity value. Should be `undefined` if the quantity is unlimited.",name:"value",required:!1,type:{name:'number | ""'}},showFreeCheckbox:{defaultValue:null,description:'A flag to show the "Gratuit" checkbox.',name:"showFreeCheckbox",required:!1,type:{name:"boolean"}},hideAsterisk:{defaultValue:{value:"false"},description:"",name:"hideAsterisk",required:!1,type:{name:"boolean"}},error:{defaultValue:null,description:`A custom error message to be displayed.
If this prop is provided, the error message will be displayed and the field will be marked as errored`,name:"error",required:!1,type:{name:"string"}},currency:{defaultValue:{value:"EUR"},description:"Currency to use to display price amount",name:"currency",required:!1,type:{name:"enum",value:[{value:'"EUR"'},{value:'"XPF"'}]}}}}}catch{}const ne={title:"@/ui-kit/forms/PriceInput",component:o},n={args:{name:"email",label:"Email"}},l={args:{name:"email",label:"Email",smallLabel:!0}},s={args:{name:"email",label:"Email",showFreeCheckbox:!0}};n.parameters={...n.parameters,docs:{...n.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'email',
    label: 'Email'
  }
}`,...n.parameters?.docs?.source}}};l.parameters={...l.parameters,docs:{...l.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'email',
    label: 'Email',
    smallLabel: true
  }
}`,...l.parameters?.docs?.source}}};s.parameters={...s.parameters,docs:{...s.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'email',
    label: 'Email',
    showFreeCheckbox: true
  }
}`,...s.parameters?.docs?.source}}};const le=["Default","SmallLabel","WithCheckbox"];export{n as Default,l as SmallLabel,s as WithCheckbox,le as __namedExportsOrder,ne as default};
